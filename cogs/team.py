"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""
import discord
import datetime
import logging
from discord import app_commands, Message
from discord.ext import commands

logger = logging.getLogger(__name__)

# Here we name the cog and create a new class for the cog.
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

    async def member_id_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        member_id_list = await self.bot.database.get_all_member_id()
        logger.info(f"Member ID List: {member_id_list}")
        return [
            app_commands.Choice(name=member[1], value=member[0])
            for member in member_id_list if current.lower() in member[1].lower()
        ]

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.hybrid_group(
        name="team",
        description="Perintah untuk manajemen team Judge",
    )
    @commands.has_permissions(administrator=True)
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
    async def list_member(self, ctx: commands.Context) -> Message:
        """
        This is a testing command that does nothing.

        :param ctx: Interaksi dari pengguna
        """
        try:
            list_data = await self.bot.database.get_team_member()
            if not list_data:
                return await ctx.send("Belum ada member, nih.", ephemeral=True)
            embed = discord.Embed(
                title="✨┃Judge Team Roster",
                color=discord.Color.gold(),
                timestamp=datetime.datetime.now(datetime.UTC),

            )
            categories = {"Leader": [], "Co-Leader": [], "Admin": [], "Member": []}
            for nama, jabatan, rank in list_data:
                if jabatan in categories:
                    categories[jabatan].append(f"• {nama} | {rank}")
                else:
                    categories["Member"].append(f"• {nama} | {rank}")
            for role, members in categories.items():
                if members:
                    role_icons = {
                        "Leader": ":crown:",
                        "Co-Leader": ":shield:",
                        "Admin": ":star:",
                        "Member": ":bust_in_silhouette:"
                    }
                    icon = role_icons.get(role, ":bust_in_silhouette:")
                    embed.add_field(
                        name=f"{icon} ┃ {role}",
                        value="\n".join(members),
                        inline=False
                    )
            embed.set_footer(text="Jumlah player {}".format(len(list_data)))
            return await ctx.send(embed=embed)
        except discord.Forbidden:
            return await ctx.send(
                "Sepertinya saya tidak bisa mengirim pesan disini",
                ephemeral=True,
            )

    @team.command(
        name="addmember",
        description="Menambah member team"
    )
    @app_commands.describe(
        nama="Nama Member",
        rank="Rank Member di Server",
        jabatan="Jabatan Member di team",
    )
    @app_commands.autocomplete(
        rank=rank_autocomplete,
        jabatan=jabatan_autocomplete
    )
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def add_member(self, context: commands.Context, nama: str, rank: str, jabatan: str) -> None:
        """
        Menambah member team
        :param jabatan: Jabatan memberdi team
        :param context: Interaksi dari member discord
        :param nama: Nama Member dalam str
        :param rank: Rank Member dalam str
        :return: None
        """
        try:
            add_member_status = await self.bot.database.add_team_member(nama, rank, jabatan)
            if add_member_status["success"]:
                await context.send(
                    embed=discord.Embed(
                        title="Added Member",
                        description=f"Member: {nama} Rank: {rank} serta Jabatan: {jabatan} berhasil di tambahkan ke database",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.green(),
                    )
                )
            else:
                await context.send(
                    embed=discord.Embed(
                        title="Added Member",
                        description=f"Ada Kesalahan saat menambah member {nama} dengan {rank}"
                                    f"Dengan error {add_member_status['error']}",
                        timestamp=datetime.datetime.now(datetime.UTC),
                        color=discord.Color.red(),
                    )
                )
        except discord.Forbidden:
            await context.send(
                "Sepertinya saya tidak bisa mengirim pesan disini",
                ephemeral=True,
            )

    @team.command(
        name="removemember",
        description="menghapus member team"
    )
    @app_commands.describe(
        nama="Nama Member",
    )
    @app_commands.autocomplete(
        nama=member_id_autocomplete,
    )
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
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

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(TeamManagement(bot))
