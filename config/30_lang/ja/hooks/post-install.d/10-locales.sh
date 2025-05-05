#!/bin/sh
# post-install.d/10-locales.sh
# --- ロケール生成 ---
echo "ja_JP.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
update-locale LANG=ja_JP.UTF-8
