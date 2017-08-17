import discord
import asyncio

class Game():

    # Game states.
    STATE_PREPARE = -1
    STATE_LOBBY = 0
    STATE_GAME = 1
    STATE_END = 2

    def __init__(self, bot, server):
        self.bot = bot
        self.server = server

        self.game_state = self.STATE_PREPARE
        self.players = []
        self.observers = []

        self.player_role = None
        self.observer_role = None

        self.locations = {"1" : Location(self, name="Dev Room 1", topic="It's", description="A dev room... Spooky!"),
                          "2" : Location(self, name="Dev Room 2", topic="The", description="This room, ah yes... This room. It makes you feel relaxed"),
                          "3" : Location(self, name="Dev Room 3", topic="Nutshack", description="This room is quite boring... There's nothing special here.")}

        self.channel = None

    async def prepare(self):
        self.player_role = await self.bot.create_role(self.server, name="Mystery Player")
        self.observer_role = await self.bot.create_role(self.server, name="Mystery Observer")

        everyone_perm = discord.ChannelPermissions(target=self.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        player_perm = discord.ChannelPermissions(target=self.player_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        observer_perm = discord.ChannelPermissions(target=self.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False))

        self.channel = await self.bot.create_channel(self.server, "mystery_lobby", everyone_perm, player_perm, observer_perm)

        await self.bot.edit_channel(self.channel, topic="Mystery game lobby.")

        self.game_state = self.STATE_LOBBY

        for location in self.locations.values():
            await location.start()

    async def start(self):
        await self.bot.send_message(self.channel, "Game will start in 45 seconds. (BUT ACTUALLY 15 FOR DEBUG HEEEHEEEHEEE)")
        await asyncio.sleep(15)
        self.game_state = self.STATE_GAME
        await self.bot.send_message(self.channel, "The game has started! @everyone")
        await self.bot.edit_channel(self.channel, topic="Mystery game lobby. The game has already started!")
        await asyncio.sleep(2)
        await self.bot.edit_channel(self.channel, topic="Mystery game lobby. The game has already started! You can discuss it here.")
        await self.bot.edit_channel_permissions(self.channel, target=self.player_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        await self.bot.edit_channel_permissions(self.channel, target=self.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        for player in self.players:
            await list(self.locations.values())[0].player_enter(player)

    async def stop(self):
        await self.bot.delete_role(self.server, self.player_role)
        await self.bot.delete_role(self.server, self.observer_role)
        await self.bot.delete_channel(self.channel)
        for location in list(self.locations.values()):
            await location.delete()

    async def add_player(self, user):
        if self.game_state == self.STATE_LOBBY:
            player = self.find_by_user(user)
            if not (player in self.players):
                self.players.append(Player(self, user))
                await self.bot.add_roles(self.server.get_member(user.id), self.player_role)
                await self.bot.send_message(self.channel, "%s joins the game!" % (user.mention))
                return True
        return False

    async def remove_player(self, user):
        if self.game_state == self.STATE_LOBBY:
            player = self.find_by_user(user)
            if player:
                if not player.is_observer and player in self.players:
                    self.players.remove(player)
                    await self.bot.remove_roles(player.member, self.player_role)
                    await self.bot.send_message(self.channel, "%s leaves the game..." % (user.mention))
                    return True
        return False

    async def add_observer(self, user):
        if self.game_state != self.STATE_PREPARE:
            player = self.find_by_user(user)
            if not player:
                self.observers.append(Player(self, user, True))
                await self.bot.add_roles(self.server.get_member(user.id), self.observer_role)
                return True
        return False

    async def remove_observer(self, user):
        player = self.find_by_user(user)
        if player:
            if player.is_observer and player in self.observers:
                self.observers.remove(player)
                await self.bot.remove_roles(player.member, self.observer_role)
                return True
        return False

    def find_by_user(self, user):
        for item in self.players:
            if item.user == user:
                return item
        for item in self.observers:
            if item.user == user:
                return item
        return False

    def find_by_member(self, member):
        for item in self.players:
            if item.member == member:
                return item
        for item in self.observers:
            if item.member == member:
                return item
        return False

class Player():
    def __init__(self, game, user, is_observer=False):
        self.game = game
        self.user = user
        self.name = self.user.name
        self.member = self.game.server.get_member(self.user.id)
        if self.member.nick:
            self.name = self.member.nick
        self.location = None
        self.is_observer = is_observer
        self.is_bloody = False
        self.equipped_item = None
        self.inventory = []

    def add_item(self, item):
        if item not in self.items:
            if isinstance(item.parent, Player) or isinstance(item.parent, Location):
                item.parent.remove_item(item)
            self.inventory += item
            item.parent = self

    def remove_item(self, item):
        if item in self.items:
            if item.parent:
                item.parent = None

    def find_item(self, item):
        for mitem in self.inventory:
            if mitem.name == item:
                return mitem
        return False

    def examine(self):
        '''Returns a single-line string.'''
        examined = "%s doesn't seem injured.\n"%self.name
        if self.is_bloody:
            examined += " %s's clothes are **blood-stained**!\n"%self.name
        return examined

class Item():
    def __init__(self, name="Unknown", description="Unknown item."):
        self._name = name
        self.description = description
        self.is_bloody = False
        self.parent = None

    def name(self):
        if is_bloody:
            return "**blood-stained** __%s__"%(self._name)
        else:
            return "__%s__"%(self._name)

    def pickup(self, player):
        if isinstance(player, Player):
            player.add_item(self)

    def drop(self):
        if isinstance(self.parent, Player):
            self.parent.location.add_item(self)

    def examine(self):
        if name[0] in ("a", "e", "i", "o", "u") and not is_bloody:
            if isinstance(self.parent, Player):
                return "This is an %s! "%(self.name().lower()) + self.description
            else:
                return "There is an %s! "%(self.name().lower())
        else:
            if isinstance(self.parent, Player):
                return "This is a %s! "%(self.name().lower()) + self.description
            else:
                return "There is a %s! "%(self.name().lower())

class Usable(Item):
    async def use(self):
        pass

class Weapon(Usable):
    def __init__(self):
        pass

class Location():
    def __init__(self, game, name, topic="", description=""):
        self.game = game
        self.name = name.replace(" ", "_")
        self.role = None
        self.topic = topic

        self.description = description

        self.players = [] # Players in this location.
        self.items = [] # Items in this location.

        self.channel = None
        # self.on_message = self.game.bot.event(self.on_message)

    async def start(self):
        self.role = await self.game.bot.create_role(self.game.server, name="Location")

        everyone_perm = discord.ChannelPermissions(target=self.game.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False))
        role_perm = discord.ChannelPermissions(target=self.role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=False))
        observer_perm = discord.ChannelPermissions(target=self.game.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False, read_message_history=True))

        self.channel = await self.game.bot.create_channel(self.game.server, "mystery_%s"%self.name, everyone_perm, role_perm, observer_perm)
        await self.game.bot.edit_channel(self.channel, topic=self.topic)

    def add_item(self, item):
        if item not in self.items:
            if isinstance(item.parent, Player) or isinstance(item.parent, Location):
                item.parent.remove_item(item)
            self.items += item
            item.parent = self

    def remove_item(self, item):
        if item in self.items:
            if item.parent:
                item.parent = None

    def find_item(self, item):
        for mitem in self.items:
            if mitem.name == item:
                return mitem
        return False

    async def player_enter(self, player):
        if player.is_observer:
            return False
        if not (player in self.players):
            await self.game.bot.add_roles(player.member, self.role)
            await self.game.bot.send_message(self.channel, "%s enters." %(player.user.mention))
            if player.location:
                await player.location.player_leave(player)
            player.location = self
            self.players.append(player)
            return True

    async def player_leave(self, player):
        if player in self.players:
            await self.game.bot.send_message(self.channel, "%s leaves." %(player.user.mention))
            await self.game.bot.remove_roles(player.member, self.role)
            if player.location == self:
                player.location = None
            self.players.remove(player)

    async def delete(self):
        await self.game.bot.delete_channel(self.channel)
        await self.game.bot.delete_role(self.game.server, self.role)

    def examine(self):
        examined = self.description + "\n"
        for player in self.players:
            examined += "%s is in the room. %s \n"%(player.name, player.examine())
        examined += "\n"
        for item in self.items:
            examined += ""
        return examined

    def bot(self):
        return self.game.bot

    # async def on_message(self, message):
    #     if message.channel == self.channel:
    #         await self.game.bot.process_commands(message)
    #         await asyncio.sleep(20)
    #         try:
    #             await self.game.bot.delete_message(message)
    #         except:
    #             pass
    #     else:
    #         await self.game.bot.process_commands(message)

if __name__ == "__main__":
    raise Exception("Execute main.py instead.")
