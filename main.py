import discord
import asyncio
from discord.ext import commands
from mystery.game import Game

description = """Murder everyone!"""
token = ""
game = None
bot = commands.Bot(command_prefix=">", description=description)

@bot.command(description="Creates a game instance", pass_context=True)
async def create_game(ctx):
    if game == None and ctx.message.server:
        await bot.say("%s created a game! Join using >join" %(ctx.message.author.mention))
        global game
        game = Game(bot, ctx.)
    elif game != None:
        await bot.say("A game already exists.")
    elif not ctx.message.server:
        await bot.say("You must create the game in a server, silly!")
    else:
        await bot.say("Unknown error...")

@bot.command(description="Starts the game", pass_context=True)
async def start(ctx):
    """Puts the game in game mode."""
    await bot.say("%s started the game!" %(ctx.message.author.mention))

if __name__ == "__main__":
    bot.run(token)
