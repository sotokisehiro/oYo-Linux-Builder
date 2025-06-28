#!/bin/bash
#
# ネットワークチェックの無効化
#
# 【目的】:
#   - 起動時のネットワークチェックに時間がかかるため無効化
#
set -e

# ネットワークチェックの無効化
systemctl disable systemd-networkd-wait-online.service
systemctl mask systemd-networkd-wait-online.service

