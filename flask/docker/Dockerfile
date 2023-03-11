FROM python:3.9

WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install flask
RUN pip install flask-socketio
RUN pip install blinker
RUN pip install elastic-apm

CMD ["python", "main.py"]