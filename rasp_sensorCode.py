# project.py


import io
import cv2
import RPi.GPIO as GPIO
import time
import subprocess  # subprocess 모듈 추가
from PIL import Image, ImageFilter
import paho.mqtt.client as mqtt

# pin에 연결된 LED에 value(0/1) 값을 출력하여 LED를 켜거나 끄는 함수
def led_on_off(pin, value):
    GPIO.output(pin, value)

GPIO.setmode(GPIO.BCM)  # BCM 모드로 작동
GPIO.setwarnings(False)  # 경고 메시지를 출력하지 않도록 설정

trig = 20  # GPIO20
echo = 16  # GPIO16
led1 = 6  # GPIO6 핀
led2 = 5  # GPIO5 핀

ON = 1  # 1은 디지털 출력 값. 1 = 5V
OFF = 0  # 0은 디지털 출력 값. 0 = 0V

GPIO.setup(led1, GPIO.OUT)  # GPIO6 핀을 출력으로 설정
GPIO.setup(led2, GPIO.OUT)  # GPIO5 핀을 출력으로 설정
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

broker_ip = "localhost"
image_file_path = "/home/pi/MiniProject/MyCamera/images"  # 이미지 파일 경로

client = mqtt.Client()
client.connect(broker_ip, 1883)  # 1883 포트로 mosquitto에 접속
client.loop_start()  # 메시지 루프를 실행하는 스레드 생성


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

try:
    previousDistance = -10  # 이전 거리
    distanceChange = 50 # 거리 변화, 10 이내일 때, 초기값 50으로 설정 

    while True:
        distance = measureDistance(trig, echo) # 카메라로부터의 거리
        distanceChange = abs(previousDistance - distance)
        time.sleep(5)

        # 거리변화 10 이내 LED ON
        if distanceChange < 10:
            led_on_off(led1, ON)  # 10cm 이내, 2개 LED 모두 켬
            led_on_off(led2, ON)

            # 거리 변화가 없을 때 cameraapp.py 실행
            subprocess.run(["python3", "cameraapp.py"], capture_output = True)


        # 기록된 distance 이전 거리로 옮김
        previousDistance = distance
except KeyboardInterrupt:
    print("Ctrl+C로 종료")
finally:
    print("클린업")
    GPIO.cleanup()
    client.loop_stop()  # 메시지 루프를 실행하는 스레드 종료
    client.disconnect()
