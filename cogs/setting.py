import discord
from discord.ext import commands
from discord import app_commands
import json

class SettingsButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Settings Channel", style=discord.ButtonStyle.primary, emoji="📝")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        # from cogs.survey import SurveyModal Make
        await interaction.response.send_modal()

class SettingCog():
    def __init__(self, bot):
        self.bot = bot
    # Write check user to administrator

    @app_commands.command(name="Setting",description="Admin setting")
    @app_commands.describe(name="Settings choice")
    @app_commands.choices(
        name={
            app_commands.Choice(name="Settings Channel", value="Settings Channel")
        }
    )

    async def setting(self, ):
        embed = discord.Embed(
            title={"Administrator Settings"},
            description=(
                "Channel for moderation",
                "Channel for form",
                "Channel for submitting an application",              
                ),
            color=discord.Color.blue()
            
            )