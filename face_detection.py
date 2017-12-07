from PIL import Image, ImageFilter
from sightengine.client import SightengineClient
import cv2

client = SightengineClient('1815250773', 'oGKFfnDkDkcoKcH3x2hw')

# def check_image_for_minors(image):
#     # output = client.check('face-attributes').set_url(image_url)
#     output = client.check('face-attributes').set_file(image)
#     # print('The output from checking the image', output)
#     try:
#         for face in output['faces']:
#             if 'attributes' in face:
#                 if face['attributes']['minor'] > 0.80:
#                     print("child image found")
#                     imgpil = Image.open(image)
#                     imgwidth = imgpil.size[0]
#                     imgheight = imgpil.size[1]

#                     x1 = face['x1']
#                     y1 = face['y1']
#                     x2 = face['x2']
#                     y2 = face['y2']

#                     xx1 = int(round(float(x1 * imgwidth)))
#                     yy1 = int(round(float(y1 * imgheight)))
#                     xx2 = int(round(float(x2 * imgwidth)))
#                     yy2 = int(round(float(y2 * imgheight)))

#                     baby = imgpil.copy()
#                     blurredbaby = baby.crop((xx1, yy1, xx2, yy2))

#                     blurredbaby = blurredbaby.filter(ImageFilter.GaussianBlur(10))
#                     baby.paste(blurredbaby, (xx1, yy1))
#                     baby.save(image)
#     except:
#         print('no face found yo')
#     print("done!")


def check_image_for_minors(imagePath):
    
    # Create the haar cascade
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    # Read the image
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    print("Found {0} faces!".format(len(faces)))
    
    # cv2.imwrite(imagePath, image)
    result_image = image.copy()
    if len(faces) != 0:         # If there are faces in the images
        for (x, y, w, h) in faces:         # For each face in the image
    
            # get the rectangle img around all the faces
            cv2.rectangle(image, (x,y), (x+w,y+h), (255,255,0), 5)
            sub_face = image[y:y+h, x:x+w]
            # apply a gaussian blur on this new recangle image
            sub_face = cv2.GaussianBlur(sub_face,(23, 23), 30)
            # merge this blurry rectangle to our final image
            result_image[y:y+sub_face.shape[0], x:x+sub_face.shape[1]] = sub_face
            face_file_name = "./static/tmp/faces/face_" + str(y) + ".jpg"
            cv2.imwrite(face_file_name, sub_face)
    
    # cv2.imshow("Detected face", result_image)
    cv2.imwrite(imagePath, result_image)