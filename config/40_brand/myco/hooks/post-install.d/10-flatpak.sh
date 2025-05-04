#!/bin/sh
set -e
# Flathub リポジトリを追加（もし無ければ）
flatpak remote-add --if-not-exists flathub \
  https://dl.flathub.org/repo/flathub.flatpakrepo
