from flask import Flask, Response, render_template, request, session
from camera import VideoCamera
from speech import TextRecorder
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import speech
import camera
import settings
import time
import operator

app = Flask(__name__,static_url_path="/static")
capture_duration = 10
spoken_text = ""

emotions = []

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):

    start_time = time.time()
    while (int(time.time() - start_time) < capture_duration):
        settings.init()
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if len(settings.myList) != 0:
            emotions.append(settings.myList[0][0])
            print(settings.myList[0][0])
            
def sentiment_analysis(sentiment_text):

    score = SentimentIntensityAnalyzer().polarity_scores(sentiment_text)

    neg = score['neg']

    pos = score['pos']

    if neg > pos:
        return("Negative :(")
    elif pos > neg:
        return("Positive :)")
    else:
        return("Neutral")

def classify(text):
    while True:
        global spoken_text
        result = text.run()
        spoken_text = result
        final = sentiment_analysis(result)

        return final
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/new.html')
def newlog():
    return render_template('new.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/results')
def results():
    classified_text = TextRecorder()

    final_result = classify(classified_text)

    output = "What you said: "+ spoken_text + "\nSentiment analysis: " + final_result

    return render_template("results.html", results = output)

    # return Response(output)

if __name__ == '__main__':
    app.run(host='localhost', debug = True)