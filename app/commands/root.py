from commands import permissions, command


@command("random", keep_args=False, aliases=["rand"])
async def random_command(msg):
    await msg.reply("Hello World!")


@command("rando", keep_args=True, aliases=["ran"])
async def random_command(msg, rest):
    await msg.reply("Hello World!" + " " + rest)
