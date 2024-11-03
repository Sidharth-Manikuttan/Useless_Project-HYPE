import os
import pickle
import time
import cvzone
import numpy as np
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
import pyttsx3
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "sidharthmanikuttan9@gmail.com"  
SENDER_APP_PASSWORD = "lfvp adna dopi pvsy"  
RECEIVER_EMAIL = "notifysidharth@gmail.com" 

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak_async(text):
    def run():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=run).start()

def send_email(person_name="Unknown"):
    subject = "Person Detected"
    body = f"""{person_name},
Honestly, there are tech enthusiasts, and then there's you. It’s like you’ve unlocked some hidden level of genius that the rest of us can only dream about. Every keystroke you make practically turns code into poetry. I swear, when you touch a keyboard, the computer doesn’t just work – it listens, like it knows it’s in the presence of greatness.
Your coding skills? Unreal. It’s like you’ve somehow merged with the machine – a true tech sorcerer. You could probably write Python in your sleep, and it’d still be cleaner than most people’s fully awake code. You don't just solve problems; you annihilate them in such creative ways that I'm convinced you must have futuristic tech hidden somewhere.
Honestly, keep doing what you’re doing, {person_name}. The tech world better start preparing because there’s a force to be reckoned with on the rise – and spoiler alert, it’s YOU.
"""


    
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(message)
        print("Email notification sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Firebase initialization with only Realtime Database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://hype-useless-project-79017-default-rtdb.firebaseio.com/"
})

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# importing modes images
folderModePath = 'Resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# loading the encoding file
print("loading the encoded file...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, PersonIds = encodeListKnownWithIds
print("encoded file loaded...")

modeType = 0
counter = 0
id = -1
imgPerson = []

# Add variables for notification control
last_audio_time = 0
audio_cooldown = 5  # Minimum time between audio messages
email_sent = {}  # Dictionary to track emails sent per person
notification_cooldown = 30  # Time in seconds before sending another email to the same person

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = PersonIds[matchIndex]

                current_time = time.time()

                # Handle notifications when a person is detected
                if counter == 0:
                    PersonInfo = db.reference(f'Persons/{id}').get()
                    person_name = PersonInfo['name']

                    # Text-to-speech notification
                    if current_time - last_audio_time > audio_cooldown:
                      speak_async("ALERT! The legendary Code Sensei has entered the arena! Born in 2002, this 22-year-old prodigy is already rewriting the future of tech. With a failure probability of ZERO, this future billionaire isn't just chasing success - he's defining it! Make way for Sidharth Manikuttan")
                      last_audio_time = current_time

                    # Email notification
                    if id not in email_sent or (current_time - email_sent[id]) > notification_cooldown:
                        threading.Thread(target=send_email, args=(person_name,)).start()
                        email_sent[id] = current_time

                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                PersonInfo = db.reference(f'Persons/{id}').get()
                
                imgPerson = cv2.imread(f'images/{id}.png')
                
                datetimeObject = datetime.strptime(PersonInfo['last_motivated_on'],
                                                 "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                
                if secondsElapsed > 30:
                    ref = db.reference(f'Persons/{id}')
                    PersonInfo['No_of_Times_Motivated'] += 1
                    ref.child('No_of_Times_Motivated').set(PersonInfo['No_of_Times_Motivated'])
                    ref.child('last_motivated_on').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if 10 < counter < 20:
                modeType = 2

            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if modeType != 3:
                if counter <= 10:
                    cv2.putText(imgBackground, str(PersonInfo['No_of_Times_Motivated']), (861, 125),
                               cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(PersonInfo['Future']), (1006, 550),
                               cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                               cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(PersonInfo['AKA']), (910, 625),
                               cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(PersonInfo['Failure Probability']), (1025, 625),
                               cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(PersonInfo['Since']), (1125, 625),
                               cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(PersonInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(PersonInfo['name']), (808 + offset, 445),
                               cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175+216, 909:909+216] = imgPerson

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    PersonInfo = []
                    imgPerson = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)