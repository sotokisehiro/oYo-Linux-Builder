#!/bin/bash
set -e

#plymouthの変更
update-alternatives --install  /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/custom-spinner 60

#vendor-logos
mkdir -p /usr/share/desktop-base/custom-logos
cp /tmp/logos/logo.svg /usr/share/desktop-base/custom-logos/logo.svg
cp /tmp/logos/logo-text.svg /usr/share/desktop-base/custom-logos/logo-text.svg
cp /tmp/logos/logo-text.svg /usr/share/desktop-base/custom-logos/logo-text-version.svg

rsvg-convert  -w 64 -h 64 -o /usr/share/desktop-base/custom-logos/logo-64.png /tmp/logos/logo.svg
rsvg-convert  -w 128 -h 128 -o /usr/share/desktop-base/custom-logos/logo-128.png /tmp/logos/logo.svg
rsvg-convert  -w 256 -h 256 -o /usr/share/desktop-base/custom-logos/logo-256.png /tmp/logos/logo.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/custom-logos/logo-text-64.png /tmp/logos/logo-text.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/custom-logos/logo-text-128.png /tmp/logos/logo-text.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/custom-logos/logo-text-256.png /tmp/logos/logo-text.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/custom-logos/logo-text-version-64.png /tmp/logos/logo-text-version.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/custom-logos/logo-text-version-128.png /tmp/logos/logo-text-version.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/custom-logos/logo-text-version-256.png /tmp/logos/logo-text-version.svg

update-alternatives --install /usr/share/images/vendor-logos vendor-logos /usr/share/desktop-base/custom-logos 60 \
 --slave /usr/share/icons/vendor/64x64/emblems/emblem-vendor.png emblem-vendor-64 /usr/share/desktop-base/custom-logos/logo-64.png \
 --slave /usr/share/icons/vendor/128x128/emblems/emblem-vendor.png emblem-vendor-128 /usr/share/desktop-base/custom-logos/logo-128.png \
 --slave /usr/share/icons/vendor/256x256/emblems/emblem-vendor.png emblem-vendor-256 /usr/share/desktop-base/custom-logos/logo-256.png \
 --slave /usr/share/icons/vendor/scalable/emblems/emblem-vendor.svg emblem-vendor-scalable /usr/share/desktop-base/custom-logos/logo.svg \
 --slave /usr/share/icons/vendor/64x64/emblems/emblem-vendor-symbolic.png emblem-vendor-symbolic-64 /usr/share/desktop-base/custom-logos/logo-64.png \
 --slave /usr/share/icons/vendor/128x128/emblems/emblem-vendor-symbolic.png emblem-vendor-symbolic-128 /usr/share/desktop-base/custom-logos/logo-128.png \
 --slave /usr/share/icons/vendor/256x256/emblems/emblem-vendor-symbolic.png emblem-vendor-symbolic-256 /usr/share/desktop-base/custom-logos/logo-256.png \
 --slave /usr/share/icons/vendor/scalable/emblems/emblem-vendor-symbolic.svg emblem-vendor-symbolic-scalable /usr/share/desktop-base/custom-logos/logo.svg \
 --slave /usr/share/icons/vendor/64x64/emblems/emblem-vendor-white.png emblem-vendor-white-64 /usr/share/desktop-base/custom-logos/logo-64.png \
 --slave /usr/share/icons/vendor/128x128/emblems/emblem-vendor-white.png emblem-vendor-white-128 /usr/share/desktop-base/custom-logos/logo-128.png \
 --slave /usr/share/icons/vendor/256x256/emblems/emblem-vendor-white.png emblem-vendor-white-256 /usr/share/desktop-base/custom-logos/logo-256.png \
 --slave /usr/share/icons/vendor/scalable/emblems/emblem-vendor-white.svg emblem-vendor-white-scalable /usr/share/desktop-base/custom-logos/logo.svg

#Debian-logos
cp /tmp/logos/logo.svg /usr/share/desktop-base/debian-logos/logo.svg
cp /tmp/logos/logo-text.svg /usr/share/desktop-base/debian-logos/logo-text.svg
cp /tmp/logos/logo-text.svg /usr/share/desktop-base/debian-logos/logo-text-version.svg

rsvg-convert  -w 64 -h 64 -o /usr/share/desktop-base/debian-logos/logo-64.png /tmp/logos/logo.svg
rsvg-convert  -w 128 -h 128 -o /usr/share/desktop-base/debian-logos/logo-128.png /tmp/logos/logo.svg
rsvg-convert  -w 256 -h 256 -o /usr/share/desktop-base/debian-logos/logo-256.png /tmp/logos/logo.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/debian-logos/logo-text-64.png /tmp/logos/logo-text.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/debian-logos/logo-text-128.png /tmp/logos/logo-text.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/debian-logos/logo-text-256.png /tmp/logos/logo-text.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/debian-logos/logo-text-version-64.png /tmp/logos/logo-text-version.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/debian-logos/logo-text-version-128.png /tmp/logos/logo-text-version.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/debian-logos/logo-text-version-256.png /tmp/logos/logo-text-version.svg

#calamares logo
rsvg-convert  -w 128 -h 128 -o /etc/calamares/branding/custom/logo.png /tmp/logos/logo.svg

#テーマ
update-alternatives --install /usr/share/desktop-base/active-theme desktop-theme /usr/share/desktop-base/custom-theme 60

#壁紙
mkdir -p /usr/share/backgrounds/custom/
cp /tmp/backgrounds/background.png /usr/share/backgrounds/custom/background.png

update-initramfs -u
