from flask import Flask
from sklearn.linear_model import LinearRegression
import joblib


app = Flask(__name__)

@app.route('/')
def home():
    return '여긴 쓰나미 예측 서버'
if __name__ == '__main__':
    app.run(port=5000, debug=True)