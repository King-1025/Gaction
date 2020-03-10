#!/usr/bin/env bash

# 检查安装ffmpeg
function check_ffmpeg()
{ 
  which ffmpeg
  if [ $? -eq 1 ]; then
     sudo apt autoremove \
     && \
     sudo apt update -y \
     && \
     sudo apt install ffmpeg -y
  else
     echo ffmpeg oK!
  fi
}
