import cv2
from threading import Thread, Event
import time

class VideoStream:
    def __init__(self, path, skip=0):
        self.path = path
        self.skip = skip
        self.frame = None
        self.ret = False
        self.ready = Event()
        self.next_frame_requested = Event()
        self.stopped = False

        self.open_stream()

        # Start background frame loader thread
        self.th = Thread(target=self.update, daemon=True)
        self.th.start()

    def open_stream(self, retry_delay=5):
        self.cap = None
        while self.cap is None or not self.cap.isOpened():
            print("Attempting to connect to stream...")
            self.cap = cv2.VideoCapture(self.path)
            if not self.cap.isOpened():
                print(f"Failed to connect. Retrying in {retry_delay} seconds.")
                time.sleep(retry_delay)
        print("Connected to stream.")
#        print(self.stopped)

        self.next_frame_requested.set()
#        self.ready.clear()

    def update(self):
        while not self.stopped:
#            print('!', end='', flush=True)
            # Wait until main thread signals to fetch the next frame
            self.next_frame_requested.wait()
            self.next_frame_requested.clear()

            if not self.cap.isOpened():
                self.ret = False
                break

            self.ret, self.frame = self.cap.read()
            for _ in range(self.skip):
                ret, frame = self.cap.read()
                if not ret:
                    break

            if not self.ret or self.frame is None:
                print("Connection lost. Reconnecting...")
                self.cap.release()
                time.sleep(5)
                self.open_stream()
                continue

            # Signal that a new frame is ready
            self.ready.set()

    def goto_frame(self, frame_no):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)

    def read(self):
        # Request next frame, wait for it to be ready
        self.next_frame_requested.set()
        self.ready.wait()
        self.ready.clear()

        return self.frame

    def stop(self):
        self.stopped = True
        time.sleep(0.25)
        self.cap.release()

if __name__ == "__main__":
    from dotenv import dotenv_values
    from stream_camera import streamCamera

#    env = '.env_114'
#    env = '.env_sezon1'
    env = '.env_sezon4'
#    env = '.env_84'
    cfg = dotenv_values(env)

    camera = streamCamera(cfg)
    stream = VideoStream(camera.rtsp_uri1)
#    stream.camera = camera

    while True:
        stream.read()

        cv2.imshow("Video Frame", stream.frame)

        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.stop()

    # Clean up
#    stream.cap.release()
    cv2.destroyAllWindows()
