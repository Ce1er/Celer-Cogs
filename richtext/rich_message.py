import discord

from io import BytesIO
from pathlib import Path
import asyncio
import subprocess
import tempfile
import dateutil
from enum import Enum

from redbot.core import commands, app_commands

class DateFormat(Enum):
    TIMER = "R"
    TIME = "t"
    SECONDS_TIME = "T"
    DATE = "d"
    DATETIME = "s"
    DATETIME_SECONDS = "S"
    MONTH_DATE = "D"
    MONTH_DATETIME = "f"
    LONG = "F"

def latex_to_png(latex: str, density: int) -> bytes:
    with tempfile.TemporaryDirectory() as temp_dir:
        workdir = Path(temp_dir)
        tex_path = workdir / "input.tex"

        tex_path.write_text(latex, encoding="utf-8")

        subprocess.run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                "input.tex",
            ],
            cwd=workdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        subprocess.run(
            [
                "convert",
                "-density",
                "300",
                "-background",
                "white",
                "-alpha",
                "remove",
                "-alpha",
                "off",
                "input.pdf",
                "output.png",
            ],
            cwd=workdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        return (workdir / "output.png").read_bytes()


class LatexModal(discord.ui.Modal, title="Render LaTeX"):
    latex = discord.ui.TextInput(
        label="LaTeX",
        style=discord.TextStyle.paragraph,
        max_length=4000,
    )
    extra_preamble = discord.ui.TextInput(
        label="Extra preamble",
        style=discord.TextStyle.paragraph,
        max_length=4000,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        preamble = r"""
        \documentclass[preview]{standalone}
        \usepackage[latin1]{inputenc}
        \usepackage{float}
        \usepackage{amsmath}
        \usepackage{amssymb}
        \usepackage{subcaption}
        \usepackage{xcolor}
        \usepackage{soul}
        \usepackage{bera}
        \usepackage{graphicx}
        \usepackage{listings}
        \usepackage{standalone}
        \usepackage[english]{babel}
        \usepackage{hyperref}
        \hypersetup{
        colorlinks=true, linkcolor=black, urlcolor=cyan
        }


        \begin{document}
        """
        ending = r"\end{document}"
        latex = (
            preamble
            + "\n"
            + self.extra_preamble.value
            + self.latex.value
            + "\n"
            + ending
            + "\n"
        )

        png_bytes = await asyncio.to_thread(latex_to_png, latex, 300)

        await interaction.response.send_message(
            file=discord.File(BytesIO(png_bytes), filename="output.png")
        )


class RichMessage(commands.Cog):
    """Show information about a flight."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def tex_message(self, interaction: discord.Interaction):
        """Message with TeX inspired rich formatting."""
        await interaction.response.send_modal(LatexModal())

    @app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def echo(self, interaction: discord.Interaction, message: str):
        """Message with TeX inspired rich formatting."""
        await interaction.response.send_message(message)


    @app_commands.command()
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def dev_timestamp(self, interaction: discord.Interaction, datetime:str, format: DateFormat=DateFormat.TIMER):
        """Echo text"""
        try:
            date = dateutil.parser.parse(datetime)
        except Exception as e:
            await interaction.response.send_message(f"Invalid date: {e}", ephemeral=True)
            return

        await interaction.response.send_message("<t:"+str(int(date.timestamp()))+f":{format.value}>")
