import cv2

class Predict():
    AGE_MODEL = cv2.dnn.readNetFromCaffe("age_deploy.prototxt", "age_net.caffemodel")
    GENDER_MODEL = cv2.dnn.readNetFromCaffe("gender_deploy.prototxt", "gender_net.caffemodel")
    NET = cv2.dnn.readNetFromCaffe("deploy.prototxt.txt", "res10_300x300_ssd_iter_140000.caffemodel")

    AGE_LIST = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    GENDER_LIST = ['Man', 'Woman']

    MIDDLE = dict()
    demography = {"age": None,  "gender": {"Man": None, "Woman": None}, "dominant_gender": None}

    def __init__(self):
        for n, e in enumerate(self.AGE_LIST):
            z = e[1:-1].split('-')
            self.MIDDLE[n] = (int(z[0]) + int(z[1]))/2

    def process_image(self, face):
        face = cv2.resize(face, (227, 227))
        self.predict_age_gender(face)

    def predict_age_gender(self, face_img):
        blob = cv2.dnn.blobFromImage(face_img, 1.0, (227, 227), (78.426, 87.768, 114.895), swapRB=False)
    
        self.GENDER_MODEL.setInput(blob)
        gender_pred = self.GENDER_MODEL.forward().flatten()
        self.demography["dominant_gender"] = self.GENDER_LIST[self.GENDER_MODEL.forward().argmax()]
        self.demography["gender"]["Man"] = 100*gender_pred[0]
        self.demography["gender"]["Woman"] = 100*gender_pred[1]

        self.AGE_MODEL.setInput(blob)
        age_preds = self.AGE_MODEL.forward().flatten()
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

    def get_confidence(self, image):
        # Prepare input blob
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

        # Forward pass
        self.NET.setInput(blob)
        detections = self.NET.forward()

        mc = 0
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            mc = max(mc, confidence)

        return mc


if __name__ == '__main__':
    import face_recognition

    predict = Predict()

    image = face_recognition.load_image_file("image.jpg")
    face_locations = face_recognition.face_locations(image)

    for top, right, bottom, left in face_locations:
        predict.process_image(image[top:bottom, left:right])
        print(predict.demography)
