import datetime
from typing import TYPE_CHECKING

from discord import Message, TextChannel
import discord
from discord.ext import commands, tasks

from database.models import PlayerLogEntry

if TYPE_CHECKING:
    from bot import DiscordBot

class PlayerLog(commands.Cog):
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        self.online_player: dict[str, PlayerLogEntry] = {}
        self.join_leave_channel_id: TextChannel | None = None
        self.player_list_embed: Message | None = None
    
    @tasks.loop(seconds=30)
    async def update_player_list(self) -> None:
        # 1. Validasi: Jika message objek tidak ada, jangan lanjut
        if not self.player_list_embed:
            return

        try:
            # 2. Build ulang Embed dari awal (Lebih aman & bersih)
            online_count = len(self.online_player)
            
            # Buat list string untuk player
            if online_count > 0:
                player_entries = [
                    f"- **{data['nickname']}** (Sejak: <t:{int(data['online_at'].timestamp())}:R>)"
                    for data in self.online_player.values()
                ]
                description = "**Online Players:**\n" + "\n".join(player_entries)
            else:
                description = "*Tidak ada pemain yang online saat ini.*"

            new_embed = discord.Embed(
                title="🎮 MarlinMC | Player Online",
                description=description,
                color=discord.Color.blue() if online_count > 0 else discord.Color.light_grey(),
                # Gunakan timestamp asli embed agar muncul di samping footer
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            
            # Footer hanya teks biasa (karena timestamp <t:R> tidak jalan di sini)
            new_embed.set_footer(text="Terakhir diperbarui")

            # 3. Eksekusi Edit
            await self.player_list_embed.edit(embed=new_embed)
        except discord.NotFound:
            # Jika pesan dihapus manual di Discord, reset variabel agar handler buat baru
            self.player_list_embed = None
            self.update_player_list.stop()
        except Exception as e:
            self.bot.logger.error(f"Gagal update player list: {e}")
    
    
    async def _online_player_handler(self, message: Message, player_list_channel_id: int) -> None:
        if not message.embeds:
            return
        
        embed = message.embeds[0]
        if not embed.author or not embed.author.name:
            return
        
        author_text = embed.author.name.lower()
        
        is_join = "joined" in author_text
        is_leave = "left" in author_text
    
        if not is_join and not is_leave:
            return
        
        nickname = embed.author.name.split()[0]
        if is_join:
            self.online_player[nickname] = {"nickname": nickname, "online_at": message.created_at}
        elif is_leave:
            self.online_player.pop(nickname, None)
        
        if not self.player_list_embed:
            channel = self.bot.get_channel(player_list_channel_id)
            if isinstance(channel, TextChannel):
                embed = discord.Embed(title="Player List",
                                      description="No players currently online.",
                                      color=discord.Color.blue(),
                                      timestamp=datetime.datetime.now(datetime.UTC))
                embed.set_footer(text=f"Last updated: <t:{int(datetime.datetime.now(datetime.UTC).timestamp())}:R>")
                self.player_list_embed = await channel.send(embed=embed)
        
        if not self.update_player_list.is_running():
            self.update_player_list.start()
        
    
    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if not message.guild:
            return
        
        settings = self.bot.guild_settings_cache.get(message.guild.id, {})
        if settings:
            leave_join_channel_id = settings.get("team", {}).get("player_log_channel_id", None)
            player_list_channel_id = settings.get("general", {}).get("player_list_channel_id", None)
            if leave_join_channel_id and player_list_channel_id and message.channel.id == leave_join_channel_id:
                await self._online_player_handler(message, player_list_channel_id)
    
    async def cog_unload(self) -> None:
        if self.update_player_list.is_running():
            self.update_player_list.cancel()
        
        if self.player_list_embed:
            try:
                await self.player_list_embed.delete()
            except Exception:
                pass
    
async def setup(bot: "DiscordBot") -> None:
    await bot.add_cog(PlayerLog(bot))

        