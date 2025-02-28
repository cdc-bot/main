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

MARRIAGES = []

WAITING_FOR_REACTION = []

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

def has_proposed(id):
    for waiting in WAITING_FOR_REACTION:
        if waiting["initiator"] == id:
            return True
    return False

def is_married(id):
    for marriage in MARRIAGES:
        if id in marriage:
            return True
    return False

def get_partner(id):
    for marriage in MARRIAGES:
        for partner in marriage:
            if partner != id:
                return partner
    return None

def get_marriage(id):
    for marriage in MARRIAGES:
        for partner in marriage:
            if partner == id:
                return marriage
    return None


def create_marriage(person1,person2):
    MARRIAGES.append([person1,person2])

async def remove_existing_proposals(person):
    for waiting in WAITING_FOR_REACTION:
        if waiting["type"] == "proposal":
            if waiting["initiator"] == person:
                WAITING_FOR_REACTION.remove(waiting)
                continue
            if waiting["partner"] == person:
                WAITING_FOR_REACTION.remove(waiting)
                marriage_message = bot.get_message(waiting["id"])
                await marriage_message.reply(f"Dear <@{waiting["initiator"]}>, <@{waiting["partner"]}> got married, sorry..")
                await marriage_message.delete()

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

@bot.event
async def on_reaction_add(reaction,user):
    for waiting in WAITING_FOR_REACTION:
        if reaction.message.id == waiting["id"]:
            if waiting["type"] == "proposal":
                if str(reaction.emoji) == "💍" and user.id == waiting["partner"]:
                    create_marriage(waiting["initiator"],waiting["partner"])
                    WAITING_FOR_REACTION.remove(waiting)
                    await remove_existing_proposals(user.id)
                    await reaction.message.reply(f"<@{waiting["initiator"]}> and <@{waiting["partner"]}> are now married! Congrats!! 🥳🥳")


@bot.slash_command()
async def divorce(i,reason=None):
    if is_married(i.author.id):
        partner = get_partner(i.author.id)
        marriage = get_marriage(i.author.id)
        MARRIAGES.remove(marriage)
        partner_u = await bot.fetch_user(partner)
        reason_text = "They haven't given a reason as to why."
        if reason != None:
            reason_text = "This was their reasoning: \"" + reason + "\""
        await partner_u.send(f"# Your partner has divorced you\n{i.author.mention} has divorced you. {reason_text}")
        await i.send(f"# Divorce succeded.\nYou've successfully divorced <@{partner}>.",ephemeral=True)
    else:
        await i.send(f"this isnt meant for u, ur not married yet!",ephemeral=True)


        
                    

@bot.slash_command()
async def propose(i,user: disnake.Member):
    if user.bot:
        await i.send("listen, i know you're desperate.. BUT YOU CANT JUST MARRY A FUCKING BOT DUDE.",ephemeral=True)
        return
    if i.author.id == user.id:
        await i.send("u cant marry yourself. how would that even work...?",ephemeral=True)
        return
    if has_proposed(i.author.id):
        await i.send("chill! you've already proposed to someone!",ephemeral=True)
        return
    if is_married(i.author.id):
        await i.send("you cheater, of course you cant marry them!!\nyour partner will be notified about this.",ephemeral=True)

        partner_obj = await bot.fetch_user(get_partner(i.author.id))
        await partner_obj.send(f"# Cheating notice\nYour partner, {i.author.mention} has just tried to propose to {user.mention}.\nYou can divorce them if you'd like by running **/divorce**")

        return
    if is_married(user.id):
        await i.send(f"{user} is already married.",ephemeral=True)
        return
    await i.send(f"Dear {user.mention}, {i.author.mention} would like to marry you.\nReact with :ring: to get married!")
    marriageStarter = await i.original_response()
    await marriageStarter.add_reaction("💍")
    tempDict = {"id":marriageStarter.id,"type":"proposal","partner":user.id,"initiator":i.author.id}
    WAITING_FOR_REACTION.append(tempDict)

    

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
