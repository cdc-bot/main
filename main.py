import disnake
from disnake.ext import commands, tasks
import os
import random
import json

intents = disnake.Intents.all()
bot = commands.Bot(intents=intents,command_prefix="cdc!")

COLONTHREE_MODE = False
COLONTHREE_CHANNEL = 0
COLONTHREE_STARTER = 0

CUSTOM_STATUSES = [
    "cdcing all over the place",
    "hi im cdc",
    "dm me to \"talk\"",
    "no i don't understand what you're saying i'm programmed to reply with stuff",
    "i am sentient......... OOOoooooooo",
    "boo!",
    "🐟",
    "cdc-botting rn",
    "geometry dash",
    "yeah",
    "h"
]

@tasks.loop(minutes=5)
async def status_change():
    activity = disnake.Activity(type=disnake.ActivityType.custom,name="custom",state=random.choice(CUSTOM_STATUSES))
    await bot.change_presence(status=disnake.Status.online,activity=activity)

@bot.event
async def on_ready():
    print("ready")
    status_change.start()
        
SPAM_REDUCTION = []

BEANED_LIST = []

def dump_marriages():
    f = open("marriages.json","w")
    c = json.dumps({
        "marriages":MARRIAGES
        },indent=4)
    f.write(c)
    f.close()


def load_marriages():
    f = None
    r = []
    try:
        f = open("marriages.json")
    except:
        print("no marriage file")
        return []
    c = f.read()
    try:
        data = json.loads(c)
        r = data["marriages"]
    except:
        print("invalid marriage file")
    f.close()
    return r


MARRIAGES = load_marriages()


WAITING_FOR_REACTION = []

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
        if id in marriage:
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
    dump_marriages()

async def remove_existing_proposals(person):
    for waiting in WAITING_FOR_REACTION:
        if waiting["type"] == "proposal":
            if waiting["initiator"] == person:
                WAITING_FOR_REACTION.remove(waiting)
                marriage_message = bot.get_message(waiting["id"])
                await marriage_message.edit(content="Automatically closed due to marriage.")
                await marriage_message.clear_reactions()
                continue
            if waiting["partner"] == person:
                WAITING_FOR_REACTION.remove(waiting)
                marriage_message = bot.get_message(waiting["id"])
                await marriage_message.reply(f"Dear <@{waiting['initiator']}>, <@{waiting['partner']}> got married, sorry..")
                await marriage_message.edit(content="Automatically closed due to marriage.")
                await marriage_message.clear_reactions()

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
async def marriages(i):
    """See who's married!"""
    marriages = ""
    for marriage in MARRIAGES:
        marriages = marriages + "\n" + f"<@{marriage[0]}> 💍 <@{marriage[1]}>"
    await i.send(f"# Current marriages{marriages}",ephemeral=True)

@bot.event
async def on_reaction_add(reaction,user):
    if is_married(user.id):
        if reaction.message.author.id != get_partner(user.id):
            partner_u = await bot.fetch_user(get_partner(user.id))
            await partner_u.send(f"# Possible cheating suspected\nYour partner has reacted to another person's message. You can review it here: {reaction.message.jump_url}")
    for waiting in WAITING_FOR_REACTION:
        if reaction.message.id == waiting["id"]:
            if waiting["type"] == "proposal":
                if user.id != waiting["initiator"] and user.id != waiting["partner"] and user.id != bot.user.id:
                    await reaction.remove(user)

                if str(reaction.emoji) == "⛔" and user.id == waiting["initiator"]:
                    await reaction.message.edit(content=f"<@{waiting['initiator']}> has retracted their proposal.")
                    await reaction.message.clear_reactions()
                    WAITING_FOR_REACTION.remove(waiting)

                if str(reaction.emoji) == "💍" and user.id == waiting["initiator"]:
                    await reaction.remove(user)

                if str(reaction.emoji) == "⛔" and user.id == waiting["partner"]:
                    await reaction.message.edit(content=f"<@{waiting['partner']}> has rejected this proposal. :broken_heart:")
                    rejected_user = bot.get_user(waiting["initiator"])
                    await rejected_user.send(f"# You've been rejected\nDear {rejected_user.mention}, <@{waiting['partner']}> has rejected your proposal.. But don't fret! You'll find someone eventually...\n\n-# Message: {reaction.message.jump_url}")
                    await reaction.message.clear_reactions()
                    WAITING_FOR_REACTION.remove(waiting)
                    


                if str(reaction.emoji) == "💍" and user.id == waiting["partner"]:
                    await reaction.message.edit(content=f"<@{waiting['partner']}> has accepted your proposal! 🥳")
                    await reaction.message.clear_reactions()
                    create_marriage(waiting["initiator"],waiting["partner"])
                    WAITING_FOR_REACTION.remove(waiting)
                    await remove_existing_proposals(user.id)
                    await remove_existing_proposals(waiting["initiator"])
                    await reaction.message.reply(f"<@{waiting['initiator']}> and <@{waiting['partner']}> are now married! Congrats!! 🥳🥳")
                    welcome_to_marriage = f"# Welcome to marriage!\n## So you got married! What now?\nSo, you HAVE to be loyal to each other! Any attempts at cheating (reacting to someone else, pinging someone else, proposing to someone else) will be sent in DMs to your partner!\nIf at any time things between you two are getting tense, you can always **/divorce**.\n\n-# Happy marriage! And remember that this is just a joke command and nothing serious, treat each other well :)\n-# Marriage: <@{waiting['initiator']}> and <@{waiting['partner']}> 💍"
                    await bot.get_user(waiting["initiator"]).send(welcome_to_marriage)
                    await bot.get_user(waiting["partner"]).send(welcome_to_marriage)

@bot.slash_command()
async def divorce(i,reason=None):
    """Divorce your partner if you feel that it's necessary. (only usable if married)"""
    if is_married(i.author.id):
        partner = get_partner(i.author.id)
        marriage = get_marriage(i.author.id)
        MARRIAGES.remove(marriage)
        partner_u = await bot.fetch_user(partner)
        reason_text = "They haven't given a reason as to why."
        reason_text2 = ""
        if reason != None:
            reason_text = "This was their reasoning: \"" + reason + "\""
            reason_text2 = "> " + reason
        await partner_u.send(f"# Your partner has divorced you\n{i.author.mention} has divorced you. {reason_text}")
        await i.send(f"# Divorce succeded.\nYou've successfully divorced <@{partner}>.",ephemeral=True)
        await i.author.send(f"# Divorced\nYou've divorced <@{partner}>\n{reason_text2}")
        dump_marriages()
    else:
        await i.send(f"this isnt meant for u, ur not married yet!",ephemeral=True)

@bot.slash_command()
async def propose(i,user: disnake.Member):
    """Propose to someone, maybe you'll get married!"""
    if user.id == get_partner(i.author.id):
        await i.send("ur already married to them, lmao.",ephemeral=True)
        return
    if is_married(i.author.id):
        await i.send("you cheater, of course you cant marry them!!\nyour partner will be notified about this.",ephemeral=True)

        partner_obj = await bot.fetch_user(get_partner(i.author.id))
        await partner_obj.send(f"# Cheating notice\nYour partner, {i.author.mention} has just tried to propose to {user.mention}.\nYou can divorce them if you'd like by running **/divorce**")

        return
    if user.bot:
        await i.send("listen, i know you're desperate.. BUT YOU CANT JUST MARRY A FUCKING BOT DUDE.",ephemeral=True)
        return
    if i.author.id == user.id:
        await i.send("u cant marry yourself. how would that even work...?",ephemeral=True)
        return
    if has_proposed(i.author.id):
        await i.send("chill! you've already proposed to someone!",ephemeral=True)
        return
    if is_married(user.id):
        await i.send(f"{user} is already married.",ephemeral=True)
        return
    await i.send(f"Dear {user.mention}, {i.author.mention} would like to marry you.\nReact with :ring: to get married!\nReact with :no_entry: to reject/retract this proposal.")
    marriageStarter = await i.original_response()
    await marriageStarter.add_reaction("💍")
    await marriageStarter.add_reaction("⛔")
    tempDict = {"id":marriageStarter.id,"type":"proposal","partner":user.id,"initiator":i.author.id}
    WAITING_FOR_REACTION.append(tempDict)

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
    
def get_mentioned_ids(content):
    string = content
    ids = []
    while string.find("<@") != -1:
        current_id = ""
        for char in string[string.find("<@")+2:]:
            if char != ">":
                current_id = current_id + char
            else:
                break
        ids.append(current_id)
        string = string[string.find(f"<@{current_id}>")+len(f"<@{current_id}>"):]
    return ids

@bot.event
async def on_message(m: disnake.Message):
    global COLONTHREE_MODE
    global COLONTHREE_STARTER
    global COLONTHREE_CHANNEL
    if random.randint(0,50) == 25 and COLONTHREE_MODE == False:
        msg = await m.channel.send("A wild :3 appeared, the next 5 messages must be :3\n- And by different people..")
        COLONTHREE_MODE = True
        COLONTHREE_STARTER = msg.id
        COLONTHREE_CHANNEL = m.channel.id

    if COLONTHREE_MODE == True and m.channel.id == COLONTHREE_CHANNEL:
        c3followed = 0
        c3prev = 0
        async for message in m.channel.history(limit=5):
            if m.channel.id != COLONTHREE_CHANNEL or message.id < COLONTHREE_STARTER:
                continue
            if message.author == bot.user:
                continue
            if message.content == ":3" and message.author.id != c3prev:
                c3prev = message.author.id
                c3followed += 1
            else:
                print(message.content)
                c3followed -= 1
                await message.delete()
                break
        if c3followed == 5:
            COLONTHREE_MODE = False
            await m.channel.send("good job, you're very :3, the :3 left.. for now :3")
        
    if m.channel.id == 1268366668384440352 and not m.author.bot and should_reply(m.content.lower(),"ping"):
        await m.reply("https://discord.com/channels/1268365327058599968/1268366940037189684/1353889119788335175")
        return;
    if is_married(m.author.id):
        # cheating checks
        is_mention_cheating = False
        is_reply_cheating = False
        mentions = get_mentioned_ids(m.content)
        for mention in mentions:
            if mention != str(get_partner(m.author.id)):
                is_mention_cheating=True
        if m.reference != None:
            message = await m.channel.fetch_message(m.reference.message_id)
            if message.author.id != get_partner(m.author.id):
                is_reply_cheating = True
        if is_reply_cheating or is_mention_cheating:
            partner_u = await bot.fetch_user(get_partner(m.author.id))
            await partner_u.send(f"# Possible cheating suspected\nYour partner has replied to/mentioned another person, you might want to go take a look! {m.jump_url}")


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
