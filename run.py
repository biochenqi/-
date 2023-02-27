#!/usr/bin/python3.6
from flask import Flask,url_for,render_template,request
from Book_app.Book import book    # 从分路由倒入路由函数
from Meth_app.Meth import meth    # 从分路由倒入路由函数
from flask_bootstrap import Bootstrap

app = Flask(__name__)

# 注册蓝图 第一个参数 是蓝图对象
app.register_blueprint(book)
app.register_blueprint(meth)
bootstrap = Bootstrap(app)

@app.route('/')
def hello_world():
 return render_template('test.html')

if __name__ == '__main__':
 app.run(host='0.0.0.0',port=5500)
