import discord
from discord import app_commands
from discord.app_commands import Choice
from utils.logging_setup import retrieve_logger
from utils.config import settings, scope


import gspread_asyncio
from oauth2client.service_account import ServiceAccountCredentials

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


google_client_manager = gspread_asyncio.AsyncioGspreadClientManager(lambda: ServiceAccountCredentials.from_json_keyfile_name(settings.creds_filename, scopes=scope))
client = UsedClient()
UsedClient.tree = app_commands.CommandTree(client)




@UsedClient.tree.command(name='request', guild=discord.Object(id=settings.guild_id))
@app_commands.describe(request_type='Select the request type')
@app_commands.describe(description='Provide an in-depth description')
@app_commands.choices(request_type=[
    Choice(name='schedule/reschedule a match', value=0),
    Choice(name='report a problem', value=1),
])
async def submit_request(interaction: discord.Interaction, request_type: Choice[int], description: str):
    await interaction.response.send_message('Your message is currently being sent...', ephemeral=True)
    session = await google_client_manager.authorize()
    ss = await session.open_by_key(settings.sheet_id)
    ws = await ss.get_worksheet(0)
    
    last_empty_row_index = len(await ws.get_all_values()) + 1
    await ws.update_cell(last_empty_row_index, 1, request_type.value)
    await ws.update_cell(last_empty_row_index, 2, description)
    #await interaction.response.send_message('Your message will be delivered to the corresponding staff team member.', ephemeral=True)
    #await interaction.response.send_message(f"You have chosen: {request_type.name}, corresponding to {request_type.value}. You are telling: {description}", ephemeral=True)
    await interaction.edit_original_response(content='Your message was successfully delivered!')
    
client.run(settings.bot_token)

#simple examples, to be removed

# @UsedClient.tree.command(name='test', guild=discord.Object(id=settings.guild_id))
# async def slash(interaction: discord.Interaction, number: int, string: str):
#     await interaction.response.send_message(f'{number=} {string=}', ephemeral=True)

# @UsedClient.tree.command(name='asd', guild=discord.Object(id=settings.guild_id))
# @app_commands.describe(attachment='The file to upload')
# async def upload(interaction: discord.Interaction, attachment: discord.Attachment):
#     await interaction.response.send_message(f'Thanks for uploading {attachment.filename}!', ephemeral=True)




# @UsedClient.tree.command(name='fruit', guild=discord.Object(id=settings.guild_id))
# @app_commands.describe(fruits='fruits to choose from')
# @app_commands.choices(fruits=[
#     Choice(name='apple', value=1),
#     Choice(name='banana', value=2),
#     Choice(name='cherry', value=3),
# ])
# async def fruit(interaction: discord.Interaction, fruits: Choice[int]):
#     await interaction.response.send_message(f'Your favourite fruit is {fruits.name}.')


    
        


