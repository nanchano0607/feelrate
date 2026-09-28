# 1단계: Python 기반 이미지 선택
FROM python:3.11-slim

# 2단계: 작업 디렉토리 설정
WORKDIR /app

# 3단계: requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4단계: 코드 복사
COPY . .

# 5단계: FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
