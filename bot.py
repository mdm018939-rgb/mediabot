import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp

BOT_TOKEN = "8586804228:AAEmGwq9Gba4NBacILVIKAUIyROWeRpGwfE"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def fake_progress(msg):
    for p in range(0, 101, 10):
        await asyncio.sleep(1)
        try:
            await msg.edit_text(f"⏳ Downloading… {p}%")
        except:
            pass

def download_video(url):
    ydl_opts = {
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    msg = await update.message.reply_text("⏳ Downloading… 0%")

    progress = asyncio.create_task(fake_progress(msg))

    try:
        file_path = await asyncio.to_thread(download_video, url)
    except Exception:
        progress.cancel()
        await msg.edit_text("❌ Download failed")
        return

    progress.cancel()
    await msg.edit_text("📤 Uploading…")

    await update.message.reply_video(
        video=open(file_path, "rb"),
        supports_streaming=True
    )

    await msg.delete()
    os.remove(file_path)

if name == "main":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("Bot running...")
    app.run_polling()
