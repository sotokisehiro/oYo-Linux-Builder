# CHANGELOG

All notable changes to this project will be documented in this file.

## [Unreleased]

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
