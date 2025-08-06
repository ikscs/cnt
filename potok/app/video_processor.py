from PIL import Image
import imagehash
import mediapipe as mp
import cv2
from io import BytesIO

class VideoProcessor:
    def __init__(self, delta_hash=3, min_detection_confidence=0.1):
        self.delta_hash = delta_hash
        mp_face = mp.solutions.face_detection
        mp_pose = mp.solutions.pose

        self.face_detection = mp_face.FaceDetection(model_selection=1, min_detection_confidence=min_detection_confidence)
        self.pose = mp_pose.Pose(static_image_mode=True)

        self.hash1 = imagehash.phash(Image.new('RGB', (1, 1)))
        self.hash2 = imagehash.phash(Image.new('RGB', (1, 1)))
        self.img = None

    def check_frame(self, frame):
        # Convert to RGB (MediaPipe uses RGB)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.img = Image.fromarray(image_rgb)

        self.hash2 = imagehash.phash(self.img)

        delta = self.hash2 - self.hash1
        if delta > self.delta_hash:
            self.hash1 = self.hash2

            self.refer_frame = frame

            # Run poses detection
            results = self.pose.process(image_rgb)
            if results.pose_landmarks:
                #print('b', end='', flush=True)
                #self.camera.get_snapshoot()
                is_pose = True

#            if is_pose:
                # Run face detection
                results = self.face_detection.process(image_rgb)
                if results.detections:
                    return True
                    #print('f', end='', flush=True)
#                    self.camera.get_snapshoot()

#                    now = datetime.now()
#                    image_name = f'./{SNAP}/img_small{now:%Y%m%d_%H%M%S_%f}.jpg'
#                    cv2.imwrite(image_name, self.frame)

#            print(delta, end=' ', flush=True)
        return False

    def get_snapshoot(self):
        if not self.img:
            return None
        buffer = BytesIO()
        self.img.save(buffer, format='JPEG')
        content = buffer.getvalue()
        return content

if __name__ == "__main__":
    import numpy as np

    pil_image1 = Image.open("image1.jpg").convert("RGB")
    rgb_array1 = np.array(pil_image1)
    frame1 = cv2.cvtColor(rgb_array1, cv2.COLOR_RGB2BGR)

    pil_image2 = Image.open("image2.jpg").convert("RGB")
    rgb_array2 = np.array(pil_image2)
    frame2 = cv2.cvtColor(rgb_array2, cv2.COLOR_RGB2BGR)

    vp = VideoProcessor()

    print(vp.check_frame(frame1))
    print(vp.check_frame(frame2))
    print(vp.check_frame(frame2))
