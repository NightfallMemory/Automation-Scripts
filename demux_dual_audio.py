#!/usr/bin/env python
"""
    A script for demuxing dual/tri/infinite audio anime releases and keeping only the jp audio.
    
    Requirements:
    - ffmpeg & ffprobe in path.
"""
import os
import glob
import subprocess
import json

# Variables
video_ext = ["mkv","mp4"];
audio_codecs = ["aac","ac3","flac","opus"];
subtitle_formats = ["ass","srt","pgs"];
language = "jp";

# Init variables
audio_track = 0;
language_key = "language";
subtitle_track = 0;
subtitle_key = "subtitle";
video_list = [];
video_path = [];
path = os.getcwd();
counter = 0;

print("The start of the script.");

# Get the video files from the current folder and its subfolders
for ext in video_ext:
    video_list += glob.glob(path + '/**/*.' + ext, recursive=True);

# Get the full path to the files
for filename in video_list:
    video_path.append(os.path.join(path,filename));

# Demuxing process
for f in video_path:
    counter += 1;
    print(counter);
    print('Demuxing "' + os.path.basename(f) + '".');
    metadata = subprocess.run(['ffprobe',
                            '-loglevel','error',
                            '-show_streams',
                            '-of','json',
                            f], capture_output=True).stdout;
    metadata = json.loads(metadata);
    metadata = metadata['streams'];
    audio_track_no = 0; # Audio track counter
    subtitle_track_no = 0; # Subtitle track counter
    for file_metadata in metadata:
        # Checking video tracks
        # WIP: Maybe in the future if it's relevant
        
        # Checking audio tracks
        if "audio" in file_metadata['codec_type']:
            for audio_codec in audio_codecs:
                if audio_codec in file_metadata['codec_name']:
                    file_metadata_tags = file_metadata['tags'];
                    audio_track_no += 1;
                    if language in file_metadata_tags['language'] and ("Commentary" or "commentary" not in file_metadata['title']):
                        audio_track = file_metadata['index']-1; # We have to substract the video track(s)... (WIP: To count video tracks maybe if it's relevant)
                        
        # Checking subtitle tracks
        if "subtitle" in file_metadata['codec_type']:
            for subtitle_format in subtitle_formats:
                if subtitle_format in file_metadata['codec_name']:
                    file_metadata_tags = file_metadata['tags'];
                    subtitle_track_no += 1;
                    if 'title' in file_metadata_tags.keys():
                        if "Sign" or "Signs" in file_metadata_tags['title']:
                            subtitle_track = subtitle_track_no-1; # The Signs/Songs subtitle track that I want demuxed.
                        
    if audio_track_no > 1:
        subprocess.run(["ffmpeg",
                    "-i",f,
                    '-loglevel','error',
                    '-map','0:v',
                    '-map','0:a:'+str(audio_track)+'?',
                    '-map','0:s?',
                    '-map','-0:s:'+str(subtitle_track)+'?',
                    '-map','0:t?',
                    '-c','copy',
                    '-disposition:v:0','default',
                    '-disposition:a:0','default',
                    '-disposition:s:0','default',
                    '-y',os.path.splitext(f)[0]+'_DAD.mkv']);
        print('The video was demuxed.');
        os.remove(f);
    else:
        print('The video"' + os.path.basename(f) +'" is single audio.');

print("------------------------");
print("A total of " + str(counter) + " episodes were demuxed.");
print("The end of the script.");
input("Press ANY key to close the window."); # Waiting for an input before closing the window.
