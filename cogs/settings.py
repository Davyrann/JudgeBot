"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""

from discord import Embed, Interaction, TextChannel, app_commands
import discord
from discord.ext import commands
from typing import TYPE_CHECKING, cast
from database import models

if TYPE_CHECKING:
    from bot import DiscordBot

class Settings(commands.Cog, name="Settings"):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot

    settings_group = app_commands.Group(
        name="settings",
        description="Perintah untuk mengelola pengaturan bot",
        default_permissions=discord.Permissions(administrator=True)
        )

    auction_group = app_commands.Group(
        name="auction",
        parent=settings_group,
        description="Perintah untuk mengelola pengaturan lelang",
        )

    async def auction_settings_autocomplete(self, interaction: Interaction, current: str) -> list[app_commands.Choice[str]]:
        settings = {"Auction Event Channel": "event_channel_id",
                    "Auction Alert Channel": "alert_channel_id"}
        return [
            app_commands.Choice(name=label, value=tech_key) 
            for label, tech_key in settings.items() 
            if current.lower() in label.lower()
        ]

    @auction_group.command(name="channel",
                           description="Atur saluran untuk pengaturan lelang")
    @app_commands.describe(setting="Pilih pengaturan channel yang ingin diatur")
    @app_commands.autocomplete(setting=auction_settings_autocomplete)
    async def set_auction_channel(self, interaction: Interaction, setting: str, channel: TextChannel):
        if not interaction.guild:
            await interaction.response.send_message("Perintah ini hanya dapat digunakan dalam server.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        setting_key = setting  # Gunakan nilai yang dipilih langsung sebagai key
        setting_value = channel.id
        payload = {setting_key: setting_value}
        
        response = await self.bot.database.set_settings(guild_id, "auction", payload)
        if not response["success"]:
                await interaction.followup.send(f"Gagal menyimpan pengaturan: {response['error']}", ephemeral=True)
                return
        
        if guild_id not in self.bot.guild_settings_cache:
            self.bot.guild_settings_cache[guild_id] = cast(models.GuildSettings, {})
        
        if "auction" not in self.bot.guild_settings_cache[guild_id]:
            self.bot.guild_settings_cache[guild_id]["auction"] = cast(models.AuctionSettings, {})
        
        guild_cache = self.bot.guild_settings_cache.get(guild_id, cast(models.GuildSettings, {}))
        guild_cache.get("auction", cast(models.AuctionSettings, {}))[setting_key] = setting_value

        setting_label = setting_key.replace("_id", "").replace("_", " ").title()
        embed = Embed(title="Pengaturan telah Disimpan",
                      description=f"{setting_label} telah diatur ke {channel.mention}.",
                      color=discord.Color.green())

        await interaction.followup.send(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(Settings(bot))
