# CHANGELOG

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-05-08
### Added
- `--tmpfs` オプションを追加し、`work/` ディレクトリを tmpfs にマウントして高速ビルドを可能にした
- ビルド処理の高速化のため、`mmdebstrap` を導入して debootstrap を並列化
- パッケージインストールフェーズの高速化のため、`apt-fast` と `aria2` による並列ダウンロードを導入


## [0.1.0] - 2025-05-03
### Added
- 初期リリース
  - `init` / `build` / `clean` コマンド実装
  - フレーバー（Flavor）、言語（Language）、ブランド（Brand）対応
  - Overlay 機構によるファイル上書き／追加
  - Hooks 機構（pre-install / post-install スクリプト）
  - Templates 機構（Jinja2 テンプレートによる os-release, branding.desc 自動生成）
  - README, INSTALL, USAGE, CONFIGURATION, EXTENDING, CONTRIBUTING ドキュメント
  - QEMU による BIOS/UEFI 起動サポート
