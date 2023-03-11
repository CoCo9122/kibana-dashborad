from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from elasticapm.contrib.flask import ElasticAPM

from random import random
from datetime import datetime

from math import exp, cos, sin, tanh

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'realtime!'
app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'web-socket-flask',
    'SERVER_URL': 'http://kibana-dashborad-apm-1:8200',
}
apm = ElasticAPM(app)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
        
def background_thread(epoch):

    funcs = {
        'exp' :exp,
        'cos' :cos,
        'sin' :sin,
        'tanh' : tanh
    }

    count = 0
    global thread
    for i in range(int(epoch['epoch'])):
        socketio.sleep(0.5)
        count += 1
        socketio.emit('my_epoch',
                      {'count': count/10, 
                       'data': funcs[epoch['func']](count/10),
                       'epoch': epoch['epoch']},
                      namespace='/')
    thread = None
        
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")
        
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

class RealTimeChart(Namespace):

    def on_my_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']})

    def on_connect(self):
        emit('my_response', {'data': 'Connected', 'count': 0})

    def on_start(self, epoch):
        session['receive_count'] = session.get('receive_count', 0) + 1
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_thread, epoch)

    def on_disconnect_request(self):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'Disconnected!', 'count': session['receive_count']})
        disconnect()

    def on_disconnect(self):
        print('Client disconnected', request.sid)

socketio.on_namespace(RealTimeChart('/'))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')