from doctest import debug_script
import discord
#from .discord import app_commands
from utils.logging_setup import retrieve_logger
from utils.config import settings
from typing import List, Callable

main_logger = retrieve_logger(__name__)
print(main_logger)

main_logger.debug("Starting the application...")

class bot_client(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        
        self.is_synced = False
    
    
    async def on_ready(self):
        await self.wait_until_ready()
        
        if not self.is_synced:
            await tree.sync(guild=discord.Object(id=settings.guild_id))
            self.is_synced = True
        main_logger.info(f"Successful login as: {self.user}")

    
client = bot_client()
tree = discord.app_commands.CommandTree(client)

@tree.command(name='test', guild=discord.Object(id=settings.guild_id))
async def tester(interaction:discord.Interaction, name:str):
    await interaction.response.send_message(f"Hey {name}!")
    
client.run(settings.bot_token)