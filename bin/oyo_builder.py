#!/usr/bin/env python3
import os
import sys
import pathlib
from typer import Option, Context, Exit, echo

# ——— プロジェクトルートを sys.path に挿入 ———
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
# 非 root なら一度だけ sudo で再実行（venv の Python を使う）
if os.geteuid() != 0:
    os.execvp("sudo", ["sudo", "-E", sys.executable] + sys.argv)

import typer
from typer import Option, Context, Exit
from lib.builder import initialize as cmd_init, build_iso as cmd_build, clean_work as cmd_clean

# ——— 単一の Typer インスタンスを使い回す ———
app = typer.Typer(help="oYo-Builder: ISOビルドツール")

@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    flavor: str = Option("common", "--flavor", "-f"),
    lang:   str = Option("en",     "--lang",   "-l"),
    brand:  str = Option("default","--brand","-b"),
):
    # 環境変数にセットしてから各コマンド起動
    os.environ["OYO_FLAVOR"] = flavor
    os.environ["OYO_LANG"]    = lang
    os.environ["OYO_BRAND"]  = brand
    if ctx.invoked_subcommand is None:
        echo(ctx.get_help())
        raise Exit()


@app.command("init")
def init():
    """初期セットアップを行う"""
    try:
        cmd_init()
        typer.secho("初期化が完了しました。", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"[ERROR] {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command("build")
def build():
    """ISOイメージをビルドする"""
    try:
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
