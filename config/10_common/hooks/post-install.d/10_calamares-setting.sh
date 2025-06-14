#!/bin/bash
#
# Calamaresで使用する以下の画像を、/custom-theme/からコピーして配置します。
#  ・Calamares起動画面に表示する画像(welcome.png)
#  ・インストール中に表示するスライドショー画像
# 【目的】:
#   - Calamaresで使用する画像を簡単に差し替えできるようにする
#

set -e

# コピー先ディレクトリ
DEST_DIR="/etc/calamares/branding/custom"
mkdir -p "$DEST_DIR"

# 画像ファイルをコピー
find /custom-theme/calamares -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.svg' \) -exec cp {} $DEST_DIR \;

# QMLファイル生成
QML_FILE="${DEST_DIR}/show.qml"

echo '[INFO] Generating show.qml...'
{
echo 'import QtQuick 2.0;'
echo 'import calamares.slideshow 1.0;'
echo ''
echo 'Presentation'
echo '{'
echo '    id: presentation'
echo ''
echo '    Timer {'
echo '        interval: 10000'
echo '        running: true'
echo '        repeat: true'
echo '        onTriggered: presentation.goToNextSlide()'
echo '     }'

# スライド画像を列挙して追加
find "$DEST_DIR" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.svg' \) | sort | while read -r img; do
  fname=$(basename "$img")
  
  # welcome.png は除外
  if [ "$fname" != "welcome.png" ]; then
    echo '    Slide {'
    echo '        Image {'
    echo "            source: \"${fname}\""
    echo '            width: 864'
    echo '            fillMode: Image.PreserveAspectFit'
    echo '            anchors.centerIn: parent'
    echo '        }'
    echo '    }'
  fi
done

echo '}'
} > "$QML_FILE"

chmod 644 "$QML_FILE"

