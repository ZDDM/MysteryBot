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
        else:
            await bot.say("You can't do that now, %s!"%ctx.message.author.mention)

@bot.command(description="Move to another location", pass_context=True)
async def move(ctx, location : str):
    if game:
        if game.game_state == game.STATE_GAME:
            if location in game.locations:
                player = game.find_by_user(ctx.message.author)
                if not player.move_cooldown:
                    await game.locations[location].player_enter(player)
                    player.move_cooldown = True
                    await asyncio.sleep(3)
                    player.move_cooldown = False
                else:
                    await bot.say("Can't move yet!")
        else:
            await bot.say("You can't do that now, %s!"%ctx.message.author.mention)

@bot.command(description="Examines the room you're in.", pass_context=True)
async def look(ctx):
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer:
                    await bot.send_message(player.location.channel, "%s takes a look around..." %(player.name))
                    em = discord.Embed(title="%s"%player.location.name, description=player.location.examine(), colour=0x6699bb)
                    em.set_footer(text=player.location.topic)
                    await bot.send_message(player.user, embed=em)
                    return
            await bot.say("You're not a player!")
        await bot.say("You can't do that now, %s!"%ctx.message.author.mention)

@bot.command(description="Use the item you've equipped. If it's a weapon, you can commit suicide by using it.", pass_context=True)
async def use(ctx):
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer:
                    if player.equipped_item:
                        if hasattr(player.equipped_item, "use"):
                            await player.equipped_item.use()
                        else:
                            await bot.send_message(player.user, "You can't use that!")

@bot.command(description="Sends you a private message with the contents of your inventory.", pass_context=True)
async def inventory(ctx):
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer:
                    if len(player.inventory):
                        invcont = ""
                        for item in player.inventory:
                            invcont += "%s \n"%(item._name)
                        em = discord.Embed(title="Inventory", description=invcont, colour=0x6699bb)
                        await bot.send_message(player.user, embed=em)

@bot.command(description="Picks up an item from the location you're in.", pass_context=True)
async def pickup(ctx, item : str):
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer:
                    fitem = player.location.find_item(item)
                    if fitem:
                        fitem.pickup(player)
                        await bot.say("%s picks up the %s!"%(player.user.mention, fitem.name()))
                    else:
                        await bot.say("There's no such item in here.")

@bot.command(description="Drops an item to the location you're in.", pass_context=True)
async def drop(ctx, item : str):
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer:
                    fitem = player.find_item(item)
                    if fitem:
                        fitem.drop()
                        await bot.say("%s drops the %s!"%(player.user.mention, fitem.name()))
                    else:
                        await bot.say("There's no such item in your inventory.")

@bot.command(description="Attacks another person in your location. If you don't have a weapon equipped, you'll attack them with your fists!", pass_context=True)
async def attack(ctx, who : discord.Member):
    pass

if __name__ == "__main__":
    bot.run(token)
