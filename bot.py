import discord
from discord.ext import commands
import random
import os
import json

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
DATA_FILE = "moderation.json"
ROLE_NAME = "рыцарь"
ORGS = ["ФСБ", "ЦГБ3", "ЦГБ7", "УМВД", "ГИБДД", "ФСВНГ", "СК", "Прокурор"]

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

def find_role(guild, name):
    return discord.utils.find(lambda r: r.name.lower() == name.lower(), guild.roles)

class ApplicationModal(discord.ui.Modal, title="Анкета"):
    def __init__(self, org):
        super().__init__()
        self.org = org
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
        data = load_data()
        user = get_user(data, guild.id, interaction.user.id)
        user["profile"] = {
            "ic": str(self.ic.value).strip(),
            "work": self.org,
            "age": str(self.age.value).strip(),
            "real_name": str(self.real_name.value).strip(),
            "timezone": str(self.timezone.value).strip(),
        }
        save_data(data)

        names = [ROLE_NAME, self.org]
        roles = [find_role(guild, name) for name in names]
        roles = [r for r in roles if r]
        missing = [name for name in names if not find_role(guild, name)]
        try:
            if roles:
                await interaction.user.add_roles(*roles, reason="Анкета")
            text = f"Анкета отправлена.\nОрганизация: {self.org}"
            if missing:
                text += "\nНе найдены роли: " + ", ".join(missing)
            await interaction.response.send_message(text, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("Анкета сохранена, но роль бота ниже выдаваемых ролей.", ephemeral=True)

class OrgSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=name) for name in ORGS]
        super().__init__(placeholder="Где работаешь", min_values=1, max_values=1, options=options, custom_id="org_select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ApplicationModal(self.values[0]))

class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OrgSelect())

@bot.event
async def on_ready():
    bot.add_view(ApplicationView())
    print(f"Бот {bot.user} успешно запущен!")

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    if channel:
        message = random.choice(welcome_messages)
        await channel.send(
            f"{message} {member.mention}\nВыбери организацию и заполни анкету.",
            view=ApplicationView()
        )

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
    embed.add_field(name="!инфа @ник", value="Анкета, предупреждения и выговоры", inline=False)
    embed.add_field(name="!досье @ник", value="Только предупреждения и выговоры", inline=False)
    embed.add_field(name="!предупреждение @ник причина", value="Предупреждение. 3 = выговор", inline=False)
    embed.add_field(name="!выговор @ник причина", value="Выговор. 2 = бан навсегда", inline=False)
    embed.add_field(name="!снятьпредупреждение @ник", value="Снять 1 предупреждение", inline=False)
    embed.add_field(name="!снятьвыговор @ник", value="Снять 1 выговор", inline=False)
    embed.add_field(name="!бан @ник причина", value="Бан сразу", inline=False)
    embed.add_field(name="!созыв текст", value="Позвать всех", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
