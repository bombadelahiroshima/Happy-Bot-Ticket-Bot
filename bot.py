import asyncio
import io
import json
import os
import logging
import re
from datetime import datetime, timezone
from typing import Optional

import discord
from discord import Interaction, app_commands
from discord.ext import commands







TOKEN = ""
GUILD_ID = None
LOGO_URL = "https://i.imgur.com/3c5baMT.png"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("happybot")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_channel_name(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return (value or "ticket")[:90]


class JSONStore:
    """Simple JSON storage. No external database required."""
    def __init__(self):
        self.lock = asyncio.Lock()
        self.files = {
            "guild_configs": "guild_configs.json",
            "tickets": "tickets.json",
            "blacklist": "blacklist.json",
        }
        self.data = {key: self._load(path) for key, path in self.files.items()}

    @staticmethod
    def _load(path: str) -> dict:
        try:
            if not os.path.exists(path):
                return {}
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _save(self, key: str) -> None:
        path = self.files[key]
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data[key], f, indent=4, ensure_ascii=False)
        os.replace(tmp, path)

    async def save(self, *keys: str) -> None:
        async with self.lock:
            for key in keys:
                self._save(key)

    async def reload(self) -> None:
        async with self.lock:
            self.data = {key: self._load(path) for key, path in self.files.items()}

    async def get_config(self, guild_id: int) -> Optional[dict]:
        async with self.lock:
            return self.data["guild_configs"].get(str(guild_id))

    async def get_ticket(self, channel_id: int) -> Optional[dict]:
        async with self.lock:
            return self.data["tickets"].get(str(channel_id))

    async def open_ticket_count(self, guild_id: int, user_id: int) -> int:
        async with self.lock:
            return sum(
                1
                for ticket in self.data["tickets"].values()
                if ticket.get("guild_id") == guild_id
                and ticket.get("user_id") == user_id
                and ticket.get("status") == "open"
            )

    async def is_blacklisted(self, guild_id: int, user_id: int) -> bool:
        async with self.lock:
            return str(user_id) in self.data["blacklist"].get(str(guild_id), [])

    async def next_ticket_number(self, guild_id: int) -> int:
        async with self.lock:
            guild_key = str(guild_id)
            config = self.data["guild_configs"].get(guild_key)
            if not config:
                raise RuntimeError("Guild is not configured")
            number = int(config.get("ticket_counter", 0)) + 1
            config["ticket_counter"] = number
            self._save("guild_configs")
            return number


store = JSONStore()


def make_embed(title: str, description: str, color: discord.Color = discord.Color(0xFFFFFF)) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color, timestamp=discord.utils.utcnow())
    embed.set_thumbnail(url=LOGO_URL)
    embed.set_footer(text="Happy Bot — Powerful tickets. Full control.", icon_url=LOGO_URL)
    return embed


async def get_config(guild_id: int):
    return await store.get_config(guild_id)


async def get_ticket(channel_id: int):
    return await store.get_ticket(channel_id)


async def is_staff(member: discord.Member, config: dict) -> bool:
    role_id = int(config.get("staff_role_id", 0))
    return role_id in {role.id for role in member.roles} or member.guild_permissions.manage_guild


async def require_ticket(interaction: Interaction) -> Optional[dict]:
    if not interaction.guild or not interaction.channel:
        await interaction.response.send_message("❌ Tickets can only be managed inside a server.", ephemeral=True)
        return None

    ticket = await get_ticket(interaction.channel.id)
    if not ticket or ticket["guild_id"] != interaction.guild.id:
        await interaction.response.send_message("❌ This channel is not a Happy Bot ticket.", ephemeral=True)
        return None
    return ticket


async def can_manage_ticket(interaction: Interaction, ticket: dict, staff_only: bool = True) -> bool:
    config = await get_config(interaction.guild.id)
    if not config:
        await interaction.response.send_message("❌ Happy Bot is not configured.", ephemeral=True)
        return False

    member = interaction.user
    if not isinstance(member, discord.Member):
        await interaction.response.send_message("❌ This action is only available to server members.", ephemeral=True)
        return False

    staff = await is_staff(member, config)
    owner = member.id == ticket["user_id"]

    if staff_only and not staff:
        await interaction.response.send_message("❌ You do not have permission to manage this ticket.", ephemeral=True)
        return False

    if not staff_only and not (staff or owner):
        await interaction.response.send_message("❌ You do not have access to this ticket action.", ephemeral=True)
        return False

    return True


async def build_transcript_file(channel: discord.TextChannel) -> discord.File:
    lines = [
        "=" * 60,
        "HAPPY BOT TICKET TRANSCRIPT",
        "=" * 60,
        f"Channel: #{channel.name}",
        f"Generated: {utc_now()}",
        "=" * 60,
        "",
    ]

    async for msg in channel.history(limit=None, oldest_first=True):
        content = msg.clean_content or ""
        lines.append(f"[{msg.created_at.isoformat()}] {msg.author} ({msg.author.id})")
        if content:
            lines.append(f"  {content}")
        for attachment in msg.attachments:
            lines.append(f"  [Attachment] {attachment.url}")
        lines.append("")

    payload = "\n".join(lines).encode("utf-8")
    return discord.File(io.BytesIO(payload), filename=f"{safe_channel_name(channel.name)}-transcript.txt")


class TicketReasonModal(discord.ui.Modal, title="Open a Support Ticket"):
    subject = discord.ui.TextInput(
        label="Subject / Topic",
        placeholder="e.g. Billing Issue, Technical Help...",
        required=True,
        max_length=100,
    )
    reason = discord.ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        placeholder="Explain your situation...",
        required=True,
        max_length=1000,
    )

    async def on_submit(self, interaction: Interaction):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("❌ Tickets can only be created inside a server.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        config = await get_config(guild_id)
        if not config:
            await interaction.response.send_message("❌ Happy Bot is not configured. Run `/setup` first.", ephemeral=True)
            return

        if await store.is_blacklisted(guild_id, interaction.user.id):
            await interaction.response.send_message("❌ You are blacklisted from opening tickets in this server.", ephemeral=True)
            return

        open_count = await store.open_ticket_count(guild_id, interaction.user.id)
        if open_count >= config["max_tickets_per_user"]:
            await interaction.response.send_message(
                f"❌ You already have {open_count} open ticket(s). Max allowed: {config['max_tickets_per_user']}.",
                ephemeral=True,
            )
            return

        category = interaction.guild.get_channel(config["category_id"])
        staff_role = interaction.guild.get_role(config["staff_role_id"])
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("❌ The configured ticket category no longer exists.", ephemeral=True)
            return

        bot_member = interaction.guild.me
        if bot_member is None:
            await interaction.response.send_message("❌ I could not resolve my server permissions.", ephemeral=True)
            return

        ticket_number = await store.next_ticket_number(guild_id)
        channel_name = f"ticket-{ticket_number:04d}"

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
            bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, read_message_history=True),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True)

        try:
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                reason=f"Happy Bot ticket #{ticket_number:04d}",
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to create ticket channels.", ephemeral=True)
            return
        except discord.HTTPException as exc:
            log.exception("Failed to create ticket channel: %s", exc)
            await interaction.response.send_message("❌ Discord rejected the ticket creation request.", ephemeral=True)
            return

        async with store.lock:
            store.data["tickets"][str(channel.id)] = {
                "channel_id": channel.id,
                "guild_id": guild_id,
                "ticket_number": ticket_number,
                "user_id": interaction.user.id,
                "claimed_by": None,
                "priority": "Normal",
                "status": "open",
                "subject": self.subject.value,
                "reason": self.reason.value,
                "created_at": utc_now(),
                "closed_at": None,
                "closed_by": None,
            }
            store._save("tickets")

        staff_ping = staff_role.mention if staff_role else ""
        embed = make_embed(
            f"HAPPY BOT • Ticket #{ticket_number:04d}",
            f"Welcome {interaction.user.mention}!\nA staff member will assist you shortly.\n\n"
            f"**Subject:** {discord.utils.escape_markdown(self.subject.value)}\n"
            f"**Reason:** {discord.utils.escape_markdown(self.reason.value)}",
        )
        embed.add_field(name="Priority", value="🟢 Normal", inline=True)
        embed.add_field(name="Claimed By", value="Unclaimed", inline=True)

        try:
            await channel.send(content=f"{interaction.user.mention} {staff_ping}".strip(), embed=embed, view=TicketControlView())
        except discord.HTTPException:
            log.exception("Ticket was created but the initial ticket message failed: %s", channel.id)

        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)


class RenameModal(discord.ui.Modal, title="Rename Ticket"):
    new_name = discord.ui.TextInput(
        label="New channel name",
        placeholder="resolved-billing",
        required=True,
        max_length=90,
    )

    async def on_submit(self, interaction: Interaction):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return

        new_name = safe_channel_name(self.new_name.value)
        try:
            await interaction.channel.edit(name=new_name, reason=f"Ticket renamed by {interaction.user}")
            await interaction.response.send_message(f"✏️ Ticket renamed to **{new_name}**.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to rename this channel.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ Discord rejected the rename.", ephemeral=True)


class UserModal(discord.ui.Modal):
    user_id = discord.ui.TextInput(label="Discord User ID", placeholder="123456789012345678", required=True, max_length=20)

    def __init__(self, mode: str):
        super().__init__(title="Add Member to Ticket" if mode == "add" else "Remove Member from Ticket")
        self.mode = mode

    async def on_submit(self, interaction: Interaction):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return

        try:
            target_id = int(self.user_id.value.strip())
        except ValueError:
            await interaction.response.send_message("❌ Invalid Discord user ID.", ephemeral=True)
            return

        try:
            member = await interaction.guild.fetch_member(target_id)
            if self.mode == "add":
                await interaction.channel.set_permissions(
                    member,
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                )
                await interaction.response.send_message(f"➕ Added {member.mention} to this ticket.")
            else:
                if member.id == ticket["user_id"]:
                    await interaction.response.send_message("❌ You cannot remove the ticket owner.", ephemeral=True)
                    return
                await interaction.channel.set_permissions(member, overwrite=None)
                await interaction.response.send_message(f"➖ Removed {member.mention} from this ticket.")
        except discord.NotFound:
            await interaction.response.send_message("❌ User not found in this server.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to change that user's ticket access.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("❌ Discord rejected the permission change.", ephemeral=True)


class PrioritySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Low", emoji="🔵", value="Low"),
            discord.SelectOption(label="Normal", emoji="🟢", value="Normal"),
            discord.SelectOption(label="High", emoji="🟠", value="High"),
            discord.SelectOption(label="Urgent", emoji="🔴", value="Urgent"),
        ]
        super().__init__(
            placeholder="Change ticket priority...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="hb:ticket:priority",
        )

    async def callback(self, interaction: Interaction):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return

        value = self.values[0]
        async with store.lock:
            store.data["tickets"][str(interaction.channel.id)]["priority"] = value
            store._save("tickets")
        icons = {"Low": "🔵", "Normal": "🟢", "High": "🟠", "Urgent": "🔴"}
        await interaction.response.send_message(f"Priority updated to **{icons[value]} {value}**.")


class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="hb:panel:open")
    async def open_ticket(self, interaction: Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(TicketReasonModal())


class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PrioritySelect())

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="🙋", custom_id="hb:ticket:claim")
    async def claim(self, interaction: Interaction, _: discord.ui.Button):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return
        if ticket["status"] != "open":
            await interaction.response.send_message("❌ This ticket is closed.", ephemeral=True)
            return
        if ticket["claimed_by"]:
            member = interaction.guild.get_member(ticket["claimed_by"])
            await interaction.response.send_message(
                f"❌ Already claimed by {member.mention if member else 'another staff member'}.",
                ephemeral=True,
            )
            return
        async with store.lock:
            current = store.data["tickets"].get(str(interaction.channel.id))
            if not current or current.get("claimed_by") is not None:
                changed = 0
            else:
                current["claimed_by"] = interaction.user.id
                store._save("tickets")
                changed = 1
        if changed == 0:
            await interaction.response.send_message("❌ Someone else claimed this ticket first.", ephemeral=True)
            return
        await interaction.response.send_message(f"🙋 {interaction.user.mention} claimed this ticket.")

    @discord.ui.button(label="Unclaim", style=discord.ButtonStyle.secondary, emoji="↩️", custom_id="hb:ticket:unclaim")
    async def unclaim(self, interaction: Interaction, _: discord.ui.Button):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return
        if ticket["claimed_by"] != interaction.user.id and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Only the current claimer or a server manager can unclaim this ticket.", ephemeral=True)
            return
        async with store.lock:
            store.data["tickets"][str(interaction.channel.id)]["claimed_by"] = None
            store._save("tickets")
        await interaction.response.send_message("↩️ Ticket is now unclaimed.")

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.secondary, emoji="✏️", custom_id="hb:ticket:rename")
    async def rename(self, interaction: Interaction, _: discord.ui.Button):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return
        await interaction.response.send_modal(RenameModal())

    @discord.ui.button(label="Add Member", style=discord.ButtonStyle.secondary, emoji="➕", custom_id="hb:ticket:add")
    async def add_member(self, interaction: Interaction, _: discord.ui.Button):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return
        await interaction.response.send_modal(UserModal("add"))

    @discord.ui.button(label="Remove Member", style=discord.ButtonStyle.secondary, emoji="➖", custom_id="hb:ticket:remove")
    async def remove_member(self, interaction: Interaction, _: discord.ui.Button):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return
        await interaction.response.send_modal(UserModal("remove"))

    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.secondary, emoji="📄", custom_id="hb:ticket:transcript")
    async def transcript(self, interaction: Interaction, _: discord.ui.Button):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=True):
            return
        await interaction.response.defer(ephemeral=True)
        try:
            file = await build_transcript_file(interaction.channel)
            await interaction.followup.send("📄 Transcript generated.", file=file, ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send("❌ The transcript could not be uploaded.", ephemeral=True)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="hb:ticket:close")
    async def close(self, interaction: Interaction, _: discord.ui.Button):
        ticket = await require_ticket(interaction)
        if not ticket or not await can_manage_ticket(interaction, ticket, staff_only=False):
            return
        if ticket["status"] != "open":
            await interaction.response.send_message("❌ This ticket is already closed.", ephemeral=True)
            return


        async with store.lock:
            current = store.data["tickets"].get(str(interaction.channel.id))
            if not current or current.get("status") != "open":
                changed = 0
            else:
                current["status"] = "closed"
                current["closed_at"] = utc_now()
                current["closed_by"] = interaction.user.id
                store._save("tickets")
                changed = 1
        if changed == 0:
            await interaction.response.send_message("❌ This ticket was already closed.", ephemeral=True)
            return
        await interaction.response.send_message("🔒 Closing ticket and creating transcript...")

        config = await get_config(interaction.guild.id)
        transcript_channel = None
        if config and config["transcript_channel_id"]:
            candidate = interaction.guild.get_channel(config["transcript_channel_id"])
            if isinstance(candidate, discord.TextChannel):
                transcript_channel = candidate

        if transcript_channel:
            try:
                file = await build_transcript_file(interaction.channel)
                embed = make_embed(
                    f"HAPPY BOT • Ticket Log: {interaction.channel.name}",
                    f"**Closed By:** {interaction.user.mention}\n**Ticket Owner ID:** `{ticket['user_id']}`",
                    discord.Color.red(),
                )
                await transcript_channel.send(embed=embed, file=file)
            except discord.HTTPException:
                log.exception("Failed to send transcript for ticket %s", interaction.channel.id)

        await asyncio.sleep(3)
        try:
            await interaction.channel.delete(reason=f"Happy Bot ticket closed by {interaction.user}")
        except discord.NotFound:
            pass
        except discord.Forbidden:
            log.warning("Missing permission to delete ticket channel %s", interaction.channel.id)
        except discord.HTTPException:
            log.exception("Discord rejected ticket deletion for %s", interaction.channel.id)


class HappyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(PanelView())
        self.add_view(TicketControlView())


        commands_to_copy = list(self.tree.get_commands())
        self.tree.clear_commands(guild=None)
        await self.tree.sync()


        for command in commands_to_copy:
            self.tree.add_command(command)

        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)
        log.info("Synced %d slash commands to guild %s", len(synced), GUILD_ID)

    async def update_presence(self):
        server_count = len(self.guilds)
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=f"Happy Bot • {server_count} servers")
        )


bot = HappyBot()


@bot.tree.command(name="setup", description="Configure Happy Bot for this server.")
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
async def setup_cmd(
    interaction: Interaction,
    staff_role: discord.Role,
    category: discord.CategoryChannel,
    transcript_channel: Optional[discord.TextChannel] = None,
):
    if not interaction.guild:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    existing = await get_config(interaction.guild.id)
    counter = existing.get("ticket_counter", 0) if existing else 0
    max_tickets = existing.get("max_tickets_per_user", 1) if existing else 1

    async with store.lock:
        store.data["guild_configs"][str(interaction.guild.id)] = {
            "guild_id": interaction.guild.id,
            "staff_role_id": staff_role.id,
            "category_id": category.id,
            "transcript_channel_id": transcript_channel.id if transcript_channel else None,
            "max_tickets_per_user": max_tickets,
            "ticket_counter": counter,
        }
        store._save("guild_configs")

    embed = make_embed(
        "HAPPY BOT • Setup Complete",
        "The ticket system is ready.",
    )
    embed.add_field(name="Staff Role", value=staff_role.mention, inline=False)
    embed.add_field(name="Ticket Category", value=category.name, inline=False)
    embed.add_field(name="Transcript Channel", value=transcript_channel.mention if transcript_channel else "Not set", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ticket-panel", description="Send a ticket panel to a channel.")
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
async def ticket_panel_cmd(
    interaction: Interaction,
    channel: discord.TextChannel,
    title: str = "Support",
    description: str = "Need help? Open a ticket below.",
):
    if not await get_config(interaction.guild.id):
        await interaction.response.send_message("❌ Run `/setup` first.", ephemeral=True)
        return

    try:
        embed = make_embed(f"HAPPY BOT • {title}", description)
        await channel.send(embed=embed, view=PanelView())
        await interaction.response.send_message(f"✅ Ticket panel sent to {channel.mention}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to send messages in that channel.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("❌ Discord rejected the panel message.", ephemeral=True)


@bot.tree.command(name="ticket-config", description="View or update ticket configuration.")
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
async def ticket_config_cmd(
    interaction: Interaction,
    max_tickets_per_user: Optional[app_commands.Range[int, 1, 20]] = None,
    staff_role: Optional[discord.Role] = None,
    category: Optional[discord.CategoryChannel] = None,
    transcript_channel: Optional[discord.TextChannel] = None,
):
    if not interaction.guild:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return

    config = await get_config(interaction.guild.id)
    if not config:
        await interaction.response.send_message("❌ Run `/setup` first.", ephemeral=True)
        return

    new_staff = staff_role.id if staff_role else config["staff_role_id"]
    new_category = category.id if category else config["category_id"]
    new_transcript = transcript_channel.id if transcript_channel else config["transcript_channel_id"]
    new_max = int(max_tickets_per_user) if max_tickets_per_user is not None else config["max_tickets_per_user"]

    async with store.lock:
        guild_config = store.data["guild_configs"].get(str(interaction.guild.id))
        if not guild_config:
            await interaction.response.send_message("❌ Run `/setup` first.", ephemeral=True)
            return
        guild_config.update({
            "staff_role_id": new_staff,
            "category_id": new_category,
            "transcript_channel_id": new_transcript,
            "max_tickets_per_user": new_max,
        })
        store._save("guild_configs")

    embed = make_embed("HAPPY BOT • Ticket Settings", "Configuration updated.")
    staff = interaction.guild.get_role(new_staff)
    cat = interaction.guild.get_channel(new_category)
    trans = interaction.guild.get_channel(new_transcript) if new_transcript else None
    embed.add_field(name="Staff Role", value=staff.mention if staff else f"`{new_staff}`", inline=False)
    embed.add_field(name="Category", value=cat.name if cat else f"`{new_category}`", inline=False)
    embed.add_field(name="Transcript Channel", value=trans.mention if trans else "Not set", inline=False)
    embed.add_field(name="Max Open Tickets / User", value=str(new_max), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ticket-stats", description="Show ticket statistics for this server.")
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
async def ticket_stats_cmd(interaction: Interaction):
    if not interaction.guild:
        await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
        return
    config = await get_config(interaction.guild.id)
    if not config:
        await interaction.response.send_message("❌ Run `/setup` first.", ephemeral=True)
        return

    async with store.lock:
        guild_tickets = [
            t for t in store.data["tickets"].values()
            if t.get("guild_id") == interaction.guild.id
        ]
        total = len(guild_tickets)
        open_count = sum(1 for t in guild_tickets if t.get("status") == "open")
        closed_count = sum(1 for t in guild_tickets if t.get("status") == "closed")
        claimed_count = sum(1 for t in guild_tickets if t.get("claimed_by") is not None)

    embed = make_embed("HAPPY BOT • Ticket Statistics", "Current ticket data for this server.")
    embed.add_field(name="Total", value=str(total), inline=True)
    embed.add_field(name="Open", value=str(open_count), inline=True)
    embed.add_field(name="Closed", value=str(closed_count), inline=True)
    embed.add_field(name="Claimed", value=str(claimed_count), inline=True)
    embed.add_field(name="Ticket Counter", value=str(config["ticket_counter"]), inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ticket-blacklist", description="Block or unblock a member from opening tickets.")
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
])
async def ticket_blacklist_cmd(interaction: Interaction, member: discord.Member, action: app_commands.Choice[str]):
    guild_key = str(interaction.guild.id)
    user_key = str(member.id)
    async with store.lock:
        users = store.data["blacklist"].setdefault(guild_key, [])
        if action.value == "add":
            if user_key not in users:
                users.append(user_key)
            message = f"🚫 {member.mention} can no longer open tickets."
        else:
            if user_key in users:
                users.remove(user_key)
            message = f"✅ {member.mention} can open tickets again."
        store._save("blacklist")
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.error
async def on_app_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ You do not have permission to use this command."
    elif isinstance(error, app_commands.CheckFailure):
        message = "❌ You do not have permission to use this command."
    else:
        log.exception("Unhandled application command error", exc_info=error)
        message = "❌ Something went wrong while running that command."

    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except discord.HTTPException:
        log.exception("Could not send command error response")


@bot.event
async def on_ready():
    await bot.update_presence()
    log.info("Logged in as %s (%s) | %d servers", bot.user, bot.user.id if bot.user else "unknown", len(bot.guilds))


@bot.event
async def on_guild_join(guild):
    await bot.update_presence()


@bot.event
async def on_guild_remove(guild):
    await bot.update_presence()


if __name__ == "__main__":
    if TOKEN == "PASTE_YOUR_DISCORD_BOT_TOKEN_HERE":
        raise RuntimeError("Set your Discord bot token in TOKEN at the top of bot.py")
    bot.run(TOKEN)
