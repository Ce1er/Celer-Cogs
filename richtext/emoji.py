import discord

from redbot.core import commands, app_commands


class EmojiManager(commands.Cog):
    """Show information about a flight."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def send_emoji(self, interaction: discord.Interaction, name: str):
        emojis = await interaction.client.fetch_application_emojis()
        for emoji in emojis:
            if emoji.name == name:
                await interaction.response.send_message(str(emoji))

        await interaction.response.send_message("Couldn't find emoji", ephemeral=True)
