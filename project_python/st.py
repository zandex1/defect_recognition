import cv2
import glob
import time

start_time = time.time()

imagefiles = glob.glob('Images/*')
imagefiles.sort()

images = []
for filename in imagefiles:
    img =cv2.imread(filename)
    images.append(img)
print('sort')
stitcher = cv2.Stitcher_create()
status, result = stitcher.stitch(images)
cv2.imwrite('res.jpg',img=result)
print(f'complete: {time.time()-start_time} seconds')