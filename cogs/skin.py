"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""
import os
import discord
import aiohttp
from discord import app_commands
from discord.ext import commands



# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # async def cape_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get("https://api.mineskin.org/v2/capes") as resp:
    #             capes_req = await resp.json()
    #     capes = capes_req["capes"]
    #     supported_capes = [cape for cape in capes if cape.get("supported")]
    #     return [
    #         app_commands.Choice(name=cape["alias"], value=cape["uuid"])
    #         for cape in supported_capes if current.lower() in cape["alias"].lower()
    #     ]
    async def skin_size_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skin_sizes = ["slim", "classic"]
        return [
            app_commands.Choice(name=skin_size, value=skin_size)
            for skin_size in skin_sizes if current.lower() in skin_size.lower()
        ]

    
    @app_commands.command( # Menggunakan app_commands untuk Slash Command
        name="skin", # Slash command disarankan menggunakan huruf kecil semua
        description="Mengirimkan url untuk set skin di MarlinMC dengan mengunggah gambar skin",
    )
    @app_commands.describe(
        nama_skin="Nama skin yang ingin digunakan",
        skin_size="Ukuran skin yang ingin digunakan",
        gambar_skin="Upload gambar skin di sini", # Menggantikan context.message.attachments
        # cape="Cape yang ingin digunakan (opsional)"
    )
    @app_commands.autocomplete(
        skin_size=skin_size_autocomplete,
        # cape=cape_autocomplete
    )
    async def skin(
        self, 
        interaction: discord.Interaction, # Menggunakan Interaction, bukan Context
        nama_skin: str, 
        skin_size: str, 
        gambar_skin: discord.Attachment, # User bisa langsung drag-and-drop gambar di Discord
        # cape: str = ""
    ) -> None:
        # PENTING: Karena API Mineskin butuh waktu, kita "defer" dulu agar bot tidak dianggap timeout oleh Discord
        await interaction.response.defer(ephemeral=False)

        url = "https://api.mineskin.org/v2/generate"
        image_url = gambar_skin.url # Mengambil url dari attachment yang diupload

        payload = {
            "variant": skin_size,
            "name": nama_skin,
            "visibility": "public",
            # "cape": cape,
            "url": image_url
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {os.getenv("MINESKIN_API_KEY")}'
        }

        # Menggunakan aiohttp agar bot tidak lag/freeze saat request API
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    # Sesuaikan dengan struktur return dari API Mineskin v2 terbaru
                    skin_url = response.get("links", {}).get("skin") 
                    if skin_url:
                        skin_id = skin_url.split("/")[-1]
                        embed = discord.Embed(
                            title="Skin Berhasil Dibuat!",
                            description=f"- Nama Skin: {nama_skin}\n- Ukuran: {skin_size}",
                            color=discord.Color.green(),
                            )
                        embed.add_field(
                            name="Link command",
                            value=f"`/skin url {f"https://mineskin.org/skins/{skin_id}"} {skin_size}`",
                        )
                        await interaction.followup.send(embed=embed)
                        return
                # Jika gagal
                embed = discord.Embed(
                    title="Gagal Membuat Skin",
                    description="Gagal membuat skin. Pastikan gambar yang diupload valid dan coba lagi. atau Terkena Rate Limit tunggu beberapa jam ya",
                    color=discord.Color.red(),
                )
                
                await interaction.followup.send(embed=embed)

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Template(bot))
