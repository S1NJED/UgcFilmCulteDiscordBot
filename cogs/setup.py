from discord import app_commands, Interaction
from UGC import UgcRegions, UgcScrapper
import discord
from utils import connDb
import asqlite
from discord.ext.commands import Cog, Bot
from typing import Literal

class Setup(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
    
    @app_commands.command(name="setup", description="Setup le channel notif et le message")
    @app_commands.describe(channel="Le channel où les notifs seront envoyés")
    @app_commands.describe(message="Un éventuel message qui sera envoyé en plus de l'embed")
    async def setup(self, interaction: Interaction, channel: discord.TextChannel = None, message: str = None):
        if not channel and not message:
            return await interaction.response.send_message("spécifie un channel et/ou un message qui sera envoyé lorsqu'un film culte sera dispo dans un cinéma choisis", ephemeral=True)

        async with asqlite.connect("bdd.sqlite") as conn:
            async with conn.cursor() as cursor:
                content = []

                if channel:
                    content.append(f"Le channel a bien été modifié (<#{channel.id}>)")
                    await cursor.execute("UPDATE notify_channel SET channel_id = ? WHERE id = 1", (channel.id,))
                if message:
                    content.append(f"Le message a bien été modifié:\n> {message}")
                    await cursor.execute("UPDATE notify_channel SET message = ? WHERE id = 1", (message,))

                await interaction.response.send_message(content, ephemeral=True)

                await conn.commit()


async def setup(bot: Bot):
    await bot.add_cog(Setup(bot))