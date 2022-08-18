from doctest import debug_script
from config import settings
from . import discord
#from .discord import app_commands
from logging_setup import retrieve_logger
from typing import List, Callable

main_logger = retrieve_logger()

main_logger.debug("Starting the application...")

class bot_client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        
        self.tree = discord.app_commands.CommandTree(client=self)
        
        super().__init__(intents=intents)
        
        self.is_synced = False
    
    async def on_ready(self):
        await self.wait_until_ready()
        if not self.is_synced:
            await self.tree.sync(guild=discord.Object(id=settings.guild_id))
            self.is_synced = True
        main_logger.info(f"Successful login as: {self.user}")

    def add_tree_commands(self, commands: List[Callable]):
        for item in commands:
            self.tree.add_command(item)
        
@discord.app_commands.command(name="test")
async def slashcommand(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Hello {name}!")
    
client = bot_client()
client.add_tree_commands([slashcommand])
client.run(settings.bot_token)