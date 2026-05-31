# Sử dụng Python 3.12 bản nhẹ (slim)
FROM python:3.12-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Mở cổng 8000 cho FastAPI
EXPOSE 8000

# Lệnh khởi chạy API Server (ta sẽ viết file main.py chứa FastAPI ở bước tiếp theo)
CMD ["uvicorn", "main.py", "--host", "0.0.0.0", "--port", "8000"]