import asyncio
import inspect
import math
import random
import sqlite3
import time
import aiohttp
import datetime
import warnings
import discord
from nextcord.ext import commands
from nextcord.ext.commands import MissingPermissions, MissingRequiredArgument
import nextcord
from googletrans import Translator
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import psycopg2
import asyncpg
import os
import json
from google_images_search import GoogleImagesSearch
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

warnings.filterwarnings("ignore", category=DeprecationWarning)
intents = nextcord.Intents.all()
client = commands.Bot(command_prefix=["t!"], intents=intents)
client.remove_command('help')
client.session = aiohttp.ClientSession()

my_bytes_io = BytesIO()

main_guild = client.get_guild(828423940531159101)

gis = GoogleImagesSearch(os.environ["thing"],os.environ["thingy"])


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


async def timeout_user(*, user_id: int, guild_id: int, until):
    headers = {"Authorization": f"Bot {client.http.token}"}
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
    timeout = (datetime.datetime.utcnow() + datetime.timedelta(minutes=until)).isoformat()
    json = {'communication_disabled_until': timeout}
    async with client.session.patch(url, json=json, headers=headers) as session:
        if session.status in range(200, 299):
            return True
        return False


#@client.event
#async def on_message_edit(before, after):
#    logs_channel = client.get_channel(845049306242613298)
#    if before.author == client.user: return
#    if before.author.bot: return
#    if before.content == after.content: return
#    if before.attachments: return
#    embed = nextcord.Embed(color=nextcord.Color.orange())
#    embed.set_author(name=before.author.name, icon_url=before.author.avatar.url)
#    embed.add_field(name="Before:", value=before.content)
#    embed.add_field(name="After:", value=after.content)
#    await logs_channel.send(embed=embed)
#
#
#@client.event
#async def on_message_delete(before):
#    logs_channel = client.get_channel(845049306242613298)
#    if before.author == client.user: return
#    if before.author.bot: return
#    if before.attachments:
#        embed = nextcord.Embed(color=nextcord.Color.red())
#        embed.set_author(name=before.author.name, icon_url=before.author.avatar.url)
#        embed.add_field(name="Deleted message (Contains attachment(s)):", value=before.attachments[0])
#        await logs_channel.send(embed=embed)
#    else:
#        embed = nextcord.Embed(color=nextcord.Color.red())
#        embed.set_author(name=before.author.name, icon_url=before.author.avatar.url)
#        embed.add_field(name="Deleted message:", value=before.content)
#        await logs_channel.send(embed=embed)


@client.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx: commands.Context, member: nextcord.Member, until: int = 5, *, reason=None):
    if member == ctx.author:
        return await ctx.send("{} You cannot mute yourself.".format(ctx.author.mention))
    handshake = await timeout_user(user_id=member.id, guild_id=ctx.guild.id, until=until)
    print(reason, member.id)
    if handshake:
        try:
            command1 = f"""CREATE TABLE IF NOT EXISTS
                            MUTES_{ctx.guild.id} (
                            REASON  TEXT    PRIMARY KEY  NOT NULL,
                            ID      NUMERIC              NOT NULL,
                            TIME    TEXT                 NOT NULL
                            )"""
            cursor.execute(command1)
            command2 = f"INSERT INTO MUTES_{ctx.guild.id} VALUES ('{reason}', '{member.id}', '{until}');"
            cursor.execute(command2)
            connection.commit()
            return await ctx.send(f"Successfully muted user for {until} minutes.")
        except DatabaseError:
            cursor.execute("rollback;")

        # return await ctx.send("cannot add mute because tamim is retarded and he is trying to fix the database")
    await ctx.send("Something went wrong")

@client.command()
async def mutes(ctx, member: discord.Member):
    try:
        cursor.execute(f"""SELECT REASON,TIME FROM MUTES_{ctx.guild.id} WHERE ID = '{member.id}';""")
        mutesOfPerson = cursor.fetchall()
        embed = nextcord.Embed(title=f"{member.name}#{member.discriminator}'s mutes", color=discord.Color.orange())
        timeOfMute = cursor.fetchall()
        for i in mutesOfPerson:
                embed.add_field(name=f'Reason: {i[0]}', value=f'Duartion: {i[1]} minutes.', inline=False)
        print(mutesOfPerson)
        await ctx.send(embed=embed)
    except DatabaseError:
        cursor.execute("rollback;")



@client.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx: commands.Context, member: nextcord.Member):
    handshake = await timeout_user(user_id=member.id, guild_id=ctx.guild.id, until=0)
    if handshake:
        return await ctx.send(f"Successfully unmuted user.")
    await ctx.send("Something went wrong")


@mute.error
@unmute.error
async def kick_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You do not have the required perms to do that")
    elif isinstance(error, MissingRequiredArgument):
        embed = nextcord.Embed(title="Timeout Command",
                               description="A command that can be used to timeout users with the new timeout feature from discord",
                               color=nextcord.Color.orange())
        embed.add_field(name="Usage:", value="t!mute (userid or user here) (time in minutes)", inline=False)
        embed.add_field(name="Example 1:", value="t!mute @tamim#7304", inline=False)
        embed.add_field(name="(if you put no time in the 3rd arguement then it will be defaulted to 5 minutes)",
                        value="h", inline=False)
        embed.add_field(name="Example 2:", value="t!mute @tamim#7304 10", inline=False)
        embed.set_footer(text="This was made because you are missing some arguements.")
        await ctx.send(embed=embed)


@client.event
async def on_message(message):
    logs_channel = client.get_channel(845049306242613298)
    if message.content == "t!": return
    if message.content.startswith("t!"):
        try:
            command5 = f"""SELECT
	    CUSTOMCOMMAND
    FROM    
	    CUSTOMCOMMANDS_{message.guild.id}
   WHERE
	    CUSTOMCOMMAND = '{message.content.replace("t!", "")}'"""
            cursor.execute(command5)
            command6 = f"""SELECT
	    WHATWILLCCSEND
    FROM    
	    CUSTOMCOMMANDS_{message.guild.id}
    WHERE 
	    CUSTOMCOMMAND LIKE '{message.content.replace("t!", "")}%';"""
            cursor.execute(command6)
            result = cursor.fetchone()
            if result is not None:
                await message.channel.send(result[0].replace("(,)", ""))
        except DatabaseError:
            cursor.execute("rollback;")

    if "pls pfp" in message.content or "plz pfp" in message.content:
        imagename = str(uuid.uuid4())
        #  images = gis.search(search_params=_search_params, custom_image_name=imagename)
        randomnumber = random.randint(0, 12)
        print(randomnumber)
        # gis.results()[randomnumber].download(os.path.dirname(__file__))
        list_of_files = glob.glob(os.path.dirname(__file__) + "\*")
        latest_file = max(list_of_files, key=os.path.getctime)
        await message.channel.send(file=nextcord.File(latest_file))

    await client.process_commands(message=message)


# @client.command(name="t")
# async def s(ctx, ccname):
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
    embed = nextcord.Embed(
        title='Ping',
        description=f"The ping is: `{math.floor(client.latency * 1000)}ms`",
        color=nextcord.Colour.orange()
    )

    embed.set_footer(text="i am racist")
    embed.set_image(
        url="https://media.discordapp.net/attachments/824625614312046592/844570716250963978/caption-5-1.gif")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)


@client.command()
async def allcc(ctx):
    try:
        cursor.execute(f"SELECT CUSTOMCOMMAND FROM CUSTOMCOMMANDS_{ctx.guild.id}")
        allccs = cursor.fetchall()
        embed = nextcord.Embed(
            title="All Custom Commands",
            description=allccs,
            color=nextcord.Colour.orange()
        )

        embed.set_footer(text=f"Number of custom commands is: {len(allccs)}")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/824625614312046592/844570716250963978/caption-5-1.gif")

        await ctx.send(embed=embed)
    except DatabaseError:
        cursor.execute("rollback;")


@client.command()
async def addcc(ctx, thing, *, thingtosend):
    print(thing, thingtosend)
    try:
        command1 = f"""CREATE TABLE IF NOT EXISTS
        CUSTOMCOMMANDS_{ctx.guild.id}(
        CUSTOMCOMMAND  TEXT  PRIMARY KEY NOT NULL,
        WHATWILLCCSEND TEXT              NOT NULL)"""
        cursor.execute(command1)
        cursor.execute(
            f"INSERT INTO CUSTOMCOMMANDS_{ctx.guild.id} (CUSTOMCOMMAND, WHATWILLCCSEND) VALUES ('{thing}','{thingtosend}');")
        connection.commit()
        await ctx.send("added " + thing + " in database")
    except DatabaseError:
        cursor.execute("rollback;")


@client.command()
async def removecc(ctx, *, thingtoremove):
    if ctx.author.guild_permissions.manage_messages or ctx.author.id == 756504591725756537:
        try:
            command4 = f"""DELETE FROM CUSTOMCOMMANDS_{ctx.guild.id} WHERE CUSTOMCOMMAND LIKE '{thingtoremove}%';"""
            cursor.execute(command4)
            connection.commit()
            await ctx.send(f"deleted {thingtoremove} from database")
        except DatabaseError:
            cursor.execute("rollback;")
    else:
        await ctx.send(
            "you do not have the required premissions to remove a custom command. please tell someone who has manage messages perms to delete it and give a good reason to why")


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
    embed = nextcord.Embed(
        title="Help",
        description="Use t!help to find out about all the commands",
        color=nextcord.Colour.orange()
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
    embed = nextcord.Embed(
        title="translation",
        color=nextcord.Colour.orange()
    )

    embed.set_footer(text="Note: This is not 100% correct so dont expect it to be exactly that")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name=f"From {result.src}", value=thingtotranslate)
    embed.add_field(name=f"To {result.dest}", value=result.text)

    if result is not None:
        await ctx.send(embed=embed)


@client.command()
async def translate_from(ctx, source, desti, *, thingtotranslate):
    result = translator.translate(text=f'{thingtotranslate}', src=f'{source}', dest=f'{desti}')
    embed = nextcord.Embed(
        title="translation",
        color=nextcord.Colour.orange()
    )

    embed.set_footer(text="Note: This is not 100% correct so dont expect it to be exactly that")
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.add_field(name=f"From {result.src}", value=thingtotranslate)
    embed.add_field(name=f"To {result.dest}", value=result.text)

    if result is not None:
        await ctx.send(embed=embed)


@client.command()
async def im(ctx, *, thingtosearch):
    _search_params = {
        'q': f'{thingtosearch}',
        'num': 100,
        #'fileType': 'jpg|gif|png',
       # 'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
       # 'safe': 'off',
       # 'imgType': 'imgTypeUndefined',
       # 'imgSize': 'imgSizeUndefined',
       # 'imgDominantColor': 'imgDominantColorUndefined',
       # 'imgColorType': 'color|gray|mono|trans|imgColorTypeUndefined'
    }
    page = 0
    userid = str(ctx.author.id)
    thing = gis.search(search_params=_search_params)
    msg = await ctx.send(embed=discord.Embed(title="Search result:", description=(str(page + 1) + " out of " + str(len(gis.results()))), color=discord.Color.red())
                         .set_image(url=gis.results()[0].url)
                         .add_field(name="Link:", value=gis.results()[0].referrer_url))
    await msg.add_reaction("⬅️")
    first_time = True
    await msg.add_reaction("➡️")
    previuspage = "⬅️"
    nextpage = "➡️"
    loopclose = 0

    def checkforreaction(reaction, user):
        return str(user.id) == userid and str(reaction.emoji) in [previuspage, nextpage]

    while loopclose == 0:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=300, check=checkforreaction)
            if reaction.emoji == nextpage:
                    page += 1
            elif reaction.emoji == previuspage:
                    page -= 1
            await msg.edit(embed=discord.Embed(title="Search result:", description=(str(page + 1) + " out of " + str(len(gis.results()))), color=discord.Color.red())
                           .set_image(url=gis.results()[page].url)
                           .add_field(name="Link:", value=gis.results()[page].referrer_url))

        except asyncio.TimeoutError:
            loopclose = 1
        except IndexError:
            page = 0
            await msg.edit(embed=discord.Embed(title="Search result:", description=(str(page + 1) + " out of " + str(len(gis.results()))), color=discord.Color.red())
                           .set_image(url=gis.results()[0].url)
                           .add_field(name="Link:", value=gis.results()[page].referrer_url))


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
async def esnipe(ctx):
    guildid = str(ctx.guild.id)
    userid = str(ctx.author.id)
    previuspage = '⬅️'
    nextpage = '➡️'
    page = len(edited_messages_list)
    first_time = True
    msg = await ctx.send("Click the right arrow to go to the latest edit and the left arrow to go to the oldest")
    await msg.add_reaction(previuspage)
    await msg.add_reaction(nextpage)

    def checkforreaction(reaction, user):
        return str(user.id) == userid and str(reaction.emoji) in [previuspage, nextpage]

    loopclose = 0
    while loopclose == 0:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=300, check=checkforreaction)
            if reaction.emoji == nextpage:
                if first_time:
                    first_time = False
                    page = len(edited_messages_list) - 1
                    print(page)
                else:
                    page += 1
            elif reaction.emoji == previuspage:
                if first_time:
                    first_time = False
                    page = len(edited_messages_list) - len(edited_messages_list)
                else:
                    page -= 1
            await msg.edit(embed=discord.Embed(color=discord.Color.orange()) .add_field(name="Unedited message:", value=edited_messages_list[page]) .set_author(name=edited_messages_usernames[page], icon_url=edited_messages_avatarurl[page]) .set_footer(text="press the right arrow to go to the next edit and the left arrow to go to the previous edit"))

        except asyncio.TimeoutError:
            loopclose = 1
        except IndexError:
            await ctx.send("there are no more edits")
            loopclose = 1

@client.command()
async def snipe(ctx):
    guildid = str(ctx.guild.id)
    userid = str(ctx.author.id)
    previuspage = '⬅️'
    nextpage = '➡️'
    page = len(edited_messages_list)
    first_time = True
    msg = await ctx.send("Click the right arrow to go to the latest deleted message and the left arrow to go to the oldest")
    await msg.add_reaction(previuspage)
    await msg.add_reaction(nextpage)

    def checkforreaction(reaction, user):
        return str(user.id) == userid and str(reaction.emoji) in [previuspage, nextpage]

    loopclose = 0
    while loopclose == 0:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=300, check=checkforreaction)
            if reaction.emoji == nextpage:
                if first_time:
                    first_time = False
                    page = len(deleted_messages_list) - 1
                    print(page)
                else:
                    page += 1
            elif reaction.emoji == previuspage:
                if first_time:
                    first_time = False
                    page = len(deleted_messages_list) - len(deleted_messages_list)
                else:
                    page -= 1
            await msg.edit(embed=discord.Embed(color=discord.Color.orange()).add_field(name="Deleted message:",
                                                                                       value=deleted_messages_list[
                                                                                           page]).set_author(
                name=deleted_messages_usernames[page], icon_url=deleted_messages_avatarurl[page]).set_footer(
                text="press the right arrow to go to the next deleted message and the left arrow to go to the previous deleted messages"))

        except asyncio.TimeoutError:
            loopclose = 1
        except IndexError:
            await ctx.send("there are no more deleted messages")
            loopclose = 1
	
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
            with open(imagename, 'wb') as out_file:
                print("saving image" + imagename)
                shutil.copyfileobj(r.raw, out_file)
                font = ImageFont.truetype(r"C:\Users\tamim\PycharmProjects\the epic troll\impact.ttf", 30)
                im = Image.open(imagename)
                WIDTH, HEIGHT = im.size
                d = ImageDraw.Draw(im)
                width, height = d.textsize(whattotype, font=font)
                points = [(WIDTH - width // 2), (HEIGHT - height // 2)]
                d.text(((WIDTH - width) / 2 + 30, (HEIGHT - height) / 2 - 200), whattotype, fill="white", anchor="mt",
                       font=font)
                test_image = im.save("testimage.jpg", "JPEG")
                await ctx.send(file=nextcord.File("testimage.jpg"))


@client.command()
async def allbots(ctx):
    bots = len(ctx.guild.get_all_members)
    await ctx.send(bots)


# @client.command()
# async def punishment(ctx):
#   punishments = open("punishments.json")

TOKEN = os.environ["funnytoken"]

client.run(TOKEN)
