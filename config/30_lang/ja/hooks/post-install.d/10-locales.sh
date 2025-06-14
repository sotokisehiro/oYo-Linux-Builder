#!/bin/sh
#
# /etc/locale.gen に日本語ロケール (ja_JP.UTF-8) を追加し、
# 日本語ロケールファイルを生成・システムデフォルトを日本語化します。
#
# 【目的】:
#   - システム全体のデフォルト言語を ja_JP.UTF-8 に設定
#   - 日本語ロケールを生成し、日本語表示・日本語入力が可能な環境を作る
#

# 「/etc/locale.gen」に日本語ロケール（ja_JP.UTF-8）の行を追加
echo "ja_JP.UTF-8 UTF-8" >> /etc/locale.gen

# ロケールファイルを生成
locale-gen

# デフォルトロケールを日本語に設定
update-locale LANG=ja_JP.UTF-8
