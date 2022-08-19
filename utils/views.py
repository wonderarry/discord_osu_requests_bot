import discord
from utils.config import settings
from typing import List, Any
import gspread_asyncio

class Base_Confirm_Remove_Buttons(discord.ui.View):
    def __init__(self, parent_interaction: discord.Interaction, worksheet_value_range: str, worksheet_data: List[List[Any]], worksheet: gspread_asyncio.AsyncioGspreadWorksheet):
        self.parent_interaction = parent_interaction
        self.worksheet_value_range = worksheet_value_range
        self.worksheet_data = worksheet_data
        self.worksheet = worksheet
        super().__init__()
    

class Application_Confirm_Remove_Buttons(Base_Confirm_Remove_Buttons):
    def __init__(self,
                 parent_interaction: discord.Interaction,
                 application_embed: discord.Embed,
                 client: discord.Client,
                 worksheet_value_range: str,
                 worksheet_data: List[List[Any]],
                 worksheet: gspread_asyncio.AsyncioGspreadWorksheet
                 ):
        
        self.client = client
        self.application_embed = application_embed
        super().__init__(parent_interaction, worksheet_value_range, worksheet_data, worksheet)


    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = self.client.get_channel(settings.looking_for_team_channel_id)
        await channel.send(embed=self.application_embed)
        await self.worksheet.update(self.worksheet_value_range, self.worksheet_data)
        await self.parent_interaction.edit_original_response(content='The application has been successfully submitted!', embed=None, view=None)
        return


    @discord.ui.button(label='Remove', style=discord.ButtonStyle.gray)
    async def remove_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.parent_interaction.edit_original_response(content='The application will not be submitted.', embed=None, view=None)
        return
    
    
class Request_Confirm_Remove_Button(Base_Confirm_Remove_Buttons):
    def __init__(self, parent_interaction: discord.Interaction, worksheet_value_range: str, worksheet_data: List[List[Any]], worksheet: gspread_asyncio.AsyncioGspreadWorksheet):
        super().__init__(parent_interaction, worksheet_value_range, worksheet_data, worksheet)
        
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm_button(self, button: discord.ui.Button, interaction: discord.Interaction):  
        await self.worksheet.update(self.worksheet_value_range, self.worksheet_data)
        await self.parent_interaction.edit_original_response(content='The request was successfully submitted!', embed=None, view=None)
        return
        pass
    @discord.ui.button(label='Remove', style=discord.ButtonStyle.gray)
    async def remove_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.parent_interaction.edit_original_response(content='The request will not be submitted.', embed=None, view=None)
        return 
    