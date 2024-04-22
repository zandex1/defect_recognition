import cv2
import numpy as np
cv2.ocl.setUseOpenCL(False)
import warnings
warnings.filterwarnings('ignore')

def select_descriptor_method(image, method=None):
    
    assert method is not None, "Please define a descriptor method. Accepted values are: 'sift', 'surf', 'orb', 'brisk' "
    
    if method == 'sift':
        descriptor = cv2.SIFT_create()
    if method == 'surf':
        descriptor = cv2.SURF_create()
    if method == 'orb':
        descriptor = cv2.ORB_create()
    if method == 'brisk':
        descriptor = cv2.BRISK_create()
    
    (keypoints, features) = descriptor.detectAndCompute(image, None)
    
    return (keypoints, features)

def create_matching_object(method, crossCheck):
    if method == 'sift' or method == 'surf':
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=crossCheck)
    elif method == 'orb' or method == 'brisk':
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=crossCheck)
    
    return bf

def key_points_matching(feature_train_img, feature_query_img, method):
    bf = create_matching_object(method=method, crossCheck=True)
    
    best_mathces = bf.match(feature_train_img, feature_query_img)
    
    raw_matches = sorted(best_mathces, key =lambda x: x.distance)
    print('Raw matches with Brute Force', len(raw_matches))
    
    return raw_matches

def key_points_matching_KNN(feature_train_img, feature_query_img, ratio, method):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    # bf = create_matching_object(method=method, crossCheck=False)
    
    raw_matches = bf.knnMatch(feature_train_img, feature_query_img, k=2)
    print('Raw matches with KNN', len(raw_matches))
    
    knn_matches = []
    
    for m,n in raw_matches:
        if m.distance < n.distance * ratio:
            knn_matches.append(m)    
    
    return knn_matches

def homography_stitching(keypoints_train_img, keypoints_query_img, matches, reprojThresh):
    # converte to numpy array
    
    keypoints_train_img = np.float32([keypoint.pt for keypoint in keypoints_train_img])
    keypoints_query_img = np.float32([keypoint.pt for keypoint in keypoints_query_img])
    
    if len(matches) > 4:
        points_train = np.float32([keypoints_train_img[m.queryIdx] for m in matches])
        points_query = np.float32([keypoints_query_img[m.trainIdx] for m in matches])
        
        (H, status) = cv2.findHomography(points_train, points_query, cv2.RANSAC, reprojThresh)
        
        return(matches, H ,status)
    
    else:
        return None
