mkdir -p config/20_gnome/hooks/post-install.d
cat << 'EOF' > config/20_gnome/hooks/post-install.d/10-enable-gdm3.sh
#!/bin/sh
set -e

# chroot 内で動くのでパスは chroot ルートからの絶対パス
if [ -e /lib/systemd/system/gdm3.service ]; then
  echo "→ Enabling gdm3 for graphical.target"
  mkdir -p /etc/systemd/system/graphical.target.wants
  ln -sf /lib/systemd/system/gdm3.service \
         /etc/systemd/system/graphical.target.wants/gdm3.service
else
  echo "→ gdm3.service not found; skipping"
fi
EOF
