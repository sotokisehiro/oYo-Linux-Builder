#!/bin/bash
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

