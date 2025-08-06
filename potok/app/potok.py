from stream_camera import streamCamera
from video_stream import VideoStream
from video_processor import VideoProcessor
from sender import Sender

import cv2

from datetime import datetime

from db_wrapper import DB

def main(cfg):
    sender = Sender(cfg)
    camera = streamCamera(cfg)
    stream = VideoStream(camera.rtsp_uri1 if cfg['channel'] == 'primary' else camera.rtsp_uri2)
    vp = VideoProcessor()

    while True:
        stream.read()
        if vp.check_frame(stream.frame):
            now = datetime.now()
            if cfg['channel'] == 'ss':
                content = camera.get_snapshoot()
            else:
                content = vp.get_snapshoot()
            if content:
                sender.send_email(f'{now.isoformat()}', '', attachment_data=content, attachment_name=f'{now:%Y%m%d_%H%M%S_%f}.jpg')
#        try:
#            cv2.imshow("Video Frame", stream.frame)
#        except Exception as err:
#            pass

        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    stream.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    from dotenv import load_dotenv, dotenv_values

    cfg = dotenv_values('.env')
    origin_type_id = cfg['origin_type_id']
    origin_id = cfg['origin_id']

    load_dotenv()

    db = DB()
    db.open()

    sql = 'SELECT params, credentials FROM origin JOIN origin_type USING(origin_type_id) WHERE origin_type_id=%s AND id=%s'
    db.cursor.execute(sql, [origin_type_id, origin_id])
    columns = [col.name for col in db.cursor.description]
    row = db.cursor.fetchone()
    data = dict()
    for i, col_name in enumerate(columns):
        data[col_name] = row[i]

    cfg = data['params'].copy()
    cfg.update(data['credentials'])

    db.close()

    main(cfg)
