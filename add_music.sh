#!/bin/bash
# uso: add_music.sh <video_com_capa.mp4> <saida.mp4> [trilha.wav]   (mistura lo-fi baixinho com ducking sob a voz)
V="$1"; O="$2"; T="${3:-$(dirname "$0")/trilhas/lofi1_original.mp3}"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$V")
OFF=$(python3 -c "import random; print(round(random.uniform(0, max(0, 96-$DUR-1)),2))")
ffmpeg -y -loglevel error -i "$V" -ss $OFF -i "$T" -filter_complex "[1:a]atrim=0:${DUR},asetpts=N/SR/TB,afade=t=in:d=1.0,afade=t=out:st=$(python3 -c "print(max(0,$DUR-3))"):d=3,aresample=44100,loudnorm=I=-14:TP=-1.5:LRA=11,volume=0.20[m];[0:a]aresample=44100,asplit[v][sc];[m][sc]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=400:makeup=1[md];[v][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14.5:TP=-2:LRA=11,aresample=44100,alimiter=limit=0.85[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k "$O"
