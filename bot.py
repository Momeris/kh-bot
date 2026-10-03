import discord
from discord.ext import commands
import random
import os
import json
import sys
import re

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
DATA_FILE = "moderation.json"
ROLE_NAME = "рыцарь"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

welcome_messages = [
    "Привет бро! 👋 Рад, что ты с нами!",
    "Йоу! Добро пожаловать в семью 🔥",
    "Здарова! Теперь ты официально часть нашей банды 😎",
    "Привет-привет! Заходи, располагайся ❤️",
    "Опа, новенький! Добро пожаловать, бро!",
    "Хей! Рады видеть тебя здесь 🎉",
    "Приветствую! Теперь ты один из нас 💪",
    "Здорово, бро! Залетай скорее!",
    "Вау, новый человек! Добро пожаловать в семью ❤️",
    "Привет! Надеюсь, тебе у нас понравится 😊",
    "Йо-йо! Свежая кровь в семье 🔥",
    "Здарова, путник! Добро пожаловать!",
    "Привет! Рады тебя видеть!",
    "О, новый участник! Залетай скорее 👋",
    "Добро пожаловать в нашу дружную семью!",
    "Приветствую тебя в наших рядах!",
    "Йоу бро, давно тебя ждали!",
    "Здарова! Теперь ты официально с нами 😎",
    "Привет! Рад знакомству, залетай!",
    "Новенький? Добро пожаловать в семью!",
    "Хей хей! Присоединяйся к нам ❤️",
    "Привет, друг! Рады, что ты здесь!",
    "Опана! Новый человек в доме 🔥",
    "Здорово! Добро пожаловать на борт!",
    "Привет-привет, рады тебя видеть!",
    "Йоу! Заходи, не стесняйся!",
    "Добро пожаловать!",
    "Привет! Надеюсь, тебе у нас будет круто!",
    "Здарова! Теперь ты часть большой семьи!",
    "Хей! Рад, что ты с нами!",
    "Приветствую! Залетай в наш уютный уголок!",
    "О, свежее пополнение! Добро пожаловать!",
    "Йо! Добро пожаловать в семью, бро!",
    "Привет! Мы тебя уже заждались 😎",
    "Здарова-здарова! Рады видеть!",
    "Добро пожаловать! Здесь тебе всегда рады!",
    "Привет, новый друг! Заходи смелее!",
    "Йоу! Теперь ты один из нас!",
    "Здорово, путник! Присоединяйся!",
    "Привет! Добро пожаловать в нашу банду 🔥",
    "Опа! Новый участник семьи прибыл!",
    "Хей бро! Рад знакомству!",
    "Приветствую тебя! Надеюсь, останешься с нами надолго!",
    "Здарова! Залетай, располагайся поудобнее!",
    "Добро пожаловать в семью! Мы тебя ждали!"
]

form_text = """Скопируй форму, заполни пустые поля и отправь одним сообщением:

IC: 
Где работаешь: 
Возраст: 
Настоящее имя: 
Тег зам или лид: 
Часовой пояс: 
"""

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, guild_id, user_id):
    gid = str(guild_id)
    uid = str(user_id)
    data.setdefault(gid, {})
    data[gid].setdefault(uid, {"warnings": 0, "reprimands": 0, "profile": {}})
    data[gid][uid].setdefault("profile", {})
    return data[gid][uid]

def can_moderate(ctx):
    perms = ctx.author.guild_permissions
    return perms.ban_members or perms.administrator

def field(text, label):
    match = re.search(rf"{label}\s*:\s*(.+)", text, re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip()

def parse_form(text):
    profile = {
        "ic": field(text, "IC"),
        "work": field(text, "Где работаешь"),
        "age": field(text, "Возраст"),
        "real_name": field(text, "Настоящее имя"),
        "tag": field(text, "Тег зам или лид"),
        "timezone": field(text, "Часовой пояс"),
    }
    if not all(profile.values()):
        return None
    return profile

@bot.event
async def on_ready():
    print(f"Бот {bot.user} успешно запущен!")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        message = random.choice(welcome_messages)
        await channel.send(f"{message} {member.mention}\n{form_text}")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    if not message.content.startswith(PREFIX):
        profile = parse_form(message.content)
        if profile:
            data = load_data()
            user = get_user(data, message.guild.id, message.author.id)
            user["profile"] = profile
            save_data(data)

            role = discord.utils.find(lambda r: r.name.lower() == ROLE_NAME, message.guild.roles)
            given = False
            if role:
                try:
                    await message.author.add_roles(role, reason="Заполнил заявку")
                    given = True
                except discord.Forbidden:
                    given = False

            if given:
                await message.channel.send(f"{message.author.mention}, заявка принята. Роль {role.mention} выдана.")
            elif role is None:
                await message.channel.send(f"{message.author.mention}, заявка сохранена, но роль `рыцарь` на сервере не найдена.")
            else:
                await message.channel.send(f"{message.author.mention}, заявка сохранена, но бот не смог выдать роль. Подними роль бота выше роли `рыцарь`.")
            return

    await bot.process_commands(message)

@bot.command(name="привет")
async def hello(ctx):
    await ctx.send(f"Привет, {ctx.author.mention}! 👋")

@bot.command(name="пинг")
async def ping(ctx):
    await ctx.send(f"Понг! 🏓 {round(bot.latency * 1000)} мс")

@bot.command(name="семья")
async def family(ctx):
    await ctx.send("👨‍👩‍👧‍👦 Это наш семейный сервер! Здесь всегда рады всем ❤️")

@bot.command(name="заявка")
async def application(ctx):
    await ctx.send(form_text)

@bot.command(name="инфа")
async def info(ctx, member: discord.Member = None):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if member is None:
        await ctx.send("Напиши: `!инфа @ник`")
        return
    data = load_data()
    user = get_user(data, ctx.guild.id, member.id)
    profile = user.get("profile") or {}
    if not profile:
        await ctx.send(f"По {member.mention} заявки нет.")
        return
    await ctx.send(
        f"📋 Инфа {member.mention}\n"
        f"IC: {profile.get('ic', '—')}\n"
        f"Где работает: {profile.get('work', '—')}\n"
        f"Возраст: {profile.get('age', '—')}\n"
        f"Настоящее имя: {profile.get('real_name', '—')}\n"
        f"Тег зам или лид: {profile.get('tag', '—')}\n"
        f"Часовой пояс: {profile.get('timezone', '—')}\n"
        f"Предупреждения: {user['warnings']}/3\n"
        f"Выговоры: {user['reprimands']}/2"
    )

@bot.command(name="предупреждение")
async def warn(ctx, member: discord.Member = None, *, reason: str = "не указана"):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if member is None:
        await ctx.send("Напиши: `!предупреждение @ник причина`")
        return
    if member.bot or member == ctx.author:
        await ctx.send("Так нельзя.")
        return

    data = load_data()
    user = get_user(data, ctx.guild.id, member.id)
    user["warnings"] += 1
    text = f"⚠️ {member.mention} получил предупреждение.\nПричина: {reason}\nПредупреждений: {user['warnings']}/3"

    if user["warnings"] >= 3:
        user["warnings"] = 0
        user["reprimands"] += 1
        text += f"\n\n🚨 3 предупреждения. Автоматически выдан выговор.\nВыговоров: {user['reprimands']}/2"

        if user["reprimands"] >= 2:
            save_data(data)
            try:
                await member.ban(reason="2 выговора")
                text += "\n\n⛔ 2 выговора. Выдан бан навсегда."
            except discord.Forbidden:
                text += "\n\nНе смог забанить: у бота нет права Ban Members или роль бота ниже роли человека."
            await ctx.send(text)
            return

    save_data(data)
    await ctx.send(text)

@bot.command(name="выговор")
async def reprimand(ctx, member: discord.Member = None, *, reason: str = "не указана"):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if member is None:
        await ctx.send("Напиши: `!выговор @ник причина`")
        return
    if member.bot or member == ctx.author:
        await ctx.send("Так нельзя.")
        return

    data = load_data()
    user = get_user(data, ctx.guild.id, member.id)
    user["reprimands"] += 1
    user["warnings"] = 0
    text = f"🚨 {member.mention} получил выговор.\nПричина: {reason}\nВыговоров: {user['reprimands']}/2"

    if user["reprimands"] >= 2:
        save_data(data)
        try:
            await member.ban(reason="2 выговора")
            text += "\n\n⛔ 2 выговора. Выдан бан навсегда."
        except discord.Forbidden:
            text += "\n\nНе смог забанить: у бота нет права Ban Members или роль бота ниже роли человека."
        await ctx.send(text)
        return

    save_data(data)
    await ctx.send(text)

@bot.command(name="бан")
async def ban_user(ctx, member: discord.Member = None, *, reason: str = "не указана"):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if member is None:
        await ctx.send("Напиши: `!бан @ник причина`")
        return
    if member.bot or member == ctx.author:
        await ctx.send("Так нельзя.")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"⛔ {member.mention} забанен навсегда.\nПричина: {reason}")
    except discord.Forbidden:
        await ctx.send("Не смог забанить. Подними роль бота выше роли человека и дай боту право Ban Members.")

@bot.command(name="досье")
async def dossier(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_data()
    user = get_user(data, ctx.guild.id, member.id)
    await ctx.send(
        f"📋 Досье {member.mention}\n"
        f"Предупреждения: {user['warnings']}/3\n"
        f"Выговоры: {user['reprimands']}/2"
    )

@bot.command(name="снять")
async def clear_mod(ctx, member: discord.Member = None):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if member is None:
        await ctx.send("Напиши: `!снять @ник`")
        return
    data = load_data()
    gid = str(ctx.guild.id)
    uid = str(member.id)
    if gid in data and uid in data[gid]:
        data[gid][uid]["warnings"] = 0
        data[gid][uid]["reprimands"] = 0
        save_data(data)
    await ctx.send(f"✅ С {member.mention} сняты предупреждения и выговоры.")

@bot.command(name="созыв")
async def call_all(ctx, *, text: str = None):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if not text:
        await ctx.send("Напиши: `!созыв текст созыва`")
        return
    await ctx.send(f"@everyone\n{text}\nВызвал: {ctx.author.mention}")

@bot.command(name="перезапуск")
async def restart(ctx):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    await ctx.send("Перезапускаюсь...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@bot.command(name="помощь")
async def help_command(ctx):
    embed = discord.Embed(title="📋 Команды", color=discord.Color.blue())
    embed.add_field(name="!привет", value="Поздороваться", inline=False)
    embed.add_field(name="!пинг", value="Проверить бота", inline=False)
    embed.add_field(name="!семья", value="Сообщение для семьи", inline=False)
    embed.add_field(name="!заявка", value="Показать форму заявки", inline=False)
    embed.add_field(name="!инфа @ник", value="Заявка и наказания. Только модераторам", inline=False)
    embed.add_field(name="!досье @ник", value="Сколько предупреждений и выговоров", inline=False)
    embed.add_field(name="!предупреждение @ник причина", value="Выдать предупреждение. 3 = выговор", inline=False)
    embed.add_field(name="!выговор @ник причина", value="Выдать выговор. 2 = бан навсегда", inline=False)
    embed.add_field(name="!бан @ник причина", value="Бан сразу", inline=False)
    embed.add_field(name="!снять @ник", value="Обнулить предупреждения и выговоры", inline=False)
    embed.add_field(name="!созыв текст", value="Позвать всех на сервере", inline=False)
    embed.add_field(name="!перезапуск", value="Перезапустить бота", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
