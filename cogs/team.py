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

    async def cog_load(self) -> None:
        team_member = await self.bot.database.get_team_member()
        if team_member['success'] and team_member['result']:
            group_guild_id = defaultdict(list)

            for member in team_member['result']:
                guild_id = member['guild_id']
                group_guild_id[guild_id].append(dict(member))

            self.member_cache = group_guild_id
            self.bot.logger.info(f"Team member berhasil di load total {len(self.member_cache)} guild")
        else:
            self.member_cache = {}
            self.bot.logger.info("Belum ada team member")


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(TeamManagement(bot))
