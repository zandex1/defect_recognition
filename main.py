import cv2
import glob
import stitchingcopy as stitching
def main():
    path_images = glob.glob('Images1/*')
    images=[]
    
    images_in_row = 30
    images_in_coloumn = 10
    
    for image_path in path_images:
        images.append(image_path)
    k=0
    
    for i in range(0,images_in_coloumn):
        result = cv2.imread(images[k])
        for j in range(0,images_in_row):
            print(k)
            
            result = stitching.main(train_path=images[k+1], query_photo=result,k=k+1)
            k+=1
            
            if k%30 == 0:
                break 

            
        cv2.imwrite(f'{i+1}.jpg', cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    

if __name__=='__main__':
    main()