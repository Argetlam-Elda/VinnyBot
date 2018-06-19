import discord
import operator
import time
import random
from random import randint


async def games(message, client):
    server = message.guild
    members = server.members
    gamelist = []
    for member in members:
        if member.game is not None and not member.bot:
            gamelist.append(member.game.name)
    if not gamelist:  # if list is empty
        await message.channel.send(":x: No one appears to be playing anything... :thinking:")
        return
    # Creates dictionary where word is the game and definition is # of people playing
    countedgames = {i: gamelist.count(i) for i in gamelist}
    # Sorts dict by # of people playing
    sortedgames = sorted(countedgames.items(), key=operator.itemgetter(1))
    finalstring = "Games being played by members now: \n"
    for (game, players) in sortedgames:
        finalstring += game + ": " + str(players) + "\n"
    await message.channel.send(finalstring)


async def battle(message, client):
    # Get the people that are fighting & initial error finding
    mentioned = message.mentions
    if len(mentioned) > 2 or len(mentioned) is 0:
        await message.channel.send(":x:Please mention only 1 or 2 members:x:")
        return
    if len(mentioned) is 2:
        user1 = mentioned[0]
        user2 = mentioned[1]
    else:
        user1 = message.author
        user2 = mentioned[0]
    if user1 is user2:  # If user mentions themself or the same person twice
        await message.channel.send("You'll have to fight your inner demons on your own...")
        return

    # Solve if user has a server nickname or not
    user1_name = user1.nick
    if user1_name is None:
        user1_name = user1.name
    user2_name = user2.nick
    if user2_name is None:
        user2_name = user2.name
    if user1_name == user2_name:  # If users have the same nickname on the server
        user1_name += "(1)"
        user2_name += "(2)"
    await message.channel.send(user1_name + " and " + user2_name + " are battling!")

    # players are given weapons randomly
    weapons = ["dagger :dagger:", "bow :bow_and_arrow:", "sword :crossed_swords:", "wits :thinking:"]
    user1_weapon = weapons[randint(0, 3)]
    user2_weapon = weapons[randint(0, 3)]
    await message.channel.send(user1_name + " wields their " + user1_weapon + ", while " + user2_name +
                               " takes in their trusty " + user2_weapon + ".")

    # initialize health and starting attacker (random)
    attacker_health = 100
    defender_health = 100
    if randint(0, 1) is 0:
        attacker = user1
        attacker_name = user1_name
        defender = user2
        defender_name = user2_name
    else:
        attacker = user2
        attacker_name = user2_name
        defender = user1
        defender_name = user1_name

    # Someday the great spaghetti code monster will be summoned and reap all our lives, And I will be a bit at fault.
    flipthis = False  # To keep users' HP on the same side each time

    # battle loop
    while attacker_health > 0 and defender_health > 0:
        time.sleep(2)  # Damn humans need time to read
        roll = randint(1, 20)
        battlerecord = ""
        if roll is 1:
            attacker_health -= 10
            if attacker_health < 0:
                attacker_health = 0
            battlerecord += "Critical fail! " + attacker_name + " hurts themself for 10!"

        elif roll is 20:
            defender_health -= 40
            if defender_health < 0:
                defender_health = 0
            battlerecord += "Critical hit! " + attacker_name + " hits " + defender_name + " for 40!"

        else:
            hit = roll + 10
            defender_health -= hit
            if defender_health < 0:
                defender_health = 0
            battlerecord += attacker_name + " strikes " + defender_name + " for " + str(hit)

        if flipthis:
            battlerecord += "\n" + defender_name + ": " + str(defender_health) + " | " + \
                            attacker_name + ": " + str(attacker_health)
        else:
            battlerecord += "\n" + attacker_name + ": " + str(attacker_health) + " | " + \
                            defender_name + ": " + str(defender_health)
        await message.channel.send(battlerecord)

        # Switch attacker <-> defender
        temp = attacker
        attacker = defender
        defender = temp

        temp = attacker_name
        attacker_name = defender_name
        defender_name = temp

        # Switch health to match player
        temp = attacker_health
        attacker_health = defender_health
        defender_health = temp

        flipthis = not flipthis

    # Announce winner
    if defender_health < 1:
        loser_name = defender_name
        winner_name = attacker_name
    else:
        loser_name = attacker_name
        winner_name = defender_name
    await message.channel.send(winner_name + " defeated " + loser_name + "!")


async def battle_royale(message, client, verbose):
    # get candidates from mention/role/guild list
    candidates = await get_player_list(message)
    # get fighters from candidates
    fighters = await populate_roster(candidates)

    # Weed out any fringe cases
    if len(fighters) < 3:
        await message.channel.send(":x:It's not a battle royal if you don't have at least 3 fighters:x:")
        return

    # TODO - alphabatize fighters by name
    """
    temp_fighters = fighters
    fighters = {}
    keys = {}
    for fighter in temp_fighters:
        keys[temp_fighters[fighter]["name"]] = fighter
    print(len(keys))
    for key in sorted(keys):
        print("Key is " + key)
        print("Keys[key] is " + keys[key])
        time.sleep(0.1)
        fighters[keys[key]] = temp_fighters.pop(keys[key])
    """
    # Enact the battle of our lifetimes
    await enact_battle(message, fighters, verbose)

    # Print victory message, unless the players are feeling suicidal
    if len(fighters) is 0:
        await message.channel.send("```\nLoser, loser, chicken loser.\n```")
    else:
        victor = fighters[random.choice(list(fighters))]
        weapon = victor["weapon"]["name"]
        armor = victor["armor"]["name"]
        await message.channel.send("```\nBehold your champion, {} of {}, weilding their mighty {} and wearing their {}!\n```".format(victor["name"], message.guild.name, weapon, armor))


async def equip_combatant(fighters, index):
    fighters[index]["weapon"] = {}
    fighters[index]["armor"] = {}

    # Roll for weapon
    luck = randint(0, 10000)
    if 0 <= luck <= 10:
        fighters[index]["weapon"]["name"] = "oven mitts"
        fighters[index]["weapon"]["damage"] = -5
        fighters[index]["weapon"]["hit"] = "pats down"
        fighters[index]["weapon"]["crit"] = "mitts to the mouth"
        fighters[index]["weapon"]["self"] = "struggles with"
        fighters[index]["weapon"]["suicide"] = "chokes"
        fighters[index]["weapon"]["crip"] = -5
    elif 10 < luck <= 50:
        fighters[index]["weapon"]["name"] = "bb gun"
        fighters[index]["weapon"]["damage"] = -1
        fighters[index]["weapon"]["hit"] = "\"shoots\""
        fighters[index]["weapon"]["crit"] = "clubs"
        fighters[index]["weapon"]["self"] = "enucleates"
        fighters[index]["weapon"]["suicide"] = "impales"
        fighters[index]["weapon"]["crip"] = -2
    elif 50 < luck <= 5000:
        fighters[index]["weapon"]["name"] = "hand"
        fighters[index]["weapon"]["damage"] = 0
        fighters[index]["weapon"]["hit"] = "punches"
        fighters[index]["weapon"]["crit"] = "pimpslaps"
        fighters[index]["weapon"]["self"] = "smacks"
        fighters[index]["weapon"]["suicide"] = "strangles"
        fighters[index]["weapon"]["crip"] = 0
    elif 5000 < luck <= 7500:
        fighters[index]["weapon"]["name"] = "knife"
        fighters[index]["weapon"]["damage"] = 1
        fighters[index]["weapon"]["hit"] = "slashes"
        fighters[index]["weapon"]["crit"] = "stabs"
        fighters[index]["weapon"]["self"] = "cuts"
        fighters[index]["weapon"]["suicide"] = "wrist cuts"
        fighters[index]["weapon"]["crip"] = 4
    elif 7500 < luck <= 8500:
        fighters[index]["weapon"]["name"] = "katana"
        fighters[index]["weapon"]["damage"] = 2
        fighters[index]["weapon"]["hit"] = "slices"
        fighters[index]["weapon"]["crit"] = "cleaves"
        fighters[index]["weapon"]["self"] = "teleports behind"
        fighters[index]["weapon"]["suicide"] = "sepukus"
        fighters[index]["weapon"]["crip"] = 4
    elif 8500 < luck <= 9200:
        fighters[index]["weapon"]["name"] = "pistol"
        fighters[index]["weapon"]["damage"] = 4
        fighters[index]["weapon"]["hit"] = "fires at"
        fighters[index]["weapon"]["crit"] = "pistol whips"
        fighters[index]["weapon"]["self"] = "shoots"
        fighters[index]["weapon"]["suicide"] = "\"headshots\""
        fighters[index]["weapon"]["crip"] = 2
    elif 9200 < luck <= 9570:
        fighters[index]["weapon"]["name"] = "shotgun"
        fighters[index]["weapon"]["damage"] = 6
        fighters[index]["weapon"]["hit"] = "peppers"
        fighters[index]["weapon"]["crit"] = "point blanks"
        fighters[index]["weapon"]["self"] = "recoil hits"
        fighters[index]["weapon"]["suicide"] = "Kurt Cobains"
        fighters[index]["weapon"]["crip"] = 3
    elif 9570 < luck <= 9670:
        fighters[index]["weapon"]["name"] = "wok"
        fighters[index]["weapon"]["damage"] = 8
        fighters[index]["weapon"]["hit"] = "clangs"
        fighters[index]["weapon"]["crit"] = "clonks"
        fighters[index]["weapon"]["self"] = "bongs"
        fighters[index]["weapon"]["suicide"] = "bangs"
        fighters[index]["weapon"]["crip"] = 0
    elif 9670 < luck <= 9880:
        fighters[index]["weapon"]["name"] = "assault rifle"
        fighters[index]["weapon"]["damage"] = 10
        fighters[index]["weapon"]["hit"] = "assaults"
        fighters[index]["weapon"]["crit"] = "full autos"
        fighters[index]["weapon"]["self"] = "fires upon"
        fighters[index]["weapon"]["suicide"] = "ends"
        fighters[index]["weapon"]["crip"] = 5
    elif 9880 < luck <= 9940:
        fighters[index]["weapon"]["name"] = "sniper rifle"
        fighters[index]["weapon"]["damage"] = 17
        fighters[index]["weapon"]["hit"] = "downranges"
        fighters[index]["weapon"]["crit"] = "headshots"
        fighters[index]["weapon"]["self"] = "shoots"
        fighters[index]["weapon"]["suicide"] = "headsplodes"
        fighters[index]["weapon"]["crip"] = 7
    elif 9940 < luck <= 10000:
        fighters[index]["weapon"]["name"] = "grenade launcher"
        fighters[index]["weapon"]["damage"] = 15
        fighters[index]["weapon"]["hit"] = "blasts"
        fighters[index]["weapon"]["crit"] = "explodes"
        fighters[index]["weapon"]["self"] = "concusses"
        fighters[index]["weapon"]["suicide"] = "suicide bombs"
        fighters[index]["weapon"]["crip"] = 12
    # Reroll for armor
    luck = randint(0, 10000)
    if 0 <= luck <= 5000:
        fighters[index]["armor"]["name"] = "t-shirt"
        fighters[index]["armor"]["resist"] = 0
        #if the range is changed for destruction, this needs to be changed in the check for destroyed also
        fighters[index]["armor"]["save"] = 100
    elif 5000 < luck <= 7500:
        fighters[index]["armor"]["name"] = "sweatshirt"
        fighters[index]["armor"]["resist"] = 1
        fighters[index]["armor"]["save"] = 1
    elif 7500 < luck <= 8500:
        fighters[index]["armor"]["name"] = "bike helmet"
        fighters[index]["armor"]["resist"] = 2
        fighters[index]["armor"]["save"] = 3
    elif 8500 < luck <= 9300:
        fighters[index]["armor"]["name"] = "police vest"
        fighters[index]["armor"]["resist"] = 3
        fighters[index]["armor"]["save"] = 3
    elif 9300 < luck <= 9720:
        fighters[index]["armor"]["name"] = "kevlar"
        fighters[index]["armor"]["resist"] = 4
        fighters[index]["armor"]["save"] = 4
    elif 9720 < luck <= 9910:
        fighters[index]["armor"]["name"] = "SWAT gear"
        fighters[index]["armor"]["resist"] = 6
        fighters[index]["armor"]["save"] = 5
    elif 9910 < luck <= 10000:
        fighters[index]["armor"]["name"] = "wok"
        fighters[index]["armor"]["resist"] = 8
        fighters[index]["armor"]["save"] = 8
    return fighters


async def role_mentioned(message):
    # If there is more than 1 element (the command) in the message, see if it's a role.
    if len(message.content.split(" ")) > 1:
        find_role = message.content.split(" ")[1]
        for role in message.guild.roles:
            if role.mention == find_role:
                return role
    return None


async def get_player_list(message):
    candidates = list()
    # Get contestant list
    # if there are mentions, use them. Otherwise, use all guild members
    role = await role_mentioned(message)
    # add users by mention if here are mentions
    if len(message.mentions) > 0:
        candidates = message.mentions
    # add users by role if a role was mentioned
    elif role is not None:
        for applicant in message.guild.members:
            if role in applicant.roles:
                candidates.append(applicant)
    # add all users
    else:
        candidates = message.guild.members
    return candidates


async def populate_roster(candidates):
    # add eligible candidates to the fighters list
    fighters = {}
    for index, candidate in enumerate(candidates):
        # filter out bots
        if candidate.bot:
            continue
        name = candidate.nick
        if name is None:
            name = candidate.name
        # Each player has a dictionary with hp, name, and revenge key
        fighters[str(index)] = {}
        fighters[str(index)]["name"] = name
        fighters[str(index)]["hp"] = 100
        fighters[str(index)]["revenge"] = None
        fighters = await equip_combatant(fighters, str(index))
    return fighters


async def enact_attack(fighters, attacker, defender, name_len, verbose):
    # Person to take the damage, defender unless there is a critical fail
    target = defender
    # Was this a critical hit?
    critical = True
    # Roll to hit
    roll = randint(1, 20)
    # Damage total
    damage = randint(1, 10) + roll + fighters[attacker]["weapon"]["damage"] - fighters[defender]["armor"]["resist"]
    #max weapon use phrasing length
    phrase_len = 18
    #max weapon name length
    wepn_len = 13
    # Critical fail, hit self
    if roll is 1:
        target = attacker
        damage += fighters[defender]["armor"]["resist"] - fighters[attacker]["armor"]["resist"]
    elif roll is 20:
        damage += 10
    else:
        critical = False
    # If there are no other defenders, and the attacker didn't hit themself
    if target is None:
        return ""
    # Target takes damage
    fighters[target]["hp"] -= max(damage, 0)
    hit = ""
    if roll is 1 and fighters[target]["hp"] < 1:
        hit = fighters[attacker]["weapon"]["suicide"]
    elif roll is 1 and fighters[target]["hp"] > 0:
        hit = fighters[attacker]["weapon"]["self"]
    elif roll is 20:
        hit = fighters[attacker]["weapon"]["crit"]
        if randint(0,10) + fighters[attacker]["weapon"]["crip"] > 7 + fighters[defender]["armor"]["save"]:
            destruction = True
            armorname = fighters[defender]["armor"]["name"]
            fighters[defender]["armor"]["name"] = "t-shirt"
            fighters[defender]["armor"]["resist"] = 0
            fighters[defender]["armor"]["save"] = 100
        else:
            destruction = False
            armorname = ""
    else:
        hit = fighters[attacker]["weapon"]["hit"]
    battle_report = ""
    if verbose:
        # Print the default format attack
        battle_report += "\n{:{w}} {:{x}} {:{y}} with their {:{z}} for {:>2}".format(fighters[attacker]["name"], hit, ("themself" if attacker is target else fighters[target]["name"]), fighters[attacker]["weapon"]["name"], str(max(damage, 0)), w=name_len, x=phrase_len, y=name_len, z=wepn_len)
        # When attacker is the last person, print special messages
        # Critical texts
        if critical:
            if target is defender and destruction is True:
                battle_report += "\nCritical hit! {} destroyed {}'s {} with their {}.".format(
                    fighters[attacker]["name"], fighters[defender]["name"], armorname,
                    fighters[attacker]["weapon"]["name"])
            elif target is defender and destruction is False:
                battle_report += "\nCritical hit!"
            elif target is attacker:
                battle_report += "\nCritical fail!"
                if fighters[target]["hp"] > 0 and len(fighters) is 1:
                    battle_report += "\n{}, seeing no more opponents before them, attempts to end it all, but fails. Not that we expected anything more from them.".format(
                        fighters[attacker]["name"])
        if fighters[target]["hp"] < 1:
                battle_report += "\n"

        if defender is None:
            if fighters[target]["hp"] < 1:
                battle_report += "\tTest"
    # Attacker Loots Defender
    if fighters[defender]["hp"] < 1 and randint(1,15) < fighters[defender]["weapon"]["damage"] - fighters[attacker]["weapon"]["damage"]:
        weaponloot = True
        fighters[attacker]["weapon"]["name"] = fighters[defender]["weapon"]["name"]
        fighters[attacker]["weapon"]["damage"] = fighters[defender]["weapon"]["damage"]
        fighters[attacker]["weapon"]["hit"] = fighters[defender]["weapon"]["hit"]
        fighters[attacker]["weapon"]["crit"] = fighters[defender]["weapon"]["crit"]
        fighters[attacker]["weapon"]["self"] = fighters[defender]["weapon"]["self"]
        fighters[attacker]["weapon"]["suicide"] = fighters[defender]["weapon"]["suicide"]
        fighters[attacker]["weapon"]["crip"] = fighters[defender]["weapon"]["crip"]
    elif fighters[defender]["hp"] < 1 and randint(1,10) < fighters[defender]["armor"]["resist"] - fighters[attacker]["armor"]["resist"]:
        armorloot = True
        fighters[attacker]["armor"]["name"] = fighters[defender]["armor"]["name"]
        fighters[attacker]["armor"]["resist"] = fighters[defender]["armor"]["resist"]
        fighters[attacker]["armor"]["save"] = fighters[defender]["armor"]["save"]
    else:
        weaponloot = False
        armorloot = False
    if fighters[target]["hp"] < 1:
        if target is attacker:
            if len(fighters) is 1:
                battle_report += "{}, seeing no more opponents before them, decides to end it all.".format(
                    fighters[attacker]["name"])
            else:
                battle_report += "{} kills themself out of shame.".format(fighters[attacker]["name"])
        elif critical:
            battle_report += "{} fucking murders {} with their {}".format(fighters[attacker]["name"], fighters[defender]["name"], fighters[attacker]["weapon"]["name"])
            if weaponloot is True and armorloot is True:
                battle_report += ", and loots their {} and {}!".format(fighters[defender]["weapon"]["name"], fighters[defender]["armor"]["name"])
            elif weaponloot is True and armorloot is False:
                battle_report += ", and loots their {}!".format(fighters[defender]["weapon"]["name"])
            elif weaponloot is False and armorloot is True:
                battle_report += ", and loots their {}!".format(fighters[defender]["armor"]["name"])
            else:
                battle_report += "!"
        else:
            battle_report += "{} kills {} with their {}".format(fighters[attacker]["name"], fighters[defender]["name"], fighters[attacker]["weapon"]["name"])
            if weaponloot is True and armorloot is True:
                battle_report += ", and loots their {} and {}!".format(fighters[defender]["weapon"]["name"], fighters[defender]["armor"]["name"])
            elif weaponloot is True and armorloot is False:
                battle_report += ", and loots their {}!".format(fighters[defender]["weapon"]["name"])
            elif weaponloot is False and armorloot is True:
                battle_report += ", and loots their {}!".format(fighters[defender]["armor"]["name"])
            else:
                battle_report += "!"
        # Remove the dead candidate from the roster
        fighters.pop(target, None)
    else:
        # Defender will attempt revenge
        fighters[defender]["revenge"] = attacker
    if len(battle_report) > 0:
        battle_report += "\n"
    return battle_report


async def enact_round(fighters, name_len, verbose):
    # Text record of what happens during each round
    battle_report = ""
    # Shuffle the fighter attack order
    shuffled_fighters = list(fighters.keys())
    random.shuffle(shuffled_fighters)
    for attacker in shuffled_fighters:
        # if attacker is dead
        if fighters.get(attacker) is None:
            continue
        # Select defender
        defender = None
        # if there is a potential for revenge, 50% chance of hitting them
        if fighters[attacker]["revenge"] is not None and fighters.get(fighters[attacker]["revenge"]) is not None and randint(0,1) is 1:
            defender = fighters[attacker]["revenge"]
        # if there is no one left to hit, check for suicide
        elif len(fighters) is 1:
            battle_report += await enact_attack(fighters, attacker, defender, name_len, verbose)
        # Otherwise, choose a random opponent
        else:
            while defender is attacker or defender is None:
                defender = random.choice(list(fighters))
        # Enact an attack, and save the battle report for it
        battle_report += await enact_attack(fighters, attacker, defender, name_len, verbose)
    return battle_report


async def enact_battle(message, fighters, verbose):
    round_count = 0
    # As long as there is more than 1 fighter, do another round.
    while len(fighters) > 1:
        name_len = 0
        for fighter in fighters:
            name_len = max(len(fighters[fighter]["name"]), name_len)
        battle_report = await enact_round(fighters, name_len, verbose)
        # Split the battle report into an array of each line
        line_by_line = battle_report.split("\n")
        round_count += 1
        # Print round number, combatant count, and the battle reports
        output = "```\n\tRound  {}:\tCombatants: {}\n".format(round_count, len(fighters))
        if len(line_by_line) is 1 and len(line_by_line[0]) is 0:
            output += "No fatalities.\n"
        for line in line_by_line:
            if len(output) + len(line) < 1900:
                output += line + "\n"
            else:
                output += "```"
                await message.channel.send(output)
                output = "```\n" + line + "\n"
                time.sleep(3)
        output += "```"
        await message.channel.send(output)
        time.sleep(3)
        # In verbose mode, print all combatant's hp
        if verbose:
            output = "```\nRemaining Combatants: {}\n".format(len(fighters))
            for fighter in fighters:
                line = "{:{x}}: {:<2}\n".format(fighters[fighter]["name"], fighters[fighter]["hp"], x=name_len)
                if len(output) + len(line) < 1900:
                    output += line
                else:
                    output += "```"
                    await message.channel.send(output)
                    time.sleep(3)
                    output = "```\n{}".format(line)
            output += "```"
            await message.channel.send(output)
            time.sleep(3)

