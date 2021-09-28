import discord
import requests
import json
import os
import random
from itertools import cycle
from replit import db
from discord.ext import commands
from discord.ext import tasks
import weather

my_secret = os.environ['TOKEN']
my_secret_api = os.environ['api_key']

#client = discord.Client()

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents = intents)
command_prefix = 'w.'

status = cycle(['with fire', 'with knives', 'with feelings', 'with hearts', 'with myself', 'dead'])
def update_courses(course_link):
  if "courses" in db.keys():
    courses = db["courses"]
    courses.append(course_link)
    db["courses"] = courses
  else:
    db["courses"] = [course_link]

def delete_course(index):
  courses = db["courses"]
  if len(courses) > index:
    del courses[index]
    db["courses"] = courses


@client.event
async def on_member_join(member): 
                         
    #guild = client.get_guild(814620705425195049)   #serverID
    #channel = guild.get_channel(814620705794687017)   #channelID
    
    #testing server
    guild = client.get_guild(892181610726838292)
    channel = guild.get_channel(892181610726838295)

    print('join info: ',member.name)

    #welcome the member on server
    await channel.send(f':computer: Welcome, its COMP216/SEC401 Group 2 {member.mention} ! :nerd:')
    

@client.event
async def on_ready():
    print('we have {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='w.[location]'))

@client.event
async def on_message(message):
    if message.author != client.user and message.content.startswith(command_prefix):
        if len(message.content.replace(command_prefix, '')) >= 1:
            location = message.content.replace(command_prefix, '').lower()
            url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={my_secret_api}&units=imperial'
            try:
                data = weather.parse_data(json.loads(requests.get(url).content)['main'])
                await message.channel.send(embed=weather.weather_message(data, location))
            except KeyError:
                await message.channel.send(embed=weather.error_message(location))


    msg = message.content

    if msg.lower() == '$hi':
        await message.channel.send('Hello! I am a welcoming bot, you can type $help to ask! ')

    if msg.lower().startswith("$help"):
      helpEmbed = discord.Embed(
        title="Commands list",
        colour=0x4EE3D9
      )
      helpEmbed.add_field(name="--------------------------------------------------------------------------------------------------", value=":pushpin: General commands", inline=False)
      helpEmbed.add_field(name="how are you  ||  how are you doing", value="Ask the bot how it feels", inline=True)
      
      helpEmbed.add_field(name="--------------------------------------------------------------------------------------------------", value=":pushpin: Course commands", inline=False)
    
      helpEmbed.add_field(name="$list", value="Shows all courses in the list", inline=True)
      helpEmbed.add_field(name="$add + link", value="Add a new course", inline=True)
      helpEmbed.add_field(name="del + number", value="Delete corresponding course (list starts in 0)", inline=True)
      helpEmbed.add_field(name="$random", value="Selects a random course", inline=True)
      helpEmbed.add_field(name="--------------------------------------------------------------------------------------------------", value=":pushpin: Weather commands", inline=False)
      helpEmbed.add_field(name="w.'location'", value="Display the temperature, in Fahrenheit, of the location", inline=False)
      helpEmbed.add_field(name="Locations examples: ", value="Toronto, Mississauga, Scarborough", inline=False)
      helpEmbed.add_field(name="--------------------------------------------------------------------------------------------------", value=":pushpin: Admin commands", inline=False)
      helpEmbed.add_field(name="!clear", value="Clear the last 5 messages", inline=True)
      helpEmbed.add_field(name="!kick + @member name", value="Kick the member from the server", inline=True)
      helpEmbed.add_field(name="!ban + @member name", value="Ban the member from the server", inline=True)
      
      await message.channel.send(embed=helpEmbed)

    responses = ["If I were any better, I'd be you.",
                 'Average. Not terrific, not terrible, just average.',
                 "I’ve been going through some crests and troughs in my life. Is everything stable at your end?",
                 "Overworked and underpaid.",
                 "Like you, but better.",
                 "Can't complain. Nobody listens to me anyway.",
                 "All the better, now that you asked.",
                 "I don't know, you tell me. How am I right now?",
                 "I love you.",
                 "Not so well, does that bother you?",
                 "Somewhere between better and best.",
                 "I was fine until you asked.",
                 "Better now that I'm talking to you.",
                 "Well, I haven't had my morning coffee yet and no one has gotten hurt, so I'd say pretty good at this point in time.",
                 "Good at minding my own business? Better than most people.",
                 "I can't complain! It's against the Company Policy.",
                 "Well, unless the weather has different plans in store."]

    if msg.lower() == 'how are you?' or msg.lower() == 'how are you' or msg.lower() == 'how r u' or msg.lower() == 'how are u' or msg.lower() == 'how u doing' or msg.lower() == 'how are you doing':
      response = random.choice(responses)
      await message.channel.send(response)             

    if msg.lower().startswith('$list'):
        courses = []
        if "courses" in db.keys():
            courses = db["courses"]
        for x in courses:
          await message.channel.send(x)

    if msg.lower().startswith('$add'):
      course_link = msg.split("$add ",1)[1]
      update_courses("<"+course_link+">")
      await message.channel.send("New course added")

    if msg.lower().startswith('$del'):
      courses = []
      if "courses" in db.keys():
        index = int(msg.split("$del",1)[1])
        delete_course(index)
        courses = db["courses"]
      await message.channel.send("Course removed")
    
    if msg.lower().startswith('$random'):
      await message.channel.send(random.choice(db["courses"]))

    await client.process_commands(message)
    
    # if msg.lower().startswith('$list'):
    #     courses = []
    #     if "courses" in db.keys():
    #         courses = db["courses"]
    #     for x in courses:
    #       await message.channel.send(x)

@client.command()
async def ping(ctx):
  await ctx.send(f'{round(client.latency * 1000)}ms')

@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

@tasks.loop(seconds=30)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

client.run(my_secret)

