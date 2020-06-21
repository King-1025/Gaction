#!/usr/bin/env bash

# 检查安装pip包
function check_requests()
{
   pip3 install requests requests-toolbelt
   echo requests oK!
}
