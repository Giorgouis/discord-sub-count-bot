import requests
import json
import asyncio
import discord
from discord.ext import commands, tasks

# SETUP
client = commands.Bot(command_prefix='!')
with open('settings.json', 'r') as fp:
    settings = json.load(fp)



name = settings['config']['channel_name']
key = settings['config']['youtube_api_token']


@client.event
async def on_ready():
    get_sub_count.start()


@tasks.loop(seconds=30)
async def get_sub_count():
    # GET
    data = requests.get(
        f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={name}&key={key}").json()
    subs = data['items'][0]['statistics']['subscriberCount']
    with open('settings.json', 'r') as fp:
        previous = json.load(fp)
    
    # Check if gained more subscribers

    if int(subs) > int(previous['subs']['max']):
        
        previous['subs']['max'] = subs
        
        # send message
        channel = client.get_channel(int(settings['config']['discord_channel_id']))
        await channel.send(settings['config']['message'].replace('--subs', subs))
    previous['subs']['current'] = str(subs)

    # write the data
    with open('settings.json', 'w') as fp:
        json.dump(previous, fp, indent=4)
    if int(subs) % 50 == 0:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{subs} Subscribers!!"))
        await asyncio.sleep(120)
        await client.change_presence(status=discord.Status.online)


client.run(settings['config']['discord_token'])
