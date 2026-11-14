from .emoji import EmojiManager
from .rich_message import RichMessage


async def setup(bot):
    await bot.add_cog(RichMessage(bot))
    await bot.add_cog(EmojiManager(bot))
