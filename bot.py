import discord
import os
from discord.ext import commands
import asyncio
from UGC import UgcScrapper
import argparse
import os
import dotenv


class Bot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        self.ugc = UgcScrapper(bot=self)
        
        super().__init__(command_prefix="??", intents=intents)
    
    # execute before the bot start
    async def setup_hook(self):
        try:
            cogsFolder = os.listdir("cogs")

            for file in cogsFolder:
                try:
                    if file.endswith(".py"):
                        file = file.removesuffix('.py')
                        await self.load_extension(f"cogs.{file}")
                        print(f"[{file}] - sucessfully loaded {file} Cog")
                except discord.ext.commands.errors.ExtensionAlreadyLoaded as err:
                    print(err)
                    print("extension already loaded")
                except Exception as err:
                    raise err
                    
        except Exception as err:
            raise err
        
        await self.tree.sync()
        print("Sucessfully synced") 



    async def on_ready(self):

        await self.change_presence(status=discord.Status.idle)
        print(f"Bot logged on as {self.user}")

        # threading.Thread(target=asyncio.run, args=(self.ugc.worker(),)).start()
        asyncio.create_task(self.ugc.worker())
        print("UGC worker started")
    
    async def on_message(self, message: discord.Message):
        
        if message.content.startswith(self.command_prefix):

            if message.content.startswith("?deco"):
                self.ugc.workerLoopState = False

                await message.channel.send("bot off")
                await self.close()
            
            elif message.content.startswith("?reload"):
                cogsFolder = os.listdir("cogs")

                for file in cogsFolder:
                    try:
                        if file.endswith(".py"):
                            file = file.removesuffix('.py')
                            await self.reload_extension(f"cogs.{file}")
                            print(f"Reloading cogs.{file}")
                    except Exception as err:
                        print(file, err)
                

                await message.channel.send("reloaded cogs")
            
            elif message.content.startswith("?sync"):

                await self.tree.sync()

         

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="dev env")
    args = parser.parse_args()
    dev = args.dev

    dotenv.load_dotenv(".env.production" if dev else ".env")

    TOKEN = os.getenv("BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("No token provided, add it in the .env file")
    
    bot = Bot()
    bot.run(token=TOKEN)

if __name__ == '__main__':
    main()