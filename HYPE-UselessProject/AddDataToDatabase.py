import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://hype-useless-project-79017-default-rtdb.firebaseio.com/"
})

ref = db.reference('Persons')

data = {
    "100000": {
        "name": "Sidharth Manikuttan",
        "Future": "Billionaire",
        "Since": "2002",  
        "No_of_Times_Motivated": 0,
        "AKA": "Code Sensei",
        "Failure Probability": "0",  
        "last_motivated_on": "2024-11-03 10:00:00"
    },
    "100001": {
        "name": "Emly Blunt",
        "Future": "Actress",
        "Since": "2023",  
        "No_of_Times_Motivated": 0,
        "AKA": "The Beautiful",
        "Failure Probability": "8",  
        "last_motivated_on": "2024-11-03 10:00:00"
    },
    "100002": {
        "name": "Elon Musk",
        "Future": "Trillionaire",
        "Since": "2023",  
        "No_of_Times_Motivated": 0,
        "AKA": "Tony Stark",
        "Failure Probability": "2",  
        "last_motivated_on": "2024-11-03 10:00:00"
    }
}

for key, value in data.items():
    try:
        ref.child(key).set(value)
        print(f"Successfully added data for ID: {key}")
    except Exception as e:
        print(f"Error adding data for ID {key}: {str(e)}")