import discord
from discord import app_commands
from discord.app_commands import Choice
from utils.logging_setup import retrieve_logger
from utils.config import settings, google_client_manager
from utils.schemas import ReturnedUserData
from utils.sheet_tools import *


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

    ws = await get_requests_worksheet()

    returned_model = ReturnedUserData(request_type_name=request_type.name,
                                      request_description=description,
                                      discord_user=get_discord_name(
                                          interaction),
                                      assigned_status='unprocessed')

    await ws.update(await generate_request_lookup_string(ws), [list(returned_model.dict().values())])

    await interaction.edit_original_response(content='Your message was successfully delivered!')


class Confirm_Remove_Buttons(discord.ui.View):
    def __init__(self, parent_interaction: discord.Interaction, application_embed: discord.Embed):
        self.parent_interaction = parent_interaction
        self.application_embed = application_embed
        super().__init__()

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = client.get_channel(settings.looking_for_team_channel_id)
        await channel.send(embed=self.application_embed)
        await self.parent_interaction.edit_original_response(content='The application has been successfully submitted!', embed=None, view=None)
        return

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.gray)
    async def remove_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.parent_interaction.edit_original_response(content='The application will not be submitted.', embed=None, view=None)
        return


@UsedClient.tree.command(name='looking_for_team', guild=discord.Object(id=settings.guild_id))
@app_commands.describe(player_tier='Select the tier you are applying for')
@app_commands.describe(description="Name your strengths and weaknesses")
@app_commands.describe(osu_profile_id="Provide your osu! profile ID")
@app_commands.choices(player_tier=[
    Choice(name='High tier', value=0),
    Choice(name='Mid tier', value=1),
    Choice(name='Low tier', value=2),
])
async def submit_looking_for_team(interaction: discord.Interaction, player_tier: Choice[int], description: str, osu_profile_id: int):
    await interaction.response.send_message('Validating the data...', ephemeral=True)

    is_profile_valid, validation_message, generated_profile_link = await validate_osu_profile(player_tier.value, osu_profile_id)

    if not is_profile_valid:
        main_logger.warning(
            f"User {get_discord_name(interaction)} has not passed the validation! Validation message: {validation_message}")
        await interaction.edit_original_response(content=validation_message)
        return

    await interaction.edit_original_response(content="Profile successfully validated! Creating a post...")

    converted_description = prepare_player_description(
        generated_profile_link, description)

    embed = discord.Embed(color=discord.Color.blurple(), title=get_discord_name(
        interaction), description=converted_description)

    await interaction.edit_original_response(content="Take a look at a preview of your post and make sure everything is correct!",
                                             embed=embed,
                                             view=Confirm_Remove_Buttons(interaction, embed))


client.run(settings.bot_token)

# simple examples, to be removed

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
