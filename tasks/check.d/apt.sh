#!/usr/bin/env bash

function apt_check()
{
  local list=""
  for i in "$@"; do
     echo "> apt checking $i ..."
     which $i
     if [ $? -eq 1 ]; then
	list="$i $list"
     else
        echo -e "$i oK!\n"
     fi
  done
  if [ "$list" != "" ]; then
     sudo apt autoremove \
     && \
     sudo apt update -y \
     && \
     sudo apt install $list -y
  fi
}

#apt_check ls cat curl axel wget hf 
