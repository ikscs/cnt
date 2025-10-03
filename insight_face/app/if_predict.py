#!/usr/bin/python3
import json
import numpy as np
import insightface

from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

model_recognition = insightface.app.FaceAnalysis(allowed_modules=['detection', 'recognition'])
model_recognition.prepare(ctx_id=-1)
model_genderage = insightface.app.FaceAnalysis(allowed_modules=['detection', 'genderage'])
model_genderage.prepare(ctx_id=-1)

class Predict():
    confidence = 0.7
    area = 40
    demography = {"age": None,  "gender": None}

    def __init__(self):
        pass

    def process_image(self, face, is_one_person=False, area=None):
        if area != None:
            self.area = area
        return self.get_demography(face, is_one_person)

    def get_represent(self, image, confidence=None, area=None):
        if area != None:
            self.area = area
        if confidence != None:
            self.confidence = confidence

        try:
            faces_data = model_recognition.get(image)
        except Exception as err:
            print(str(err))
            faces_data = []

        content = [face for face in faces_data if face['det_score'] >= self.confidence and (face['bbox'][2] - face['bbox'][0]) >= self.area]
        return content

    def get_demography(self, image, is_one_person=False):
        try:
            faces_data = model_genderage.get(image)
        except Exception as err:
            print(str(err))
            faces_data = []

        content = []
        for face in faces_data:
            self.demography = {'age': int(face.age), 'gender': int(face['gender']), 'bbox': face['bbox'], 'confidence': face['det_score']}
            if is_one_person:
                return [self.demography]

            if face['det_score'] < self.confidence or (face['bbox'][2] - face['bbox'][0]) < self.area:
                continue

            content.append(self.demography)

        return content

    def load_image_file(self, file):
        im = Image.open(file)
        return np.array(im)
        #image = cv2.imread(file)
        #return image

if __name__ == '__main__':

    predict = Predict()

    full_path = "image.jpg"
    image = predict.load_image_file(full_path)

#    represent = predict.get_represent(image)
#    print(represent[0], len(represent[0]['embedding']))
    demography = predict.get_demography(image, is_one_person=True)
    print(demography)
