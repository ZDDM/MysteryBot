import discord
import asyncio
import random
import os
from discord.ext import commands
from mystery.game import Game

description = """Murder everyone!"""
token = os.environ["MysteryToken"]
game = None
bot = commands.Bot(command_prefix=commands.when_mentioned_or('>'), description=description)
__version__ = "v0.1.0"

@bot.command(description="Returns the version of the bot.")
async def version():
    '''Returns the version of the bot.'''
    await bot.say("```MysteryBot version %s```" %(__version__))

@bot.command(description="Creates a game instance. The argument time is how much the bot will wait before starting the game.", pass_context=True)
async def create_game(ctx, timer : int = 45):
    '''Create a new instance of the game if one isn't running already. Takes a "time" argument.'''
    if timer >= 15:
        global game
        if game == None and ctx.message.server:
            await bot.say("%s created a game! Preparing game instance..." %(ctx.message.author.mention))
            game = Game(bot, ctx.message.server, cleanup_game)
            await game.prepare()
            await game.add_player(ctx.message.author)
            await bot.say("You can join the game now using >join or observe using >observe!")
            await game.start(timer)
        elif game != None:
            await bot.say("A game already exists.")
        elif not ctx.message.server:
            await bot.say("You must create the game in a server, silly!")
        else:
            await bot.say("Unknown error...")
    else:
        await bot.say("That's too low! Try setting the timer to be higher than 15 seconds")

@bot.command(description="Stops a game instance, allowing you to create a new one.", pass_context=True)
async def stop(ctx):
    '''Ends the current game.'''
    global game
    if game:
        if game.game_state == game.STATE_GAME:
            await bot.say("Ending game!")
            await game.end_game()
            game = None
        elif game.game_state == game.STATE_END:
            await bot.say("Stopping game!")
            await game.stop()
            game = None


@bot.command(description="Join the game", pass_context=True)
async def join(ctx):
    '''Allows you to join a game instance as a player.'''
    if game:
        code = await game.add_player(ctx.message.author)
        if not code:
            await bot.say("%s couldn't join. Try again later, please."%ctx.message.author.mention)

@bot.command(description="Observe the game", pass_context=True)
async def observe(ctx):
    '''Allows you to join a game instance as an observer.'''
    if game:
        await game.add_observer(ctx.message.author)

@bot.command(description="Leave the game", pass_context=True)
async def leave(ctx):
    '''Allows you to leave the game if it hasn't started already.'''
    if game:
        await game.remove_player(ctx.message.author)

@bot.command(description="Get a list of locations at reach", pass_context=True)
async def locations(ctx):
    '''Returns a list of locations you can move to right now.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            locstr = ""
            for location in player.location.adjacent_locations:
                locstr += "%s: %s\n"%(location.name, location.topic)
            em = discord.Embed(title="Adjacent locations", description=locstr, colour=0x6699bb)
            em.set_footer(text="Locations you can move to right now")
            await bot.send_message(ctx.message.channel, embed=em)
        else:
            await bot.say("You can't do that now, %s!"%ctx.message.author.mention)

@bot.command(description="Move to another location", pass_context=True)
async def move(ctx, location : str):
    '''Allows you to move to an adjacent location.'''
    if game:
        if game.game_state == game.STATE_GAME:
            location = game.find_location(location)
            if location:
                player = game.find_by_user(ctx.message.author)
                if (not player.is_observer) and (not player.is_dead):
                    if (location in player.location.adjacent_locations):
                        if not player.move_cooldown:
                            await location.player_enter(player)
                            player.move_cooldown = True
                            await asyncio.sleep(location.cooldown)
                            player.move_cooldown = False
                        else:
                            await bot.say("%s gasps for air!"%(player.name))
                    else:
                        await bot.say("That location is not adjacent to your current location!")
        else:
            await bot.say("You can't do that now, %s!"%ctx.message.author.mention)

@bot.command(description="Examines the room you're in.", pass_context=True)
async def look(ctx):
    '''Returns information about the room, the people in it... Takes no arguments'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer and not player.is_dead:
                    examined = player.location.examine()
                    await bot.send_message(player.location.channel, "%s takes a look around..." %(player.name))
                    emloc = discord.Embed(title="%s - Location info"%player.location.name, description=examined["location"], colour=0x6699bb)
                    emloc.set_footer(text=player.location.topic)
                    empla = discord.Embed(title="%s - People"%player.location.name, description=examined["players"], colour=0x6699bb)
                    empla.set_footer(text=player.location.topic)
                    emfur = discord.Embed(title="%s - Furniture"%player.location.name, description=examined["furniture"], colour=0x6699bb)
                    emfur.set_footer(text=player.location.topic)
                    emitem = discord.Embed(title="%s - Items"%player.location.name, description=examined["items"], colour=0x6699bb)
                    emitem.set_footer(text=player.location.topic)
                    await bot.send_message(player.user, "-----------------------------------")
                    await bot.send_message(player.user, embed=emloc)
                    await bot.send_message(player.user, embed=empla)
                    await bot.send_message(player.user, embed=emfur)
                    await bot.send_message(player.user, embed=emitem)
                    await bot.send_message(player.user, "-----------------------------------")

@bot.command(description="Use the item you've equipped. Pass an user as the second argument and if the item allows it, you'll use it on them.", pass_context=True)
async def use(ctx, item : str, *args):
    '''Allows you to use an item in your inventory.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                item = player.find_item(item)
                if not player.is_observer and not player.is_dead:
                    if item:
                        if hasattr(item, "use"):
                            await item.use(*args)
                        else:
                            await bot.say("You can't use that item!")
                    else:
                        await bot.say("There's no such item!")

@bot.command(description="Sends you a private message with the contents of your inventory.", pass_context=True)
async def inventory(ctx):
    '''Returns information about all the items in your inventory'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer and not player.is_dead:
                    if len(player.inventory):
                        invcont = ""
                        for item in player.inventory:
                            invcont += "__%s__ - %s\n"%(item._name, item.examine())
                        em = discord.Embed(title="Inventory", description=invcont, colour=0x6699bb)
                        await bot.send_message(player.user, embed=em)

@bot.command(description="Picks up an item from the location you're in.", pass_context=True)
async def pickup(ctx, item : str):
    '''Allows you to pick up an item from your current location.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer and not player.is_dead:
                    fitem = player.location.find_item(item)
                    if fitem:
                        fitem.pickup(player)
                        await bot.say("%s picks up the %s!"%(player.user.mention, fitem.name()))
                    else:
                        await bot.say("There's no such item in here.")

@bot.command(description="Drops an item to the location you're in.", pass_context=True)
async def drop(ctx, item : str):
    '''Allows you to drop an item.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer and not player.is_dead:
                    fitem = player.find_item(item)
                    if fitem:
                        fitem.drop()
                        await bot.say("%s drops the %s!"%(player.user.mention, fitem.name()))
                    else:
                        await bot.say("There's no such item in your inventory.")

@bot.command(description="Equips an item from your inventory.", pass_context=True)
async def equip(ctx, item : str):
    '''Allows you to equip an item from your inventory.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer and not player.is_dead:
                    fitem = player.find_item(item)
                    if fitem:
                        code = player.equip(fitem)
                        if code:
                            await bot.say("%s takes out %s %s from their inventory and holds it in their hands."%(player.name, fitem.indef_article(), fitem.name()))
                        else:
                            await bot.say("%s wonders where they put their %s... Until they realize it was in their hands all along. How dumb." %(player.name, fitem.name()))
                    else:
                        await bot.say("There's no such item in your inventory.")

@bot.command(description="Unequips an item from your inventory.", pass_context=True)
async def unequip(ctx):
    '''Allows you to unequip the item you are holding.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                if not player.is_observer and not player.is_dead:
                    if player.equipped_item:
                        await bot.say("%s stores their %s in their inventory."%(player.user.mention, player.equipped_item.name()))
                        player.equipped_item = None
                    else:
                        await bot.say("%s tries to store their hands in their inventory! ...Until they realize that's not possible."%(player.user.mention))

@bot.command(description="Attacks another person in your location. If you don't have a weapon equipped, you'll attack them with your fists!", pass_context=True)
async def attack(ctx, who : discord.Member):
    '''Allows you to attack a person in your location.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            other = game.find_by_member(who)
            if player and other:
                if not ((player.is_observer or player.is_dead) or (other.is_observer or other.is_dead)) and (player.location == other.location):
                    code = await player.attack(other)
                    if code == player.ATTACK_COOLDOWN:
                        await bot.say("%s gasps for air!" %(player.name))
                    elif code == player.ATTACK_FAIL:
                        await bot.say("%s evades %s's attack!"%(other.name, player.name))
                    elif code == player.ATTACK_SUCCESS:
                        if player.equipped_a_weapon():
                            await bot.say("%s attacks %s with %s %s!"%(player.name, other.name, player.equipped_item.indef_article(), player.equipped_item.name()))
                        else:
                            await bot.say("%s punches %s!"%(player.name, other.name))
                    elif code == player.ATTACK_CRITICAL:
                        if player.equipped_a_weapon():
                            await bot.say("%s BEATS %s with %s %s!"%(player.name, other.name, player.equipped_item.indef_article(), player.equipped_item.name()))
                        else:
                            await bot.say("%s punches %s IN THE FACE!"%(player.name, other.name))
                    elif code == player.ATTACK_LETHAL:
                        if player.equipped_a_weapon():
                            await bot.say("%s deals the final blow to %s with the %s!"%(player.name, other.name, player.equipped_item.name()))
                        else:
                            await bot.say("%s delivers a deadly blow to %s's nose!"%(player.name, other.name))
                        await other.die(player)
                    if not code == player.ATTACK_COOLDOWN:
                        if player.move_cooldown or other.move_cooldown:
                            player.attack_cooldown = True
                            other.attack_cooldown = True
                            await asyncio.sleep(random.randint(1, 3))
                            player.attack_cooldown = False
                            other.attack_cooldown = False
                        else:
                            player.attack_cooldown = True
                            other.attack_cooldown = True
                            player.move_cooldown = True
                            other.move_cooldown = True
                            await asyncio.sleep(random.randint(1, 3))
                            player.attack_cooldown = False
                            other.attack_cooldown = False
                            player.move_cooldown = False
                            other.move_cooldown = False

@bot.command(description="Dumps the contents of a furniture to the floor.", pass_context=True)
async def dump(ctx, furniture : str):
    '''Dumps the contents of a furniture in your location.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            furniture = player.location.find_furniture(furniture)
            if player:
                if furniture:
                    if not player.is_observer and not player.is_dead:
                        furniture.dump()
                        await bot.say("%s dumps the %s's contents to the floor!"%(player.name, furniture.name))
                else:
                    await bot.say("There's no such furniture in this room.")

@bot.command(description="Stores an item from your inventory inside a furniture or a dead body in your location.", pass_context=True)
async def store(ctx, item : str, furniture):
    '''Allows you to store an item from your inventory inside a furniture or a dead body in your location.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                item = player.find_item(item)
                if item:
                    converter = commands.converter.MemberConverter(ctx, furniture)
                    member = None
                    try:
                        member = converter.convert()
                    except:
                        furniture = player.location.find_furniture(furniture)
                        if furniture:
                            if not player.is_observer and not player.is_dead:
                                furniture.add_item(item)
                                await bot.say("%s stores %s %s in the %s"%(player.name, item.indef_article(), item.name(), furniture.name))
                        else:
                            await bot.say("There's no such furniture in your location.")
                    else:
                        other = game.find_by_member(member)
                        if other:
                            if other.is_dead and (other.location == player.location):
                                other.add_item(item)
                                await bot.say("%s stores a %s inside %s's inventory" %(player.user.mention, item.name(), other.user.mention))
                            else:
                                await bot.say("You can't do that now!")
                        else:
                            await bot.say("You can't do that now!")
                else:
                    await bot.say("There's no such item in your inventory.")

@bot.command(description="Takes an item from a container or a dead body.", pass_context=True)
async def take_from(ctx, furniture, item : str):
    '''Allows you to take an item from a container.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            if player:
                converter = commands.converter.MemberConverter(ctx, furniture)
                member = None
                try:
                    member = converter.convert()
                except:
                    furniture = player.location.find_furniture(furniture)
                    if furniture:
                        item = furniture.find_item(item)
                        if item:
                            if not player.is_observer and not player.is_dead:
                                player.add_item(item)
                                await bot.say("%s picks up %s %s from the %s"%(player.name, item.indef_article(), item.name(), furniture.name))
                        else:
                            await bot.say("There's no such item in the %s."%(furniture.name))
                    else:
                        await bot.say("There's no such furniture in your location.")
                else:
                    other = game.find_by_user(member)
                    if other:
                        if other.is_dead and (other.location == player.location):
                            fitem = other.find_item(item)
                            if fitem:
                                player.add_item(fitem)
                                await bot.say("%s picks up %s %s from %s's inventory"%(player.name, item.indef_article(), item.name(), other.name))
                            else:
                                await bot.say("There's no such item in %s's inventory" %(other.name))
                        else:
                            await bot.say("You can't do that now!")
                    else:
                        await bot.say("You can't do that now!")

@bot.command(description="Examines a furniture or a dead body from your location.", pass_context=True)
async def look_inside(ctx, furniture):
    '''Returns information about the contents of a furniture in your location.'''
    if game:
        if game.game_state == game.STATE_GAME:
            player = game.find_by_user(ctx.message.author)
            converter = commands.converter.MemberConverter(ctx, furniture)
            member = None
            try:
                member = converter.convert()
            except:
                furniture = player.location.find_furniture(furniture)
                if player:
                    if furniture:
                        if not player.is_observer and not player.is_dead:
                            await bot.send_message(player.location.channel, "%s takes a look inside the %s..." %(player.name, furniture.name))
                            em = discord.Embed(title="%s's contents"%furniture.name, description=furniture.examine_contents(), colour=0x6699bb)
                            em.set_footer(text="Furniture")
                            await bot.send_message(player.user, embed=em)
                    else:
                        await bot.say("There's no such furniture in your location.")
            else:
                other = game.find_by_user(member)
                if other:
                    if other.is_dead and other.location == player.location:
                        await bot.send_message(player.location.channel, "%s takes a look inside %s's inventory..." %(player.name, other.name))
                        invcont = ""
                        for item in other.inventory:
                            invcont += "__%s__ - %s\n"%(item._name, item.examine())
                        em = discord.Embed(title="%s's inventory"%other.name, description=invcont, colour=0x6699bb)
                        em.set_footer(text="Dead body")
                        await bot.send_message(player.user, embed=em)
                    else:
                        await bot.say("You can't do that now!")
                else:
                    await bot.say("You can't do that now!")

def cleanup_game():
    global game
    game = None

if __name__ == "__main__":
    bot.run(token)
