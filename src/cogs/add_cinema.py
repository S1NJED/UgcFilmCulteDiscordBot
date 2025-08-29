from discord.ext.commands import Cog, Bot
from discord import app_commands, Interaction
from UGC import UgcRegions, UgcScrapper
import discord
from utils import connDb
import asqlite
import os

class CinemaSelect(discord.ui.Select):

    def __init__(self, regionId, user_id: int):
        self.regionId = regionId
        self.user_id = user_id
        super().__init__(placeholder="📌 Choisis un cinéma")

        scrapper = UgcScrapper()

        cinemas = scrapper.getCinemasFromRegion(regionId=regionId)
        for cinema in cinemas:
            self.add_option(label=cinema['name'], value=f"cinema_{cinema['id']}_{cinema['name']}")

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id: return
        _, cinema_id, cinema_name = interaction.data['values'][0].split('_')
        
        async with asqlite.connect(os.getenv("DB_NAME")) as conn:
            await conn.execute("INSERT INTO cinemas(id, name) VALUES(?, ?)", (cinema_id, cinema_name) )
            await conn.commit()
            
        await interaction.message.edit(content=f"Cinéma ajouté avec succès ✅", view=None)
        await interaction.response.defer()

class RegionSelect(discord.ui.Select):

    def __init__(self, user_id: int):
        super().__init__(placeholder="🌍 Choisis une région")
        self.user_id = user_id
        regions = vars(UgcRegions())
        for region, id in regions.items():
            self.add_option(label=region, value=f"region_{id}")

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id: return
        callback_data = interaction.data['values'][0]
        
        if callback_data.startswith("region_"):
            # We send the CinemaSelect
            view = discord.ui.View()
            view.add_item(CinemaSelect(regionId=callback_data.split('_')[1], user_id=self.user_id))
            
            await interaction.message.edit(view=view)
            await interaction.response.defer()

class AddCinema(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    '''
    region -> cinema
    1. Choisir une région
    2. Choisir un cinéma
    '''
    @app_commands.command(name="add_cinema", description="Ajouter un cinéma a surveiller")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_cinema(self, interaction: Interaction):

        view = discord.ui.View()
        view.add_item(RegionSelect())
        
        await interaction.response.send_message(view=view)

async def setup(bot: Bot):
    await bot.add_cog(AddCinema(bot))

