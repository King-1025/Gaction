#!/usr/bin/env bash

# 检查安装pip包
function check_requests()
{
   pip install requests requests-toolbelt
   echo requests oK!
}
