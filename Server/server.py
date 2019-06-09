from flask import Flask, g, session
from flask_socketio import SocketIO, send, emit
import io
import base64
import cv2
from imageio import imread
import time
from emotions import final_ml_predict as ml_predict

app = Flask(__name__)
socketio = SocketIO(app)

with app.app_context():
    g.emotions = []
    g.timestamp = []
    
@app.route("/")
def hello():
    return "Hello World!"

@socketio.on('image&ac', namespace=r'/ml')
def handle_my_custom_event(message, activated):
    print('Got image')
    if not hasattr(session, "emotions"):
        session.emotions = []
    if not hasattr(session, "timestamp"):
        session.timestamp = []
    
    image = message['image']
    img = imread(io.BytesIO(base64.b64decode(image)))
    cv2_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv_result, emotion_text = ml_predict(cv2_img)
    _, buffer = cv2.imencode('.jpg', cv_result)
    result_im = base64.b64encode(buffer).decode('UTF-8')
    #print("Something")
    #print(activated)
    if activated:
        elapsed_time = time.time()
        if emotion_text == 'angry':
            session.emotions.append('angry')
            session.timestamp.append(elapsed_time)            
        elif emotion_text == 'sad':
            session.emotions.append('sad')
            session.timestamp.append(elapsed_time)
        elif emotion_text == 'happy':
            session.emotions.append('happy')
            session.timestamp.append(elapsed_time)
        elif emotion_text == 'surprise':    
            session.emotions.append('surpise')
            session.timestamp.append(elapsed_time)
        else:
            session.emotions.append('neutral')
            session.timestamp.append(elapsed_time)
     #   if timestamp[len(timestamp)-1] - timestamp[0] >30:
     
        emit('timeAndEmotion', (session.timestamp, session.emotions))

    # print('Result: ')
    # print(result_im[:20])
    send({'result': result_im})
    
    if len(session.emotions)%100 == 30:
        print(activated)    
        print(session.emotions)    

if __name__ == '__main__':
    socketio.run(app, port=8000)