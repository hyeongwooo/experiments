import os
import redis
import traceback
import time
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)

# ✅ logging 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Redis 연결 정보
REDIS_HOST = os.getenv("REDIS_HOST", "redis.user1.svc.cluster.local")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

@app.route('/update', methods=['POST'])
def update_status():
    logging.info("/update 호출됨")

    try:
        # 요청이 JSON인지 확인
        if not request.is_json:
            logging.error("요청이 JSON 형식이 아님")
            return jsonify({"error": "Request content type must be application/json"}), 400

        # JSON 파싱
        data = request.get_json(force=True)
        logging.info(f"수신된 JSON 데이터: {data}")

        # 필수 필드 확인
        sensor_name = data.get("sensorName")
        subscription_id = data.get("subscriptionID")
        if not sensor_name or not subscription_id:
            logging.error("sensorName 또는 subscriptionID 누락됨")
            return jsonify({"error": "Missing sensorName or subscriptionID"}), 400

        # ⏱️ Redis 저장 처리 시간 측정 시작
        start_time = time.time()

        # Redis 연결
        logging.info(f"Redis에 연결 중: {REDIS_HOST}:{REDIS_PORT}")
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        logging.info("Redis 연결 성공")

        # Redis 저장
        key = f"{sensor_name}-{subscription_id}"
        r.set(key, "detected")
        logging.info(f"Redis에 저장 완료: {key} = detected")

        # ⏱️ 처리 시간 측정 종료
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"Redis 저장 전체 소요 시간: {duration:.3f}초")

        return jsonify({"message": "Status updated successfully"}), 200

    except redis.exceptions.ConnectionError as conn_err:
        logging.error(f"Redis 연결 실패: {conn_err}")
        return jsonify({"error": "Redis connection failed"}), 500

    except Exception as e:
        logging.exception("일반 예외 발생:")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

