#!/usr/bin/env python3
# -*- utf-8; -*-

import os
import sys
import time
import json
import shutil
import tempfile
 
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

def exec_command(path, comm):
    if path is not None and os.path.exists(path):
       print(comm)
       os.system(comm)
    else:
       print("%s not exist!" % path)

def exec_install_command(path):
    comm="android install %s" % path
    exec_command(path, comm)

def exec_view_command(path):
    comm="android view -f %s" % path
    exec_command(path, comm)

def exec_fusion_command(parts, path):
    comm="cat %s/* > %s" % (parts, path)
    exec_command(parts, comm)

def may_decompress_file(path):
    ch_dd=os.path.dirname(path)
    ch_ff=os.path.basename(path)
    comm, tmp, flag = None, None, None
    if ch_ff.endswith(".7z"):
       flag="7z"
       comm="7z e %s -o%s" % (path, ch_dd)
    elif ch_ff.endswith(".zip"):
       flag="zip"
       tmp = tempfile.mkdtemp()
       comm="unzip %s -d %s && mv %s/* %s" % (path, tmp, tmp, ch_dd)
    elif ch_ff.endswith(".tar"):
       flag="tar"
       comm="tar -xvf %s -C %s" % (path, ch_dd)
    elif ch_ff.endswith(".tar.gz"):
       flag="tgz"
       comm="tar -xzvf %s -C %s" % (path, ch_dd)
    elif ch_ff.endswith(".tar.bz2"):
       flag="tbz"
       comm="tar -xjvf %s -C %s" % (path, ch_dd)
    elif ch_ff.endswith(".tar.xz"):
       flag="txz"
       comm="tar -xJvf %s -C %s" % (path, ch_dd)

    if comm is not None:
    #   print(comm)
       print("\033[1;6;35m> decompress(%s) %s\033[m" % (flag, path))
       os.system(comm)
       os.remove(path)

    if tmp is not None:
       shutil.rmtree(tmp, ignore_errors=True)

def may_download_record(cxp, path):
    if path.endswith(".record"):
       data=None
       with open(path, "r") as jf:
          data=json.loads(jf.read())
       os.remove(path)
       if data is not None:
          print("")
          bsdir=os.path.dirname(path)
          parts=os.path.join(bsdir, "%s_parts" % data["name"])
          shutil.rmtree(parts, ignore_errors=True)
          os.makedirs(parts)

          rlist=None
          if "list" in cxp.base_query(str(data["id"])).data:
             rlist = cxp.data["list"]
          if rlist is None:
             print("query is null! %s" % data["id"])
             sys.exit(1)
             
          total, count =int(data["total"]), 1
          for r in data["record"]:
              print("\033[1;6;32m> download part... (%d/%d)\033[m" % (total, count))
              oid=None
              for nn in rlist:
                if nn["name"] == r["part"]:
                   oid=nn["objectId"]
                   break
              if oid is None:
                 print("not found part: %s" % r["part"])
                 continue
              path=cxp.download(r["part"], str(oid), parts)
              print("")
              may_decompress_file(path)
              print("")
              count+=1
          path=os.path.join(bsdir, data["name"])
          exec_fusion_command(parts, path)
          shutil.rmtree(parts, ignore_errors=True)
          print("")
    return path
