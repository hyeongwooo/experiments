from flask import Flask, request, jsonify
import redis
import os
import time
import logging

app = Flask(__name__)

# ✅ logging 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Redis 연결 설정
REDIS_HOST = os.getenv("REDIS_HOST", "redis.user1.svc.cluster.local")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/output', methods=['POST'])
def detect_event():
    try:
        function_start_time = time.time()  # 기능 처리 시간 시작

        data = request.get_json()
        if not data:
            logging.error("요청에 JSON 데이터가 없습니다.")
            return jsonify({"error": "JSON 데이터가 필요합니다."}), 400

        sensor_name = data.get("sensorName")
        subscription_id = data.get("subscriptionID")
        event_timestamp = data.get("timestamp")

        if not sensor_name or not subscription_id or event_timestamp is None:
            logging.error("필수 필드 누락: sensorName, subscriptionID, 또는 timestamp")
            return jsonify({"error": "sensorName, subscriptionID, timestamp가 필요합니다."}), 400

        # Redis 키 구성
        redis_key = f"{sensor_name}-{subscription_id}"
        status = redis_client.get(redis_key)

        if status == "detected":
            logging.info(f"{subscription_id}번 {sensor_name}센서가 이벤트를 감지했습니다")
            response_msg = {"message": "감지됨"}
            status_code = 200
        else:
            logging.info(f"{subscription_id}번 {sensor_name} 센서가 이벤트를 감지하지 않음 또는 상태 미일치")
            response_msg = {"message": "감지되지 않음"}
            status_code = 404

        function_end_time = time.time()
        function_duration = function_end_time - function_start_time
        event_duration = function_end_time - float(event_timestamp)

        # 처리 시간 로그
        logging.info(f"기능 처리 소요 시간: {function_duration:.3f}초")
        logging.info(f"이벤트 발생부터 기능 종료까지 총 시간: {event_duration:.3f}초")

        return jsonify({
            **response_msg,
            "functionDuration": round(function_duration, 3),
            "eventToEndDuration": round(event_duration, 3)
        }), status_code

    except Exception as e:
        logging.exception("서버 처리 중 예외 발생")
        return jsonify({"error": "서버 오류"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

