from flask import Flask

# Flask 앱 생성
app = Flask(__name__)

# http://127.0.0.1:5000/ 주소로 접속하면
@app.route('/')
def home():
    return "안녕하세요! Flask 서버가 작동 중입니다."

# 이 파일을 직접 실행했을 때만 서버를 가동
if __name__ == '__main__':
    app.run(debug=True, port=5000)