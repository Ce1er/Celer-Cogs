from redbot.core.utils.chat_formatting import pagify

def code_pagify(language: str, *args, **kwargs):
    for part in pagify(*args, **kwargs, page_length=2000 - len(language) - 7):
        yield f"```{language}\n{part}```"
