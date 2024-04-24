# Importing necessary libraries
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pylab as plt

# Defining a function 'trim' to remove black part obtained after stitching having area of common regions
def trim(frame):
    #crop top
    if not np.sum(frame[0]):
        return trim(frame[1:])
    #crop bottom
    elif not np.sum(frame[-1]):
        return trim(frame[:-2])
    #crop left
    elif not np.sum(frame[:,0]):
        return trim(frame[:,1:]) 
    #crop right
    elif not np.sum(frame[:,-1]):
        return trim(frame[:,:-2])    
    return frame


# Defining a function 'stitch' that performs all necessary operations to get panorama image
def stitch(image01,image02):

    image1 = cv2.cvtColor(image01,cv2.COLOR_BGR2GRAY)
    image2 = cv2.cvtColor(image02,cv2.COLOR_BGR2GRAY)
    
    # Extracting features using SIFT
    sift = cv2.SIFT_create()

    # Finding the key points (kp) and descriptors (des) with SIFT
    kp1, des1 = sift.detectAndCompute(image1,None)
    kp2, des2 = sift.detectAndCompute(image2,None)

    ky1 = cv2.drawKeypoints(image01,kp1,None)
    ky2 = cv2.drawKeypoints(image02,kp2,None)
    
    # BFmatcher matches the most similar features and knnMatcher with k=2 gives 2 best matches for each descriptor.
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2, k=2)

    # The features may be existing in many places of the image which can mislead the operations. 
    # So,we filter out through all the matches to obtain the best ones by applying ratio test.
    # We consider a match if the ratio defined below is predominantly greater than the specified ratio.
    good = []
    for m in matches:
        if m[0].distance < 0.55*m[1].distance:
            good.append(m[0])
            matches = np.asarray(good)
                   
    matches = bf.knnMatch(des2,des1, k=2)
    good = []
    for m in matches:
        if m[0].distance < 0.55*m[1].distance:
            good.append(m[0])
            matches = np.asarray(good)
    print(len(matches))
    # A homography matrix is needed to perform the transformation using RANSAC and requires atleast 4 matches.
    if len(matches) >= 4:
        src = np.float32([ kp2[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
        dst = np.float32([ kp1[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
        H, masked = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    
    else:
        print("Insufficient keypoints")
        exit()
        
    # Now the images are warped and stitched together.
    dst = cv2.warpPerspective(image02,H,(image01.shape[1] + image02.shape[1], image01.shape[0]))
    dst[0:image01.shape[0], 0:image01.shape[1]] = image01
    
    # Triming and crop a little from right of stitched image to remove the undesired black portion obtained while stitching.
    dst = trim(dst)
    height = dst.shape[0]
    width = dst.shape[1] 

    y=0
    x=0
    h=int(height)
    w=int(0.97*width)
    dst = dst[y:y+h, x:x+w]
    
    return dst