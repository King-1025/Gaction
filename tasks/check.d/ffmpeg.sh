#!/usr/bin/env bash

# 检查安装ffmpeg
function check_ffmpeg()
{ 
   source apt.sh && apt_check ffmpeg
}

#check_ffmpeg
