#!/bin/bash
#
# flathubリポジトリを追加
#
# 【目的】:
#   - flathubリポジトリを追加
#
set -e

#flathubリポジトリを追加
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

