"""
Copyright © Krypton 2019-Present - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
🐍 A simple template to start to code your own and personalized Discord bot in Python

Version: 6.5.0
"""
import datetime
import logging

import discord
from discord.ext import commands
from discord import app_commands



# Here we name the cog and create a new class for the cog.
class Welcome(commands.Cog, name="welcome"):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_group(
        name="welcomerole",
        description="Welcome role group"
    )
    @commands.has_permissions(administrator=True)
    async def welcomerole(self, context: commands.Context):
        if context.invoked_subcommand is None:
            await context.send("Gunakan subcommand")

    @welcomerole.command(
        name="add",
        description="menambahkan role pada saat member baru join server",
    )
    @app_commands.describe(
        role="Role yang ingin diberikan kepada member baru"
    )
    async def add(self, context: commands.Context, role: discord.Role):
        guild_id = context.guild.id
        role_id = role.id
        result = await self.bot.database.add_welcome_role(guild_id, role_id)
        if result['success']:
            return await context.send(
                embed=discord.Embed(
                    title=":white_check_mark: Welcome Role Added",
                    description=f"Welcome Role Added Successfully!\n"
                                f"Role ID: {role_id}\n"
                                f"Role Name: {role.name}\n"
                                f"<@&{role_id}>",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )
        elif result['duplicate']:
            return await context.send(
                embed=discord.Embed(
                    title=":white_check_mark: Welcome Role Already Set",
                    description=f"Welcome role untuk server ini sudah di setting",
                    color=discord.Color.yellow(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )
        return await context.send(
            embed=discord.Embed(
                title=":white_check_mark: Welcome Role Error",
                description=f"{result['error']}",
                color=discord.Color.red(),
                timestamp=datetime.datetime.now(datetime.UTC),
            )
        )

    @welcomerole.command(
        name="remove",
        description="menghapus role yang diberikan kepada member baru join server",
    )
    async def remove(self, context: commands.Context):
        guild_id = context.guild.id
        result = await self.bot.database.remove_welcome_role(guild_id)
        if result['success']:
            return await context.send(
                embed=discord.Embed(
                    title=":white_check_mark: Welcome Role Removed",
                    description=f"Welcome Role Removed Successfully!",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )
        else:
            return await context.send(
                embed=discord.Embed(
                    title=":white_check_mark: Welcome Role Error",
                    description=f"{result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )

    @welcomerole.command(
        name="edit",
        description="melihat role yang diberikan kepada member baru join server",
    )
    @app_commands.describe(
        role="Role yang ingin diberikan kepada member baru"
    )
    async def edit(self, context: commands.Context, role: discord.Role):
        guild_id = context.guild.id
        role_id = role.id
        result = await self.bot.database.edit_welcome_role(guild_id, role_id)
        if result['success']:
            return await context.send(
                embed=discord.Embed(
                    title=":white_check_mark: Welcome Role Edited",
                    description=f"Welcome Role Edited Successfully!\n"
                                f"Role ID: {role_id}\n"
                                f"Role Name: {role.name}\n"
                                f"<@&{role_id}>",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )
        else:
            return await context.send(
                embed=discord.Embed(
                    title=":white_check_mark: Welcome Role Error",
                    description=f"{result['error']}",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now(datetime.UTC),
                )
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id
        result = await self.bot.database.get_welcome_role(guild_id)
        if result['success']:
            role_id = result['value']
            role = member.guild.get_role(role_id)
            await member.add_roles(role)
            logging.info(f"Welcome role {role.name} has been added to {member.name}#{member.discriminator} in guild {member.guild.name}")


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Welcome(bot))
