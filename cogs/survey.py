import discord
from discord.ext import commands
from discord import app_commands
import re
import json
from os import access,F_OK
from os import path as Path

from db import save_survey, get_survey_by_user  # Предполагается, что реализованы
CWD = Path.realpath(Path.dirname(__name__))
def JSONLoad(filename,cwd=CWD):	
    path = "{}\{}".format(cwd,filename)
    try:
        access(path, F_OK)
        with open(path, "r") as f:
            data = json.load(f)
        return data
    except:
        print("did not found '{}' file.".format(filename))
        return 0
CONFIG = JSONLoad("config.json")
SURVEY_CHANNEL_ID,REACTION_EMOJI = CONFIG["SURVEY_CHANNEL_ID"],CONFIG["REACTION_EMOJI"]

class SurveyModal(discord.ui.Modal, title="📔 Отправка анкеты"):
    data = JSONLoad("survey_questions.json")
    textInputs = {name:discord.ui.TextInput(**question) for name,question in data["questions"]}
    questionValues = {name:Input.value for name,Input in textInputs.items()} #MAY BREAK IF SOCIALS IS EMPTY
    async def on_submit(self, interaction: discord.Interaction):

        # Проверяем, что в age_value нет букв (латиницы и кириллицы)
        if re.search(r"[A-Za-zА-Яа-яЁё]", self.questionValues["age"].strip()):
            await interaction.response.send_message(
                "⚠️ В поле возраст нельзя вводить буквы. Пожалуйста, используйте цифры и символы.",
                ephemeral=True
            )
            return

        # Сохраняем анкету в базу данных
        save_survey(user_id=interaction.user.id, **self.questionValues)

        # Публикуем анкету в нужный канал
        channel = interaction.client.get_channel(SURVEY_CHANNEL_ID)
        if channel is None:
            await interaction.response.send_message("❌ Канал для публикации анкеты не найден.", ephemeral=True)
            return

        embed = discord.Embed(title="📝 Новая анкета", color=discord.Color.purple())
        for name,question in self.data["questions"]:
            embed.add_field(name=question["label"], value=self.questionValues[name] if self.questionValues[name] else "—", inline=False)
        embed.set_footer(text=f"Отправлено пользователем: {interaction.user.display_name}")

        msg = await channel.send(embed=embed)
        await msg.add_reaction(REACTION_EMOJI)

        await interaction.response.send_message("✅ Ваша анкета была успешно отправлена!", ephemeral=True)


class SurveyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="анкета", description="Редактировать или посмотреть анкету")
    @app_commands.describe(
        действие="Что сделать: редактировать или посмотреть",
        участник="Пользователь, чью анкету нужно посмотреть"
    )
    @app_commands.choices(
        действие=[
            app_commands.Choice(name="редактировать", value="редактировать"),
            app_commands.Choice(name="посмотреть", value="посмотреть")
        ]
    )
    async def анкета(
        self,
        interaction: discord.Interaction,
        действие: app_commands.Choice[str],
        участник: discord.User = None
    ):
        if действие.value == "редактировать":
            await interaction.response.send_modal(SurveyModal())
        elif действие.value == "посмотреть":
            user = участник or interaction.user

            # Получаем анкету из БД
            data = get_survey_by_user(user.id)
            if not data:
                await interaction.response.send_message("❌ Анкета не найдена.", ephemeral=True)
                return

            embed = discord.Embed(
                title=f"📝 Анкета пользователя {user.display_name}",
                color=discord.Color.green()
            )
            for name,question in self.data["questions"]:
                embed.add_field(name=question["label"], value=self.questionValues[name] if self.questionValues[name] else "—", inline=False)
            embed.set_footer(text=f"Пользователь: {user.display_name}")

            await interaction.response.send_message(embed=embed, ephemeral=True)

    # НЕ нужно повторно добавлять команду в on_ready, если используется discord.py 2.x+
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.bot.tree.add_command(self.анкета)


async def setup(bot):
    await bot.add_cog(SurveyCog(bot))
