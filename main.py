import discord
from configparser import ConfigParser
import re

configFileName = 'config.ini'
config = ConfigParser()
settings = config.read(configFileName)

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
            

client.run(config['BotValues']['TOKEN'])

print("hi")
