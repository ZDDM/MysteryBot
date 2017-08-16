import discord
import asyncio

class Game():

    # Game states.
    STATE_LOBBY = 0
    STATE_GAME = 1
    STATE_END = 2

    async def __init__(self, bot, server):
        self.bot = bot
        self.server = server

        self.game_state = self.STATE_LOBBY
        self.players = []
        self.observers = []
        self.locations = {"1" : Location(self, name="Dev Room 1", topic="It's"), "2" : Location(self, name="Dev Room 2", topic="The"), "3" : Location(self, name="Dev Room 3", topic="Nutshack")}

        self.player_role = await self.bot.create_role(self.server, name="Mystery Player")
        self.observer_role = await self.bot.create_role(self.serevr, name="Mystery Observer")

        everyone_perm = discord.ChannelPermissions(target=self.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        player_perm = discord.ChannelPermissions(target=self.player_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        observer_perm = discord.ChannelPermissions(target=self.game.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False))

        self.channel = await self.bot.create_channel(self.game.server, "mystery_lobby", everyone_perm, plyer_perm, observer_perm)

        await self.bot.edit_channel(self.channel, topic="Mystery game lobby.")
        await self.bot.send_message(self.channel, "Game will start in 45 seconds. (BUT ACTUALLY 15 FOR DEBUG HEEEHEEEHEEE)")
        await asyncio.sleep(15)
        await start()

    async def start(self):
        self.game_state = self.STATE_GAME
        await self.bot.send_message(self.channel, "The game has started! @everyone")
        await self.bot.edit_channel(self.channel, topic="Mystery game lobby. The game has already started!")
        await asyncio.sleep(5)
        await self.bot.edit_channel(self.channel, topic="Mystery game lobby. The game has already started! You can discuss it here.")
        await self.bot.edit_channel_permissions(self.channel, target=self.player_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        for player in players:
            locations.values()[0].player_enter(player)

    async def stop(self):
        await self.bot.delete_role(self.server, self.player_role)
        await self.bot.delete_role(self.server, self.observer_role)
        await self.bot.delete_channel(self.channel)
        for location in self.locations:
            await location.delete()

    async def add_player(self, user):
        if self.game_state == self.STATE_LOBBY:
            player = find_by_user(user)
            if not (player in players):
                self.players.append(Player(self, user))
                self.bot.add_roles(self.game.server.get_member(user.id), self.player_role)
                self.bot.send_message(self.channel, "%s joins the game!" % (user.name))

    async def remove_player(self, user):
        if self.game_state == self.STATE_LOBBY:
            player = find_by_user(user)
            if player:
                if not player.is_observer and player in players:
                    self.players.remove(player)
                    self.bot.remove_roles(player.member, self.player_role)
                    self.bot.send_message(self.channel, "%s leaves the game..." % (user.name))

    async def add_observer(self, user):
        player = find_by_user(user)
        if not player:
            self.observers.append(Player(self, user, True))
            self.bot.add_roles(self.game.server.get_member(user.id), self.observer_role)
            return True
        return False

    async def remove_observer(self, user):
        player = find_by_user(user)
        if player:
            if player.is_observer and player in observers:
                self.observers.remove(player)
                self.bot.remove_roles(player.member, self.observer_role)
                return True
        return False

    def find_by_user(user):
        for item in players:
            if item.user == user:
                return item
        for item in observers:
            if item.user == user:
                return item
        return False

class Player():
    async def __init__(self, game, user, is_observer=False):
        self.game = game
        self.user = user
        self.member = self.game.server.get_member(self.user.id)
        self.location = None
        self.is_observer = is_observer

class Location():
    async def __init__(self, game, name, topic=""):
        self.game = game
        self.name = name
        self.role = await self.game.bot.create_role(self.game.server, name="Location")

        self.players = []

        everyone_perm = discord.ChannelPermissions(target=self.game.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        role_perm = discord.ChannelPermissions(target=self.role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        observer_perm = discord.ChannelPermissions(target=self.game.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False))

        self.channel = await self.game.bot.create_channel(self.game.server, "mystery_%s"%self.name, everyone_perm, role_perm, observer_perm)
        await self.game.bot.edit_channel(self.channel, topic=topic)
        self.on_message = decorate(self.game.bot.event)

    async def player_enter(self, player):
        if player.is_observer:
            return False
        if not (player in players):
            await self.game.bot.add_roles(player.member, self.role)
            await self.game.bot.send_message(self.channel, "%s enters." %(player.user.name))
            if player.location:
                await player.location.player_leave(player)
            player.location = self
            players.append(player)
            return True

    async def player_leave(self, player):
        if player in players:
            await self.game.bot.remove_roles(player.member, self.role)
            await self.game.bot.send_message(self.channel, "%s leaves." %(player.user.name))
            if player.location == self:
                player.location = None
            players.remove(player)

    async def delete(self):
        await self.game.bot.delete_channel(self.channel)
        await self.game.bot.delete_role(self.game.server, self.role)

    def bot(self):
        return self.game.bot

    async def on_message(message):
        if message.channel == self.channel:
            await self.game.bot.process_commands(message)
            await asyncio.sleep(20)
            try:
                await self.game.bot.delete_message(message)
            except:
                pass
        else:
            await self.game.bot.process_commands(message)

if __name__ == "__main__":
    raise Exception("Execute main.py instead.")
