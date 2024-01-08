import io
import cv2
import RPi.GPIO as GPIO
import time
import subprocess  # subprocess 모듈
from PIL import Image, ImageFilter
import paho.mqtt.client as mqtt
import Adafruit_MCP3008
from adafruit_htu21d import HTU21D
import busio
import sys # 출력 관련


### LED 센서 제어 ###

# pin에 연결된 LED에 value(0/1) 값을 출력하여 LED를 켜거나 끄는 함수
def led_on_off(pin, value):
    GPIO.output(pin, value)

GPIO.setmode(GPIO.BCM)  # BCM 모드로 작동
GPIO.setwarnings(False)  # 경고 메시지를 출력하지 않도록 설정

trig = 20  # GPIO20
echo = 16  # GPIO16
led1 = 6   # GPIO6 핀
led2 = 5   # GPIO5 핀
sda = 2    # GPIO2 핀. sda 이름이 붙여진 핀
scl = 3    # GPIO3 핀. scl 이름이 붙여진 핀

ON = 1  # 1은 디지털 출력 값. 1 = 5V
OFF = 0  # 0은 디지털 출력 값. 0 = 0V


def increase(pwm):
    for value in range(0, 100):  # 5초 동안 루프
        pwm.ChangeDutyCycle(value)
        time.sleep(0.05)

def decrease(pwm):
    for value in range(99, -1, -1):  # 5초 동안 루프
        pwm.ChangeDutyCycle(value)
        time.sleep(0.05)


### 카메라 모듈, 서버 제어 ###

broker_ip = "localhost"

client = mqtt.Client()
client.connect(broker_ip, 1883)  # 1883 포트로 mosquitto에 접속
client.loop_start()  # 메시지 루프를 실행하는 스레드 생성


### 초음파 센서 제어 ###

# 초음파를 사용하여 거리 측정
def measureDistance(trig, echo):
    GPIO.output(trig, 1)  # trig 핀 신호 High
    time.sleep(0.00001)  # 잠시 대기 (10 마이크로초)
    GPIO.output(trig, 0)  # trig 핀 신호 Low

    while GPIO.input(echo) == 0:
        pass

    pulse_start = time.time()
    while GPIO.input(echo) == 1:
        pass

    pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    return pulse_duration * 340 * 100 / 2  # 거리를 계산하여 반환 (단위 cm)


### 조도 센서 제어 ###

from adafruit_htu21d import HTU21D
import busio

mcp = Adafruit_MCP3008.MCP3008(clk=11, cs=8, miso=9, mosi=10)


### 온도 센서 제어 ###

# 센서로부터 온도 값을 수신하여 리턴하는 함수
def getTemperature(sensor) :
    return float(sensor.temperature)

i2c = busio.I2C(scl, sda) # I2C 버스 통신을 실행하는 객체 생성
sensor = HTU21D(i2c) # I2C 버스에서 HTU21D 장치를 제어하는 객체 리턴
THRESHOLD = 27 # 체크할 온도
prev_temp = 0 # 0으로 초기화


### 서버 통신 제어 ###

client = mqtt.Client()
client.connect(broker_ip, 1883)  # 1883 포트로 mosquitto에 접속
client.loop_start()  # 메시지 루프를 실행하는 스레드 생성


# GPIO 핀 초기화
GPIO.setup(led1, GPIO.OUT)  # GPIO6 핀을 출력으로 설정
GPIO.setup(led2, GPIO.OUT)  # GPIO5 핀을 출력으로 설정
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

pwm = GPIO.PWM(led1, 100)  # GPIO6 핀에 100Hz의 신호를 발생하도록 설정
pwm.start(0)  # GPIO6 핀에 듀티 사이클 0%, 100Hz의 신호 발생 시작



try:
    # 30초간 건강 이상 확인 측정(초음파 센서로 움직임 감지)
    timer = 10 # 원래 30초, 간단한 측정 예시 위해 5초로 임의 변경
    preDistance = 0 # 이전 거리
    distanceChange = 100

    while True:
        if timer == 0: # 측정시간 종료
            break 

        print("건강 측정 중입니다.")

        # 거리 변화 5 이내 응급 발생 의심, 실시간 송출 서버 연결
        if distanceChange == 0:
            print("응급상황 발생 의심")
            # 상황 발생 시, cameraapp.py 실행
            subprocess.run(["python3", "cameraapp.py"], capture_output=True)         

        distance = measureDistance(trig, echo) # 카메라로부터의 거리
        distanceChange = abs(preDistance - distance)

        # 기록된 distance 이전 거리로 옮김
        preDistance = distance
        timer -= 1 # 1초씩 감소
        time.sleep(0.5) 


    # 온습도, 조도, LED 켜기
    while True:
        illuminanceValue = mcp.read_adc(0)  # channel 0에 연결된 조도 센서로부터 조도값 읽기
        cur_temp = getTemperature(sensor)

        # 터미널 화면을 지우고 커서를 처음으로 위치시키기
        sys.stdout.write("\033[H\033[J")

        # 500 이하: 두 개의 LED 모두 켜기, 1,000 이상: 두 개의 LED 모두 끄기
        if illuminanceValue <= 500:
            led_on_off(led1, ON)
            led_on_off(led2, ON)
        elif illuminanceValue < 1000:  # 500 초과 20,000 미만: 실내 밝기, LED 1개 ON(LED1)
            if illuminanceValue < 500:  # 어두운 실내
                increase(pwm)  # 5초동안 듀티 사이클 증가. LED1을 점점 밝게
            else:  # 밝은 실내
                decrease(pwm)  # 5초동안 듀티 사이클 감소. LED1을 점점 어둡게
        else:  # 1,000 이상: 야외 밝기, LED OFF
            led_on_off(led1, OFF)
            led_on_off(led2, OFF)

        print("실내 온도: %4.1d" % cur_temp)

        if cur_temp > 30:
            print("실내 온도를 낮추세요.")
        elif cur_temp < 18:
            print("실내 온도를 높이세요.")

        client.publish("illuminance", illuminanceValue, qos=0) # "illuminance" 토픽으로 조도값 전송
        time.sleep(5)

except KeyboardInterrupt:
    print("Ctrl+C로 종료")
finally:
    print("클린업")
    GPIO.cleanup()
    client.loop_stop()  # 메시지 루프를 실행하는 스레드 종료
    client.disconnect()
