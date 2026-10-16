"""Dịch vụ xuất tài liệu đa định dạng (Markdown, Word DOCX, PDF, SRT, WebVTT)."""
from typing import Any, Dict, List, Optional


class ExporterService:
    @staticmethod
    def export_srt(segments: List[Dict[str, Any]], text_mode: str = "auto", include_speakers: bool = True) -> bytes:
        """Xuất phụ đề SRT.
        TODO: Định dạng thời gian HH:MM:SS,mmm và số thứ tự phụ đề.
        """
        pass

    @staticmethod
    def export_vtt(segments: List[Dict[str, Any]], text_mode: str = "auto", include_speakers: bool = True) -> bytes:
        """Xuất phụ đề WebVTT.
        TODO: Định dạng thời gian HH:MM:SS.mmm với header WEBVTT.
        """
        pass

    @staticmethod
    def export_markdown(
        title: str,
        segments: List[Dict[str, Any]],
        summary: Optional[Dict[str, Any]] = None,
        highlights: Optional[List[Dict[str, Any]]] = None,
        action_items: Optional[List[Dict[str, Any]]] = None,
        text_mode: str = "auto",
        include_speakers: bool = True,
    ) -> bytes:
        """Xuất văn bản Markdown hoàn chỉnh.
        TODO: Tổng hợp tiêu đề, tóm tắt, việc cần làm, đoạn đánh dấu và lời thoại.
        """
        pass

    @staticmethod
    def export_docx(
        title: str,
        segments: List[Dict[str, Any]],
        summary: Optional[Dict[str, Any]] = None,
        action_items: Optional[List[Dict[str, Any]]] = None,
        text_mode: str = "auto",
        include_speakers: bool = True,
    ) -> bytes:
        """Xuất tài liệu Word (.docx).
        TODO: Sử dụng python-docx để tạo các đoạn văn bản và danh sách có định dạng.
        """
        pass

    @staticmethod
    def export_pdf(
        title: str,
        segments: List[Dict[str, Any]],
        summary: Optional[Dict[str, Any]] = None,
        text_mode: str = "auto",
        include_speakers: bool = True,
    ) -> bytes:
        """Xuất file PDF nhúng font NotoSans để giữ dấu tiếng Việt.
        TODO: Sử dụng fpdf2 nhúng font assets/fonts/NotoSans-Regular.ttf.
        """
        pass
