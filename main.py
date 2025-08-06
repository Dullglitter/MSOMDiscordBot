import discord
from discord.ext import commands, tasks
from configparser import ConfigParser
import re
from datetime import datetime
import csv
from datetime import datetime
import sys
from pytz import timezone
import pytz

from Gameday import Gameday
from BandEvent import BandEvent

configFileName = 'config.ini'
config = ConfigParser()
config.read(configFileName)
gamedayCSV = 'events.csv'
list_time_index = 0

events = []
with open(gamedayCSV, newline='') as csvfile:
    format_string = '%Y-%m-%d %H:%M:%S'
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
# timezone = pytz.timezone(config['Other']['timezone'])

# current_time = datetime.now().astimezone(timezone)
for event in events:
    if event.time < datetime.now():
        list_time_index += 1
    else:
        break
    

    
prefix = config['BotValues']['PREFIX']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@tasks.loop(minutes=1)
async def time_check():
    global list_time_index
    # global timezone    
    # current_time = datetime.now().astimezone(timezone)
    current_time = datetime.now()
    if events[list_time_index].time <= current_time:
        await announce(events[list_time_index])
        list_time_index += 1
    # await message_channel.send('test')

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
                elif parsedMessage[1].lower() == 'currentrole':
                    if len(parsedMessage) == 3:
                        config['DiscordValues']['CURRENTROLE'] = parsedMessage[2]
                        print(parsedMessage[2])
                        config.write(configfile)
                        await message.channel.send('set currentrole')
                    else:
                        await message.channel.send('set incorrect number parameters, expected 3, got {}'.format(len(parsedMessage)))
                elif parsedMessage[1].lower() == 'adminrole':
                    if len(parsedMessage) == 3:
                        config['DiscordValues']['ADMINROLE'] = parsedMessage[2]
                        print(parsedMessage[2])
                        config.write(configfile)
                        await message.channel.send('set adminrole')
                    else:
                        await message.channel.send('set incorrect number parameters, expected 3, got {}'.format(len(parsedMessage)))
                        
                else:
                    await message.channel.send('Unknown configuration: ' + parsedMessage[1].lower())
                
        else:
            await message.channel.send('Error: Not enough arguments')
            
    elif command == 'announce':
        await announce(events[0])
            
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
    """
    Sends an announcement if event.doNotify is True, if not does nothing
    :param event: the event to make the announcement about
    :return (bool): returns False if not supposed to notify, returns True if announcement is sent
    """
    if not event.doNotify:
        return False
    announcement = event.announce_str(config['DiscordValues']['currentrole'])
    message_channel = client.get_channel(int(config['DiscordValues']['ANNOUNCECHANNEL']))
    return message_channel.send(announcement)
    return True
    
def write_to_CSV():
    """
    writes all events in events to the csv events.csv
    """
    CSV_str = ''
    CSV_str += events[0].toCSVrow()
    for e in events[1:]:
        CSV_str += '\n'
        CSV_str += e.toCSVrow()
        
    with open('events.csv', 'w') as f:
        f.write(CSV_str)
            
client.run(config['BotValues']['TOKEN'])