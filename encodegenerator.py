import cv2
import face_recognition
import os
import pickle

#to send image to database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendance-system-ea099-default-rtdb.firebaseio.com/",
    "storageBucket":"attendance-system-ea099.appspot.com"})


#importing all the images students
foldermodepath="Images"
imgpath=os.listdir(foldermodepath)
imgList=[]#contain all the images of student
studentid=[]
for i in imgpath:
    imgList.append(cv2.imread (os.path.join(foldermodepath,i)))
    #print(os.path.splitext(i)[0])
    studentid.append(os.path.splitext(i)[0])#here i split student id from name of img that contain some image extension 
    #print(studentid) #checking
#print(len(imgList)) #checking
    
    filename=f'{foldermodepath}/{i}'
    bucket=storage.bucket()
    blob=bucket.blob(filename)
    blob.upload_from_filename(filename)
    
'''opencv use the BGR color spaces and face recognition use RGB color space'''
def findEncodings(imgesList):
    encodinglist=[]
    for img in imgesList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)#converting BGR TO RGB beacuse we are taking imput from cv2 and encoding through face-recognition
        encode=face_recognition.face_encodings(img)[0]
        encodinglist.append(encode)
    return encodinglist

encodeListKnown=findEncodings(imgList)
encodeListKnownWithId=[encodeListKnown,studentid]#putting the endoding with student is so that we can get easly
#print(encodeListKnownWithId)

file=open("EncodeFile.p","wb")
pickle.dump(encodeListKnownWithId,file)
file.close()




