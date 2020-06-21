#!/usr/bin/env bash

# 检查安装pip包
function check_yaml()
{
#   pip3 install PyYAML
   pip3 install --ignore-installed PyYAML
   echo PyYAML oK!
}
