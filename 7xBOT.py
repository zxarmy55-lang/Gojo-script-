# GOJO GOD.py - COMPLETE WORKING SCRIPT
import asyncio
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import json
import os
import sys
import getpass
import time
import io
import random
import logging
from collections import defaultdict
from datetime import datetime
from telegram import Update
from telegram.error import RetryAfter, TimedOut, NetworkError
from telegram.ext import Application, CommandHandler, ContextTypes
import telegram

# ---------------------------
# BOT TOKENS
# ---------------------------
TOKENS = [ "8614074215:AAE2gNVnI2kjAePU9MeQD2k518w1nnw6GeE",
    "8282444875:AAETnQ6I2TQjjZenLgBQcs3GF2LXFN1lv3s",
    "7848499465:AAHxNQPINUMJamEwQCmHEn-t_n8BUkC79yM",
    "8443813380:AAHMPKJ4XJu_Cw95ZTc6OVu2mBfKq95lfUc",
    "8196966190:AAEdRsUpo-uVmRvfZg1q4imLnoERZCTSeNw",
    "8445944754:AAE-jGYAR1AitZTSMU11HtKVZ6WxUkzJ8T0",
    "8641881951:AAGN6-uW0avSQkpoN_KODBoJFOQl8-tn8Yk",
    "8535078549:AAFaHf4U_MPW6Ux_PUW6VhvtQ3JURz3rED4",
    "8681101100:AAGRew9dRLUS7HD86t2HsyCZwJrXx9TJZ5Y",
   "8692349403:AAFBJFdZweXqpkiDLBoq8Xe4yE7n_OQ4nQM",
    "8603362680:AAFtzogk9HwAhZDupsP65o1TdTjwV4XYOJ8",
    "8319728619:AAGvwNVTH-tNBghA340qeCSPBnDgckwJrJY",
    "8549265202:AAF2R2lulFfQh4pFMKyq68GUFtLKxdhFnig",
    "8608360078:AAFqWvALQnMuQSkVe-e19TWZ1HeEgXF1yPE",
    "8130315271:AAGmG99lW7qxD24JrqCat3l00MA3R6H0xkw",
    "8682666099:AAGOZlxIKJipLD3SJ_PiYiZ_gZwrysZTCsw",
    "8732608375:AAGmes8cZnJeVmM9CEELRaDF-FNTv8JCWw0",
    "8393004600:AAGAZJqMGm8HPUTgXOltd0Nsw9wG6SyD_nY",
    "8651558939:AAEVpNePO34ghMbJnq6iqrtyR47-MDI7d1g",
    "8362915044:AAFoXqkmLzSkkeTBFbBwOHdDg5xSB4Z88PI",
   "8676621716:AAF7z6TrKNjA9mhzITkmthu2mgzmCBHAzi8",
    "8774709787:AAHFepQSYP9o3MA3pF7UKAgk86joXDVgfzg",
    "8563333519:AAHo9JSMJ5rdTvUmiTqfMx9aLmaQtBJQWMw",
    "8672143246:AAHxS9yuw7oJ5vmKvnBo9al-UFZPzhbm914",
    "8288183398:AAGx-HqwnVWJ7dogerUw-N9DjsdOkBQIsWw",
    "8531122571:AAHIsFkkiCIHR4oyVb3kkd5Ke3Z6VuF_-ik",
    "8651606634:AAET3xjDfvByX5yQtubTNJlw8XIroKGok5w",
    "8309703684:AAEjOzZ6HFPOu5omTJBoTGu3ZBl5nkL4euQ", ]

# ---------------------------
# OWNER & SUDO CONFIG
# ---------------------------
OWNER_ID = 7069720635
SUDO_FILE = "sudo_users.json"

if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = set()

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

# ---------------------------
# GLOBAL STATE
# ---------------------------
apps = []
bots = []
nc_tasks = {}
spam_tasks = {}
slider_tasks = {}
photo_tasks = {}
chat_photos = {}
GLOBAL_DELAY = 1

# Default messages
NON_SUDO_MSG = "❌ You are not authorized to use this command!"

logging.basicConfig(level=logging.INFO)

# ---------------------------
# PERMISSION HELPERS
# ---------------------------
def is_owner_or_sudo(uid):
    return uid == OWNER_ID or uid in SUDO_USERS

def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id == OWNER_ID:
            return await func(update, context)
        await update.message.reply_text("❌ Only owner can use this command!")
    return wrapper

def sudo_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_owner_or_sudo(update.effective_user.id):
            return await func(update, context)
        await update.message.reply_text(NON_SUDO_MSG)
    return wrapper
    
# ---------------------------
# NC PATTERNS
# ---------------------------
HINDINC_PATTERNS = [
    "{text} चुडाकड़ ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖",
    "{text} रैंडी ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
    "{text} गरीब ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖",
    "{text} चमार˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
    "{text} भेंगे⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖",
    "{text} रैंडी के बच्चे˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
    "{text} गुलाम⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖",
    "{text} गुलामी कर˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
    "{text} चुदाई केंद्र⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖",
    "{text} नांगा नाच कर˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
    "{text} पापा बोल 𝐕ᴀʀᴅᴀɴ को⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖",
    "{text} तेरी मां नंगी करू˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
    "{text} छक्के⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖",
    "{text} भोसड़ी के˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
]

ct_PATTERNS = [
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ɢᴜʟᴀᴍ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴋᴀᴍᴢᴏʀ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ʙᴄ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ᴄᴜᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ᴛᴍʀ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʀɴᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʀᴏᴏ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʟᴏᴅᴀ ʟᴇ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴄᴠʀ ᴋʀ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʀɴᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴛᴍᴋʟ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ɢᴏᴊᴏ ꜱᴇ ᴄʜᴜᴅᴏ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʙʜᴀᴅᴠᴇ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʜɪᴢᴅᴇ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ᴛᴇʀɪ ʙʜɴ ʀɴᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴘʏ ꜱɪᴋʜᴀᴜ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴄᴜᴅᴀᴋᴀᴀᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴘʏ ᴅᴇᴋʜ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴘʏ ʟᴀɢᴀɴᴀ ꜱɪᴋʜᴀᴜ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴋᴜᴛᴛɪ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴄʜᴜꜱꜱᴀ ᴍᴀʀ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴋɪᴅᴇ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ᴘʏ ɴᴄ ʜᴀɪ ʏᴇ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʀᴏᴏ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ᴛᴇʀɪ ʙʜɴ ʀɴᴅ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ɢᴜʟᴀᴍ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʙɪᴛᴄʜ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʀᴀɴᴅɪ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ɢᴀɴᴅ ᴍʀᴀ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ꜱᴘᴇᴇᴅ ʟᴀ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ᴄʜᴜᴅᴀɪ ᴋᴇ ʙᴀᴋʀᴇ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚. ɢᴀɴᴅᴜ",
 "{text} ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ⭒˚.⋆ ʟᴜɴᴅ ᴄʜᴜᴅ"
]

LIVE_PATTERNS = [
    "{text}  𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐊𝐀 𝐁𝐄𝐓𝐀 𝐇𝐄 𝐓𝐔  🔥⃤⃟⃝🐦‍🔥『🚩』",
    "{text}  𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐂𝐇𝐃 𝐊𝐄 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐎𝐍 𝐓𝐎𝐏 🔥⃤⃟⃝🐦‍🔥『🚩』",
    "{text}  𝐂𝐔𝐃 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐎𝐍 𝐓𝐎𝐏 🔥⃤⃟⃝🐦‍🔥『🚩』",
    "{text}  𝐂𝐘𝐀 𝐑𝐄 𝐑𝐍𝐃𝐘 𝐊𝐄 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐒𝐄 𝐂𝐔𝐃 🔥⃤⃟⃝🐦‍🔥『🚩』",
    "{text}  𝐓𝐄𝐑𝐈 𝐂𝐔𝐃𝐘 𝐁𝐘 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐏𝐀𝐏𝐀  🔥⃤⃟⃝🐦‍🔥『🚩』",
    "{text}  𝐂𝐕𝐑 𝐊𝐑 𝐓𝐌𝐊𝐂 🔥⃤⃟⃝🐦‍🔥『🚩』",
    "{text}  𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐔𝐓𝐓𝐓𝐈𝐘𝐀 🔥⃤⃟⃝🐦‍🔥 『🚩』",
    "{text}  𝐓𝐄𝐑𝐈 𝐁𝐄𝐇𝐍 𝐂𝐎𝐃 𝐊𝐄 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐅𝐀𝐑𝐀𝐑 🔥⃤⃟⃝🐦‍🔥『🚩』",
    "{text}  ---𝐁ʜᴀɢ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐑ɴᴅʏ🐣",
    "{text}  𝐓ʀᴀ 𝐁ᴀᴀᴘ 𝐀ᴍᴀ𝐍 sᴇ चुद गया -!",
    "Aʟᴏᴏ Kʜᴀᴋᴇ {text}  Kɪ Mᴀ Cʜᴅ Dᴜɴɢᴀ!",
    "{text}  𝐊ᴜᴛᴛɪʏᴀ 𝐇ᴇ 𝐓ᴜ",
    "{text}  𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽  ᴘᴀᴘᴀ पिताश्री Mᴇʀɪ Mᴀ Cʜᴅ Dᴏ",
    "{text}  Kɪ Mᴀ Bᴏʟᴇ 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 ᴘᴀᴘᴀ Sᴇ Cʜᴜᴅᴜɴɢɪ",
    "{text}  Kɪ Bᴇʜɴ Kɪ Cʜᴜ𝐔ᴛ Kᴀʟɪ Kᴀʟɪ",
    "{text}  Kɪ Mᴀ R𝐍ᴅɪ",
    "{text}  ɢᴀʀᴇᴇʙ ᴋᴀ ʙᴀᴄʜʜᴀ",
    "{text}  ᴄʜʜUᴅ ᴋᴇ ᴘᴀɢᴀʟ ʜᴏɢᴀʏᴀ",
    "{text}  ᴋɪ ʙᴇʜɴ ᴄʜᴏᴏᴅᴜ",
    "{text}  ʟɴᴅ ᴄʜᴜsᴇɢᴀ sᴀʙᴋᴀ",
    "{text}  ᴋɪ ᴍᴀ ᴋᴏ ᴄʜᴏᴏᴅᴇ ᴀᴍᴀɴ ᴘᴀᴘᴀ",
    "{text}  ᴋɪ ᴍᴀ ᴀᴍᴀɴ  ᴘᴀᴘᴀ ꜱᴇ ᴄʜᴜᴅᴇ",
    "{text}  ᴀᴍᴀɴ ᴘᴀᴘᴀ ꜱᴇ ᴄʜᴜᴅᴀ",
    "{text}  CUDKE MARGYA",
    "{text}  ɴᴇ ᴀᴍᴀɴ ᴘᴀᴘᴀ ᴋᴏ ʙᴀᴀᴩ ʙɴᴀ ʟɪyᴀ",
    "{text}  ʙᴏʟᴇ ᴀᴍᴀɴ  ᴘᴀᴘᴀ ᴩᴀᴩᴀ",
    "{text}  𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐒𝐄 𝐂𝐇𝐔𝐔𝐃𝐈",
    "{text}  𝐍𝐎𝐊𝐀𝐑 𝐇𝐄 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐏𝐀𝐏𝐀 𝐊𝐀 😋",
]

BIHARI_PATTERNS = [
    "{text} भोसड़ी के बा⋆꙳^̩̩͙❅*̩̩͙‧͙ ‧͙*̩̩͙❆ ͙͛ ˚₊⋆",
    "{text} सतमेरवनी₊˚ʚ ᗢ₊˚✧ ﾟ.",
    "{text} गरीब⋆꙳^̩̩͙❅*̩̩͙‧͙ ‧͙*̩̩͙❆ ͙͛ ˚₊⋆",
    "{text} कॉकर के ह₊˚ʚ ᗢ₊˚✧ ﾟ.",
    "{text} नसल⋆꙳^̩̩͙❅*̩̩͙‧͙ ‧͙*̩̩͙❆ ͙͛ ˚₊⋆",
    "{text} एगो बेतरतीब के लइका₊˚ʚ ᗢ₊˚✧ ﾟ.",
    "{text} गुलाम⋆꙳^̩̩͙❅*̩̩͙‧͙ ‧͙*̩̩͙❆ ͙͛ ˚₊⋆",
    "{text} कमबख्त सेंटर के बा₊˚ʚ ᗢ₊˚✧ ﾟ.",
    "{text} नंगा हो गइल बा⋆꙳^̩̩͙❅*̩̩͙‧͙ ‧͙*̩̩͙❆ ͙͛ ˚₊⋆",
    "{text} छक्का के लोग⋆꙳^̩̩͙❅*̩̩͙‧͙ ‧͙*̩̩͙❆ ͙͛ ˚₊⋆",
    "{text} रे हरामी₊˚ʚ ᗢ₊˚✧ ﾟ.",
]

ENGLISH_PATTERNS = [
 "{text}─(😀)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😂)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤣)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😭)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😝)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🙂)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😙)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🥶)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤢)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🥵)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🫩)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😤)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤮)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤩)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😓)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤡)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😪)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤕)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤯)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(☹️)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😢)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😎)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😑)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😶)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(😖)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
 "{text}─(🤥)──ɢᴏᴊᴏ x  ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ᴛᴀᴛᴛᴇ ⋆‧°𓏲ּ𝄢",
]

EMOJI_NC_EMOJIS = ["🐧","🦭","🦈","🫍","🐬","🐋","🐳","🐟","🐠","🐡","🦐","🦞","🦀","🦑","🐙","🪼","🦪","🪸","🫧","🦂"]
EMOJI_NC_PATTERN = "{text} 𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎<⋆.ೃ࿔*:･{emoji}⋆.ೃ࿔*:･>"

NC1_EMOJIS = ["💐","🌹","🥀","🌺","🌷","🪷","🌸","💮","🏵️","🪻","🌻","🌼","🍂","🍁","🌱","🍃","☘️","🍀"]
NC1_PATTERN = "˚⊱{emoji}⊰˚{text} 𝐂ʏᴜ 𝐑ᴇ मदरचोद  GOJO बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥 <˚⊱⊰˚{emoji}˚⊱⊰˚>"

NC2_EMOJIS = ["🪽","🪶","🐦","🐦‍⬛","🐓","🐔","🐣","🐤","🐥","🦅","🦉","🦜","🕊️","🦤","🦢","🦆","🪿","🦩","🦚","🐦‍🔥","🦃"]
NC2_PATTERN = "{text} 𝙏𝙈𝙆𝘽 𝙈𝙄𝙀 𝙈𝙐𝙏 𝘿𝙐 ? 𝙏𝘽𝙆𝘾 𝙈𝙄𝙀 𝙇𝘼𝘼𝙏 𝙂𝙐𝙇𝘼𝙈𝙄 𝙆𝙍 ¡! <ִֶָ𓂃 ࣪˖ ִֶָ{emoji}ִֶָ་༘࿐>"

NC3_EMOJIS = ["💠","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇦🇽","🇦🇿","🇧🇦","🇧🇧","🇧🇩","🇧🇪","🇧🇫","🇧🇬","🇧🇭","🇧🇮","🇧🇯","🇧🇱","🇧🇲","🇧🇳","🇧🇴","🇧🇶","🇧🇷","💠"]
NC3_PATTERN = "{text} नहीं नहीं तेरी मां को 𝐒ɪʀғ  GOJO बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ??? <{emoji}>"

NC4_EMOJIS = ["🏔️","🌋","☃️","🏝️","🏖️","🌊","🌬️","❄️","🌀","🌪️","⚡","☔","💧","☁️","🌨️","🌧️","🌩️","⛈️","🌦️","🌥️","⛅","🌤️","☀️","🌞","🌝","🌚","🌜","🌛","🌙","⭐","🌟","✨","🪐","🌍","🌠","🌌","☄️","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]
NC4_PATTERN = "{text}𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭 <{emoji}>"

NC5_EMOJIS = ["🪔","🪅","🪩","🎐","🎏","🎎","🧨","🫟","🎨","💸","💵","💴","💶","💷","💳","💰","🧿","🪬","📿","🪤","♥️","🩶","🩵","🩷","🤍","🖤","🤎","❤️","🧡","💛","💚","💙","💜"]
NC5_PATTERN = "{text} 🩷गुलाबी चूत वाला💘 <𓂃˖˳·˖ ִֶָ ⋆{emoji}⋆ ִֶָ˖·˳˖𓂃 ִֶָ>"

KNC_EMOJIS = ["😆","😂","🤣","🥰","😍","😌","😏","🤤","😋","😛","😝","😜","🤪","🫪","😔","🥺","😬","😑"]
KNC_PATTERN = "{text} <{emoji}> 🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯💢🫯"

ANC_EMOJIS = ["🌈","☔","⚡","🌪️","🌀","🏖️","🏝️","🌊","🌬️","❄️","💧","🌨️","☁️"]
ANC_PATTERN = "{text} <{emoji}> 🍃🪢📯🍃📯🪢🍃🪢📯🍃🪢📯🍃🪢📯🍃🪢📯🍃🪢📯🍃🪢📯🍃🪢📯🍃"

FNC_EMOJIS = ["❤️","🧡","💛","💚","🩵","💙","💜","🤎","🖤","🩶","🤍","🩷"]
FNC_PATTERN = "{text} 𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾 <{emoji}> જ⁀➴❤️‍🔥જ⁀➴🎀જ⁀➴🤍જ⁀➴💓જ⁀➴❣️જ⁀➴🩵જ⁀➴💚જ⁀➴❤️"

# ---------------------------
# SLIDE MESSAGES
# ---------------------------
SLIDE1_MESSAGES = [
    "𝐓ᴍᴋʙ 𝐑ɴᴅʏ ᴋᴇ 𝐋ᴀᴅᴋᴇ 😈🖕🏻😈🖕🏻😈",
    "𝐓ᴇʀɪ ᴍᴀᴀ ᴍᴀʀ ɢʏɪ ¿😆😆😆",
    "𝐀ᴀʀ ꜱᴀᴍᴀɴᴅᴀʀ ᴘᴀᴀʀ ꜱᴀᴍᴀɴᴅᴀʀ ʙᴇᴇᴄʜ ᴍɪᴇ ʜᴀɪ ɴᴀɪʏᴀ ᴘʜʟᴇ ᴛᴇʀɪ ʙʜᴇɴ चोदू ʙᴀᴀᴅ ᴍɪᴇ चोदू ᴍᴀɪʏᴀ ¡! 🥰🖕🏻🥰🖕🏻🥰🖕🏻",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ʜᴜᴍᴇꜱʜᴀ ᴍᴜᴊʜꜱᴇ ʜɪ ᴋʏᴜ चुडती है ¡! 😡🤬😡🤬😡",
    "𝐃ᴇᴋʜ ᴀᴀᴊ ᴛᴇʀɪ 𝐌ᴀᴀ ᴋᴀ ɴᴀɴɢᴀ ᴅᴀɴᴄᴇ ᴅɪᴋʜᴀᴜ ! 🩰🧑🏻‍🩰",
    "𝐒𝐀𝐘 𝐆𝐎𝐉𝐎 !! ON TOP",
    "😂😂😂😂 𝐓ᴇRI Mᴀᴀ GOJO sᴇ ᴄʜᴅɪ 😂😂😂😂",
    "𝐏ɪʟʟᴇ  ᴋᴜᴛᴛɪʏᴀ ᴋᴇ ʙᴀᴄᴄʜᴇ ᴄᴜᴅ😆💔🖕🏽",
    "𝑻𝑴𝑲𝑪 𝑷𝑬 𝑪𝑯𝑨𝑷𝑷𝑨𝑳 𝑴𝑨𝑹𝑼 !!🔥😂🩴",
    "𝑻𝑬𝑹𝑨 𝑩𝑨𝑨𝑷 𝑨𝑴𝑨𝑵🤢🤢🤢",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "𝐘ᴇ 𝐃ᴇᴋ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ᴏᴅᴋᴇ 🏃 𝐀ɪꜱᴇ 𝐁ʜᴀɢᴀ 𝐓ʜᴀ?",
    "अबे गंदी नाली के कीड़े, तू अपनी औकात में रह! 🤢👊",
    "𝐆ᴀʟᴀᴛ 𝐉ᴀᴡᴀʙ  𝐀ʙ 𝐓ᴜ 𝐂ᴜᴅᴇɢA/~😏🙌 ⚡",
    "𝗧ᴇ𝗥ɪ 𝗠ᴀ तो 𝗛ᴇ𝗟ɪ𝗖ᴏ𝗣ᴛ𝗘ʀ में चोदूंगा रंडीके 🤣🤣🔥",
    "𝘢𝘣𝘦 𝘩𝘢𝘵𝘵 सस्ती Rᴀɴᴅɪ ᴋᴀ काला 𝘉𝘢𝘤𝘤𝘩𝘢🤢",
    "𝐀ᴀ𝐉 𝐌ᴇ𝐀 𝐊ʜᴀᴜ𝐍ɢʜ𝐀 𝐁ᴜʀɢᴇ𝐑 𝐓ᴇ𝐑ɪ 𝐁ᴇʜᴇ𝐍 को chodunga घर घर 😹🖕😹🖕😹",
    "𝐓ᴜᴊʜ𝐄 𝐂ᴏᴏ𝐋 𝐁ᴏʟ𝐔 𝐘ᴀ 𝐑ᴀɴᴅɪᴋ𝐀  𝐁ᴀᴄᴄʜ𝐀 😑👏🏻😑👏🏻?",
    "Tere baap 𝐆𝐎𝐉𝐎 !! ? 💓🤪💓🤪💓🤪💓🤪💓🤪💓🤪💓🤪💓🤪",
    "𝐒ᴀʏ 𝐑ᴀ𝐏ɪsᴛ GOJO  पिता जी 🤢¿? Mere मां mat चोदो प्लेस 🙏🏻🔥",
    "𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ  GOJO 𝐒ᴇ - 🦢💘",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ  GOJO ! 🌙",
    "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh  GOJO ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe  GOJO ka hamla 😂⚔🔥💥",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass  GOJO hai 😂🎀",
    " try maa hagte hue paad mari -#😹🔥🥀",
    "  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ  GOJO 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜","𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ  GOJO 𝐒ᴇ - 🦢💘",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ  GOJO ! 🌙",
    "acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
    "chudke bhaga kaise 😂💥🤣🤘🏻",
    "ne toh  GOJO ka lun muh me lelia 😂🙏🏻😂🙏🏻",
    "try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
    "mkl lun te vaj 😂✊🏻💦",
    "𝗧ᴍᴋ𝗕 pe  GOJO ka hamla 😂⚔🔥💥",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "chl rndyce chud ke dikha 😂💥🤣🔥",
    "𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
    "tera baap bass  GOJO hai 😂🎀",
    " try maa hagte hue paad mari -#😹🔥🥀",
    "  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ  GOJO 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
]

SLIDE2_MESSAGES = [
    "𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐆ᴜʟᴀʙɪ 𝐂ʜᴜᴛ ᴍɪᴇ 𝐌ᴜᴛ ᴋʀ ʙʜᴀɢ ᴊᴀᴜɢᴀ 𝐁ꜱᴅᴋ ! 😆",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴄʜᴏᴅɴᴇ ᴀʀʜᴀ ʜᴜ ʀᴜᴋ ᴡʜɪ ɢᴜʟᴀᴍ ! 😾",
        "  ---𝐁ʜᴀɢ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐑ɴᴅʏ🐣",
    "  𝐓ʀᴀ 𝐁ᴀᴀᴘ 𝐀ᴍᴀ𝐍 sᴇ चुद गया -!",
    "Aʟᴏᴏ Kʜᴀᴋᴇ   Kɪ Mᴀ Cʜᴅ Dᴜɴɢᴀ!",
    "  𝐊ᴜᴛᴛɪʏᴀ 𝐇ᴇ 𝐓ᴜ",
    "  𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽  ᴘᴀᴘᴀ पिताश्री Mᴇʀɪ Mᴀ Cʜᴅ Dᴏ",
    "  Kɪ Mᴀ Bᴏʟᴇ 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 ᴘᴀᴘᴀ Sᴇ Cʜᴜᴅᴜɴɢɪ",
    "  Kɪ Bᴇʜɴ Kɪ Cʜᴜ𝐔ᴛ Kᴀʟɪ Kᴀʟɪ",
    "  Kɪ Mᴀ R𝐍ᴅɪ",
    "  ɢᴀʀᴇᴇʙ ᴋᴀ ʙᴀᴄʜʜᴀ",
    "  ᴄʜʜUᴅ ᴋᴇ ᴘᴀɢᴀʟ ʜᴏɢᴀʏᴀ",
    "  ᴋɪ ʙᴇʜɴ ᴄʜᴏᴏᴅᴜ",
    "  ʟɴᴅ ᴄʜᴜsᴇɢᴀ sᴀʙᴋᴀ",
    "  ᴋɪ ᴍᴀ ᴋᴏ ᴄʜᴏᴏᴅᴇ ᴀᴍᴀɴ ᴘᴀᴘᴀ",
    "  ᴋɪ ᴍᴀ ᴀᴍᴀɴ  ᴘᴀᴘᴀ ꜱᴇ ᴄʜᴜᴅᴇ",
    "  ᴀᴍᴀɴ ᴘᴀᴘᴀ ꜱᴇ ᴄʜᴜᴅᴀ",
    "  CUDKE MARGYA",
    "  ɴᴇ ᴀᴍᴀɴ ᴘᴀᴘᴀ ᴋᴏ ʙᴀᴀᴩ ʙɴᴀ ʟɪyᴀ",
    "  ʙᴏʟᴇ ᴀᴍᴀɴ  ᴘᴀᴘᴀ ᴩᴀᴩᴀ",
    "  𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐒𝐄 𝐂𝐇𝐔𝐔𝐃𝐈",
    "  𝐍𝐎𝐊𝐀𝐑 𝐇𝐄 𝐆ᴏᴊᴏ 𝐋ɪᴠᴇ 🪽 𝐏𝐀𝐏𝐀 𝐊𝐀 😋",
    "𝐓ᴇʀɪ ʙʜᴇɴ ᴋᴇ ʙᴏᴏʙɪᴇꜱ ᴋᴇ ʙᴇᴇᴄʜ ᴍɪᴇ ʟɴᴅ ꜰᴀꜱᴀ ᴋʀ ᴍᴜᴛʜ ᴍᴀᴀʀ ᴅᴜɢᴀ ʙꜱᴅᴋ 😆",
    "𝐓ᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍɪᴇ ᴍᴀɢɢɪᴇ ʙɴᴀ ᴋʀ ᴍᴜᴛʜ ʙʜᴀʀ ᴅᴜɢᴀ ! 😆",
    "𝐓ᴇʀɪ ᴍᴀᴀ ʙʜᴛ ʀᴏᴛɪ ᴇʏ ʙɪʟᴋᴜʟ 𝐓ᴇʀɪ ᴛʀʜ ᴅᴏɴᴏ ʀɴᴅʏ ʀᴏɴᴀ ᴋʀᴛᴇ ʜᴏ ᴇᴡᴡ ! 😆",
    "𝐓ᴇʀɪ ʙʜᴇɴ ᴋɪ ɢᴜʟᴀʙɪ ᴄʜᴛ ᴋᴀᴀᴛ ᴅᴜɢᴀ ɢᴜʟᴀᴍ ! 😆",
    "𝐂ʜʟ ɢᴜʟᴀᴍ ɢᴜʟᴀᴍɪ ᴋʀ ! 😾",
]

SLIDE3_PATTERN = "{text} જ⁀➴🍃જ⁀➴😆જ⁀➴❤️"

# ---------------------------
# SPAM PATTERNS
# ---------------------------
SPAM1_PATTERN = "🎐𓍼ֶ˖ܓ  ( < {text} > )  तेरे मां के दूदू के बीच मेरा lund fas gaya oops 🤪（ ͜.🍆 ͜.）"

SPAM2_SINGLE_PATTERN = "{text} - 𝐓ᴇʀʏ 𝐌ᴀ  𝐊ᴀ 𝐂ʜɪʟᴅ 𝐏ᴏʀɴ 𝐑ᴇᴄᴏʀᴅ 𝐇ᴏɢʏᴀ 𝐀ʙ 𝐓ᴏ 𝐒ɪᴅʜᴀ 𝐕ɪʀᴀʟ 𝐇ᴏɢᴀ 𝐘ᴇ ˙✧˖°📷༘ ⋆｡°"
SPAM2_PATTERN = (SPAM2_SINGLE_PATTERN + "\n\n") * 10

SPAM3_SINGLE_PATTERN = "{text} ࿐Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन  GOJO /\~ 👑 बाप से सही chudi 🥵🔥"

SPAM3_PATTERN = (SPAM3_SINGLE_PATTERN + "\n\n") * 10

SPAM4_SINGLE_PATTERN = "𓆩{text}𓆪 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐓ᴇʀʏ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅɴᴇ  मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃"

SPAM4_PATTERN = (SPAM4_SINGLE_PATTERN + "\n\n") * 10

            
# ---------------------------
# NC LOOP FUNCTIONS
# ---------------------------
async def hindinc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            pattern = HINDINC_PATTERNS[i % len(HINDINC_PATTERNS)]
            new_title = pattern.format(text=text)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def ctnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            pattern = ct_PATTERNS[i % len(ct_PATTERNS)]
            new_title = pattern.format(text=text)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def livenc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            pattern = LIVE_PATTERNS[i % len(LIVE_PATTERNS)]
            new_title = pattern.format(text=text)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def biharinc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            pattern = BIHARI_PATTERNS[i % len(BIHARI_PATTERNS)]
            new_title = pattern.format(text=text)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def engnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            pattern = ENGLISH_PATTERNS[i % len(ENGLISH_PATTERNS)]
            new_title = pattern.format(text=text)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def emonc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = EMOJI_NC_EMOJIS[i % len(EMOJI_NC_EMOJIS)]
            new_title = EMOJI_NC_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def nc1_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NC1_EMOJIS[i % len(NC1_EMOJIS)]
            new_title = NC1_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def nc2_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NC2_EMOJIS[i % len(NC2_EMOJIS)]
            new_title = NC2_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def nc3_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NC3_EMOJIS[i % len(NC3_EMOJIS)]
            new_title = NC3_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def nc4_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NC4_EMOJIS[i % len(NC4_EMOJIS)]
            new_title = NC4_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def nc5_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NC5_EMOJIS[i % len(NC5_EMOJIS)]
            new_title = NC5_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def knc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = KNC_EMOJIS[i % len(KNC_EMOJIS)]
            new_title = KNC_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def anc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = ANC_EMOJIS[i % len(ANC_EMOJIS)]
            new_title = ANC_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def fnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FNC_EMOJIS[i % len(FNC_EMOJIS)]
            new_title = FNC_PATTERN.format(text=text, emoji=emoji)
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# SLIDE LOOP FUNCTIONS
# ---------------------------
async def slide1_loop(bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            message = SLIDE1_MESSAGES[i % len(SLIDE1_MESSAGES)]
            await bot.send_message(chat_id, message, reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def slide2_loop(bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            message = SLIDE2_MESSAGES[i % len(SLIDE2_MESSAGES)]
            await bot.send_message(chat_id, message, reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def slide3_loop(bot, chat_id, target_msg_id, text):
    i = 0
    while True:
        try:
            message = SLIDE3_PATTERN.format(text=text)
            await bot.send_message(chat_id, message, reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# SPAM LOOP FUNCTIONS
# ---------------------------
async def spam1_loop(bot, chat_id, text):
    while True:
        try:
            message = SPAM1_PATTERN.format(text=text)
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def spam2_loop(bot, chat_id, text):
    while True:
        try:
            message = SPAM2_PATTERN.format(text=text)
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def spam3_loop(bot, chat_id, text):
    while True:
        try:
            message = SPAM3_PATTERN.format(text=text)
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def spam4_loop(bot, chat_id, text):
    while True:
        try:
            message = SPAM4_PATTERN.format(text=text)
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# PHOTO LOOP FUNCTION
# ---------------------------
async def photo_loop(bot, chat_id):
    while True:
        try:
            if chat_id not in chat_photos or not chat_photos[chat_id]:
                await asyncio.sleep(5.0)
                continue
            
            photos_list = chat_photos[chat_id]
            file_id = random.choice(photos_list)

            photo_file = await bot.get_file(file_id)
            buf = io.BytesIO()
            await photo_file.download_to_memory(buf)
            buf.seek(0)
            
            await bot.set_chat_photo(chat_id=chat_id, photo=buf)
            await asyncio.sleep(0.5)
            
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"Photo change error: {e}")
            await asyncio.sleep(5.0)

# ---------------------------
# NC COMMAND HANDLERS
# ---------------------------
@sudo_only
async def hindinc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /hindinc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(hindinc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Hindi NC started!\n📝 Text: {text}")

@sudo_only
async def ctnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /ctnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(ctnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ ct NC started!\n📝 Text: {text}")

@sudo_only
async def livenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /livenc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(livenc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ LIVE NC started!\n📝 Text: {text}")

@sudo_only
async def biharinc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /biharinc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(biharinc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Bihari NC started!\n📝 Text: {text}")

@sudo_only
async def chinesenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Chinese NC is coming soon! Stay tuned.")

@sudo_only
async def engnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /engnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(engnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ English NC started!\n📝 Text: {text}")

@sudo_only
async def emonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /emonc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(emonc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Emoji NC started!\n📝 Text: {text}")

@sudo_only
async def nc1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /nc1 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(nc1_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC1 started!\n📝 Text: {text}")

@sudo_only
async def nc2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /nc2 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(nc2_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC2 started!\n📝 Text: {text}")

@sudo_only
async def nc3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /nc3 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(nc3_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC3 started!\n📝 Text: {text}")

@sudo_only
async def nc4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /nc4 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(nc4_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC4 started!\n📝 Text: {text}")

@sudo_only
async def nc5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /nc5 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(nc5_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC5 started!\n📝 Text: {text}")

@sudo_only
async def knc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /knc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(knc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ KNC started!\n📝 Text: {text}")

@sudo_only
async def anc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /anc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(anc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ ANC started!\n📝 Text: {text}")

@sudo_only
async def fnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /fnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(fnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ FNC started!\n📝 Text: {text}")

# ---------------------------
# SLIDE COMMAND HANDLERS
# ---------------------------
@sudo_only
async def slide1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start slide1!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(slide1_loop(b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Slide1 started!")

@sudo_only
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.add(update.message.reply_to_message.from_user.id)
        return await update.message.reply_text("💥 Slide spam started.")
        
@sudo_only
async def slide2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start slide2!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(slide2_loop(b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Slide2 started!")

@sudo_only
async def slide3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /slide3 <text> (reply to a message)")
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start slide3!")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(slide3_loop(b, chat_id, target_msg_id, text)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Slide3 started!\n📝 Text: {text}")

# ---------------------------
# SPAM COMMAND HANDLERS
# ---------------------------
@sudo_only
async def spam1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /spam1 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(spam1_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Spam1 started!\n📝 Text: {text}")

@sudo_only
async def spam2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /spam2 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(spam2_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Spam2 started!\n📝 Text: {text}")

@sudo_only
async def spam3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /spam3 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(spam3_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Spam3 started!\n📝 Text: {text}")

@sudo_only
async def spam4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /spam4 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(spam4_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Spam4 started!\n📝 Text: {text}")

# ---------------------------
# PHOTO COMMAND HANDLERS
# ---------------------------
@sudo_only
async def savephoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Reply to a photo to save it!")
    
    chat_id = update.message.chat_id
    file_id = update.message.reply_to_message.photo[-1].file_id
    
    if chat_id not in chat_photos:
        chat_photos[chat_id] = []
    
    chat_photos[chat_id].append(file_id)
    await update.message.reply_text(f"✅ Photo saved! Total: {len(chat_photos[chat_id])}")

@sudo_only
async def startphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    if chat_id not in chat_photos or len(chat_photos[chat_id]) < 1:
        return await update.message.reply_text("⚠️ Save at least 1 photo first using /savephoto (reply to a photo)!")
    
    if chat_id in photo_tasks:
        for task in photo_tasks[chat_id]:
            task.cancel()
    
    tasks = [asyncio.create_task(photo_loop(b, chat_id)) for b in bots]
    photo_tasks[chat_id] = tasks
    await update.message.reply_text(f"🔄 Photo loop started for {len(bots)} bots! (Changes every 0.5s with random photos)")

@sudo_only
async def stopphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    if chat_id in photo_tasks:
        for task in photo_tasks[chat_id]:
            task.cancel()
        del photo_tasks[chat_id]
        await update.message.reply_text("⏹ Photo loop stopped!")
    else:
        await update.message.reply_text("❌ No active photo loop")

@sudo_only
async def clearphotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    if chat_id in chat_photos:
        del chat_photos[chat_id]
        await update.message.reply_text("🗑 Saved photos cleared!")
    else:
        await update.message.reply_text("❌ No saved photos to clear")

@sudo_only
async def listphotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    if chat_id not in chat_photos or not chat_photos[chat_id]:
        return await update.message.reply_text("📭 No photos saved yet! Use /savephoto (reply to a photo)")
    
    count = len(chat_photos[chat_id])
    await update.message.reply_text(f"📸 Total saved photos: {count}\n\nUse /startphoto to begin changing group PFP with these photos!")

# ---------------------------
# STOP COMMAND HANDLERS
# ---------------------------
@sudo_only
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
        await update.message.reply_text("🛑 NC stopped!")
    else:
        await update.message.reply_text("❌ No NC running in this chat.")

@sudo_only
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text("🛑 Spam stopped!")
    else:
        await update.message.reply_text("❌ No Spam running in this chat.")

@sudo_only
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
        await update.message.reply_text("🛑 Slide stopped!")
    else:
        await update.message.reply_text("❌ No Slide running in this chat.")

@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    stopped = []
    
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
        stopped.append("NC")
    
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        stopped.append("Spam")
    
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
        stopped.append("Slide")
    
    if chat_id in photo_tasks:
        for task in photo_tasks[chat_id]:
            task.cancel()
        del photo_tasks[chat_id]
        stopped.append("Photo")
    
    if stopped:
        await update.message.reply_text(f"🛑 Stopped: {', '.join(stopped)} in this chat!")
    else:
        await update.message.reply_text("❌ No active activities to stop.")

# ---------------------------
# CONTROL COMMAND HANDLERS
# ---------------------------
@sudo_only
async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_DELAY
    if not context.args:
        await update.message.reply_text(f"⏱ Current delay: {GLOBAL_DELAY:.3f}s\nUsage: /delay <0.005-0.05>")
        return
    try:
        new_delay = float(context.args[0])
        if new_delay < 0.005 or new_delay > 0.05:
            await update.message.reply_text("❌ Delay must be between 0.005 and 0.05 seconds.")
            return
        GLOBAL_DELAY = new_delay
        await update.message.reply_text(f"✅ Delay set to {GLOBAL_DELAY:.3f}s")
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Use /delay <0.005-0.05>")

@sudo_only
async def hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🐍 GOJO X BHAGWAN is alive!")

# --- Auto Replies ---
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid, chat_id = update.message.from_user.id, update.message.chat_id
    if uid in slide_targets:
        for text in RAID_TEXTS: await update.message.reply_text(text)
    if uid in slidespam_targets:
        for text in RAID_TEXTS: await update.message.reply_text(text)
    if chat_id in swipe_mode:
        for text in RAID_TEXTS: await update.message.reply_text(f"{swipe_mode[chat_id]} {text}")
        
# ---------------------------
# SUDO MANAGEMENT COMMANDS
# ---------------------------
@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message to add them as sudo!")
    target_user = update.message.reply_to_message.from_user
    uid = target_user.id
    username = target_user.username or target_user.first_name
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Added sudo user: {username} (ID: {uid})")

@owner_only
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message to remove them from sudo!")
    target_user = update.message.reply_to_message.from_user
    uid = target_user.id
    username = target_user.username or target_user.first_name
    if uid == OWNER_ID:
        return await update.message.reply_text("❌ Cannot remove the owner from sudo list!")
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"✅ Removed sudo user: {username} (ID: {uid})")
    else:
        await update.message.reply_text(f"❌ {username} is not in the sudo list!")

@owner_only
async def sudos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not SUDO_USERS:
        return await update.message.reply_text("📋 No sudo users added yet.\n\nOnly the owner can use commands.")
    lines = []
    for uid in SUDO_USERS:
        if uid == OWNER_ID:
            lines.append(f"👑 **{uid}** (Owner)")
        else:
            lines.append(f"🛡️ `{uid}`")
    await update.message.reply_text(f"**📋 SUDO USERS LIST**\n\n" + "\n".join(lines) + f"\n\n**Total:** {len(SUDO_USERS)}", parse_mode="Markdown")

# ---------------------------
# ADMIN MANAGEMENT COMMANDS
# ---------------------------
@sudo_only
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    promoter_bot = context.bot
    promoter_id = promoter_bot.id
    other_bots = [b for b in bots if b.id != promoter_id]
    if not other_bots:
        return await update.message.reply_text("❌ No other bots found to promote!")
    permissions = {
        'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True,
        'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True,
        'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True,
        'can_manage_chat': True
    }
    promoted_count = 0
    status_msg = await update.message.reply_text("🔄 Promoting bots to admin... Please wait.")
    for bot in other_bots:
        try:
            await promoter_bot.promote_chat_member(chat_id=chat_id, user_id=bot.id, **permissions)
            promoted_count += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            logging.warning(f"Failed to promote bot {bot.id}: {e}")
    if promoted_count > 0:
        await status_msg.edit_text(f"✅ Successfully promoted {promoted_count} bot(s) to admin!")
    else:
        await status_msg.edit_text("❌ Failed to promote any bots!\n\nMake sure the bot that received the /admin command has:\n• Admin privileges\n• 'Add New Admins' permission")

@sudo_only
async def checkadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    status_msg = await update.message.reply_text("🔄 Checking bot admin status...")
    admin_bots = []
    non_admin_bots = []
    for bot in bots:
        try:
            chat_member = await bot.get_chat_member(chat_id, bot.id)
            if chat_member.status in ['administrator', 'creator']:
                admin_bots.append(f"✅ {str(bot.id)[:10]}... - {chat_member.status}")
            else:
                non_admin_bots.append(f"❌ {str(bot.id)[:10]}... - {chat_member.status}")
        except Exception:
            non_admin_bots.append(f"⚠️ {str(bot.id)[:10]}... - Can't check")
    result = f"**📊 BOT ADMIN STATUS**\n\n"
    result += f"**Admins ({len(admin_bots)}):**\n" + "\n".join(admin_bots) if admin_bots else "No admin bots found"
    result += f"\n\n**Non-Admins ({len(non_admin_bots)}):**\n" + "\n".join(non_admin_bots[:10])
    if len(non_admin_bots) > 10:
        result += f"\n...and {len(non_admin_bots) - 10} more"
    await status_msg.edit_text(result, parse_mode="Markdown")

# ---------------------------
# LEAVE/BYE COMMANDS
# ---------------------------
@sudo_only
async def bye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    try:
        await update.message.delete()
    except Exception:
        pass
    leave_count = 0
    for bot in bots:
        try:
            await bot.leave_chat(chat_id)
            leave_count += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            logging.warning(f"Bot could not leave: {e}")
    print(f"👋 Bots left chat {chat_id}. Total left: {leave_count}/{len(bots)}")

# ---------------------------
# HELP COMMAND
# ---------------------------
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id):
        help_text = """
╔════════════════╗
         👑 𝗚𝗢𝗝𝗢 𝗘𝗥𝗔 👑
╚════════════════╝

        ⚡ 𝗚𝗢𝗟𝗗 𝟯𝗗 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 ⚡

╭━━━━━━━━━━━━╮
┃ ✅ 𝗕𝗢𝗧 𝗔𝗖𝗧𝗜𝗩𝗘       ┃
┃ ✅ 1. 𝗛𝗢𝗨𝗥 𝗦𝗬𝗦𝗧𝗘𝗠𝗦 ┃
╰━━━━━━━━━━━━╯
 ✦ 𝗡𝗢 𝗥𝗘𝗟𝗢𝗔𝗗 𝗡𝗖 𝗙𝗜𝗟𝗘 🦋
 
/hindinc   😂     /emonc😖       /nc1🟢
/ctnc   🤣      /engnc😑       /nc2🔴
/livenc 😛       /knc🥴        /anc🟡
/biharinc  🫣        /fnc😣        /nc3🟣
/chinesenc🤑        /nc4😵‍💫        /nc5⚫

 ✦ 𝗙𝗔𝗦𝗧 𝗦𝗣𝗘𝗘𝗗 𝗦𝗣𝗔𝗠 𝗦𝗬𝗦𝗧𝗘𝗠 🦋

/slide1 ---- /stopall
/slide2 ---- /stopnc           
/slide3 ---- /stopspam
/spam1 ---- /stopslide
/spam2 ---- /delay
/spam3 ---- /admin
/spam4 ---- /bye

 ✦ 𝗙𝗔𝗦𝗧 𝗦𝗣𝗘𝗘𝗗 𝗣𝗙𝗣 𝗟𝗢𝗢𝗣 🦋

/savephoto (reply to photo)
/startphoto     /addsudo
/stopphoto     /delsudo
/clearphotos   /sudos
       /listphotos

⚜️ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗚𝗢𝗝𝗢 𝗘𝗥𝗔 ⚜️                

"""
        await update.message.reply_text(help_text)
    else:
        await update.message.reply_text(" 𝗚𝗢𝗝𝗢 𝗣𝗔𝗣𝗔 𝗦𝗘 𝗦𝗨𝗗𝗢 𝗞𝗜 𝗕𝗛𝗜𝗞 𝗠𝗔𝗡𝗚 𝗥𝗡𝗗𝗜 😆")

# ---------------------------
# BOT SETUP
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    
    # NC Commands
    app.add_handler(CommandHandler("hindinc", hindinc))
    app.add_handler(CommandHandler("ctnc", ctnc))
    app.add_handler(CommandHandler("livenc", livenc))
    app.add_handler(CommandHandler("biharinc", biharinc))
    app.add_handler(CommandHandler("chinesenc", chinesenc))
    app.add_handler(CommandHandler("engnc", engnc))
    app.add_handler(CommandHandler("emonc", emonc))
    app.add_handler(CommandHandler("nc1", nc1))
    app.add_handler(CommandHandler("nc2", nc2))
    app.add_handler(CommandHandler("nc3", nc3))
    app.add_handler(CommandHandler("nc4", nc4))
    app.add_handler(CommandHandler("nc5", nc5))
    app.add_handler(CommandHandler("knc", knc))
    app.add_handler(CommandHandler("anc", anc))
    app.add_handler(CommandHandler("fnc", fnc))
    
    # Slide Commands
    app.add_handler(CommandHandler("slide1", slide1))
    app.add_handler(CommandHandler("slide2", slide2))
    app.add_handler(CommandHandler("slide3", slide3))

    
    # Spam Commands
    app.add_handler(CommandHandler("spam1", spam1))
    app.add_handler(CommandHandler("spam2", spam2))
    app.add_handler(CommandHandler("spam3", spam3))
    app.add_handler(CommandHandler("spam4", spam4))
   
    # Photo Commands
    app.add_handler(CommandHandler("savephoto", savephoto))
    app.add_handler(CommandHandler("startphoto", startphoto))
    app.add_handler(CommandHandler("stopphoto", stopphoto))
    app.add_handler(CommandHandler("clearphotos", clearphotos))
    app.add_handler(CommandHandler("listphotos", listphotos))
    
    # Stop Commands
    app.add_handler(CommandHandler("stopnc", stopnc))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("stopall", stopall))
    
    # Control Commands
    app.add_handler(CommandHandler("delay", delay))
    app.add_handler(CommandHandler("hi", hi))
    
    # Sudo Management
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("sudos", sudos))
    
    # Admin Management
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("checkadmin", checkadmin))
    
    # Leave
    app.add_handler(CommandHandler("bye", bye))
    
    # Help
    app.add_handler(CommandHandler("help", help_cmd))
    
    return app

async def run_all_bots():
    if not TOKENS:
        print("❌ No bot tokens added!")
        return
    
    for token in TOKENS:
        try:
            app = build_app(token)
            apps.append(app)
            bots.append(app.bot)
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Bot started: {token[:10]}...")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

    print(f"\n🐍 GOJO X BHAGWAN is running with {len(bots)} bots!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"⚡ Default delay: {GLOBAL_DELAY:.3f}s")
    print(f"📸 Photo Loop: ACTIVE")
    print("="*50)
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("      GOJO X BHAGWAN - MULTI BOT SYSTEM")
    print("="*50)
    
    print("\n✅ ACCESS GRANTED! INITIALIZING FREAKY HYDRA...\n")
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 GOJO stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")
