#!/bin/bash
set -e

THEME_NAME="custom-spinner"

if [ -x /usr/sbin/plymouth-set-default-theme ]; then
  echo "Setting Plymouth theme to $THEME_NAME"
  plymouth-set-default-theme "$THEME_NAME"
  update-initramfs -u
fi

