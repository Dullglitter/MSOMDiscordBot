import discord
from discord.ext import commands, tasks
from configparser import ConfigParser
import re
from datetime import datetime, timedelta
import csv
import sys
from pytz import timezone
import pytz

from Gameday import Gameday
from BandEvent import BandEvent

configFileName = 'config.ini'
config = ConfigParser()
config.read(configFileName)
gamedayCSV = 'events.csv'
notify_time_index = 0
remind_time_index = 0
announcement_msg = None

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
    if event.time - timedelta(minutes=int(config['Other']['notify_offset_minutes'])) < datetime.now():
        notify_time_index += 1
    else:
        break

remind_time_index = notify_time_index

    
prefix = config['BotValues']['PREFIX']

intents = discord.Intents.all()
intents.message_content = True

client = discord.Client(intents=intents)

@tasks.loop(seconds=1)
async def time_check():
    global notify_time_index
    global announcement_msg
    # global timezone    
    # current_time = datetime.now().astimezone(timezone)
    if events[notify_time_index].time - timedelta(minutes=int(config['Other']['notify_offset_minutes'])) <= datetime.now():
        announcement_msg = await announce(events[notify_time_index])
        await announcement_msg.add_reaction('🎷')
        notify_time_index += 1
    global remind_time_index
    if events[remind_time_index].time - timedelta(minutes=int(config['Other']['remind_offset_miuntes'])) <= datetime.now():
        await remind(events[notify_time_index])
        remind_time_index += 1

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
    
    admin_role = client.get_guild(int(config['DiscordValues']['guild'])).get_role(int(config['DiscordValues']['adminrole']))
    admin_list = admin_role.members
    is_admin = False
    if message.author in admin_list:
        is_admin = True
    if command == 'hello':
        await message.channel.send('Hello!')
        
    elif command == 'set':
        if not is_admin and message.author.id != 508292942155218959:
            await message.channel.send('You do not have access to that command')
            return
            
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
                elif parsedMessage[1].lower() == 'guikd':
                    config['DiscordValues']['guild'] = str(message.server.id)
                    config.write(configfile)
                elif parsedMessage[1].lower() == 'currentrole':
                    if len(parsedMessage) == 3:
                        match = re.search('\d+', parsedMessage[2])
                        config['DiscordValues']['currentrole'] = match.group()
                        print(parsedMessage[2])
                        config.write(configfile)
                        await message.channel.send('set currentrole')
                    else:
                        await message.channel.send('set incorrect number parameters, expected 3, got {}'.format(len(parsedMessage)))
                elif parsedMessage[1].lower() == 'adminrole':
                    if len(parsedMessage) == 3:
                        match = re.search('\d+', parsedMessage[2])
                        config['DiscordValues']['adminrole'] = match.group()
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
        await announce(events[notify_time_index])
            
    elif command == 'stop':
        if not is_admin and message.author.id != 508292942155218959:
            await message.channel.send('You do not have access to that command')
            return
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
    reaction = config['Other']['reaction']
    announcement = event.announce_str(config['DiscordValues']['currentrole'])
    message_channel = client.get_channel(int(config['DiscordValues']['ANNOUNCECHANNEL']))
    if event.doCheckin:
        reaction_time = int(config['Other']['notify_offset_minutes']) - int(config['Other']['remind_offset_miuntes'])
        msg = message_channel.send(announcement + '\n\nReact to this message with a {}within {} minutes'
                                    ' or be :hotdog:'.format(reaction, reaction_time))
        return msg
        
    return message_channel.send(announcement)
    
def remind(event:BandEvent): 
    """
    Sends an weenies members of current_role if they have not reacted to the message for the event
    :param event: the event to make the check reactions on
    :return (bool): returns False if not supposed to remind, returns True if message sent or no one to remind
    """
    client.get_all_members()
    reaction = config['Other']['reaction']
    match = re.search('\d+', config['DiscordValues']['currentrole'])
    # role = client.get_role(int(config['DiscordValues']['currentrole']))
    guild = client.get_guild(int(config['DiscordValues']['guild']))
    role = guild.get_role(int(config['DiscordValues']['currentrole']))
    member_list = guild.members
    weenies = []
    for member in member_list:
        if role in member.roles:
            weenies.append(member)
    # if member has role and hasnt reacted -> weenie
    print(member_list)
    
    
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