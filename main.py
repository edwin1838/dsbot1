import asyncio
import os
from datetime import datetime

import discord
from discord.ext import commands

# ================= НАСТРОЙКИ =================
# Для bothost.ru используем переменную окружения
TOKEN = os.getenv("MTQ1ODA5OTAwNzc0OTQ5MjgxMQ.Gzvks2.rZJUGkfb6wPM56Qdprkqf1bg6rcU34YkuO-AX0", "").strip()  # Получаем токен из переменных окружения

# ID Discord сервера и канала
GUILD_ID = 1453830527705550981
CHANNEL_ID = 1458082973382475873

# РОЛИ ДЛЯ АВТОМАТИЧЕСКОЙ ВЫДАЧИ ПРИ ВХОДЕ
# ВСТАВЬТЕ РЕАЛЬНЫЕ ID РОЛЕЙ С ВАШЕГО СЕРВЕРА!
AUTO_ROLES = [
    1453831562340003940,  # Это @everyone (основная роль)
    1458091690412871742
    # Добавьте сюда ID других ролей, которые нужно выдавать автоматически:
    # 123456789012345678,  # Пример: Роль "Игрок"
    # 987654321098765432,  # Пример: Роль "Участник"
]

# Канал для приветственного сообщения (опционально)
WELCOME_CHANNEL_ID = 1458083054571487254  # Вставьте ID канала для приветствий, или оставьте 0 для отключения

# СТИЛЬ MIRAGE
MIRAGE_YELLOW = 0xC0E2F2

# КАРТИНКИ
LOGO_URL = "https://cdn.discordapp.com/attachments/1458089769929277533/1461047542199353537/2_1.png?ex=697b970f&is=697a458f&hm=474cd1b93afe421e3916bf70d25093e27b49903e6431b54db01129d25074100a"
BANNER_INFO = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"
BANNER_SERVERS = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"
BANNER_RULES = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"
BANNER_SUPPORT = "https://cdn.discordapp.com/attachments/1458089769929277533/1462412094375723323/photo_2026-01-18_14-35-49.jpg"

# ================= BOT =================

intents = discord.Intents.default()
intents.members = True  # ВАЖНО: необходимо для отслеживания входа участников
intents.guilds = True
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


# ================= ФУНКЦИИ АВТОМАТИЧЕСКОЙ ВЫДАЧИ РОЛЕЙ =================

async def assign_auto_roles(member: discord.Member):
    """
    Автоматически выдает роли новому участнику
    """
    try:
        added_roles = []
        failed_roles = []

        for role_id in AUTO_ROLES:
            try:
                # Пропускаем некорректные ID
                if role_id == 0:
                    continue

                # Получаем объект роли
                role = member.guild.get_role(role_id)
                if role:
                    # Проверяем, нет ли уже этой роли у пользователя
                    if role not in member.roles:
                        await member.add_roles(role)
                        added_roles.append(f"`{role.name}`")
                        print(f"✅ Выдана роль {role.name} пользователю {member.name}")
                else:
                    print(f"⚠️ Роль с ID {role_id} не найдена на сервере!")
                    failed_roles.append(str(role_id))

            except discord.Forbidden:
                print(f"❌ Нет прав для выдачи роли {role_id}")
                failed_roles.append(str(role_id))
            except discord.HTTPException as e:
                print(f"❌ Ошибка при выдаче роли {role_id}: {e}")
                failed_roles.append(str(role_id))
            except Exception as e:
                print(f"❌ Неизвестная ошибка: {e}")
                failed_roles.append(str(role_id))

        # Возвращаем результат
        return added_roles, failed_roles

    except Exception as e:
        print(f"❌ Критическая ошибка в assign_auto_roles: {e}")
        return [], []


def create_welcome_embed(member: discord.Member, added_roles: list):
    """Создает embed для приветственного сообщения"""
    embed = discord.Embed(
        title="🚀 Добро пожаловать на сервер!",
        description=(
            f"**{member.mention}, рады видеть тебя на сервере GPT RUST!**\n\n"
            "🎮 Здесь ты найдешь единомышленников по игре Rust\n"
            "📢 Следи за новостями и анонсами\n"
            "🤝 Общайся, играй и развивайся с нами!\n\n"
            f"👥 **Теперь нас:** {member.guild.member_count}"
        ),
        color=MIRAGE_YELLOW,
        timestamp=datetime.utcnow()
    )

    # Добавляем информацию о выданных ролях
    if added_roles:
        embed.add_field(
            name="✅ Автоматически выданы роли:",
            value=", ".join(added_roles),
            inline=False
        )

    embed.add_field(
        name="📌 Важно:",
        value="Ознакомься с правилами в канале <#1458082973382475873>",
        inline=False
    )

    if LOGO_URL:
        embed.set_thumbnail(url=LOGO_URL)
        embed.set_footer(text="GPT RUST Community", icon_url=LOGO_URL)
    else:
        embed.set_footer(text="GPT RUST Community")

    return embed


# ================= СОБЫТИЯ БОТА =================

@bot.event
async def on_member_join(member: discord.Member):
    """
    Срабатывает когда новый участник заходит на сервер
    """
    try:
        print(f"👤 Новый участник: {member.name} ({member.id}) присоединился к серверу")

        # Выдаем автоматические роли
        added_roles, failed_roles = await assign_auto_roles(member)

        # Отправляем приветственное сообщение (если канал указан)
        if WELCOME_CHANNEL_ID and added_roles:
            welcome_channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
            if welcome_channel:
                try:
                    embed = create_welcome_embed(member, added_roles)
                    await welcome_channel.send(embed=embed)
                    print(f"📢 Отправлено приветственное сообщение для {member.name}")
                except Exception as e:
                    print(f"⚠️ Не удалось отправить приветствие: {e}")

        # Логирование в консоль
        if added_roles:
            print(f"✅ {member.name} получил роли: {', '.join(added_roles)}")
        if failed_roles:
            print(f"⚠️ Не удалось выдать роли с ID: {', '.join(failed_roles)}")

    except Exception as e:
        print(f"❌ Ошибка в on_member_join: {e}")


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


# ================= КОМАНДА ДЛЯ РУЧНОЙ ВЫДАЧИ РОЛЕЙ =================

@bot.tree.command(
    name="add_roles",
    description="Выдать автоматические роли участнику"
)
@commands.has_permissions(administrator=True)
async def add_roles(interaction: discord.Interaction, member: discord.Member):
    try:
        await interaction.response.defer(ephemeral=True)

        added_roles, failed_roles = await assign_auto_roles(member)

        if added_roles:
            message = f"✅ {member.mention} получил роли: {', '.join(added_roles)}"
        else:
            message = f"ℹ️ {member.mention} уже имеет все автоматические роли"

        if failed_roles:
            message += f"\n⚠️ Не удалось выдать роли с ID: {', '.join(failed_roles)}"

        await interaction.followup.send(message, ephemeral=True)

    except Exception as e:
        print(f"Ошибка в команде add_roles: {e}")
        await interaction.followup.send("Произошла ошибка при выполнении команды.", ephemeral=True)


# ================= ON READY =================

@bot.event
async def on_ready():
    try:
        print("=" * 50)
        print(f"✅ Бот {bot.user} успешно запущен!")
        print(f"👥 Серверов: {len(bot.guilds)}")
        print("=" * 50)

        # Проверяем настройки
        print(f"🔧 Настройки автоматической выдачи ролей:")
        print(f"   • Ролей для выдачи: {len(AUTO_ROLES)}")
        print(f"   • Приветственный канал: {'Включен' if WELCOME_CHANNEL_ID else 'Отключен'}")
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

        # Предупреждение о необходимости настройки
        if len(AUTO_ROLES) <= 1:  # Если только @everyone
            print("\n⚠️ ВНИМАНИЕ: Не настроены роли для автоматической выдачи!")
            print("Добавьте ID ролей в список AUTO_ROLES в начале файла")
            print("Как узнать ID роли: https://support.discord.com/hc/articles/206346498")
            print("Пример: AUTO_ROLES = [123456789, 987654321]")

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
