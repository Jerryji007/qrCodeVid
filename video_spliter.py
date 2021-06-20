from moviepy.video.io.VideoFileClip import VideoFileClip
import argparse
import os

def split_video(start_time, end_time, file_path, dest_name):
    if file_path.endswith(".mp4") or file_path.endswith(".avi") :
        with VideoFileClip(file_path) as video:
            clipped = video.subclip(start_time, end_time)
            clipped.write_videofile(dest_name+".mp4", audio=False, bitrate='5000000')
            clipped.close()



#if __name__ == '__main__':
#    parser = argparse.ArgumentParser(
#        description='Visualizer')
#    parser.add_argument('-v', '--video_path', default=".\\final_video.mp4")
#    args = parser.parse_args()
#    video_path = args.video_path
#    if video_path.endswith(".mp4"):
#        with VideoFileClip(video_path) as video:
#            clipped = video.subclip(60, 70)
#            clipped.write_videofile(".\split.mp4", audio_codec='aac')

