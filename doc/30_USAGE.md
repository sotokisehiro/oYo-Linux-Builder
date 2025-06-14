# USAGE.md

## コマンド一覧と主なオプション

oYo-Builder には主に以下のコマンドがあります:

| コマンド      | 説明                                     |
|--------------|------------------------------------------|
| `init`       | ビルド用の `work/` と `log/` ディレクトリを作成 |
| `build`      | ISO イメージをビルド                      |
| `clean`      | `work/` ディレクトリをクリーンアップ       |

### 主なオプション

| オプション        | 説明                                              |
|-------------------|---------------------------------------------------|
| `--flavor`, `-f`  | デスクトップ環境の指定（例: gnome, xfce, kde）   |
| `--lang`, `-l`    | 言語リソースの指定（例: ja, en）                 |
| `--brand`, `-b`   | ブランド（テーマ・壁紙セットなど）の指定          |
| `--tmpfs`, `-t`   | workディレクトリをtmpfs(RAMディスク)にマウント    |
| `--help`          | コマンドラインヘルプを表示                        |

全コマンド共通で `--help` を付けると詳細が表示されます:

```bash
./bin/oyo_builder.py --help
```

---

## 実行例

```bash
./bin/oyo_builder.py --flavor gnome --lang ja --brand Sample-gnome build --tmpfs
```

---

## build コマンドの詳細

- `--tmpfs`, `-t`: `work/` ディレクトリを `tmpfs` にマウントしてビルドを行います。メモリ上に一時領域を確保するため、ディスク I/O を削減し処理速度が向上します。指定しない場合はディスク上でビルドします。

---

## Jinja2 テンプレート利用方法

Jinja2テンプレートとYAML変数で設定ファイルを動的生成できます。

```bash
# テンプレート配置例
templates/
├── os-release.conf.j2
├── branding.desc.j2
├── grub.cfg.j2
├── plymouth-theme.conf.j2
```

- 変数は `brand.yml` などにYAML形式で記述し、テンプレートで参照されます。
- 主な生成先例:  
    - `chroot/etc/os-release`  
    - `chroot/etc/calamares/branding/<brand>/branding.desc`  
    - `ISO/boot/grub/grub.cfg`  
    - `chroot/usr/share/plymouth/themes/<theme>/theme`  

テンプレート変数の例：
```yaml
# brand.yml
name: "openYellow"
version: "1.0"
theme: "custom"
background: "/usr/share/backgrounds/mywall.png"
```
テンプレート内では `{{ name }}` のように参照します。

---

## よくあるエラー・ヒント

- テンプレート展開時にファイルが生成されない場合は、brand.ymlやテンプレート名のスペル・パスを再確認してください。
- 必須コマンド（mmdebstrap等）が見つからない場合は `apt install` を再度確認してください。

---

詳細な設定方法やカスタマイズは [CONFIGURATION.md](./40_CONFIGURATION.md) をご覧ください。
