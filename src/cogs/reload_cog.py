from discord.ext.commands import Cog, Bot
import os
from discord.ext.commands.errors import ExtensionAlreadyLoaded
from discord import app_commands, Interaction

class ReloadCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="reload")
    @app_commands.checks.has_permissions(administrator=True)
    async def reload_cog(self, interaction: Interaction):
        try:
            cogsFolder = os.listdir("src/cogs")

            for file in cogsFolder:
                if file.endswith(".py"):
                    file_name = file.removesuffix('.py')
                    try:
                        await self.bot.reload_extension(f"cogs.{file_name}")
                        print(f"Successfully reloaded {file_name} cog")
                    except ExtensionAlreadyLoaded:
                        print(f"{file_name} cog is already loaded")
                    except Exception as err:
                        print(f"Error loading {file_name} cog: {err}")
                        raise err
                        
        except Exception as err:
            print(f"Error in reloading cogs: {err}")
            raise err

        # Sync the app commands (slash commands)
        # await self.bot.tree.sync()
        await interaction.response.send_message("Reloaded all cogs successfully!")

async def setup(bot: Bot):
    await bot.add_cog(ReloadCog(bot))
