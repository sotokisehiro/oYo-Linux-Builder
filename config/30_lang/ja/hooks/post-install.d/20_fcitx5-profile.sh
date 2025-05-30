#!/bin/bash

set -e

LIVE_USER_HOME="/home/live"
FCITX5_PROFILE_DIR="${LIVE_USER_HOME}/.config/fcitx5"
PROFILE_FILE="${FCITX5_PROFILE_DIR}/profile"

# ディレクトリ作成
mkdir -p "$FCITX5_PROFILE_DIR"

# プロファイル内容を書き込み
cat > "$PROFILE_FILE" <<EOF
[Groups/0]
# Group Name
Name=デフォルト
# Layout
Default Layout=jp
# Default Input Method
DefaultIM=mozc

[Groups/0/Items/0]
# Name
Name=keyboard-jp
# Layout
Layout=

[Groups/0/Items/1]
# Name
Name=mozc
# Layout
Layout=

[GroupOrder]
0=デフォルト
EOF

# 所有権をliveユーザーに変更（存在する場合）
if id live &>/dev/null; then
    chown -R live:live "$FCITX5_PROFILE_DIR"
fi

