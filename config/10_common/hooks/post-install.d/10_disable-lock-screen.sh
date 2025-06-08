#!/bin/bash
set -e

# ライブ起動時のロックスクリーンの無効化
gsettings set org.gnome.desktop.lockdown disable-lock-screen true
