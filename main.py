import discord
import asyncio
import os
from discord.ext import commands
from mystery.game import Game

description = """Murder everyone!"""
token = os.environ["MysteryToken"]
game = None
bot = commands.Bot(command_prefix=commands.when_mentioned_or('>'), description=description)

@bot.command(description="Creates a game instance", pass_context=True)
async def create_game(ctx):
    global game
    if game == None and ctx.message.server:
        await bot.say("%s created a game! Preparing game instance..." %(ctx.message.author.mention))
        game = Game(bot, ctx.message.server)
        await game.prepare()
        await game.add_player(ctx.message.author)
        await bot.say("You can join the game now using >join or observe using >observe!")
        await game.start()
    elif game != None:
        await bot.say("A game already exists.")
    elif not ctx.message.server:
        await bot.say("You must create the game in a server, silly!")
    else:
        await bot.say("Unknown error...")

@bot.command(description="Stops a game instance", pass_context=True)
async def stop(ctx):
    await bot.say("Stopping game!")
    await game.stop()

@bot.command(description="Join the game", pass_context=True)
async def join(ctx):
    if game:
        code = await game.add_player(ctx.message.author)
        if not code:
            await bot.say("%s couldn't join. Try again later, please."%ctx.message.author.mention)

@bot.command(description="Observe the game", pass_context=True)
async def observe(ctx):
    if game:
        await game.add_observer(ctx.message.author)

@bot.command(description="Leave the game", pass_context=True)
async def leave(ctx):
    if game:
        await game.remove_player(ctx.message.author)

@bot.command(description="Get a list of locations at reach", pass_context=True)
async def locations(ctx):
    if game:
        if game.game_state == game.STATE_GAME:
            locstr = ""
            for name, location in game.locations.items():
                locstr += "%s: %s\n"%(name, location.topic)
            em = discord.Embed(title="Adjacent locations", description=locstr, colour=0x6699bb)
            em.set_footer(text="Locations you can move to right now")
            await bot.send_message(ctx.message.channel, embed=em)

@bot.command(description="Move to another location", pass_context=True)
async def move(ctx, location : str):
    if game:
        if game.game_state == game.STATE_GAME:
            if location in game.locations:
                await game.locations[location].player_enter(game.find_by_user(ctx.message.author))

if __name__ == "__main__":
    bot.run(token)
