import discord
from discord.ext import commands, tasks
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
config.read(configFileName)
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
        print(event)
        
prefix = config['BotValues']['PREFIX']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@tasks.loop(minutes=1)
async def time_check():
    message_channel = client.get_channel(int(config['DiscordValues']['OUTPUTCHANNEL']))
    await message_channel.send('test')

@time_check.before_loop
async def before_tc():
    await client.wait_until_ready()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    time_check.start()
    

    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.lower() == prefix + 'are you a turtle?':
        await message.channel.send("YOU BET YOUR SWEET ASS I AM!!!", reference=message)
    elif not message.content.startswith(prefix):
        return
    parsedMessage = message.content.split(' ')
    command = parsedMessage[0].lower()[1:]
    if command == 'hello':
        await message.channel.send('Hello!')
        
    elif command == 'set':
        if len(parsedMessage) >= 2:
            
            with open('config.ini', 'w') as configfile: 
                # done in each if statement in order to make sure writes are being done correctly
                if parsedMessage[1].lower() == 'announce':
                    config['DiscordValues']['ANNOUNCECHANNEL'] = str(message.channel.id)
                    config.write(configfile)
                    await client.get_channel(int(config['DiscordValues']['ANNOUNCECHANNEL'])).send('set announce channel')
                elif parsedMessage[1].lower() == 'weenie':
                    config['DiscordValues']['WEENIECHANNEL'] = str(message.channel.id)
                    config.write(configfile)
                    await client.get_channel(int(config['DiscordValues']['WEENIECHANNEL'])).send('set weenie channel')
                elif parsedMessage[1].lower() == 'output':
                    config['DiscordValues']['OUTPUTCHANNEL'] = str(message.channel.id)
                    config.write(configfile)
                    await client.get_channel(int(config['DiscordValues']['OUTPUTCHANNEL'])).send('set output channel')
                elif parsedMessage[1].lower() == 'server':
                    config['DiscordValues']['SERVER'] = str(message.server.id)
                    config.write(configfile)
                    await message.channel.send('set server')
                else:
                    await message.channel.send('Unknown configuration: ' + parsedMessage[1].lower())
                
        else:
            await message.channel.send('Error: Not enough arguments')
            
    elif command == 'stop':
        await message.channel.send('stopping')
        write_to_CSV()
        time_check.stop()
        client.close()
        print('stopped')
        sys.exit(0)
    elif command == 'channelid':
        id = str(message.channel.id)
        await message.channel.send(id)
        await client.get_channel(int(id)).send('test')

def announce(event:BandEvent):
    announcement = event.announce_str('<@&{}>'.format(config['BotValues']['ROLE']))
    message_channel = client.get_channel(int(config['DiscordValues']['OUTPUTCHANNEL']))
    message_channel.send(announcement)
    
def write_to_CSV():
    CSV_str = ''
    CSV_str += events[0].toCSVrow()
    for e in events[1:]:
        CSV_str += '\n'
        CSV_str += e.toCSVrow()
        
    with open('events.csv', 'w') as f:
        f.write(CSV_str)
            
client.run(config['BotValues']['TOKEN'])