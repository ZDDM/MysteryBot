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

        self.player_role = await self.bot.create_role(self.server, name="Mystery Player")
        self.observer_role = await self.bot.create_role(self.serevr, name="Mystery Observer")

        everyone_perm = discord.ChannelPermissions(target=self.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        player_perm = discord.ChannelPermissions(target=self.player_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        observer_perm = discord.ChannelPermissions(target=self.game.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False))

        self.channel = await self.bot.create_channel(self.game.server, "mystery_lobby", everyone_perm, plyer_perm, observer_perm)

        self.locations = []

    async def start(self):
        self.game_state = self.STATE_GAME

        self.bot.send_message(self.channel, "The game has started!")

    async def stop(self):
        await self.bot.delete_role(self.server, self.player_role)
        await self.bot.delete_role(self.server, self.observer_role)
        for location in self.locations:
            location.delete()

    async def add_player(user):
        if self.game_state == self.STATE_LOBBY:
            self.players.append(user)
            return

    async def remove_player(user):
        if self.game_state == self.STATE_LOBBY:
            self.players.remove(user)
            return

class Location():
    async def __init__(self, game, name):
        self.game = game
        self.name = name
        self.role = await self.game.bot.create_role(self.game.server, name="Location")

        everyone_perm = discord.ChannelPermissions(target=self.game.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        role_perm = discord.ChannelPermissions(target=self.role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        observer_perm = discord.ChannelPermissions(target=self.game.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False))

        self.channel = await self.game.bot.create_channel(self.game.server, "mystery_%s"%self.name, everyone_perm, role_perm, observer_perm)

    async def player_enter(user):
        if not self.role in self.game.server.get_member(user.id).roles:
            self.game.bot.add_roles(self.game.server.get_member(user.id), self.role)
            self.game.bot.send_message(self.channel, "%s enters." %(user.name))

    async def player_leave(user):
        if self.role in self.game.server.get_member(user.id).roles:
            self.game.bot.add_roles(self.game.server.get_member(user.id), self.role)
            self.game.bot.send_message(self.channel, "%s leaves." %(user.name))

    async def delete(self):
        await self.game.bot.delete_channel(self.channel)
        await self.game.bot.delete_role(self.game.server, self.role)

if __name__ == "__main__":
    raise Exception("Execute main.py instead.")
