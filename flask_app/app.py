from flask import Flask, url_for, redirect, render_template, request
from flaskwebgui import FlaskUI
from decouple import config
import threading

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.get('/shutdown')
def shutdown_flask_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def _run_flask():
    app.run(host=config("FLASK_IP"), port=config("FLASK_PORT"), debug=True, use_reloader=False)
    print("Flask Server Shutting Down")

def start_flask_thread():
    flask_thread = threading.Thread(
        target=_run_flask,
        daemon=True
    )
    flask_thread.start()



if __name__ == '__main__':
    None