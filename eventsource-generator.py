import requests
import random
import time

# 센서 유형별 이벤트소스 포트 매핑
eventsource_map = {
    "차량 감지": "http://192.168.21.157:32541/vehicle-detected",
    "속도 감지": "http://192.168.21.157:31035/over-speed",
    "보행자 감지": "http://192.168.21.157:30366/pedestrian-detected"
}

sensor_types = list(eventsource_map.keys())
event_count = 1  # 전송 횟수

for i in range(event_count):
    sensor_name = random.choice(sensor_types)
    sensor_number = random.randint(1, 99)
    subscription_id = f"{sensor_number}"

    payload = {
        "sensorName": sensor_name,
        "subscriptionID": subscription_id,
        "timestamp": time.time()
    }

    target_url = eventsource_map[sensor_name]

    try:
        res = requests.post(
            url=target_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        print(f"[{i+1:03}] ✅ Sent to {target_url}: {subscription_id} (Status {res.status_code})")
    except Exception as e:
        print(f"[{i+1:03}] ❌ Failed to send to {target_url}: {e}")

    time.sleep(0.2)  # 필요한 경우 조절