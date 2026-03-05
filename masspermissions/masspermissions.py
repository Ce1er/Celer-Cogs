"""
MIT License

Copyright (c) 2026-present Ce1er

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from collections import defaultdict
from typing import Set, Optional, Literal
import io

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import box, pagify


class MassPermissions(commands.Cog):
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=3731648926068903790, force_registration=True
        )
        default_global = {"permissions": 8, "whitelisted": []}
        self.config.register_global(**default_global)
        self.perms: Optional[discord.Permissions] = None
        self._whitelist: Set[int] = set()

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        return

    @commands.group()
    @commands.guild_only()
    async def massperms(self, ctx):
        """Mass permissions group command."""

    @commands.admin()
    @massperms.command()
    async def members(self, ctx):
        pass

    @commands.admin()
    @massperms.command()
    async def channels(self, ctx):
        pass

    @massperms.group()
    async def roles(self, ctx):
        """Mass permissions role group."""

    @commands.admin()
    @roles.command(name="dict")
    async def roles_dict(self, ctx):
        perms = {}
        for role in ctx.guild.roles:
            human = []
            for perm, value in role.permissions:
                if value:
                    human.append(perm)

            perms[role.id] = {
                "name": role.name,
                "permissions": role.permissions.value,
                "permissions_human": human,
                "colour": role.colour.to_rgb(),
                "hoisted": role.hoist,
                "position": role.position,
                "managed": role.managed,
                "mentionable": role.mentionable,
                "created_at": role.created_at,
                "members": list(map(lambda x: x.id, role.members)),
            }

        file = discord.File(io.StringIO(str(dict(perms))), filename="output.py")

        await ctx.send(file=file)

    @commands.admin()
    @roles.command(name="embed")
    async def roles_embed(
        self, ctx, show_all: Literal["all", ""] = "", inline: Literal["inline", ""] = ""
    ):
        include_all: bool = show_all == "all"
        as_inline: bool = inline == "inline"

        perms = defaultdict(list)
        for role in ctx.guild.roles:
            if role.permissions.administrator:
                perms[role].append("administrator")
                continue

            for perm, value in role.permissions:
                if value:
                    perms[role].append(perm)
            if len(perms[role]) == 0:
                perms[role].append("no_permissions")

        # embeds = [discord.Embed()]
        # embeds[0].title = "Role Permissions"
        perms = dict(sorted(perms.items(), key=lambda item: -item[0].position))

        messages: list[list[discord.Embed]] = [[discord.Embed()]]
        messages[0][0].title = "Role Permissions"
        chars = len(messages[0][0].title)
        embeds = 1
        fields = 0
        for role, permissions in perms.items():
            title = ""
            description = role.mention + "\n" + ", ".join(sorted(permissions))

            chars += (current := len(title) + len(description))

            if embeds >= 10 or chars > 6000:
                messages.append([discord.Embed()])
                chars = current
                fields = 1
                embeds = 1

            elif fields >= 25:
                messages[-1].append(discord.Embed())
                embeds += 1
                fields = 1

            messages[-1][-1].add_field(name=title, value=description, inline=as_inline)
            fields += 1

        for message in messages:
            for embed in message:
                chars = 0
                for field in embed.fields:
                    chars += len(field.name) + len(field.value)

        for message in messages:
            await ctx.send(embeds=message)
