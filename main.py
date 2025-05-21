from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN
import sqlite3

# Init Bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Init DB
conn = sqlite3.connect('bot_users.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    invited_by INTEGER,
    bonus_claimed INTEGER DEFAULT 0
)""")
conn.commit()

# Register or get user
def register_user(user_id, username, invited_by=None):
    cur.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users (id, username, invited_by) VALUES (?, ?, ?)",
                    (user_id, username, invited_by))
        conn.commit()

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    args = message.get_args()
    inviter_id = int(args) if args.isdigit() else None
#    register_user(message.from_user.id, message.from_user.username, inviter_id)await message.reply("👋 Welcome to RS FIBER TEAM Bot!Use /help to see commands.")
@dp.message_handler(commands=['help'])
async def help_cmd(message: types.Message):
    await message.reply(
        "/myaccount - Show your account"

        "/invite - Get your invite link"

        "/bonus - Claim your bonus"

        "/redeem CODE - Redeem a code"

        "/stats - View statistics")

@dp.message_handler(commands=['myaccount'])
async def myaccount_cmd(message: types.Message):
    user_id = message.from_user.id
    cur.execute("SELECT username, bonus_claimed FROM users WHERE id=?", (user_id,))
    data = cur.fetchone()
    if data:
        await message.reply("👤 Username: @{data[0]}
💰 Bonus Claimed: {data[1]}")
    else:
        await message.reply("❌ You are not registered.")

@dp.message_handler(commands=['invite'])
async def invite_cmd(message: types.Message):
    invite_link = f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}"
    await message.reply(f"📨 Share this invite link:
{invite_link}")

@dp.message_handler(commands=['bonus'])
async def bonus_cmd(message: types.Message):
    user_id = message.from_user.id
    cur.execute("SELECT bonus_claimed FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    if row:
        if row[0] == 0:
            cur.execute("UPDATE users SET bonus_claimed = 1 WHERE id=?", (user_id,))
            conn.commit()
            await message.reply("✅ Bonus claimed successfully!")
        else:
            await message.reply("⚠️ You have already claimed your bonus.")
    else:
        await message.reply("❌ You are not registered.")

@dp.message_handler(commands=['redeem'])
async def redeem_cmd(message: types.Message):
    code = message.get_args()
    if code == "FREE100":
        await message.reply("🎁 Code Redeemed: You got 100 coins!")
    else:
        await message.reply("❌ Invalid code.")

@dp.message_handler(commands=['stats'])
async def stats_cmd(message: types.Message):
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    await message.reply(f"📊 Total Registered Users: {total_users}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
