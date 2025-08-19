import os
from flask import Flask, render_template
from flask_cors import CORS 
from booklist import booklist_bp
from imageslist import imageslist_bp
from videolist import videolist_bp
from txt2voice import txt2voice_bp
from videomerge import videomerge_bp
from autovideo import autovideo_bp
from autovideo_list import autovideo_list_bp

app = Flask(__name__)

# 精确配置CORS
CORS(app, resources={
    r"/create_video": {
        "origins": ["http://127.0.0.1:5000", "http://47.98.194.143:15678", "http://47.98.194.143:9914"],  # 接受跨域可访问源地址
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 注册蓝图
app.register_blueprint(booklist_bp)
app.register_blueprint(imageslist_bp)
app.register_blueprint(videolist_bp)
app.register_blueprint(txt2voice_bp)
app.register_blueprint(videomerge_bp)
app.register_blueprint(autovideo_bp)
app.register_blueprint(autovideo_list_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
