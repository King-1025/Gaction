#!/usr/bin/env bash

# 检查安装curl
function check_curl()
{ 
  which curl
  if [ $? -eq 1 ]; then
     sudo apt autoremove \
     && \
     sudo apt update -y \
     && \
     sudo apt install curl -y
  else
     echo curl oK!
  fi
}
