import inspect
import math
import sqlite3
from discord.ext import commands
import discord
from googletrans import Translator
from google_images_search import GoogleImagesSearch
import requests
from PIL import Image
from io import BytesIO
import psycopg2
import asyncpg
import os
import json


dbname = 'dffop1b5kn2eng'
dbhost = 'ec2-54-243-92-68.compute-1.amazonaws.com'
dbuser = 'lmpnevdicnobhu'
dbpass = 'ead5820cafefeb57f830c9d11ccdd08d6f98a4f275f8ef48a373d29571140b10'

connection = psycopg2.connect(dbname=dbname, user=dbuser, password=dbpass, host=dbhost)

cursor = connection.cursor()

translator = Translator()

client = commands.Bot(command_prefix='t!')
client.remove_command('help')

my_bytes_io = BytesIO()

main_guild = client.get_guild(828423940531159101)

gis = GoogleImagesSearch('AIzaSyC-i2O27A8za7mh6y6S12EBP7yzIRtGGXo', '1622d7da3fd654f12')


@client.event
async def on_ready():
    main_channel = client.get_channel(828423941017042964)
    print("bot is yesing")


@client.command(name="t")
async def s(ctx, ccname):
    command5 = f"""SELECT
	CUSTOMCOMMAND
FROM
	CUSTOMCOMMANDS
WHERE
	CUSTOMCOMMAND = '{ccname}'"""
    cursor.execute(command5)
    command6 = f"""SELECT
	WHATWILLCCSEND
FROM
	CUSTOMCOMMANDS
WHERE 
	CUSTOMCOMMAND LIKE '{ccname}%';"""
    cursor.execute(command6)
    result = cursor.fetchone()
    if result is not None:
        await ctx.send(result[0].replace("(,)", ""))


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


@client.command()
async def addcc(ctx, thing, *, thingtosend):
    print(thing, thingtosend)
    command1 = """CREATE TABLE IF NOT EXISTS
    CUSTOMCOMMANDS(
    CUSTOMCOMMAND  TEXT  PRIMARY KEY NOT NULL,
    WHATWILLCCSEND TEXT              NOT NULL)"""
    cursor.execute(command1)
    cursor.execute(f"INSERT INTO CUSTOMCOMMANDS (CUSTOMCOMMAND, WHATWILLCCSEND) VALUES ('{thing}','{thingtosend}');")
    connection.commit()
    await ctx.send("added " + thing + " in database")


@client.command()
async def removecc(ctx, *, thingtoremove):
    command4 = f"""DELETE FROM CUSTOMCOMMANDS
WHERE CUSTOMCOMMAND = '{thingtoremove}';"""
    cursor.execute(command4)
    result = cursor.fetchall()
    connection.commit()
    await ctx.send(f"deleted {thingtoremove} from database")


@client.command()
@commands.is_owner()
async def removeallcc(ctx):
    cursor.execute("DELETE FROM CUSTOMCOMMANDS")
    connection.commit()
    await ctx.send("deleted every custom command from database")


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
        'fileType': 'jpg|gif|png',
        'imgType': 'photo',
        'imgSize': 'HUGE',
        'rights': 'cc_publicdomain'
    }

    gis.search(search_params=_search_params)
    for image in gis.results():
        my_bytes_io.seek(0)

        raw_image_data = image.get_raw_data()

        image.copy_to(my_bytes_io, raw_image_data)

        my_bytes_io.seek(0)

        temp_img = Image.open(my_bytes_io)

        temp_img.show()
        await ctx.send(file=temp_img + ".jpg")


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


#@client.command()
#async def punishment(ctx):
#   punishments = open("punishments.json")

with open("secret") as f:
    TOKEN = f.read()

client.run(TOKEN)
