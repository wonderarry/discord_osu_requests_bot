import discord
from discord import app_commands
from discord.app_commands import Choice
from utils.logging_setup import retrieve_logger
from utils.config import settings

main_logger = retrieve_logger(__name__)

main_logger.debug("Starting the application...")

intents = discord.Intents.default()
intents.message_content = True

class UsedClient(discord.Client):
    tree: app_commands.CommandTree
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.is_synced = False
    
    async def on_ready(self):
        await self.wait_until_ready()
        
        if not self.is_synced:
            await UsedClient.tree.sync(guild=discord.Object(id=settings.guild_id))
            self.is_synced = True
        main_logger.info(f"Successful login as: {self.user}")


client = UsedClient()
UsedClient.tree = app_commands.CommandTree(client)
@UsedClient.tree.command(name='test', guild=discord.Object(id=settings.guild_id))
async def slash(interaction: discord.Interaction, number: int, string: str):
    await interaction.response.send_message(f'{number=} {string=}', ephemeral=True)

@UsedClient.tree.command(name='asd', guild=discord.Object(id=settings.guild_id))
@app_commands.describe(attachment='The file to upload')
async def upload(interaction: discord.Interaction, attachment: discord.Attachment):
    await interaction.response.send_message(f'Thanks for uploading {attachment.filename}!', ephemeral=True)

@UsedClient.tree.command(name='fruit', guild=discord.Object(id=settings.guild_id))
@app_commands.describe(fruits='fruits to choose from')
@app_commands.choices(fruits=[
    Choice(name='apple', value=1),
    Choice(name='banana', value=2),
    Choice(name='cherry', value=3),
])
async def fruit(interaction: discord.Interaction, fruits: Choice[int]):
    await interaction.response.send_message(f'Your favourite fruit is {fruits.name}.')
    
        
client.run(settings.bot_token)


