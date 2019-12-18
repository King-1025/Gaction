#!/usr/bin/env python3
# -*- coding: utf-8; -*-

import sys

def getRid(pwd,path):
    plist,fname = fliter(path)
    if plist is not None and fname is not None:
      lp = len(plist)
      if lp > 0:
        q = None
        if plist[0] == "":
          q = query("/0")
          plist.
       else:
          q = query(pwd)
      for i in range(lp):
        if q is not None:
           pass 
      

def fliter(path):
    chlist = []
    ff = None
    if path is not None:
       plist = path.split('/')
       plen  = len(plist)
       for i in range(plen):
           cpt = plist[i]
           if cpt == "":
              if i == 0:
                 chlist.append("")
              continue
           elif cpt == ".":
              continue
           elif cpt == "..":
              if len(chlist) > 0:
                 chlist.pop()
              else:
                 chlist = None
                 break
           elif cpt == "...":
              if len(chlist) > 1:
                 chlist.pop()
                 chlist.pop()
              else:
                 chlist = None
                 break
           else:
              chlist.append(cpt)
       if chlist != None:
         if plist[-1] != "":
            if len(chlist) > 0:
                ff = chlist.pop()
    return chlist, ff

if __name__ == "__main__":
   print(getRid(str(sys.argv[1])))
