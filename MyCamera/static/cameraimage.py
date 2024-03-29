// 전역 변수 선언
let canvas;
let context;
let img;

// load 이벤트 리스너 등록. 웹페이지가 로딩된 후 실행 
window.addEventListener("load", function() {
        canvas = document.getElementById("myCanvas");
        context = canvas.getContext("2d");

        img = new Image();
        img.onload = function () {
                context.drawImage(img, 0, 0, canvas.width, canvas.height); // (0,0) 위치에 img의 크기로 그리기
        }
});

function bytes2base64( bytes ) { // 바이너리 데이터를 base64 문자 코드로 변환하는 함수
	let binary = '';
	bytes = new Uint8Array( bytes );
	let len = bytes.byteLength;
	for (let i = 0; i < len; i++) {
		binary += String.fromCharCode( bytes[ i ] );
	}
	return window.btoa( binary );
}

// drawImage()는 "image' 토픽이 도착하였을 때 onMessageArrived()에 의해 호출된다.
function drawImage(bytes) { // bytes는 서버로부터 받은 JPEG 이미지 바이너리 형태
        img.src = "data:image/jpg;base64," + bytes2base64(bytes); // img 객체에 "load" 이벤트 발생
}

let isImageSubscribed = false;
function startCamera() {
    if (!isImageSubscribed) {
        subscribe('image'); // 토픽 image 등록
        isImageSubscribed = true;
    }
    publish('camera', 'start'); // 토픽: camera, 값: start 메시지 전송. 카메라 촬영 후 JPEG 이미지 보내도록 지시
}

function stopCamera() {
    if (isImageSubscribed) {
        unsubscribe('image'); // 토픽 image 등록 취소
        isImageSubscribed = false;
    }
    publish('camera', 'stop'); // 토픽: camera, 값: stop 메시지 전송. 카메라 촬영 중지
}


// 차트 js 합치기

let ctx = null;
let chart = null;
let config = {
	// type은 차트 종류 지정
	type: 'line', // 라인그래프
	// data는 차트에 출력될 전체 데이터 표현
	data: {
		// labels는 배열로 데이터의 레이블들
		labels: [],
		// datasets 배열로 이 차트에 그려질 모든 데이터 셋 표현. 그래프 1개만 있음
		datasets: [{
			label: '조도 센서로부터 측정된 실시간 조도값',
			backgroundColor: 'blue',
			borderColor: 'rgb(255, 99, 132)',
			borderWidth: 2,
			data: [], // 각 레이블에 해당하는 데이터
			fill : false, // 채우지 않고 그리기
		}]
	},
	// 차트의 속성 지정
	options: {
		responsive : false, // 크기 조절 금지
		scales: { // x축과 y축 정보
			xAxes: [{
				display: true,
				scaleLabel: { display: true, labelString: '시간(초)' },
			}],
			yAxes: [{
				display: true,
				scaleLabel: { display: true, labelString: '조도 값' }
			}]
		}
	}
};

let LABEL_SIZE = 20; // 차트에 그려지는 데이터의 개수 
let tick = 0; // 도착한 데이터의 개수임, tick의 범위는 0에서 99까지만 

function drawChart() {
	ctx = document.getElementById('canvas').getContext('2d');
	chart = new Chart(ctx, config);
	init();
} 

function init() { // chart.data.labels의 크기를 LABEL_SIZE로 만들고 0~19까지 레이블 붙이기
	for(let i=0; i<LABEL_SIZE; i++) {
		chart.data.labels[i] = i;
	}
	chart.update();
}

function addChartData(value) {
	tick++; // 도착한 데이터의 개수 증가
	tick %= 100; // tick의 범위는 0에서 99까지만. 100보다 크면 다시 0부터 시작
	let n = chart.data.datasets[0].data.length; // 현재 데이터의 개수 
	if(n < LABEL_SIZE) // 현재 데이터 개수가 LABEL_SIZE보다 작은 경우
		chart.data.datasets[0].data.push(value);
	else { // 현재 데이터 개수가 LABEL_SIZE를 넘어서는 경우
		// 새 데이터 value 삽입
		chart.data.datasets[0].data.push(value); // value를 data[]의 맨 끝에 추가
		chart.data.datasets[0].data.shift(); // data[]의 맨 앞에 있는 데이터 제거

		// 레이블 삽입
		chart.data.labels.push(tick); // tick 값을 labels[]의 맨 끝에 추가
		chart.data.labels.shift(); // labels[]의 맨 앞에 있는 값 제거
	}
	chart.update();

}

function hideshow() { // 캔버스 보이기 숨기기 
	let canvas =  document.getElementById('canvas'); // canvas DOM 객체 알아내기
	if(canvas.style.display == "none") // canvas 객체가 보이지 않는다면
		canvas.style.display = "inline-block"; // canvas 객체를 보이게 배치
	else 
		canvas.style.display = "none" ;  // canvas 객체를 보이지 않게 배치
}

window.addEventListener("load", drawChart); // load 이벤트가 발생하면 drawChart() 호출하도록 등록

 
