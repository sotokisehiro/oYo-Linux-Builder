# INSTALL.md

## 導入手順

このドキュメントでは、oYo-Builder を動かすための環境構築と依存パッケージのインストール手順を説明します。

---

### 1. システム要件

- **ホスト OS**: Debian系Linux（Debian GNU/Linux 12 Bookworm 以降、open.Yellow.os Freesia 以降推奨）  
- **CPU**: x86_64 アーキテクチャ  
- **メモリ**: 最低 4 GB（ビルド時は8 GB以上推奨、--tmpfs使用時はさらに多いと快適）  
- **ディスク容量**: ビルド用ワークディレクトリに少なくとも 10 GB  
- **権限**: root権限 または sudo 可能なユーザー

---

### 2. ホスト側依存パッケージのインストール

以下のコマンドを実行し、必要なツールをインストールします。

```bash
sudo apt update
sudo apt install -y   mmdebstrap   rsync   squashfs-tools   grub-pc-bin   grub-efi-amd64-bin   grub-efi-amd64-signed   shim-signed   xorriso   dosfstools   mtools   python3-venv   python3-pip   git
```

- `mmdebstrap`: Debianベースシステムの展開（高速でapt互換。debootstrapの上位互換）
- `rsync`: ファイルコピー用
- `squashfs-tools`: squashfsイメージ生成
- `grub-pc-bin`, `grub-efi-amd64-bin`: BIOS/UEFIブートローダー生成
- `grub-efi-amd64-signed`, `shim-signed`: Secure Boot対応ISO作成に必須
- `xorriso`: ISOイメージ作成
- `dosfstools`, `mtools`: EFIブート用FATイメージ作成などに利用
- `python3-venv`, `python3-pip`, `git`: Python仮想環境と依存管理

---

### 3. Python 仮想環境のセットアップ

プロジェクトルートで以下を実行します。

```bash
cd oYo-Linux-Builder
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

- `.venv/` 配下に仮想環境を作成し、Python依存ライブラリをインストールします。

---

### 4. 初期セットアップ

ビルド用ディレクトリ等の初期化を行います。

```bash
./bin/oyo_builder.py init
```

必要に応じてオプションを指定できます。

```bash
./bin/oyo_builder.py --flavor gnome --lang ja --brand myco init
```

---

### 5. ISO のビルド

初期化後、ISOイメージをビルドします。

```bash
./bin/oyo_builder.py build
```

オプション例:

```bash
./bin/oyo_builder.py   --flavor gnome   --lang ja   --brand Sample-gnome   build
```

- RAMディスク（tmpfs）を使いたい場合は `--tmpfs` を追加してください（十分なメモリが必要）。
  ```bash
  ./bin/oyo_builder.py --flavor gnome --lang ja --brand Sample-gnome build --tmpfs
  ```

---

### 6. クリーンアップ

ビルド後、作業ディレクトリを削除したい場合:

```bash
./bin/oyo_builder.py clean
```

---

### 7. QEMU での起動テスト

#### BIOS モード
```bash
qemu-system-x86_64   -enable-kvm   -m 2048   -machine type=pc,accel=kvm   -cdrom openyellowos-1.0-ja.iso   -boot menu=on   -vga qxl   -serial mon:stdio
```

#### UEFI モード
```bash
mkdir -p "$HOME/ovmf"
cp /usr/share/OVMF/OVMF_VARS.fd "$HOME/ovmf/OVMF_VARS.fd"

qemu-system-x86_64   -enable-kvm   -m 2048   -machine q35,accel=kvm   -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd   -drive if=pflash,format=raw,file="$HOME/ovmf/OVMF_VARS.fd"   -cdrom openyellowos-1.0-ja.iso   -boot menu=on   -vga qxl   -serial mon:stdio
```
> ファイル名例は `openyellowos-1.0-ja.iso` など、実際の出力に合わせて指定してください。

---

### 8. ビルド成果物

- 完成したISOイメージは**プロジェクトルート直下**に `os名-バージョン-言語.iso` 形式で出力されます。
  - 例: `openyellowos-1.0-ja.iso`
- 作業用ファイルは `work/iso` 配下にも保存されます。


---

> 詳細は [README.md](../README.md) や [doc/30_USAGE.md](./30_USAGE.md) をご参照ください。

