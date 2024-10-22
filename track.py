#this file is used to get angle and distance between the hand landmarks

import numpy as np
def getangle(a,b,c):
    radians = np.arctan2(c[1]-b[1],c[0]-b[0])-np.arctan2(a[1]-b[1],a[0]-b[0])
    angle = np.abs(np.degrees(radians))
    return angle

def get_distance(landmark_list):
    if len(landmark_list)<2:
        return
    (x1,y1),(x2,y2) = landmark_list[0],landmark_list[1]
    l = np.hypot(x2-x1,y2-y1)
    return np.interp(l,[0,1],[0,1000])
