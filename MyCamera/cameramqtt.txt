#publisher 

import io, time
import cv2
from PIL import Image, ImageFilter
import paho.mqtt.client as mqtt
import cv2
import camera
import base64


isStart  = False

def on_connect(client, userdata, msg, rc):
	client.subscribe("camera")

def on_message(client, userdata, msg):
	global isStart
	if msg.payload.decode('utf-8') == 'start':
		isStart = True
		print("Start Camera")
	else:
		isStart = False
	pass
		

broker_ip = "localhost"

client = mqtt.Client()
client.connect(broker_ip, 1883) # 1883 포트로 mosquitto에 접속
client.on_connect = on_connect
client.on_message = on_message

client.loop_start() # 메시지 루프를 실행하는 스레드 생성

camera.init()
stream = io.BytesIO()

while True:
	if isStart == True:
		frame = camera.take_picture()
		stream.seek(0) # stream 파일의 커서를 맨 앞으로 이동한다
		image = Image.fromarray(frame) # numpy array 데이터를 PILLOW의 image 데이터 포맷으로 변환
		image.save(stream, format='JPEG') #이미지 변환후 JPEG 형식으로 이미지를 저장
		
		client.publish("image", stream.getvalue(), qos=0) # image토픽으로 이미지 데이터 전송
		stream.truncate() # stream 파일에 있는 모든 내용을 지운다
	else:
		print("I am idle")
		time.sleep(1000)

camera.release() # 카메라 사용 끝내기
client.loop_stop() # 메시지 루프를 실행하는 스레드 종료
client.disconnect()
