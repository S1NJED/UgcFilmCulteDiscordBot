from discord import app_commands, Interaction
from UGC import UgcRegions, UgcScrapper
import discord
from utils import connDb
import asqlite
from discord.ext.commands import Cog, Bot

class RemoveCinema(Cog):

    ids = []
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="remove_cinema", description="Supprime un cinéma de la liste")
    @app_commands.describe(cinema="Entrez le nom du cinéma")
    async def remove_cinema(self, interaction: Interaction, cinema: str):
        
        async with asqlite.connect("bdd.sqlite") as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM cinemas WHERE name = ?", (cinema,))

                await interaction.response.send_message(content=f"Le cinéma `{cinema}` à bien été supprimé.")
        
    @remove_cinema.autocomplete("cinema")
    async def remove_cinema_autocomplete_cinema(self, interaction: Interaction, current: str):
        current = current.lower()

        async with asqlite.connect("bdd.sqlite") as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT name FROM cinemas")
                data = await cursor.fetchall() # [sqlte3(name)]
                names = [elem['name'] for elem in data if current in elem['name'].lower()]

                return [app_commands.Choice(name=name, value=name) for name in names]


async def setup(bot: Bot):
    await bot.add_cog(RemoveCinema(bot))