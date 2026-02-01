import discord
from discord.ext import commands
import asyncio
import os
import sys
from datetime import datetime

# ================= НАСТРОЙКИ =================
TOKEN = os.getenv("DISCORD_TOKEN", "MTQ1ODA5OTAwNzc0OTQ5MjgxMQ.Gzvks2.rZJUGkfb6wPM56Qdprkqf1bg6rcU34YkuO-AX0").strip()

# Проверяем токен сразу
if not TOKEN:
    print("❌ ОШИБКА: Токен бота не найден в переменных окружения!")
    print("Токен должен быть установлен как переменная окружения DISCORD_TOKEN")
    sys.exit(1)

# ID Discord сервера и канала
GUILD_ID = 1453830527705550981
CHANNEL_ID = 1458082973382475873

# РОЛИ ДЛЯ АВТОМАТИЧЕСКОЙ ВЫДАЧИ
# ВАЖНО: Добавьте реальные ID ролей с вашего сервера
AUTO_ROLES = [
    1453831562340003940,  # @everyone (основная роль)
    1458091690412871742,
    # Примеры (замените на реальные ID):
    # 123456789012345678,  # Роль "Игрок"
    # 987654321098765432,  # Роль "Участник"
]

# СТИЛЬ MIRAGE
MIRAGE_YELLOW = 0xC0E2F2

# ================= BOT =================

intents = discord.Intents.default()
intents.members = True  # КРИТИЧЕСКИ ВАЖНО для on_member_join
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ================= ПРОВЕРКА ТОКЕНА =================

def validate_token(token):
    """Проверяет валидность токена"""
    if not token:
        return False, "Токен пустой"

    # Проверяем длину и формат
    if len(token) < 50:
        return False, f"Токен слишком короткий: {len(token)} символов"

    # Токен обычно начинается с определенных префиксов
    valid_prefixes = ['MT', 'OT', 'Nz', 'ND', 'MTA', 'OD']
    if not any(token.startswith(prefix) for prefix in valid_prefixes):
        return False, "Неверный формат токена"

    return True, "Токен выглядит валидным"


# ================= ОБРАБОТЧИКИ ОШИБОК =================

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Ошибка в событии {event}: {args} {kwargs}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"⚠️ Ошибка команды: {error}")


# ================= ОСНОВНЫЕ ФУНКЦИИ =================

async def assign_auto_roles(member: discord.Member):
    """Автоматически выдает роли новому участнику"""
    try:
        print(f"🎯 Попытка выдать роли пользователю: {member.name}")

        added_roles = []
        for role_id in AUTO_ROLES:
            try:
                role = member.guild.get_role(role_id)
                if role and role not in member.roles:
                    await member.add_roles(role)
                    added_roles.append(role.name)
                    print(f"✅ Выдана роль: {role.name}")
            except Exception as e:
                print(f"⚠️ Не удалось выдать роль {role_id}: {e}")

        return added_roles
    except Exception as e:
        print(f"❌ Ошибка в assign_auto_roles: {e}")
        return []


@bot.event
async def on_member_join(member: discord.Member):
    """Обработчик входа нового участника"""
    try:
        print(f"👤 Новый участник: {member.name}")
        await assign_auto_roles(member)
    except Exception as e:
        print(f"❌ Ошибка в on_member_join: {e}")


# ================= КОМАНДЫ =================

@bot.tree.command(name="test", description="Тестовая команда")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Бот работает!", ephemeral=True)


@bot.tree.command(name="roles", description="Проверить выдачу ролей")
async def roles(interaction: discord.Interaction):
    try:
        added = await assign_auto_roles(interaction.user)
        if added:
            await interaction.response.send_message(f"✅ Вам выданы роли: {', '.join(added)}", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ У вас уже есть все автоматические роли", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ошибка: {e}", ephemeral=True)


# ================= ЗАПУСК =================

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ Бот {bot.user} успешно запущен!")
    print(f"🆔 ID бота: {bot.user.id}")
    print(f"👥 Серверов: {len(bot.guilds)}")
    print("=" * 50)

    # Синхронизация команд
    try:
        await bot.tree.sync()
        print("✅ Команды синхронизированы")
    except Exception as e:
        print(f"⚠️ Ошибка синхронизации: {e}")

    # Проверяем наличие сервера
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f"✅ Найден сервер: {guild.name}")
        print(f"👥 Участников: {guild.member_count}")

        # Проверяем канал
        channel = guild.get_channel(CHANNEL_ID)
        if channel:
            print(f"📢 Канал найден: #{channel.name}")
        else:
            print(f"⚠️ Канал {CHANNEL_ID} не найден")
    else:
        print(f"⚠️ Сервер {GUILD_ID} не найден")

    print("=" * 50)


async def main():
    """Основная функция запуска"""
    try:
        # Валидация токена
        is_valid, message = validate_token(TOKEN)
        if not is_valid:
            print(f"❌ Неверный токен: {message}")
            print("\nКак получить токен:")
            print("1. https://discord.com/developers/applications")
            print("2. Выберите ваше приложение")
            print("3. Bot → Reset Token → Copy")
            print("4. На bothost.ru добавьте переменную: DISCORD_TOKEN=ваш_токен")
            return

        print(f"🚀 Запуск бота...")
        print(f"✅ Токен валидный ({len(TOKEN)} символов)")

        # Проверяем интенты
        print(f"🔧 Интенты активированы:")
        print(f"   • Members: {intents.members}")
        print(f"   • Guilds: {intents.guilds}")

        async with bot:
            await bot.start(TOKEN)

    except discord.LoginFailure:
        print("❌ Ошибка авторизации: Неверный токен!")
        print("Проверьте токен на https://discord.com/developers/applications")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {type(e).__name__}: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Запуск Discord бота GPT RUST")
    print("=" * 50)

    # Запускаем с обработкой KeyboardInterrupt
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Остановка бота...")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")