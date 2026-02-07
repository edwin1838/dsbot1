import re
import uuid

import discord
from discord.ext import commands

# ================= НАСТРОЙКИ =================

BOT_TOKEN = "MTQ1ODA5OTAwNzc0OTQ5MjgxMQ.GihYRh.DgDiDnEnrvDw6qGGoPec0TffwIDzPu9utIkSOk"

SUPPORT_CHANNEL_ID = 1458081896272625664  # канал где создаются ветки
SUPPORT_PANEL_CHANNEL_ID = 1458081893898518548  # админ-панель

SUPPORT_ROLES = ["Support", "Admin"]

STEAM_REGEX = re.compile(r"^7656119\d{10}$")

COLOR_MAIN = 0xF1C40F
COLOR_SUCCESS = 0x2ECC71
COLOR_ERROR = 0xE74C3C

# =============================================

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ticket_id -> data
tickets = {}


# ================= UTILS =================

def valid_steam(steam: str) -> bool:
    return bool(STEAM_REGEX.match(steam))


def is_support(member: discord.Member):
    return any(r.name in SUPPORT_ROLES for r in member.roles)


# ================= USER THREAD =================

async def create_ticket(interaction, title, fields):
    base_channel = interaction.guild.get_channel(SUPPORT_CHANNEL_ID)
    panel_channel = interaction.guild.get_channel(SUPPORT_PANEL_CHANNEL_ID)

    ticket_id = str(uuid.uuid4())[:8]

    thread = await base_channel.create_thread(
        name="Ваш тикет",
        type=discord.ChannelType.private_thread
    )

    await thread.add_user(interaction.user)

    tickets[ticket_id] = {
        "thread_id": thread.id,
        "user_id": interaction.user.id,
        "title": title
    }

    embed_user = discord.Embed(title=f"📌 {title}", color=COLOR_MAIN)
    for n, v in fields:
        embed_user.add_field(name=n, value=v or "Пусто", inline=False)

    embed_user.add_field(
        name="",
        value="━━━━━━━━━━━━━━\n🕐 **Модератор изучает запрос —**\nпожалуйста, подождите",
        inline=False
    )

    await thread.send(embed=embed_user)

    # ===== ADMIN PANEL =====

    embed_admin = discord.Embed(
        title="🎟 Новый тикет",
        color=COLOR_MAIN
    )
    embed_admin.add_field(name="ID", value=ticket_id, inline=True)
    embed_admin.add_field(name="Тип", value=title, inline=True)
    embed_admin.add_field(name="Пользователь", value=interaction.user.mention, inline=False)

    view = AdminPanelView(ticket_id)

    await panel_channel.send(embed=embed_admin, view=view)

    await interaction.response.send_message(
        f"Готово! 🎟️ Ваш тикет создан!\nКликните по {thread.mention}, чтобы перейти.",
        ephemeral=True
    )


# ================= ADMIN MODAL =================

class ReplyModal(discord.ui.Modal, title="Ответ пользователю"):
    message = discord.ui.TextInput(
        label="Ответ от GPT-Ticket",
        style=discord.TextStyle.paragraph
    )

    def __init__(self, ticket_id):
        super().__init__()
        self.ticket_id = ticket_id

    async def on_submit(self, interaction):
        data = tickets.get(self.ticket_id)
        if not data:
            await interaction.response.send_message("🚫 Тикет не найден", ephemeral=True)
            return

        thread = interaction.guild.get_channel(data["thread_id"])

        embed = discord.Embed(
            description=self.message.value,
            color=COLOR_SUCCESS
        )
        embed.set_author(name="GPT-Ticket")

        await thread.send(embed=embed)
        await interaction.response.send_message("✅ Ответ отправлен", ephemeral=True)


# ================= ADMIN BUTTONS =================

class AdminPanelView(discord.ui.View):
    def __init__(self, ticket_id):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(label="📨 Ответить", style=discord.ButtonStyle.success)
    async def reply(self, interaction: discord.Interaction, _):
        if not is_support(interaction.user):
            await interaction.response.send_message("🚫 Нет доступа", ephemeral=True)
            return
        await interaction.response.send_modal(ReplyModal(self.ticket_id))

    @discord.ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.secondary)
    async def close(self, interaction: discord.Interaction, _):
        if not is_support(interaction.user):
            await interaction.response.send_message("🚫 Нет доступа", ephemeral=True)
            return

        data = tickets.pop(self.ticket_id, None)
        if data:
            thread = interaction.guild.get_channel(data["thread_id"])
            await thread.edit(archived=True, locked=True)

        await interaction.response.send_message("🔒 Тикет закрыт", ephemeral=True)

    # ================= MODAL =================

    class ServerModal(discord.ui.Modal, title="Вопрос по серверу"):
        server = discord.ui.TextInput(label="Сервер")
        steam = discord.ui.TextInput(label="SteamID")
        desc = discord.ui.TextInput(label="Описание", style=discord.TextStyle.paragraph)
        proof = discord.ui.TextInput(label="Доп. материалы", required=False)

        async def on_submit(self, interaction):
            if not valid_steam(self.steam.value):
                await interaction.response.send_message("🚫 Неверный SteamID", ephemeral=True)
                return

            await create_ticket(
                interaction,
                "Вопрос по серверу",
                [
                    ("Сервер", self.server.value),
                    ("SteamID", self.steam.value),
                    ("Описание", self.desc.value),
                    ("Доп. материалы", self.proof.value),
                ]
            )

    # ================= PANEL =================

    class TicketPanel(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.select(
            placeholder="Выберите тип обращения",
            options=[
                discord.SelectOption(label="Вопрос по серверу", emoji="🛠"),
                discord.SelectOption(label="Жалоба", emoji="🚨"),
                discord.SelectOption(label="Обжалование", emoji="⚖️"),
                discord.SelectOption(label="Сотрудничество", emoji="👑"),
            ]
        )
        async def select(self, interaction, select):
            await interaction.response.send_modal(ServerModal())

    # ================= READY =================

    @bot.event
    async def on_ready():
        print(f"✅ GPT-Ticket запущен как {bot.user}")
        bot.add_view(TicketPanel())

    # ================= START =================

    bot.run(BOT_TOKEN)
