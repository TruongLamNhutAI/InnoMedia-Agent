# Sử dụng Python 3.12 bản nhẹ nhất
FROM python:3.12-slim

# Cập nhật hệ thống và cài đặt các thư viện cần thiết (bao gồm FFmpeg, ImageMagick và các công cụ biên dịch cho Pillow)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-dejavu \
    gcc \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Xóa bỏ hoàn toàn các rào cản bảo mật của ImageMagick
RUN find /etc -type f -name "policy.xml" -delete

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements.txt và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn của Service 3 vào container
COPY . .

# Expose cổng 8001 cho API
EXPOSE 8001

# Lệnh khởi chạy FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]