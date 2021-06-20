# qrCodeVid
This is a simple script that given a video path, split the video into parts where based on the time that pre-defined START/STOP arucodes show up in the video.
The script has a bit Fault Tolerence (quickly change to STOP after a wrong START signal) and have SAVECKPT option to save the last trimming points and RESUME option to resume the trimming process from a frame of the video.  


It is recommended to use this script with anaconda on Windows. (If conda is avaliable, please use conda_req.txt to install the environment).
It will work on Powershell and cmd prompt only by just running:
```
pip install -r requirement.txt
```
## Usage

```
python main.py -v PATH_to_MP4_videoFILE  ...
```

Options:
```
--saveckpt
    [default True]
    this option allows the script to save the latest trimmed information
    into a file name as PATH_to_MP4_videoFILEckpt.txt
    For now, always save checkpoint

--mirror 
    [default False]
    this option allows the video trimmer to detect
    for START&STOP signals on horizontally mirrored image on each frame

--resume FRAMENUM
    [default 1 (start from the original video)], must be a number bigger than 1 
    this number should be number from the last line of the XXX_ckpt.txt file created during the last trimming process
    It will restart the process of trimming from FRAMENUM  
```

/signals -- this folder contains all the different ARuCode that should be used when recording the video

conda_req.txt & requirement.txt -- conda requirement and pip requirement

main.py -- main function and argument parsing

video_spliter.py -- method that helps split a .mp4 or .avi video with start time and end time in seconds

vidreader.py -- most crucial logic and implementation in this file
                it reads a video frame by frame and detect the START & STOP signals in the video and trim based on these signals
                for pair of START and STOP signal, the processor trim from (last frame of START + OFFSETframes) to (first frame of STOP - OFFSETframes)
                user could choose one set of START STOP singal from two options
                user could adjust the OFFSETframe
                The script also has a fault protection when the person in the video raise a START signal after a START signal 
                (after self.FAULT_TOLERENCE amount of frames).
                
qrvidreader.py -- another detection option that uses QRcode that was initially used instead of ARuCo, it is there merely for a reference

### Signal Switching
The script is equipped with two sets of START & STOP signal.
```
Defualt:
START id: 32
STOP  id: 48
ARuCO dictionary: aruco.DICT_ARUCO_ORIGINAL
```

Mirror needed:

Warning:

When use 0 and 99 (signals/unmirroredID{0, 99}.pdf) and recording with hicar camera, please use the <mark>--mirror</mark> option

Please change:
```
self.START_AR_CODE from 32 to 0
self.STOP_AR_CODE from 48 to 99
self.ARuCO_DICT to aruco.Dictionary_get(aruco.DICT_6X6_1000)
```
```
START id: 0
STOP id: 99
ARuCO dictionary: aruco.DICT_6X6_1000
```

# Video merger
This script merges all the videos in a folder. The videos in the folder should be ordered using their names. 
(script will merge based on the name of the videos)
The script takes a -f argument which should be the folder path that contains the video
Give the script a folder path that has the video to be merged. Then give the output filename.

```
python video_merger.py -f FOLDERNAME -o DESIRED_OUTPUT_FILENAME
```


