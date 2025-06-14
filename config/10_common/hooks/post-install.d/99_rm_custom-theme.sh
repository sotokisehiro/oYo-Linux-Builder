#!/bin/bash
#
# /custom-themeディレクトリを削除する
#
# 【目的】:
#   - /custom-themeディレクトリは、ビルド中のみ必要なディレクトリで
#     ライブISOには不要ため、削除する
#
set -e

#custom-themeディレクトリを削除
rm -rf /custom-theme

