import os
import json
import subprocess
import threading
from pathlib import Path
from dotenv import load_dotenv
import boto3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    CallbackQueryHandler, ContextTypes, filters,
)

load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN         = os.environ["BOT_TOKEN"]
ALLOWED_USER      = int(os.environ["ALLOWED_USER"])
NACPAC_DIR        = os.environ["NACPAC_DIR"]
MOBILE_DIR        = os.environ["MOBILE_DIR"]
DESKTOP_DIR       = os.environ["DESKTOP_DIR"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

R2_ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
R2_BUCKET      = os.environ["R2_BUCKET"]
R2_ENDPOINT    = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
R2_PUBLIC_URL  = os.environ["R2_PUBLIC_URL"]

STATUS_FILE = Path(__file__).parent / "last_build.json"
_build_lock = threading.Lock()

# Per-user state: tracks last Claude output so we can push/build after
user_state: dict = {}


def auth(update: Update) -> bool:
    return update.effective_user.id == ALLOWED_USER


def run(cmd, cwd=None, timeout=1800):
    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            cwd=cwd, timeout=timeout, env=env,
        )
        out = (result.stdout or b"").decode("utf-8", errors="replace").strip()
        err = (result.stderr or b"").decode("utf-8", errors="replace").strip()
        return result.returncode, out, err
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out."
    except Exception as e:
        return 1, "", str(e)


def save_status(target: str, success: bool, detail: str):
    STATUS_FILE.write_text(json.dumps({
        "target": target, "success": success, "detail": detail[:800],
    }))


def upload_to_r2(local_path: str, r2_key: str) -> str:
    s3 = boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
    )
    s3.upload_file(local_path, R2_BUCKET, r2_key)
    from urllib.parse import quote
    return f"{R2_PUBLIC_URL}/{quote(r2_key)}"


# ── Natural language task handler ────────────────────────────────────────────

async def handle_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not auth(update):
        return

    user_msg = update.message.text.strip()
    await update.message.reply_text("Working on it...")

    prompt = (
        f"You are an AI coding agent for the Nacpac app (D:\\nacpac). "
        f"The app has a mobile folder (Expo React Native, Android) and a desktop folder (Electron, Windows). "
        f"Task: {user_msg}\n\n"
        f"Make all necessary code changes. When done, summarise what you changed in 2-3 lines."
    )

    code, out, err = run(
        f'claude --print --max-turns 10 --model claude-haiku-4-5-20251001 -p "{prompt.replace(chr(34), chr(39))}"',
        cwd=NACPAC_DIR,
        timeout=600,
    )

    summary = out[-1500:] if out else err[-1000:] or "No output."
    user_state[update.effective_user.id] = {"done": True}

    # Auto-push
    await update.message.reply_text(f"Done.\n\n{summary}\n\nPushing to GitHub...")
    # Push mobile submodule first if it has changes
    run('git add . && git commit -m "techbot update" && git push origin main', cwd=os.path.join(NACPAC_DIR, "mobile"))
    # Then push parent repo
    code, out, err = run(
        'git add . && git commit -m "techbot update" && git push origin main',
        cwd=NACPAC_DIR,
    )
    if code != 0:
        await update.message.reply_text(f"Push failed.\n{(err or out)[-400:]}")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Build APK", callback_data="build_apk"),
         InlineKeyboardButton("Build EXE", callback_data="build_exe"),
         InlineKeyboardButton("Build Both", callback_data="build_both")],
        [InlineKeyboardButton("Skip build", callback_data="skip_build")],
    ])
    await update.message.reply_text("Pushed. Build now?", reply_markup=keyboard)


# ── Callback buttons ─────────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth(update):
        return

    data = query.data

    if data in ("build_apk", "build_exe", "build_both"):
        await query.edit_message_text("Build started. This takes 10-20 min for APK...")
        results = []

        if data in ("build_apk", "build_both"):
            if not _build_lock.acquire(blocking=False):
                await query.edit_message_text("Another build is already running.")
                return
            try:
                code, out, err = run(
                    "eas build --platform android --profile preview --non-interactive",
                    cwd=MOBILE_DIR,
                    timeout=1800,
                )
                if code == 0:
                    lines = out.split("\n")
                    # EAS outputs the download URL on a line by itself
                    url = next((l.strip() for l in lines if l.strip().startswith("https://") and ("apk" in l.lower() or "expo.dev" in l.lower() or "objects" in l.lower())), None)
                    if not url:
                        # fallback: grab any https line near the end
                        url = next((l.strip() for l in reversed(lines) if l.strip().startswith("https://")), None)
                    msg = f"APK ready.\nDownload: {url}" if url else f"APK built but URL not found.\nFull output:\n{out[-600:]}"
                    save_status("apk", True, url or out[-400:])
                    results.append(msg)
                else:
                    detail = (err or out)[-400:]
                    save_status("apk", False, detail)
                    results.append(f"APK failed: {detail}")
            finally:
                _build_lock.release()

        if data in ("build_exe", "build_both"):
            code, out, err = run("npm run build", cwd=DESKTOP_DIR, timeout=300)
            if code == 0:
                dist_dir = Path(DESKTOP_DIR) / "dist"
                exe_files = list(dist_dir.glob("*.exe"))
                if exe_files:
                    try:
                        url = upload_to_r2(str(exe_files[0]), f"desktop/{exe_files[0].name}")
                        save_status("exe", True, url)
                        results.append(f"EXE: {url}")
                    except Exception as e:
                        results.append(f"EXE upload failed: {e}")
                else:
                    results.append("EXE build done but no .exe found in dist/")
            else:
                results.append(f"EXE build failed: {(err or out)[-300:]}")

        await query.edit_message_text("Builds complete.\n\n" + "\n".join(results))

    elif data == "skip_build":
        await query.edit_message_text("Done. No build triggered.")


# ── /status command ───────────────────────────────────────────────────────────

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not auth(update):
        return
    lines = []
    if STATUS_FILE.exists():
        data = json.loads(STATUS_FILE.read_text())
        state = "OK" if data["success"] else "FAILED"
        lines.append(f"Last build [{data['target'].upper()}]: {state}\n{data['detail']}")
    else:
        lines.append("No builds recorded yet.")
    code, out, _ = run("git log --oneline -5", cwd=NACPAC_DIR)
    if out:
        lines.append(f"\nLast 5 commits:\n{out}")
    await update.message.reply_text("\n".join(lines))


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not auth(update):
        return
    await update.message.reply_text(
        "Nacpac Techbot\n\n"
        "Just tell me what to build or change in plain text.\n"
        "I'll make the code changes and ask if you want to push and build.\n\n"
        "/status — last build result"
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_task))
    print("Nacpac Techbot running...")
    app.run_polling()
