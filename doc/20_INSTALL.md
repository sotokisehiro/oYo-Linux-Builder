# INSTALL.md

## 導入手順

このドキュメントでは、oYo-Builder を動かすための環境構築と依存パッケージのインストール手順を説明します。

---

### 1. システム要件

- **ホスト OS**: Debian 系 Linux（Debian GNU/Linux 12 Bullseye 以降、Ubuntu 20.04 以降推奨）  
- **CPU**: x86_64 アーキテクチャ  
- **メモリ**: 最低 4 GB (ビルド時は 2 GB 以上推奨)  
- **ディスク容量**: ビルド用ワークディレクトリに少なくとも 10 GB  
- **権限**: root 権限 または sudo 可能なユーザー

---

### 2. ホスト側依存パッケージのインストール

以下のコマンドを実行し、必要なツールをインストールします。

```bash
sudo apt update
sudo apt install -y \
  debootstrap \
  rsync \
  squashfs-tools \
  grub-pc-bin \
  grub-efi-amd64-bin \
  xorriso \
  dosfstools
```

- `debootstrap` : Debian チェルネルの初期ベースシステムを作成  
- `rsync`       : ファイルコピーに使用  
- `squashfs-tools` : squashfs 生成  
- `grub-*-bin`  : BIOS/UEFI ブートローダ生成  
- `xorriso`     : ISO イメージ作成  
- `dosfstools`  : FAT ファイルシステム作成

---

### 3. Python 仮想環境のセットアップ

プロジェクトルートで以下を実行します。

```bash
cd oYo-Builder
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

- `.venv/` 配下に 仮想環境 を作成し、依存ライブラリをインストールします。

---

### 4. 初期セットアップ

ビルド用のディレクトリを作成します。

```bash
./bin/oyo_builder.py init
```

必要に応じてオプションを指定できます。

```bash
./bin/oyo_builder.py --flavor gnome --lang ja --brand myco init
```

---

### 5. ISO のビルド

初期化後、ISO イメージをビルドします。

```bash
./bin/oyo_builder.py build
```

オプション例:

```bash
./bin/oyo_builder.py \
  --flavor gnome \
  --lang ja \
  --brand myco \
  build
```

---

### 6. クリーンアップ

ビルド後、ワークディレクトリを削除したい場合:

```bash
./bin/oyo_builder.py clean
```

---

### 7. QEMU での起動テスト

#### BIOS モード
```bash
qemu-system-x86_64 \
  -enable-kvm \
  -m 2048 \
  -machine type=pc,accel=kvm \
  -cdrom *.iso \
  -boot menu=on \
  -vga qxl \
  -serial mon:stdio
```

#### UEFI モード
```bash
mkdir -p ~/ovmf
cp /usr/share/OVMF/OVMF_VARS.fd ~/ovmf/
qemu-system-x86_64 \
  -enable-kvm \
  -m 2048 \
  -machine q35,accel=kvm \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd \
  -drive if=pflash,format=raw,file=~/ovmf/OVMF_VARS.fd \
  -cdrom *.iso \
  -boot menu=on \
  -vga qxl \
  -serial mon:stdio
```

---

以上で導入手順は完了です。詳細は README.md や各種ドキュメントをご参照ください。
