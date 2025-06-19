import discord
from discord.ext import commands
from discord import app_commands
import re

from db import save_survey, get_survey_by_user  # Предполагается, что реализованы

SURVEY_CHANNEL_ID = 1384511819237822545
REACTION_EMOJI = "❤️"

class SurveyModal(discord.ui.Modal, title="📔 Отправка анкеты"):
    name = discord.ui.TextInput(
        label="Имя / Псевдоним",
        placeholder="Как к Вам обращаться?",
        required=True,
        max_length=100
    )

    age = discord.ui.TextInput(
        label="Возраст",
        placeholder="Можете также указать свой ДР.",
        required=True,
        max_length=50
    )

    creative_fields = discord.ui.TextInput(
        label="Вид деятельности",
        placeholder="Можно указать несколько направлений.",
        required=True,
        max_length=200
    )

    about = discord.ui.TextInput(
        label="О себе",
        placeholder="Напишите не менее 100 символов. И без самохейта и спама!",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=100
    )

    socials = discord.ui.TextInput(
        label="Ссылки на соцсети",
        placeholder="Можно оставить пустым...",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        age_value = self.age.value.strip()

        # Проверяем, что в age_value нет букв (латиницы и кириллицы)
        if re.search(r"[A-Za-zА-Яа-яЁё]", age_value):
            await interaction.response.send_message(
                "⚠️ В поле возраст нельзя вводить буквы. Пожалуйста, используйте цифры и символы.",
                ephemeral=True
            )
            return

        # Сохраняем анкету в базу данных
        save_survey(
            user_id=interaction.user.id,
            name=self.name.value,
            age=self.age.value,
            creative_fields=self.creative_fields.value,
            about=self.about.value,
            socials=self.socials.value if self.socials.value else None
        )

        # Публикуем анкету в нужный канал
        channel = interaction.client.get_channel(SURVEY_CHANNEL_ID)
        if channel is None:
            await interaction.response.send_message("❌ Канал для публикации анкеты не найден.", ephemeral=True)
            return

        embed = discord.Embed(title="📝 Новая анкета", color=discord.Color.purple())
        embed.add_field(name="Имя / Псевдоним", value=self.name.value, inline=False)
        embed.add_field(name="Возраст", value=self.age.value, inline=False)
        embed.add_field(name="Вид деятельности", value=self.creative_fields.value, inline=False)
        embed.add_field(name="О себе", value=self.about.value, inline=False)
        embed.add_field(name="Соцсети", value=self.socials.value if self.socials.value else "—", inline=False)
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
            embed.add_field(name="Имя / Псевдоним", value=data["name"], inline=False)
            embed.add_field(name="Возраст", value=data["age"], inline=False)
            embed.add_field(name="Вид деятельности", value=data["creative_fields"], inline=False)
            embed.add_field(name="О себе", value=data["about"], inline=False)
            embed.add_field(name="Соцсети", value=data["socials"] if data["socials"] else "—", inline=False)
            embed.set_footer(text=f"Пользователь: {user.display_name}")

            await interaction.response.send_message(embed=embed, ephemeral=True)

    # НЕ нужно повторно добавлять команду в on_ready, если используется discord.py 2.x+
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.bot.tree.add_command(self.анкета)


async def setup(bot):
    await bot.add_cog(SurveyCog(bot))
