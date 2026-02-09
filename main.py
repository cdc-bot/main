import disnake
from disnake.ext import commands, tasks
import os
import random
import time
import json
import datetime
import logging

test = None
try:
    if (os.environ["CDC_DEBUG"] == "1"):
        test = [1373082837422444668]
        logging.basicConfig(level=logging.DEBUG)
except:
    print("cdc-bot is normal")

intents = disnake.Intents.all()
# oops - 

bot = commands.Bot(command_prefix="cdc!",intents=intents,test_guilds=test)

CUSTOM_STATUSES = [
    "meow",
    ":3",
    "j",
    "h"
]

@tasks.loop(minutes=5)
async def status_change():
    activity = disnake.Activity(type=disnake.ActivityType.custom,name="custom",state=random.choice(CUSTOM_STATUSES))
    await bot.change_presence(status=disnake.Status.online,activity=activity)

@bot.event
async def on_ready():
    print("ready")
    bot.load_extension("preferences")
    bot.load_extension("currency")
    bot.load_extension("marriages")
    bot.load_extension("wordgame")
    status_change.start()
        
SPAM_REDUCTION = []

BEANED_LIST = []

GAMBLING_PPL = []

# funny game

WORDGAME_INSTANCES = []

class Wordgame:
    def __init__(self):
        self.channel = 0
        self.messages = []
        self.word = ""
        self.times = random.randint(2,10)
        self.starter = -1

async def trigger_wordgame(channel_id:int,word=None):
    if wordgame_exists(channel_id):
        return
    global WORDGAME_INSTANCES
    words = ["balls"]
    if word != None:
        words = [word]
    game = Wordgame()
    game.channel = channel_id
    game.word = random.choice(words)

    # send starter
    channel = bot.get_channel(channel_id)
    msg = await channel.send(f"a wild {game.word} has appeared! the next {game.times} messages must be {game.word}.")
    game.starter = msg.id
    WORDGAME_INSTANCES.append(game)

def wordgame_exists(channel_id:int):
    global WORDGAME_INSTANCES
    for game in WORDGAME_INSTANCES:
        if game.channel == channel_id:
            return True
    return False

async def stop_wordgame(channel_id:int):
    global WORDGAME_INSTANCES
    for game in WORDGAME_INSTANCES:
        if game.channel == channel_id:
            # send ender
            channel = bot.get_channel(channel_id)
            WORDGAME_INSTANCES.remove(game)
            await channel.send(f"good job! you're all very {game.word}, the {game.word} left.")
            break

async def update_wordgames(message:disnake.Message):
    global WORDGAME_INSTANCES
    for game in WORDGAME_INSTANCES:
        if game.channel == message.channel.id:
            if message.id <= game.starter:
                continue
            if len(game.messages) != 0:
                if game.messages[len(game.messages)-1].author.id == message.author.id:
                    await message.delete()
                    continue
            if message.content.lower() != game.word.lower() or message.author.bot:
                await message.delete()
                continue
            game.messages.append(message)
            if len(game.messages) >= game.times:
                await stop_wordgame(game.channel)
                continue

FORMS = {
        "hi":["hi","hello"],
        "how are you":["how are you","how r you","how are u","how r u"],
        "im good":["im good","i'm good","im ok","i'm ok","i'm alright","im alright"],
        ":3":[":3","uwu","owo",":3c","nya","cat","kitty"],
        "im bad":["im bad","i'm bad","im horrible","i'm horrible"],
        "fuck you":["fuck you","screw you","you suck","i hate you","kys"],
        "i love you":["i love you","ily","i love yoy"],
        "geming furry?":["geming furry?","is geming a furry"],
        "marry me":["marry me","marry you","marry u","kiss me","hug me","fuck me"],
        "yay":["yay","yippee","yaay","🥳"],
        "what":["what","huh","wtf","what the fuck"],
        "no":["no","nah","nope","ur gay","you're gay","homosexual"],
        "do you like cheese":["do you like cheese","do u like cheese"],
        "ur hot":["ur hot","you're hot","ur pretty","you're pretty","you're kinda hot"],
        "skill issue":["skill issue"],
        "np":["np","no problem","you're welcome","ur welcome"]
        }

RESPONSES = {
        "hi":["hi!","hello","yo! how are you?"],
        "how are you":["im good","im fine","im doing ok."],
        "im good":["glad to hear!","stay happy!"],
        ":3":[":3","FURRY!!!",":33",":cat2:"],
        "im bad":["aww... i hope you feel better soon","hopefully the people here cheer you up!!","hey.. please, for me, turn that frown upside down!!!","oh damn."],
        "fuck you":["stfu","oh shut up.","why so rude?","im a bot bro"],
        "i love you":["it is not mutual","me too","😘", "i remember one day maybe was the first day of my life, you came to my heart my eyes wide open to you"],
        "geming furry?":["idk","no?","maybe","yea :3","bro","hi tjc"],
        "marry me":["uhh..","man, im a bot, i dont know anything about these topics","no thanks 💀","uh.. i cant","ok!!!!","sure, cmere bb","heeellll naww","😳","..oh?","huuh 🧐🧐","i literally cant.","😏😏"],
        "yay":["yeeee!!!",":D","yippeee!!!!!!!!!",":colonThreeCat:\nif only i had that emoji.."],
        "what":["what are you confused about","?","huh","what","what?","i said nothing wrong.","i said what i said","u heard that right."],
        "no":["ok then","okay","oka","o","fine"],
        "do you like cheese":["yeah","yep, its tasty","yuh uh","yes.",":white_check_mark:"],
        "ur hot":["ty","i know","thanks!!","eeeh... okay??"],
        "skill issue":["kys","kill yourself","die","ok vro","fucking kill yourself"],
        "np":["ye ye ye ye","okii","lol",":3",":D"]
}
NO_RESPONSE_SET = ":fish:"

def should_reply(content,to_detect):
    content = " " + str(content) + " "
    is_phrase = (to_detect.find(" ") != -1)
    if is_phrase:
        if content.find(" "+to_detect+" ") != -1:
            return True
    else:
        for word in content.split(" "):
            if word == to_detect:
                return True
    return False

@bot.slash_command()
async def opinion(i):
    """Tells you what the bot "thinks" you are."""
    if i.author.id == 708750647847157880:
        await i.send("oki",ephemeral=True)
        exit()
    random_responses = ["idk","ur a person","ur someone",f"ur {i.author}","ur cool","ur stupid","ur a programmer.. maybe",":baby:"]
    await i.send(random.choice(random_responses))

@bot.slash_command()
async def bean(i, user: disnake.Member):
    """Bean someone!"""
    if user == bot.user:
        if i.author.id not in BEANED_LIST:
            BEANED_LIST.append(i.author.id)
            await i.send("YOU THOUGHT YOU COULD BEAN ME? WELL GUESS WHAT?! IM GONNA BEAN YOU!!!!")
        else:
                         await i.send("i would have an epic monologue about you beaning me but ur already beaned :/")
        return
    if user.id in BEANED_LIST:
        await i.send("theyre already beaned, chill.",ephemeral=True)
        return
    BEANED_LIST.append(user.id)
    await i.send(f"{user.mention} beaned!")

@bot.slash_command()
async def manual_wordgame_trigger(i,word=None):
    await i.channel.send(f"{i.author.mention} has started a wordgame!")
    await trigger_wordgame(i.channel.id,word)

@bot.event
async def on_message(m: disnake.Message):
    await update_wordgames(m)

    if m.author.id in BEANED_LIST:
        await m.add_reaction("<:bean:1345818012879552605>")
        BEANED_LIST.remove(m.author.id)
    

    reply = False
    confusedReact = False
    useSend = False
    if m.reference != None:
        message = await m.channel.fetch_message(m.reference.message_id)
        if message.author == bot.user:
            reply = True
        if message.content == NO_RESPONSE_SET and message.author == bot.user:
            confusedReact = True
    
    if type(m.channel) == disnake.DMChannel:
        useSend = True
        reply = True
    

    if m.content.find(bot.user.mention) != -1 or reply == True:
        if not  m.author.bot:
            hasReplied = False
            for key in RESPONSES:
                forms = FORMS[key]
                for form in forms:
                    if should_reply(m.content.lower(),form):
                        hasReplied = True
                        if m.author.id in SPAM_REDUCTION:
                            SPAM_REDUCTION.remove(m.author.id)
                        if not useSend:
                            await m.reply(random.choice(RESPONSES[key]))
                        else:
                            await m.channel.send(random.choice(RESPONSES[key]))
                        break
                if hasReplied:
                    break
            # NO_RESPONSE_SET used here
            if hasReplied == False:
                if not confusedReact:
                    if m.author.id not in SPAM_REDUCTION:
                        if not useSend:
                            rand = random.randint(1,5)
                            if rand != 2:
                                await m.reply(NO_RESPONSE_SET)
                            else:
                                await m.reply(f"\"{m.content}\" :nerd:",allowed_mentions=disnake.AllowedMentions.none)
                        else:
                            rand = random.randint(1,5)
                            if rand != 2:
                                await m.channel.send(NO_RESPONSE_SET)
                            else:
                                await m.channel.send(f"\"{m.content}\" :nerd:")
                        SPAM_REDUCTION.append(m.author.id)
                    else:
                        await m.add_reaction("😕")
                else:
                    try:
                        await m.add_reaction("😕")
                    except:
                        print(f"couldnt react to {m.author}, probably blocked")    

bot.run(os.environ["CDC_TOKEN"])
