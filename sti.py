import cv2
import glob

def main():
    path_images = glob.glob('out/*')
    images=[]
    imgs=[]
    images_in_row = 30
    images_in_coloumn = 10
    stitcher  = cv2.Stitcher.create(mode = 1)
    for image_path in path_images:
        images.append(image_path)
    k=0
    for i in images:
        imgs.append(cv2.imread(i))
    print(len(imgs))
    (dummy,output)=stitcher.stitch(imgs) 
  
    if dummy != cv2.STITCHER_OK: 
    # checking if the stitching procedure is successful 
    # .stitch() function returns a true value if stitching is  
    # done successfully 
        print("stitching ain't successful") 
    else:  
        print('Your Panorama is ready!!!')     
        
    cv2.imwrite('res1.jpg',output)
    

if __name__=='__main__':
    main()