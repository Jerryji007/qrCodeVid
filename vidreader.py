import cv2
import os
#from pyzbar.pyzbar import decode
import cv2.aruco as aruco
import time
from video_spliter import split_video
import ffmpeg
from datetime import datetime    

def check_rotation(path_video_file):
    # https://stackoverflow.com/questions/53097092/frame-from-video-is-upside-down-after-extractings
    # this returns meta-data of the video file in form of a dictionary
    # comment out for now, as ffmpeg uses subprocess
    # if one uses only powerShell or cmd prompt without conda env, it will break
    meta_dict = dict() #ffmpeg.probe(path_video_file)

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

class VidProcessor():

    def __init__(self, vid_path, save_path, args):

        self.path = vid_path
        self.save_to = save_path
        if not os.path.isdir(self.save_to):
            os.makedirs(self.save_to)
        self.qrcodes = {}
        self.splits = []
        self.stop = False
        
        self.args = args
        vid_name  = self.path.split('\\')[-1].split('.')[0]
        self.checkpoint = vid_name + 'ckpt.txt'
        self.last_startsig = None

        # constants 
        self.FAULT_TOLERENCE = 120 # allow 4 seconds fault tolerence
        self.OFFSET = 30
        self.FPS = 30

        # AruCo related
        self.START_AR_CODE = 32 #0
        self.STOP_AR_CODE = 48 #99
        # when using start stop as 0 and 99
        # self.ARuCO_DICT = aruco.Dictionary_get(aruco.DICT_6X6_1000)
        # when using start stop as 32 and 48
        self.ARuCO_DICT = aruco.Dictionary_get(aruco.DICT_ARUCO_ORIGINAL)

    def read_mp4vidAR(self):
        '''
        Use cv2.vidcap to read in the video file ends with .mp4 or .avi
        in each frame, detect pre-defined START or STOP signal (aruco)
        Split video on (Start frame + offset, STOP frame - offset)
        At same time, preview the video when running the algo
        '''
        #frame num (start with frame num 1)
        count = 1
        # initialize vid cap 
        vidcap = cv2.VideoCapture(self.path)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, self.args['resume']-1) # resume on certain frame
        count = self.args['resume']
        rotateCode = check_rotation(self.path)
        success,image = vidcap.read()
        while success:
            # option to mirror every input frame
            if self.args['mirror']:
                image = cv2.flip(image, 1)
            # some vids came in with a rotation angle, rotated it back to a normal view
            if rotateCode is not None:
                image = correct_rotation(image, rotateCode)
            # fame count display
            cv2.putText(image, str(count), (60,60), cv2.FONT_HERSHEY_SIMPLEX,
                                1,(0, 0, 255), 2)
            # split video according to the self.splits (if there is piece to be cut)
            self.split_n_save()
            detected, image, datatuple = self.detectARcode(image)
            if detected:
                # for debug # save = os.path.join(self.save_to, "frame%d.jpg" % count)
                # for debug # cv2.imwrite(save, image)     # save frame as JPEG file   
                corners, ids, rejectedImgPoints = datatuple
                idlist = ids.tolist()
                for i in idlist:
                    detection = self.update_AR(i, count)
                    if count % 30 == 0:
                        print(count, 'detected' + detection)
            cv2.imshow('fm', image) # preview
            # exit condition
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 
            success,image = vidcap.read()
            count += 1
            time.sleep(0.01)
        print('Total frame num:', count)
        print(self.qrcodes)
        # append the last start stop pair if there are one
        if 'START' in self.qrcodes and 'STOP' in self.qrcodes:
            pair = (self.qrcodes['START'], self.qrcodes['STOP'])
            self.splits.append(pair)
        self.split_n_save()
        print(self.splits)
        
        # destroy, free memory
        vidcap.release()
        cv2.destroyAllWindows()

    def detectARcode(self, image):
        '''
        @param: image [ndarray]
        @return: bool (detected or not)
        '''
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # create detection setup
        arucoParameters = aruco.DetectorParameters_create()
        # parameter of the detected box must be greater than max dim of input image(1920 for 1920*1080)
        arucoParameters.minMarkerPerimeterRate = 0.5
        # accuracy that detected box shape looks like a squared box 
        arucoParameters.polygonalApproxAccuracyRate = 0.1
        corners, ids, rejectedImgPoints = aruco.detectMarkers(
            gray, self.ARuCO_DICT, parameters=arucoParameters)
        if ids is None or len(ids) == 0:
            # no id detected, return false and ori_image
            return False, image, (corners, ids, rejectedImgPoints)
        
        # protection, one could also hand coded the requirement of a detected box

        # detected and change the image for preview (with bbox on the aruco)
        image = aruco.drawDetectedMarkers(image, corners, ids)
        return True, image, (corners, ids, rejectedImgPoints)

    def update_AR(self, ids, frame_num):
        data = ids[0]
        if data == self.START_AR_CODE:
            data = 'START'
            if self.stop and 'START' in self.qrcodes:
                pair = (self.qrcodes['START'], self.qrcodes['STOP'])
                self.splits.append(pair)
                self.qrcodes = dict()
                self.stop = False
            elif self.stop and 'START' not in self.qrcodes:
                self.qrcodes = dict()
                self.stop = False
        elif data == self.STOP_AR_CODE:
            data = 'STOP'
            self.stop = True
        if type(data) != str:
            data = 'NEW detected' + str(int(data))
            print(data)


        # update the latest frame number tracking of 'STOP' or 'START'
        if data in self.qrcodes:
            if data == 'START' and frame_num > self.qrcodes[data][1] and frame_num - self.qrcodes[data][1] < self.FAULT_TOLERENCE:
                # update the last frame seen START, there is a fault tolerence, in case data collector accidentally 
                # raise START after gesture shown again
                self.qrcodes[data] = (self.qrcodes[data][0], frame_num)
            elif data == 'STOP' and frame_num > self.qrcodes[data][1]:
                #update the last time seen STOP
                self.qrcodes[data] = (self.qrcodes[data][0], frame_num)
        elif data == 'START' or data == 'STOP':
            self.qrcodes[data] = (frame_num, frame_num)
        #print(self.qrcodes)
        return data

    def split_n_save(self):
        '''
        generate a trim of video based on the self.splits array
        '''
        if len(self.splits) > 0:
            pair = self.splits.pop(0)
            print(pair)
            start_pair = pair[0]
            end_pair = pair[1]
            fps = self.FPS
            start_fm = (start_pair[1] + self.OFFSET)/fps
            end_fm = (end_pair[0] - self.OFFSET)/fps
            # STRING OF OUTPUT FORMAT: createdtime + originalname + startFrame + stopFrame
            # linux
            # dest = os.path.join(self.save_to, self.path.split('/')[-1].split('.')[0] + str(round(start_fm,2)) + '_' + str(round(end_fm,2)))
            # windows
            tot_fm = end_pair[0] - start_pair[1] - 2*self.OFFSET
            date = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
            dest = os.path.join(self.save_to, date+'_'+ 'fd-' + str(tot_fm) + '_' + self.path.split('\\')[-1].split('.')[0] + '_' +str(int(start_fm)) + '_' + str(int(end_fm)))
            
            print(start_fm, end_fm)
            # split the video if the endframe is later than start frame
            if start_fm < end_fm:
                print('splitting')
                print(dest)
                split_video(start_fm, end_fm, self.path, dest)
                # save the checkpoint if trimmed a piece of the video
                if self.args['saveckpt']:
                    date = datetime.now().strftime("%y-%m-%d-%H:%M:%S")
                    print(date)
                    f = open(self.checkpoint, 'a+')
                    f.write(date + ' Last stop cutting Frame was: frame num' + str(end_pair[0] - self.OFFSET) + '\n')
                    print(date + ' Last stop cutting Frame was: frame num' + str(end_pair[0] - self.OFFSET) + '\n')
            else:
                print('not valid start and stop, gesture too short')
            