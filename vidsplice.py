#!/usr/bin/env python3

import argparse 
import subprocess
import codecs
import pysubs
import os
import ast
from datetime import *
from ffmpy import FFmpeg

parser = argparse.ArgumentParser()
parser.add_argument('-t', metavar='timestamps', action='store', dest='t')
parser.add_argument('-i', metavar='infile', action='store', dest='i')
parser.add_argument('-o', metavar='outfile', action='store', dest='o')

args = parser.parse_args()

with open(args.t, 'r') as ts:
    times = ast.literal_eval(ts.read())
    ts.close()
    starts = [t[0] for t in times]
    ends = [t[1] for t in times]
    for i in range(len(times) - 1):
        start = datetime.strptime(times[i][1], '%H:%M:%S')
        end = datetime.strptime(times[i+1][0], '%H:%M:%S')
        substart = start - timedelta(seconds=2)
        subend = end + timedelta(seconds=2)
        elapsed = end - start
        seconds = elapsed.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        time_elapsed = ''
        if hours > 0:
            time_elapsed += str(hours)+' hrs '
        if minutes > 0:
            time_elapsed += str(minutes)+' min '
        if seconds > 0:
            time_elapsed += str(seconds)+' sec'
        with codecs.open('subtitles.srt', 'a', 'utf-8-sig') as s:
            s.write(str(i+1))
            s.write('\n')
            s.write(str(substart)[11:]+',000 --> '+str(subend)[11:]+',000\n')
            s.write(time_elapsed+' skipped \n'+ times[i][2]+'\n \n')
            s.close()

subs = pysubs.load('subtitles.srt')
subs.save('subtitles.ass')

subtitle = FFmpeg(
    inputs = {
        args.i : None
    },
    outputs = {
        'subtitled.mp4' : '-vf "ass=subtitles.ass"'
    }
)

subtitle.run()

for i in range(len(starts)):
    name = str(i) + '.mp4'

    if i == 0: a = 'w'
    else: a = 'a'
    with open('videos.txt', a) as v:
        v.write("file '"+name+"'\n")
        v.close()
    ffmpeg = FFmpeg(
        inputs = {
            'subtitled.mp4' : None
        },
        outputs = {
            name : '-ss '+starts[i]+' -c copy -to '+ends[i]
        }
    )
    ffmpeg.run()

concat = FFmpeg(
    inputs = {
        'videos.txt' : ['-f', 'concat', '-safe', '0']
    },
    outputs = {
        args.o : '-c copy'
    }
)

concat.run()

for i in range(len(starts)):
    try:
        os.remove(str(i) + '.mp4')
    except FileNotFoundError: 
        print('No such file or directory: '+str(i)+'.mp4')

os.remove('videos.txt')
os.remove('subtitles.srt')
os.remove('subtitles.ass')
os.remove('subtitled.mp4')
print(args.t, args.i, args.o)

