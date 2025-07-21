import discord
from configparser import ConfigParser
import re
from datetime import datetime
import csv
from datetime import datetime
import sys

from Gameday import Gameday
from BandEvent import BandEvent

configFileName = 'config.ini'
config = ConfigParser()
settings = config.read(configFileName)
gamedayCSV = "events.csv"

events = []
with open(gamedayCSV, newline='') as csvfile:
    format_string = "%Y-%m-%d %H:%M"
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        print(', '.join(row))
        event_time = datetime.strptime(row[2], format_string)
        print(event_time)
        if row[0] == 'gameday':
            events.append(Gameday(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        elif row[0] == 'event':
            events.append(BandEvent(row[1], row[2], row[3], row[4]))
    #game = Gameday(gameday['Name'],gameday['Time'],gameday['doCheckin'],
                #gameday['doNotify'],gameday['otherSchool'],gameday['otherMascot'])
    #events.append(game)
    #print(game)
    events.sort()
    
    for event in events:
        print(event.toCSVrow())
        
prefix = '!'

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == prefix + 'are you a turtle?':
        await message.channel.send("YOU BET YOUR SWEET ASS I AM!!!", reference=message)
    if not message.content.startswith(prefix):
        return
    parsedMessage = message.content.split(' ')
    command = parsedMessage[0].lower()[1:]
    if command == 'hello':
        await message.channel.send('Hello!')
        
    if command == 'set':
        if len(parsedMessage) >= 2:
            if parsedMessage[1].lower() == 'announce':
                await message.channel.send('TODO!')
            if parsedMessage[1].lower() == 'weenie':
                await message.channel.send('TODO!')
            if parsedMessage[1].lower() == 'config':
                await message.channel.send('TODO!')
        else:
            await message.channel.send('Error: Not enough arguments')
            
    if command == 'stop':
        await message.channel.send('stopping')
        client.close()
        print('stopped')
        sys.exit(0)
            

client.run(config['BotValues']['TOKEN'])

print("hi")
