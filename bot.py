import asyncio
import inspect
import math
import random
import sqlite3
import time

from discord.ext import commands
import discord
from googletrans import Translator
from google_images_search import GoogleImagesSearch
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import psycopg2
import asyncpg
import os
import json
from google_images_download import google_images_download
from psycopg2 import DatabaseError
import glob
import uuid
import shutil
import imghdr

dbname = os.environ["dbname"]
dbhost = os.environ["dbhost"]
dbuser = os.environ["dbuser"]
dbpass = os.environ["dbpass"]

connection = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpass, host=dbhost)

cursor = connection.cursor()

translator = Translator()

detectionenabled = False

edited_messages_list = []
edited_messages_usernames = []
edited_messages_avatarurl = []
deleted_messages_list = []
deleted_messages_avatarurl = []
deleted_messages_usernames = []
revers = False

client = commands.Bot(command_prefix='t!')
client.remove_command('help')

my_bytes_io = BytesIO()

main_guild = client.get_guild(828423940531159101)

gis = GoogleImagesSearch(os.environ["thing"], os.environ["thingy"])




@client.event
async def on_ready():
    main_channel = client.get_channel(828423941017042964)
    print("bot is yesing")

_search_params = {
        'q': f'gif',
        'num': 12,
        'safe': 'medium',
        'fileType': 'gif',
        'imgType': 'photo',
        'imgSize': 'imgSizeUndefined',
        'imgDominantColor': 'black',
        'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived'
    }

@client.event
async def on_message_edit(before, after):
    if before.author == client.user: return
    if before.author.bot: return
    if before.content == after.content: return
    if before.attachments: return
    edited_messages_list.append(before.content)
    edited_messages_usernames.append(before.author.name)
    edited_messages_avatarurl.append(str(before.author.avatar_url_as(size=128)))
    print(before.author.name)
    print("added " + before.content + " In table")
    print(list(edited_messages_list))

@client.event
async def on_message_delete(before):
    if before.author == client.user: return
    if before.author.bot: return
    if before.attachments:
        deleted_messages_list.append(before.attachments[0].url)
        deleted_messages_usernames.append(before.author.name)
        deleted_messages_avatarurl.append(str(before.author.avatar_url_as(size=128)))
    else:
        deleted_messages_list.append(before.content)
        deleted_messages_usernames.append(before.author.name)
        deleted_messages_avatarurl.append(str(before.author.avatar_url_as(size=128)))
    print(before.author.name)
    print("added " + before.content + " In table")
    print(list(deleted_messages_list))

@client.event
async def on_message(message):

    if message.content == "t!": return
    if message.content.startswith("t!"):
        try:
            command5 = f"""SELECT
	    CUSTOMCOMMAND
    FROM    
	    CUSTOMCOMMANDS
   WHERE
	    CUSTOMCOMMAND = '{message.content.replace("t!","")}'"""
            cursor.execute(command5)
            command6 = f"""SELECT
	    WHATWILLCCSEND
    FROM    
	    CUSTOMCOMMANDS
    WHERE 
	    CUSTOMCOMMAND LIKE '{message.content.replace("t!","")}%';"""
            cursor.execute(command6)
            result = cursor.fetchone()
            if result is not None:
                await message.channel.send(result[0].replace("(,)", ""))
        except DatabaseError:
            cursor.execute("rollback;")

    #elif "media.discordapp.net" in message.content and ".mp4" in message.content or ".mov" in message.content or ".webm" in message.content:
   #     trashemoji = "🗑️"

    #    def checkforreaction(reaction, user):
    #        return str(user.id) == str(message.author.id) and str(reaction.emoji) in [trashemoji]
    #    await message.delete()
    #    msg = await message.channel.send(message.content.replace("media.discordapp.net", "cdn.discordapp.com") + " this video is sent by " + message.author.mention + "(this has been done so videos work correctly)")
     #   await msg.add_reaction(trashemoji)
    #    reaction, user = await client.wait_for("reaction_add", timeout=1000, check=checkforreaction)
    #    if reaction.emoji == trashemoji:
     #       await msg.delete()

    elif "pls pfp" in message.content or "plz pfp" in message.content:
        imagename = str(uuid.uuid4())
        images = gis.search(search_params=_search_params, custom_image_name=imagename)
        randomnumber = random.randint(0,12)
        print(randomnumber)
        gis.results()[randomnumber].download(os.path.dirname(__file__))
        list_of_files = glob.glob(os.path.dirname(__file__) + "\*")
        latest_file = max(list_of_files, key=os.path.getctime)
        await message.channel.send(file=discord.File(latest_file))


    await client.process_commands(message=message)

#@client.command(name="t")
#async def s(ctx, ccname):
#    try:
#        command5 = f"""SELECT
#	    CUSTOMCOMMAND
#    FROM
#	    CUSTOMCOMMANDS
#   WHERE
#	    CUSTOMCOMMAND = '{ccname}'"""
#        cursor.execute(command5)
#        command6 = f"""SELECT
#	    WHATWILLCCSEND
#    FROM
#	    CUSTOMCOMMANDS
#    WHERE
#	    CUSTOMCOMMAND LIKE '{ccname}%';"""
#        cursor.execute(command6)
#        result = cursor.fetchone()
#        if result is not None:
#            await ctx.send(result[0].replace("(,)", ""))
#    except DatabaseError:
#        cursor.execute("rollback;")


@client.command(name='eval', pass_context=True)
@commands.is_owner()
async def eval_(ctx, *, command):
    res = eval(command)
    if inspect.isawaitable(res):
        print(await res)
    else:
        print(res)


@client.command()
async def ping(ctx):
    embed = discord.Embed(
        title='Ping',
        description=f"Pong! `{math.floor(client.latency * 1000)}ms`",
        color=discord.Colour.orange()
    )

    embed.set_footer(text="i am racist")
    embed.set_image(
        url="https://media.discordapp.net/attachments/824625614312046592/844570716250963978/caption-5-1.gif")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))

    await ctx.send(embed=embed)



@client.command()
async def allcc(ctx):
    try:
        cursor.execute("SELECT CUSTOMCOMMAND FROM CUSTOMCOMMANDS")
        allccs = cursor.fetchall()
        embed = discord.Embed(
            title="All Custom Commands",
            description=allccs,
            color=discord.Colour.orange()
        )

        embed.set_footer(text=f"Number of custom commands is: {len(allccs)}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/824625614312046592/844570716250963978/caption-5-1.gif")

        await ctx.send(embed=embed)
    except DatabaseError:
        cursor.execute("rollback;")


@client.command()
async def addcc(ctx, thing, *, thingtosend):
    print(thing, thingtosend)
    try:
        command1 = """CREATE TABLE IF NOT EXISTS
        CUSTOMCOMMANDS_(
        CUSTOMCOMMAND  TEXT  PRIMARY KEY NOT NULL,
        WHATWILLCCSEND TEXT              NOT NULL)"""
        cursor.execute(command1)
        cursor.execute(
            f"INSERT INTO CUSTOMCOMMANDS (CUSTOMCOMMAND, WHATWILLCCSEND) VALUES ('{thing}','{thingtosend}');")
        connection.commit()
        await ctx.send("added " + thing + " in database")
    except DatabaseError:
        cursor.execute("rollback;")


@client.command()
async def removecc(ctx, *, thingtoremove):
    if ctx.author.guild_permissions.manage_messages or ctx.author.id == 756504591725756537:
        try:
            command4 = f"""DELETE FROM CUSTOMCOMMANDS WHERE CUSTOMCOMMAND LIKE '{thingtoremove}%';"""
            cursor.execute(command4)
            connection.commit()
            await ctx.send(f"deleted {thingtoremove} from database")
        except DatabaseError:
            cursor.execute("rollback;")
    else:
        await ctx.send("you do not have the required premissions to remove a custom command. please tell someone who has manage messages perms to delete it and give a good reason to why")

@client.command()
@commands.is_owner()
async def removeallcc(ctx):
    try:
        cursor.execute("DELETE FROM CUSTOMCOMMANDS")
        connection.commit()
        await ctx.send("deleted every custom command from database")
    except DatabaseError:
        cursor.execute("rollback;")


@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="Use t!help to find out about all the commands",
        color=discord.Colour.orange()
    )
    embed.add_field(name="Custom Commands",
                    value="t!addcc {customcommand} {whatwillcustomcommandsend} \nt!removecc {customcommandname} \nt!removeallcc(tamim only) \nt!t {customcommandname}",
                    inline=False)
    embed.add_field(name="Status", value="t!ping")
    embed.add_field(name="Other", value="t!john_china")
    embed.add_field(name="Translation",
                    value="t!translate {untranslated text} \nt!translate_from {from} {to} {untranslated text}")
    embed.set_footer(text="yo mama so fat")
    embed.set_author(name=ctx.author.name)

    await ctx.send(embed=embed)


@client.command()
async def john_china(ctx):
    await ctx.send("https://cdn.discordapp.com/attachments/792480412647161906/848385363709526046/video0_1.mp4")


@client.command()
async def translate(ctx, *, thingtotranslate):
    result = translator.translate(text=f'{thingtotranslate}', src='auto', dest='en')
    embed = discord.Embed(
        title="translation",
        color=discord.Colour.orange()
    )

    embed.set_footer(text="Note: This is not 100% correct so dont expect it to be exactly that")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))
    embed.add_field(name=f"From {result.src}", value=thingtotranslate)
    embed.add_field(name=f"To {result.dest}", value=result.text)

    if result is not None:
        await ctx.send(embed=embed)


@client.command()
async def translate_from(ctx, source, desti, *, thingtotranslate):
    result = translator.translate(text=f'{thingtotranslate}', src=f'{source}', dest=f'{desti}')
    embed = discord.Embed(
        title="translation",
        color=discord.Colour.orange()
    )

    embed.set_footer(text="Note: This is not 100% correct so dont expect it to be exactly that")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url_as(size=128))
    embed.add_field(name=f"From {result.src}", value=thingtotranslate)
    embed.add_field(name=f"To {result.dest}", value=result.text)

    if result is not None:
        await ctx.send(embed=embed)


@client.command()
async def im(ctx, *, thingtosearch):
    _search_params = {
        'q': f'{thingtosearch}',
        'num': 1,
        'safe': 'off',
        'fileType': 'jpg',
        'imgType': 'photo',
        'imgSize': 'imgSizeUndefined',
        'imgDominantColor': 'black',
        'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived'
    }

    thing = gis.search(search_params=_search_params)
    for image in gis.results():
        downloaded_result = image.download(os.path.dirname(__file__))


@client.command()
async def txt2img(ctx, *, thingtoput):
    r = requests.post(
        "https://api.deepai.org/api/text2img",
        data={
            'text': f'{thingtoput}',
        },
        headers={'api-key': 'd832cc77-92fb-4a09-895f-b9c1ec4a67b0'}
    )
    await ctx.send(r.json()['output_url'])

@client.command()
async def draw(ctx, *, whattotype):
        try:
            url = ctx.message.attachments[0].url


        except IndexError:
            await ctx.send("no attachements")
        else:
            if url[0:26] == "https://cdn.discordapp.com":
                r = requests.get(url, stream=True)
                imagename = str(uuid.uuid4()) + ".jpg"
                with open(imagename , 'wb') as out_file:
                    print("saving image" + imagename)
                    shutil.copyfileobj(r.raw, out_file)
                    font = ImageFont.truetype(r"C:\Users\tamim\PycharmProjects\the epic troll\impact.ttf", 30)
                    im = Image.open(imagename)
                    WIDTH, HEIGHT = im.size
                    d = ImageDraw.Draw(im)
                    width, height = d.textsize(whattotype, font=font)
                    points = [(WIDTH - width // 2), (HEIGHT - height // 2)]
                    d.text(((WIDTH - width)/2 + 30,(HEIGHT - height)/2 - 200), whattotype, fill="white", anchor="mt", font=font)
                    test_image = im.save("testimage.jpg", "JPEG")
                    await ctx.send(file=discord.File("testimage.jpg"))

# @client.command()
# async def punishment(ctx):
#   punishments = open("punishments.json")

TOKEN = os.environ["funnytoken"]

client.run(TOKEN)
