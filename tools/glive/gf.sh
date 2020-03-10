#!/usr/bin/env bash

function app()
{
   local argc=$1; shift 1; declare -a argv=("$@")
#   echo argc: $argc
#   echo argv: ${argv[@]}
   if [ $argc -ge 1 ]; then
      if [ "$1" != "range" ]; then
	 if [ "$1" == "json" ]; then
            base_request_json | jq .event.feed.data -M
         else
            ${argv[@]}
	 fi
         exit 0
      else
	 shift 1
      fi
   fi
   local data=$(mktemp -u)
   request_json $data
   format_video_data $data $@
   rm -rf $data
}

function request_json()
{
   if [ $# -eq 1 ]; then
      echo $(base_request_json) > $1
   fi
}

function base_request_json()
{
   curl -sL "https://livestream.com/accounts/27235681/events/8197481/player?width=960&height=540&enableInfoAndActivity=true&defaultDrawer=feed&autoPlay=true&mute=false" | sed -n "/window.config/p" | sed "s/\(.*\)window.config = \(.*\);\(.*\)/\2/g"
}

function filter_video_data()
{
   if [ $# -eq 2 ]; then
    if [ -e $1 ]; then
       pick $1 video "" > $2
       #jq -r .event.feed.data $1 > $2
    fi
  fi
}

function format_video_data()
{
   if [ $# -ge 1 ]; then
    if [ -e $1 ]; then
       local video=$(mktemp -u)

       filter_video_data $1 $video

       #set -x
       local count=$(jq ".|length" $video)
       local s_v=0
       local e_v=$count
       if [ $# -ge 2 ]; then s_v=$2; fi
       if [ $# -ge 3 ]; then e_v=$3; fi
       #set +x

       echo details:
       for ((i=$s_v; i < $e_v; i++)); do
           echo "  - "video: $i
	   echo "    "caption: $(pick $video caption $i)
	   echo "    "duration: $(pick $video duration $i)
	   echo "    "publish: $(ftime "$(pick $video publish $i)")
	   echo "    "view: $(pick $video view $i)
	   echo "    "like: $(pick $video like $i)
	   echo "    "comment: $(pick $video comment $i)
	   echo "    "qualities: && list_qualities $video $i
           echo ""
       done
       echo total: $count
       rm -rf $video
    fi
  fi
}

function list_qualities()
{
  if [ $# -eq 2 ]; then
     local d=$(mktemp -u)
     local v=$(mktemp -u)
     pick $1 qualities $2 > $d
     curl -sL "$(pick $1 m3u8url $2)" > $v
#     cat data/0 > $v
     local l=$(jq ".|length" $d)
     for ((j=0; j < $l; j++)); do
	echo "      - "id: $j
	echo "        "qname: $(pick "$d" qname $j)
        echo "        "width: $(pick "$d" width $j)
        echo "        "height: $(pick "$d" height $j)
	echo "        "size: $(pick "$d" size $j)
	echo "        "url: $(sed -n "$((3*j+4))p" $v)
     done
     rm -rf $d $v
 fi
}

function pick()
{
   if [ $# -eq 3 ]; then
      if [ -e "$1" ]; then
	 local i=$3
	 local s=""
         case "$2" in
	   "video")     s=".event.feed.data";;
	   "caption")   s=".[$i].data.caption";;
	   "duration")  s=".[$i].data.duration";;
	   "publish")   s=".[$i].data.publish_at";;
           "view")      s=".[$i].data.views";;
	   "like")      s=".[$i].data.likes.total";;
           "comment")   s=".[$i].data.comments.total";;
	   "m3u8url")   s=".[$i].data.m3u8_url";;
	   "qualities") s=".[$i].data.asset.qualities";;
	   "width")     s=".[$i].width";;
	   "height")    s=".[$i].height";;
	   "qname")     s=".[$i].name";;
	   "size")      s=".[$i].bytesize";;
	 esac
	 if [ "" != "$s" ]; then
            eval jq -r $s $1
	 else
            echo "null"
	 fi
      fi
   fi
}

function ftime()
{
   if [ $# -eq 1 ]; then
      date --date="$1" "+%Y-%m-%d_%H:%M:%S"
   fi
}

function once()
{
   local url_list=$(curl -sL "https://livestream.com/accounts/27235681/events/8197481/player?width=960&height=540&enableInfoAndActivity=true&defaultDrawer=feed&autoPlay=true&mute=false" | sed -n "/window.config/p" | sed "s/\(.*\)window.config = \(.*\);\(.*\)/\2/g" | jq .event.feed.data[].data.m3u8_url -r | sed "s/api/player-api/g")
   local i=0

   rm -rf data
   mkdir data
   for url in $url_list; do
      echo -n "$i: fetch $url..."
      curl -o "data/$i" -sL $url
      if [ $? -eq 0 ]; then
         echo -e "oK!\n"
      else
         echo -e "nO!\n"
      fi
      ((i++))
   done
   echo "total: $i"
}

app $# $*
