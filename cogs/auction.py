"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""

from collections import defaultdict
from datetime import datetime
from discord import Color, Embed, Interaction, Message, TextChannel, app_commands
from discord.ext import commands
from discord.ext.commands import Context
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import DiscordBot


class Auction(commands.Cog, name="Auction"):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.item_list: defaultdict[int, list[str]] = defaultdict(list) # Untuk menyimpan daftar item yang sedang dicari di lelang

    @commands.hybrid_group(
        name="auction",
        description="Perintah untuk mengelola lelang",
    )
    async def auction(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Gunakan subperintah: `alert`")

    @auction.command(
        name="alert",
        description="Menambahkan item yang ingin dicari di lelang",
    )
    @app_commands.describe(nama_item="Nama item yang ingin dicari di lelang, bisa di dapat dari channel auction",
                           is_permanent="Apakah alert ini permanen?")
    async def alert(self, ctx: Context, nama_item: str, is_permanent: bool = False) -> None:
        """Command alert jika ada item spesifik yang di jual di auction

        Args:
            ctx (Context): Context dari pengguna discord
            nama_item (str): Nama item yang ingin di jual
            is_permanent (bool): Apakah alert ini permanen?
        """
        if not ctx.guild:
            await ctx.send("Perintah ini hanya dapat digunakan di dalam server.", ephemeral=True)
            return
        
        guild_id = ctx.guild.id
        author_id = ctx.author.id

        self.item_list[guild_id].append(nama_item)
        resp = await self.bot.database.add_auction_alert(guild_id, author_id, nama_item, is_permanent)

        if resp["success"]:
            data = resp["data"]
            if not data:
                await ctx.send(f"Sukses menambahkan item ke daftar pencarian lelang, tetapi tidak ada data yang dikembalikan.\n{resp}")
                return
            embed = Embed(
                title="Item di tambahkan ke daftar pencarian lelang",
                description=f"- **Alert ID**: {data['id']}\n- **Item**: {nama_item}\n- **Guild ID**: {guild_id}\n"
                f"- **User ID**: <@{author_id}>\n- **Created At**: <t:{int(data['created_at'].timestamp())}:F>\n- **Active**: {"Active" if data['is_active'] else "Inactive"}\n- **Permanent**: {"Yes" if data['is_permanent'] else "No"}",
                timestamp=data['created_at'],
                color=Color.green()
            )
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar.url
            )
            embed.set_footer(text="Auction Alert")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=Embed(
                    title="Gagal menambahkan item ke daftar pencarian lelang",
                    description=f"Error: {resp['error']}",
                    color=Color.red()
                )
            )

    @auction.command(
            name="list",
            description="Menampilkan daftar item yang sedang kamu dicari di lelang",
    )
    async def list_auction(self, ctx: Context) -> None:
        if not ctx.guild:
            await ctx.send("Perintah ini hanya dapat digunakan di dalam server.", ephemeral=True)
            return
        guild_id = ctx.guild.id
        author_id = ctx.author.id
        resp = await self.bot.database.get_user_auction_alert(guild_id, author_id)
        if resp["success"]:
            data = resp["data"]
            if not data:
                await ctx.send("Kamu tidak memiliki item yang sedang dicari di lelang.", delete_after=10)
                return

            embed = Embed(
                title="Daftar item yang sedang kamu cari di lelang",
                timestamp=datetime.now(),
                color=Color.blue()
            )

            for index, item in enumerate(data, 1):
                embed.add_field(
                    name=f"{index}. Alert ID: {item.get('id', 'N/A')}",
                    value=f"- **Item**: {item.get('item_name', 'N/A')}\n- **Created At**: <t:{int(item.get('created_at', datetime.now()).timestamp())}:F>\n- **Permanent**: {'Yes' if item.get('is_permanent', False) else 'No'}",
                    inline=False
                )
                
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar.url
            )
            embed.set_footer(text=f"Auction Alert List | {len(data)}/5 Alerts | Use /auction remove <Alert ID> to remove an alert")
            await ctx.send(embed=embed)

    
    @auction.command(
        name="remove",
        description="Menghapus item yang sudah tidak ingin dicari di lelang",
    )
    @app_commands.describe(alert_id="ID alert yang ingin dihapus, bisa di dapat dari daftar item yang sedang dicari di lelang")
    async def remove(self, ctx: Context, alert_id: int) -> None:
        if not ctx.guild:
            await ctx.send("Perintah ini hanya dapat digunakan di dalam server.", ephemeral=True)
            return
        await ctx.defer(ephemeral=True)
        guild_id = ctx.guild.id
        author_id = ctx.author.id
        resp = await self.bot.database.remove_auction_alert(
            alert_id=alert_id,
            guild_id=guild_id,
            user_id=author_id
        )

        if resp["success"]:
            data = resp["data"]
            if not data:
                await ctx.send(f"Sukses menghapus alert dengan ID {alert_id} dari daftar pencarian lelang, tetapi tidak ada data yang dikembalikan.\n{resp}")
                return
                
            deskripsi = (
                f"- **Alert ID**: {data['id']}\n"
                f"- **Item**: {data['item_name']}\n"
                f"- **Guild ID**: {guild_id}\n"
                f"- **User ID**: <@{author_id}>\n"
                f"- **Created At**: <t:{int(data['created_at'].timestamp())}:F>\n"
                f"- **Active**: Deleted"
            )
                
            embed = Embed(
                title="Item dihapus dari daftar pencarian lelang",
                description=deskripsi,
                timestamp=data['created_at'],
                color=Color.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.set_footer(text="Auction Alert Removed")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=Embed(
                    title="Gagal menghapus item",
                    description=f"Error: {resp['error']}",
                    color=Color.red()
                )
            )

    @remove.autocomplete("alert_id")
    async def alert_id_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[int]]:
       
        guild_id = interaction.guild_id
        user_id = interaction.user.id
        if not guild_id:
            return []
            
        resp = await self.bot.database.get_user_auction_alert(guild_id, user_id)
        
        if resp["success"] and resp["data"]:
            return [
                app_commands.Choice(name=f"{item.get('item_name', 'N/A')} (ID: {item.get('id', 'N/A')})", value=item.get('id', 0))
                for item in resp["data"]
                if current.lower() in item.get('item_name', 'N/A').lower() or current in str(item.get('id', 0))
            ]
            
        return []

    async def cog_load(self) -> None:
        self.item_list = defaultdict(list)
        item_list_resp = await self.bot.database.get_list_auction_item()
        if item_list_resp["success"] and item_list_resp["data"]:
            for item in item_list_resp["data"]:
                guild_id = item["guild_id"]
                item_name = item.get("item_name", "Name Not Found")
                self.item_list[guild_id].append(item_name)
        self.bot.logger.info(f"Loaded auction item list for {len(self.item_list)} guilds.")


    async def _auction_event_handler(self, message: Message, guild_id: int, alert_channel_id: int | None) -> None:
        if not alert_channel_id:
            return
        if message.embeds:
            if "selling" in str(message.embeds[0].author).lower():
                for embed in message.embeds:
                    for field in embed.fields:
                        if field.name and "item" in field.name.lower():
                            if not field.value:
                                break
                            item_name = field.value.strip()
                            if item_name in self.item_list.get(guild_id, []):
                                resp = await self.bot.database.get_all_user_item(guild_id, item_name)
                                embed_event = message.embeds[0].copy()
                                if resp["success"] and resp["data"]:
                                    user_list = resp["data"]
                                    content = f"🚨 **Auction Alert** 🚨\n- Item **{item_name}** sedang dijual di lelang!\n||{' '.join(f'<@{user["user_id"]}>' for user in user_list)}||"

                                    await self.bot.database.deactivate_auction_alert(item_name=item_name,
                                                                                    guild_id=guild_id)
                                else:
                                    content = f"🚨 **Auction Alert** 🚨\n- Item **{item_name}** sedang dijual di lelang!"
                                
                                alert_channel = self.bot.get_channel(alert_channel_id)
                                if alert_channel and isinstance(alert_channel, TextChannel):
                                    message = await alert_channel.send(content=content, embed=embed_event)
                                    await message.add_reaction("🛎️")
                                    break
                                break 


    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if not message.guild:
            return
        
        auction_settings = self.bot.guild_settings_cache.get(message.guild.id, {}).get("auction", {})
        alert_channel_id = auction_settings.get("alert_channel_id")
        event_channel_id = auction_settings.get("event_channel_id")


        if message.channel.id == event_channel_id:
            await self._auction_event_handler(message, message.guild.id, alert_channel_id)

async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(Auction(bot))
