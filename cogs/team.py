"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""
import random
import discord
import datetime
import time
from discord import User, app_commands, Interaction
from discord.ext import commands
from typing import TYPE_CHECKING
from database import models

if TYPE_CHECKING:
    from bot import DiscordBot

async def rank_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
    """
    Fungsi autocomplete untuk menyarankan daftar rank yang tersedia.

    Args:
        interaction: Interaksi dari Discord saat command dijalankan.
        current: Teks parsial yang sedang diketik oleh user di menu pilihan.

    Returns:
        Daftar pilihan rank (maksimal 25) yang relevan dengan input `current`.
    """
    ranks = ["Explorer", "Fisherman", "Bubble", "Coral", "Atlantis",
             "Orca", "Wave", "Aqua", "Pirate", "Siren", "Poseidon",
             "Tiktok"]
    return [
        app_commands.Choice(name=rank, value=rank)
        for rank in ranks if current.lower() in rank.lower()
    ]

async def jabatan_autocomplete(interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
    """
    Fungsi autocomplete untuk menyarankan jabatan yang tersedia di team

    Args:
        interaction (Interaction): Interaksi pengguna discord
        current (str): Teks parsial yang sedang diketik oleh pengguna discord

    Returns:
        list[app_commands.Choice[str]]: Daftar pilihan jabatan yang relevan dengan input user
    """
    jabatans = ["Leader", "Co-Leader", "Admin", "Member"]
    return [
        app_commands.Choice(name=jabatan, value=jabatan)
        for jabatan in jabatans if current.lower() in jabatan.lower()
    ]

class TeamManagement(commands.Cog, name="teammanagement"):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.team_cache: dict[int, models.Team] = {}
        self.member_cache: dict[str, models.TeamMember] = {}
    
    team_group = app_commands.Group(name="team",
                                    description="Command semua hal tentang team")
    
    @team_group.command(name="list_member")
    async def list_member_slash(self, interaction: Interaction, team_id: int) -> None:
        """akan mengirim list member berdasarkan nama_team

        Args:
            interaction (Interaction): Interaction dari pengguna discord
            team_id (str): ID tim yang ingin dilihat membernya

        Returns:
            _type_: _description_
        """
        if not interaction.guild:
            await interaction.response.send_message("Gunakan command ini di dalam server!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)
        time_start = int(time.time())
        
        list_member = [member for member in self.member_cache.values() if member.get("team_id") == int(team_id)]
        team_data = self.team_cache[team_id]
        
        embed = discord.Embed(
            title=f"✨ ┃ Team {team_data.get('name', 'Unknown')} Member List",
            color=random.choice([discord.Color.gold(), discord.Color.blue(), discord.Color.green()]),
            timestamp=datetime.datetime.now(datetime.UTC),
        )

        categories = {"Leader": [], "Co-Leader": [], "Admin": [], "Member": []}

        for member in list_member:
            nama = member.get("nama", "Unknown")
            jabatan = member.get("jabatan", "Member")
            rank = member.get("rank", "Unranked")
            user_id = member.get("user_id", 0)
            user = None
            if user_id:
                user = self.bot.get_user(int(user_id)) # Sangat cepat karena mengambil dari memori bot
                if not user:
                    try:
                        # Hanya hit API jika user tidak ada di memori
                        user = await self.bot.fetch_user(int(user_id))
                    except discord.NotFound:
                        user = None
            timestamp = member.get("last_login", 0)

            if jabatan in categories:
                categories[jabatan].append(f"- **{nama}** | **{rank}** | {user.mention if user else 'Unknown User'} | Online <t:{int(timestamp.timestamp())}:R>")
            else:
                categories["Member"].append(f"- **{nama}** | **{rank}** | {user.mention if user else 'Unknown User'} | Online <t:{int(timestamp.timestamp())}:R>")

        for role, members in categories.items():
            if members:  # Hanya buat field jika ada isinya
                role_icons = {
                    "Leader": ":crown:",
                    "Co-Leader": ":shield:",
                    "Admin": ":star:",
                    "Member": ":bust_in_silhouette:"
                }
                icon = role_icons.get(role, ":bust_in_silhouette:")

                embed.add_field(
                    name=f"{icon} ┃ `{role}`",
                    value="\n".join(members),
                    inline=False
                )
        time_end = int(time.time())
        execution_duration = time_end - time_start
        embed.set_footer(text=f"Total Team Members: {len(list_member)} | Execution Time: {execution_duration} seconds")

        await interaction.followup.send(embed=embed)

    @team_group.command(name="list")
    async def list_team_slash(self, interaction: Interaction) -> None:
        """akan mengirim list team yang ada di server

        Args:
            interaction (Interaction): Interaction dari pengguna discord

        Returns:
            _type_: _description_
        """
        if not interaction.guild:
            await interaction.response.send_message("Gunakan command ini di dalam server!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=False)
        
        embed = discord.Embed(
            title="✨ ┃ Team List",
            color=random.choice([discord.Color.gold(), discord.Color.blue(), discord.Color.green()]),
            timestamp=datetime.datetime.now(datetime.UTC),
        )

        for team in self.team_cache.values():
            team_name = team.get("name", "Unknown")
            team_id = team.get("team_id", "Unknown")
            created_at = team.get("created_at", "Unknown")
            user_id = team.get("created_by", "Unknown")
            user = self.bot.get_user(user_id)
            embed.description = "".join([embed.description or "", f"- **{team_name}** (ID: {team_id}) oleh {user.mention if user else 'Unknown User'} | Created At: <t:{int(created_at.timestamp())}:f>\n"])

        await interaction.followup.send(embed=embed)

    team_admin_group = app_commands.Group(name="admin",
                                          parent=team_group,
                                          description="Command admin untuk team",
                                          default_permissions=discord.Permissions(administrator=True))
    
    @team_admin_group.command(name="add_team",
                              description="Membuat team baru")
    @app_commands.describe(name="Nama team yang ingin dibuat")
    async def add_team(self, interaction: Interaction, name: str) -> None:
        await interaction.response.defer()
        created_by = interaction.user.id
        try:
            resp = await self.bot.database.team.add_team(name=name, created_by=created_by)
            if resp["success"]:
                team_data = resp["data"]
                if team_data:
                    self.team_cache[team_data['team_id']] = team_data
                    await interaction.followup.send(f"Team '{name}' berhasil dibuat dengan ID: {team_data['team_id']}")
                else:
                    await interaction.followup.send("Team berhasil dibuat, tetapi data tim tidak ditemukan dalam respons.")
            else:
                await interaction.followup.send(f"Gagal membuat team: {resp['error']}")
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan saat membuat team: {str(e)}")

    @team_admin_group.command(name="remove_team",
                              description="Menghapus team yang sudah ada")
    @app_commands.describe(team_id="ID team yang ingin dihapus")
    async def remove_team(self, interaction: Interaction, team_id: int) -> None:
        await interaction.response.defer()
        try:
            resp = await self.bot.database.team.remove_team(team_id=team_id)
            if resp["success"] and resp["data"]:
                data = resp["data"]
                self.team_cache.pop(team_id, None)
                embed = discord.Embed(title="Team Deleted",
                                      description=f"- Team ID: {team_id}\n- Team Name: {data.get('name', 'Unknown')}\n- Created At: <t:{int(data.get('created_at', datetime.datetime.now()).timestamp())}:f>",
                                      color=discord.Color.green(),
                                      timestamp=datetime.datetime.now(datetime.UTC))
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title="Failed to Delete Team", description=f"Gagal menghapus team dengan ID '{team_id}'. Error: {resp['error']}", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan saat menghapus team: {str(e)}")

    @team_admin_group.command(name="edit_team",
                              description="Mengedit nama team yang sudah ada")
    @app_commands.describe(team_id="ID team yang ingin diedit", new_name="Nama baru untuk team")
    async def edit_team(self, interaction: Interaction, team_id: int, new_name: str) -> None:
        await interaction.response.defer()
        try:
            resp = await self.bot.database.team.edit_team(team_id=team_id, new_name=new_name)
            if resp["success"] and resp["data"]:
                data = resp["data"]
                self.team_cache[team_id] = data
                embed = discord.Embed(title="Team Updated",
                                      description=f"- Team ID: {team_id}\n- New Name: {data.get('name', 'Unknown')}\n- Created At: <t:{int(data.get('created_at', datetime.datetime.now()).timestamp())}:f>",
                                      color=discord.Color.green(),
                                      timestamp=datetime.datetime.now(datetime.UTC))
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title="Failed to Update Team", description=f"Gagal mengedit team dengan ID '{team_id}'. Error: {resp['error']}", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Terjadi kesalahan saat mengedit team: {str(e)}")

    @team_admin_group.command(name="add_member",
                              description="Menambahkan member ke dalam team")
    @app_commands.describe(nama="Nama member yang ingin ditambahkan",
                           rank="Rank member di server game",
                           jabatan="Jabatan member di team",
                           user_discord="User discord pemilik akun (opsional)",
                           team_id="ID team tempat member akan ditambahkan")
    @app_commands.autocomplete(rank=rank_autocomplete,
                               jabatan=jabatan_autocomplete)
    async def add_member(self, inteaction: Interaction, nama: str, rank: str, jabatan: str, user_discord: User | None, team_id: int):
        await inteaction.response.defer()
        user_id = user_discord.id if user_discord else None
        try:
            resp = await self.bot.database.team.add_member(team_id=team_id, nama=nama, rank=rank, jabatan=jabatan, user_id=user_id)
            if resp["success"] and resp["data"]:
                member_data = resp["data"]
                if team_id in self.team_cache:
                    self.member_cache[member_data['nama']] = member_data
                    embed = discord.Embed(title="Member Added",
                                          description=f"- Nama: {nama}\n- Rank: {rank}\n- Jabatan: {jabatan}\n- User Discord: {user_discord.mention if user_discord else 'Unknown User'}\n- Team ID: {team_id}",
                                          color=discord.Color.green(),
                                          timestamp=datetime.datetime.now(datetime.UTC),)
                    await inteaction.followup.send(embed=embed)
                else:
                    await inteaction.followup.send(f"Member berhasil ditambahkan, tetapi data tim dengan ID '{team_id}' tidak ditemukan dalam cache.")
            else:
                await inteaction.followup.send(f"Gagal menambahkan member: {resp['error']}")
        except Exception as e:
            await inteaction.followup.send(f"Terjadi kesalahan saat menambahkan member: {str(e)}")
    
    @team_admin_group.command(name="edit_member",
                              description="Mengedit data member yang sudah ada")
    @app_commands.describe(nama="Nama member yang ingin diedit",
                           rank="Rank member di server game",
                           jabatan="Jabatan member di team",
                           user_discord="User discord pemilik akun (opsional)",
                           team_id="ID team tempat member akan diedit",
                           member_id="ID member yang ingin diedit")
    @app_commands.autocomplete(rank=rank_autocomplete,
                               jabatan=jabatan_autocomplete)
    async def edit_member(self, interaction: Interaction, team_id: int, member_id: int, nama: str, rank: str, jabatan: str, user_discord: User | None):
        await interaction.response.defer()
        user_id = user_discord.id if user_discord else None
        
        try:
            old_data = None
            for m in self.member_cache.values():
                if m['id'] == member_id:
                    old_data = m
                    break

            # 2. Jalankan Update Database
            resp = await self.bot.database.team.edit_member(
                member_id=member_id, 
                team_id=team_id, 
                nama=nama, 
                rank=rank, 
                jabatan=jabatan, 
                user_id=user_id
            )

            if not resp.get("success"):
                return await interaction.followup.send(f"❌ Gagal: {resp.get('error')}")

            if old_data and old_data["nama"] in self.member_cache and resp["data"]:
                old_name = old_data['nama']
                self.member_cache.pop(old_name)
                new_data = resp["data"]
                self.member_cache[new_data['nama']] = new_data

            embed = discord.Embed(title=f"Member __{nama}__ Updated",
                                  description=f"- Nama: {nama}\n- Rank: {rank}\n- Jabatan: {jabatan}\n- User Discord: {user_discord.mention if user_discord else 'Unknown User'}\n- Team ID: {team_id}",
                                  color=discord.Color.green(),
                                  timestamp=datetime.datetime.now(datetime.UTC))
            await interaction.followup.send(embed=embed)

        except Exception as e:
            self.bot.logger.error(f"Error edit_member: {e}")
            await interaction.followup.send("Terjadi kesalahan sistem.")

    @team_admin_group.command(name="remove_member",
                                description="Menghapus member dari team")
    @app_commands.describe(team_id="ID team tempat member berada",
                           member_id="ID member yang ingin dihapus")
    async def remove_member(self, interaction: Interaction, team_id: int, member_id: int) -> None:
        await interaction.response.defer()
        try:
            owner_team = self.team_cache.get(team_id)
            if owner_team and interaction.user.id != owner_team.get("created_by", 0):
                await interaction.followup.send(embed=discord.Embed(title="Permission Denied", description="Hanya creator team yang bisa menghapus member!", color=discord.Color.red()))
                return

            resp = await self.bot.database.team.remove_member(member_id=member_id)
            if resp["success"] and resp["data"]:
                member_data = resp["data"]
                self.member_cache.pop(member_data['nama'], None)
                
                embed = discord.Embed(title="Member Deleted",
                                      description=f"- Nama: {member_data['nama']}\n- Rank: {member_data['rank']}\n- Jabatan: {member_data['jabatan']}\n- User Discord: <@{member_data.get('user_id', 'Unknown')}>\n- Team ID: {member_data['team_id']}",
                                      color=discord.Color.green())
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title="Failed to Delete Member", description=f"Gagal menghapus member dengan ID '{member_id}'. Error: {resp['error']}", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
        except Exception as e:
            self.bot.logger.error(f"Error remove_member: {e}")

    @list_member_slash.autocomplete("team_id")
    @remove_team.autocomplete("team_id")
    @edit_team.autocomplete("team_id")
    @add_member.autocomplete("team_id")
    @edit_member.autocomplete("team_id")
    @remove_member.autocomplete("team_id")
    async def list_member_team_id_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        """
        Fungsi autocomplete untuk team id di command list_member

        Args:
            interaction (Interaction): Interaction dari pengguna discord
            current (str): Teks parsial yang sedang diketik oleh pengguna discord

        Returns:
            list[app_commands.Choice[str]]: Daftar pilihan team id yang relevan dengan input user
        """
        team_id_list = []
        for team_id, team_data in self.team_cache.items():
            if current.lower() in team_data.get("name", "").lower():
                team_id_list.append(
                    app_commands.Choice(
                        name=f"{team_data.get('name', 'Unknown')} (ID: {team_id})",
                        value=str(team_id))
                    )
        return team_id_list[:25]


    @edit_member.autocomplete('member_id')
    @remove_member.autocomplete('member_id')
    async def member_autocomplete(self, interaction: discord.Interaction, current: str):
        selected_team_id = interaction.namespace.team_id
        
        if not selected_team_id:
            return [app_commands.Choice(name="⚠️ Pilih Tim terlebih dahulu!", value=-1)]

        team_member = [member for member in self.member_cache.values() if member.get("team_id") == int(selected_team_id)]
        
        choices = []
        for member_name in team_member:
            if current.lower() in member_name['nama'].lower():
                choices.append(
                    app_commands.Choice(name=member_name['nama'], value=member_name['id'])
                )
        
        return choices[:25]

    async def _member_login_handler(self, message: discord.Message, team_log_channel_id: int | None):
        if not team_log_channel_id or not message.embeds:
            return
        
        embed_data = message.embeds[0]
        if not (embed_data.author and embed_data.author.name):
            return
        author_text = embed_data.author.name.lower()
        
        is_join = "joined" in author_text
        is_leave = "left" in author_text
        
        if not is_join and not is_leave:
            return
        
        player_name = embed_data.author.name.split(" ")[0]
        member_data = self.member_cache.get(player_name)
        
        if member_data:
            resp = await self.bot.database.team.member_login(member_id=member_data["id"])
            
            if resp["success"] and resp["data"]:
                db_data = resp["data"]
                member_data["last_login"] = db_data.get("last_login", member_data.get("last_login"))
                self.member_cache[player_name] = member_data
                team_data = self.team_cache.get(member_data["team_id"], {})
                if is_join:
                    embed_title = " | Member Joined"
                    status_text = "Online"
                    embed_color = discord.Color.green()
                else:
                    embed_title = " | Member Left"
                    status_text = "Offline"
                    embed_color = discord.Color.red()
                
                user_mention = f"<@{member_data['user_id']}>" if member_data.get('user_id') else "`Not Linked`"
                ts_int = int(member_data['last_login'].timestamp())
                
                embed = discord.Embed(
                    description=(
                        f"- Member: **{member_data['nama']}**\n"
                        f"- Rank: `{member_data['rank']}`\n"
                        f"- Jabatan: `{member_data['jabatan']}`\n"
                        f"- Discord: {user_mention}\n"
                        f"- Team ID: `{member_data['team_id']}`\n"
                        f"- Team Name: `{team_data.get('name', 'Unknown')}`\n"
                        f"- Status: **{status_text}**\n"
                        f"- Waktu: <t:{ts_int}:R>"
                    ),
                    
                    color=embed_color,
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.set_author(name=embed_title, icon_url=embed_data.author.icon_url) 
                embed.set_footer(text=f"Member ID: {member_data['id']}")
                
                channel = self.bot.get_channel(team_log_channel_id)
                if isinstance(channel, discord.TextChannel):
                    await channel.send(embed=embed)
                
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return
        
        settings = self.bot.guild_settings_cache.get(message.guild.id, {}).get("team", {})
        player_log_channel_id = settings.get("player_log_channel_id")
        team_log_channel_id = settings.get("team_log_channel_id")
        if message.channel.id == player_log_channel_id:
            await self._member_login_handler(message, team_log_channel_id=team_log_channel_id)
        
        
        
    async def cog_load(self) -> None:
        resp = await self.bot.database.get_team_member()
        if not resp["success"]:
            self.bot.logger.warning("⚠️ Gagal memuat data team member dari database.\nError: %s", resp["error"])
            return
        
        self.member_cache = resp["team_member_data"] or {}
        self.team_cache = resp["team_data"] or {}
        self.bot.logger.info("✅ Berhasil memuat data team member dari database. Total members: %d", len(self.member_cache))
        self.bot.logger.info("✅ Berhasil memuat data team dari database. Total teams: %d", len(self.team_cache))
        
async def setup(bot) -> None:
    await bot.add_cog(TeamManagement(bot))
