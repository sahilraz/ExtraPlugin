import aiohttp
import json
import random
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import filters
from ChampuMusic import app
from datetime import datetime
from io import BytesIO
from urllib.parse import quote

# Initialize scheduler
scheduler = AsyncIOScheduler()
scheduler.start()

# Auto tasks file path
AUTO_TASKS_FILE = "auto_tasks.json"

# Function to load auto tasks
def load_auto_tasks():
    try:
        with open(AUTO_TASKS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"auto_like": {}, "auto_spam": {}}

# Function to save auto tasks
def save_auto_tasks(data):
    with open(AUTO_TASKS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Function to get random time between 6 AM to 10 AM
def get_random_time():
    random_hour = random.randint(6, 9)
    random_minute = random.randint(0, 59)
    return time(hour=random_hour, minute=random_minute)

# Schedule daily auto tasks
async def schedule_daily_tasks():
    tasks_data = load_auto_tasks()
    
    # Schedule auto likes
    for uid, info in tasks_data["auto_like"].items():
        scheduler.add_job(
            auto_like_task,
            'cron',
            hour=get_random_time().hour,
            minute=get_random_time().minute,
            args=[uid, info["region"], info["user_id"]]
        )
    
    # Schedule auto spam
    for uid, info in tasks_data["auto_spam"].items():
        scheduler.add_job(
            auto_spam_task,
            'cron',
            hour=get_random_time().hour,
            minute=get_random_time().minute,
            args=[uid, info["region"], info["user_id"]]
        )

# Auto like task function
async def auto_like_task(uid, region, user_id):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_ENDPOINTS['GIVE_LIKES']}?uid={uid}&region={region}"
            async with session.get(url) as response:
                data = await response.json()
                
        likes_data = data.get("likes", {})
        
        # Format response message
        if "error" in likes_data:
            response_msg = f"❌ ᴀᴜᴛᴏ ʟɪᴋᴇ ғᴀɪʟᴇᴅ ғᴏʀ ᴜɪᴅ {uid}: {likes_data['error']}"
        else:
            region_name = REGION_NAMES.get(likes_data["region"], likes_data["region"])
            response_msg = MESSAGES["SUCCESS"].format(
                nickname=likes_data["nickname"],
                region_name=region_name,
                likes_before="{:,}".format(int(likes_data["likes_before"])),
                likes_after="{:,}".format(int(likes_data["likes_after"])),
                likes_given=likes_data["likes_given"]
            )
        
        # Send response to user
        await app.send_message(user_id, response_msg)
        
    except Exception as e:
        await app.send_message(user_id, f"❌ ᴀᴜᴛᴏ ʟɪᴋᴇ ᴇʀʀᴏʀ ғᴏʀ ᴜɪᴅ {uid}: {str(e)}")

# Auto spam task function
async def auto_spam_task(uid, region, user_id):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_ENDPOINTS['SPAM_FRIEND']}?uid={uid}&region={region}"
            async with session.get(url) as response:
                data = await response.json()
                
        spam_info = data.get("spaminfo", {})
        
        # Format response message
        if "error" in spam_info:
            response_msg = f"❌ ᴀᴜᴛᴏ sᴘᴀᴍ ғᴀɪʟᴇᴅ ғᴏʀ ᴜɪᴅ {uid}: {spam_info['error']}"
        else:
            response_msg = MESSAGES["SPAM_SUCCESS"].format(
                nickname=spam_info["nickname"],
                region_name=REGION_NAMES.get(spam_info["region"], spam_info["region"]),
                totalspam=spam_info["totalspam"]
            )
        
        # Send response to user
        await app.send_message(user_id, response_msg)
        
    except Exception as e:
        await app.send_message(user_id, f"❌ ᴀᴜᴛᴏ sᴘᴀᴍ ᴇʀʀᴏʀ ғᴏʀ ᴜɪᴅ {uid}: {str(e)}")

# API Endpoints
API_BASE_URL = "https://ff-spy.onrender.com"
API_ENDPOINTS = {
    "GIVE_LIKES": f"{API_BASE_URL}/givelikes",
    "CHECK_BAN": f"{API_BASE_URL}/isbanned",
    "SEARCH": f"{API_BASE_URL}/fuzzysearch",
    "SPAM_FRIEND": f"{API_BASE_URL}/spamfriend",
    "TOKEN_STATUS": f"{API_BASE_URL}/tokenstatus",
    "RELOAD_TOKEN": f"{API_BASE_URL}/reloadtoken",
    "GET_INFO": f"{API_BASE_URL}/getinfo",
    "GEN_PROFILE_IMG": f"{API_BASE_URL}/genprofileimg"
}

# Loading message format
LOADING_MESSAGE = "**ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ... ⏳**"

# Response message formats
MESSAGES = {
    "SUCCESS": """**✦ ʜᴇʀᴇ's ʏᴏᴜʀ ʟɪᴋᴇs ʀᴇᴘᴏʀᴛ 💖**

⭒ ɴɪᴄᴋɴᴀᴍᴇ: {nickname}
⭒ ʀᴇɢɪᴏɴ: {region_name}

╭─ **🅛🅘🅚🅔 🅢🅣🅐🅣🅢** ─╮
┃ 💫 ʙᴇꜰᴏʀᴇ: {likes_before}
┃ 💞 ᴀꜰᴛᴇʀ: {likes_after}
┃ 🎁 ɢɪᴠᴇɴ: {likes_given}
╰────────────────╯

ꜱᴛᴀʏ ᴀᴡᴇꜱᴏᴍᴇ 💌""",

    "MAX_LIKES": """**✦ ʜєʏ {nickname} ✦**

──────────────────────────
**❗ ᴛʜɪs ɪᴅ ʜᴀs ʀᴇᴄᴇɪᴠᴇᴅ ᴀʟʟ ʟɪᴋᴇs ғᴏʀ ᴛᴏᴅᴀʏ! ❗**
──────────────────────────

⌛ ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ ᴛᴏ ᴅɪꜱʜ ᴍᴏʀᴇ ʟᴏᴠᴇ! 💖""",

    "INVALID_UID": "❌ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴜɪᴅ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ ᴏʀ ɪs ɪɴᴠᴀʟɪᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴡɪᴛʜ ᴀ ᴅɪғғᴇʀᴇɴᴛ ᴜɪᴅ.",
    
    "MISSING_ARGS_LIKE": """❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /like [region] [uid]
ʀᴇɢɪᴏɴs: ɪɴᴅ/ᴇᴜ
ᴇxᴀᴍᴘʟᴇ: /like ind 123456789""",

    "MISSING_ARGS_BAN": """❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /banned [uid]
ᴇxᴀᴍᴘʟᴇ: /banned 123456789""",

    "INVALID_REGION": "❌ ɪɴᴠᴀʟɪᴅ ʀᴇɢɪᴏɴ! ᴏɴʟʏ 'ɪɴᴅ' ᴀɴᴅ 'ᴇᴜ' ᴀʀᴇ sᴜᴘᴘᴏʀᴛᴇᴅ.",

    "NOT_BANNED": """╭───── **ʙᴀɴ sᴛᴀᴛᴜs** ────╮
┃ ᴜɪᴅ: {uid}
┃ sᴛᴀᴛᴜs: **ɴᴏᴛ ʙᴀɴɴᴇᴅ** ✅
╰─────────────────╯

🎉 ʏᴏᴜ'ʀᴇ ᴀʟʟ ᴄʟᴇᴀʀ! ᴋᴇᴇᴘ ᴇɴᴊᴏʏɪɴɢ! 🟢""",

    "BANNED": """╭───── **ʙᴀɴ sᴛᴀᴛᴜs** ────╮
┃ ᴜɪᴅ: {uid}
┃ sᴛᴀᴛᴜs: **ʙᴀɴɴᴇᴅ** 🚫
╰─────────────────╯

💔 ᴛʜɪs ᴀᴄᴄᴏᴜɴᴛ ʜᴀs ʙᴇᴇɴ ʟᴏsᴛ ᴛᴏ ᴛʜᴇ ᴠᴏɪᴅ... 
⚰️ ᴛʜᴇʀᴇ's ɴᴏ ᴄᴏᴍɪɴɢ ʙᴀᴄᴋ.""",

    # Search command messages
    "MISSING_ARGS_SEARCH": """❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /search [name]
ᴇxᴀᴍᴘʟᴇ: /search devil""",

    "SEARCH_ERROR_401": """❌ sᴇᴀʀᴄʜ ᴇʀʀᴏʀ

ᴀᴘɪ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.""",

    "INVALID_NAME_LENGTH": """❌ ɪɴᴠᴀʟɪᴅ ɴᴀᴍᴇ ʟᴇɴɢᴛʜ

ɴᴀᴍᴇ ᴍᴜsᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 3 ᴀɴᴅ 12 ᴄʜᴀʀᴀᴄᴛᴇʀs ʟᴏɴɢ.""",
    
    "NO_RESULTS": "❌ ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ.",
    
    "SEARCH_RESULTS": """**✦ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ "{query}" ✦**

ғᴏᴜɴᴅ {count} ᴍᴀᴛᴄʜᴇs:

{results}

ᴘᴀɢᴇ: {current_page}/{total_pages}""",

    # Spam friend command messages
    "SPAM_SUCCESS": """**✦ ꜰʀɪᴇɴᴅ ʀᴇǫᴜᴇsᴛ sᴘᴀᴍ ʀᴇᴘᴏʀᴛ 💫**

⭒ ɴɪᴄᴋɴᴀᴍᴇ: {nickname}
⭒ ʀᴇɢɪᴏɴ: {region_name}

╭─ **🅢🅟🅐🅜 🅢🅣🅐🅣🅢** ─╮
┃ 📨 ᴛᴏᴛᴀʟ sᴘᴀᴍ: {totalspam}
╰────────────────╯

✨ sᴘᴀᴍ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!""",

    "SPAM_MAX_REACHED": """**✦ ꜰʀɪᴇɴᴅ ʀᴇǫᴜᴇsᴛ sᴘᴀᴍ ʀᴇᴘᴏʀᴛ ⚠️**

⭒ ɴɪᴄᴋɴᴀᴍᴇ: {nickname}
⭒ ʀᴇɢɪᴏɴ: {region_name}

**❗ᴍᴀxɪᴍᴜᴍ sᴘᴀᴍ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ**
⌛ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!""",

    "MISSING_ARGS_SPAM": """❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /spamf [region] [uid]
ʀᴇɢɪᴏɴs: ɪɴᴅ/ᴇᴜ
ᴇxᴀᴍᴘʟᴇ: /spamf ind 123456789""",

    "INVALID_SPAM_UID": "❌ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴜɪᴅ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ ᴏʀ ɪs ɪɴᴠᴀʟɪᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴡɪᴛʜ ᴀ ᴅɪғғᴇʀᴇɴᴛ ᴜɪᴅ.",

    # Token status messages
    "TOKEN_STATUS_HEADER": """**✦ ᴛᴏᴋᴇɴ sᴛᴀᴛᴜs ʀᴇᴘᴏʀᴛ ✦**
ʟᴀsᴛ ᴜᴘᴅᴀᴛᴇᴅ: {last_updated}

""",
    
    "TOKEN_STATUS_REGION": """╭── {region_name} ──╮
┃ sᴛᴀᴛᴜs: {status}
┃ ᴛᴏᴋᴇɴs: {token_count}
{expiry_info}╰─────────────╯

""",

    # Token reload messages
    "TOKEN_RELOAD_SUCCESS": """**✦ ᴛᴏᴋᴇɴ ʀᴇʟᴏᴀᴅ ʀᴇᴘᴏʀᴛ ✦**

{message}

╭── **ʀᴇʟᴏᴀᴅ ᴅᴇᴛᴀɪʟs** ──╮
┃ 🔄 ʟᴏᴀᴅᴇᴅ ʀᴇɢɪᴏɴs: {regions}
┃ 🎫 ᴛᴏᴛᴀʟ ᴛᴏᴋᴇɴs: {total}
┃ ⏰ ᴛɪᴍᴇsᴛᴀᴍᴘ: {timestamp}
╰─────────────────╯""",

    # Get info messages
    "GET_INFO_ERROR": "❌ **ᴇʀʀᴏʀ:** {error}",
    
    "GET_INFO_SUCCESS": """**✦ ᴀᴄᴄᴏᴜɴᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ✦**

╭───── **ʙᴀsɪᴄ ɪɴғᴏ** ─────╮
┃ 👤 ɴᴀᴍᴇ: `{nickname}`
┃ 🆔 ᴜɪᴅ: `{uid}`
┃ 📊 ʟᴇᴠᴇʟ: {level} (ᴇxᴘ: {exp})
┃ 🌍 ʀᴇɢɪᴏɴ: {region}
┃ ❤️ ʟɪᴋᴇs: {likes}
┃ 🏅 ʜᴏɴᴏʀ sᴄᴏʀᴇ: {honor_score}
┃ 👑 ᴄᴇʟᴇʙʀɪᴛʏ sᴛᴀᴛᴜs: {celebrity}
┃ 🎯 ᴇᴠᴏ ᴀᴄᴄᴇss: {evo_access}
┃ 🏆 ᴛɪᴛʟᴇ: {title}
┃ ✒️ sɪɢɴᴀᴛᴜʀᴇ: `{signature}`
╰────────────────────╯

╭──── **ᴀᴄᴛɪᴠɪᴛʏ** ────╮
┃ 🔄 ᴏʙ ᴠᴇʀsɪᴏɴ: {ob_version}
┃ 🎫 ғɪʀᴇ ᴘᴀss: {fire_pass}
┃ 🎖️ ʙᴘ ʙᴀᴅɢᴇs: {bp_badges}
┃ 🏆 ʙʀ ʀᴀɴᴋ: {br_rank} ({br_points})
┃ ⚔️ ᴄs ᴘᴏɪɴᴛs: {cs_points}
┃ 📅 ᴄʀᴇᴀᴛᴇᴅ: {created_at}
┃ ⏳ ʟᴀsᴛ ʟᴏɢɪɴ: {last_login}
╰────────────────────╯

╭──── **ᴏᴠᴇʀᴠɪᴇᴡ** ────╮
┃ 🎭 ᴀᴠᴀᴛᴀʀ ɪᴅ: {avatar_id}
┃ 🎨 ʙᴀɴɴᴇʀ ɪᴅ: {banner_id}
┃ 📌 ᴘɪɴ ɪᴅ: {pin_id}
┃ ⚡ sᴋɪʟʟs: {skills}
┃ 🔫 ᴇǫᴜɪᴘᴘᴇᴅ ɢᴜɴ: {gun_id}
┃ 🎬 ᴀɴɪᴍᴀᴛɪᴏɴ ɪᴅ: {anim_id}
┃ 🔄 ᴛʀᴀɴsғᴏʀᴍ ɪᴅ: {transform_id}
╰────────────────────╯

╭───── **ᴘᴇᴛ ɪɴғᴏ** ─────╮
┃ ✅ ᴇǫᴜɪᴘᴘᴇᴅ: {pet_equipped}
┃ 🦊 ᴘᴇᴛ ɴᴀᴍᴇ: {pet_name}
┃ 🐾 ᴘᴇᴛ ᴛʏᴘᴇ: {pet_type}
┃ 🌟 ᴘᴇᴛ ᴇxᴘ: {pet_exp}
┃ 📈 ᴘᴇᴛ ʟᴇᴠᴇʟ: {pet_level}
╰────────────────────╯

╭───── **ɢᴜɪʟᴅ ɪɴғᴏ** ─────╮
┃ 🏰 ɢᴜɪʟᴅ ɴᴀᴍᴇ: {guild_name}
┃ 🆔 ɢᴜɪʟᴅ ɪᴅ: `{guild_id}`
┃ 🎖️ ɢᴜɪʟᴅ ʟᴇᴠᴇʟ: {guild_level}
┃ 👥 ᴍᴇᴍʙᴇʀs: {members}/{capacity}
┃
┃ 👑 **ʟᴇᴀᴅᴇʀ ɪɴғᴏ:**
┃ ├─ 👤 ɴᴀᴍᴇ: `{leader_name}`
┃ ├─ 🆔 ᴜɪᴅ: `{leader_uid}`
┃ ├─ 📊 ʟᴇᴠᴇʟ: {leader_level}
┃ ├─ 🎖️ ʙᴘ ʙᴀᴅɢᴇs: {leader_badges}
┃ ├─ 🏆 ʙʀ ᴘᴏɪɴᴛs: {leader_br}
┃ ├─ ⚔️ ᴄs ᴘᴏɪɴᴛs: {leader_cs}
┃ └─ ⏳ ʟᴀsᴛ ʟᴏɢɪɴ: {leader_login}
╰────────────────────╯"""
}

REGION_NAMES = {
    "IND": "ɪηɗɪɐ",
    "EU": "Ɛυʀοƿℯ"
}

@app.on_message(filters.command("like"))
async def give_likes(_, message):
    loading_msg = None
    try:
        loading_msg = await message.reply_text(LOADING_MESSAGE)
        # Split command arguments
        args = message.text.split()
        
        # Check if all required arguments are provided
        if len(args) != 3:
            return await message.reply_text(MESSAGES["MISSING_ARGS_LIKE"])
        
        # Extract region and UID
        region = args[1].lower()
        uid = args[2]
        
        # Validate region
        if region not in ['ind', 'eu']:
            return await message.reply_text(MESSAGES["INVALID_REGION"])
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            url = f"{API_ENDPOINTS['GIVE_LIKES']}?uid={uid}&region={region}"
            async with session.get(url) as response:
                data = await response.json()
                
        likes_data = data.get("likes", {})
        
        # Handle different response types
        if "error" in likes_data:
            error_msg = likes_data["error"]
            if "UID_LIKE_REGION_NOT_FOUND" in error_msg:
                await message.reply_text(MESSAGES["INVALID_UID"])
            elif "received all available likes" in error_msg:
                nickname = likes_data.get("nickname", "ᴜsᴇʀ")
                await message.reply_text(MESSAGES["MAX_LIKES"].format(nickname=nickname))
            else:
                await message.reply_text(f"❌ ᴇʀʀᴏʀ: {error_msg}")
        else:
            # Format successful response
            region_name = REGION_NAMES.get(likes_data["region"], likes_data["region"])
            await message.reply_text(
                MESSAGES["SUCCESS"].format(
                    nickname=likes_data["nickname"],
                    region_name=region_name,
                    likes_before="{:,}".format(int(likes_data["likes_before"])),
                    likes_after="{:,}".format(int(likes_data["likes_after"])),
                    likes_given=likes_data["likes_given"]
                )
            )
            
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")
    finally:
        if loading_msg:
            await loading_msg.delete()

@app.on_message(filters.command("banned"))
async def check_ban(_, message):
    loading_msg = None
    try:
        loading_msg = await message.reply_text(LOADING_MESSAGE)
        # Split command arguments
        args = message.text.split()
        
        # Check if UID is provided
        if len(args) != 2:
            return await message.reply_text(MESSAGES["MISSING_ARGS_BAN"])
        
        uid = args[1]
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            url = f"{API_ENDPOINTS['CHECK_BAN']}?uid={uid}"
            async with session.get(url) as response:
                data = await response.json()
                
        ban_info = data.get("BannedInfo", "")
        
        # Check ban status and format response
        if "not banned" in ban_info.lower():
            await message.reply_text(MESSAGES["NOT_BANNED"].format(uid=uid))
        elif "banned" in ban_info.lower():
            await message.reply_text(MESSAGES["BANNED"].format(uid=uid))
        else:
            await message.reply_text(f"❌ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ʀᴇsᴘᴏɴsᴇ: {ban_info}")
            
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")
    finally:
        if loading_msg:
            await loading_msg.delete()

@app.on_message(filters.command("search"))
async def search_players(_, message):
    loading_msg = None
    try:
        loading_msg = await message.reply_text(LOADING_MESSAGE)
        # Split command arguments
        args = message.text.split()
        
        # Check if name is provided
        if len(args) < 2:
            return await message.reply_text(MESSAGES["MISSING_ARGS_SEARCH"])
        
        # Extract name (combine all args after command)
        name = " ".join(args[1:])
        
        # Validate name length
        if not 3 <= len(name) <= 12:
            return await message.reply_text(MESSAGES["INVALID_NAME_LENGTH"])
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            url = f"{API_ENDPOINTS['SEARCH']}?name={name}"
            async with session.get(url) as response:
                data = await response.json()
                
        # Handle specific error cases
        if not data.get("success", False):
            error_msg = data.get("error", "Unknown error")
            if "401" in error_msg:
                return await message.reply_text(MESSAGES["SEARCH_ERROR_401"])
            elif "between 3 and 12 characters" in error_msg:
                return await message.reply_text(MESSAGES["INVALID_NAME_LENGTH"])
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ: {error_msg}")
        
        results = data.get("result", [])
        if not results:
            return await message.reply_text(MESSAGES["NO_RESULTS"])
        
        # Format results with pagination (10 results per page)
        PAGE_SIZE = 10
        total_results = len(results)
        total_pages = (total_results + PAGE_SIZE - 1) // PAGE_SIZE
        
        for page in range(total_pages):
            start_idx = page * PAGE_SIZE
            end_idx = min((page + 1) * PAGE_SIZE, total_results)
            page_results = results[start_idx:end_idx]
            
            formatted_results = []
            for idx, player in enumerate(page_results, start=start_idx + 1):
                # Convert lastLogin to readable format
                from datetime import datetime
                last_login = datetime.fromtimestamp(player["lastLogin"]).strftime("%d-%m-%Y")
                
                formatted_results.append(
                    f"""╭─────── ᴘʟᴀʏᴇʀ {idx} ───────╮
┃ 🆔 ᴜɪᴅ: {player["accountId"]}
┃ 👤 ɴᴀᴍᴇ: {player["nickname"].replace("\\t", " ")}
┃ 🌍 ʀᴇɢɪᴏɴ: {player["region"]}
┃ 📊 ʟᴇᴠᴇʟ: {player["level"]}
┃ 📅 ʟᴀsᴛ ʟᴏɢɪɴ: {last_login}
╰────────────────────╯"""
                )
            
            result_text = MESSAGES["SEARCH_RESULTS"].format(
                query=name,
                count=total_results,
                results="\n".join(formatted_results),
                current_page=page + 1,
                total_pages=total_pages
            )
            
            await message.reply_text(result_text)
            
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")
    finally:
        if loading_msg:
            await loading_msg.delete()

@app.on_message(filters.command("spamf"))
async def spam_friend(_, message):
    loading_msg = None
    try:
        loading_msg = await message.reply_text(LOADING_MESSAGE)
        # Split command arguments
        args = message.text.split()
        
        # Check if all required arguments are provided
        if len(args) != 3:
            return await message.reply_text(MESSAGES["MISSING_ARGS_SPAM"])
        
        # Extract region and UID
        region = args[1].upper()
        uid = args[2]
        
        # Validate region
        if region not in ['IND', 'EU']:
            return await message.reply_text(MESSAGES["INVALID_REGION"])
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            url = f"{API_ENDPOINTS['SPAM_FRIEND']}?uid={uid}&region={region}"
            async with session.get(url) as response:
                data = await response.json()
                
        # Handle error cases
        if "error" in data:
            error_msg = data["error"]
            if "Invalid region" in error_msg:
                return await message.reply_text(MESSAGES["INVALID_REGION"])
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ: {error_msg}")
        
        spam_info = data.get("spaminfo", {})
        
        # Handle different response types
        if "error" in spam_info:
            error_msg = spam_info["error"]
            if "UID_SPAM_REGION_NOT_FOUND" in error_msg:
                return await message.reply_text(MESSAGES["INVALID_SPAM_UID"])
            return await message.reply_text(f"❌ ᴇʀʀᴏʀ: {error_msg}")
        
        # Check if maximum spam limit reached
        if spam_info.get("totalspam", 0) == 0:
            return await message.reply_text(
                MESSAGES["SPAM_MAX_REACHED"].format(
                    nickname=spam_info["nickname"],
                    region_name=REGION_NAMES.get(spam_info["region"], spam_info["region"])
                )
            )
        
        # Format successful response
        await message.reply_text(
            MESSAGES["SPAM_SUCCESS"].format(
                nickname=spam_info["nickname"],
                region_name=REGION_NAMES.get(spam_info["region"], spam_info["region"]),
                totalspam=spam_info["totalspam"]
            )
        )
            
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")
    finally:
        if loading_msg:
            await loading_msg.delete()

@app.on_message(filters.command("tokenstatus"))
async def token_status(_, message):
    loading_msg = None
    try:
        loading_msg = await message.reply_text(LOADING_MESSAGE)
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            url = API_ENDPOINTS['TOKEN_STATUS']
            async with session.get(url) as response:
                data = await response.json()
                
        if not data.get("success", False):
            return await message.reply_text("❌ ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ᴛᴏᴋᴇɴ sᴛᴀᴛᴜs")
        
        # Start building response message
        response_text = MESSAGES["TOKEN_STATUS_HEADER"].format(
            last_updated=data["lastUpdated"]
        )
        
        # Process each region
        for region, info in data["regions"].items():
            expiry_info = ""
            if info["status"] == "✅ VALID":
                expiry_info = f"""┃ ᴇxᴘɪʀᴇs: {info['expiresAt']}
┃ ᴛɪᴍᴇ ʟᴇғᴛ: {info['timeRemaining']}
┃ ɴᴇxᴛ ᴜᴘᴅᴀᴛᴇ: {info['nextUpdateIn']}"""
            
            response_text += MESSAGES["TOKEN_STATUS_REGION"].format(
                region_name=region,
                status=info["status"],
                token_count=info["tokenCount"],
                expiry_info=f"{expiry_info}\n" if expiry_info else ""
            )
        
        await message.reply_text(response_text.strip())
            
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")
    finally:
        if loading_msg:
            await loading_msg.delete()

@app.on_message(filters.command("reloadtoken"))
async def reload_token(_, message):
    loading_msg = None
    try:
        loading_msg = await message.reply_text(LOADING_MESSAGE)
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            url = API_ENDPOINTS['RELOAD_TOKEN']
            async with session.get(url) as response:
                data = await response.json()
                
        if not data.get("success", False):
            return await message.reply_text("❌ ᴇʀʀᴏʀ ʀᴇʟᴏᴀᴅɪɴɢ ᴛᴏᴋᴇɴs")
        
        # Format the loaded regions list
        loaded_regions = ", ".join(data["loadedRegions"])
        
        # Build and send response
        response_text = MESSAGES["TOKEN_RELOAD_SUCCESS"].format(
            message=data["message"],
            regions=loaded_regions,
            total=data["totalTokens"],
            timestamp=data["timestamp"]
        )
        
        await message.reply_text(response_text)
            
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")
    finally:
        if loading_msg:
            await loading_msg.delete()

@app.on_message(filters.command(["get", "GET"], prefixes=["/", ""]))
async def get_info(_, message):
    loading_msg = None
    try:
        loading_msg = await message.reply_text(LOADING_MESSAGE)
        
        # Split command arguments
        args = message.text.split()
        
        # Check if UID is provided
        if len(args) != 2:
            return await message.reply_text("❌ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜɪᴅ\n\nᴇxᴀᴍᴘʟᴇ: `/get 123456789`")
        
        uid = args[1]
        
        # Make API request
        async with aiohttp.ClientSession() as session:
            url = f"{API_ENDPOINTS['GET_INFO']}/{uid}"
            async with session.get(url) as response:
                data = await response.json()
                
        # Check for error response
        if "error" in data:
            return await message.reply_text(MESSAGES["GET_INFO_ERROR"].format(error=data["error"]))
        
        # Extract account info
        account_info = data.get("accountInfo", {})
        basic_info = account_info.get("basicInfo", {})
        profile_info = account_info.get("profileInfo", {})
        clan_info = account_info.get("clanBasicInfo", {})
        captain_info = account_info.get("captainBasicInfo", {})
        pet_info = account_info.get("petInfo", {})
        social_info = account_info.get("socialInfo", {})
        honour_info = account_info.get("HonourScoreInfo", {})
        
        # Convert timestamps
        created_at = datetime.fromtimestamp(basic_info.get("createAt", 0)).strftime("%d %B %Y at %H:%M:%S")
        last_login = datetime.fromtimestamp(basic_info.get("lastLoginAt", 0)).strftime("%d %B %Y at %H:%M:%S")
        leader_login = datetime.fromtimestamp(captain_info.get("lastLoginAt", 0)).strftime("%d %B %Y at %H:%M:%S") if captain_info else "N/A"
        
        # Get equipped skills
        equipped_skills = profile_info.get("EquippedSkills", [])
        skills_text = ", ".join(str(skill["skill"]) for skill in equipped_skills) if equipped_skills else "N/A"
        
        # Determine celebrity status and evo access
        celebrity_status = "True" if basic_info.get("showRank", 0) == 1 else "False"
        evo_access = "Active" if basic_info.get("badgeId", 0) > 0 else "Inactive"
        
        # Determine fire pass type
        fire_pass = "Premium" if basic_info.get("badgeCnt", 0) > 0 else "Basic"
        
        # Format BR rank
        br_points = basic_info.get("BRPoints", 0)
        br_rank = "Bronze 1" if br_points <= 1200 else "N/A"  # Add more rank logic as needed
        
        # Format response
        response_text = MESSAGES["GET_INFO_SUCCESS"].format(
            nickname=basic_info.get("nickname", "N/A"),
            uid=basic_info.get("accountId", "N/A"),
            level=basic_info.get("level", "N/A"),
            exp=basic_info.get("exp", "N/A"),
            region=basic_info.get("region", "N/A"),
            likes=basic_info.get("likes", "N/A"),
            honor_score=honour_info.get("HonourScore", "N/A"),
            celebrity=celebrity_status,
            evo_access=evo_access,
            title=basic_info.get("title", "N/A"),
            signature=social_info.get("signature", "N/A"),
            ob_version=basic_info.get("OBVersion", "N/A"),
            fire_pass=fire_pass,
            bp_badges=basic_info.get("badgeCnt", "N/A"),
            br_rank=br_rank,
            br_points=br_points,
            cs_points=basic_info.get("csRankingPoints", "N/A"),
            created_at=created_at,
            last_login=last_login,
            avatar_id=basic_info.get("avatarId", "N/A"),
            banner_id=basic_info.get("bannerId", "N/A"),
            pin_id=basic_info.get("PinId", "N/A"),
            skills=skills_text,
            gun_id="N/A",  # Add if available in API
            anim_id="N/A",  # Add if available in API
            transform_id="N/A",  # Add if available in API
            pet_equipped="Yes" if pet_info.get("isSelected", 0) == 1 else "No",
            pet_name=pet_info.get("name", "N/A"),
            pet_type="hawk" if pet_info.get("id") == 1300000091 else str(pet_info.get("id", "N/A")),
            pet_exp=pet_info.get("exp", "N/A"),
            pet_level=pet_info.get("level", "N/A"),
            guild_name=clan_info.get("clanName", "N/A"),
            guild_id=clan_info.get("clanId", "N/A"),
            guild_level=clan_info.get("clanLevel", "N/A"),
            members=clan_info.get("memberNum", "N/A"),
            capacity=clan_info.get("capacity", "N/A"),
            leader_name=captain_info.get("nickname", "N/A"),
            leader_uid=captain_info.get("accountId", "N/A"),
            leader_level=captain_info.get("level", "N/A"),
            leader_badges=captain_info.get("badgeCnt", "N/A"),
            leader_br=captain_info.get("rank", "N/A"),
            leader_cs=captain_info.get("csRankingPoints", "N/A"),
            leader_login=leader_login
        )
        
        await message.reply_text(response_text)
        
        # Generate and send profile image
        try:
            # Create a new session specifically for image download
            async with aiohttp.ClientSession() as img_session:
                # Get guild name, use empty string if not in a guild
                guild_name = clan_info.get("clanName", "").strip()
                
                # URL encode the parameters to handle special characters
                from urllib.parse import quote
                
                image_url = (
                    f"{API_ENDPOINTS['GEN_PROFILE_IMG']}"
                    f"?avatarId={basic_info.get('avatarId', 'default')}"
                    f"&bannerId={basic_info.get('bannerId', 'default')}"
                    f"&pinId={basic_info.get('PinId', 'default')}"
                    f"&uid={uid}"
                    f"&nickname={quote(basic_info.get('nickname', ''))}"
                    f"&guildName={quote(guild_name)}"
                    f"&level={basic_info.get('level', '')}"
                    f"&isverified=0"
                )
                
                async with img_session.get(image_url) as img_response:
                    if img_response.status == 200:
                        img_data = await img_response.read()
                        img_bytes = BytesIO(img_data)
                        img_bytes.name = "profile.webp"
                        img_bytes.seek(0)
                        
                        await message.reply_document(img_bytes)
                    else:
                        await message.reply_text("⚠️ ғᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴘʀᴏғɪʟᴇ ɪᴍᴀɢᴇ")
        except Exception as e:
            await message.reply_text(f"⚠️ ᴇʀʀᴏʀ ɢᴇɴᴇʀᴀᴛɪɴɢ ᴘʀᴏғɪʟᴇ ɪᴍᴀɢᴇ: {str(e)}")
            
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")
    finally:
        if loading_msg:
            await loading_msg.delete()

@app.on_message(filters.command("autolike"))
async def auto_like(_, message):
    try:
        # Split command arguments
        args = message.text.split()
        
        # Check if all required arguments are provided
        if len(args) != 3:
            return await message.reply_text("""❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /autolike [region] [uid]
ʀᴇɢɪᴏɴs: ɪɴᴅ/ᴇᴜ
ᴇxᴀᴍᴘʟᴇ: /autolike ind 123456789""")
        
        # Extract region and UID
        region = args[1].lower()
        uid = args[2]
        
        # Validate region
        if region not in ['ind', 'eu']:
            return await message.reply_text(MESSAGES["INVALID_REGION"])
        
        # Load current auto tasks
        tasks_data = load_auto_tasks()
        
        # Add new auto like task
        tasks_data["auto_like"][uid] = {
            "region": region,
            "user_id": message.from_user.id,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save updated tasks
        save_auto_tasks(tasks_data)
        
        # Schedule the task
        random_time = get_random_time()
        scheduler.add_job(
            auto_like_task,
            'cron',
            hour=random_time.hour,
            minute=random_time.minute,
            args=[uid, region, message.from_user.id]
        )
        
        await message.reply_text(f"""✅ **ᴀᴜᴛᴏ ʟɪᴋᴇ ᴛᴀsᴋ ᴀᴅᴅᴇᴅ**

• ᴜɪᴅ: {uid}
• ʀᴇɢɪᴏɴ: {region.upper()}
• sᴄʜᴇᴅᴜʟᴇᴅ: ᴅᴀɪʟʏ ᴀᴛ ʀᴀɴᴅᴏᴍ ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ 6 ᴀᴍ - 10 ᴀᴍ""")
        
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")

@app.on_message(filters.command("autospam"))
async def auto_spam(_, message):
    try:
        # Split command arguments
        args = message.text.split()
        
        # Check if all required arguments are provided
        if len(args) != 3:
            return await message.reply_text("""❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /autospam [region] [uid]
ʀᴇɢɪᴏɴs: ɪɴᴅ/ᴇᴜ
ᴇxᴀᴍᴘʟᴇ: /autospam ind 123456789""")
        
        # Extract region and UID
        region = args[1].lower()
        uid = args[2]
        
        # Validate region
        if region not in ['ind', 'eu']:
            return await message.reply_text(MESSAGES["INVALID_REGION"])
        
        # Load current auto tasks
        tasks_data = load_auto_tasks()
        
        # Add new auto spam task
        tasks_data["auto_spam"][uid] = {
            "region": region,
            "user_id": message.from_user.id,
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save updated tasks
        save_auto_tasks(tasks_data)
        
        # Schedule the task
        random_time = get_random_time()
        scheduler.add_job(
            auto_spam_task,
            'cron',
            hour=random_time.hour,
            minute=random_time.minute,
            args=[uid, region, message.from_user.id]
        )
        
        await message.reply_text(f"""✅ **ᴀᴜᴛᴏ sᴘᴀᴍ ᴛᴀsᴋ ᴀᴅᴅᴇᴅ**

• ᴜɪᴅ: {uid}
• ʀᴇɢɪᴏɴ: {region.upper()}
• sᴄʜᴇᴅᴜʟᴇᴅ: ᴅᴀɪʟʏ ᴀᴛ ʀᴀɴᴅᴏᴍ ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ 6 ᴀᴍ - 10 ᴀᴍ""")
        
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")

@app.on_message(filters.command("autotasks"))
async def list_auto_tasks(_, message):
    try:
        # Load current auto tasks
        tasks_data = load_auto_tasks()
        
        # Format auto like tasks
        auto_like_text = "**ᴀᴜᴛᴏ ʟɪᴋᴇ ᴛᴀsᴋs:**\n\n"
        if tasks_data["auto_like"]:
            for uid, info in tasks_data["auto_like"].items():
                if info["user_id"] == message.from_user.id:
                    auto_like_text += f"""• ᴜɪᴅ: {uid}
• ʀᴇɢɪᴏɴ: {info['region'].upper()}
• ᴀᴅᴅᴇᴅ: {info['added_at']}\n\n"""
        else:
            auto_like_text += "ɴᴏ ᴀᴜᴛᴏ ʟɪᴋᴇ ᴛᴀsᴋs\n\n"
        
        # Format auto spam tasks
        auto_spam_text = "**ᴀᴜᴛᴏ sᴘᴀᴍ ᴛᴀsᴋs:**\n\n"
        if tasks_data["auto_spam"]:
            for uid, info in tasks_data["auto_spam"].items():
                if info["user_id"] == message.from_user.id:
                    auto_spam_text += f"""• ᴜɪᴅ: {uid}
• ʀᴇɢɪᴏɴ: {info['region'].upper()}
• ᴀᴅᴅᴇᴅ: {info['added_at']}\n\n"""
        else:
            auto_spam_text += "ɴᴏ ᴀᴜᴛᴏ sᴘᴀᴍ ᴛᴀsᴋs\n\n"
        
        await message.reply_text(f"{auto_like_text}{auto_spam_text}\n**ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀ ᴛᴀsᴋ, ᴜsᴇ:**\n/removeauto [like/spam] [uid]")
        
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")

@app.on_message(filters.command("removeauto"))
async def remove_auto_task(_, message):
    try:
        # Split command arguments
        args = message.text.split()
        
        # Check if all required arguments are provided
        if len(args) != 3:
            return await message.reply_text("""❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /removeauto [like/spam] [uid]
ᴇxᴀᴍᴘʟᴇ: /removeauto like 123456789""")
        
        # Extract task type and UID
        task_type = args[1].lower()
        uid = args[2]
        
        # Validate task type
        if task_type not in ['like', 'spam']:
            return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴛᴀsᴋ ᴛʏᴘᴇ! ᴜsᴇ 'like' ᴏʀ 'spam'")
        
        # Load current auto tasks
        tasks_data = load_auto_tasks()
        
        # Get the correct task dictionary
        task_dict = "auto_like" if task_type == "like" else "auto_spam"
        
        # Check if the task exists and belongs to the user
        if uid in tasks_data[task_dict]:
            if tasks_data[task_dict][uid]["user_id"] == message.from_user.id:
                # Remove the task
                del tasks_data[task_dict][uid]
                save_auto_tasks(tasks_data)
                
                # Remove the scheduled job
                for job in scheduler.get_jobs():
                    if job.args and job.args[0] == uid:
                        job.remove()
                
                await message.reply_text(f"✅ ᴀᴜᴛᴏ {task_type} ᴛᴀsᴋ ʀᴇᴍᴏᴠᴇᴅ ғᴏʀ ᴜɪᴅ: {uid}")
            else:
                await message.reply_text("❌ ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ʀᴇᴍᴏᴠᴇ ʏᴏᴜʀ ᴏᴡɴ ᴛᴀsᴋs!")
        else:
            await message.reply_text(f"❌ ɴᴏ ᴀᴜᴛᴏ {task_type} ᴛᴀsᴋ ғᴏᴜɴᴅ ғᴏʀ ᴜɪᴅ: {uid}")
        
    except Exception as e:
        await message.reply_text(f"❌ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ: {str(e)}")

# Schedule initial tasks on startup
@app.on_start()
async def start_schedule_daily_tasks(client):
    await schedule_daily_tasks()


__MODULE__ = "ꜰʀᴇᴇ ꜰɪʀᴇ"
__HELP__ = """
/like [region] [uid] - ɢɪᴠᴇ ʟɪᴋᴇs ᴛᴏ ᴀ ꜰʀᴇᴇ ꜰɪʀᴇ ᴘʀᴏꜰɪʟᴇ
/banned [uid] - ᴄʜᴇᴄᴋ ɪꜰ ᴀ ꜰʀᴇᴇ ꜰɪʀᴇ ᴜɪᴅ ɪs ʙᴀɴɴᴇᴅ
/search [name] - sᴇᴀʀᴄʜ ꜰᴏʀ ꜰʀᴇᴇ ꜰɪʀᴇ ᴘʟᴀʏᴇʀs ʙʏ ɴᴀᴍᴇ
/spamf [region] [uid] - sᴘᴀᴍ ꜰʀɪᴇɴᴅ ʀᴇǫᴜᴇsᴛs ᴛᴏ ᴀ ᴜsᴇʀ
/tokenstatus - ᴄʜᴇᴄᴋ ᴛʜᴇ sᴛᴀᴛᴜs ᴏғ ᴀʟʟ ʀᴇɢɪᴏɴ ᴛᴏᴋᴇɴs
/reloadtoken - ʀᴇʟᴏᴀᴅ ᴛᴏᴋᴇɴs ғᴏʀ ᴀʟʟ ʀᴇɢɪᴏɴs
/get [uid] - ɢᴇᴛ ᴅᴇᴛᴀɪʟᴇᴅ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴀ ᴘʟᴀʏᴇʀ

**ᴀᴜᴛᴏ ᴛᴀsᴋs:**
/autolike [region] [uid] - ᴀᴅᴅ ᴀ ᴜɪᴅ ᴛᴏ ᴅᴀɪʟʏ ᴀᴜᴛᴏ ʟɪᴋᴇ ʟɪsᴛ
/autospam [region] [uid] - ᴀᴅᴅ ᴀ ᴜɪᴅ ᴛᴏ ᴅᴀɪʟʏ ᴀᴜᴛᴏ sᴘᴀᴍ ʟɪsᴛ
/autotasks - ᴠɪᴇᴡ ʏᴏᴜʀ ᴀᴜᴛᴏ ᴛᴀsᴋs ʟɪsᴛ
/removeauto [like/spam] [uid] - ʀᴇᴍᴏᴠᴇ ᴀ ᴜɪᴅ ғʀᴏᴍ ᴀᴜᴛᴏ ᴛᴀsᴋs

ʀᴇɢɪᴏɴs: ɪɴᴅ/ᴇᴜ

ᴇxᴀᴍᴘʟᴇs:
• /like ind 123456789
• /banned 123456789
• /search devil
• /spamf ind 123456789
• /tokenstatus
• /reloadtoken
• /get 123456789
• /autolike ind 123456789
• /autospam ind 123456789
• /autotasks
• /removeauto like 123456789
""" 
