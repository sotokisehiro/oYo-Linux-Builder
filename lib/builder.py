#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path
import logging
import datetime
import re
import yaml
from jinja2 import Environment, FileSystemLoader
import typer
import atexit

# --- 定数 ---
ROOT     = Path(__file__).resolve().parent.parent
CFG_BASE = ROOT / "config"
WORK     = ROOT / "work"
CHROOT   = WORK / "chroot"
ISO      = WORK / "iso"
LOG_DIR  = ROOT / "log"

# workディレクトリをtmpfs（RAMディスク）にマウントする際の容量
# 環境変数OYO_TMPFS_SIZEで変更可能（例: "8G", "16G", "80%"）。デフォルトは8G。
TMPFS_SIZE = os.getenv("OYO_TMPFS_SIZE", "8G")

# --- ビルドに必要な外部コマンド ---
REQUIRED_COMMANDS = [
    "sudo",
    "mmdebstrap",
    "grub-mkrescue",
    "mksquashfs",
    "cp",
    "mount",
    "umount",
    "rsync",
    "apt-cache",
    "chroot",
    "rm",
    "ln",
    "useradd",
    "sh",
    "chpasswd",
    "mountpoint",
]

# 今回ビルドごとにタイムスタンプ付きログファイルを作成
LOG_DIR.mkdir(parents=True, exist_ok=True) 
ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
LOG_FILE = LOG_DIR / f"build_{ts}.log"

# debootstrap などが /usr/sbin/ に入っている場合があるので、
# チェックを行う前に sbin を PATH に含める
os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + "/usr/sbin"

# アンマウント対象を記録するリスト
_MOUNTS: list[Path] = []

def _register_unmount(path: Path):
    """
    ビルド中にmountしたディレクトリを記録する。
    プログラム終了時やクリーンアップ時にアンマウント対象として利用する。
    """
    if path not in _MOUNTS:
        _MOUNTS.append(path)

def _cleanup_mounts():
    """
    _register_unmountで登録した全ディレクトリをアンマウントする。
    プログラム終了時に必ず呼ばれ、マウントしっぱなしのリソースを残さないようにする。
    """
    for m in reversed(_MOUNTS):
        subprocess.run(
            ["sudo", "umount", "-l", str(m)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

# プログラム終了時に必ず呼ぶ
atexit.register(_cleanup_mounts)

def _mount_tmpfs(path: Path):
    """
    指定パスにtmpfsをマウントする。ISOビルドの高速化のため一時ワークをRAM上に配置したい場合に利用。
    """
    _run(["sudo", "mount", "-t", "tmpfs",
          "-o", f"size={TMPFS_SIZE},mode=0755", "tmpfs", str(path)])
    print(f"Mounted tmpfs ({TMPFS_SIZE}) on {path}")
    _register_unmount(path)

def get_configs() -> list[Path]:
    """
    各種設定レイヤー（common, flavor, lang, brand）を自動検出し、適用順に返す。
    ビルドやoverlay適用時にどの設定を参照すべきかを動的に決めるための関数。
    """
    flavor = os.getenv("OYO_FLAVOR", "common")
    lang   = os.getenv("OYO_LANG",    "en")
    brand  = os.getenv("OYO_BRAND",   "default")

    configs: list[Path] = []
    for grp in sorted(CFG_BASE.iterdir()):
        if not grp.is_dir() or "_" not in grp.name:
            continue
        # ディレクトリ名を "NN_key" に分割
        _num, key = grp.name.split("_", 1)

        # common レイヤー
        if key == "common":
            configs.append(grp)

        # flavor レイヤー（config/NN_flavor/<flavor> を探す）
        elif key == "flavor":
            sub = grp / flavor
            if sub.is_dir():
                configs.append(sub)

        # lang レイヤー（サブディレクトリ ja|en があるはず）
        elif key == "lang":
            sub = grp / lang
            if sub.is_dir():
                configs.append(sub)

        # brand レイヤー（サブディレクトリ default|myco があるはず）
        elif key == "brand":
            sub = grp / brand
            if sub.is_dir():
                configs.append(sub)

    return configs

def get_hook_configs() -> list[Path]:
    """
    pre-install/post-install用のhooks対象レイヤーを取得。
    フック実行時にどのhooksディレクトリを順番に見るかを決める。
    """
    flavor = os.getenv("OYO_FLAVOR", "common")
    lang   = os.getenv("OYO_LANG",    "en")
    brand  = os.getenv("OYO_BRAND",   "default")

    configs: list[Path] = []
    for grp in sorted(CFG_BASE.iterdir()):
        if not grp.is_dir() or "_" not in grp.name:
            continue
        _num, key = grp.name.split("_", 1)

        # 共通処理：各レイヤーの該当サブディレクトリを追加
        if key == "common":
            configs.append(grp)
        elif key == "flavor":
            sub = grp / flavor
            if sub.is_dir():
                configs.append(sub)
        elif key == "lang":
            sub = grp / lang
            if sub.is_dir():
                configs.append(sub)
        elif key == "brand":
            sub = grp / brand
            if sub.is_dir():
                configs.append(sub)

    return configs
    
def _run_hooks(stage: str):
    """
    指定ステージ（pre-install, post-install）に応じた全フックシェルスクリプトをchroot内で順次実行する。
    各レイヤーの拡張処理・追加カスタマイズを一括実行するための仕組み。
    """
    all_scripts = []

    for cfg in get_hook_configs():
        hooks_dir = cfg / "hooks" / f"{stage}.d"
        if hooks_dir.is_dir():
            for script in hooks_dir.glob("*.sh"):
                if script.is_file():
                    all_scripts.append(script)

    # ファイル名でソート（フルパスではなくファイル名で）
    all_scripts.sort(key=lambda p: p.name)

    if not all_scripts:
        print(f"[INFO] No hook scripts found for stage: {stage}")
        return

    tmpdir = CHROOT / "tmp"
    tmpdir.mkdir(parents=True, exist_ok=True)

    for script in all_scripts:
        dest = tmpdir / script.name
        print(f"→ hook: copying {script} to {dest}")
        _run(["sudo", "cp", str(script), str(dest)])

    for script in all_scripts:
        print(f"→ hook: executing {script.name} in chroot")
        _run([
            "sudo", "chroot", str(CHROOT),
            "sh", f"/tmp/{script.name}"
        ])
    
def _render_brand_template(template_name: str, dest: Path, context: dict):
    """
    ブランドごとのJinja2テンプレートをレンダリングし、chroot内の所定パスに書き込む。
    各種branding・設定ファイルを柔軟に差し替えるために使う。
    """
    brand = os.getenv("OYO_BRAND", "default")
    brand_layer = find_brand_layer()
    
    if not brand_layer:
        raise FileNotFoundError("config 配下に *_brand ディレクトリが見つかりません")
    tpl_dir = brand_layer / brand / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    tpl = env.get_template(template_name)
    rendered = tpl.render(**context)

    target = CHROOT / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered)
    print(f"Rendered {template_name} → {target}")

def _check_host_dependencies():
    """
    ビルドに必要な外部コマンドが揃っているか事前に検査する。
    未導入の場合はエラーで強制終了し、途中ビルド失敗を防ぐ。
    """
    missing = []
    for cmd in REQUIRED_COMMANDS:
        if shutil.which(cmd) is None:
            missing.append(cmd)
    if missing:
        print(f"[ERROR] 以下のコマンドが見つかりません: {', '.join(missing)}")
        print("ビルドを続行するには、これらをインストールしてください。")
        sys.exit(1)



# logging の設定：ファイルとコンソールの両方に出力
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def initialize(use_tmpfs: bool = False):
    """
    work/logディレクトリの初期化、ホスト依存コマンドの検査を行う。
    tmpfs利用時は作業ディレクトリをRAM上にマウントする。
    ビルド開始前の環境セットアップに必須。
    """
    # ホスト依存チェック
    _check_host_dependencies()

    # ディレクトリ作成
    for d in (WORK, ISO, CHROOT, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)
    print(f"Created directories: {WORK}, {ISO}, {CHROOT}, {LOG_DIR}")

    # フラグが True のときだけ tmpfs をマウント
    if use_tmpfs:
        _mount_tmpfs(WORK)
        print("tmpfs created")

# スクリプトが root で実行中か
IS_ROOT = (os.geteuid() == 0)

def _run(cmd, **kwargs):
    """
    外部コマンドを安全に実行し、ログ記録・root時のsudo除去などのラッパーも兼ねる。
    失敗時は例外送出してビルド全体の異常終了を管理する。
    """
    # root なら sudo を外す
    if IS_ROOT and cmd and cmd[0] == "sudo":
        cmd = cmd[1:]
    logger.info(">> %s", " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **kwargs
    )
    for line in proc.stdout:
        logger.info(line.rstrip())
    proc.wait()
    if proc.returncode != 0:
        logger.error(f"コマンド失敗: {' '.join(cmd)}\nリターンコード: {proc.returncode}")
        raise subprocess.CalledProcessError(proc.returncode, cmd)


def _get_codename_from_os_release() -> str:
    """common→flavor の順で os-release を探し、VERSION_CODENAME を返す"""
    # 1) os-release ファイルを検索
    for cfg in get_configs():
        src = cfg / "os-release"
        if src.exists():
            break
    else:
        paths = ", ".join(str(p / "os-release") for p in get_configs())
        raise FileNotFoundError(
            f"以下のいずれにも os-release が見つかりません:\n  {paths}\n"
            "config/common/os-release をご確認ください。"
        )

    # 2) 中身をパースして VERSION_CODENAME を探す
    for line in src.read_text().splitlines():
        if line.startswith("VERSION_CODENAME="):
            codename = line.split("=",1)[1].strip().strip('"')
            if codename:
                return codename
    raise RuntimeError(
        f"{src} に VERSION_CODENAME が見つかりません。\n"
        "例：VERSION_CODENAME=bookworm\n"
        "を追記してください。"
    )
    
def _get_iso_filename() -> str:
    """
    templates/os-release.conf.j2 から生成された
    **{CHROOT}/etc/os-release** を最優先に参照し、  
    ISO ファイル名を決定する。
    ─ 優先度 ─
        1.  {CHROOT}/etc/os-release   (テンプレート済み)
        2.  従来の config/common → flavor → … の os-release
    """
    # --- 1) chroot 側を最優先 ---
    chroot_osr = CHROOT / "etc/os-release"
    if chroot_osr.exists():
        src = chroot_osr
    else:
        # --- 2) 旧来ロジックへのフォールバック ---
        src = None
        for cfg in get_configs():
            cand = cfg / "os-release"
            if cand.exists():
                src = cand
                break
        if src is None:
            paths = "\n  ".join(str(p / 'os-release') for p in get_configs())
            raise FileNotFoundError(
                "以下のいずれにも os-release が見つかりません:\n"
                f"  {paths}\n"
                "テンプレートまたは config/common/os-release を確認してください。"
            )

    # --- 3) os-release をパース ---
    info: dict[str,str] = {}
    for line in src.read_text().splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split("=", 1)
        info[k] = v.strip().strip('"')

    name    = info.get("NAME", "os").lower()
    version = info.get("VERSION_ID", "")
    base    = f"{name}-{version}" if version else name
    # 不正文字をハイフンに置換
    safe    = re.sub(r'[^A-Za-z0-9._-]+', '-', base)
    # 環境変数 OYO_LANG から言語コードを取得（デフォルト en）
    lang    = os.getenv("OYO_LANG", "en")
    # 最終的なファイル名に言語コードを追加
    return f"{safe}-{lang}.iso"

def _prepare_chroot(codename: str):
    """
    chroot環境を初期化し、mmdebstrapでベースシステムと追加パッケージ群を展開する。
    古いchrootは安全にクリーンアップし直す。
    """

    # 古い chroot をまるごと削除
    if CHROOT.exists():
        # ─── 念のため残存マウントをアンマウント ───
        for m in ("dev/pts", "dev/shm", "dev/mqueue", "dev/hugepages",
                  "dev", "sys", "proc", "run"):
            target = CHROOT / m
            if target.exists():
                # lazy unmount でリソースビジーを回避
                subprocess.run(
                    ["sudo", "umount", "-l", str(target)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        # すべてアンマウントしたあとにディレクトリ削除
        _run(["sudo", "rm", "-rf", str(CHROOT)])

    # chroot ディレクトリを再作成
    CHROOT.mkdir(parents=True, exist_ok=True)

    # ── 1) パッケージ一覧を収集 ──
    pkg_list: list[str] = []
    for cfg in get_configs():
        pkgfile = cfg / "packages.txt"
        if pkgfile.exists():
            pkg_list += [
                p.strip() for p in pkgfile.read_text().splitlines()
                if p.strip() and not p.strip().startswith("#")
            ]

    # ── 2) mmdebstrap に渡す必須パッケージ群 ──
    base_pkgs = ["bash", "coreutils"]
    include_pkgs = sorted(set(base_pkgs + pkg_list))

    #signed kernel を探して include_pkgs に追加
    print("Probing for latest linux-image-*-signed package…")
    try:
        result = subprocess.run(
            ["apt-cache", "search", "^linux-image-.*-signed$"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True
        )
        candidates = [line.split()[0] for line in result.stdout.strip().splitlines()]
        if candidates:
            selected_kernel = sorted(candidates)[-1]
            print(f"Detected signed kernel: {selected_kernel}")
            include_pkgs.append(selected_kernel)
        else:
            print("[Warning] No signed kernel found in apt-cache")
    except Exception as e:
        print(f"[Warning] Could not detect signed kernel automatically: {e}")

    #include_opt を定義する
    include_opt = "--include=" + ",".join(include_pkgs)

    print("Deploying base system via mmdebstrap (incl. all packages)…")
    
    # ISOファイルサイズを減らすため、docs / man / 多言語ロケールを除外
    dpkg_opts = [
        "--dpkgopt=path-exclude=/usr/share/doc/*",
        "--dpkgopt=path-exclude=/usr/share/man/*",
        "--dpkgopt=path-exclude=/usr/share/info/*",
        "--dpkgopt=path-exclude=/usr/share/locale/*",
        "--dpkgopt=path-include=/usr/share/locale/ja/*",
    ]
    
    _run([
        "sudo", "mmdebstrap",
        "--architectures=amd64",
        # ISOサイズ削減のため、"minbase"を指定したいが
        # calamaresインストールでエラーになるため"important"を指定する
        "--variant=important",

        # ── 並列ダウンロード・リトライ設定 ──
        "--aptopt=Acquire::Queue-Mode \"host\";",
        "--aptopt=Acquire::Retries \"3\";",

        # ISOファイルサイズを減らすため、Recommendsを除外        
        "--aptopt=APT::Install-Recommends \"false\";",

        # ── あらかじめ集めたパッケージ群 ──
        include_opt,

        # ISOファイルサイズを減らすため、docs / man / 多言語ロケールを除外
        *dpkg_opts,

        # ── その他の引数 ──
        codename,
        str(CHROOT),
        "deb http://deb.debian.org/debian trixie main contrib non-free non-free-firmware"
    ])

    # ISOファイルサイズを減らすため、キャッシュを削除    
    _apt_clean() 

    print(f"Base system + packages deployed via mmdebstrap ({codename}).")

def _copy_overlay():
    """
    各設定レイヤーごとのoverlayファイル群をchrootへ順次コピー。
    sudoers.dの所有権リセットも含め、環境依存トラブルを未然に防ぐ。
    """
    
    for cfg in get_configs():
        overlay = cfg / "overlay"
        if overlay.exists():
            print(f"Applying overlay from {overlay} …")
            # rsync -a なら既存のファイル／シンボリックリンクを上書き削除してくれる
            _run([
                "sudo", "rsync",
                "-a",                      # アーカイブ  
                "--chown=root:root",       # ★ 追加：コピー先では必ず root:root
                f"{overlay}/",
                str(CHROOT) + "/"
            ])
       
    # 所有者がroot出ない場合、sudo が実行できないため、  
    # ここで必ず /etc/sudoers,sudoers.d の所有者を root:root に設定する 
    print("Fixing ownership on /etc/sudoers,/etc/sudoers.d …")
    _run(["sudo", "chroot", str(CHROOT), "chown", "root:root", "/etc/sudoers"])
    _run(["sudo", "chroot", str(CHROOT), "chmod", "0440",      "/etc/sudoers"])
    _run(["sudo", "chroot", str(CHROOT), "visudo", "-cf",      "/etc/sudoers"])
    _run(["sudo", "chroot", str(CHROOT),"chown", "-R", "root:root", "/etc/sudoers.d"])


    print("Overlay files copied.")

def _apply_os_release():
    """
    os-releaseをブランド用テンプレートまたはoverlayからchrootに反映。
    システム情報・識別情報を正しく埋め込むための処理。
    """
    
    # 1) brand.yml を読み込んで context 作成
    brand = os.getenv("OYO_BRAND", "default")

    # 数字接頭辞付きの「*_brand」ディレクトリを探す
    brand_layer = find_brand_layer()

    if not brand_layer:
        raise FileNotFoundError("config 配下に *_brand ディレクトリが見つかりません")

    # この下に各ブランド設定フォルダ（Sample-gnome など）がある想定
    brand_dir = brand_layer / brand
        
     # 1) brand.yml を読み込んで context 作成
    brand_yml = brand_dir / "brand.yml"

    context = {}
    if brand_yml.exists():
        context = yaml.safe_load(brand_yml.read_text())

    # 2) テンプレートがあれば優先してレンダリング
    tpl = brand_dir / "templates" / "os-release.conf.j2"
    if tpl.exists():
        _render_brand_template(
            "os-release.conf.j2",
            Path("etc") / "os-release",
            context
        )
        return

    # 3) なければ従来通り common→flavor→lang overlay からコピー
    for cfg in get_configs():
        src = cfg / "os-release"
        if src.exists():
            _run(["sudo", "cp", str(src), str(CHROOT / "etc/os-release")])
            print(f"Applied os-release from {src}")
            return
    raise FileNotFoundError("config/common/os-release をご確認ください。")

def _apply_calamares_branding():
    """
    Calamaresインストーラのbranding設定をテンプレートで生成またはoverlayから反映する。
    ブート時のブランド表現やインストーラ見た目を柔軟に変更可能にする。
    """
    brand = os.getenv("OYO_BRAND", "default")

    # 数字付きプレフィックスの「*_brand」ディレクトリを探す
    brand_layer = find_brand_layer()
    
    # brand.yml から変数を読み込む
    yml = brand_layer / brand / "brand.yml" if brand_layer else CFG_BASE / "brand" / brand / "brand.yml"

    context = {}
    if yml.exists():
        context = yaml.safe_load(yml.read_text())
    # テンプレートがあればレンダリング
    tpl = brand_layer / brand / "templates" / "branding.desc.j2" if brand_layer else CFG_BASE / "brand" / brand / "templates" / "branding.desc.j2"
    if tpl.exists():
        dest = Path("etc") / "calamares" / "branding" / "custom" / "branding.desc"
        _render_brand_template("branding.desc.j2", dest, context)
    else:
        print(f"No branding.desc.j2 for brand={brand}, skipping template.")

def build_iso():
    """
    ISOイメージ生成の全手順を統括するメイン処理。
    chroot準備、overlay適用、ユーザー作成、フック実行、テンプレ展開、イメージ生成まで一貫して行う。
    """
    logger.info("=== Build started ===")
    codename = _get_codename_from_os_release()

    _prepare_chroot(codename)

    print("Copying overlay…")
    _copy_overlay()
    
    print("User add live…")
    create_live_user()

    # ─── Calamares branding.desc をテンプレートで生成する ───
    print("Applying Calamares branding template…")
    _apply_calamares_branding()
    
    # ——— chroot 内に /proc /sys /dev をバインドマウント ———
    print("Mounting /proc, /sys, /dev into chroot…")
    for fs in ("proc", "sys", "dev"):
        target = CHROOT / fs
        target.mkdir(exist_ok=True)
        _run(["sudo", "mount", "--bind", f"/{fs}", str(target)])
        _register_unmount(target)
        
    # chroot内でネット接続するため、resolv.conf をバインド
    print("Binding host resolv.conf into chroot…")
    _bind_resolv_conf()
        
    # ホストの APT キャッシュを使う (/var/cache/apt/archives)
    print("Binding host APT cache into chroot…")
    apt_cache = CHROOT / "var" / "cache" / "apt" / "archives"
    apt_cache.mkdir(parents=True, exist_ok=True)
    _run(["sudo", "mount", "--bind", "/var/cache/apt/archives", str(apt_cache)])
    _register_unmount(apt_cache)  
    
    # ——— post-install hooks を実行 ———
    print("Running post-install hooks…")
    _run_hooks("post-install")

    # ─── GUI起動のための systemd 設定 ───
    print("Enabling graphical.target…")
    # 1) デフォルトターゲットを graphical.target に
    _run([
        "sudo", "chroot", str(CHROOT),
        "ln", "-sf",
        "/lib/systemd/system/graphical.target",
        "/etc/systemd/system/default.target"
    ])

    print("Applying OS release…")
    _apply_os_release()

    # ① live ディレクトリを作ってカーネルと initrd をワイルドカードで配置
    live_chroot = CHROOT / "live"
    _run(["sudo", "rm", "-rf", str(live_chroot)])
    live_chroot.mkdir(parents=True, exist_ok=True)

    kernel_files = sorted((CHROOT / "boot").glob("vmlinuz-*"))
    initrd_files = sorted((CHROOT / "boot").glob("initrd.img-*"))

    if not kernel_files or not initrd_files:
        raise FileNotFoundError(
            "/boot に vmlinuz-* または initrd.img-* が見つかりません。"
            "linux-image / initramfs-tools がインストールされ、"
            "update-initramfs が成功しているか確認してください。")
        
    kernel_src = kernel_files[-1]
    initrd_src = initrd_files[-1]

    _run(["sudo", "cp", str(kernel_src), str(live_chroot / "vmlinuz")])
    _run(["sudo", "cp", str(initrd_src), str(live_chroot / "initrd.img")])
    print(f"Live kernel ({kernel_src.name}) and initrd ({initrd_src.name}) copied.")

    # ——— ISO ルートを作成 ———
    print("Preparing ISO root…")
    _run(["sudo", "rm", "-rf", str(ISO)])
    ISO.mkdir(parents=True, exist_ok=True)

    # 必要なディレクトリだけコピー（相対パスでマッチさせる）
    _run([
        "sudo", "rsync", "-a",
        # 1) boot/ 以下を丸ごと
        # "--include=boot/", "--include=boot/**",
        # 2) UEFI 用の EFI ディレクトリ
        "--include=EFI/",  "--include=EFI/**",
        # 3) GRUB モジュール（i386-pc, x86_64-efi など）
        "--include=usr/",                  # usr/lib 以下を辿るため
        "--include=usr/lib/",              # usr/lib ディレクトリ自体
        "--include=usr/lib/grub/",         # grub モジュール基本フォルダ
        "--include=usr/lib/grub/**",       # grubモジュール全ファイル
        "--include=usr/lib/shim/",         # shim モジュール基本フォルダ
        "--include=usr/lib/shim/**",       # shimモジュール全ファイル
        "--include=usr/share/",            # usr/share 以下を辿るため
        "--include=usr/share/grub/",       # シェアド・grub ディレクトリ
        "--include=usr/share/grub/**",     # テーマやロケール等
        "--include=usr/share/shim/",       # シェアド・shim ディレクトリ
        "--include=usr/share/shim/**",     # shim
        "--include=usr/lib/grub/i386-pc/",    "--include=usr/lib/grub/i386-pc/**",
        "--include=usr/lib/grub/x86_64-efi/", "--include=usr/lib/grub/x86_64-efi/**",
        # 4) squashfs の置き場 live/ 以下
        "--include=live/", "--include=live/**",
        # 5) それ以外は不要
        "--exclude=*",
        f"{CHROOT}/", f"{ISO}/"
    ])

    # ── Secure Boot 対応の shim + grub を配置 ──
    efi_boot = ISO / "EFI" / "BOOT"
    efi_boot.mkdir(parents=True, exist_ok=True)

    # Secure Boot 対応用の shim + grubx64.efi を配置
    shim_src  = CHROOT / "usr/lib/shim/shimx64.efi.signed"
    mm_src    = CHROOT / "usr/lib/shim/mmx64.efi"

    # GRUB EFI（Microsoft署名済）をそのままコピー
    signed_grub = CHROOT / "usr/lib/grub/x86_64-efi-signed/grubx64.efi.signed"
    _run(["sudo", "cp", str(signed_grub), str(efi_boot / "grubx64.efi")])
    print("署名付き grubx64.efi をコピーしました")

    # shimx64 を BOOTX64.EFI として配置
    _run(["sudo", "cp", str(shim_src), str(efi_boot / "BOOTX64.EFI")])
    _run(["sudo", "cp", str(mm_src), str(efi_boot / "mmx64.efi")])
#    shutil.copy2(shim_src, efi_boot / "BOOTX64.EFI")
#    shutil.copy2(mm_src,   efi_boot / "mmx64.efi")
    print("Secure Boot 用の shimx64.efi, grubx64.efi, mmx64.efi を配置しました")

    print("ISO root prepared (with /proc, /sys, /dev excluded).")

    # ─── Plymouth テンプレートがあればここで適用 ───
    # 1) brand レイヤーを探して paths を決定
    brand = os.getenv("OYO_BRAND", "default")
    brand_layer = find_brand_layer()

    if brand_layer:
        brand_dir = brand_layer / brand
        context = {}
        yml = brand_dir / "brand.yml"
        if yml.exists():
            context = yaml.safe_load(yml.read_text())
        # --- Plymouth テンプレート適用 ---
        theme_tpl = brand_dir / "templates" / "plymouth-theme.conf.j2"
        if theme_tpl.exists():
            _render_brand_template(
                "plymouth-theme.conf.j2",
                Path("usr") / "share" / "plymouth" / "themes" / context.get("theme","default") / "theme",
                context
            )
            print(f"Applied Plymouth theme from {theme_tpl}")
        for tpl in (brand_dir / "templates").glob("plymouth-*.conf.j2"):
            out_name = tpl.name[:-3]
            _render_brand_template(
                tpl.name,
                Path("etc") / "plymouth" / out_name,
                context
            )
            print(f"Applied Plymouth config from {tpl}")

        # --- grub.cfg テンプレート適用 ---
        grub_tpl = brand_dir / "templates" / "grub.cfg.j2"
        if grub_tpl.exists():
            if yml.exists():
                context = yaml.safe_load(yml.read_text())  # 必要なら再読込
            _render_brand_template(
                "grub.cfg.j2",
                ISO / "boot" / "grub" / "grub.cfg",
                context
            )
                
    print(f"Applied branded grub.cfg from {grub_tpl} to BIOS and UEFI")
    uefi_grub_cfg_path = ISO / "EFI" / "BOOT" / "grub.cfg"
    _run([
        "sudo", "cp",
        str(ISO / "boot" / "grub" / "grub.cfg"),
        str(uefi_grub_cfg_path)
    ])
    print(f"Copied grub.cfg to UEFI path: {uefi_grub_cfg_path}")

    # ——— ISO ルートに live カーネル/初期RAMをコピー ———
    live_dir = ISO / "live"
    _run(["sudo", "rm", "-rf", str(live_dir)])
    live_dir.mkdir(parents=True, exist_ok=True)

    # chroot/boot 以下から最新のカーネルと initrd をワイルドカードで取得
    kernel_files = sorted((CHROOT / "boot").glob("vmlinuz-*"))
    initrd_files = sorted((CHROOT / "boot").glob("initrd.img-*"))
    if not kernel_files or not initrd_files:
        raise FileNotFoundError("chroot/boot に vmlinuz-* または initrd.img-* が見つかりません")
    kernel_src = kernel_files[-1]
    initrd_src = initrd_files[-1]

    _run(["sudo", "cp", str(kernel_src), str(live_dir / "vmlinuz")])
    _run(["sudo", "cp", str(initrd_src), str(live_dir / "initrd.img")])
    print(f"Copied live kernel ({kernel_src.name}) and initrd ({initrd_src.name}) into ISO root.")
    
    # squashfs イメージを作成（仮想FSを完全除外）
    # —— squashfs の前に chroot の仮想FSをアンマウント —— 
    print("Unmounting /proc, /sys, /dev from chroot before squashfs…")
    for fs in ("dev", "sys", "proc", "var/cache/apt/archives"):
        _run(["sudo", "umount", "-l", str(CHROOT / fs)])

    # squashfs イメージを作成
    squashfs = live_dir / "filesystem.squashfs"
    print("Creating squashfs image…")

    # squashfs 生成の高速化: LZ4 + 全コア使用
    cpus = os.cpu_count() or 1
    
    _run([
        "sudo", "mksquashfs",
        str(CHROOT),
        str(squashfs),
#        "-comp", "lz4",  # 圧縮方式: lz4（高速、低圧縮）
        "-comp","xz","-Xdict-size","100%",  # 圧縮方式: xz（低速、高圧縮）
        "-processors", str(cpus),   # 全コア数を指定（1以上）
        "-e","live"
    ])
    print(f"Squashfs image created at {squashfs}")

    # ─── ISO イメージを作成 (BIOS＋UEFI のハイブリッド) ───
    logger.info("Creating hybrid ISO (BIOS + UEFI)…")
    _make_iso()

    # 終了ログ
    logger.info("=== Build finished ===")

def _make_iso():
    """
    grub-mkrescueコマンドを使って、chroot/isoディレクトリから最終ISOファイルを生成する。
    BIOS/UEFI両対応イメージの作成を自動化。
    """
    # 動的にファイル名を決定
    iso_name = _get_iso_filename()
    iso_file = ROOT / iso_name
    # Root 権限で実行しないと、root:root のままのファイルを読めない
    _run([
        "sudo", "grub-mkrescue",
        "--output", str(iso_file),
        "--compress=xz",
        # モジュール名はスペース区切り（shell でまとめて渡す）
        "--modules=normal configfile iso9660 part_msdos loopback search",
        str(ISO)
    ])
    logger.info(f"ISO image created: {iso_file}")

def clean_work():
    """
    workディレクトリの全内容をアンマウント・削除し、作業領域を完全初期化する。
    不要なマウント/ゴミを残さないために実行。
    """

    devnull = subprocess.DEVNULL if os.path.exists(os.devnull) else None

    # ① まず残っている bind マウントを外す
    for fs in (
        "var/cache/apt/archives",
        "dev/pts",
        "dev/mqueue",
        "dev/hugepages",
        "dev/shm",
        "dev",
        "sys",
        "proc"
    ):
        target = CHROOT / fs
        # 存在していればアンマウントを試みる
        if target.exists():
            try:
                cmd = ["sudo", "umount", "-l", str(target)]
                subprocess.run(cmd, stdout=devnull, stderr=devnull, check=False)
            except FileNotFoundError:
                  # 念のため、失敗しても先に進める
                pass

    # ② tmpfs が残っている限り、二重マウントも含めてアンマウント
    while True:
        # mountpoint -q はマウントされていれば 0 を返します
        result = subprocess.run(["mountpoint", "-q", str(WORK)])
        if result.returncode != 0:
            break
        subprocess.run(["sudo", "umount", "-l", str(WORK)], check=False)

    # ③ work ディレクトリを丸ごと削除＆再作成
    if WORK.exists():
        _run(["sudo", "rm", "-rf", str(WORK)])
    WORK.mkdir(parents=True, exist_ok=True)

    print(f"Cleaned work directory (and unmounted tmpfs): {WORK}")
    
def create_live_user():
    """
    chroot内にライブ用ユーザー（live）を作成し、/etc/skelからホームディレクトリ内容を補完コピー。
    ライブ環境でユーザーが即利用できる状態にする。
    """
    print("Creating 'live' user in chroot...")

    # live ユーザー作成
    _run([
        "sudo", "chroot", str(CHROOT),
        "useradd", "-m", "-s", "/bin/bash", "live"
    ])

    # パスワード設定
    _run([
        "sudo", "chroot", str(CHROOT),
        "sh", "-c", "echo 'live:live' | chpasswd"
    ])

    # skel の中身を強制コピー（useraddコマンドでコピーが漏れるケースがあったため）
    _run([
        "sudo", "cp", "-a", f"{CHROOT}/etc/skel/.", f"{CHROOT}/home/live/"
    ])
    _run([
        "sudo", "chroot", str(CHROOT),
        "chown", "-R", "live:live", "/home/live"
    ])

    print("ユーザー 'live' を作成し、/etc/skel の全内容を確実にコピーしました。")
    
def find_brand_layer():
    """
    config配下から「*_brand」ディレクトリを探して返すユーティリティ。
    ブランド毎の設定探索を一元化するために利用。
    """
    return next(
        (d for d in CFG_BASE.iterdir() if d.is_dir() and d.name.split("_",1)[1] == "brand"),
        None
    )

def _apt_clean():
    """
    aptキャッシュを削除する
    """
    _run(["sudo","chroot",str(CHROOT),"apt-get","clean","autoclean"])
    _run(["sudo","rm","-rf",str(CHROOT / "var/lib/apt/lists")])
    
def _bind_resolv_conf():
    """
    ホスト側の resolv.conf を chroot に bind-mount して
    chroot 内でも DNS を使えるようにする。
    """
    # systemd-resolved があればそちらを優先
    host_resolv = Path("/run/systemd/resolve/resolv.conf") \
        if Path("/run/systemd/resolve/resolv.conf").exists() \
        else Path("/etc/resolv.conf")
        
    target = CHROOT / "etc/resolv.conf"

    # 1) 親ディレクトリを必ず作成
    _run(["sudo", "mkdir", "-p", str(target.parent)])

    # 2) 既存の壊れた symlink /ファイルを削除して空ファイルを作る
    _run(["sudo", "rm", "-f", str(target)])
    _run(["sudo", "touch", str(target)])

    _run(["sudo", "mount", "--bind", str(host_resolv), str(target)])
    _register_unmount(target)  # 終了時に自動アンマウント

