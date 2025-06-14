#!/usr/bin/env python3
"""
oYo-Builder CLI
- ISOビルドツールのエントリポイント
- Typerでサブコマンド (init, build, clean) を提供
- --flavor / --lang / --brand は環境変数で伝播
- root権限がなければ sudo で再実行
"""
import os
import sys
import pathlib
from typer import Option, Context, Exit, echo

# プロジェクトルートを sys.path に追加（lib のインポート用）
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# root権限チェック＆sudo再実行。sudoループ防止のため再帰しない
if os.geteuid() != 0:
    # 既にSUDO_USERならループ防止
    if os.environ.get("SUDO_USER"):
        echo("[ERROR] root権限が必要です。sudoで実行してください。", err=True)
        sys.exit(1)
    os.execvp("sudo", ["sudo", "-E", sys.executable] + sys.argv)

import typer
from lib.builder import initialize as cmd_init, build_iso as cmd_build, clean_work as cmd_clean

app = typer.Typer(help="oYo-Builder: ISOビルドツール")

@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    flavor: str = Option("common", "--flavor", "-f", help="デスクトップ環境(flavor)名"),
    lang:   str = Option("en",     "--lang",   "-l", help="言語設定"),
    brand:  str = Option("default","--brand",  "-b", help="ブランド名"),
    tmpfs:  bool = Option(False,   "--tmpfs/--no-tmpfs", "-t", help="work/ を tmpfs にマウントして高速ビルド"),
):
    """
    全サブコマンド共通の初期化処理
    flavor/lang/brandを環境変数にセット
    """
    os.environ["OYO_FLAVOR"] = flavor
    os.environ["OYO_LANG"]   = lang
    os.environ["OYO_BRAND"]  = brand
    if ctx.invoked_subcommand is None:
        echo(ctx.get_help())
        raise Exit()

@app.command("init")
def init():
    """初期セットアップ（ワークディレクトリ等の作成）"""
    try:
        cmd_init()
        typer.secho("初期化が完了しました。", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"[ERROR] {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command("build")
def build(
    tmpfs: bool = Option(
        False,
        "--tmpfs/--no-tmpfs",
        "-t",
        help="work/ を tmpfs にマウントして高速ビルド",
    )
):
    """ISOイメージをビルドする"""
    try:
        from lib.builder import initialize
        initialize(use_tmpfs=tmpfs)
        cmd_build()
        typer.secho("ビルドが完了しました。", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"[ERROR] {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command("clean")
def clean():
    """ワークディレクトリをクリーンアップする"""
    try:
        cmd_clean()
        typer.secho("クリーンアップが完了しました。", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"[ERROR] {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

