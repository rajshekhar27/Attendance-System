import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-system-ea099-default-rtdb.firebaseio.com/"
})

ref =db.reference("students")

data = { 
    "23scse2160021" : 
        {"Name":"Raj Shekhar",
         "major":"Development",
         "total_attendance":7,
         "starting_year":2023,
         "standing":"G",
         "year":1,
         "last_attendance_time":"2024-01-06 00:54:53"},
    "13269":
        {"Name":"Rahul panday",
         "major":"Robotics",
         "total_attendance":4,
         "starting_year":2023,
         "standing":"B",
         "year":1,
         "last_attendance_time":"2024-01-06 00:54:53"
         },
    "23scse2160060":
        {"Name":"abhinav",
         "major":"3D",
         "total_attendance":9,
         "starting_year":2023,
         "standing":"v.G",
         "year":1,
         "last_attendance_time":"2024-01-06 00:54:53"
        },
    "22scse20230168":
        {"Name":"Parth kumar",
         "major":"Frontend",
         "total_attendance":10,
         "starting_year":2022,
         "standing":"G",
         "year":2,
         "last_attendance_time":"2024-01-06 00:54:53"
         },
        
}

for key,value in data.items():
    ref.child(key).set(value)
    