# from flask import Flask, render_template, Response
# import numpy as np
# import time
# import cv2
# import os
# import imutils
# import subprocess
# from gtts import gTTS
# from pydub import AudioSegment
# import requests
# # Initialize VideoCapture (use the appropriate camera index or video file path)
# cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
# frame_count = 0
# start = time.time()
# first = True
# frames = []
# server_url = 'http://127.0.0.1:5000/process_image'

# while True:

#     success, frame = cap.read()  # read the camera frame

#     if not success:
#         break
#     ret, buffer = cv2.imencode('.jpg', frame)
#     frame = buffer.tobytes()
                
# # Define the server URL where you want to send the video frames

# # if not cap.isOpened():
# #     print("Error: VideoCapture could not be opened")

# # while cap.isOpened():
# #     ret, frame = cap.read()
# #     if not ret:
# #         break

# #     # Encode the frame as JPEG
# #     _, encoded_frame = cv2.imencode('.jpg', frame)

# #     # Convert the encoded frame to a bytes object
# #     frame_bytes = encoded_frame.tobytes()

#     # Send the frame to the server
#     try:
#         response = requests.post(server_url, data=frame, headers={'Content-Type': 'image/jpeg'})
#         if response.status_code != 200:
#             print(f"Failed to send frame. Status code: {response.status_code}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error sending frame: {e}")
    

# cap.release()




from flask import Flask, render_template, Response
import cv2
import time
import requests
import subprocess
from gtts import gTTS
from pydub import AudioSegment

app = Flask(__name__)

# Initialize VideoCapture (use the appropriate camera index or video file path)
cap = cv2.VideoCapture(0)
server_url = 'http://127.0.0.1:5000/process_image'
text_url = 'http://127.0.0.1:5000/get_text'

def fetch_text_data():
    try:
        response = requests.get(text_url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching text data: {e}")
        return []
# Route to render the index.html template

@app.route('/')
def index():
    return render_template('index.html')

# Route to stream video frames
def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
                
        # Send the frame to the server
        try:
            response = requests.post(server_url, data=frame, headers={'Content-Type': 'image/jpeg'})
            # print(response)
            if response.status_code != 200:
                print(f"Failed to send frame. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending frame: {e}")

      
        text_data = fetch_text_data()
        if text_data:
            print(text_data)
        if text_data:
            description = ', '.join(text_data)
            tts = gTTS(description, lang='en', tld="com")
           
            tts.save('static/tts.mp3')
            tts = AudioSegment.from_mp3("static/tts.mp3")
            subprocess.call(["ffplay", "-nodisp", "-autoexit", "static/tts.mp3"])

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=3000)