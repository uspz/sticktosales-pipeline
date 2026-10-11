#!/bin/bash
# uso: add_cover.sh <capa.png> <video.mp4> <saida.mp4>
ffmpeg -y -loglevel error -loop 1 -t 0.5 -i "$1" -f lavfi -t 0.5 -i anullsrc=r=44100:cl=stereo -i "$2" -filter_complex "[0:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[c];[2:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v];[1:a]aformat=sample_rates=44100:channel_layouts=stereo[ca];[2:a]aresample=44100,aformat=channel_layouts=stereo[va];[c][ca][v][va]concat=n=2:v=1:a=1[ov][oa]" -map "[ov]" -map "[oa]" -c:v libx264 -crf 18 -c:a aac -b:a 192k "$3"
