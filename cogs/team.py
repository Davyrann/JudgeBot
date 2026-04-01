"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""
from collections import defaultdict

import discord
import datetime
import logging
from discord import app_commands, Message
from discord.ext import commands

async def rank_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """
    Fungsi untuk autocomplete rank member
    :param interaction: Interaksi dari pengguna
    :param current: Input saat ini
    :return: List of app_commands.Choice
    """
    ranks = ["Explorer", "Fisherman", "Bubble", "Coral", "Atlantis",
             "Orca", "Wave", "Aqua", "Pirate", "Siren", "Poseidon",
             "Tiktok"]
    return [
        app_commands.Choice(name=rank, value=rank)
        for rank in ranks if current.lower() in rank.lower()
    ]

async def jabatan_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """
    Fungsi untuk autocomplete jabatan member
    :param interaction: Interaksi dari pengguna
    :param current: Input saat ini
    :return:
    """
    jabatans = ["Leader", "Co-Leader", "Admin", "Member"]
    return [
        app_commands.Choice(name=jabatan, value=jabatan)
        for jabatan in jabatans if current.lower() in jabatan.lower()
    ]

class TeamManagement(commands.Cog, name="teammanagement"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.member_cache: dict = {}
        self.settings_cache: dict = {}

    async def member_id_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        member_id_list = await self.bot.database.get_all_member_id()
        return [
            app_commands.Choice(name=member[1], value=member[0])
            for member in member_id_list if current.lower() in member[1].lower()
        ]

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.hybrid_group(
        name="team",
        description="Semua command tentang team",
    )
    async def team(self, context: commands.Context) -> None:
        """
        Manage warnings of a user on a server.

        :param context: The hybrid command context.
        """
        if context.invoked_subcommand is None:
            embed = discord.Embed(
                description="Tolong lebih spesifik dalam execute command\n"
                            "List Command:\n"
                            "- `/team listmember` untuk melihat list member Judge\n"
                            "- `/team addmember` untuk menambah member Judge\n"
                            "- `/team removemember` untuk menghapus member Judge\n"
                            "- `/team editmember` untuk menedit member Judge",
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
        Command untuk menampilkan daftar member tim berdasarkan jabatan.
        """
        try:
            target_guild_id = guild_id or (ctx.guild.id if ctx.guild else None)

            if not target_guild_id:
                return await ctx.send("Gunakan command ini di dalam server, atau masukkan ID server secara spesifik!",
                                      ephemeral=True)

            list_member = self.member_cache.get(int(target_guild_id), [])

            embed = discord.Embed(
                title="✨ ┃ Judge Team Roster",
                color=discord.Color.gold(),
                timestamp=datetime.datetime.now(datetime.UTC),
            )

            categories = {"Leader": [], "Co-Leader": [], "Admin": [], "Member": []}

            for member in list_member:
                nama = member.get("nama", "Unknown")
                jabatan = member.get("jabatan", "Member")
                rank = member.get("rank", "Unranked")
                user_id = member.get("user_id", 0)

                if jabatan in categories:
                    categories[jabatan].append(f"- **{nama}** | **{rank}** | <@{user_id}>")
                else:
                    categories["Member"].append(f"- **{nama}** | **{rank}** | <@{user_id}>")

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

            embed.set_footer(text=f"Total Player: {len(list_member)}")

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
        nama="Nama Member",
        rank="Rank Member di Server",
        jabatan="Jabatan Member di team",
        user="User discord pemilik akun"
    )
    @app_commands.autocomplete(
        rank=rank_autocomplete,
        jabatan=jabatan_autocomplete
    )
    async def add_member(self, context: commands.Context, nama: str, rank: str, jabatan: str, user: discord.User) -> None:
        """
        Menambah member team
        :param user: user discord yang mempunyai nickname tersebut
        :param jabatan: Jabatan memberdi team
        :param context: Interaksi dari member discord
        :param nama: Nama Member dalam str
        :param rank: Rank Member dalam str
        :return: None
        """
        try:
            guild_id = context.guild.id
            add_member_status = await self.bot.database.add_team_member(
                nama=nama,
                rank=rank,
                jabatan=jabatan,
                guild_id=guild_id,
                user_id=user.id
            )
            if add_member_status["success"]:
                new_member_id = add_member_status["id"]
                new_member_data = {
                    'id': new_member_id,
                    'guild_id': guild_id,
                    'user_id': user.id,
                    'nama': nama,
                    'rank': rank,
                    'jabatan': jabatan
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
                                    f"- User Discord: {user.name}#{user.display_name}\n"
                                    f"- Mention: <@{user.id}>\n"
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
        except discord.Forbidden:
            await context.send(
                "Sepertinya saya tidak bisa mengirim pesan disini",
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
    async def edit_member(self, context: commands.Context, member_id: int, nama: str, rank: str, jabatan: str, user: discord.User) -> None:
        try:
            edit_member_status = await self.bot.database.edit_team_member(member_id=member_id,
                                                                          nama=nama,
                                                                          rank=rank,
                                                                          jabatan=jabatan,
                                                                          guild_id=context.guild.id,
                                                                          user_id=user.id)
            if edit_member_status["success"]:
                await context.send(
                    embed=discord.Embed(
                        title="Edited Member",
                        description=f"Member: {nama}\n"
                                    f"- Rank: {rank}\n"
                                    f"- Jabatan: {jabatan}\n"
                                    f"- User Discord: {user.name}#{user.display_name}\n"
                                    f"- Mention: <@{user.id}>\n"
                                    f"Berhasil di edit di database",
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
                        color=discord.Color.dark_red(),
                    )
                )
        except discord.Forbidden:
            await context.send(
                "Sepertinya saya tidak bisa mengirim pesan disini",
                ephemeral=True,
            )


    @teamadmin.command(
        name="removemember",
        description="menghapus member team"
    )
    @app_commands.describe(
        nama="Nama Member",
    )
    @app_commands.autocomplete(
        nama=member_id_autocomplete,
    )
    async def remove_member(self, context: commands.Context, nama: int) -> None:
        try:
            remove_member_status = await self.bot.database.remove_team_member(nama)
            if remove_member_status["success"]:
                await context.send(
                    embed=discord.Embed(
                        title="Removed Member",
                        description=f"Member: {nama}\n"
                                    f"Telah berhasil **DIHAPUS** dari database",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.green(),
                    )
                )
            else:
                await context.send(
                    embed=discord.Embed(
                        title="Removed Member",
                        description=f"Member: {nama}\n"
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

        # 1. CEK CACHE SETTINGS: Apakah server ini sudah melakukan /setup?
        guild_settings = self.settings_cache.get(guild_id)
        if not guild_settings:
            return  # Abaikan jika server belum disetup

        # 2. CEK CHANNEL LOG: Pastikan pesan ini benar-benar dikirim di channel 'leave_join_channel'
        log_channel_id = guild_settings.get('leave_join_channel')
        if not log_channel_id or message.channel.id != log_channel_id:
            return  # Abaikan jika pesan dikirim di channel lain

        # 3. Pastikan pesan punya embed dan memiliki author name (Mendeteksi pesan bot log MC)
        if not (message.embeds and message.embeds[0].author and message.embeds[0].author.name):
            return

        author_name = message.embeds[0].author.name

        # 4. Cek apakah ini event Join atau Leave
        is_join = 'joined the server' in author_name
        is_leave = 'left the server' in author_name

        # Jika bukan pesan join/leave, langsung hentikan
        if not (is_join or is_leave):
            return

        # 5. Ekstrak nama dan cari di cache member
        player_name = author_name.split(" ")[0]
        team_member = self.member_cache.get(guild_id, [])

        if not team_member:
            return

        # Cari player di dalam cache
        member_yang_login = None
        for member in team_member:
            if member.get('nama') == player_name:
                member_yang_login = member
                break

        # 6. Jika member tim ditemukan, buat embed dan kirim ke channel Alert!
        if member_yang_login:
            nama = member_yang_login.get('nama')
            rank = member_yang_login.get('rank')
            jabatan = member_yang_login.get('jabatan')
            user_id = member_yang_login.get('user_id')

            # Sesuaikan Judul dan Warna Embed berdasarkan event-nya
            if is_join:
                embed_title = ':ringed_planet: | Judge Member Playing'
                embed_color = discord.Color.green()
            else:
                embed_title = ':ringed_planet: | Judge Member Leaving MarlinMC'
                embed_color = discord.Color.red()

            embed = discord.Embed(
                title=embed_title,
                description=f"- Member: **{nama}**\n"
                            f"- Rank: `{rank}`\n"
                            f"- Jabatan: `{jabatan}`\n"
                            f"- Mention: <@{user_id}>\n",
                color=embed_color
            )

            # 7. Ambil channel 'member_join_alert' dan KIRIM pesannya
            alert_channel_id = guild_settings.get('member_join_alert')

            if alert_channel_id:
                # Gunakan get_channel agar mengambil dari cache bot (lebih cepat)
                alert_channel = self.bot.get_channel(alert_channel_id)
                if alert_channel:
                    await alert_channel.send(embed=embed)

    async def cog_load(self) -> None:
        # ==========================================
        # 1. LOAD TEAM MEMBERS (1 Guild = Banyak Member)
        # ==========================================
        self.member_cache = defaultdict(list)  # Siapkan wadah kosong yang aman

        db_members = await self.bot.database.get_team_member()

        if db_members.get('success') and db_members.get('result'):
            for row in db_members['result']:
                guild_id = row['guild_id']
                self.member_cache[guild_id].append(dict(row))

            self.bot.logger.info(f"✅ Team member berhasil diload untuk {len(self.member_cache)} guild.")
        else:
            self.bot.logger.info("⚠️ Belum ada data team member di database.")

        # ==========================================
        # 2. LOAD TEAM SETTINGS (1 Guild = 1 Setting)
        # ==========================================
        self.settings_cache = {}  # Cukup pakai dictionary biasa

        db_settings = await self.bot.database.get_team_settings()

        if db_settings.get('success') and db_settings.get('result'):
            for row in db_settings['result']:
                guild_id = row['guild_id']
                # Langsung jadikan dictionary sebagai value (TIDAK PERLU di-append ke list)
                self.settings_cache[guild_id] = dict(row)

            self.bot.logger.info(f"✅ Team settings berhasil diload untuk {len(self.settings_cache)} guild.")
        else:
            self.bot.logger.info("⚠️ Belum ada data team settings di database.")

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(TeamManagement(bot))
