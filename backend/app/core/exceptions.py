from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        fields: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code
        self.message = message
        self.fields = fields


class BadRequestException(AppException):
    def __init__(self, message: str = "Yêu cầu không hợp lệ."):
        super().__init__(status.HTTP_400_BAD_REQUEST, "bad_request", message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Tài khoản hoặc mật khẩu không chính xác hoặc token không hợp lệ."):
        super().__init__(status.HTTP_401_UNAUTHORIZED, "unauthorized", message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Không tìm thấy dữ liệu yêu cầu."):
        super().__init__(status.HTTP_404_NOT_FOUND, "not_found", message)


class GpuBusyException(AppException):
    def __init__(self, message: str = "GPU đang bận với một phiên khác."):
        super().__init__(status.HTTP_409_CONFLICT, "gpu_busy", message)


class InvalidStateException(AppException):
    def __init__(self, message: str = "Trạng thái hiện tại không cho phép thao tác này."):
        super().__init__(status.HTTP_409_CONFLICT, "invalid_state", message)


class FileTooLargeException(AppException):
    def __init__(self, message: str = "Kích thước file vượt quá giới hạn cho phép."):
        super().__init__(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "file_too_large", message)


class UnsupportedMediaException(AppException):
    def __init__(self, message: str = "Định dạng file không được hỗ trợ hoặc không có luồng âm thanh."):
        super().__init__(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "unsupported_media", message)


class ValidationException(AppException):
    def __init__(self, message: str = "Dữ liệu không hợp lệ.", fields: Optional[Dict[str, str]] = None):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, "validation", message, fields=fields)


class DurationExceededException(AppException):
    def __init__(self, message: str = "Thời lượng âm thanh vượt quá giới hạn tối đa (3 giờ)."):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, "duration_exceeded", message)


class LlmNotConfiguredException(AppException):
    def __init__(self, message: str = "Hệ thống chưa cấu hình LLM_MODEL cho tác vụ này."):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, "llm_not_configured", message)


class LlmInvalidJsonException(AppException):
    def __init__(self, message: str = "Không nhận được phản hồi định dạng JSON hợp lệ từ LLM."):
        super().__init__(status.HTTP_502_BAD_GATEWAY, "llm_invalid_json", message)


class GpuOomException(AppException):
    def __init__(self, message: str = "Không đủ bộ nhớ VRAM để thực hiện tác vụ trên GPU."):
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, "gpu_oom", message)


class LlmTimeoutException(AppException):
    def __init__(self, message: str = "Hết thời gian chờ phản hồi từ LLM."):
        super().__init__(status.HTTP_504_GATEWAY_TIMEOUT, "llm_timeout", message)


def app_exception_handler(request: Any, exc: AppException) -> JSONResponse:
    content: Dict[str, Any] = {
        "error": {
            "code": exc.code,
            "message": exc.message,
        }
    }
    if exc.fields:
        content["error"]["fields"] = exc.fields
    return JSONResponse(status_code=exc.status_code, content=content)
