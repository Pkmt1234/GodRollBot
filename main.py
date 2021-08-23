import discord
import os
import nacl
import requests
import asyncio
from replit import db
from keep_alive import keep_alive

intents = discord.Intents.all()
client = discord.Client(intents=intents)

#runs when the bot logs in
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Leaderboard.....'))
  

  #for entry in db.keys():
    #del db[entry]
  #for guild in client.guilds:
    #channel = await client.fetch_channel(830421634082144256)
    #await channel.send("https://cdn.discordapp.com/attachments/716393997408534593/879468513767600178/5kk9ni.png")
  await update()
  
    
async def update():
    loop = asyncio.get_running_loop()
    #end_time = loop.time() + 3600.0
    while True:
      print(loop.time())
      set_member_stats()
      await role_change()
      #if (loop.time() + 1.0) >= end_time:
        #break
      await asyncio.sleep(3600)

def set_member_stats():
  print("start stats")
  response = requests.get("https://3gmks9uzn3.execute-api.eu-west-2.amazonaws.com/default/Leaderboard")
  leaderboarddict = response.json()
  scores = leaderboarddict["scores"]

  db["oldleaderboard"] = db["leaderboard"]

  #Resets the leaderboard
  db["leaderboard"] = []
  #grabs the membership ID and roll scores of every member
  for key in scores:
   
    #creates database entry that holds the player's membership ID
    
    if key not in db.keys():
      db[key] = {"MembershipID": key}

    #Refills the leaderboard  
    db["leaderboard"].append(db[key])
      
    
    #grabs the stats of the player and forwards it to the set_member_stats function
    playerstats = scores[key]
    membershipinfo = playerstats["membership_info"]
    stats = playerstats["roll_scores"]
    membershipID = key
    membershiptype = membershipinfo["membership_type"]

    #resets values for new entry
    totalpoints = 0
    godrolls = 0
    greatrolls = 0
    goodrolls = 0
    badrolls = 0
    totalweaponscore = 0
  
    #counts up the points of all players and checks how many rolls of each quality level they have
    try:
      for weapon in stats:
        totalpoints = totalpoints + int(stats[weapon][0])
        if int(stats[weapon][0]) == 5:
          godrolls = godrolls + 1
        elif int(stats[weapon][0]) == 3:
          greatrolls = greatrolls + 1
        elif int(stats[weapon][0]) == 1:
          goodrolls = goodrolls + 1
        else:
          badrolls = badrolls + 1 
        totalweaponscore = totalweaponscore + stats[weapon][1]
    
    except:
      for weapon in stats:
        totalpoints = totalpoints + int(stats[weapon])
        if int(stats[weapon]) == 5:
          godrolls = godrolls + 1
        elif int(stats[weapon]) == 3:
          greatrolls = greatrolls + 1
        elif int(stats[weapon]) == 1:
          goodrolls = goodrolls + 1
        else:
          badrolls = badrolls + 1 
  
    headers = {
     "X-API-Key": os.getenv("BNGTOKEN"),
    }

    membershipdata = requests.get(f"https://www.bungie.net/Platform/Destiny2/{membershiptype}/Profile/{membershipID}/?components=100", headers=headers).json()

    displayname = membershipdata["Response"]["profile"]["data"]["userInfo"]["displayName"]
  
    playerdata = db[membershipID]
    
    try: 
      discordID = playerdata["DiscordID"]
    #print (playerdata)
    except:
      playerdata["DiscordID"] = 0

    #compiles all stats into a singular dictionary unique to that player
    db[membershipID] = {
      "MembershipID": membershipID,
      "MembershipType": membershiptype,
      "Displayname": displayname,
      "Points": totalpoints,
      "God Rolls": godrolls,
      "Great Rolls": greatrolls,
      "Good Rolls": goodrolls,
      "Bad Rolls": badrolls,
      "Total Weapon Points": totalweaponscore,
      "DiscordID": discordID
      }

    
    #creates the leaderboard and adds every member to it
    if "leaderboard" not in db.keys():
      db["leaderboard"] = []

  for entry in db["leaderboard"]:
    if entry["MembershipID"] == db[membershipID]["MembershipID"]:
      entry = db[membershipID]

  
  #sorts the leaderboard based on points
  db["leaderboard"] = sorted(db["leaderboard"], key=lambda x: (x['Points']* -1, x['God Rolls']* -1, x['Great Rolls'] *-1, -x['Total Weapon Points']))
  print("end stats")
  
  db["leaderboardprint"] = ""

  for index, player in enumerate(db["leaderboard"]):
    name = player["Displayname"]
    gold = player["God Rolls"]
    silver = player["Great Rolls"]
    bronze = player["Good Rolls"]
    points = player["Points"]
    totalpoints = player["Total Weapon Points"]

    print(f"{name}: {totalpoints}")

    if index == 0:
      db[str(index)] = [f":first_place:: **{name}**: ",f"{points} Points", f"(Gold: {gold}, Silver: {silver}, Bronze: {bronze}),", f" *Score: {totalpoints}*\n"]
      #print(db[str(index)])
    elif index == 1:
      db[str(index)] = [f":second_place:: **{name}**: ",f"{points} Points", f"(Gold: {gold}, Silver: {silver}, Bronze: {bronze}),", f" *Score: {totalpoints}*\n"]
    elif index == 2:
      db[str(index)] = [f":third_place:: **{name}**: ",f"{points} Points", f"(Gold: {gold}, Silver: {silver}, Bronze: {bronze}),", f" *Score: {totalpoints}*\n"]
    else:
      db[str(index)] = [f"{index + 1}: **{name}**:",f"{points} Points", f"(Gold: {gold}, Silver: {silver}, Bronze: {bronze}),", f" *Score: {totalpoints}*\n"]
      #print(db[str(index)])

    db["changes"] = ""
    db["leaderboardchange"] = False
    if player == db["oldleaderboard"][index]:
      continue
    else:
      db["leaderboardchange"] = True
      for i, oldplayer, in enumerate(db["oldleaderboard"]):
        if name == oldplayer["Displayname"]:
          oldposition = i
          if index > oldposition:
            arrowtext = ":arrow_up:"
          else:
            arrowtext = ":arrow_down:"
          db["changes"] = db["changes"] + f"{name}: #{oldposition} {arrowtext} #{index}\n"
  



#runs when bot joins a server
@client.event
async def on_guild_join(guild):
  #sends a message to indicate the bot is working
  await guild.system_channel.send("Hello Fools\n\nTo authenticate yourself, please go to #bot-commands and link your discord to your bungie account by using !auth")

@client.event
async def on_message(message):

  if message.author == client.user:
        return

  msg = message.content
  
  if msg.startswith ("!auth "):
    number = int(msg.split("!auth ", 1)[1]) - 1
    #print(number)
    playerstats = db["leaderboard"][number]
    playerstats["DiscordID"] = message.author.id

    db[playerstats["MembershipID"]] = db["leaderboard"][number]
    await message.channel.send("Your ID has been linked to " + playerstats["Displayname"] + "'s stats!")
    #print(db["leaderboard"][number])
    return


  if msg.startswith("!auth"):
    responsemessage = ""
    playernumber = 1

    for player in db["leaderboard"]:
      for key in player:
        if key == "Displayname":
          displayname = player[key]
     
      responsemessage = responsemessage + str(playernumber) + ": " + displayname + "\n"
      playernumber = playernumber + 1
    await message.channel.send("To authenticate with the bot, please reply with !auth [number]\nYou can find the correct number below next to your in-game name\n"+ responsemessage)
    return
  
  if msg.startswith("!leaderboard"):
    embed = discord.Embed(title = "***__THE RAVIOLI CLUB GOD ROLL LEADERBOARD__***", color = 76021)
    
    for index, player in enumerate(db["leaderboard"]):
      embed.add_field(name = db[str(index)][0], value = db[str(index)][1] + " " + db[str(index)][2] + db[str(index)][3], inline = False)
    

    await message.channel.send(embed = embed)

async def role_change():
  print("start roles")
  for guild in client.guilds:
    for role in guild.roles:
      if role.name == "Human Godroll":
        firstplacerole = role
      if role.name == "Barely Human":
        secondplacerole = role
      if role.name == "Concerningly Obsessed":
        thirdplacerole = role
      if role.name == "Grass Touched":
        sixthplacerole = role
      if role.name == "Enthusiastic Amateur":
        godrollrole = role
    for index, player in enumerate(db["leaderboard"]):          
      try:
        member = guild.get_member(int(player["DiscordID"]))
      
        #await member.remove_roles(firstplacerole, reason=None, atomic=True)
        #await member.remove_roles(secondplacerole, reason=None, atomic=True)
        #await member.remove_roles(thirdplacerole, reason=None, atomic=True)
        #await member.remove_roles(sixthplacerole, reason=None, atomic=True)
        await member.remove_roles(godrollrole, reason=None, atomic=True)
        print ("Deleted roles")
        print (index)
        print (player["God Rolls"])
        if index == 0:
          try:
            await member.add_roles(firstplacerole, reason=None, atomic=True)
          except:
            continue
          try:
            await member.remove_roles(secondplacerole, reason=None, atomic=True)
            continue
          except:
            try:
              await member.remove_roles(thirdplacerole, reason=None, atomic=True)
              continue
            except:
              try:
                await member.remove_roles(sixthplacerole, reason=None, atomic=True)
                continue
              except:
                  try:
                    await member.remove_roles(godrollrole, reason=None, atomic=True)
                  except:
                    continue
          continue
        if index == 1:
          try:
            await member.add_roles(secondplacerole, reason=None, atomic=True)
          except:
            continue
          try:
            await member.remove_roles(firstplacerole, reason=None, atomic=True)
            continue
          except:
            try:
              await member.remove_roles(thirdplacerole, reason=None, atomic=True)
              continue
            except:
              try:
                await member.remove_roles(sixthplacerole, reason=None, atomic=True)
                continue
              except:
                  try:
                    await member.remove_roles(godrollrole, reason=None, atomic=True)
                  except:
                    continue
          continue
          continue
        if index == 2 or index == 3:
          try:
            await member.add_roles(thirdplacerole, reason=None, atomic=True)
          except:
            continue
          try:
            await member.remove_roles(secondplacerole, reason=None, atomic=True)
            continue
          except:
            try:
              await member.remove_roles(firstplacerole, reason=None, atomic=True)
              continue
            except:
              try:
                await member.remove_roles(sixthplacerole, reason=None, atomic=True)
                continue
              except:
                  try:
                    await member.remove_roles(godrollrole, reason=None, atomic=True)
                  except:
                    continue
          continue
          continue
        if index == 4 or index == 5 or index == 6:
          try:
            await member.add_roles(sixthplacerole, reason=None, atomic=True)
          except:
            continue
          try:
            await member.remove_roles(secondplacerole, reason=None, atomic=True)
            continue
          except:
            try:
              await member.remove_roles(thirdplacerole, reason=None, atomic=True)
              continue
            except:
              try:
                await member.remove_roles(firstplacerole, reason=None, atomic=True)
                continue
              except:
                  try:
                    await member.remove_roles(godrollrole, reason=None, atomic=True)
                  except:
                    continue
          continue
          continue
        else:
          try:
            await member.add_roles(godrollrole, reason=None, atomic=True)
          except:
            continue
          try:
            await member.remove_roles(secondplacerole, reason=None, atomic=True)
            continue
          except:
            try:
              await member.remove_roles(thirdplacerole, reason=None, atomic=True)
              continue
            except:
              try:
                await member.remove_roles(sixthplacerole, reason=None, atomic=True)
                continue
              except:
                  try:
                    await member.remove_roles(firstplacerole, reason=None, atomic=True)
                  except:
                    continue
          continue
      except:
        continue
  if db["leaderboardchange"] == True:
    channel = client.get_channel(866293300322762802)
    embed = discord.Embed(title = f"New Leaderboard Changes:\n", color = 76021, description = db["changes"])
    await channel.send(embed)
  print ("end roles")

#keeps bot running 24/7

keep_alive()
client.run(os.getenv('TOKEN'))
asyncio.run(update())