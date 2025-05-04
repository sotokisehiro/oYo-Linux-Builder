# EXTENDING.md

oYo-Builder の拡張ガイドです。  
新しいフレーバーやブランド、Hook、CI/CD 連携などの手順をまとめています。

---

## 1. 新しいフレーバー（Flavor）の追加

1. **ディレクトリ作成**  
   `config/` 配下に数字付きプレフィックスを用いて新フォルダを作成します（例: `25_xfce`）。  
   ```
   config/
   ├ 10_common/
   ├ 20_gnome/
   ├ 25_xfce/       ← 追加
   └ 30_lang/
   ```
2. **設定ファイル配置**  
   - `config/25_xfce/packages.txt` に XFCE 用パッケージを記載  
   - `config/25_xfce/overlay/` に XFCE 固有の設定ファイルやテーマを置く  
3. **テスト**  
   ```bash
   ./bin/oyo_builder.py -f xfce -l en build
   ```
4. **QEMU 起動**  
   上記に加えて `--brand`/`--lang` を指定して検証します。

---

## 2. 新しいブランド（Brand）の追加

1. **ディレクトリ作成**  
   `config/40_brand/` 配下にブランド名でサブディレクトリを追加（例: `myco`）。  
2. **Overlay と Templates**  
   - `config/40_brand/myco/overlay/`: 壁紙、アイコン、Plymouth テーマなど  
   - `config/40_brand/myco/templates/`: `brand.yml` と `.j2` テンプレート  
3. **テスト**  
   ```bash
   ./bin/oyo_builder.py -f gnome -l ja -b myco build
   ```

---

## 3. Hook スクリプトの追加

- **カテゴリ**  
  - `hooks/pre-install.d/` : パッケージインストール前  
  - `hooks/post-install.d/`: パッケージインストール後  

1. **シェルスクリプト作成**  
   ```bash
   #!/bin/sh
   set -e
   # 任意コマンド
   echo "Running custom hook!"
   ```
2. **配置場所**  
   - `config/10_common/hooks/post-install.d/10-custom.sh`  
   - 他レイヤーでも同様に配置可能  
3. **実行確認**  
   ビルドログに `→ hook: executing 10-custom.sh in chroot` が表示されれば成功

---

## 4. CI/CD 連携例

### GitHub Actions

```yaml
name: Build ISO

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y debootstrap rsync squashfs-tools grub-pc-bin grub-efi-amd64-bin xorriso dosfstools
    - name: Setup venv
      run: |
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
    - name: Build ISO
      run: |
        ./bin/oyo_builder.py -f gnome -l en -b default build
    - name: Upload ISO
      uses: actions/upload-artifact@v3
      with:
        name: iso
        path: *.iso
```

---

## 5. トラブルシューティング

- **パッケージ不足エラー**  
  - `Command '['chroot' ...] returned non-zero exit status` → `packages.txt` に必要なパッケージを追加  
- **Overlay が反映されない**  
  - ディレクトリ構成やプレフィックス順を再確認  
- **Hook が実行されない**  
  - スクリプトに実行権 (`chmod +x`) があるか  
  - `hooks/…` のパスが正しいか  
- **ISO が起動しない**  
  - `grub.cfg` のパス設定（`set root=(cd)` vs `(cd0)`）  
  - `vmlinuz`/`initrd.img` が正しいか

---

上記を参考に、独自要件の追加やパイプラインへの組み込みを行ってください。
