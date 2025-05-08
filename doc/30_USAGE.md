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
...
```

---

## build コマンドの詳細

`build` コマンドには高速化オプションとして `--tmpfs` (`-t`) が利用できます。

- `--tmpfs`, `-t`: `work/` ディレクトリを `tmpfs` にマウントしてビルドを行います。メモリ上に一時領域を確保するため、ディスク I/O を削減し処理速度が向上します。指定しない場合は従来通りディスク上に作成されます。

---

Jinja2 テンプレートを使って設定ファイルを生成:

```bash
# テンプレート配置例
templates/
├── os-release.conf.j2
└── branding.desc.j2
```

- `brand.yml` で変数を定義し、テンプレートでレンダリング  
- 生成先は `chroot/etc/os-release` や `chroot/etc/calamares/branding/...`

詳細な設定方法は `CONFIGURATION.md` をご覧ください。
