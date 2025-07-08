import network
import time
from machine import Pin, time_pulse_us, PWM
import urequests
import ujson

SSID     = "" #와이파이 이름
PASSWORD = "" #와이파이 비밀번호

SERVER_URL = "" #피코에서 전송한 데이터를 받는 주소, endpoint 포함되어야함.

trig = Pin(20, Pin.OUT)
echo = Pin(12, Pin.IN)
led = Pin(5, Pin.OUT)
buzzer = PWM(Pin(2))

WARNING_FREQ = 2000

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Wi-Fi 연결 중")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Wi-Fi 연결됨:", wlan.ifconfig())

def read_distance(timeout_us=30000):
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    try:
        pulse = time_pulse_us(echo, 1, timeout_us)
    except OSError:
        return None
    return round((pulse * 0.0343) / 2, 2)

def post_distance(dist):
    payload = {
        "distance": dist,
        "status":   "ok" if (dist is not None and dist >= 0) else "invalid"
    }
    if payload["status"] == "invalid":
        payload["error"] = "잘못된 거리값"

    body = ujson.dumps(payload)
    headers = {
        "Content-Type":   "application/json",
        "Content-Length": str(len(body)),
        "Connection":     "close"
    }

    print("POST payload:", body)
    try:
        res = urequests.post(SERVER_URL, data=body, headers=headers)
        print("   응답 코드:", res.status_code)
        print("   응답 바디:", res.text)
        res.close()
    except Exception as e:
        print("POST 오류:", e)

def alert_hardware(dist):
    if dist is None:
        led.off()
        buzzer.duty_u16(0)
        return

    if dist < 20:
        led.on()
        buzzer.freq(WARNING_FREQ)
        buzzer.duty_u16(30000)
    else:
        led.off()
        buzzer.duty_u16(0)

def main():
    connect_wifi()

    try:
        test = urequests.get("") # 서버 주소 입력, 센서데이터 받는 엔드포인트를 포함한 주소로
        print("서버 GET 테스트:", test.status_code)
        test.close()
    except:
        print("서버 연결 테스트 실패")

    while True:
        dist = read_distance()
        print("측정된 거리:", dist)
        post_distance(dist)
        alert_hardware(dist)
        time.sleep(1)

if __name__ == "__main__":
    main()

