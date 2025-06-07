#!/bin/bash
set -e

GRUB_FILE="/etc/default/grub"
THEME_IMG="/usr/share/desktop-base/custom-theme/grub/grub-16x9.png"

if [ -f "$GRUB_FILE" ] && [ -f "$THEME_IMG" ]; then
    sed -i '/^GRUB_BACKGROUND=/d' "$GRUB_FILE"
    echo "GRUB_BACKGROUND=\"$THEME_IMG\"" >> "$GRUB_FILE"
fi

update-grub


