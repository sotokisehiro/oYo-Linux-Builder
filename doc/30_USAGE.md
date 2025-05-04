# USAGE.md

## コマンド一覧

oYo-Builder には主に以下のコマンドがあります:

| コマンド      | 説明                                   |
|--------------|----------------------------------------|
| `init`       | ビルド用の `work/` と `log/` ディレクトリを作成 |
| `build`      | ISO イメージをビルド                    |
| `clean`      | `work/` ディレクトリをクリーンアップ     |

全コマンド共通で `--help` を付けると詳細が表示されます:

```bash
./bin/oyo_builder.py --help
./bin/oyo_builder.py init --help
```

---

## オプション一覧

| オプション            | 説明                                             | デフォルト    |
|-----------------------|--------------------------------------------------|--------------|
| `-f`, `--flavor`      | デスクトップ環境を指定 (common, gnome, xfce, kde など) | `common`     |
| `-l`, `--lang`        | 言語を指定 (ja, en)                              | `en`         |
| `-b`, `--brand`       | ブランド名を指定 (default, myco など)            | `default`    |

### 例

- GNOME 日本語版をビルド:
  ```bash
  ./bin/oyo_builder.py -f gnome -l ja build
  ```
- Xfce 英語版 デフォルトブランド:
  ```bash
  ./bin/oyo_builder.py --flavor xfce --lang en --brand default build
  ```

---

## ディレクトリ構成（config）

`config/` 配下はレイヤーごとに分かれています:

```
config/
├── 10_common/            # 共通設定
│   ├ overlay/
│   └ packages.txt
├── 20_gnome/             # フレーバー: GNOME
│   ├ overlay/
│   └ packages.txt
├── 30_lang/
│   ├ ja/                # 言語: 日本語
│   │   ├ overlay/
│   │   └ packages.txt
│   └ en/                # 言語: 英語
│       ├ overlay/
│       └ packages.txt
└── 40_brand/
    ├ default/           # ブランド: default
    │   ├ overlay/
    │   └ packages.txt
    └ myco/              # ブランド: myco
        ├ overlay/
        └ packages.txt
```

- **Overlay** フォルダ: chroot 上のファイルをそのまま上書き  
- **packages.txt**: インストールするパッケージ一覧を記載  
- レイヤーは `10_`, `20_`, `30_`, `40_` のプレフィックス順にマージされます

---

## フック機構（hooks）

特定のタイミングで任意スクリプトを実行可能:

- `config/.../hooks/pre-install.d/` : パッケージインストール前
- `config/.../hooks/post-install.d/` : パッケージインストール後

ファイル名の数字順に実行されます:
```
config/common/hooks/post-install.d/10-flatpak.sh
config/gnome/hooks/post-install.d/20-some.sh
```

---

## テンプレート機構（templates）

Jinja2 テンプレートを使って設定ファイルを生成:

```
config/brand/<brand>/templates/
├── os-release.conf.j2
└── branding.desc.j2
```

- `brand.yml` で変数を定義し、テンプレートでレンダリング  
- 生成先は `chroot/etc/os-release` や `chroot/etc/calamares/branding/...`

---

詳細な設定方法は `CONFIGURATION.md` をご覧ください。
