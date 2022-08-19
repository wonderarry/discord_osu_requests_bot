import discord
from discord import app_commands
from discord.app_commands import Choice
from utils.logging_setup import retrieve_logger
from utils.config import settings, google_client_manager
from utils.schemas import ReturnedUserData, ApplicationPlayerData
from utils.sheet_tools import *
from utils.views import Application_Confirm_Remove_Buttons, Request_Confirm_Remove_Button

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
    await interaction.response.send_message('Your message is currently being validated...', ephemeral=True)

    ws = await get_requests_worksheet()

    returned_model = ReturnedUserData(request_type_name=request_type.name,
                                      request_description=description,
                                      discord_user=get_discord_name(
                                          interaction),
                                      assigned_status='unprocessed')

    embed = discord.Embed(color=discord.Color.blurple(
    ), title="Request Preview", description=prepare_request_description(discord_username=returned_model.discord_user,
                                                                        request_type_name=returned_model.request_type_name,
                                                                        text_description=returned_model.request_description))

    await interaction.edit_original_response(content="Here's a preview of the request you are about to send. Make sure everything is correct before sending it!",
                                             embed=embed,
                                             view=Request_Confirm_Remove_Button(
                                                 interaction,
                                                 await generate_request_lookup_string(ws),
                                                 [list(returned_model.dict().values())],
                                                 ws))


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

    ws = await get_application_worksheet()
    
    returned_model = ApplicationPlayerData(player_tier_value=player_tier.value,
                                           player_tier_name=player_tier.name,
                                           player_profile_link=generated_profile_link,
                                           player_description=description,
                                           discord_user=get_discord_name(interaction))

    await interaction.edit_original_response(content="Profile successfully validated! Creating a post...")

    embed = discord.Embed(color=discord.Color.blurple(),
                          title=returned_model.discord_user,
                          description=prepare_player_description(returned_model.player_profile_link,
                                                                 returned_model.player_tier_name,
                                                                 returned_model.player_description))

    await interaction.edit_original_response(content="Take a look at a preview of your post and make sure everything is correct!",
                                             embed=embed,
                                             view=Application_Confirm_Remove_Buttons(interaction,
                                                                                     embed,
                                                                                     client,
                                                                                     await generate_application_lookup_string(ws),
                                                                                     [list(returned_model.dict().values())[1:]],
                                                                                     ws))


client.run(settings.bot_token)

