import discord
import asyncio
import random
from copy import deepcopy as copy

class Game():

    # Game states.
    STATE_PREPARE = -1
    STATE_LOBBY = 0
    STATE_GAME = 1
    STATE_END = 2

    def __init__(self, bot, server, cleanup_function=None):
        self.bot = bot
        self.server = server

        self.cleanup_function = cleanup_function

        self.game_state = self.STATE_PREPARE
        self.players = []
        self.observers = []
        self.murderers = []

        self.weapon_database = {"book" : Weapon(name="book", description="Bust someone's head with it! Still better than your fists", robustness=7),
                                "branch" : Weapon(name="branch", description="A branch from a tree. Better than using your fists!", robustness=8),
                                "knife" : Weapon(name="knife", description="A kitchen knife", robustness=10),
                                "hatchet" : Weapon(name="Hatchet", description="A small axe.", robustness=13),
                                "baseball bat" : Weapon(name="baseball bat", description="SMAAAAASH! Homerun!", robustness=15),
                                "billhook" : Weapon(name="billhook", description="Traditional cutting tool", robustness=20),
                                "toolbox" : Weapon(name="toolbox", description="Originally used for storing tools, now used for busting heads!", robustness=25),
                                "katana" : Weapon(name="katana", description="Traditional japanese sword", robustness=30),
                                "sword" : Weapon(name="sword", description="A beautiful long sword", robustness=30),
                                "winchester" : Weapon(name="winchester 1894", description="A ranged rifle for \"self-defense\"...", robustness=50)}

        self.channel_prefix = "mystery_"

        self.player_role = None
        self.observer_role = None
        self.dead_role = None

        self.locations = self.map_rokkenjima()

        self.channel = None

    def map_devtest(self):

        self.channel_prefix = "dev_"

        chest = Furniture(name="chest", description="A chest forged from zeros and ones.", \
                          contents=[Item(name="Useless junk", description="Totally useless..."), \
                          Weapon(name="Toolbox", description="ROBUST!", robustness=30)], \
                          random_content=[(Weapon(name="Legendary bike horn", description="Used by a clown living inside a space station... Cool, eh?"),1/3)])

        devroom1 = Location(self, name="devroom1", topic="OH NO, A DEV ROOM", items=[Item(name="Tears", description="Solidified tears from a coder.", is_bloody=True)], furniture=[chest])
        devroom2 = Location(self, name="devroom2", topic="Oh hey, it's a dev room.", items=[Weapon(name="Billhook", description="Popularized by teenage girls.", robustness=20)])

        devroom1.add_adjacent_location(devroom2)

        locations = [devroom1, devroom2]

        return locations

    def map_rokkenjima(self):

        self.channel_prefix = "rokkenjima_"

        closet = Furniture(name="closet", description="Full of clothes", random_content=[(self.weapon_database["toolbox"],1/4)])
        locker = Furniture(name="locker", description="A person could fit in, maybe...", random_content=[(copy(self.weapon_database["baseball bat"]), 1/3)])
        shelf = Furniture(name="shelf", description="Just a shelf", random_content=[(copy(self.weapon_database["book"]),1/3)])
        crate = Furniture(name="crate", description="It's a crate! Oh no!", random_content=[(copy(self.weapon_database["katana"]), 1/6)])

        pier = Location(self, name="pier", topic="A small pier where boats come by", furniture=[copy(crate)])
        rose_garden = Location(self, name="rose_garden", topic="A beautiful rose garden")
        tool_shed = Location(self, name="tool_shed", topic="A shed for storing various gardening tools", furniture=[copy(locker), copy(shelf)], items=[copy(self.weapon_database["hatchet"])], random_items=[(copy(self.weapon_database["billhook"]), 1/2)])
        forest1 = Location(self, name="forest1", topic="Full of trees...", random_items=[(copy(self.weapon_database["branch"]),1/2), (copy(self.weapon_database["branch"]),1/2)])
        forest2 = Location(self, name="forest2", topic="Like, REALLY full of trees...", random_items=[(copy(self.weapon_database["branch"]),1/2), (copy(self.weapon_database["branch"]),1/2)])
        kuwadorian = Location(self, name="kuwadorian", topic="A beautiful mansion inside the forest", furniture=[copy(closet), copy(crate)], random_items=[(copy(self.weapon_database["katana"]), 1/4), (copy(self.weapon_database["sword"]), 1/4)])
        guest_house_1f = Location(self, name="guest_house_1f", topic="First floor of the guest house")
        guest_house_parlor = Location(self, name="parlor", topic="A rustical chamber with a bar for the guests", furniture=[copy(closet)])
        guest_house_archive = Location(self, name="archive", topic="Holds a small but a wide collection of books", furniture=[copy(closet)], items=[copy(self.weapon_database["book"]), copy(self.weapon_database["book"])])
        guest_house_2f = Location(self, name="guest_house_2f", topic="Second floor of the guest house")
        guest_house_bedroom = Location(self, name="guest_house_bedroom", topic="An elegant guest room with a few beds", furniture=[copy(shelf)], items=[copy(self.weapon_database["baseball bat"])])
        mansion_entrance = Location(self, name="mansion_entrance", topic="I wonder how the mansion looks on the inside...")
        mansion_1f = Location(self, name="mansion_1f", topic="First floor of the guest house. The portrait of a beautiful witch can be seen on the wall...")
        mansion_dining_room = Location(self, name="dining_room", topic="A big but elegant dining room")
        mansion_kitchen = Location(self, name="kitchen", topic="It looks like the kitchen from some restaurant...", furniture=[copy(closet), copy(locker)], items=[copy(self.weapon_database["knife"])])
        mansion_2f = Location(self, name="mansion_2f", topic="Second floor of the mansion", items=[copy(self.weapon_database["book"])])
        mansion_bedroom = Location(self, name="mansion_bedroom", topic="A luxurious bedroom with a large bed", furniture=[copy(closet)])
        mansion_bathroom = Location(self, name="mansion_bathroom", topic="It's just a bathroom. You can't fit through the sink, though!", furniture=[copy(locker)])
        mansion_3f = Location(self, name="mansion_3f", topic="Third and last floor of the mansion")
        mansion_study = Location(self, name="mansion_study", topic="An apartment-sized study", furniture=[copy(closet), copy(shelf), copy(locker)], random_items=[(copy(self.weapon_database["winchester"]), 1/3)])
        mansion_study_kitchen = Location(self, name="mansion_study_kitchen", topic="An ordinary kitchen", items=[copy(self.weapon_database["knife"])])
        mansion_study_bathroom = Location(self, name="mansion_study_bathroom", topic="Just a bathroom...")

        pier.add_adjacent_location(rose_garden)
        rose_garden.add_adjacent_location(tool_shed)
        rose_garden.add_adjacent_location(forest1)
        tool_shed.add_adjacent_location(forest1)
        rose_garden.add_adjacent_location(guest_house_1f)
        rose_garden.add_adjacent_location(mansion_entrance)
        forest1.add_adjacent_location(forest2)
        forest2.add_adjacent_location(kuwadorian)
        kuwadorian.add_adjacent_location(pier, one_way=True)
        guest_house_1f.add_adjacent_location(guest_house_parlor)
        guest_house_1f.add_adjacent_location(guest_house_archive)
        guest_house_1f.add_adjacent_location(guest_house_2f)
        guest_house_2f.add_adjacent_location(guest_house_bedroom)
        mansion_entrance.add_adjacent_location(mansion_1f)
        mansion_1f.add_adjacent_location(mansion_kitchen)
        mansion_1f.add_adjacent_location(mansion_dining_room)
        mansion_1f.add_adjacent_location(mansion_2f)
        mansion_2f.add_adjacent_location(mansion_bedroom)
        mansion_bedroom.add_adjacent_location(mansion_bathroom)
        mansion_2f.add_adjacent_location(mansion_3f)
        mansion_3f.add_adjacent_location(mansion_study)
        mansion_study.add_adjacent_location(mansion_study_kitchen)
        mansion_study.add_adjacent_location(mansion_study_bathroom)
        mansion_study_kitchen.add_adjacent_location(mansion_study_bathroom)

        locations = [pier, rose_garden, tool_shed, forest1, forest2, kuwadorian, guest_house_1f, guest_house_parlor,\
                     guest_house_archive, guest_house_2f, guest_house_bedroom, mansion_entrance, mansion_1f, mansion_2f,\
                     mansion_bedroom, mansion_bathroom, mansion_3f, mansion_study, mansion_study_kitchen, mansion_study_bathroom]

        return locations

    async def prepare(self):
        self.player_role = await self.bot.create_role(self.server, name="Mystery Player")
        self.observer_role = await self.bot.create_role(self.server, name="Mystery Observer")
        self.dead_role = await self.bot.create_role(self.server, name="Location")

        everyone_perm = discord.ChannelPermissions(target=self.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        player_perm = discord.ChannelPermissions(target=self.player_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        observer_perm = discord.ChannelPermissions(target=self.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False))
        dead_perm = discord.ChannelPermissions(target=self.dead_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))

        self.channel = await self.bot.create_channel(self.server, "%slobby"%(self.channel_prefix), everyone_perm, player_perm, observer_perm, dead_perm)

        await self.bot.edit_channel(self.channel, topic="Mystery game lobby.")

        self.game_state = self.STATE_LOBBY

        for location in self.locations:
            await location.start()

    async def start(self, timer):
        await self.bot.send_message(self.channel, "The game will start in %s seconds."%(timer))
        await asyncio.sleep(timer)
        self.game_state = self.STATE_GAME
        await self.bot.send_message(self.channel, "The game has started! @everyone")
        await self.bot.edit_channel(self.channel, topic="Mystery game lobby. The game has already started!")
        await asyncio.sleep(2)
        await self.bot.edit_channel(self.channel, topic="Mystery game lobby. The game has already started! You can discuss it here.")
        await self.bot.edit_channel_permissions(self.channel, target=self.player_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))
        await self.bot.edit_channel_permissions(self.channel, target=self.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True))
        # murderer_number = int(len(self.players) / 3)
        murderer_number = 1 # Only one for debug purposes
        murderer_list = ""
        random.seed()
        sample = random.sample(range(len(self.players)), murderer_number)
        for i in sample:
            self.murderers.append(self.players[i])
            self.players[i].role = Player.ROLE_MURDERER
            murderer_list += self.players[i].user.mention + "\n"
            await self.bot.send_message(self.players[i].user, "You're the **MURDERER**. Your goal is to kill all innocents without being caught.")

        em = discord.Embed(title="Murderers", description=murderer_list, colour=0xff5555)
        em.set_footer(text="Know your \"friends\"...")

        for i in self.murderers:
            await self.bot.send_message(i.user, embed=em)

        for player in self.players:
            random.seed()
            await self.locations[random.randint(0, len(self.locations) - 1)].player_enter(player)

    async def stop(self):
        await self.bot.delete_role(self.server, self.player_role)
        await self.bot.delete_role(self.server, self.observer_role)
        await self.bot.delete_role(self.server, self.dead_role)
        await self.bot.delete_channel(self.channel)
        for location in self.locations:
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

    def find_location(self, loc):
        for location in self.locations:
            if location.name == loc:
                return location
        return False

class Player():

    ATTACK_FAIL = 0
    ATTACK_COOLDOWN = 1
    ATTACK_SUCCESS = 2
    ATTACK_CRITICAL = 3
    ATTACK_LETHAL = 4

    ROLE_NONE = 0
    ROLE_MURDERER = 1

    def __init__(self, game, user, is_observer=False):
        self.game = game
        self.user = user
        self.name = self.user.name
        self.role = self.ROLE_NONE
        self.member = self.game.server.get_member(self.user.id)
        if self.member.nick:
            self.name = self.member.nick
        self.location = None
        self.is_observer = is_observer
        self.is_bloody = False
        self.is_dead = False
        self.equipped_item = None
        self.inventory = []
        self.health = 100

        self.killed_by = None

        self.move_cooldown = False
        self.attack_cooldown = False

    def equipped_a_weapon(self):
        return isinstance(self.equipped_item, Weapon)

    def equip(self, item):
        if item in self.inventory:
            if item != self.equipped_item:
                self.equipped_item = item
                return True
        return False

    async def die(self, who_killed_me=None):
        self.killed_by = who_killed_me
        self.is_dead = True
        await self.game.bot.send_message(self.location.channel, "**%s seizes up and falls limp, their eyes dead and lifeless...**"%(self.name))
        await self.game.bot.remove_roles(self.member, self.location.role)
        await asyncio.sleep(0.25)
        await self.game.bot.add_roles(self.member, self.game.dead_role)

    async def attack(self, player):
        if not self.attack_cooldown:
            assert isinstance(player, Player)
            if player == self:
                pass
            else:
                robustness = 5
                if self.equipped_a_weapon():
                    robustness += self.equipped_item.robustness
                random.seed()
                if random.randint(0, 100) <= 30:
                    return self.ATTACK_FAIL
                else:
                    random.seed()
                    if random.randint(0, 100) <= 15:
                        robustness *= 1.5
                        await self._attack(player, robustness)
                        if player.health:
                            return self.ATTACK_CRITICAL
                        else:
                            return self.ATTACK_LETHAL
                    else:
                        await self._attack(player, robustness)
                        if player.health:
                            return self.ATTACK_SUCCESS
                        else:
                            return self.ATTACK_LETHAL
        return self.ATTACK_COOLDOWN

    async def _attack(self, player, robustness):
        damage = random.randint(10, 15) + robustness
        player.health -= damage
        if random.randint(0, 1):
            self.is_bloody = True
        if random.randint(0, 1):
            player.is_bloody = True
        if self.equipped_a_weapon():
            self.equipped_item.on_attack(player)
            if random.randint(0, 1):
                self.equipped_item.is_bloody = True
        if player.health <= 0:
            player.health = 0
            player.is_bloody = True

    def add_item(self, item):
        if item not in self.inventory:
            if isinstance(item.parent, Player) or isinstance(item.parent, Location):
                item.parent.remove_item(item)
            self.inventory.append(item)
            item.parent = self

    def remove_item(self, item):
        if item in self.inventory:
            if item.parent:
                item.parent = None
            self.inventory.remove(item)
            if self.equipped_item == item:
                self.equipped_item = None

    def find_item(self, item):
        for mitem in self.inventory:
            if mitem._name.lower() == item.lower():
                return mitem
        return False

    def examine(self):
        '''Returns a single-line string.'''
        examined = ""
        if not self.is_dead:
            if self.health >= 100:
                examined = "%s seems to be doing alright.\n"%self.name
            elif self.health > 90:
                examined = "%s seems to be slightly hurt.\n"%self.name
            elif self.health > 70:
                examined = "%s seems to be hurt.\n"%self.name
            elif self.health > 50:
                examined = "%s seems to be injured.\n"%self.name
            elif self.health > 30:
                examined = "%s seems to be quite injured...\n"%self.name
            elif self.health > 10:
                examined = "%s seems like they need urgent medical care!\n"%self.name
            elif self.health >= 1:
                examined = "%s seems like they're about to die!\n"%self.name
            else:
                examined = "%s is already...\n"
        else:
            examined = "%s seems to be dead!\n"%self.name
        if self.is_bloody:
            examined += "%s's clothes are **blood-stained**!\n"%self.name
        if self.equipped_item:
            examined += "%s is holding %s %s. \n"%(self.name, self.equipped_item.indef_article(), self.equipped_item.name())
        return examined

class Item():
    def __init__(self, name="Unknown", description="Unknown item.", is_bloody=False):
        self._name = name
        self.description = description
        self.is_bloody = is_bloody
        self.parent = None

    def name(self):
        if self.is_bloody:
            return "**blood-stained** __%s__"%(self._name)
        else:
            return "__%s__"%(self._name)

    def pickup(self, player):
        if isinstance(player, Player):
            player.add_item(self)

    def drop(self):
        if isinstance(self.parent, Player):
            self.parent.location.add_item(self)

    def indef_article(self):
        if self._name[0] in ("a", "e", "i", "o", "u") and not self.is_bloody:
            return "an"
        else:
            return "a"

    def examine(self):
        if isinstance(self.parent, Player):
            return "This is %s %s! "%(self.indef_article(), self.name().lower()) + self.description
        elif isinstance(self.parent, Location):
            return "There is %s %s on the ground! "%(self.indef_article(), self.name().lower())
        elif isinstance(self.parent, Furniture):
            return "There is %s %s inside the %s! "%(self.indef_article(), self.name().lower(), self.parent.name.lower())

class Usable(Item):
    async def use(self):
        pass

class Weapon(Usable):
    def __init__(self, name="Unknown", description="Unknown weapon.", is_bloody=False, robustness=15):
        super(Weapon, self).__init__(name, description, is_bloody)
        self.robustness = robustness

    async def on_attack(self, other):
        pass

class Furniture():
    def __init__(self, name="", description="", contents=[], random_content=[]):
        '''contents uses object instances.
           random_content uses a tuple including an object instance and a chance (from 0.0 to 1.0)'''
        self.parent = None
        self.contents = []
        self.name = name
        for item, chance in random_content:
            random.seed()
            if random.random() < chance:
                self.add_item(item)
        for item in contents:
            self.add_item(item)

    def examine(self):
        if self.name[0] in ("a", "e", "i", "o", "u"):
            return "There is an %s! "%(self.name.lower())
        else:
            return "There is a %s! "%(self.name.lower())

    def dump(self):
        for item in self.contents:
            self.parent.add_item(item)

    def examine_contents(self):
        contentstr = ""
        for content in self.contents:
            contentstr += "%s \n"%(content.examine())
        return contentstr

    def add_item(self, item):
        if item not in self.contents:
            if isinstance(item.parent, Player) or isinstance(item.parent, Location):
                item.parent.remove_item(item)
            self.contents.append(item)
            item.parent = self

    def remove_item(self, item):
        if item in self.contents:
            if item.parent:
                item.parent = None

    def find_item(self, item):
        for mitem in self.contents:
            if mitem._name.lower() == item.lower():
                return mitem
        return False

class Location():
    def __init__(self, game, name, topic="", description="", items=[], random_items=[], furniture=[], random_furniture=[], cooldown=3):
        '''items uses item instances.
           random_content uses a tuple including an item instance and a chance (from 0.0 to 1.0)
           furniture uses furniture instances
           random_furniture uses a tuple including a furniture instance and a chance (from 0.0 to 1.0)'''
        self.game = game
        self.name = name.replace(" ", "_")
        self.role = None
        self.topic = topic
        self.cooldown = cooldown

        self.description = description

        self.players = [] # Players in this location.
        self.items = [] # Items in this location.
        self.furniture = [] # Furniture in this location

        self.adjacent_locations = []

        self.channel = None

        for item, chance in random_items:
            random.seed()
            if random.random() < chance:
                self.add_item(item)

        for item in items:
            self.add_item(item)

        for furniture, chance in random_furniture:
            random.seed()
            if random.random() < chance:
                self.add_furniture(furniture)

        for furniture in furniture:
            self.add_furniture(furniture)

    async def start(self):
        self.role = await self.game.bot.create_role(self.game.server, name="Location")

        everyone_perm = discord.ChannelPermissions(target=self.game.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False))
        role_perm = discord.ChannelPermissions(target=self.role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=False))
        observer_perm = discord.ChannelPermissions(target=self.game.observer_role, overwrite=discord.PermissionOverwrite(read_messages=True, send_messages=False, read_message_history=True))
        dead_perm = discord.ChannelPermissions(target=self.game.dead_role, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False))

        self.channel = await self.game.bot.create_channel(self.game.server, "%s%s"%(self.game.channel_prefix, self.name), everyone_perm, role_perm, observer_perm, dead_perm)
        await self.game.bot.edit_channel(self.channel, topic=self.topic)

    def add_adjacent_location(self, location, one_way=False):
        assert isinstance(location, Location)
        if location not in self.adjacent_locations:
            self.adjacent_locations.append(location)
            if self not in location.adjacent_locations and not one_way:
                location.adjacent_locations.append(self)

    def add_item(self, item):
        if item not in self.items:
            if isinstance(item.parent, Player) or isinstance(item.parent, Location) or isinstance(item.parent, Furniture):
                item.parent.remove_item(item)
            self.items.append(item)
            item.parent = self

    def remove_item(self, item):
        if item in self.items:
            if item.parent:
                item.parent = None
            self.items.remove(item)

    def find_item(self, item):
        for mitem in self.items:
            if mitem._name.lower() == item.lower():
                return mitem
        return False

    def add_furniture(self, furniture):
        if furniture not in self.furniture:
            if isinstance(furniture.parent, Location):
                furniture.parent.remove_furniture(item)
            self.furniture.append(furniture)
            furniture.parent = self

    def remove_furniture(self, furniture):
        if furniture in self.furniture:
            if furniture.parent:
                furniture.parent = None
                self.furniture.remove(furniture)

    def find_furniture(self, furniture):
        for mfurniture in self.furniture:
            if mfurniture.name == furniture:
                return mfurniture
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
        examined = {"players" : "", "furniture" : "", "items" : "", "location" : self.description}
        for player in self.players:
            if player.is_dead:
                examined["players"] += "%s lies on the floor!\n%s"%(player.name, player.examine())
            else:
                examined["players"] += "%s is in here.\n%s"%(player.name, player.examine())

        for furniture in self.furniture:
            examined["furniture"] += furniture.examine()

        for item in self.items:
            examined["items"] += item.examine()

        return examined

if __name__ == "__main__":
    raise Exception("Execute main.py instead.")
