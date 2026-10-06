import discord
from discord.ext import commands, tasks
import random
import os
import json
import io
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
import pytesseract

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
DATA_FILE = "moderation.json"
ROLE_NAME = "рыцарь"
ORGS = ["ФСБ", "ЦГБ3", "ЦГБ7", "УМВД", "ГИБДД", "ФСВНГ", "СК", "Прокурор"]
DEPOSIT_CHANNEL = "пополнение-счета-семьи"
FAMILY_ROLES = ["рыцарь", "байкер", "техник", "заместитель", "босс", "бос"]
WEEK_TZ = ZoneInfo("Europe/Moscow")

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
welcome_images = [
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162706195746826/image.png?backend=b2&ex=6ac328f5&is=6ac1d775&hm=76c4b21601b68815aaa6a68f5cbfe799b8668898d00905f4e860c290dbf069ef&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162708569718894/image.png?backend=b2&ex=6ac328f5&is=6ac1d775&hm=dc82237f3c54ff5f3a054015be583bc5fda666133145908e81cc96af19102863&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162710469615707/image.png?backend=b2&ex=6ac328f6&is=6ac1d776&hm=9583d13e938a83c8b0fb7391e437636633769be8f85595114a1c82b2327b977d&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162712151789589/image.png?backend=b2&ex=6ac328f6&is=6ac1d776&hm=c6c3f6c1815ce14514ebbbd10d1e8bf4c152b0a659004fd5aba4b172f4b7675f&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162714030702654/image.png?backend=b2&ex=6ac328f7&is=6ac1d777&hm=cb2c8e85d2dc3debfd73b6ed1b0706cd445f947348bb814a65d7bf55b04e8a0c&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162715389661234/image.png?backend=b2&ex=6ac328f7&is=6ac1d777&hm=9cc950149b221c302bc4857d2b09db2dc9b2dec9a4b58b71d8bc611468a201b5&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162716840755210/image.png?backend=b2&ex=6ac328f7&is=6ac1d777&hm=229f3ee8048f3da4a9e8d2fae8998ec07ddcb7a6876ce52d8d0ed657ff600f96&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162718657159238/image.png?backend=b2&ex=6ac328f8&is=6ac1d778&hm=0e8ac3ae70f913ee77da7af61c5e793b75081ae9ec17f59b6ab318a008740a90&",
    "https://cdn.discordapp.com/attachments/1555563045617410181/1556162720041275472/image.png?backend=b2&ex=6ac328f8&is=6ac1d778&hm=efc216a930d5a4e28d516aca2acd1bbfc9a45654668a178dbeff04d2e5aaef75&"
]

AMOUNT_RE = re.compile(r"\d{1,3}(?:[ \u00a0.,]\d{3})+|\d{3,12}")

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
    data[gid].setdefault(uid, {"warnings": 0, "reprimands": 0, "profile": {}, "deposited": 0, "week_deposited": 0, "week_id": ""})
    data[gid][uid].setdefault("profile", {})
    return data[gid][uid]

def can_moderate(ctx):
    perms = ctx.author.guild_permissions
    return perms.ban_members or perms.administrator

def in_family(member):
    for role in member.roles:
        name = role.name.lower()
        if any(name.startswith(family) for family in FAMILY_ROLES):
            return True
    return False

def find_role(guild, name):
    return discord.utils.find(lambda r: r.name.lower() == name.lower(), guild.roles)

def current_week():
    return datetime.now(WEEK_TZ).strftime("%Y-W%W")

def numbers_from_text(text):
    text = (text or "").replace("\u00a0", " ")
    found = []
    for raw in AMOUNT_RE.findall(text):
        digits = re.sub(r"\D", "", raw)
        if not digits.isdigit():
            continue
        value = int(digits)
        if 1 <= value <= 50_000_000:
            found.append(value)
    return found

def screenshot_numbers(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    texts = [pytesseract.image_to_string(image, lang="rus+eng")]
    gray = image.convert("L")
    texts.append(pytesseract.image_to_string(gray, lang="rus+eng", config="--psm 6"))
    found = []
    for text in texts:
        found.extend(numbers_from_text(text))
    return list(dict.fromkeys(found))

def top_lines(guild, rows):
    lines = []
    for i, (amount, uid) in enumerate(rows[:10], 1):
        member = guild.get_member(int(uid))
        name = member.display_name if member else uid
        lines.append(f"{i}. {name} — {amount}")
    return "\n".join(lines) if lines else "Пока пусто."

class FilledView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        done = discord.ui.Select(
            placeholder="Анкета заполнена",
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label="Анкета заполнена", value="done")],
            disabled=True,
            custom_id="anketa_filled",
        )
        self.add_item(done)

class ApplicationModal(discord.ui.Modal, title="Анкета"):
    def __init__(self, org, source_message):
        super().__init__()
        self.org = org
        self.source_message = source_message
        self.ic = discord.ui.TextInput(label="IC: Имя", placeholder="Игровое имя", required=True, max_length=50)
        self.age = discord.ui.TextInput(label="Возраст", placeholder="18", required=True, max_length=3)
        self.real_name = discord.ui.TextInput(label="Настоящее имя", placeholder="Имя", required=True, max_length=50)
        self.timezone = discord.ui.TextInput(label="Часовой пояс", placeholder="МСК", required=True, max_length=30)
        self.add_item(self.ic)
        self.add_item(self.age)
        self.add_item(self.real_name)
        self.add_item(self.timezone)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        ic_name = str(self.ic.value).strip()[:32]
        data = load_data()
        user = get_user(data, guild.id, interaction.user.id)
        user["profile"] = {
            "ic": ic_name,
            "work": self.org,
            "age": str(self.age.value).strip(),
            "real_name": str(self.real_name.value).strip(),
            "timezone": str(self.timezone.value).strip(),
        }
        save_data(data)
        nick_ok = True
        try:
            await interaction.user.edit(nick=ic_name)
        except discord.Forbidden:
            nick_ok = False
        names = [ROLE_NAME, self.org]
        roles = [find_role(guild, name) for name in names]
        roles = [r for r in roles if r]
        missing = [name for name in names if not find_role(guild, name)]
        try:
            if roles:
                await interaction.user.add_roles(*roles, reason="Анкета")
        except discord.Forbidden:
            await interaction.response.send_message("Анкета сохранена, но роль бота ниже выдаваемых ролей.", ephemeral=True)
            return
        done = discord.Embed(description=f"{interaction.user.mention}\nАнкета заполнена ✅")
        try:
            await self.source_message.edit(embed=done, view=FilledView())
        except discord.HTTPException:
            pass
        text = f"Анкета заполнена ✅\nОрганизация: {self.org}\nНик: {ic_name}"
        if not nick_ok:
            text += "\nНик не сменён: роль бота ниже роли человека или это владелец сервера."
        if missing:
            text += "\nНе найдены роли: " + ", ".join(missing)
        await interaction.response.send_message(text, ephemeral=True)

class OrgSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=name) for name in ORGS]
        super().__init__(placeholder="Где работаешь", min_values=1, max_values=1, options=options, custom_id="org_select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ApplicationModal(self.values[0], interaction.message))

class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OrgSelect())

@bot.event
async def on_ready():
    bot.add_view(ApplicationView())
    bot.add_view(FilledView())
    if not week_reset.is_running():
        week_reset.start()
    print(f"Бот {bot.user} успешно запущен!")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        message = random.choice(welcome_messages)
        embed = discord.Embed(description=f"{message} {member.mention}\nВыбери организацию и заполни анкету.")
        embed.set_image(url=random.choice(welcome_images))
        await channel.send(embed=embed, view=ApplicationView())

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    await bot.process_commands(message)
    if not message.channel.name.startswith(DEPOSIT_CHANNEL):
        return
    images = [f for f in message.attachments if f.content_type and f.content_type.startswith("image/")]
    if not images:
        return
    if len(images) != 2:
        await message.reply("Нужно 2 скрина: сначала банк до пополнения, потом банк после.")
        return
    try:
        before = screenshot_numbers(await images[0].read())
        after = screenshot_numbers(await images[1].read())
    except Exception as e:
        await message.reply(f"Ошибка чтения скрина: {e}")
        return
    if not before or not after:
        await message.reply("Не увидел сумму счёта на скрине.")
        return
    old_balance = max(before)
    new_balance = max(after)
    amount = new_balance - old_balance
    if amount <= 0:
        await message.reply("На втором скрине счёт не больше, чем на первом. Сначала до, потом после.")
        return
    data = load_data()
    user = get_user(data, message.guild.id, message.author.id)
    week = current_week()
    if user.get("week_id") != week:
        user["week_id"] = week
        user["week_deposited"] = 0
    user["deposited"] = user.get("deposited", 0) + amount
    user["week_deposited"] = user.get("week_deposited", 0) + amount
    gid = str(message.guild.id)
    data[gid]["family_balance"] = new_balance
    save_data(data)
    await message.reply(
        f"✅ Засчитано: {amount}\n"
        f"Было: {old_balance}\n"
        f"Стало: {new_balance}\n"
        f"Твой вклад: {user['deposited']}\n"
        f"За эту неделю: {user['week_deposited']}\n"
        f"Счёт семьи: {new_balance}"
    )

@tasks.loop(minutes=1)
async def week_reset():
    now = datetime.now(WEEK_TZ)
    if not (now.weekday() == 0 and now.hour == 0 and now.minute == 0):
        return
    week = current_week()
    data = load_data()
    for guild in bot.guilds:
        gid = str(guild.id)
        users = data.get(gid, {})
        rows = []
        for uid, info in list(users.items()):
            if not isinstance(info, dict):
                continue
            amount = info.get("week_deposited", 0)
            if amount and info.get("week_id") != week:
                rows.append((amount, uid))
                info["week_deposited"] = 0
                info["week_id"] = week
        if not rows:
            continue
        rows.sort(reverse=True)
        text = top_lines(guild, rows)
        users["previous_week_text"] = text
        channel = discord.utils.find(lambda c: c.name.startswith(DEPOSIT_CHANNEL), guild.text_channels)
        if channel:
            await channel.send("🏁 Топ прошедшей недели\n" + text + "\n\nНовая неделя началась.")
    save_data(data)

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
    await ctx.send("Выбери организацию и заполни анкету.", view=ApplicationView())

@bot.command(name="рейтинг")
async def deposit_top(ctx):
    if not in_family(ctx.author):
        await ctx.send("Команда только для семьи.")
        return
    data = load_data()
    users = data.get(str(ctx.guild.id), {})
    rows = []
    for uid, info in users.items():
        if not isinstance(info, dict):
            continue
        amount = info.get("deposited", 0)
        if amount:
            rows.append((amount, uid))
    rows.sort(reverse=True)
    balance = users.get("family_balance", 0)
    await ctx.send("🏆 Общий рейтинг\n" + top_lines(ctx.guild, rows) + f"\n\nСчёт семьи: {balance}")

@bot.command(name="неделя")
async def week_top(ctx):
    if not in_family(ctx.author):
        await ctx.send("Команда только для семьи.")
        return
    data = load_data()
    users = data.get(str(ctx.guild.id), {})
    week = current_week()
    rows = []
    for uid, info in users.items():
        if not isinstance(info, dict):
            continue
        if info.get("week_id") == week and info.get("week_deposited", 0):
            rows.append((info["week_deposited"], uid))
    rows.sort(reverse=True)
    previous = users.get("previous_week_text", "Прошлой недели ещё нет.")
    await ctx.send("📅 Прошлая неделя\n" + previous + "\n\n📅 Текущая неделя\n" + top_lines(ctx.guild, rows))

@bot.command(name="счет")
async def family_balance(ctx):
    if not in_family(ctx.author):
        await ctx.send("Команда только для семьи.")
        return
    data = load_data()
    balance = data.get(str(ctx.guild.id), {}).get("family_balance", 0)
    await ctx.send(f"💵 Счёт семьи: {balance}")

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
        await ctx.send(
            f"По {member.mention} анкеты нет.\n"
            f"Предупреждения: {user['warnings']}/3\n"
            f"Выговоры: {user['reprimands']}/2"
        )
        return
    await ctx.send(
        f"📋 Инфа {member.mention}\n"
        f"IC: {profile.get('ic', '—')}\n"
        f"Где работает: {profile.get('work', '—')}\n"
        f"Возраст: {profile.get('age', '—')}\n"
        f"Настоящее имя: {profile.get('real_name', '—')}\n"
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
                text += "\n\nНе смог забанить: роль бота ниже роли человека."
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
            text += "\n\nНе смог забанить: роль бота ниже роли человека."
        await ctx.send(text)
        return
    save_data(data)
    await ctx.send(text)

@bot.command(name="снятьпредупреждение")
async def remove_warning(ctx, member: discord.Member = None):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if member is None:
        await ctx.send("Напиши: `!снятьпредупреждение @ник`")
        return
    data = load_data()
    user = get_user(data, ctx.guild.id, member.id)
    if user["warnings"] <= 0:
        await ctx.send(f"У {member.mention} нет предупреждений.")
        return
    user["warnings"] -= 1
    save_data(data)
    await ctx.send(f"✅ С {member.mention} снято 1 предупреждение. Осталось: {user['warnings']}/3")

@bot.command(name="снятьвыговор")
async def remove_reprimand(ctx, member: discord.Member = None):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if member is None:
        await ctx.send("Напиши: `!снятьвыговор @ник`")
        return
    data = load_data()
    user = get_user(data, ctx.guild.id, member.id)
    if user["reprimands"] <= 0:
        await ctx.send(f"У {member.mention} нет выговоров.")
        return
    user["reprimands"] -= 1
    save_data(data)
    await ctx.send(f"✅ С {member.mention} снят 1 выговор. Осталось: {user['reprimands']}/2")

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
        await ctx.send("Не смог забанить. Подними роль бота выше роли человека.")

@bot.command(name="очистить")
async def clear_chat(ctx, amount: int = 10):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if amount < 1 or amount > 100:
        await ctx.send("Напиши число от 1 до 100.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"Удалено сообщений: {len(deleted) - 1}")
    await msg.delete(delay=3)

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

@bot.command(name="созыв")
async def call_all(ctx, *, text: str = None):
    if not can_moderate(ctx):
        await ctx.send("У тебя нет прав на это.")
        return
    if not text:
        await ctx.send("Напиши: `!созыв текст созыва`")
        return
    await ctx.send(f"@everyone\n{text}\nВызвал: {ctx.author.mention}")

@bot.command(name="помощь")
async def help_command(ctx):
    embed = discord.Embed(title="📋 Команды", color=discord.Color.blue())
    embed.add_field(name="!привет", value="Поздороваться", inline=False)
    embed.add_field(name="!пинг", value="Проверить бота", inline=False)
    embed.add_field(name="!семья", value="Сообщение для семьи", inline=False)
    embed.add_field(name="!заявка", value="Открыть анкету", inline=False)
    embed.add_field(name="!рейтинг", value="Общий рейтинг пополнений. Только семья", inline=False)
    embed.add_field(name="!неделя", value="Прошлая и текущая неделя. Только семья", inline=False)
    embed.add_field(name="!счет", value="Счёт семьи. Только семья", inline=False)
    embed.add_field(name="!инфа @ник", value="Анкета, предупреждения и выговоры", inline=False)
    embed.add_field(name="!досье @ник", value="Только предупреждения и выговоры", inline=False)
    embed.add_field(name="!предупреждение @ник причина", value="Предупреждение. 3 = выговор", inline=False)
    embed.add_field(name="!выговор @ник причина", value="Выговор. 2 = бан навсегда", inline=False)
    embed.add_field(name="!снятьпредупреждение @ник", value="Снять 1 предупреждение", inline=False)
    embed.add_field(name="!снятьвыговор @ник", value="Снять 1 выговор", inline=False)
    embed.add_field(name="!бан @ник причина", value="Бан сразу", inline=False)
    embed.add_field(name="!очистить 10", value="Удалить сообщения. От 1 до 100", inline=False)
    embed.add_field(name="!созыв текст", value="Позвать всех", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
