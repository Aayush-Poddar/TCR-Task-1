# -*- coding: utf-8 -*-
"""
Created on Sun May 23 12:07:48 2021

@author: user
"""

from flask import Flask, render_template, Response,jsonify
import cv2
import numpy as np

app = Flask(__name__)

def gen_frames():  
  video = cv2.VideoCapture(0,cv2.CAP_DSHOW)  
  while True:
    check,frame=video.read()

    frame2=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    l_r = np.array([36, 50, 70])
    u_r = np.array([89, 255, 255])
    
    mask=cv2.inRange(frame2,l_r,u_r)
    res=cv2.bitwise_and(frame,frame,mask=mask)
    gray=cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
    gray=cv2.medianBlur(gray,5)
    
    width  = video.get(3)
    height = video.get(4)
    area_frame=width*height
    global ball_detected
    ball_detected="Ball Not Detected"
    global percentage_of_area
    percentage_of_area="No Ball"
    global corner
    corner="No Ball"
    
    circles=cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,150,param1=200,param2=18,minRadius=0,maxRadius=0)
    if circles is not None:
         circles = np.round(circles[0, :]).astype("int")
         
         ball_detected="Ball Detected"
         
         r=circles[0][2]
         area_of_ball=3.14*r*r
         percentage_of_area=str((area_of_ball/area_frame)*100)
         
         x=circles[0][0]
         y=circles[0][1]
         if x < width//2 and y < height//2:
              corner = "Top Left"
         elif x < width//2 and y > height//2 :
              corner = "Bottom Left"
         elif x > width//2 and y < height//2 :
              corner = "Top Right"
         else :
              corner = "Bottom Right"
         
         font=cv2.FONT_HERSHEY_SIMPLEX
         cv2.putText(frame,"Green Ball",(circles[0][0]+circles[0][2]+1,circles[0][1]),font,1,(0,0,255),2)
         for (x,y,r) in circles:
            cv2.circle(frame, (x,y), r, (0,0,255), 4)
            cv2.circle(frame,(x,y),2,(0,0,255),3)   
            
    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    key=cv2.waitKey(1)
    
    if key==ord('s'):
        break    
    if not check:
        break
    
  video.release()
  cv2.destroyAllWindows() 


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/send_data")
def send_data() :
    return jsonify(ball_detected=ball_detected, percentage_of_area=percentage_of_area, corner=corner)

if __name__ == '__main__':
    app.run()