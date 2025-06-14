#!/bin/bash
#
# /etc/skel/にあるユーザー用のアイコンを削除する
#
# 【目的】:
#   - このファイルがあるとログイン画面などで、ユーザーアイコンに
#     Debianロゴが表示されてしまうため
#
set -e

#ユーザーのアイコンを削除
rm /etc/skel/.face
rm /etc/skel/.face.icon
rm /home/live/.face
rm /home/live/.face.icon
