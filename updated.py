import cv2

import UpdatedHandTrackingModule as htm
import time
from pynput.mouse import Controller,Button
import tkinter as tk
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import speech_recognition as sr
import pyautogui
import threading
import pyttsx3
import time


root = tk.Tk()
root.withdraw() 
# frameR=150 
frameR=100
mouse = Controller()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
smoothening=4
plocX,plocY=0,0
clocX,clocY=0,0
oldvalue=0
prevX,prevY=0,0
clickcheck=False
rightclick=False
isvirtualKeyboardOn=False
isSelected=False
tempVal=0
doubleClickCount=0
isdoubleClick=False
recognizer = sr.Recognizer()
mic = sr.Microphone()
WAKE_WORD = "jarvis"


engine = pyttsx3.init()
engine.setProperty('rate', 150)




print(f"Screen size: {screen_width}x{screen_height}")


wCam,hCam=640,480
pTime=0
cTime=0
detector=htm.handDetector(maxHands=1)



cap=cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

def say():
    engine.say("How can I help you?")
    engine.runAndWait()

def keyboard():
    global isvirtualKeyboardOn
    isvirtualKeyboardOn=True
    r = sr.Recognizer()



    with sr.Microphone() as source:
        print("Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=2)
        threading.Thread(target=say,daemon=True).start()
        r.energy_threshold = 100
        print("Listening for command...")
        
        
        

        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=5)
            print("Recognizing...")

            text = r.recognize_google(audio)
            print("You said:", text)
            pyautogui.write(text,interval=0.05)


        except sr.WaitTimeoutError:
            print("Timed out waiting for speech.")
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError as e:
            print(f"API error: {e}")


def movement():
    global plocX
    global plocY
    global clocX
    global clocY
    
    x3=np.interp(x1,(frameR,wCam-frameR),(0,screen_width))
    y3=np.interp(y1,(50,hCam-200),(0,screen_height))

    clocX=plocX+(x3-plocX)/smoothening
    clocY=plocY+(y3-plocY)/smoothening
    
    mouse.position = (screen_width-clocX,clocY)
    cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
    plocX,plocY=clocX,clocY


# def movement_chlid():
#     global plocX
#     global plocY
#     global clocX
#     global clocY

#     x3=np.interp(prevX,(frameR,wCam-frameR),(0,screen_width))
#     y3=np.interp(prevY,(50,hCam-200),(0,screen_height))

#     clocX=plocX+(x3-plocX)/smoothening
#     clocY=plocY+(y3-plocY)/smoothening
    
#     mouse.position = (screen_width-clocX,clocY)
#     cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
#     plocX,plocY=clocX,clocY
#     prevX=x1
#     prevY=y1
def listen_command():
    with mic as source:
        print("Listening for command...")
        # recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio).lower()
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError:
            print("Speech recognition service failed")
            return ""

def execute_command(command):
    if "type" in command:
        text_to_type = command.replace("type", "").strip()
        pyautogui.typewrite(text_to_type)
    elif "press enter" in command:
        pyautogui.press("enter")
    elif "press backspace" in command: 
        pyautogui.press("backspace")
    else:
        print("Command not recognized.")

def Ai_keyboard():
    while True:
        print("Waiting for wake word...")
        wake = listen_command()
        if WAKE_WORD in wake:
            threading.Thread(target=say,daemon=True).start()
            print("Wake word detected!")
            command = listen_command()
            execute_command(command)
        time.sleep(0.5)





threading.Thread(target=Ai_keyboard,daemon=True).start()






while True:
    # print(ref)
    success,img=cap.read()
    img=detector.findHands(img,draw=False)
    lmList,bbox=detector.findPosition(img,draw=False)

    if len(lmList)!=0:
        x1,y1=lmList[8][1:]                      
        x2,y2=lmList[12][1:]
        cv2.rectangle(img,(frameR,50),(wCam-frameR,hCam-200),(255,0,255),2)

        fingers=detector.fingersUp()
        # print(fingers)
        if fingers[0]==0 and fingers[1]==1 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0:
            if isSelected:
                 mouse.release(Button.left)
                 isSelected=False
            isdoubleClick=False
            clickcheck=True
            rightclick=True
            isvirtualKeyboardOn=False
            # movement()
            threading.Thread(target=movement,daemon=True).start()
            
    
            
        if fingers[0]==0 and fingers[1]==1 and fingers[2]==1 and fingers[3]==0 and fingers[4]==1:
            length,img,LineInfo=detector.findDistance(8,12,img,draw=True)
            
            if length<40:
                if rightclick:
                    mouse.click(Button.right)
                        
                    rightclick=False
                    print("rightclick")
                
        if fingers[0]==0 and fingers[1]==1 and fingers[2]==1 and fingers[3]==0 and fingers[4]==0:
            length,img,LineInfo=detector.findDistance(8,12,img,draw=False)
            if length<40:
                doubleClickCount=doubleClickCount+1
                if clickcheck:
                    mouse.click(Button.left)
                    
                    clickcheck=False
                    print("click")
                if doubleClickCount>50 and not isdoubleClick:
                    mouse.click(Button.left,2)
                    doubleClickCount=0
                    isdoubleClick=True
                     

        if fingers[0]==0 and fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1:
            mouse.scroll(0,1)


        if fingers[0]==0 and fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==0:
            mouse.scroll(0,-1)

      

        if fingers[0] ==1 and fingers[1]==1 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0:
            qlength,img,LineInfo=detector.findDistance(4,8,img,draw=False)
    
            if isSelected:
                threading.Thread(target=movement,daemon=True).start()
                
            if qlength<40 and not isSelected:
                print("selected")
                mouse.press(Button.left)
                isSelected=True
                
                
                

            elif qlength>40 and isSelected:
                print("release")
                mouse.release(Button.left)
                isSelected=False    



    
        if fingers[2]==0 and fingers[0]==1 and fingers[1]==1 and fingers[4]==1:
            tlength,img,tLineInfo=detector.findDistance(4,8,img)
            cv2.circle(img,(tLineInfo[4],tLineInfo[5]),10,(0,255,0),cv2.FILLED)
            volumeX = np.interp(tlength, (20, 120), (0, 1))  # Maps directly to 0.0 - 1.0
            volumeX = max(0.0, min(volumeX, 1.0))
            volumeX=round(volumeX,1)

            # print(volumeX)    

            try:
                if oldvalue !=volumeX:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevelScalar(volumeX, None)
                    oldvalue=volumeX
            except Exception as e:
                print(e)    

        # if fingers[0]==1 and fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1:
        #     tempVal=tempVal+1

        #     # print("five fingers")

        #     if not isvirtualKeyboardOn and tempVal>30:
        #         print("five fingers")
        #         threading.Thread(target=keyboard,daemon=True).start()
        #         tempVal=0
             
                        

        


    # img=cv2.flip(img,1)   
    cTame=time.time()
    fps=1/(cTame-pTime)
    pTime=cTame
    cv2.putText(img,str(int(fps)),(20,50),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
    # print(fps)
    cv2.imshow("image",img)
    cv2.waitKey(1)   
    
    
    
    
    
    
    
    
    #1. find hand landmarks
    #2. get the tip of the index and middle finger
    #3. check which finger are up
    #4. only index finger :moving mode
    #5. convert coordinates
    #6. smoothen values
    #7. move mouse
    #8. both index and middle fingers are up :clicked mode
    #9. find distance between fingers
    #10. click mouse if distance short
    #11. frame rate
    #12. display
# if fingers[1]==1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1:

#             tlength,img,tLineInfo=detector.findDistance(8,20,img)
#             # cv2.circle(img,(tLineInfo[4],tLineInfo[5]),10,(0,255,0),cv2.FILLED)
#             if tlength<70:
#                 print(y2)
#                 mouse.scroll(0,1)
#                 #y4=np.interp(y2,(50,hCam-200),(,screen_height))