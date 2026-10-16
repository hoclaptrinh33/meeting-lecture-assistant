FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Cài đặt ffmpeg và các thư viện hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài đặt PyTorch với hỗ trợ CUDA (cu121 hoặc tương thích)
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Cài đặt các thư viện từ requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Thiết lập đường dẫn thư viện cho ctranslate2 tìm libcublas / cudnn
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.11/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.11/site-packages/nvidia/cudnn/lib:${LD_LIBRARY_PATH}"

# Tạo thư mục dữ liệu và cache
RUN mkdir -p /data/audio /data/tmp /data/voice /cache/huggingface

# Tạo user không phải root để chạy ứng dụng an toàn
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /data /cache

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
