# CHANGELOG

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-06-13
### Added
- テンプレート機構の拡張（grub.cfg, plymouthテーマなど）
- ドキュメントの最新化・詳細化（README/INSTALL/USAGEなど）
### Changed
- コードの構造・コメントを整理し、保守性を向上
- 必要な依存パッケージリストの見直し
### Fixed
- 一部overlay適用時の権限エラー対策
- クリーンアップ処理の堅牢化

---

## [0.2.0] - 2025-05-08
### Added
- `--tmpfs` オプションを追加し、`work/` ディレクトリを tmpfs にマウントして高速ビルドを可能にした
- ビルド処理の高速化のため、`mmdebstrap` を導入して debootstrap を並列化
- パッケージインストールフェーズの高速化のため、`apt-fast` と `aria2` による並列ダウンロードを導入

---

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
