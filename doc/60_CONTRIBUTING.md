# CONTRIBUTING.md

oYo-Builder へのコントリビューション方法についてまとめています。  
バグ報告、機能追加、ドキュメント改善など大歓迎です。

---

## 1. Issue の報告

1. **バグ報告**  
   - 最初に既存の [Issues](https://github.com/openyellowos/oYo-Builder/issues) を検索  
   - 同様の報告がなければ、新規 Issue を作成  
   - **必須情報**:
     - oYo-Builder のバージョン  
     - 実行環境（OS、Python バージョンなど）  
     - 再現手順と期待される結果  
     - 実際のエラーメッセージやログ（可能であればログファイルを添付）

2. **機能追加リクエスト**  
   - 必要な機能の概要と利用ケースを明確に説明  
   - 可能であれば設計アイデアやコマンド例を記載

---

## 2. 開発フロー

1. **リポジトリをフォーク**  
   GitHub 上で「Fork」ボタンをクリック。

2. **ローカルにクローン**  
   ```bash
   git clone https://github.com/<your-username>/oYo-Builder.git
   cd oYo-Builder
   ```

3. **ブランチ作成**  
   ```bash
   git checkout -b feature/awesome-new-feature
   ```

4. **コードを実装・テスト**  
   - Python の仮想環境（`.venv`）を使って依存関係を再現  
   - `./bin/oyo_builder.py` の実行や QEMU テストで動作確認  
   - 必要に応じてユニットテスト／シナリオテストを追加

5. **コミット**  
   - **コミットメッセージ**は以下の形式を推奨  
     ```
     feat(init): add support for new <feature>
     fix(build): correct hook execution order
     docs: update README and INSTALL
     ```
   - `feat`, `fix`, `docs`, `chore` などをプレフィックスに使うと可読性が上がります。

6. **プルリクエスト (PR) の作成**  
   - フォーク先で「Compare & pull request」をクリック  
   - タイトルと説明を丁寧に記載  
   - コードの概要、動作確認手順、影響範囲を明記

---

## 3. コードスタイル

- **フォーマット**: [Black](https://github.com/psf/black)  
  ```bash
  pip install black
  black .
  ```
- **インポート順**: [isort](https://github.com/PyCQA/isort)  
  ```bash
  pip install isort
  isort .
  ```
- **静的解析**: [flake8](https://github.com/pycqa/flake8)  
  ```bash
  pip install flake8
  flake8 lib bin
  ```

---

## 4. テスト

- **ユニットテスト**: `tests/` ディレクトリに配置  
- **実行方法**: `pytest` を推奨  
  ```bash
  pip install pytest
  pytest
  ```
- カバレッジツール（coverage.py）なども併用可能

---

## 5. プルリクエスト後

- **CI のチェック**: GitHub Actions で自動ビルド・テストが走ります  
- **レビュー対応**: コメントに返信し、必要に応じて修正  
- **マージ**: レビュー完了後、main ブランチにマージされます

---

## 6. ドキュメント改善

- ドキュメントは `*.md` 形式でリポジトリ直下に配置  
- サンプルやスクリーンショットを追加するとわかりやすくなります

---

ご協力ありがとうございます！🎉  
oYo-Builder をより良いツールにしていきましょう！  
