#!/usr/bin/env python3
# -*- utf-8; -*-

import os
import sys
import time
 
def formatSimpleTime(st):
    simple_format = "%Y-%m-%d %H:%M:%S"
    return time.strftime(simple_format, time.localtime(st))

def formatGTMTime(st):
    gmt_format = '%a, %d %b %y %h:%m:%s GMT+0800 (中国标准时间)'
    return time.strftime(gmt_format, st)

def getFileLastGMTime(path):
    if os.path.exists(path):
       st = time.localtime(os.stat(path).st_mtime)
       return formatGTMTime(st)
    else:
       return None

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
           value = float(n) / prefix[s]
           return '%.1f%s' % (value,s)
    return '%sB' % n

def humanbytes(B):
    return bytes2human(B)

def _humanbytes(B):
    'Return the given bytes as a human friendly KB, MB, GB, or TB string'
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776
 
    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B/GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B/TB)
 
def progress(num, Sum, label = "", bar_length = 20):
    """
    显示上传进度条
    num：已上传大小
    Sum：文件总大小
    #l：定义进度条大小
    """
    percent = float(num) / float(Sum)
    hashes = '=' * int(percent * bar_length)  # 定义进度显示的数量长度百分比
    spaces = ' ' * (bar_length - len(hashes))  # 定义空格的数量=总长度-显示长度
 
    sys.stdout.write(
        "\r%s[%s] %d%%  %s/%s " % (label, hashes + spaces, percent * 100, humanbytes(num), humanbytes(Sum)))  # 输出显示进度条
    sys.stdout.flush()  # 强制刷新到屏幕
