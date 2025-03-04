import AIBOT
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.static_folder = 'static'

UPLOAD_FOLDER = 'knowledge_base'  # 上传文件存储的路径
ALLOWED_EXTENSIONS = {'md', 'pdf'}  # 允许上传的文件扩展名
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.debug=True
app.secret_key=os.urandom(24)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(AIBOT.get_response(userText))


# 检查文件扩展名是否合法
def allowed_file(filename):
    print("checking file " + filename)
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 上传文件并重定向用户到上传后的文件URL
@app.route('/upload', methods=['GET', 'POST'])  #ZJR： 是否要去掉GET
def upload_file():
    print("here")
    if request.method == 'POST':
        print("here0")
        # 检查请求中是否包含文件部分
        if 'file' not in request.files:
            print("here2")
            flash('No file part')
            return redirect(request.url)   #ZJR: 是否直接用flask.abort
        file = request.files['file']
        # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空文件
        if file.filename == '':
            print("here3")
            flash('No selected file')
            return redirect(request.url)  #ZJR: 是否直接用flask.abort
        if file and allowed_file(file.filename):
            print("here4")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("route", os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('home')) #ZJR： 这里我直接改成home了
        
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
