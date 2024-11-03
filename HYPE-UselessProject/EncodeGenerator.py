import cv2
import pickle
import os
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Initialize Firebase with only Realtime Database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://hype-useless-project-79017-default-rtdb.firebaseio.com/"
})

# importing student images
folderPath = 'images'
PathList = os.listdir(folderPath)
print(PathList)

imgList = []
PersonIds = []

# Simply load images from local directory
for path in PathList:
    # Read image directly from the local folder
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # Get student ID from filename (without extension)
    PersonIds.append(os.path.splitext(path)[0])
    print(f"Processed image: {path}")

print(f"Loaded student IDs: {PersonIds}")

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, PersonIds]
print("Encoding Completed")

# Save encodings to pickle file
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File saved")