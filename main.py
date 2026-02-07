import re
import uuid

import discord
from discord.ext import commands

# ================= НАСТРОЙКИ =================

BOT_TOKEN = "MTQ1ODA5OTAwNzc0OTQ5MjgxMQ.GihYRh.DgDiDnEnrvDw6qGGoPec0TffwIDzPu9utIkSOk"

SUPPORT_CHANNEL_ID = 1458083050520055822  # канал где создаются ветки
SUPPORT_PANEL_CHANNEL_ID = 1468671297809682699  # админ-панель

# Роли которые могут закрывать тикеты (добавьте ID ролей)
SUPPORT_ROLE_IDS = [
    1453831129315676160,  # ID роли "Support" - ЗАМЕНИТЕ на реальный ID
    1458082799033782313,  # ID роли "Admin" - ЗАМЕНИТЕ на реальный ID
    1458082797792268439,
    1458082803181686866,
    1458082812682043488,
]

# Альтернативно: названия ролей (если не хотите использовать ID)
SUPPORT_ROLE_NAMES = ["Support", "Admin", "Модератор", "Модер"]

STEAM_REGEX = re.compile(r"^7656119\d{10}$")

COLOR_MAIN = 0x42AAFF
COLOR_SUCCESS = 0x00BFFF
COLOR_ERROR = 0x00BFFF

# =============================================

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ticket_id -> data
tickets = {}


# ================= UTILS =================

def valid_steam(steam: str) -> bool:
    return bool(STEAM_REGEX.match(steam))


def is_support(member: discord.Member):
    """Проверяет, имеет ли пользователь права поддержки"""
    # Проверка по ID ролей
    if SUPPORT_ROLE_IDS:
        user_role_ids = [role.id for role in member.roles]
        if any(role_id in SUPPORT_ROLE_IDS for role_id in user_role_ids):
            return True

    # Проверка по названиям ролей
    if SUPPORT_ROLE_NAMES:
        user_role_names = [role.name for role in member.roles]
        if any(role_name in SUPPORT_ROLE_NAMES for role_name in user_role_names):
            return True

    # Проверка административных прав
    if member.guild_permissions.administrator:
        return True

    # Проверка прав на управление каналами
    if member.guild_permissions.manage_channels:
        return True

    # Проверка прав на управление сообщениями
    if member.guild_permissions.manage_messages:
        return True

    return False


def can_close_ticket(interaction: discord.Interaction, ticket_data: dict):
    """Проверяет, может ли пользователь закрыть конкретный тикет"""
    member = interaction.user

    # 1. Администраторы всегда могут закрывать
    if member.guild_permissions.administrator:
        return True

    # 2. Поддержка может закрывать
    if is_support(member):
        return True

    # 3. Создатель тикета может закрыть свой тикет
    if ticket_data and member.id == ticket_data.get("user_id"):
        return True

    return False


# ================= MODALS =================

class ServerModal(discord.ui.Modal, title="Вопрос по серверу"):
    server = discord.ui.TextInput(
        label="Сервер",
        placeholder="На каком сервере возникла проблема?",
        required=True,
        custom_id="server_modal_server"
    )
    steam = discord.ui.TextInput(
        label="SteamID",
        placeholder="7656119xxxxxxxxx",
        required=True,
        custom_id="server_modal_steam"
    )
    desc = discord.ui.TextInput(
        label="Описание",
        style=discord.TextStyle.paragraph,
        placeholder="Опишите вашу проблему подробно...",
        required=True,
        custom_id="server_modal_desc"
    )
    proof = discord.ui.TextInput(
        label="Дополнительные материалы",
        style=discord.TextStyle.paragraph,
        placeholder="Ссылки на скриншоты, видео и т.д.",
        required=False,
        custom_id="server_modal_proof"
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not valid_steam(self.steam.value):
            await interaction.response.send_message(
                "🚫 Неверный формат SteamID! Пример: 76561198123456789",
                ephemeral=True
            )
            return

        await create_ticket(
            interaction,
            "🛠 Вопрос по серверу",
            [
                ("Сервер", self.server.value),
                ("SteamID", self.steam.value),
                ("Описание", self.desc.value),
                ("Доп. материалы", self.proof.value or "Не указано"),
            ]
        )


class ReportModal(discord.ui.Modal, title="Жалоба"):
    player_name = discord.ui.TextInput(
        label="Имя игрока",
        placeholder="Никнейм нарушителя",
        required=True,
        custom_id="report_modal_player_name"
    )
    steam = discord.ui.TextInput(
        label="SteamID нарушителя",
        placeholder="7656119xxxxxxxxx",
        required=True,
        custom_id="report_modal_steam"
    )
    desc = discord.ui.TextInput(
        label="Описание нарушения",
        style=discord.TextStyle.paragraph,
        placeholder="Что произошло?",
        required=True,
        custom_id="report_modal_desc"
    )
    proof = discord.ui.TextInput(
        label="Доказательства",
        style=discord.TextStyle.paragraph,
        placeholder="Ссылки на скриншоты, видео и т.д.",
        required=True,
        custom_id="report_modal_proof"
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not valid_steam(self.steam.value):
            await interaction.response.send_message(
                "🚫 Неверный формат SteamID!",
                ephemeral=True
            )
            return

        await create_ticket(
            interaction,
            "🚨 Жалоба",
            [
                ("Нарушитель", self.player_name.value),
                ("SteamID нарушителя", self.steam.value),
                ("Описание", self.desc.value),
                ("Доказательства", self.proof.value),
            ]
        )


class AppealModal(discord.ui.Modal, title="Обжалование"):
    steam = discord.ui.TextInput(
        label="Ваш SteamID",
        placeholder="7656119xxxxxxxxx",
        required=True,
        custom_id="appeal_modal_steam"
    )
    ban_reason = discord.ui.TextInput(
        label="Причина бана",
        placeholder="Что указано в причине бана?",
        required=True,
        custom_id="appeal_modal_ban_reason"
    )
    appeal_text = discord.ui.TextInput(
        label="Текст обжалования",
        style=discord.TextStyle.paragraph,
        placeholder="Почему бан должен быть снят?",
        required=True,
        custom_id="appeal_modal_appeal_text"
    )
    proof = discord.ui.TextInput(
        label="Дополнительные материалы",
        style=discord.TextStyle.paragraph,
        placeholder="Ссылки на доказательства невиновности",
        required=False,
        custom_id="appeal_modal_proof"
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not valid_steam(self.steam.value):
            await interaction.response.send_message(
                "🚫 Неверный формат SteamID!",
                ephemeral=True
            )
            return

        await create_ticket(
            interaction,
            "⚖️ Обжалование",
            [
                ("SteamID", self.steam.value),
                ("Причина бана", self.ban_reason.value),
                ("Текст обжалования", self.appeal_text.value),
                ("Доп. материалы", self.proof.value or "Не указано"),
            ]
        )


class CooperationModal(discord.ui.Modal, title="Сотрудничество"):
    name = discord.ui.TextInput(
        label="Ваше имя/ник",
        placeholder="Как к вам обращаться?",
        required=True,
        custom_id="coop_modal_name"
    )
    contact = discord.ui.TextInput(
        label="Контактная информация",
        placeholder="Discord, Telegram, VK и т.д.",
        required=True,
        custom_id="coop_modal_contact"
    )
    proposal = discord.ui.TextInput(
        label="Предложение",
        style=discord.TextStyle.paragraph,
        placeholder="Что вы предлагаете?",
        required=True,
        custom_id="coop_modal_proposal"
    )
    details = discord.ui.TextInput(
        label="Дополнительные детали",
        style=discord.TextStyle.paragraph,
        placeholder="Опыт, портфолио, идеи и т.д.",
        required=False,
        custom_id="coop_modal_details"
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(
            interaction,
            "👑 Сотрудничество",
            [
                ("Имя", self.name.value),
                ("Контакты", self.contact.value),
                ("Предложение", self.proposal.value),
                ("Детали", self.details.value or "Не указано"),
            ]
        )


# ================= USER THREAD =================

async def create_ticket(interaction: discord.Interaction, title: str, fields: list):
    try:
        base_channel = bot.get_channel(SUPPORT_CHANNEL_ID)
        if not base_channel:
            await interaction.response.send_message(
                "❌ Канал для тикетов не найден!",
                ephemeral=True
            )
            return

        panel_channel = bot.get_channel(SUPPORT_PANEL_CHANNEL_ID)
        ticket_id = str(uuid.uuid4())[:8]

        # Создаем приватную ветку
        thread = await base_channel.create_thread(
            name=f"🎫 {title} | {interaction.user.name}",
            type=discord.ChannelType.private_thread,
            reason=f"Тикет создан пользователем {interaction.user}"
        )

        await thread.add_user(interaction.user)

        tickets[ticket_id] = {
            "thread_id": thread.id,
            "user_id": interaction.user.id,
            "user_name": interaction.user.name,
            "title": title,
            "created_at": discord.utils.utcnow()
        }

        # Сообщение в ветке пользователя
        embed_user = discord.Embed(
            title=f"🎫 {title}",
            description=f"**Тикет #{ticket_id}**",
            color=COLOR_MAIN
        )

        for name, value in fields:
            embed_user.add_field(name=name, value=value or "Не указано", inline=False)

        embed_user.add_field(
            name="Информация",
            value=(
                f"👤 **Создатель:** {interaction.user.mention}\n"
                f"🆔 **ID тикета:** `{ticket_id}`\n"
                f"📅 **Создан:** <t:{int(discord.utils.utcnow().timestamp())}:R>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🕐 **Ожидайте ответа администрации...**\n"
                "Обычно ответ занимает до 24 часов.\n\n"
                "✅ **Вы можете закрыть свой тикет командой** `/close_ticket`"
            ),
            inline=False
        )

        embed_user.set_footer(text="GPT-Ticket Support System")

        await thread.send(
            content=f"{interaction.user.mention}, ваш тикет создан!",
            embed=embed_user
        )

        # Уведомление в админ-панель
        if panel_channel:
            embed_admin = discord.Embed(
                title="🎟️ Новый тикет",
                description=f"**#{ticket_id}**",
                color=COLOR_MAIN
            )

            embed_admin.add_field(name="Тип", value=title, inline=True)
            embed_admin.add_field(name="Пользователь", value=interaction.user.mention, inline=True)
            embed_admin.add_field(name="Ветка", value=thread.mention, inline=True)
            embed_admin.add_field(name="ID пользователя", value=f"`{interaction.user.id}`", inline=False)

            embed_admin.add_field(
                name="Действия",
                value="Используйте кнопки ниже для управления тикетом",
                inline=False
            )

            view = AdminPanelView(ticket_id)
            await panel_channel.send(embed=embed_admin, view=view)

        await interaction.response.send_message(
            f"✅ Тикет создан!\n"
            f"**ID:** `{ticket_id}`\n"
            f"**Тип:** {title}\n"
            f"**Ссылка:** {thread.mention}\n\n"
            f"📌 **Вы можете закрыть тикет командой** `/close_ticket`",
            ephemeral=True
        )

    except Exception as e:
        print(f"❌ Ошибка создания тикета: {e}")
        await interaction.response.send_message(
            "❌ Произошла ошибка при создании тикета!",
            ephemeral=True
        )


async def close_ticket_by_id(ticket_id: str, closer: discord.Member):
    """Закрывает тикет по ID"""
    data = tickets.pop(ticket_id, None)
    if not data:
        return False, "Тикет не найден"

    try:
        thread = closer.guild.get_channel(data["thread_id"])
        if not thread:
            return False, "Ветка не найдена"

        # Отправляем сообщение о закрытии
        embed = discord.Embed(
            title="🔒 Тикет закрыт",
            description=(
                f"Тикет закрыт {closer.mention}\n"
                f"🆔 **ID тикета:** `{ticket_id}`\n"
                f"📅 **Закрыт:** <t:{int(discord.utils.utcnow().timestamp())}:R>\n\n"
                f"👤 **Создатель:** <@{data['user_id']}>\n"
                f"👮 **Закрыл:** {closer.mention}"
            ),
            color=COLOR_ERROR
        )
        await thread.send(embed=embed)

        # Закрываем ветку
        await thread.edit(archived=True, locked=True)

        return True, f"✅ Тикет #{ticket_id} успешно закрыт!"

    except Exception as e:
        print(f"❌ Ошибка при закрытии тикета: {e}")
        return False, f"⚠️ Ошибка при закрытии: {e}"


# ================= ADMIN MODAL =================

class ReplyModal(discord.ui.Modal, title="Ответ пользователю"):
    message = discord.ui.TextInput(
        label="Сообщение от поддержки",
        style=discord.TextStyle.paragraph,
        placeholder="Введите ваш ответ...",
        required=True,
        custom_id="reply_modal_message"
    )

    def __init__(self, ticket_id: str):
        super().__init__()
        self.ticket_id = ticket_id

    async def on_submit(self, interaction: discord.Interaction):
        data = tickets.get(self.ticket_id)
        if not data:
            await interaction.response.send_message("❌ Тикет не найден!", ephemeral=True)
            return

        thread = interaction.guild.get_channel(data["thread_id"])
        if not thread:
            await interaction.response.send_message("❌ Ветка не найдена!", ephemeral=True)
            return

        embed = discord.Embed(
            description=self.message.value,
            color=COLOR_SUCCESS
        )
        embed.set_author(
            name=f"Ответ от {interaction.user.name}",
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )
        embed.set_footer(text="GPT-Ticket Support")

        await thread.send(embed=embed)
        await interaction.response.send_message("✅ Ответ отправлен!", ephemeral=True)


# ================= ADMIN PANEL VIEW =================

class AdminPanelView(discord.ui.View):
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="📨 Ответить", style=discord.ButtonStyle.success, emoji="📨", custom_id="admin_reply_btn")
    async def reply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_support(interaction.user):
            await interaction.response.send_message("❌ У вас нет прав для ответа на тикеты!", ephemeral=True)
            return

        await interaction.response.send_modal(ReplyModal(self.ticket_id))

    @discord.ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="admin_close_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = tickets.get(self.ticket_id)

        # Проверяем права на закрытие
        if not can_close_ticket(interaction, data):
            await interaction.response.send_message(
                "❌ У вас нет прав для закрытия этого тикета!\n"
                "Только поддержка или создатель тикета могут его закрыть.",
                ephemeral=True
            )
            return

        success, message = await close_ticket_by_id(self.ticket_id, interaction.user)
        await interaction.response.send_message(message, ephemeral=True)


# ================= TICKET PANEL VIEW =================

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🎫 Выберите тип обращения",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Вопрос по серверу",
                description="Технические вопросы и помощь",
                emoji="🛠",
                value="server_issue"
            ),
            discord.SelectOption(
                label="Жалоба",
                description="Жалоба на игрока или персонал",
                emoji="🚨",
                value="complaint"
            ),
            discord.SelectOption(
                label="Обжалование",
                description="Обжалование бана или наказания",
                emoji="⚖️",
                value="appeal"
            ),
            discord.SelectOption(
                label="Сотрудничество",
                description="Предложения по развитию проекта",
                emoji="👑",
                value="cooperation"
            ),
        ],
        custom_id="ticket_type_select"
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]

        if value == "server_issue":
            await interaction.response.send_modal(ServerModal())
        elif value == "complaint":
            await interaction.response.send_modal(ReportModal())
        elif value == "appeal":
            await interaction.response.send_modal(AppealModal())
        elif value == "cooperation":
            await interaction.response.send_modal(CooperationModal())


# ================= BOT EVENTS =================

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"🤖 Бот вошел как: {bot.user}")
    print(f"🆔 ID бота: {bot.user.id}")
    print(f"👥 Серверов: {len(bot.guilds)}")
    print("=" * 50)

    # Проверяем настройки прав
    print("🔧 Настройки прав доступа:")
    print(f"   • ID ролей поддержки: {SUPPORT_ROLE_IDS}")
    print(f"   • Названия ролей поддержки: {SUPPORT_ROLE_NAMES}")
    print("=" * 50)

    # Синхронизируем команды
    try:
        synced = await bot.tree.sync()
        print(f"✅ Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"⚠️ Ошибка синхронизации: {e}")

    # Устанавливаем статус
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🎫 систему тикетов"
        ),
        status=discord.Status.online
    )

    print("✅ Бот готов к работе!")


# ================= SLASH COMMANDS =================

@bot.tree.command(name="setup_tickets", description="Настроить панель тикетов")
async def setup_tickets(interaction: discord.Interaction):
    """Команда для создания панели тикетов"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Только администраторы могут настраивать панель!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎫 Система поддержки GPT-Ticket",
        description=(
            "**Добро пожаловать в систему поддержки!**\n\n"
            "Выберите тип обращения из списка ниже:\n\n"
            "🛠 **Вопрос по серверу**\n"
            "Технические вопросы, помощь с сервером\n\n"
            "🚨 **Жалоба**\n"
            "Жалобы на игроков или персонал\n\n"
            "⚖️ **Обжалование**\n"
            "Обжалование банов и наказаний\n\n"
            "👑 **Сотрудничество**\n"
            "Предложения по развитию проекта\n\n"
            "👇 **Выберите категорию ниже:**"
        ),
        color=COLOR_MAIN
    )

    embed.set_footer(text="GPT-Ticket Support System • Ответ в течение 24 часов")

    view = TicketPanelView()
    await interaction.response.send_message(embed=embed, view=view)

    print(f"✅ Панель тикетов создана пользователем {interaction.user.name}")


@bot.tree.command(name="ticket_info", description="Информация о системе тикетов")
async def ticket_info(interaction: discord.Interaction):
    """Информация о системе"""
    embed = discord.Embed(
        title="ℹ️ Информация о системе тикетов",
        description=(
            "**Как работает система:**\n"
            "1. Выберите тип обращения\n"
            "2. Заполните форму\n"
            "3. Создается приватный тикет\n"
            "4. С вами свяжется поддержка\n"
            "5. Проблема будет решена!\n\n"

            "**Кто может закрывать тикеты:**\n"
            "• Администраторы сервера\n"
            "• Пользователи с ролями поддержки\n"
            "• Создатель тикета (только свой)\n\n"

            "**Команды:**\n"
            "• `/close_ticket` - Закрыть свой тикет\n"
            "• `/ticket_stats` - Статистика (только поддержка)\n"
            "• `/my_tickets` - Мои активные тикеты\n\n"

            "**Что нужно указывать:**\n"
            "• SteamID (для вопросов и жалоб)\n"
            "• Подробное описание проблемы\n"
            "• Доказательства (скриншоты, видео)"
        ),
        color=COLOR_MAIN
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="close_ticket", description="Закрыть свой тикет")
async def close_ticket(interaction: discord.Interaction, ticket_id: str = None):
    """Закрыть тикет (можно указать ID или выбрать активный)"""
    if not ticket_id:
        # Ищем активный тикет пользователя
        user_tickets = [tid for tid, data in tickets.items() if data["user_id"] == interaction.user.id]

        if not user_tickets:
            await interaction.response.send_message(
                "❌ У вас нет активных тикетов!\n"
                "Укажите ID тикета: `/close_ticket ticket_id:12345678`",
                ephemeral=True
            )
            return

        if len(user_tickets) == 1:
            ticket_id = user_tickets[0]
        else:
            # Если несколько тикетов, показываем список
            ticket_list = "\n".join([f"• `{tid}` - {tickets[tid]['title']}" for tid in user_tickets])
            embed = discord.Embed(
                title="🎫 Ваши активные тикеты",
                description=f"У вас несколько активных тикетов:\n\n{ticket_list}\n\n**Используйте:** `/close_ticket ticket_id:ID`",
                color=COLOR_MAIN
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    data = tickets.get(ticket_id)

    if not data:
        await interaction.response.send_message("❌ Тикет не найден!", ephemeral=True)
        return

    # Проверяем права
    if not can_close_ticket(interaction, data):
        await interaction.response.send_message(
            "❌ Вы не можете закрыть этот тикет!\n"
            "Вы можете закрывать только свои тикеты.",
            ephemeral=True
        )
        return

    success, message = await close_ticket_by_id(ticket_id, interaction.user)
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="my_tickets", description="Показать мои активные тикеты")
async def my_tickets(interaction: discord.Interaction):
    """Показать активные тикеты пользователя"""
    user_tickets = [(tid, data) for tid, data in tickets.items() if data["user_id"] == interaction.user.id]

    if not user_tickets:
        await interaction.response.send_message(
            "📭 У вас нет активных тикетов!",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="🎫 Ваши активные тикеты",
        color=COLOR_MAIN
    )

    for ticket_id, data in user_tickets:
        thread = interaction.guild.get_channel(data["thread_id"])
        thread_mention = thread.mention if thread else "Ветка не найдена"

        embed.add_field(
            name=f"#{ticket_id} - {data['title']}",
            value=f"**Ветка:** {thread_mention}\n**Создан:** <t:{int(data['created_at'].timestamp())}:R>\n**Закрыть:** `/close_ticket ticket_id:{ticket_id}`",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ticket_stats", description="Статистика тикетов")
async def ticket_stats(interaction: discord.Interaction):
    """Статистика активных тикетов"""
    if not is_support(interaction.user):
        await interaction.response.send_message("❌ У вас нет прав для просмотра статистики!", ephemeral=True)
        return

    active_tickets = len(tickets)

    embed = discord.Embed(
        title="📊 Статистика тикетов",
        color=COLOR_MAIN
    )

    embed.add_field(name="Активных тикетов", value=str(active_tickets), inline=True)
    embed.add_field(name="Система", value="Работает ✅", inline=True)

    if active_tickets > 0:
        ticket_list = []
        for ticket_id, data in list(tickets.items())[:10]:  # Показываем первые 10
            user = interaction.guild.get_member(data["user_id"])
            user_name = user.mention if user else f"`{data['user_name']}`"
            thread = interaction.guild.get_channel(data["thread_id"])
            thread_info = thread.mention if thread else "Не найдена"

            ticket_list.append(f"`#{ticket_id}` - {data['title']}\n👤 {user_name} | 🧵 {thread_info}")

        embed.add_field(
            name=f"Активные тикеты ({len(ticket_list)})",
            value="\n\n".join(ticket_list) if ticket_list else "Нет активных тикетов",
            inline=False
        )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="force_close", description="Принудительно закрыть тикет (только админы)")
async def force_close(interaction: discord.Interaction, ticket_id: str):
    """Принудительно закрыть любой тикет (только администраторы)"""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Только администраторы могут использовать эту команду!",
                                                ephemeral=True)
        return

    success, message = await close_ticket_by_id(ticket_id, interaction.user)
    await interaction.response.send_message(message, ephemeral=True)


# ================= ERROR HANDLING =================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"⚠️ Ошибка команды: {error}")


# ================= ЗАПУСК БОТА =================

if __name__ == "__main__":
    print("🚀 Запуск бота GPT-Ticket...")
    print("=" * 50)

    print("🔧 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ ПРАВ:")
    print("1. Найдите ID ролей поддержки на вашем сервере")
    print("2. Вставьте их в список SUPPORT_ROLE_IDS")
    print("3. Или укажите названия ролей в SUPPORT_ROLE_NAMES")
    print("=" * 50)

    try:
        bot.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Ошибка авторизации: Неверный токен!")
        print("Проверьте токен на https://discord.com/developers/applications")
    except Exception as e:
        print(f"❌ Непредвиденная ошибка: {e}")
