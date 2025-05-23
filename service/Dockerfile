# 1. 베이스 이미지 (Python 3.9 풀 버전)
FROM python:3.9

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 패키지 설치 (Flask + redis)
RUN pip install --no-cache-dir flask redis

# 4. 애플리케이션 코드 복사
COPY update.py .

# 5. Flask 앱 실행
CMD ["python", "update.py"]
