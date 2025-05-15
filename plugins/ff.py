import aiohttp
from pyrogram import filters
from DevilMusic import app

# API Endpoints
API_BASE_URL = "https://ff-spy.onrender.com"
API_ENDPOINTS = {
    "GIVE_LIKES": f"{API_BASE_URL}/givelikes",
    "CHECK_BAN": f"{API_BASE_URL}/isbanned",
    "SEARCH": f"{API_BASE_URL}/fuzzysearch",
    "SPAM_FRIEND": f"{API_BASE_URL}/spamfriend"
}

# Response message formats
MESSAGES = {
    "SUCCESS": """✦ ʜᴇʀᴇ'ꜱ ʏᴏᴜʀ ʟɪᴋᴇꜱ ʀᴇᴘᴏʀᴛ 💖

⭒ ɴɪᴄᴋɴᴀᴍᴇ: {nickname}
⭒ ʀᴇɢɪᴏɴ: {region_name}

╭─ 🅛🅘🅚🅔 🅢🅣🅐🅣🅢 ─╮
┃ 💫 ʙᴇꜰᴏʀᴇ: {likes_before}
┃ 💞 ᴀꜰᴛᴇʀ: {likes_after}
┃ 🎁 ɢɪᴠᴇɴ: {likes_given}
╰────────────────╯

ꜱᴛᴀʏ ᴀᴡᴇꜱᴏᴍᴇ 💌""",

    "MAX_LIKES": """✦ ʜєʏ {nickname} ✦

──────────────────────────
❗ ᴛʜɪs ɪᴅ ʜᴀs ʀᴇᴄᴇɪᴠᴇᴅ ᴀʟʟ ʟɪᴋᴇs ғᴏʀ ᴛᴏᴅᴀʏ! ❗
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

    "NOT_BANNED": """╭── ʙᴀɴ sᴛᴀᴛᴜs ──╮
┃ ᴜɪᴅ: {uid}
┃ sᴛᴀᴛᴜs: ɴᴏᴛ ʙᴀɴɴᴇᴅ ✅
╰─────────────────╯

🎉 ʏᴏᴜ'ʀᴇ ᴀʟʟ ᴄʟᴇᴀʀ! ᴋᴇᴇᴘ ᴇɴᴊᴏʏɪɴɢ! 🟢""",

    "BANNED": """╭── ʙᴀɴ sᴛᴀᴛᴜs ──╮
┃ ᴜɪᴅ: {uid}
┃ sᴛᴀᴛᴜs: ʙᴀɴɴᴇᴅ 🚫
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
    
    "SEARCH_RESULTS": """✦ sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs ғᴏʀ "{query}" ✦

ғᴏᴜɴᴅ {count} ᴍᴀᴛᴄʜᴇs:

{results}

ᴘᴀɢᴇ: {current_page}/{total_pages}""",

    # Spam friend command messages
    "SPAM_SUCCESS": """✦ ꜰʀɪᴇɴᴅ ʀᴇǫᴜᴇsᴛ sᴘᴀᴍ ʀᴇᴘᴏʀᴛ 💫

⭒ ɴɪᴄᴋɴᴀᴍᴇ: {nickname}
⭒ ʀᴇɢɪᴏɴ: {region_name}

╭─ 🅢🅟🅐🅜 🅢🅣🅐🅣🅢 ─╮
┃ 📨 ᴛᴏᴛᴀʟ sᴘᴀᴍ: {totalspam}
╰────────────────╯

✨ sᴘᴀᴍ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!""",

    "SPAM_MAX_REACHED": """✦ ꜰʀɪᴇɴᴅ ʀᴇǫᴜᴇsᴛ sᴘᴀᴍ ʀᴇᴘᴏʀᴛ ⚠️

⭒ ɴɪᴄᴋɴᴀᴍᴇ: {nickname}
⭒ ʀᴇɢɪᴏɴ: {region_name}

❗ᴍᴀxɪᴍᴜᴍ sᴘᴀᴍ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ
⌛ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!""",

    "MISSING_ARGS_SPAM": """❌ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ ᴄᴏᴍᴍᴀɴᴅ!

ᴜsᴀɢᴇ: /spamf [region] [uid]
ʀᴇɢɪᴏɴs: ɪɴᴅ/ᴇᴜ
ᴇxᴀᴍᴘʟᴇ: /spamf ind 123456789""",

    "INVALID_SPAM_UID": "❌ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴜɪᴅ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ ᴏʀ ɪs ɪɴᴠᴀʟɪᴅ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴡɪᴛʜ ᴀ ᴅɪғғᴇʀᴇɴᴛ ᴜɪᴅ."
}

REGION_NAMES = {
    "IND": "ɪηɗɪɐ",
    "EU": "Ɛυʀοƿℯ"
}

@app.on_message(filters.command("like"))
async def give_likes(_, message):
    try:
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

@app.on_message(filters.command("banned"))
async def check_ban(_, message):
    try:
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

@app.on_message(filters.command("search"))
async def search_players(_, message):
    try:
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

@app.on_message(filters.command("spamf"))
async def spam_friend(_, message):
    try:
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

__MODULE__ = "ꜰʀᴇᴇ ꜰɪʀᴇ"
__HELP__ = """
/like [region] [uid] - ɢɪᴠᴇ ʟɪᴋᴇs ᴛᴏ ᴀ ꜰʀᴇᴇ ꜰɪʀᴇ ᴘʀᴏꜰɪʟᴇ
/banned [uid] - ᴄʜᴇᴄᴋ ɪꜰ ᴀ ꜰʀᴇᴇ ꜰɪʀᴇ ᴜɪᴅ ɪs ʙᴀɴɴᴇᴅ
/search [name] - sᴇᴀʀᴄʜ ꜰᴏʀ ꜰʀᴇᴇ ꜰɪʀᴇ ᴘʟᴀʏᴇʀs ʙʏ ɴᴀᴍᴇ
/spamf [region] [uid] - sᴘᴀᴍ ꜰʀɪᴇɴᴅ ʀᴇǫᴜᴇsᴛs ᴛᴏ ᴀ ᴜsᴇʀ
ʀᴇɢɪᴏɴs: ɪɴᴅ/ᴇᴜ

ᴇxᴀᴍᴘʟᴇs:
• /like ind 123456789
• /banned 123456789
• /search devil
• /spamf ind 123456789
""" 