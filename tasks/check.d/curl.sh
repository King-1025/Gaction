#!/usr/bin/env bash

# 检查安装curl
function check_curl()
{ 
   source $CHECK_DIR/apt.sh && apt_check curl
}

#check_curl
