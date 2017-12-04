lsimport urllib.request
import cv2
import numpy as np
import os

postiveImages = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n00007846'
links = urllib.request.urlopen(postiveImages).read().decode()
holder = 1

def pull_image():
    for i in links.split('\n'):
        try: 
            print(i)
            urllib.request.urlretrieve(i, "images/"+str(holder)+'.jpg')
            image = cv2.imread("images/"+str(holder)+ '.jpg', cv2.IMREAD_GRAYSCALE)
            resized_image = cv2.resize(image, (100,100))
            cv2.imwrite("images/"+str(holder)+'.jpg', resized_image)
            holder +=1

        except Exception as e:
            print(str(e))

def mrClean():
    for file in ['images']:
        for img in os.listdir(file):
            for ugly in os.listdir('bad_Links'):
                try:
                    current_image_path = str(file)+'/'+str(img)
                    ugly = cv2.imread('bad_Links/'+str(ugly))
                    question = cv2.imread(current_image_path)
                    if ugly.shape == question.shape and not(np.bitwise_xor(ugly,question).any()):
                        print('That is one ugly pic! Deleting!')
                        print(current_image_path)
                        os.remove(current_image_path)
                except Exception as e:
                    print(str(e))


def pos_neg():
    for file_type in ['neg_images']:
        
        for img in os.listdir(file_type):
            if file_type == 'neg_images':
                line = file_type+ '/'+img+'\n'
                with open('bg.txt', 'a') as f:
                    f.write(line)
            
            elif file_type == 'pos_images':
                line = file_type+ '/'+img+' 1 0 0 50 50\n'
                with open('info.txt', 'a') as f:
                    f.write(line)

                
            
            


pos_neg()
pull_image()
mrClean()