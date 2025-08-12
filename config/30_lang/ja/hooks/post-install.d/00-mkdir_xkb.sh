#!/bin/bash
#
# convertedKeymapPathのディレクトリ作成
#
# 【目的】:
#   - Calamaresのキーボード設定、convertedKeymapPathのディレクトリ作成
#   -  (空ディレクトリはGitHubでは扱えないため)
#
set -e

mkdir -p /usr/share/X11/xkb/
