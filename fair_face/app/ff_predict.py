from transformers import AutoModelForImageClassification, AutoProcessor
import torch
import numpy as np

def to_percentages(tensor_values):
  e_x = np.exp(tensor_values - np.max(tensor_values))  # Subtract max for numerical stability
  softmax_values = e_x / np.sum(e_x)
  percentages = [float(val * 100.0) for val in softmax_values]
  return percentages

class Predict():
    processor = AutoProcessor.from_pretrained("dima806/fairface_gender_image_detection", use_fast=False)
    model_gender = AutoModelForImageClassification.from_pretrained("dima806/fairface_gender_image_detection")

    #processor = AutoProcessor.from_pretrained("dima806/facial_age_image_detection", use_fast=False)
    model_age = AutoModelForImageClassification.from_pretrained("dima806/facial_age_image_detection")

    MIDDLE = dict()
    demography = {"age": None,  "gender": {"Man": None, "Woman": None}, "dominant_gender": None}

    def __init__(self):
        last_age = 0
        for n, e in self.model_age.config.id2label.items():
            if e.endswith('+'):
                val = int(e[:-1])
                last_age = val
            else:
                z = e.split('-')
                if len(z) == 2:
                    val = (int(z[0]) + int(z[1]))/2.0
                    last_age = int(z[1])
                else:
                    val = (last_age + int(e))/2.0
                    last_age = int(e)
            self.MIDDLE[n] = val

    def process_image(self, face):
        self.predict_age_gender(face)

    def predict_age_gender(self, face_img):
        inputs = self.processor(images=face_img, return_tensors="pt")

        with torch.no_grad():
            logits_gender = self.model_gender(**inputs).logits
            logits_age = self.model_age(**inputs).logits

        predicted_class_idx = logits_gender.argmax(-1).item()
        predicted_class = self.model_gender.config.id2label[predicted_class_idx]

        gender = logits_gender[0].tolist()

        self.demography["dominant_gender"] = {'Female': 'Woman', 'Male': 'Man'}.get(predicted_class)
        gender_preds = to_percentages(gender)
        self.demography["gender"]["Man"] = gender_preds[1]
        self.demography["gender"]["Woman"] = gender_preds[0]

        age_preds = to_percentages(logits_age[0].tolist())
        self.demography["age"] = self.get_age(age_preds)

    def get_age(self, age_preds):
        idx = 0
        max_val = age_preds[idx]
        for n, val in enumerate(age_preds[1:], 1):
            if val > max_val:
                idx = n
                max_val = val

        if idx > 0:
            minus = (self.MIDDLE[idx]-self.MIDDLE[idx-1])*age_preds[idx-1]/age_preds[idx]
        else:
            minus = 0

        if idx < len(age_preds)-1:
            plus = (self.MIDDLE[idx+1]-self.MIDDLE[idx])*age_preds[idx+1]/age_preds[idx]
        else:
            plus = 0
        return round(self.MIDDLE[idx] + plus - minus)


if __name__ == '__main__':
    import face_recognition

    predict = Predict()

    image = face_recognition.load_image_file("image.jpg")

    face_locations = face_recognition.face_locations(image)

    for n, face_location in enumerate(face_locations):
        top, right, bottom, left = face_location
        predict.process_image(image[top:bottom, left:right])
        print(predict.demography)
