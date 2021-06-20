import cv2
import os
from pyzbar.pyzbar import decode
import time
from video_spliter import split_video
import ffmpeg
from datetime import datetime    


def check_rotation(path_video_file):
    # this returns meta-data of the video file in form of a dictionary
    meta_dict = ffmpeg.probe(path_video_file)

    # from the dictionary, meta_dict['streams'][0]['tags']['rotate'] is the key
    # we are looking for
    rotateCode = None
    rotate = meta_dict.get('streams', [dict(tags=dict())])[0].get('tags', dict()).get('rotate', 0)
    num = round(int(rotate) / 90.0) * 90
    print(num)
    if num == 90:
        rotateCode = cv2.ROTATE_90_CLOCKWISE
    elif num == 180:
        rotateCode = cv2.ROTATE_180
    elif num == 270:
        rotateCode = cv2.ROTATE_90_COUNTERCLOCKWISE
    return rotateCode

def correct_rotation(frame, rotateCode):  
    return cv2.rotate(frame, rotateCode)

class VidProcessorQR():

    def __init__(self, vid_path, save_path, args):

        self.path = vid_path
        self.save_to = save_path
        if not os.path.isdir(self.save_to):
            os.makedirs(self.save_to)
        self.qrcodes = {}
        self.splits = []
        self.stop = False
        self.OFFSET = 45
        self.args = args
        self.checkpoint = 'checkpoint.txt'

    def read_mp4vidQR(self):
        vidcap = cv2.VideoCapture(self.path)
        success,image = vidcap.read()
        count = 1 # start with frame num 1
        while success:
            detected, qrcodes = self.detect_QRcode(image)
            cv2.putText(image, str(count), (60,60), cv2.FONT_HERSHEY_SIMPLEX,
                                1,(0, 0, 255), 2)
            if detected:
                save = os.path.join(self.save_to, "frame%d.jpg" % count)
                #cv2.imwrite(save, image)     # save frame as JPEG file   
                for i in qrcodes:
                    self.update_dict(i, count)
                    barcode = i[0]
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    text = "{} ({})".format(i[1], i[2])
                    cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 2)
                    
                    if count % 30 == 0:
                        print(count, text)
            cv2.imshow('fm', image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            success,image = vidcap.read()
            #print('Read a new frame: ', success)
            count += 1
        print('Total frame num:', count)
        print(self.qrcodes)
        
        vidcap.release()
        cv2.destroyAllWindows()
    
    def detect_QRcode(self, img, code=None):
        res = []
        # load the input image
        image = img
        # find the barcodes in the image and decode each of the barcodes
        # barcodes = decode(image)
        if len(barcodes) == 0:
            return False, None
        # loop over the detected barcodes
        # WARNING: here we should only assume one barcode
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            # (x, y, w, h) = barcode.rect
            # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            # cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            #     0.5, (0, 0, 255), 2)
            # print the barcode type and data to the terminal
            #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
            if code is None or code == barcodeData:
                res.append((barcode, barcodeData, barcodeType))
        # # show the output image
        # cv2.imshow("Image", image)
        # cv2.waitKey(0)
        return True, res
    
    def update_dict(self, qrcode_tuple, frame_num):
        qrcode = qrcode_tuple[0]
        data = qrcode_tuple[1]
        qrtype = qrcode_tuple[2]

        if data in self.qrcodes:
            if frame_num > self.qrcodes[data][1]:
                self.qrcodes[data] = (self.qrcodes[data][0], frame_num)
        else:
            self.qrcodes[data] = (frame_num, frame_num)