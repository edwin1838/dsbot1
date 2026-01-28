import discord
from discord.ext import commands

# ================= НАСТРОЙКИ =================

TOKEN = "MTQ1ODA5OTAwNzc0OTQ5MjgxMQ.Gs8Uql.jWdOC-BwOhK9yfSZsBA6TN5MVjgNReQa13IY8U"

GUILD_ID = 1458079554278129721  # ID Discord сервера
CHANNEL_ID = 1458081872851767414  # ID канала #информация

# СТИЛЬ MIRAGE
MIRAGE_YELLOW = 0xF5C400

# КАРТИНКИ (ЗАМЕНИ НА СВОИ)
LOGO_URL = "https://tenor.com/view/gato-cora%C3%A7%C3%A3o-felino-forsaken-memes-gif-12413845295037633769"
BANNER_INFO = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg?ex=697601e5&is=6974b065&hm=c5a06a8c63869d5c008cca40621518ee2c99ef2b917fea4fee4ef50353642fb9&"
BANNER_SERVERS = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg?ex=697601e5&is=6974b065&hm=c5a06a8c63869d5c008cca40621518ee2c99ef2b917fea4fee4ef50353642fb9&"
BANNER_RULES = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg?ex=697601e5&is=6974b065&hm=c5a06a8c63869d5c008cca40621518ee2c99ef2b917fea4fee4ef50353642fb9&"
BANNER_SUPPORT = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg?ex=697601e5&is=6974b065&hm=c5a06a8c63869d5c008cca40621518ee2c99ef2b917fea4fee4ef50353642fb9&"

# ================= BOT =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# Создаем View для селектора
class InfoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Серверы", emoji="🖥"),
            discord.SelectOption(label="Правила", emoji="📜"),
            discord.SelectOption(label="Поддержка", emoji="🆘"),
        ]
        super().__init__(
            placeholder="Выберите интересующий раздел...",
            options=options,
            custom_id="info_select"
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Серверы":
            embed = servers_embed()
        elif self.values[0] == "Правила":
            embed = rules_embed()
        else:
            embed = support_embed()

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(InfoSelect())


# ================= EMBEDS =================

def main_embed():
    embed = discord.Embed(
        title="Добро пожаловать на GPT RUST",
        description=(
            "Официальный Discord сервер проекта **GPT RUST**.\n\n"
            "Выберите интересующий вас раздел ниже ⬇"
        ),
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="🖥 Серверы",
        value="Информация и IP серверов",
        inline=False
    )
    embed.add_field(
        name="📜 Правила",
        value="Основные правила проекта",
        inline=False
    )
    embed.add_field(
        name="🆘 Поддержка",
        value="Связь с администрацией",
        inline=False
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=BANNER_INFO)
    embed.set_footer(text="GPT RUST • Official Discord")

    return embed


def servers_embed():
    embed = discord.Embed(
        title="🖥 Серверы GPT RUST",
        description="Актуальные сервера и подключение",
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="MAIN 2x Vanilla",
        value="`connect main.gptrust.com`",
        inline=False
    )

    embed.add_field(
        name="Wipe",
        value="Каждый четверг в 18:00 (MSK)",
        inline=False
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=BANNER_SERVERS)
    embed.set_footer(text="GPT RUST")

    return embed


def rules_embed():
    embed = discord.Embed(
        title="📜 Основные правила",
        description="Незнание правил не освобождает от ответственности.",
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="⛔ Запрещено",
        value=(
            "• Читы, макросы, сторонний софт\n"
            "• Использование багов\n"
            "• Оскорбления игроков и администрации\n"
            "• Уклонение от проверок"
        ),
        inline=False
    )

    embed.add_field(
        name="📌 Важно",
        value="Полный список правил находится в канале **#правила**",
        inline=False
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=BANNER_RULES)
    embed.set_footer(text="GPT RUST")

    return embed


def support_embed():
    embed = discord.Embed(
        title="🆘 Поддержка",
        description="Если у вас возникли проблемы — мы поможем.",
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="Как связаться?",
        value=(
            "• Создайте тикет в разделе поддержки\n"
            "• Или напишите администрации в ЛС"
        ),
        inline=False
    )

    embed.set_thumbnail(url=LOGO_URL)
    embed.set_image(url=BANNER_SUPPORT)
    embed.set_footer(text="GPT RUST")

    return embed


# ================= SLASH COMMAND =================

@bot.tree.command(
    name="info",
    description="Информация о проекте GPT RUST"
)
@commands.guild_only()
async def info(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=main_embed(),
        view=InfoView()
    )


# ================= ON READY =================

@bot.event
async def on_ready():
    try:
        # Синхронизируем команды только для указанной гильдии
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)

        # Регистрируем персистентное View
        bot.add_view(InfoView())

        # Отправляем сообщение в канал
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            # Проверим, есть ли уже сообщение с нашим View
            # Если нет, отправим новое
            try:
                await channel.purge(limit=1)  # Очистим 1 старое сообщение
            except:
                pass

            await channel.send(
                embed=main_embed(),
                view=InfoView()
            )

        print("===================================")
        print("GPT RUST BOT STARTED")
        print(f"Logged in as {bot.user}")
        print("===================================")

    except Exception as e:
        print(f"Error in on_ready: {e}")


# ================= ERROR HANDLING =================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Error: {error}")


bot.run(TOKEN)
