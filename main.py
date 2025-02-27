import disnake
from disnake.ext import commands
import os
import random

intents = disnake.Intents.all()
bot = commands.Bot(intents=intents,command_prefix="cdc!")

@bot.event
async def on_ready():
    print("ready")
SPAM_REDUCTION = []

BEANED_LIST = []

FORMS = {
        "hi":["hi","hello"],
        "how are you":["how are you","how r you","how are u","how r u"],
        "im good":["im good","i'm good","im ok","i'm ok","i'm alright","im alright"],
        ":3":[":3","uwu","owo",":3c"],
        "im bad":["im bad","i'm bad","im horrible","i'm horrible"],
        "fuck you":["fuck you","screw you","you suck","i hate you"],
        "i love you":["i love you","ily","i love yoy"],
        "geming furry?":["geming furry?","is geming a furry"]
        }

RESPONSES = {
        "hi":["hi!","hello","yo! how are you?"],
        "how are you":["im good","im fine","im doing ok."],
        "im good":["glad to hear!","stay happy!"],
        ":3":[":3","FURRY!!!",":33",":cat2:"],
        "im bad":["aww... i hope you feel better soon","hopefully the people here cheer you up!!","hey.. please, for me, turn that frown upside down!!!","oh damn."],
        "fuck you":["stfu","oh shut up.","why so rude?","im a bot bro"],
        "i love you":["it is not mutual","me too","😘", "i remember one day maybe was the first day of my life, you came to my heart my eyes wide open to you"],
        "geming furry?":["idk","no?","maybe","yea :3","bro","hi tjc"]
}
NO_RESPONSE_SET = "i apologise, but i don't really know how to respond to that..\nmaybe i will be able to in the future though!"

def should_reply(content,to_detect):
    content = str(content)
    is_phrase = (to_detect.find(" ") != -1)
    if is_phrase:
        if content.find(to_detect) != -1:
            return True
    else:
        for word in content.split(" "):
            if word == to_detect:
                return True
    return False


@bot.slash_command()
async def who_am_i(i):
    """Tells you what the bot "thinks" you are."""
    random_responses = ["idk","a person","someone",i.author,"ur cool","ur stupid","a programmer.. maybe",":baby:"]
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
    

@bot.event
async def on_message(m):
    if m.author.id in BEANED_LIST:
        await m.add_reaction("🫘")
        BEANED_LIST.remove(m.author.id)
    reply = False
    confusedReact = False
    if m.reference != None:
        message = await m.channel.fetch_message(m.reference.message_id)
        if message.author == bot.user:
            reply = True
        if message.content == NO_RESPONSE_SET:
            confusedReact = True
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
                        await m.reply(random.choice(RESPONSES[key]))
                        break
                if hasReplied:
                    break
            if hasReplied == False:
                if not confusedReact:
                    if m.author.id not in SPAM_REDUCTION:
                        await m.reply(NO_RESPONSE_SET)
                        SPAM_REDUCTION.append(m.author.id)
                    else:
                        await m.add_reaction("😕")
                else:
                    try:
                        await m.add_reaction("😕")
                    except:
                        print(f"couldnt react to {m.author}, probably blocked")

bot.run(os.environ["CDC_TOKEN"])
