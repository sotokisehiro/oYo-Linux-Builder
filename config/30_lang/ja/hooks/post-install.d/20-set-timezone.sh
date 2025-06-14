#!/bin/bash
#
# システムのタイムゾーンを日本（Asia/Tokyo）に設定します。
#
# 【目的】:
#   - タイムゾーンを Asia/Tokyo（JST、日本標準時）に統一
#   - /etc/localtime を正しいタイムゾーンにリンクし、/etc/time にも反映
#
set -e

# タイムゾーン設定
ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
echo "Asia/Tokyo" > /etc/time	
