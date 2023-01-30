import datetime

from flask import Flask, render_template

from config import conifg
from route.routing import param

# app = Flask(__name__)

# @app.route('/')
# def root():
#     # For the sake of example, use static information to inflate the template.
#     # This will be replaced with real information in later steps.
#     dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
#                    datetime.datetime(2018, 1, 2, 10, 30, 0),
#                    datetime.datetime(2018, 1, 3, 11, 0, 0),
#                    ]
#
#     return render_template('index.html', times=dummy_times)


app = Flask(__name__)
app.register_blueprint(param)

# JSON_AS_ASCII 初期值為 True, 中日文會亂碼
app.config['JSON_AS_ASCII'] = False

# 配置 config class
app.config.from_object(conifg.BaseConfig())

@app.after_request
def after_request(res):
    res.headers.add('Access-Control-Allow-Origin', '*')
    res.headers.add('Access-Control-Allow-Headers', 'Content-Type')  # ORIGIN 跨域
    res.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')

    return res


@app.route("/")
@app.route("/hello")
def hello():
    return "Hello, World!"


# if __name__ == '__main__':
#     app.run()
#

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)