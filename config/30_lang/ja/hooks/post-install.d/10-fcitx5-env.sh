#!/bin/bash
#
#  「/etc/environment」にFcitx用の入力メソッド環境変数を
#  （無ければ）追記する処理
#
# 【目的】:
#   - GTK, Qt, Xアプリで日本語入力FcitxをデフォルトIMとして利用できるようにする
#   - 既存の同名環境変数が無い場合のみ、追記（重複防止）
#
set -e

ENV_FILE="/etc/environment"

append_if_missing() {
    KEY="$1"
    VALUE="$2"
    if ! grep -q "^$KEY=" "$ENV_FILE"; then
        echo "$KEY=$VALUE" >> "$ENV_FILE"
        echo "追加: $KEY=$VALUE"
    else
        echo "既に存在: $KEY（変更しません）"
    fi
}

append_if_missing "GTK_IM_MODULE" "fcitx"
append_if_missing "QT_IM_MODULE" "fcitx"
append_if_missing "XMODIFIERS" "@im=fcitx"

