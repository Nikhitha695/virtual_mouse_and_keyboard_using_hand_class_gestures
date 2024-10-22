import cv2 #used for video capturing
import mediapipe as mp #used for tracking hand and landmarks
import track as track
import pyautogui
from pynput.mouse import Button,Controller
from time import sleep

mouse = Controller()

screen_width,screen_height = pyautogui.size()
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode = False, #only video not image
    model_complexity = 1,
    min_detection_confidence =  0.7,
    min_tracking_confidence = 0.7,
)

keys = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L',';'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M','<','>',',']
]

def move_mouse(index_finger_tip):
    if index_finger_tip is not None:
        x = int(index_finger_tip.x*screen_width)
        y = int(index_finger_tip.y*screen_height)
        pyautogui.moveTo(x,y)

def find_finger_tip(processed):
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]
        return hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
    return None

def left_click(landmarks_list,thumb_index_dist):
    return (track.getangle(landmarks_list[5],landmarks_list[6],landmarks_list[8])<50 and
            track.getangle(landmarks_list[9],landmarks_list[10],landmarks_list[12])>90 and thumb_index_dist>50)

def right_click(landmarks_list,thumb_index_dist):
    return (track.getangle(landmarks_list[9],landmarks_list[10],landmarks_list[12])<50 and
            track.getangle(landmarks_list[5],landmarks_list[6],landmarks_list[8])>90 and thumb_index_dist>50)

def double_click(landmarks_list,thumb_index_dist):
    return (track.getangle(landmarks_list[9],landmarks_list[10],landmarks_list[12])<50 and
            track.getangle(landmarks_list[5],landmarks_list[6],landmarks_list[8])<50 and thumb_index_dist>50)

def screenshot(landmarks_list,thumb_index_dist):
    return (track.getangle(landmarks_list[9],landmarks_list[10],landmarks_list[12])<50 and
            track.getangle(landmarks_list[5],landmarks_list[6],landmarks_list[8])<50 and thumb_index_dist<50)

def detect_gestures(frame,landmarks_list,processed):
    if len(landmarks_list)>=21:
        index_finger_tip = find_finger_tip(processed)
        thumb_index_dist = track.get_distance((landmarks_list[4],landmarks_list[5]))
        if thumb_index_dist<50 and track.getangle(landmarks_list[5],landmarks_list[6],landmarks_list[8])>90:
            move_mouse(index_finger_tip)
        elif left_click(landmarks_list,thumb_index_dist):
            mouse.press(Button.left)
            mouse.release(Button.left)
            cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif right_click(landmarks_list,thumb_index_dist):
            mouse.press(Button.right)
            mouse.release(Button.right)
            cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif double_click(landmarks_list,thumb_index_dist):
            pyautogui.doubleClick()
            cv2.putText(frame,"Double Click",(50,50),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        elif screenshot(landmarks_list, thumb_index_dist):
            im1 = pyautogui.screenshot()
            label = random.randint(1, 1000)
            im1.save(f'my_screenshot_{label}.png')
            cv2.putText(frame, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

#keyboard control
class VirtualButton:
    def __init__(self,pos,text,size=[85,85]):
        self.pos = pos
        self.size=size
        self.text=text

def draw(img,buttonlist):
    for btn in buttonlist:
        x,y = btn.pos
        w,h = btn.size
        cv2.rectangle(img,btn.pos,(x+w,y+h),(255,255,255),cv2.FILLED)
        cv2.putText(img,btn.text,(x+20,y+60),cv2.FONT_HERSHEY_PLAIN,2,(0,0,0),2)
    return img

buttonlist=[]
button_size = [75,75]
x_offset = 50
y_offset = 50
x_spacing = 75
y_spacing = 75

for i,row in enumerate(keys):
    for j,key in enumerate(row):
        x = x_offset + j*x_spacing
        y = y_offset + i*y_spacing
        buttonlist.append(VirtualButton([x,y],key,button_size))

def main():
    cap = cv2.VideoCapture(0)   #initialising VideoCapture object
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280) #setting frame width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720) #setting frame hwight
    draw_utils = mp.solutions.drawing_utils #to draw the landmarks
    while True:
        ret,frame = cap.read()  #ret-sucessfully captured(bool),frame-image captured by webcame
        if not ret:
            break
        frame = cv2.flip(frame,1)  #flip frame horizontally,mirror effect
        frameRGB = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) #colour conversion from BGR to RGB
        processed = hands.process(frameRGB)
        landmarks_list = []
        if processed.multi_hand_landmarks:
            hand_landmarks = processed.multi_hand_landmarks[0]
            draw_utils.draw_landmarks(frame,hand_landmarks,mpHands.HAND_CONNECTIONS)
            for lm in hand_landmarks.landmark:
                landmarks_list.append((lm.x,lm.y))
        detect_gestures(frame,landmarks_list,processed)
        frame = draw(frame,buttonlist)
        if landmarks_list:
            index_finger_tip_x = int(landmarks_list[8][0]*1280)
            index_finger_tip_y = int(landmarks_list[8][1]*720)
            for btn in buttonlist:
                x,y = btn.pos
                w,h = btn.size
                if x<index_finger_tip_x < x+w and y < index_finger_tip_y < y+h:
                    cv2.rectangle(frame,btn.pos,(x+w,y+h),(255,178,0),cv2.FILLED)
                    cv2.putText(frame,btn.text,(x+20,y+60),cv2.FONT_HERSHEY_PLAIN,2,(255,128,255),2)
                    if track.get_distance((landmarks_list[8],landmarks_list[12]))<50 and track.get_distance((landmarks_list[4],landmarks_list[5]))>50:
                        pyautogui.press(btn.text.lower())
                        cv2.rectangle(frame,btn.pos,(x+w,y+h),(0,255,0),cv2.FILLED)
                        cv2.putText(frame,btn.text,(x+20,y+60),cv2.FONT_HERSHEY_PLAIN,2,(255,120,120),2)
                        sleep(0.2)
        cv2.imshow('Frame',frame)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()