import cv2

img = cv2.imread('sky.jpg')

print(img.shape)

y=0
x=0
k=1

while y <=4320:
    while x<=7680:
        cut_img = img[y:y+720,x:x+1280]
        cv2.imwrite(f'{k}.jpg',cut_img)
        k+=1
        x+=640
        if x+1280>7680:
            x=0
            break
    y+=360
    
    if y+720>4320:
        y=0
        break