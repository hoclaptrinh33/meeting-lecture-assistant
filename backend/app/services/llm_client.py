import json
from typing import Any, Dict, List, Literal, Optional
import httpx

from app.core.config import settings
from app.core.exceptions import (
    LlmInvalidJsonException,
    LlmNotConfiguredException,
    LlmTimeoutException,
)

CLEAN_SYSTEM_PROMPT = """Bạn là trợ lý biên tập văn bản tiếng Việt chuyên nghiệp.
Nhiệm vụ của bạn là nhận vào danh sách các câu transcript có mã vị trí (position), làm sạch các từ đệm vô nghĩa (à, ừ, thì, là, mà...), sửa lỗi chính tả, chuẩn hóa dấu câu và viết hoa, nhưng TUYỆT ĐỐI KHÔNG làm thay đổi ngữ nghĩa gốc hay cắt bớt ý.
Trả về định dạng JSON object dạng:
{
  "cleaned_segments": [
    {"position": 0, "text_cleaned": "..."},
    ...
  ]
}
"""

MEETING_SUMMARY_PROMPT = """Bạn là trợ lý tổng hợp biên bản cuộc họp tiếng Việt chuyên nghiệp.
Dựa vào toàn bộ nội dung cuộc họp có mốc thời gian kèm theo, hãy trích xuất biên bản theo định dạng JSON với cấu trúc chính xác sau:
{
  "objective": "Mục tiêu chính của cuộc họp",
  "open_issues": [{"timestamp": "MM:SS", "text": "Vấn đề còn tồn đọng/chưa thống nhất"}],
  "decisions": [{"timestamp": "MM:SS", "text": "Quyết định đã được thông qua"}],
  "actions": [{"timestamp": "MM:SS", "owner": "Tên người phụ trách", "task": "Nhiệm vụ", "deadline": "Thời hạn"}]
}
"""

LECTURE_SUMMARY_PROMPT = """Bạn là trợ lý ghi chú bài giảng tiếng Việt chuyên sâu.
Dựa vào toàn bộ nội dung bài giảng có mốc thời gian kèm theo, hãy trích xuất ghi chú học tập theo định dạng JSON với cấu trúc chính xác sau:
{
  "overview": "Tóm tắt tổng quan nội dung bài giảng",
  "concepts": [{"timestamp": "MM:SS", "term": "Tên khái niệm/thuật ngữ", "explanation": "Giải thích chi tiết"}],
  "examples": [{"timestamp": "MM:SS", "text": "Ví dụ hoặc tình huống minh họa cụ thể"}],
  "exam_notes": [{"timestamp": "MM:SS", "text": "Điểm lưu ý ôn thi, trọng tâm kiến thức"}]
}
"""


class LlmClient:
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    def _ensure_configured(self) -> None:
        if not self.model:
            raise LlmNotConfiguredException()

    def _call_chat_completions(self, messages: List[Dict[str, str]], json_mode: bool = True) -> Dict[str, Any]:
        self._ensure_configured()
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if json_mode and settings.LLM_JSON_MODE:
            payload["response_format"] = {"type": "json_object"}

        for attempt in range(2):
            try:
                with httpx.Client(timeout=float(self.timeout)) as client:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content)
            except httpx.TimeoutException as e:
                raise LlmTimeoutException() from e
            except (json.JSONDecodeError, KeyError) as e:
                if attempt == 1:
                    raise LlmInvalidJsonException() from e
            except Exception as e:
                if attempt == 1:
                    raise RuntimeError(f"Lỗi gọi LLM API: {str(e)}") from e

        raise LlmInvalidJsonException()

    def clean_transcript(self, raw_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Làm sạch các từ thừa và chuẩn hóa ngữ pháp các câu transcript."""
        user_content = json.dumps([
            {"position": s["position"], "text_raw": s["text_raw"]}
            for s in raw_segments
        ], ensure_ascii=False)

        messages = [
            {"role": "system", "content": CLEAN_SYSTEM_PROMPT},
            {"role": "user", "content": f"Dữ liệu cần làm sạch:\n{user_content}"},
        ]

        result = self._call_chat_completions(messages, json_mode=True)
        return result.get("cleaned_segments", [])

    def summarize_transcript(
        self,
        transcript_text: str,
        template: Literal["meeting", "lecture"],
    ) -> Dict[str, Any]:
        """Tóm tắt cuộc họp hoặc bài giảng có mốc thời gian."""
        system_prompt = MEETING_SUMMARY_PROMPT if template == "meeting" else LECTURE_SUMMARY_PROMPT
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Nội dung transcript:\n{transcript_text}"},
        ]
        return self._call_chat_completions(messages, json_mode=True)
