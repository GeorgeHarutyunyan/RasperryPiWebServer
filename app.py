from flask_socketio import SocketIO,emit
import serial
import time
from flask import Flask, render_template
import threading

app = Flask(__name__)

socketio = SocketIO(app)

#Handles annoying problem where replugging the Arduino through USB to RaspberryPi changes the path 
#to the device to either USB0 or USB1
try:
    ser = serial.Serial('/dev/ttyUSB0',115200,timeout=1)
except serial.serialutil.SerialException:
    ser = serial.Serial('/dev/ttyUSB1',115200,timeout=1)
ser.flush()
    

@app.route('/')
def index():
    return render_template('index.html')
    
#when Arduino sends message to RaspberryPi
@socketio.on('message event')
def process_message(message):
    emit('message event', message)
    print("Message from arduino: ",message)

#when data must be sent to Arudino
@socketio.on('arduino message')
def process_arduino_message(message):
    ser.write(str.encode(message+"\n"))
    print("Message to arduino: ",message)

@socketio.on('connect')
def test_connect():
    print("Client connected")

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

#Reads data from Arduino and processes messages to the SocketIO
def read_serial_data():
    count = 0
    while True: 
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8',errors='replace').rstrip()
            time.sleep(0.1)
            print("Data: ",line)
            if line and line != None:
                if line[0:8] == "message:": #to not display unnecessary serial data
                    socketio.emit('message event',line[8:])

                
def run_flask():
    socketio.run(app,host='0.0.0.0')
    
def run_app():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    serial_thread = threading.Thread(target=read_serial_data)
    serial_thread.start()
    
if __name__ == '__main__':
    run_app()
