import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime

#to update real-time database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-system-ea099-default-rtdb.firebaseio.com/",
    "storageBucket":"attendance-system-ea099.appspot.com"})

bucket=storage.bucket()

cap=cv2.VideoCapture(0)
cap.set(3,640)#hight of cam to fit in background
cap.set(4,480)#width

imgbackground=cv2.imread("Resources/background.png")

#importing all the images use in this project
foldermodepath="Resources/Modes"
modepath=os.listdir(foldermodepath)
imgmodelist=[]#contain all the images
for i in modepath:
    imgmodelist.append(cv2.imread (os.path.join(foldermodepath,i)))
#print(len(imgmodelist)) checking
    
#load the encoded files
file=open("EncodeFile.p","rb")
encodeListKnownWithId= pickle.load(file)
file.close()
encodeListKnown,studentid=encodeListKnownWithId
#print(studentid)

modeType=0
counter=0
id=-1
imgStudent=[]

while True:
    sucess, img=cap.read()

    imgs=cv2.resize(img,(0,0),None,0.25,0.25)#here i covert the image into smaller size because biger image take more resources
    imgs=cv2.cvtColor(imgs,cv2.COLOR_BGR2RGB)#here i change the color 

    facecurframe=face_recognition.face_locations(imgs)
    encodecurframe=face_recognition.face_encodings(imgs,facecurframe)#encode the pic come from cam

    imgbackground[162:162+480,55:55+640]=img #putting can to frame
    imgbackground[44:44+633,808:808+414]=imgmodelist[modeType]
    if facecurframe:
        for encodeFace,faceLoc in zip(encodecurframe,facecurframe):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)

            matchIndex=np.argmin(faceDis)
            if matches[matchIndex]:
                '''print("known face dected")
                print(studentid[matchIndex])'''
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgbackground = cvzone.cornerRect(imgbackground, bbox, rt=0)
                id=studentid[matchIndex]
                if counter == 0:
                    counter=1
                    modeType=1

        if counter!=0:

            if counter==1:
                studentinfo=db.reference(f'students/{id}').get()
                #print(studentinfo)

                #getting image from database
                blob=bucket.get_blob(f"Images/{id}.jpg")
                array=np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                #updating attendance
                datetimeObject = datetime.strptime(studentinfo['last_attendance_time'],
                                                    "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                #print(secondsElapsed)
                if secondsElapsed>30:
                    ref=db.reference(f"students/{id}")
                    studentinfo["total_attendance"] +=1
                    ref.child("total_attendance").set(studentinfo["total_attendance"])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType=3
                    counter=0
                    imgbackground[44:44+633,808:808+414]=imgmodelist[modeType]


            if modeType != 3:

                if 10<counter<20:
                        modeType=2

                imgbackground[44:44+633,808:808+414]=imgmodelist[modeType]            

                if counter<=10:
                    cv2.putText(imgbackground,str(studentinfo["total_attendance"]),(861,125),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgbackground,str(studentinfo["major"]),(1006,550),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgbackground,str(studentinfo["starting_year"]),(1125,625),
                                cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgbackground,str(studentinfo["year"]),(1025,625),
                                cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgbackground,str(studentinfo["standing"]),(910,625),
                                cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgbackground,str(id),(1002,493),
                                cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    
                    (w,h),_=cv2.getTextSize(studentinfo["Name"],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    ofsets=(414-w)//2
                    cv2.putText(imgbackground,str(studentinfo["Name"]),(808+ofsets,445),
                                cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)
                    
                    imgbackground[175:175+216,909:909+216]=imgStudent
                counter+=1
                if counter>=20:
                    studentinfo=[]
                    counter=0
                    imgStudent=[]
                    modeType=0
                    imgbackground[44:44+633,808:808+414]=imgmodelist[modeType]
    else:
        modeType=0
        counter=0

    #cv2.imshow("cam",img) checking
    cv2.imshow("face attendance",imgbackground)
    if cv2.waitKey(10)==ord("R"):
        break
#cap.release()