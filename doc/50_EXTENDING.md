# EXTENDING.md

oYo-Builder の拡張ガイドです。  
新しいフレーバーやブランド、Hook、CI/CD連携などの手順をまとめています。

---

## 1. 新しいフレーバー（Flavor）の追加

1. **ディレクトリ作成**  
   `config/` 配下に数字付きプレフィックスで新フォルダを作成（例: `20_gnome`、`21_kde`など）。
   ```
   config/
   ├ 10_common/
   ├ 20_gnome/
   ├ 21_kde/
   └ 30_lang/
   ```
2. **設定ファイル配置**  
   - `config/20_gnome/packages.txt` … GNOME用パッケージリスト
   - `config/20_gnome/overlay/` … GNOME専用の設定やテーマ
3. **テスト**  
   ```bash
   ./bin/oyo_builder.py --flavor gnome --lang en build
   ```
4. **QEMUで起動テスト**  
   `--brand`や`--lang`も指定して動作確認

---

## 2. 新しいブランド（Brand）の追加

1. **ディレクトリ作成**  
   `config/40_brand/` 配下にブランド名でディレクトリ作成（例: `myco`）。
2. **OverlayとTemplates**  
   - `config/40_brand/myco/overlay/` … 壁紙、アイコン、plymouthテーマ等
   - `config/40_brand/myco/templates/` … `brand.yml`や`branding.desc.j2`、`grub.cfg.j2`、`plymouth-theme.conf.j2`など
3. **テスト**  
   ```bash
   ./bin/oyo_builder.py --flavor gnome --lang ja --brand myco build
   ```

---

## 3. Hookスクリプトの追加

- **カテゴリ**  
  - `hooks/pre-install.d/` … mmdebstrapによるベース展開前に実行
  - `hooks/post-install.d/` … ベース展開・overlay・ユーザー作成後に実行

1. **シェルスクリプト作成**  
   ```bash
   #!/bin/sh
   set -e
   # 任意のカスタム処理
   echo "Running custom hook!"
   ```
2. **配置場所**  
   - `config/10_common/hooks/post-install.d/10-custom.sh`  
   - 他レイヤーにも設置可能（プレフィックス番号順で複数実行）
3. **実行確認**  
   ビルドログに `→ hook: executing 10-custom.sh in chroot` が出ていれば成功

---

## 4. CI/CD連携例

### GitHub Actions（例）

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
        sudo apt install -y mmdebstrap rsync squashfs-tools grub-pc-bin grub-efi-amd64-bin grub-efi-amd64-signed shim-signed xorriso dosfstools mtools python3-venv python3-pip
    - name: Setup venv
      run: |
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
    - name: Build ISO
      run: |
        ./bin/oyo_builder.py --flavor gnome --lang en --brand default build
    - name: Upload ISO
      uses: actions/upload-artifact@v3
      with:
        name: iso
        path: "*.iso"
```
> 必要に応じて各自のブランドやフレーバー名、ビルドオプションを編集してください。

---

## 5. トラブルシューティング

- **パッケージ不足エラー**  
  - `Command '['chroot' ...] returned non-zero exit status` → `packages.txt` に必要なパッケージを追加
- **Overlayが反映されない**  
  - ディレクトリ名・構成・数字プレフィックス順を確認
- **Hookが実行されない**  
  - 実行権（chmod +x）があるか、パスが正しいか
- **ISOが起動しない／Secure Bootで失敗**  
  - grub.cfgやEFIファイルのパス・shim, grubx64.efi.signed, mmx64.efiの有無を確認
  - Secure Bootエラー時は `grub-efi-amd64-signed`/`shim-signed` の導入・テンプレ展開を見直す

---

> 詳細なカスタマイズや設計は [CONFIGURATION.md](./40_CONFIGURATION_latest.md) も参照してください。

---

上記を参考に、独自要件の追加やパイプラインへの組み込みを行ってください。
