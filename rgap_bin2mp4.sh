#!/bin/bash
for name in *.bin; do
  ffmpeg -i "$name" -vf scale=1080:720 "${name%.*}.mp4"
done
