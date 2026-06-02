"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""
import datetime

import discord
from discord import app_commands
from discord.ext import commands
class BountyClaimView(discord.ui.View):
    def __init__(self, bot, alert_channel: discord.TextChannel, bounty_embed: discord.Embed, bounty_id: int, ingame_nick: str, context: commands.Context):
        # Set timeout ke 60 detik (1 menit)
        super().__init__(timeout=60.0)
        self.bot = bot
        self.bounty_id = bounty_id
        self.ingame_nick = ingame_nick
        self.ctx = context
        self.message: discord.Message | None = None
        self.alert_channel = alert_channel
        self.bounty_embed = bounty_embed

    # Membuat tombol Claim berwarna hijau (success)
    @discord.ui.button(label="Claim Bounty", style=discord.ButtonStyle.success, emoji="⚔️")
    async def claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        # 1. Panggil fungsi database untuk mencatat klaim
        result = await self.bot.database.claim_bounty(user_id, self.bounty_id, self.ingame_nick)

        if result.get("success"):
            # 2. Jika sukses, edit pesan ephemeral tadi menjadi pesan sukses
            self.bounty_embed.title = f"Claim Bounty"
            self.bounty_embed.description = "Seseorang telah mengklaim bounty ini! Semoga berhasil menyelesaikan tugasnya!"
            await self.alert_channel.send(
                embed=self.bounty_embed
            )

            await interaction.response.edit_message(
                content=f"✅ Kamu berhasil mengklaim bounty ini! Selamat berburu.",
                embed=None,  # Hilangkan embed detailnya
                view=None  # Hilangkan tombolnya
            )
        else:
            # Jika gagal (misal: keduluan orang lain)
            await interaction.response.edit_message(
                content=f"❌ Gagal mengklaim: {result.get('error')}",
                embed=None,
                view=None
            )

        # Hentikan timer view karena sudah diklik
        self.stop()

    # Fungsi ini otomatis terpanggil jika 1 menit habis tanpa ada tombol yang diklik
    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except discord.HTTPException:
                pass


# Here we name the cog and create a new class for the cog.
class Bounty(commands.Cog, name="bounty"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.join_leave_channel = 0
        self.join_alert_channel = 0
        self.bounty_alert_channel = 0
        self.target_bounty = set()

    # Auto Complete
    async def bounty_list(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:

        bounty_data = await self.bot.database.get_bounty_autocomplete(current)
        if not bounty_data["success"] or not bounty_data["result"]:
            return []

        return [
            app_commands.Choice(
                name=f"Target: {b['target']} | Payout: {b['payout']} | Required Kill: {b['required_kill']}",
                value=str(b['bounty_id'])
            )
            for b in bounty_data["result"]
        ]


    @commands.hybrid_group(
        name="bounty",
        description="Bounty Group"
    )
    async def bounty(self, context: commands.Context):
        if context.invoked_subcommand is None:
            await context.send("Gunakan subcommand untuk membuat bounty")

    @bounty.command(
        name="add",
        description="tambahkan seseoran ke dalam bounty"
    )
    @app_commands.describe(
        target="Target yang ingin ditambahkan ke dalam bounty",
        reason="Alasan mengapa target ditambahkan ke dalam bounty",
        payout="Jumlah hadiah yang akan diberikan kepada pembunuh target",
        required_kill="Total kill yang ingin di berikan"
    )
    async def add(self, context: commands.Context, target: str, reason: str, payout: int, required_kill: int):
        user_id = context.author.id
        result = await self.bot.database.add_bounty(
            user_id,
            target,
            reason,
            payout,
            required_kill
        )
        if result["success"]:
            self.target_bounty.add(target)
            alert_channel = self.bot.get_channel(self.bounty_alert_channel)
            await alert_channel.send(
                embed=discord.Embed(
                    title=f"Bounty Alert",
                    description=f"**Detail Bounty: {target}**\n"
                                f"Reason: {reason}\n"
                                f"Payout: {payout}\n"
                                f"Required Kill: {required_kill} To finish\n"
                                f"Silahkan Claim bounty jika ingin mengerjakan",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                )
            )
            return await context.send(
                embed=discord.Embed(
                    title=f"Bounty Added for {target}",
                    description=f"**Detail Bounty: {target}**\n"
                                f"User ID kamu: {user_id}\n"
                                f"Reason: {reason}\n"
                                f"Payout: {payout}\n"
                                f"Required Kill: {required_kill} To finish",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                ),
                ephemeral=True
            )
        error_msg = result.get("error", "Terjadi kesalahan yang tidak diketahui.")
        color = discord.Color.red()

        if result.get("blacklisted"):
            title = "🚫 Blacklisted"
        elif result.get("duplicate"):
            title = "⚠️ Bounty Still Active"
            color = discord.Color.orange()
        else:
            title = "❌ Error"

        return await context.send(
            embed=discord.Embed(
                title=title,
                description=error_msg,
                color=color
            ),
            ephemeral=True  # Agar pesan error hanya terlihat oleh pengirim
        )

    @bounty.command(
        name="remove",
        description="menghapus bounty yang kamu posting, jika belum di claim",
    )
    async def remove(self, context: commands.Context):
        user_id = context.author.id
        result = await self.bot.database.remove_bounty(user_id)
        if result["success"]:
            self.target_bounty.remove(result["target"])

            alert_channel = self.bot.get_channel(self.bounty_alert_channel)
            await alert_channel.send(
                embed=discord.Embed(
                    title=f"Bounty Alert",
                    description=f"Bounty untuk target **{result['target']}** telah dihapus oleh pembuatnya,"
                                f" Semoga tidak ada yang mengejar target ini lagi :D",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                )
            )

            return await context.send(
                embed=discord.Embed(
                    title="Bounty Removed",
                    description="Bounty kamu berhasil dihapus",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                ),
                ephemeral=True
            )
        else:
            return await context.send(
                embed=discord.Embed(
                    title="Bounty gagal dihapus",
                    description=f"{result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                ),
                ephemeral=True
            )

    @bounty.command(
        name="edit",
        description="Edit bounty yang kamu posting"
    )
    async def edit(self, context: commands.Context, target: str, reason: str, payout: int, required_kill: int):
        user_id = context.author.id
        result = await self.bot.database.edit_bounty(
            user_id,
            target,
            reason,
            payout,
            required_kill
        )
        if result["success"]:
            alert_channel = self.bot.get_channel(self.bounty_alert_channel)
            data_lama = result["data_lama"]
            await alert_channel.send(
                embed=discord.Embed(
                    title=f"Bounty Edited for {data_lama['target']} dengan id {data_lama['bounty_id']}",
                    description=f"**Detail Bounty: {target}**\n"
                                f"- Target Baru: {target}\n"
                                f"- Alasan Baru: {reason}\n"
                                f"- Payout Baru: {payout}\n"
                                f"- Required Kill Baru: {required_kill} to finish",
                )
            )
            return await context.send(
                embed=discord.Embed(
                    title=f"Bounty edited for {target}",
                    description=f"**Detail Bounty: {target}**\n"
                                f"- User ID kamu: {user_id}\n"
                                f"- Reason: {reason}\n"
                                f"- Payout: {payout}\n"
                                f"- Required Kill: {required_kill} to finish",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                ),
                ephemeral=True
            )
        else:
            return await context.send(
                embed=discord.Embed(
                    title=f"Bounty edited for {target}",
                    description=f"{result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                )
            )

    @bounty.command(
        name="claim",
        description="Claim bounty yang di post orang lain"
    )
    @app_commands.describe(
        bounty="list bounty yang bisa di klaim.",
        ingame_nick="Nick in game di minecraft kamu yang menjadikan bukti."
    )
    @app_commands.autocomplete(
        bounty=bounty_list
    )
    async def claim(self, context: commands.Context, bounty: str, ingame_nick: str):
        get_bounty = await self.bot.database.get_bounty_by_id(int(bounty))
        embed = discord.Embed(
            title=f":scroll: Detail Bounty",
            description=f"Detail bounty dengan bounty id : {bounty}",
            color=discord.Color.dark_red(),
        )
        bounty_result = get_bounty["result"]
        embed.add_field(name="The Contractor ", value=f"<@{bounty_result["user_id"]}>", inline=False)
        embed.add_field(name="Target yang harus di bunuh", value=f"{bounty_result["target"]}", inline=False)
        embed.add_field(name="Alasan", value=f"{bounty_result["reason"]}", inline=False)
        embed.add_field(name="Bayaran", value=f"{bounty_result["payout"]}", inline=False)
        embed.add_field(name="Maks Kill", value=f"{bounty_result["required_kill"]}", inline=False)

        alert_channel = self.bot.get_channel(self.bounty_alert_channel)
        view = BountyClaimView(self.bot, alert_channel, embed, int(bounty), ingame_nick, context)

        msg = await context.send(embed=embed, view=view, ephemeral=True)

        view.message = msg

    @bounty.command(
        name="unclaim",
        description="Unclaim bounty yang di klaim.",
    )
    async def unclaim(self, context: commands.Context):
        try:
            user_id = context.author.id
            result = await self.bot.database.unclaim_bounty(user_id)
            if result["success"]:
                return await context.send(
                    embed=discord.Embed(
                        title=f"Unclaim Bounty Berhasil",
                        description=f"Bounty yang kamu klaim berhasil di hapus",
                        color=discord.Color.green(),
                        timestamp=datetime.datetime.now(datetime.UTC)
                    ),
                    ephemeral=True
                )
            return await context.send(
                embed=discord.Embed(
                    title=f"Unclaim Bounty Gagal",
                    description=f"Terjadi error: {result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                ),
                ephemeral=True
            )
        except Exception as e:
            return await context.send(
                embed=discord.Embed(
                    title=f"Unclaim Bounty Gagal",
                    description=f"Terjadi error: {e}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                ),
                ephemeral=True
            )

    @commands.hybrid_group(
        name="bountyadmin",
        description="Grup command khusus admin"
    )
    @app_commands.default_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    async def bountyadmin(self, context: commands.Context):
        if context.invoked_subcommand is None:
            await context.send("Gunakan subcommand admin yang tersedia.")


    @bountyadmin.command(
        name="blacklist",
        description="Blacklist user dari membuat bounty"
    )
    @app_commands.describe(
        user="User yang ingin di blacklist",
        blacklisted="Value True/False",
    )
    async def blacklist(self, context: commands.Context, user: discord.User, blacklisted: bool):
        user_id = user.id
        result = await self.bot.database.blacklist_bounty(user_id, blacklisted)
        if result["success"]:
            status = "blacklisted" if blacklisted else "unblacklisted"
            return await context.send(
                embed=discord.Embed(
                    title=f"User {status}",
                    description=f"User {user.name} has been {status} from creating bounties.",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                )
            )
        else:
            return await context.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"{result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )


    async def add_kill_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        bounty_data = await self.bot.database.add_kill_autocomplete(current)
        if not bounty_data["success"] or not bounty_data["result"]:
            return []

        return [
            app_commands.Choice(
                name=f"Target: {b['target']} | Maks Kill: {b['required_kill']} | Person Who Claimed: {b['nickname_ingame']}",
                value=str(b['user_id'])
            )
            for b in bounty_data["result"]
        ]

    @bountyadmin.command(
        name="addkill",
        description="Add a kill user to the bounty claim"
    )
    @app_commands.describe(
        kill="jumlah kill yang ingin di tambahkan",
        user="Nickname in game player yang mengklaim bounty"
    )
    @app_commands.autocomplete(
        user=add_kill_autocomplete
    )
    async def add_kill(self, context: commands.Context, user: str, kill: int):
        user_id = int(user)
        result = await self.bot.database.add_kill_to_bounty(kill, user_id)
        if result["success"]:
            if result["completed"]:
                return await context.send(
                    embed=discord.Embed(
                        title="Success",
                        description=f"Bounty yang di claim oleh player telah selesai",
                        color = discord.Color.green(),
                        timestamp = datetime.datetime.now(datetime.UTC)
                    )
                )
            return await context.send(
                embed=discord.Embed(
                    title="Kill Added",
                    description=f"Added {kill} kill to user <@{user_id}>",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                )
            )
        else:
            return await context.send(
                embed=discord.Embed(
                    title="Error",
                    description=f"{result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )

    @bountyadmin.command(
        name="setup",
        description="setup bounty"
    )
    @app_commands.describe(
        join_leave_channel="Channel yang digunakan untuk mendeteksi player yang join server",
        join_alert_channel="Channel yang digunakan untuk mengirim alert ketika target bounty join server",
        bounty_alert_channel="Channel yang digunakan untuk mengirim alert ketika bounty baru di buat"
    )
    async def bountysetup(self, context: commands.Context, join_leave_channel: discord.TextChannel, join_alert_channel: discord.TextChannel, bounty_alert_channel: discord.TextChannel):
        self.join_leave_channel = join_leave_channel.id
        self.join_alert_channel = join_alert_channel.id
        self.bounty_alert_channel = bounty_alert_channel.id

        result = await self.bot.database.set_bounty_settings(context.guild.id, self.join_leave_channel, self.join_alert_channel, self.bounty_alert_channel)
        if result["success"]:
            return await context.send(
                embed=discord.Embed(
                    title="Bounty Setup Completed",
                    description=f"Join/Leave Channel: {join_leave_channel.mention}\n"
                                f"Join Alert Channel: {join_alert_channel.mention}\n"
                                f"Bounty Alert Channel: {bounty_alert_channel.mention}",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC)
                )
            )
        return await context.send(
            embed=discord.Embed(
                title="Bounty Setup Failed",
                description=result["error"],
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(datetime.UTC)
            )
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != self.join_leave_channel:
            return
        if message.author.bot:
            return

        embed = message.embeds[0]

        if "joined the server" in embed.author.name:
            player_name = message.content.split(" ")[0]
            if player_name in self.target_bounty:
                alert_channel = self.bot.get_channel(self.join_alert_channel)
                await alert_channel.send(
                    embed=discord.Embed(
                        title="Bounty Alert",
                        description=f"Target **{player_name}** Telah join server! Siapkan pedang mu!!!",
                        color=discord.Color.orange(),
                        timestamp=datetime.datetime.now(datetime.UTC)
                    )
                )

    async def cog_load(self):
        # 1. Load Data Bounty (Sudah aman)
        bounty_data = await self.bot.database.get_all_active_bounty_target()
        if bounty_data.get("success") and bounty_data.get("result"):
            self.target_bounty = set(b['target'] for b in bounty_data["result"])
        else:
            self.target_bounty = set()

        # 2. Load Settings (PERBAIKAN DI SINI)
        settings = await self.bot.database.get_bounty_settings(950039010733076560)

        # Tambahkan pengecekan 'and settings.get("result")'
        if settings.get("success") and settings.get("result"):
            result = settings['result']
            self.join_leave_channel = result['join_leave_channel']
            self.join_alert_channel = result['join_alert_channel']
            self.bounty_alert_channel = result['bounty_alert_channel']
        else:
            # Jika database masih kosong (belum di setup), set ke 0
            self.join_leave_channel = 0
            self.join_alert_channel = 0
            self.bounty_alert_channel = 0




# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Bounty(bot))
