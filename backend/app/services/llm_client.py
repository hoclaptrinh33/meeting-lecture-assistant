"""Client gọi API LLM tương thích OpenAI để làm sạch văn bản và tạo biên bản tóm tắt."""
from typing import Any, Dict, List, Literal


class LlmClient:
    def __init__(self):
        pass

    def clean_transcript(self, raw_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Làm sạch các từ thừa và chuẩn hóa ngữ pháp các câu transcript.
        TODO: Gửi prompt làm sạch văn bản tới POST /chat/completions.
        """
        pass

    def summarize_transcript(
        self,
        transcript_text: str,
        template: Literal["meeting", "lecture"],
    ) -> Dict[str, Any]:
        """Tóm tắt cuộc họp hoặc bài giảng có mốc thời gian.
        TODO: Gửi prompt tóm tắt cuộc họp / bài giảng theo cấu trúc JSON quy định.
        """
        pass
