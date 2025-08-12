import os
from flask import Flask, render_template
from booklist import booklist_bp
from imageslist import imageslist_bp
from videolist import videolist_bp
from txt2voice import txt2voice_bp
from videomerge import videomerge_bp

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(booklist_bp)
app.register_blueprint(imageslist_bp)
app.register_blueprint(videolist_bp)
app.register_blueprint(txt2voice_bp)
app.register_blueprint(videomerge_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
