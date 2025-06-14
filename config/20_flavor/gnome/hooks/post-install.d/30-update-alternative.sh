#!/bin/bash
#
# /custom-theme/ディレクトリのロゴ/テーマ等を必要に応じてリサイズして、gnomeに登録する
#
# 【目的】:
#   - サイズ違いのロゴファイルを用意するのは手間なので、/custom-theme/ディレクトリに
#     svgファイルを置いておき、このスクリプトでリサイズして各所に配置する。
#   - /custom-theme/ディレクトリのplymouth、themeも、をこのスクリプトを使って配置する
#
set -e

#plymouthの変更
mkdir -p /usr/share/plymouth/themes/custom
cp -a /custom-theme/plymouth/. /usr/share/plymouth/themes/custom/
update-alternatives --install  /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/custom 60

#テーマ
mkdir -p /usr/share/desktop-base/custom-theme
cp -a /custom-theme/theme/.  /usr/share/desktop-base/custom-theme
update-alternatives --install /usr/share/desktop-base/active-theme desktop-theme /usr/share/desktop-base/custom-theme 60

update-initramfs -u

