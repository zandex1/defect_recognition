import cv2
import glob
import st1 as stitching
def main():
    path_images = glob.glob('out/*')
    images=[]
    
    images_in_row = 11
    images_in_coloumn = 11
    
    for image_path in path_images:
        images.append(image_path)
    k=0
    
    for i in range(0,images_in_coloumn):
        result = cv2.imread(images[k])
        for j in range(0,images_in_row):
            print(k)
            img = cv2.imread(images[k+1])
            result = stitching.stitch(result, img)
            k+=1
            cv2.imwrite(f'{k}.jpg',result)
            if k%30 == 0:
                break 

            
        cv2.imwrite(f'{i+1}.jpg', cv2.cvtColor(result, cv2.COLOR_BGR2RGB))

    

if __name__=='__main__':
    main()