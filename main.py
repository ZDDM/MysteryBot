import discord
import asyncio
from discord.ext import commands
from mystery.game import Game

description = """Murder everyone!"""
token = ""
game = None
bot = commands.Bot(command_prefix=commands.when_mentioned_or('>'), description=description)

@bot.command(description="Creates a game instance", pass_context=True)
async def create_game(ctx):
    global game
    if game == None and ctx.message.server:
        await bot.say("%s created a game! Join using >join and observe with >observe" %(ctx.message.author.mention))
        game = Game(bot, ctx.message.server)
    elif game != None:
        await bot.say("A game already exists.")
    elif not ctx.message.server:
        await bot.say("You must create the game in a server, silly!")
    else:
        await bot.say("Unknown error...")

@bot.command(description="Stops a game instance", pass_context=True)
async def stop(ctx):
    await bot.say("Stopping game!")
    game.stop()

@bot.command(description="Join the game", pass_context=True)
async def join(ctx):
    if game:
        game.add_player(ctx.message.author)

@bot.command(description="Leave the game", pass_context=True)
async def leave(ctx):
    if game:
        game.remove_player(ctx.message.author)

@bot.command(description="Get a list of locations at reach", pass_context=True)
async def locations(ctx):
    if game:
        if game.game_state == game.STATE_GAME:
            bot.say("".join(game.locations))

@bot.command(description="Move to another location", pass_context=True)
async def move(ctx):
    if game:
        if game.game_state == game.STATE_GAME:
            if ctx.subcommand_passed:
                if game.locations.has_key(ctx.subcommand_passed):
                    await game.locations[ctx.subcommand_passed].player_enter(game.find_by_user(ctx.message.author))

if __name__ == "__main__":
    bot.run(token)
