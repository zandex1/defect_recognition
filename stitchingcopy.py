import cv2
import numpy as np
cv2.ocl.setUseOpenCL(False)
import warnings
warnings.filterwarnings('ignore')

def main(train_path, query_photo,k):
    
    feature_extraction_algo = 'sift'

    # feature_to_match = 'bf'
    feature_to_match = 'knn'

    train_photo = cv2.imread(train_path)

    train_photo = cv2.cvtColor(train_photo, cv2.COLOR_BGR2RGB)

    train_photo_gray = cv2.cvtColor(train_photo, cv2.COLOR_BGR2GRAY)

    query_photo = query_photo

    query_photo = cv2.cvtColor(query_photo, cv2.COLOR_BGR2RGB)

    query_photo_gray = cv2.cvtColor(query_photo, cv2.COLOR_BGR2GRAY)
    
    keypoints_train_img, feature_train_img = select_descriptor_method(train_photo_gray, feature_extraction_algo)

    keypoints_query_img, feature_query_img = select_descriptor_method(query_photo_gray, feature_extraction_algo)
    
    if feature_to_match == 'bf':
        matches = key_points_matching(feature_train_img, feature_query_img, method=feature_extraction_algo)
        mapped_feature_image = cv2.drawMatches(train_photo, keypoints_train_img, query_photo, keypoints_query_img, matches[:100], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    elif feature_to_match == 'knn':
        matches = key_points_matching_KNN(feature_train_img, feature_query_img, ratio= 0.75, method=feature_extraction_algo)
        mapped_feature_image_knn = cv2.drawMatches(train_photo, keypoints_train_img, query_photo, keypoints_query_img, np.random.choice(matches, 100), None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    cv2.imwrite(f'mapped_{k}.jpg',mapped_feature_image_knn)
    
    M = homography_stitching(keypoints_train_img=keypoints_train_img, keypoints_query_img=keypoints_query_img, matches=matches, reprojThresh=4)

    if M is None:
        print('Error')
        exit()
        
    (matches, Homography_Matrix, status) = M
    # print(Homography_Matrix)

    width = query_photo.shape[1] + train_photo.shape[1]-800
    height = max(query_photo.shape[0], train_photo.shape[0])

    result = cv2.warpPerspective(train_photo, Homography_Matrix, (width, height))
    cv2.imwrite(f'res_{k}.jpg', cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    result[0:query_photo.shape[0],0:query_photo.shape[1]] = query_photo
    
    cv2.imwrite(f'test{k}.jpg',cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return cv2.cvtColor(result, cv2.COLOR_BGR2RGB)

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
    
    return raw_matches

def key_points_matching_KNN(feature_train_img, feature_query_img, ratio, method):
    bf = create_matching_object(method=method, crossCheck=False)
    
    raw_matches = bf.knnMatch(feature_train_img, feature_query_img, k=2)
    
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
    

if __name__=='__main__':
    main()
