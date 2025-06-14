# oYo-Builder 仕組み

## oYo-Builder の仕組み：概要

1. **設定ファイルレイヤーの合成**
   - `config/10_common` → `config/20_flavor` → `config/30_lang` → `config/40_brand` の順で
   - `packages.txt`、`overlay/`、`hooks/`、`templates/` をそれぞれマージ

2. **chroot 準備**
   - 古い chroot を削除し、`mmdebstrap` で最小ベースシステム＋packages.txt記載パッケージを一括展開  
   - `/proc`・`/sys`・`/dev` をマウントし、ホストのAPTキャッシュもバインド

3. **フック（Hook）処理の実行**
   - `hooks/post-install.d/*.sh` → chroot展開・ユーザー作成・カスタム後に自動実行

4. **Overlay＆テンプレートの適用**
   - 各レイヤーの `overlay/` 配下ファイルを chroot 直下に順次コピー（後勝ち）
   - `templates/` 配下の Jinja2テンプレート（例: os-release, branding.desc, grub.cfg, plymouth など）をYAML変数付きでレンダリングし配置

5. **Live イメージ整形と Secure Boot対応**
   - 最新のカーネル/initrd を chroot/live/ にコピー
   - Secure Boot対応のshim, grubx64.efi.signed, mmx64.efiを ISO/EFI/BOOT 配下に配置
   - 仮想FSをアンマウントし、mksquashfsで live/filesystem.squashfs を生成

6. **ISO 生成**
   - 必要なディレクトリ（`boot/`, `EFI/`, `usr/lib/grub/`, `live/` など）だけを `rsync` で `work/iso/` に展開
   - `grub-mkrescue` で BIOS/UEFI 両対応のISOをビルド

7. **後片付け・成果物出力**
   - chroot・バインドのマウント解除
   - 完成したISOはプロジェクトルート直下に `openyellowos-1.0-ja.iso` のような命名で出力

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
    B1 --> B2[mmdebstrap base system + packages]
    B2 --> B3[マウント: /proc,/sys,/dev]
    B3 --> B4[バインド: /var/cache/apt/archives]
  end

  subgraph フックとカスタマイズ
    C1 --> C2[hooks/post-install.d/*.sh]
  end

  subgraph Overlay & Templates
    C2 --> D1[overlay/ を chroot へコピー（順次/後勝ち）]
    D1 --> D2[templates/をレンダリング→設定ファイル生成]
  end

  subgraph Liveイメージ作成とSecureBoot
    D2 --> E1[最新の vmlinuz, initrd を live/ へ]
    E1 --> E2[shim, grubx64.efi.signed, mmx64.efi 配置]
    E2 --> E3[umount 仮想 FS]
    E3 --> E4[mksquashfs work/chroot → live/filesystem.squashfs]
  end

  subgraph ISO 生成
    E4 --> F1[rsync 必要なファイルだけ to work/iso]
    F1 --> F2[grub-mkrescue で ISO 作成]
  end

  subgraph クリーンアップと成果物
    F2 --> G1[umount chroot]
    G1 --> G2[解除: APT キャッシュ]
    G2 --> H[完成: openyellowos-1.0-ja.iso]
  end
```

---

### 【主なテンプレート適用例】
- `os-release`  ... /etc/os-release にシステム情報を書き込み
- `branding.desc` ... Calamares インストーラ用ブランド定義
- `grub.cfg` ... BIOS/UEFIブート時のGRUB設定
- `plymouth-theme.conf` ... 起動画面アニメーション設定

---

### 【補足】
- 各 config レイヤーは**後勝ち（brand > lang > flavor > common）**で合成されます。
- Secure Boot対応はISO内部の`EFI/BOOT/`にshim/grubx64.efi.signed/mmx64.efiを配置することで実現します。
- 完成ISOはプロジェクトルート直下に作成され、`os-release`の内容に応じて命名されます。

---
