import discord
from discord.ext import commands
from discord import app_commands

class SurveyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Заполнить анкету", style=discord.ButtonStyle.primary, emoji="📝")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        from cogs.survey import SurveyModal
        await interaction.response.send_modal(SurveyModal())

class TemplateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="шаблон", description="Отправить шаблон анкеты с кнопкой")
    @app_commands.describe(имя="Тип шаблона")
    @app_commands.choices(
        имя=[
            app_commands.Choice(name="анкета", value="анкета"),
            # можно добавить другие виды, если появятся в будущем
        ]
    )
    async def шаблон(self, interaction: discord.Interaction, имя: app_commands.Choice[str]):
        embed = discord.Embed(
            title=f"📔 Шаблон {имя.value}",
            description=(
                "Нажмите на кнопку ниже, чтобы заполнить анкету.\n\n"
                "📔ㅤ⁠Анкета - возможность, в которой Вы можете кратко рассказать другим участникам о себе, "
                "своих интересах, своём творчестве, а также поделиться ссылками на Ваши соц. сети."
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=SurveyButton())

async def setup(bot):
    await bot.add_cog(TemplateCog(bot))
