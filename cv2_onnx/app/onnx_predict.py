import cv2
import numpy as np

class Predict():
    NET = cv2.dnn.readNetFromONNX("model.onnx")

    def __init__(self):
        self.demography = {"age": None,  "gender": dict()}

    def predict_age_gender(self, emb):
        blob = np.array([emb], dtype=np.float32)
        #blob = np.random.randn(1, 512).astype(np.float32)

        self.NET.setInput(blob)
        gender_out, age_out = self.NET.forward(['gender_output', 'age_output'])

        self.demography["dominant_gender"] = {0: "Man", 1: "Woman"}.get(int(np.argmax(gender_out)))
        self.demography["gender"]["Man"] = float(gender_out[0][0])
        self.demography["gender"]["Woman"] = float(gender_out[0][1])

        self.demography["age"] = int(np.argmax(age_out))

if __name__ == '__main__':
    predict = Predict()

    import random
    emb = [random.randint(-100, 100)/100.0 for _ in range(512)]

    predict.predict_age_gender(emb)

    print(predict.demography)
