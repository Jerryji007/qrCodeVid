import os
import argparse
from vidreader import VidProcessor

if __name__ == '__main__':
    def resume_type(x):
        x = int(x)
        if x < 1:
            raise argparse.ArgumentTypeError("Minimum resume framenum is 1")
        return x 

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", required=True, default='data/qrvidex1210.mp4',
        help="path to input video")
    ap.add_argument("--mirror", default=False, action = "store_true", help="wheather mirror each frame")
    ap.add_argument("--saveckpt", default=True, action = "store_true", help="wheather save the current video's endpoints (for resume use)")
    ap.add_argument("--resume", type=resume_type, default= 1, help="resume from a STOP signal (last cutting point)")
    args = vars(ap.parse_args()) # to a dictionary

    # load the input image
    path = args["video"]

    save_to = 'pix'
    r = VidProcessor(path, save_to, args)
    r.read_mp4vidAR()

