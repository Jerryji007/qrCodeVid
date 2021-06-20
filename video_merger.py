from moviepy.editor import VideoFileClip, concatenate_videoclips
import argparse
import os

def merge_videos(folder_path):
    videos = []
    for videoFilename in os.listdir(folder_path):
        if videoFilename.endswith(".mp4"):
            videos.append(VideoFileClip(os.path.join(folder_path, videoFilename)))
    final_video = concatenate_videoclips(videos)
    final_video.write_videofile("final_video.mp4")



if __name__ == '__main__':
   parser = argparse.ArgumentParser(
       description='Visualizer')
   parser.add_argument('-f', '--folder_path', default="data")
   parser.add_argument('-o', '--ouput_name', default="final_video", help='the name of the output merged video, just name no need to type .mp4')
   args = parser.parse_args()
   folder_path = args.folder_path
   videos = []
   for videoFilename in os.listdir(folder_path):
       if videoFilename.endswith(".mp4"):
           videos.append(VideoFileClip(folder_path+"\\"+videoFilename))
   final_video = concatenate_videoclips(videos)
   final_video.write_videofile(args.ouput_name + ".mp4")


