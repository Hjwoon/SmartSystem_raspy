# SmartSystem_raspy
2 - 2 모바일스마트시스템(파이썬) 라즈베리파이를 활용한 미니프로젝트


## 라즈베리파이를 이용한 스마트 독거노인 관리 시스템

#### 1. 작품 개요
“서울 은평구서 70대 독거노인 고독사…10여일만 발견”(NEWSIS, 2023). 우리 주변에는
지금도 애틋했던 자식들과 연락이 미처 닿지 못한 채 단칸방에서 쓸쓸히 말로를 맞이하는 노인들이 수없이 많다.
이와 같은 독거노인들을 위한 간단한 스마트 응급 관리 시스템은 큰 도움이 될 것으로 생각된다. 
건강 이슈가 발생할 경우, 실시간으로 시스템이 측정하고 데이터를 전송해 준다면 적어도 고독사까지 이르는 상황을 줄일 수 있을 것으로 
기대하며 이러한 시스템을 고안하게 되었다.
이 시스템은 일정한 시간 간격으로 초음파 센서를 활용하여 독거노인의 건강 상태 측정한다. 
초음파 센서에 거리 변화를 주어 ‘건강 이상 없음.’ 상태를 기록한다. 
이때, 초음파 센서에 거리 변화가 없을 시 웹 브라우저에 접속하면 카메라를 연결하여 노인의 현재 상태를 촬영한다. 
다른 기능으로는 실내 온도를 측정하고 최적 온도를 유지하라는 알림을 발생시키는 기능, 
조도 센서를 활용한 실내 LED 장치 조절 등의 기능이 있다. 
예상되는 시스템 구조는 다음 그림과 같다.

<img width="314" alt="image" src="https://github.com/Hjwoon/SmartSystem_raspy/assets/100463930/7dcfa3de-35a2-4e1f-b559-2addb1d082cc">

#### 2. 구현 방법
2.1 하드웨어 부분
라즈베리파이에 카메라 1대, 초음파센서 1개, LED 2개, 조도 센서, 온도 센서, MCP3202 
칩 1개, 저항, 스위치를 사용한다.
이들의 각 GPIO 핀은 다음과 같다.
LED 1 – GPIO 5(출력용)
LED 2 – GPIO 6(출력용)
초음파 센서 – Trigger 핀 : GPIO 20
 Echo 핀: GPIO 16
스위치 – GPIO 21(입력용)
카메라 – 카메라 모듈을 라즈베리파이에 연결하면 별도의 GPIO 설정할 필요 없음
조도 센서, MCP202 칩 – GPIO 20(SPI0_MOSI 신호)
 GPIO 9(SPI0_MOSI 신호)
 GPIO 11(SPI0_SCLK 신호)
 GPIO 8(SPI0_CE0 신호)
온도 센서 – GPIO 2(SDA핀), GPIO 3(SCL핀)

<img width="306" alt="image" src="https://github.com/Hjwoon/SmartSystem_raspy/assets/100463930/a0388843-d787-4ee6-bc88-83ce5bb45174">

2.2 소프트웨어 부분
이 프로젝트는 라즈베리파이에서 작동하는 파이썬 코드, Flask 웹 애플리케이션, HTML 
및 JavaScript로 구성된다.
- 파이썬 코드: 라즈베리 파이에서 실행된다. F카메라 모듈을 사용하여 사진을 촬영하고 저장한다.
- 초음파 센서, LED, 조도 센서, 온도 센서, 스위치를 제어하고 센서 데이터를 읽는다. Flask 웹 애플리케이션과 상호작용하여 데이터를 전달한다. GPIO 핀 및 카메라 모듈을 제어하기 위해 라이브러리를 사용한다.
- Flask 웹 애플리케이션(Flask App): 파이썬 코드와 상호작용하여 데이터를 수신하고 웹 페이지를 제공한다. 웹 브라우저로부터의 요청을 처리하고 응답을 반환한다. 웹 서버로 동작하며 요청을 처리한다.
- 웹 페이지를 렌더링하는데 사용된다. 웹 브라우저에서 사용자에게 보여질 페이지 레이아웃을 정의한다.

#### 3. 실행과정 및 결과
3.1 초기 건강 상태 측정
<img width="209" alt="image" src="https://github.com/Hjwoon/SmartSystem_raspy/assets/100463930/3468085e-3b61-4400-a5df-d4924e4884af">
측정 후 이상 없을 시, 실내 온도 측정 단계로 넘어가는 모습
<img width="214" alt="image" src="https://github.com/Hjwoon/SmartSystem_raspy/assets/100463930/93430910-c287-4dd9-80b8-47e7dd56b3b4">
이상 감지, 웹 서버 접속
<img width="149" alt="image" src="https://github.com/Hjwoon/SmartSystem_raspy/assets/100463930/0007eb28-d801-447a-9913-94ba043cd22e">

3.2 어두울 때LED 2개 모두 ON, 실내에서는 1개만 ON(밝은 실내 점점 어두워짐, 어두운 실내 점점 LED 밝아짐)
<img width="192" alt="image" src="https://github.com/Hjwoon/SmartSystem_raspy/assets/100463930/f9a33775-a318-46f7-939c-e8dccb6aa29b">

3.3
웹 브라우저에 접속한 후, 카메라에 연결했을 때
<img width="245" alt="image" src="https://github.com/Hjwoon/SmartSystem_raspy/assets/100463930/9b518e70-2aaa-4128-be01-0cd3ed8d55d1">
