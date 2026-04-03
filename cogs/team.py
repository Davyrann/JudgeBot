"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""
from collections import defaultdict
import discord
import datetime
import time
from discord import app_commands, Interaction
from discord.ext import commands
from typing import TYPE_CHECKING

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
        self.member_cache: dict = {}
        self.settings_cache: dict = {}

    async def member_id_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        """
        Fungsi auto complete untuk member id

        Args:
            interaction (Interaction): Interaction dari pengguna discord
            current (str): Teks Parsial yang sedang di ketik oleh pengguna discord

        Returns:
            list[app_commands.Choice[str]]: Daftar pilihan member yang relevan dengan input user
        """
        member_id_list = []
        guild_member = self.member_cache.get(interaction.guild.id, [])
        for member in guild_member:
            if current.lower() in str(member.get("nama", "")).lower():
                member_id_list.append(
                    app_commands.Choice(
                        name=member.get("nama"),
                        value=member.get("id"))
                    )
        return member_id_list[:25]  # Batasi hasil autocomplete maksimal 25 pilihan

    @commands.hybrid_group(
        name="team",
        description="Semua command tentang team",
    )
    async def team(self, context: commands.Context) -> None:
        """
        Group command untuk team

        Args:
            context (commands.Context): Context pengguna discord
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Tolong lebih spesifik dalam execute command\n"
                            "List Command:\n"
                            "- `/team listmember` untuk melihat list member Judge\n",
                color=discord.Color.dark_red(),
            )
            await context.send(embed=embed)

    @team.command(
        name="listmember",
        description="Melihat list member Judge",
    )
    @app_commands.describe(
        guild_id = "Guild id dari sebuah team"
    )
    async def list_member(self, ctx: commands.Context, guild_id: str = None) -> discord.Message:
        """
        Command list_member untuk menampilkan seluruh member team

        Args:
            ctx (commands.Context): Context dari pengguna discord
            guild_id (str, optional): Server id jika ingin melihat team server lain. Defaults to None.

        Returns:
            discord.Message: Pesan embed list team
        """
        await ctx.defer(ephemeral=False)
        
        try:
            execution_time = int(time.time())
            target_guild_id = guild_id or (ctx.guild.id if ctx.guild else None)

            if not target_guild_id:
                return await ctx.send("Gunakan command ini di dalam server, atau masukkan ID server secara spesifik!",
                                      ephemeral=True)
            
            list_member = self.member_cache.get(int(target_guild_id), [])
            embed = discord.Embed(
                title="✨ ┃ Team Member List",
                color=discord.Color.gold(),
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
                    categories[jabatan].append(f"- **{nama}** | **{rank}** | {user.mention if user else 'Unknown User'} | Online <t:{timestamp}:R>")
                else:
                    categories["Member"].append(f"- **{nama}** | **{rank}** | {user.mention if user else 'Unknown User'} | Online <t:{timestamp}:R>")

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
            execution_duration = int(time.time()) - execution_time
            embed.set_footer(text=f"Total Team Members: {len(list_member)} | Execution Time: {execution_duration} seconds")

            return await ctx.send(embed=embed)

        except Exception as e:
            return await ctx.send(
                f"Terjadi kesalahan saat memproses data: {str(e)}",
                ephemeral=True
            )

    @commands.hybrid_group(
        name="teamadmin",
        description="Semua command admin tentang team"
    )
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(administrator=True)
    async def teamadmin(self, ctx: commands.Context):
        pass


    @teamadmin.command(
        name="addmember",
        description="Menambah member team"
    )
    @app_commands.describe(
        nama="Nama member yang ingin di tambahkan",
        rank="Rank Member di Server game",
        jabatan="Jabatan Member di team",
        user="User discord pemilik akun"
    )
    @app_commands.autocomplete(
        rank=rank_autocomplete,
        jabatan=jabatan_autocomplete
    )
    async def add_member(self, context: commands.Context, nama: str, rank: str, jabatan: str, user: discord.User = None) -> None:
        """Command addmember untuk menambahkan member ke dalam database

        Args:
            context (commands.Context): Context dari user discord
            nama (str): Nama dari member yang ingin di tambahkan
            rank (str): Rank dari member di server game
            jabatan (str): Jabaran member di team
            user (discord.User, optional): User jika user ada jika tidak None. Defaults to None.
        """
        try:
            added_time = int(time.time())
            guild_id = context.guild.id
            user_id = user.id if user else None
            add_member_status = await self.bot.database.add_team_member(
                nama=nama,
                rank=rank,
                jabatan=jabatan,
                guild_id=guild_id,
                user_id=user_id,
                time=added_time
            )
            if add_member_status["success"]:
                new_member_id = add_member_status["id"]
                new_member_data = {
                    'id': new_member_id,
                    'guild_id': guild_id,
                    'user_id': user_id,
                    'nama': nama,
                    'rank': rank,
                    'jabatan': jabatan,
                    'last_login': added_time,
                }
                if guild_id not in self.member_cache:
                    self.member_cache[guild_id] = []
                self.member_cache[guild_id].append(new_member_data)

                await context.send(
                    embed=discord.Embed(
                        title="Added Member Succes",
                        description=f"- Member: {nama}\n"
                                    f"- Rank: {rank}\n"
                                    f"- Jabatan: {jabatan}\n"
                                    f"- User Discord: {user.name}#{user.display_name if user else 'Unknown User'}\n"
                                    f"- Mention: {user.mention if user else 'Unknown User'}\n"
                                    f"- Added Time: <t:{added_time}:F>\n"
                                    f"Berhasil di tambahkan ke database",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.green(),
                    )
                )
            else:
                await context.send(
                    embed=discord.Embed(
                        title="Tambah Member Gagal",
                        description=f"Dengan error {add_member_status['error']}",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.dark_red(),
                    )
                )
        except Exception as e:
            await context.send(
                f"Terjadi error {e}",
                ephemeral=True,
            )

    @teamadmin.command(
        name="editmember",
        description="Mengedit member team"
    )
    @app_commands.describe(
        member_id="Member ID  dari member yang ingin di edit",
        nama="Nama Member",
        rank="Rank Member di Server",
        jabatan="Jabatan Member di team",
        user="User discord pemilik akun"
    )
    @app_commands.autocomplete(
        member_id=member_id_autocomplete,
        rank=rank_autocomplete,
        jabatan=jabatan_autocomplete,
    )
    async def edit_member(self, context: commands.Context, member_id: int, nama: str, rank: str, jabatan: str,
                          user: discord.User = None) -> None:
        try:
            guild_id = context.guild.id
            user_id = user.id if user else None

            # 1. Update ke Database
            edit_member_status = await self.bot.database.edit_team_member(
                member_id=member_id,
                nama=nama,
                rank=rank,
                jabatan=jabatan,
                guild_id=guild_id,
                user_id=user_id
            )

            if edit_member_status["success"]:
                # 2. Siapkan data baru untuk di-cache
                # Pastikan menggunakan ID dari database jika fungsi DB-mu me-return ID, atau pakai member_id dari argumen
                target_id = edit_member_status.get("id", member_id)

                new_member_data = {
                    'id': target_id,
                    'guild_id': guild_id,
                    'user_id': user_id,
                    'nama': nama,
                    'rank': rank,
                    'jabatan': jabatan
                }
                
                if guild_id in self.member_cache:
                    member_found = False
                    for index, member_data in enumerate(self.member_cache[guild_id]):
                        if member_data.get('id') == target_id:
                            new_member_data['last_login'] = member_data['last_login']
                            self.member_cache[guild_id][index] = new_member_data
                            member_found = True
                            break

                    if not member_found:
                        self.member_cache[guild_id].append(new_member_data)
                else:
                    self.member_cache[guild_id] = [new_member_data]

                # 4. Kirim Pesan Sukses
                await context.send(
                    embed=discord.Embed(
                        title="Edited Member",
                        description=f"- Member: {nama}\n"
                                    f"- Rank: {rank}\n"
                                    f"- Jabatan: {jabatan}\n"
                                    f"- User Discord: {user.name if user else 'Unknown User'}\n"
                                    f"- Mention: {user.mention if user else 'Unknown User'}\n"
                                    f"Berhasil diedit di database dan memori",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.green(),
                    )
                )
            
            else:
                await context.send(
                    embed=discord.Embed(
                        title="Edit Member Gagal",
                        description=f"Dengan error: {edit_member_status['error']}",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.red(),
                    )
                )
        
        except Exception as e:
            await context.send(
                f"Terjadi kesalahan: {str(e)}",
                ephemeral=True
            )

    @teamadmin.command(
        name="removemember",
        description="menghapus member team"
    )
    @app_commands.describe(
        member_id="Nama Member",
    )
    @app_commands.autocomplete(
        member_id=member_id_autocomplete,
    )
    async def remove_member(self, context: commands.Context, member_id: int) -> None:
        try:
            
            remove_member_status = await self.bot.database.remove_team_member(member_id)
            guild_member = self.member_cache.get(context.guild.id, [])
            user = None

            for member in guild_member:
                if member.get("id") == member_id:
                    user = member
                    break

            nama_target = user.get("nama", f"Unknown (ID: {member_id})") if user else f"Unknown (ID: {member_id})"

            if remove_member_status["success"]:

                if user in guild_member:
                    guild_member.remove(user)
                    self.member_cache[context.guild.id] = guild_member

                await context.send(
                    embed=discord.Embed(
                        title="Removed Member",
                        description=f"Member: {nama_target}\n"
                                    f"Telah berhasil **DIHAPUS** dari database",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.green(),
                    )
                )
            
            else:
                await context.send(
                    embed=discord.Embed(
                        title="Removed Member",
                        description=f"Member: {nama_target}\n"
                                    f"gagal **DIHAPUS** dari database",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.dark_red(),
                    )
                )
        except discord.Forbidden as e:
            await context.send(
                f"Sepertinya saya kurang akses untuk mengirim pesan disini"
                f"Error: {e}",
                ephemeral=True
            )

    @teamadmin.command(
        name='settings',
        description="Team settings"
    )
    @app_commands.describe(
        settings_name="Nama setting yang ingin diubah",
        channel="Nilai setting yang ingin diubah"
    )
    @app_commands.choices(
        settings_name=[
        app_commands.Choice(name="Channel Notif Member Join/Leave", value="member_join_alert"),
        app_commands.Choice(name="Channel Join/Leave Game", value="leave_join_channel")
    ])
    async def team_channel(self, context: commands.Context, settings_name: app_commands.Choice[str], channel: discord.TextChannel) -> None:
        
        guild_id = context.guild.id
        kolom_database = settings_name.value
        nama_tampilan = settings_name.name
        result = await self.bot.database.team_settings(guild_id, kolom_database, channel.id)
    
        if result["success"]:
            if guild_id not in self.settings_cache:
                self.settings_cache[guild_id] = {}

            self.settings_cache[guild_id][kolom_database] = channel.id

            await context.send(
                embed=discord.Embed(
                    title="Team Setup",
                    description=f"Settings Berhasil di ubah\n"
                                f"- Nama Settings: {nama_tampilan}\n"
                                f"- Value: {kolom_database}",
                )
            )
        else:
            await context.send(
                embed=discord.Embed(
                    title="Team Setup",
                    description=f"Gagal mengubah settings\n"
                                f"Error: {result['error']}",
                )
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild:
            return

        guild_id = message.guild.id
        guild_settings = self.settings_cache.get(guild_id)

        if not guild_settings:
            return

        log_channel_id = guild_settings.get('leave_join_channel')
        if not log_channel_id or message.channel.id != log_channel_id:
            return

        if not (message.embeds and message.embeds[0].author and message.embeds[0].author.name):
            return

        author_name = message.embeds[0].author.name

        is_join = 'joined the server' in author_name
        is_leave = 'left the server' in author_name

        if not (is_join or is_leave):
            return

        player_name = author_name.split(" ")[0]
        team_member = self.member_cache.get(guild_id, [])

        if not team_member:
            return

        member_yang_login = None
        for member in team_member:
            if member.get('nama') == player_name:
                member_yang_login = member
                break

        if member_yang_login:
            event_time = int(time.time())
            nama = member_yang_login.get('nama')
            rank = member_yang_login.get('rank')
            jabatan = member_yang_login.get('jabatan')
            member_id = member_yang_login.get('id')
            user = self.bot.get_user(member_yang_login.get('user_id')) if member_yang_login.get('user_id') else None

            if is_join:
                embed_title = ':ringed_planet: | Team Member Playing'
                status = 'Online'
                embed_color = discord.Color.green()
            else:
                embed_title = ':ringed_planet: | Team Member Leaving MarlinMC'
                status = 'Offline'
                result = await self.bot.database.last_online_update(last_login=event_time,member_id=member_id)
                if not result.get("success"):
                    self.bot.logger.error(f"Gagal update last online untuk member ID {member_id}: {result.get('error')}")
                member_yang_login['last_login'] = event_time
                embed_color = discord.Color.red()

            embed = discord.Embed(
                title=embed_title,
                description=f"- Member: **{nama}**\n"
                            f"- Rank: `{rank}`\n"
                            f"- Jabatan: `{jabatan}`\n"
                            f"- Mention: {user.mention if user else "Unknown User Discord"}\n"
                            f"- {status}: <t:{event_time}:R>",
                color=embed_color
            )

            alert_channel_id = guild_settings.get('member_join_alert')

            if alert_channel_id:
                alert_channel = self.bot.get_channel(alert_channel_id)
                if alert_channel:
                    await alert_channel.send(embed=embed)

    async def cog_load(self) -> None:
        self.member_cache = defaultdict(list)  # Siapkan wadah kosong yang aman

        db_members = await self.bot.database.get_team_member()

        if db_members.get('success') and db_members.get('result'):
            for row in db_members['result']:
                guild_id = row['guild_id']
                self.member_cache[guild_id].append(dict(row))

            self.bot.logger.info(f"✅ Team member berhasil diload untuk {len(self.member_cache)} guild.")
        else:
            self.bot.logger.info("⚠️ Belum ada data team member di database.")

        self.settings_cache = {}  # Cukup pakai dictionary biasa

        db_settings = await self.bot.database.get_team_settings()

        if db_settings.get('success') and db_settings.get('result'):
            for row in db_settings['result']:
                guild_id = row['guild_id']
                self.settings_cache[guild_id] = dict(row)

            self.bot.logger.info(f"✅ Team settings berhasil diload untuk {len(self.settings_cache)} guild.")
        else:
            self.bot.logger.info("⚠️ Belum ada data team settings di database.")

async def setup(bot) -> None:
    await bot.add_cog(TeamManagement(bot))
