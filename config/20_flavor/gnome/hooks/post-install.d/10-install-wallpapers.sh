#!/bin/bash
#
# /custom-theme/ディレクトリの画像を、壁紙として配置する
#
# 【目的】:
#   - 壁紙を各所に配置するのは手間であるため、必要な画像を/custom-theme/ディレクトリに
#     まとめて配置しておき、このスクリプトで各所に配置する。
#
set -e

#-----------------------------------------------------
# Debianの壁紙を削除
#-----------------------------------------------------
rm /usr/share/gnome-background-properties/*.xml
rm -rf /usr/share/backgrounds/*

#-----------------------------------------------------
# default 壁紙
#-----------------------------------------------------
mkdir -p /usr/share/backgrounds/custom/
cp /custom-theme/default-backgrounds/background-default.png /usr/share/backgrounds/custom/background-default.png
cp /custom-theme/default-backgrounds/background-dark.png /usr/share/backgrounds/custom/background-dark.png


#-----------------------------------------------------
# 壁紙
#-----------------------------------------------------
# コピー先ディレクトリ
WALLPAPER_DIR="/usr/share/backgrounds/custom"
mkdir -p /usr/share/gnome-background-properties/
XML_FILE="/usr/share/gnome-background-properties/custom.xml"

# 壁紙ファイルをコピー
mkdir -p "$WALLPAPER_DIR"
find /custom-theme/backgrounds -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.svg' \) -exec cp {} $WALLPAPER_DIR \;

# XMLのヘッダ部分
echo '<?xml version="1.0" encoding="UTF-8"?>' > "$XML_FILE"
echo '<wallpapers>' >> "$XML_FILE"

# 各画像をXMLに登録
find "$WALLPAPER_DIR" -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.svg' \) | sort | while read -r img; do
  name=$(basename "$img")
  echo '  <wallpaper deleted="false">' >> "$XML_FILE"
  echo "    <name>${name}</name>" >> "$XML_FILE"
  echo "    <filename>${img}</filename>" >> "$XML_FILE"
  echo '    <options>zoom</options>' >> "$XML_FILE"
  echo '    <pcolor>#000000</pcolor>' >> "$XML_FILE"
  echo '    <scolor>#000000</scolor>' >> "$XML_FILE"
  echo '  </wallpaper>' >> "$XML_FILE"
done

# XMLのフッタ
echo '</wallpapers>' >> "$XML_FILE"

# パーミッション調整（念のため）
chmod 644 "$XML_FILE"

