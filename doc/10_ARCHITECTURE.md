# oYo-Builder 仕組み

## oYo-Builder の仕組み：概要

1. **設定ファイルレイヤーをマージ**
   - `config/10_common` → `config/20_flavor` → `config/30_lang` → `config/40_brand` の順に  
   - `packages.txt` や `overlay/`、`hooks/`、`templates/` をそれぞれ読み込み

2. **chroot 準備**
   - 古い chroot を削除し、`debootstrap` で最小ベースシステムを展開  
   - `/proc`・`/sys`・`/dev` をマウントし、ホストの APT キャッシュもバインド

3. **パッケージのインストール**
   - マージした `packages.txt` に従い、`apt-get install`  
   - `hooks/pre-install.d/` → パッケージ前フック  
   - `hooks/post-install.d/` → パッケージ後フック  

4. **Overlay＆テンプレートの適用**
   - `overlay/` 配下のファイルを chroot 内に丸ごとコピー  
   - `templates/` 配下の Jinja2 テンプレートをレンダリングして設定ファイルを生成

5. **Live イメージ整形**
   - 最新のカーネルと initrd を `chroot/live/` にコピー  
   - 仮想ファイルシステムをアンマウントしてから `mksquashfs` で `/live/filesystem.squashfs` を作成

6. **ISO 生成**
   - 必要なディレクトリ（`boot/`, `EFI/`, `usr/lib/grub/`, `live/` など）だけを `rsync` で `work/iso/` に展開  
   - カーネル／initrd を `live/` にコピー  
   - `grub-mkrescue` で BIOS/UEFI 両対応の ISO をビルド

7. **後片付け**
   - chroot 内のマウント解除  
   - APT キャッシュバインド解除  
   - 完成した ISO は `open.yellow.os-<VERSION>.iso` として出力

---

## 全体フロー図

```mermaid
flowchart TB
  subgraph Config レイヤーのマージ
    A1[10_common] --> A2[20_flavor]
    A2 --> A3[30_lang]
    A3 --> A4[40_brand]
  end

  subgraph chroot 準備
    A4 --> B1[rm -rf work/chroot]
    B1 --> B2[debootstrap base system]
    B2 --> B3[マウント: /proc,/sys,/dev]
    B3 --> B4[バインド: /var/cache/apt/archives]
  end

  subgraph パッケージ & フック
    B4 --> C1[apt-get update/install]
    C1 --> C2[hooks/pre-install.d/*.sh]
    C2 --> C3[hooks/post-install.d/*.sh]
  end

  subgraph Overlay & Templates
    C3 --> D1[overlay/ を chroot へコピー]
    D1 --> D2[templates/ をレンダリング → 設定ファイル生成]
  end

  subgraph Live イメージ作成
    D2 --> E1[最新の vmlinuz, initrd を live/ へ]
    E1 --> E2[umount 仮想 FS]
    E2 --> E3[mksquashfs work/chroot → live/filesystem.squashfs]
  end

  subgraph ISO 生成
    E3 --> F1[rsync 必要なファイルだけ to work/iso]
    F1 --> F2[カーネル & initrd を work/iso/live]
    F2 --> F3[grub-mkrescue で ISO 作成]
  end

  subgraph クリーンアップ
    F3 --> G1[umount chroot]
    G1 --> G2[解除: APT キャッシュ]
    G2 --> H[完成: open.yellow.os-<VERSION>.iso]
  end
```
