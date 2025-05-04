# CONFIGURATION.md

oYo-Builder の設定ファイル／ディレクトリ構成の詳細リファレンスです。

---

## 1. packages.txt

- **役割**: chroot 内にインストールするパッケージを一覧で指定  
- **場所**: 各レイヤーのルート（例: `config/10_common/packages.txt`, `config/20_gnome/packages.txt` など）  
- **書式**:
  - 1 行に 1 パッケージ名  
  - 空行や `#` で始まる行は無視  
  - マージ順はレイヤーのプレフィックス順  
- **例**:
  ```text
  # 基本パッケージ
  sudo
  debootstrap

  # GNOME フレーバー固有
  gnome-session
  gnome-shell
  ```

---

## 2. Overlay フォルダ

- **役割**: chroot のファイルシステム上に直接ファイルを上書き／追加  
- **場所**: 各レイヤーの `overlay/` 以下に配置  
- **動作**:
  - `overlay/` 内を丸ごと `sudo cp -a overlay/. chroot/` でコピー  
  - 既存ファイルは上書き、ディレクトリはマージ  
  - `/etc`, `/usr`, `/usr/share` など、chroot 上の任意パスに対応  
- **例**:
  ```
  config/20_gnome/overlay/usr/share/backgrounds/custom/background.png
  config/40_brand/myco/overlay/etc/dconf/db/local.d/00-brand-settings
  ```

---

## 3. Hooks 機構

- **用途**: パッケージインストールの前後やその他のタイミングで任意のコマンドを chroot 内で実行  
- **ディレクトリ**:
  ```
  config/<layer>/hooks/pre-install.d/
  config/<layer>/hooks/post-install.d/
  ```
- **実行タイミング**:
  - `pre-install.d`: `apt install` の直前  
  - `post-install.d`: `apt install` の直後  
- **ファイル名**:
  - プレフィックス数字順 (`10-`, `20-` など) でソート実行  
  - 拡張子 `.sh` の実行可能スクリプトのみ対象  
- **動作**:
  1. ホスト側から `chroot/tmp/` にコピー  
  2. `chroot sh /tmp/<script>.sh` を実行  
- **例**:
  ```bash
  # config/common/hooks/post-install.d/10-flatpak.sh
  #!/bin/sh
  set -e
  apt-get update
  apt-get install -y ca-certificates flatpak
  flatpak remote-add --if-not-exists flathub     https://dl.flathub.org/repo/flathub.flatpakrepo
  ```

---

## 4. Templates 機構

- **用途**: Jinja2 テンプレートと YAML から設定ファイルを生成  
- **ディレクトリ**:
  ```
  config/40_brand/<brand>/templates/
  ```
- **必須ファイル**:
  - `brand.yml`: テンプレートで使う変数定義（名前、バージョン、ロゴファイル名など）  
  - `<whatever>.j2`: Jinja2 テンプレートファイル  
- **対応例**:
  - `os-release.conf.j2` → chroot `/etc/os-release`  
  - `branding.desc.j2` → chroot `/etc/calamares/branding/<brand>/branding.desc`  
  - `grub.cfg.j2` → ISO ブートメニュー用 `boot/grub/grub.cfg`  
- **変数例 (`brand.yml`)**:
  ```yaml
  name: "MyCo Linux"
  pretty_name: "MyCo Linux 1.0"
  version_id: "1.0"
  logo: "myco-logo.png"
  ```
- **動作**:
  1. `_apply_os_release()` や `_apply_calamares_branding()` でテンプレートを検出  
  2. `jinja2.Environment` でレンダリング  
  3. `CHROOT` 配下の所定パスに書き込む  
- **例** (`os-release.conf.j2`):
  ```jinja
  PRETTY_NAME="{{ pretty_name }}"
  NAME="{{ name }}"
  VERSION_ID="{{ version_id }}"
  ID={{ name|lower }}
  ```

---

*詳しい使い方は `USAGE.md` も併せて参照してください。*
