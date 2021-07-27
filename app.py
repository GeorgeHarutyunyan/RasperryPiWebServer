from flask_socketio import SocketIO
import serial
import time
from flask import Flask, render_template
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
thread = None

socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
print(f"socketio Async Mode: {socketio.async_mode}")

#Handles annoying problem where replugging the Arduino through USB to RaspberryPi changes the path 
#to the device to either USB0 or USB1
try:
    ser = serial.Serial('/dev/ttyUSB0',115200,timeout=1)
except serial.serialutil.SerialException:
    ser = serial.Serial('/dev/ttyUSB1',115200,timeout=1)
ser.flush()
    

@app.route('/')
def index():
    global thread
    if thread is None:
        #thread = threading.Thread(target=read_serial_data)
        thread = socketio.start_background_task(target=read_serial_data)
        pass
    return render_template('index.html')

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
    while True: 
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8',errors='replace').rstrip()
            print("Data: ",line)
            if line and line != None:
                if line[0:8] == "message:": #to not display unnecessary serial data
                    socketio.emit('message event',line[8:])
                    print("printable message!! : ",line)
        socketio.sleep(0.2)

    
if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0')
