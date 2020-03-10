#!/usr/bin/env bash

function check_root()
{
  if [ -e "$1" ]; then
     echo "$1"
   else
     echo "$(pwd)"
  fi
}
