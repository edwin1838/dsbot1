import discord
from discord.ext import commands
import asyncio
import os

# ================= НАСТРОЙКИ =================
# Для bothost.ru используем переменную окружения
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()  # Получаем токен из переменных окружения

# ID Discord сервера и канала
GUILD_ID = 1453830527705550981
CHANNEL_ID = 1458082973382475873

# СТИЛЬ MIRAGE
MIRAGE_YELLOW = 0xF5C400

# КАРТИНКИ
LOGO_URL = "https://tenor.com/view/gato-cora%C3%A7%C3%A3o-felino-forsaken-memes-gif-12413845295037633769"
BANNER_INFO = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"
BANNER_SERVERS = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"
BANNER_RULES = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"
BANNER_SUPPORT = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"

# ================= BOT =================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ================= VIEWS =================

class InfoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🖥 Серверы", description="Информация и IP серверов", emoji="🖥"),
            discord.SelectOption(label="📜 Правила", description="Основные правила проекта", emoji="📜"),
            discord.SelectOption(label="🆘 Поддержка", description="Связь с администрацией", emoji="🆘"),
        ]
        super().__init__(
            placeholder="Выберите интересующий раздел...",
            options=options,
            custom_id="info_select"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            if self.values[0] == "🖥 Серверы":
                embed = servers_embed()
            elif self.values[0] == "📜 Правила":
                embed = rules_embed()
            else:
                embed = support_embed()

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
                delete_after=60  # Удалить через 1 минуту для экономии места
            )
        except Exception as e:
            print(f"Ошибка в селекторе: {e}")


class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def setup(self):
        """Инициализация после создания бота"""
        self.add_item(InfoSelect())


# ================= EMBEDS =================

def main_embed():
    embed = discord.Embed(
        title="🚀 Добро пожаловать на GPT RUST",
        description=(
            "**Официальный Discord сервер проекта GPT RUST**\n\n"
            "🎯 Выберите интересующий вас раздел ниже ⬇"
        ),
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="🖥 **Серверы**",
        value="> Актуальные сервера и подключение",
        inline=False
    )
    embed.add_field(
        name="📜 **Правила**",
        value="> Основные правила проекта",
        inline=False
    )
    embed.add_field(
        name="🆘 **Поддержка**",
        value="> Связь с администрацией",
        inline=False
    )

    if LOGO_URL:
        embed.set_thumbnail(url=LOGO_URL)
    if BANNER_INFO:
        embed.set_image(url=BANNER_INFO)

    embed.set_footer(text="GPT RUST • Official Discord", icon_url=LOGO_URL if LOGO_URL else None)

    return embed


def servers_embed():
    embed = discord.Embed(
        title="🖥 **Серверы GPT RUST**",
        description="📡 Актуальные сервера и подключение",
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="🎮 **MAIN 2x Vanilla**",
        value="```connect main.gptrust.com```",
        inline=False
    )

    embed.add_field(
        name="🔄 **Wipe Schedule**",
        value="```Каждый четверг в 18:00 (MSK)```",
        inline=False
    )

    if LOGO_URL:
        embed.set_thumbnail(url=LOGO_URL)
    if BANNER_SERVERS:
        embed.set_image(url=BANNER_SERVERS)

    embed.set_footer(text="GPT RUST • Серверы", icon_url=LOGO_URL if LOGO_URL else None)

    return embed


def rules_embed():
    embed = discord.Embed(
        title="📜 **Основные правила**",
        description="⚠️ Незнание правил не освобождает от ответственности.",
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="⛔ **Запрещено**",
        value=(
            "```\n"
            "• Читы, макросы, сторонний софт\n"
            "• Использование багов игры\n"
            "• Оскорбления игроков и администрации\n"
            "```"
        ),
        inline=False
    )

    embed.add_field(
        name="📌 **Важно**",
        value="Полный список правил находится в канале **#правила**",
        inline=False
    )

    if LOGO_URL:
        embed.set_thumbnail(url=LOGO_URL)
    if BANNER_RULES:
        embed.set_image(url=BANNER_RULES)

    embed.set_footer(text="GPT RUST • Правила", icon_url=LOGO_URL if LOGO_URL else None)

    return embed


def support_embed():
    embed = discord.Embed(
        title="🆘 **Поддержка**",
        description="💬 Если у вас возникли проблемы — мы поможем.",
        color=MIRAGE_YELLOW
    )

    embed.add_field(
        name="📩 **Как связаться?**",
        value=(
            "```\n"
            "1. Создайте тикет в разделе поддержки\n"
            "2. Напишите администрации в ЛС\n"
            "```"
        ),
        inline=False
    )

    if LOGO_URL:
        embed.set_thumbnail(url=LOGO_URL)
    if BANNER_SUPPORT:
        embed.set_image(url=BANNER_SUPPORT)

    embed.set_footer(text="GPT RUST • Поддержка", icon_url=LOGO_URL if LOGO_URL else None)

    return embed


# ================= SLASH COMMAND =================

@bot.tree.command(
    name="info",
    description="Информация о проекте GPT RUST"
)
async def info(interaction: discord.Interaction):
    try:
        embed = main_embed()
        view = InfoView()
        await view.setup()
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=False
        )
    except Exception as e:
        print(f"Error in info command: {e}")
        try:
            await interaction.response.send_message(
                "Произошла ошибка при выполнении команды.",
                ephemeral=True
            )
        except:
            pass


# ================= ON READY =================

@bot.event
async def on_ready():
    try:
        print("=" * 50)
        print(f"✅ Бот {bot.user} успешно запущен!")
        print(f"👥 Серверов: {len(bot.guilds)}")
        print("=" * 50)

        # Синхронизируем команды с задержкой
        await asyncio.sleep(1)
        try:
            synced = await bot.tree.sync()
            print(f"✅ Синхронизировано {len(synced)} команд")
        except Exception as e:
            print(f"⚠️ Ошибка синхронизации команд: {e}")

        # Регистрируем персистентные View
        view = InfoView()
        await view.setup()
        bot.add_view(view)

        # Автоматически отправляем сообщение в указанный канал
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            try:
                # Проверяем, есть ли уже сообщение от бота
                found_existing = False
                async for message in channel.history(limit=10):
                    if message.author == bot.user:
                        found_existing = True
                        break

                if not found_existing:
                    embed = main_embed()
                    view = InfoView()
                    await view.setup()
                    await channel.send(embed=embed, view=view)
                    print(f"✅ Сообщение отправлено в канал #{channel.name}")
                else:
                    print(f"ℹ️ Сообщение уже существует в канале #{channel.name}")

            except discord.errors.Forbidden:
                print(f"⚠️ Нет прав для отправки сообщений в канал #{channel.name}")
            except Exception as e:
                print(f"⚠️ Ошибка при отправке в канал: {e}")

        # Устанавливаем статус бота
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="GPT RUST Community"
            ),
            status=discord.Status.online
        )

        print("✅ Бот полностью готов к работе!")

    except Exception as e:
        print(f"❌ Критическая ошибка в on_ready: {e}")


# ================= ERROR HANDLING =================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"⚠️ Ошибка команды: {error}")


# ================= ЗАПУСК БОТА =================

async def main():
    """Основная функция запуска"""
    try:
        # Проверяем наличие токена
        if not TOKEN:
            print("❌ ОШИБКА: Токен бота не найден!")
            print("\nИнструкция для bothost.ru:")
            print("1. Зайдите в панель управления bothost.ru")
            print("2. Найдите раздел 'Переменные окружения'")
            print("3. Добавьте переменную: DISCORD_TOKEN=ваш_токен_бота")
            print("4. Перезапустите бота")
            return

        print(f"🚀 Запуск бота GPT RUST...")
        print(f"🆔 Будет работать на сервере: {GUILD_ID}")
        print(f"📢 Канал для сообщений: {CHANNEL_ID}")

        # Запускаем бота
        async with bot:
            await bot.start(TOKEN)

    except discord.errors.LoginFailure:
        print("❌ ОШИБКА: Неверный токен бота!")
        print("Проверьте правильность токена в настройках bothost.ru")
    except KeyboardInterrupt:
        print("\n👋 Остановка бота...")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")


if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())