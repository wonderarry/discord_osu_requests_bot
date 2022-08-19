import discord
from utils.config import settings

class Confirm_Remove_Buttons(discord.ui.View):
    def __init__(self, parent_interaction: discord.Interaction, application_embed: discord.Embed, client: discord.Client):
        self.parent_interaction = parent_interaction
        self.application_embed = application_embed
        self.client = client
        super().__init__()

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = self.client.get_channel(settings.looking_for_team_channel_id)
        await channel.send(embed=self.application_embed)
        await self.parent_interaction.edit_original_response(content='The application has been successfully submitted!', embed=None, view=None)
        return

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.gray)
    async def remove_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.parent_interaction.edit_original_response(content='The application will not be submitted.', embed=None, view=None)
        return