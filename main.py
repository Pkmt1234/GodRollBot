import discord
import os
import requests
from replit import db
from keep_alive import keep_alive

client = discord.Client()

#runs when the bot logs in
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  #for entry in db.keys():
    #del db[entry]

  for entry in db["leaderboard"]:
    print(entry)

  #pulls request from the leaderboard API
  response = requests.get("https://3gmks9uzn3.execute-api.eu-west-2.amazonaws.com/default/Leaderboard")
  leaderboarddict = response.json()
  scores = leaderboarddict["scores"]

  #grabs the membership ID and roll scores of every member
  for key in scores:
    #creates database entry that holds the player's membership ID
    if key not in db.keys():
      db[key] = {"MembershipID": key}
    
    #grabs the stats of the player and forwards it to the set_member_stats function
    playerstats = scores[key]
    set_member_stats(playerstats["roll_scores"], key)
    
  
def set_member_stats(stats, membershipID):
  #resets values for new entry
  totalpoints = 0
  godrolls = 0
  greatrolls = 0
  goodrolls = 0
  badrolls = 0
  
  #counts up the points of all players and checks how many rolls of each quality level they have
  for key in stats:
    totalpoints = totalpoints + int(stats[key])
    if int(stats[key]) == 5:
      godrolls = godrolls + 1
    elif int(stats[key]) == 3:
      greatrolls = greatrolls + 1
    elif int(stats[key]) == 1:
      goodrolls = goodrolls + 1
    else:
      badrolls = badrolls + 1 
  
  #compiles all stats into a singular dictionary unique to that player
  db[membershipID] = {
    "MembershipID": membershipID,
    "Points": totalpoints,
    "God Rolls": godrolls,
    "Great Rolls": greatrolls,
    "Good Rolls": goodrolls,
    "Bad Rolls": badrolls
  }

  #creates the leaderboard and adds every member to it
  if "leaderboard" not in db.keys():
    db["leaderboard"] = []
  if db[membershipID] not in db["leaderboard"]:
    db["leaderboard"].append(db[membershipID])
  
  #sorts the leaderboard based on points
  db["leaderboard"] = sorted(db["leaderboard"], key=lambda k: k['Points']* -1)

#runs when bot joins a server
@client.event
async def on_guild_join(guild):
  #sends a message to indicate the bot is working
  await guild.system_channel.send("Hello Fools")

  #grabs each of the roles the bot needs to change based on player stats
  for role in guild.roles:
    if str(role.name) == "Human Godroll":
      firstplacerole = role
    if str(role.name) == "Barely Human":
      secondplacerole = role
    if str(role.name) == "Concerningly Obsessed":
      thirdplacerole = role
    if str(role.name) == "Grass Touched":
      sixthplacerole = role
    if str(role.name) == "Enthusiastic Amateur":
      godrollrole = role

#keeps bot running 24/7
keep_alive()
client.run(os.getenv('TOKEN'))