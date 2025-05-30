import disnake
from disnake.ext import commands, tasks
import os
import random
import time
import json
import datetime

intents = disnake.Intents.all()
# oops - ,test_guilds=[1373082837422444668]
bot = commands.Bot(command_prefix="cdc!",intents=intents)

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

GAMBLING_PPL = []

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

@bot.slash_command()
async def manual_wordgame_trigger(i,word=None):
    await trigger_wordgame(i.channel.id,word)

@bot.event
async def on_message(m: disnake.Message):
    await update_wordgames(m)
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

@bot.slash_command()
async def currency(i):
    pass

class CurrencyTransaction:
    def __init__(self,i):
        self.initial = i
        self.after = i
    def set_after(self,a):
        self.after = a
    def as_codeblock(self):
        global CURRENCY_MANAGER
        return f"`{CURRENCY_MANAGER.format_price(self.initial)} -> {CURRENCY_MANAGER.format_price(self.after)}`"

class CurrencyUser:
    def __init__(self,id):
        self.id = id
        self.money = 0
        self.inventory = []
        self.job = "basic"
        self.last_worked = 0
    def has_item(self,item):
        return item in self.inventory 
    def add_item(self,item):
        global CURRENCY_MANAGER
        self.inventory.append(item)
        CURRENCY_MANAGER.save()
    def remove_item(self,item):
        global CURRENCY_MANAGER
        self.inventory.remove(item)
        CURRENCY_MANAGER.save()
    def from_json(self,js):
        for key in js:
            self.__dict__[key] = js[key]
    def to_json(self):
        return json.dumps(self,default=lambda o: o.__dict__, sort_keys=True,indent=4)

class CurrencyManager:
    def __init__(self):
        self.data = []
        self.currency = "€cdc"
        self.try_load()
    
    def format_price(self,p):
        return f"{p}{self.currency}"

    def get_user(self,id):
        for user in self.data:
            if user.id == str(id):
                return user
        return self.create_data(id)
    
    def create_data(self,id):
        user = CurrencyUser(str(id))
        self.data.append(user)
        return user
    
    # wallet
    def set_ballance(self,id,amt):
        user = self.get_user(id)
        user.money = amt
        self.save()
        return user.money
    
    def update_ballance(self,id,amt):
        user = self.get_user(id)
        transaction = CurrencyTransaction(user.money)
        new = self.set_ballance(id,user.money+amt)
        transaction.set_after(new)
        return transaction

    #file
    def to_json(self):
        return json.dumps(self,default=lambda o: o.__dict__, sort_keys=True,indent=4)
    
    def save(self):
        file = open("./currency.json","w")
        c = self.to_json()
        file.write(c)
        file.close()
    
    def try_load(self):
        try:
            file = open("./currency.json","r")
            c = file.read()
            file.close()
            j = json.loads(c)
            for key in j:
                if key == "data":
                    for u in j[key]:
                        user = CurrencyUser(0)
                        user.from_json(u)
                        self.data.append(user)
                    continue
                self.__dict__[key] = j[key]

        except:
            print("loading defaults - currency")

class CurrencyJob:
    def __init__(self,name,display,wage):
        self.name = name
        self.display_name = display
        self.wage = wage
        self.required_items = []
    def add_required_item(self,item):
        self.required_items.append(item)
        return self


class CurrencyItem:
    def __init__(self,name,display,usable=False):
        self.name = name
        self.display_name = display
        self.usable = usable
        self.on_use = None
    def set_usage_callback(self,callback):
        self.on_use = callback

class CurrencyItemManager:
    def __init__(self):
        self.items = []
    def add_item(self,name,display,usable=False):
        job = CurrencyItem(name,display,usable)
        self.items.append(job)
        return job
    def get_item(self,i):
        for item in self.items:
            if item.name == i:
                return item
        return None     

class CurrencyJobManager:
    def __init__(self):
        self.jobs = []
        self.hour = 0
    def add_job(self,name,display,wage):
        job = CurrencyJob(name,display,wage)
        self.jobs.append(job)
        return job
    def get_job(self,j):
        for job in self.jobs:
            if job.name == j:
                return job
        return None     
    def hour_is(self,v):
        self.hour = v   

class CurrencyShopEntry:
    def __init__(self,name,price):
        self.name = name
        self.price = price

class CurrencyShop:
    def __init__(self):
        self.items = []
    def add_item(self,name,price):
        self.items.append(CurrencyShopEntry(name,price))
    def get_item(self,name):
        for item in self.items:
            if item.name == name:
                return item
        return None

def on_computer(user):
    return ["It bluescreened and rebooted, I guess you're too clumsy.",False]
def on_debt_shield(user):
    return ["Well, it's already applied.",False]
def on_debt_protector(user):
    if user.money >= 0:
        return ["But you weren't in debt.",False]
    CURRENCY_MANAGER.set_ballance(user.id,0)
    return [f"You've been saved from debt! Your balance is now {CURRENCY_MANAGER.format_price(0)}",True]

CURRENCY_MANAGER = CurrencyManager()
CURRENCY_SHOP = CurrencyShop()
CURRENCY_SHOP.add_item("computer",150)
CURRENCY_SHOP.add_item("msvs",35)
CURRENCY_SHOP.add_item("debt_protector",100)
CURRENCY_SHOP.add_item("debt_shield",1000)
CURRENCY_SHOP.add_item("g_syringe",1100)
JOB_MANAGER = CurrencyJobManager()
JOB_MANAGER.add_job("basic","Basic",12)
JOB_MANAGER.add_job("programmer","Software Engineer",120).add_required_item("computer").add_required_item("msvs")
JOB_MANAGER.add_job("doctor","Hospital Surgeon",500).add_required_item("g_syringe")
JOB_MANAGER.hour_is(5)
ITEM_MANAGER = CurrencyItemManager()
ITEM_MANAGER.add_item("poop_stain","Poop Stain",False)
ITEM_MANAGER.add_item("computer","Computer",True).set_usage_callback(on_computer)
ITEM_MANAGER.add_item("msvs","Microsoft Visual Studio",False)
ITEM_MANAGER.add_item("debt_protector","Debt Protector",True).set_usage_callback(on_debt_protector)
ITEM_MANAGER.add_item("debt_shield","Debt Shield",True).set_usage_callback(on_debt_shield)
ITEM_MANAGER.add_item("g_syringe","Golden Syringe",True)

@currency.sub_command()
async def gamble(i: disnake.ApplicationCommandInteraction):
    """Let's go gambling!"""
    global CURRENCY_MANAGER
    await i.send("*Spinning the wheel...*")
    time.sleep(0.5)
    user = CURRENCY_MANAGER.get_user(i.author.id)
    money = user.money
    min_boundary = -money
    max_boundary = money*2
    ultra_debt = False
    if money < 0:
        min_boundary = max_boundary*328923898
    if min_boundary == 0 and max_boundary == 0:
        max_boundary = 2000
    gamble = random.randint(min_boundary,max_boundary)
    if random.randint(1,5) == 2 and not user.has_item("debt_shield"):
        gamble = min_boundary*9
        ultra_debt = True
    str = CURRENCY_MANAGER.update_ballance(i.author.id,gamble)
    await i.edit_original_message(f"{':chart_with_upwards_trend: You got' if gamble > 0 else ':chart_with_downwards_trend: You lost'} {CURRENCY_MANAGER.format_price(abs(gamble))}\n-# {str.as_codeblock()} \n{'-# Woah! Stuck in debt while gambling? Use a **Debt Prodector** or buy the **Debt Shield** and NEVER go in debt again!' if ultra_debt == True else ''}")

@currency.sub_command()
async def balance(i:disnake.ApplicationCommandInteraction,u:disnake.Member=None):
    """Check yours or someone else's balance."""
    global CURRENCY_MANAGER
    if u == None:
        u = i.author
    user = CURRENCY_MANAGER.get_user(u.id)
    await i.send(f"""{f"{u.mention}'s" if u.id != i.author.id else "Your"} balance is {CURRENCY_MANAGER.format_price(user.money)}""")

@currency.sub_command()
async def pay(i:disnake.ApplicationCommandInteraction,u:disnake.Member,amt:int):
    """Pay someone."""
    if amt < 0:
        await i.send("You can't pay negative money")
        return
    global CURRENCY_MANAGER
    user1 = CURRENCY_MANAGER.get_user(i.author.id)
    if user1.money < amt:
        await i.send("You don't have enough money for this transaction.")
        return
    transaction1 = CURRENCY_MANAGER.update_ballance(i.author.id,-amt)
    transaction2 = CURRENCY_MANAGER.update_ballance(u.id,amt)
    await i.send(f"You paid {u.mention} {CURRENCY_MANAGER.format_price(amt)}\n-# Transactions made:\n-# {i.author.mention}: {transaction1.as_codeblock()}\n-# {u.mention}: {transaction2.as_codeblock()}")

@currency.sub_command()
async def work(i:disnake.ApplicationCommandInteraction):
    """Work."""
    global CURRENCY_MANAGER
    global JOB_MANAGER
    user = CURRENCY_MANAGER.get_user(i.author.id)
    job = JOB_MANAGER.get_job(user.job)
    time_now = datetime.datetime.now().timestamp()
    diff = time_now - user.last_worked
    if diff < JOB_MANAGER.hour:
        await i.send(f"You've only started working, wait for the hour to end ({round(JOB_MANAGER.hour-diff)} seconds)")
        return
    extra = random.randint(-round(job.wage/2),round(job.wage/2))
    transaction = CURRENCY_MANAGER.update_ballance(i.author.id,job.wage+extra)
    work_msgs = ["You worked tirelessly..","You worked.......","You went to work!"]
    await i.send(f"-# *{random.choice(work_msgs)}*\nYour **{job.display_name}** job has earned you {CURRENCY_MANAGER.format_price(job.wage+extra)}!\n-# {transaction.as_codeblock()}")
    user.last_worked = time_now

async def buy_autocomp(i:disnake.Interaction,current:str):
    global CURRENCY_SHOP
    global CURRENCY_MANAGER
    global ITEM_MANAGER
    items = []
    for item in CURRENCY_SHOP.items:
        items.append(ITEM_MANAGER.get_item(item.name))
    ret = []
    for item in items:
        if item.name.find(current) != -1 or current == "":
            price = CURRENCY_SHOP.get_item(item.name).price
            ret.append(f"{item.name} - {item.display_name}: {CURRENCY_MANAGER.format_price(price)}")
    return ret[:10]
@currency.sub_command()
async def buy(i:disnake.ApplicationCommandInteraction,item = commands.Param(autocomplete=buy_autocomp)):
   """Buy something from the shop."""
   global ITEM_MANAGER
   global CURRENCY_SHOP
   global CURRENCY_MANAGER
   d = item.split(" - ")
   item = CURRENCY_SHOP.get_item(d[0])
   if item == None:
       await i.send("Bad item")
       return
   item2 = ITEM_MANAGER.get_item(d[0])
   user = CURRENCY_MANAGER.get_user(i.author.id)
   if user.money < item.price:
       await i.send(f"You don't have enough money to buy **{item2.display_name}**!")
       return
   transaction = CURRENCY_MANAGER.update_ballance(i.author.id,-item.price)
   user.add_item(item.name)
   await i.send(f"You bought **{item2.display_name}** for {CURRENCY_MANAGER.format_price(item.price)}!\n-# {transaction.as_codeblock()}")

async def item_autocomp(i:disnake.Interaction,current:str):
    global ITEM_MANAGER
    global CURRENCY_MANAGER
    user = CURRENCY_MANAGER.get_user(i.author.id)
    mc = []
    for item in user.inventory:
        if item.find(current) != -1 or current == "":
            mc.append(item)
    ret = []
    for item in mc:
        item_data = ITEM_MANAGER.get_item(item)
        ret.append(f"{item_data.name} - {item_data.display_name}")
    return ret[:10]

async def item_autocomp_usable(i:disnake.Interaction,current:str):
    global ITEM_MANAGER
    global CURRENCY_MANAGER
    user = CURRENCY_MANAGER.get_user(i.author.id)
    mc = []
    for item in user.inventory:
        if item.find(current) != -1 or current == "":
            mc.append(item)
    ret = []
    for item in mc:
        item_data = ITEM_MANAGER.get_item(item)
        if not item_data.usable:
            continue
        ret.append(f"{item_data.name} - {item_data.display_name}")
    return ret[:10]

@currency.sub_command()
async def use_item(i:disnake.ApplicationCommandInteraction,item=commands.Param(autocomplete=item_autocomp_usable)):
    """Use an item."""
    d = item.split(" - ")
    global ITEM_MANAGER
    global CURRENCY_MANAGER
    item = ITEM_MANAGER.get_item(d[0])
    if item == None:
        await i.send("Bad item")
        return
    user = CURRENCY_MANAGER.get_user(i.author.id)
    if item.name not in user.inventory:
        await i.send("You don't have this item")
        return
    if not item.usable:
        await i.send("You can't use this item")
        return
    use = item.on_use(user)
    await i.send(f"-# *You used the **{item.display_name}**.*\n{use[0]}")
    if use[1]:
        user.remove_item(item.name)

@currency.sub_command()
async def give_item(i:disnake.ApplicationCommandInteraction,u:disnake.Member,item=commands.Param(autocomplete=item_autocomp)):
    """Give someone an item."""
    d = item.split(" - ")
    global ITEM_MANAGER
    global CURRENCY_MANAGER
    item = ITEM_MANAGER.get_item(d[0])
    if item == None:
        await i.send("Bad item")
        return
    user = CURRENCY_MANAGER.get_user(i.author.id)
    user2 = CURRENCY_MANAGER.get_user(u.id)
    if item.name not in user.inventory:
        await i.send("You don't have this item")
        return
    user.remove_item(item.name)
    user2.add_item(item.name)
    await i.send(f"You gave {u.mention} the **{item.display_name}**, you're so kind!")

@currency.sub_command()
async def inventory(i:disnake.ApplicationCommandInteraction):
    """Check your inventory."""
    global CURRENCY_MANAGER
    global ITEM_MANAGER
    user = CURRENCY_MANAGER.get_user(i.author.id)
    ret = "Your items:"
    ret_initial = ret
    footer = "You can use /currency use_item on some of these!"
    for it in user.inventory:
        item = ITEM_MANAGER.get_item(it)
        ret = ret + "\n" + "- " + f"**{item.display_name}** ({item.name})"
    if ret == ret_initial:
        ret = "You have no items."
        footer = None
    embed = disnake.Embed(title="Inventory",description=ret,color=disnake.Color.gold())
    if footer != None:
        embed.set_footer(text=footer)
    await i.send(embed=embed)

@currency.sub_command()
async def shop(i:disnake.ApplicationCommandInteraction):
    """Check the item shop."""
    global CURRENCY_SHOP
    global CURRENCY_MANAGER
    global ITEM_MANAGER
    items = CURRENCY_SHOP.items
    ret = "Available items:"
    for it in items:
        item = ITEM_MANAGER.get_item(it.name)
        ret = ret + "\n" + "- " + f"**{item.display_name}** ({item.name}) - {CURRENCY_MANAGER.format_price(it.price)}"
    embed = disnake.Embed(title="Shop",description=ret,color=disnake.Color.purple())
    balance = CURRENCY_MANAGER.format_price(CURRENCY_MANAGER.get_user(i.author.id).money)
    embed.set_footer(text=f"Your balance: {balance} | Use /currency buy to buy an item from here!")
    await i.send(embed=embed)

async def job_autocomplete(i:disnake.ApplicationCommandInteraction,curr:str):
    global JOB_MANAGER
    ret = []
    for job in JOB_MANAGER.jobs:
        if job.name.find(curr) != -1 or curr == "":
            ret.append(f"{job.name} - {job.display_name}")
    return ret

@currency.sub_command()
async def job_apply(i:disnake.ApplicationCommandInteraction,job=commands.Param(autocomplete=job_autocomplete)):
    """Apply for a job"""
    global JOB_MANAGER
    global ITEM_MANAGER
    global CURRENCY_MANAGER
    p = job.split(" - ")
    job = JOB_MANAGER.get_job(p[0])
    if job == None:
        await i.send("bad job")
        return
    user = CURRENCY_MANAGER.get_user(i.author.id)
    to_have = []
    for item in job.required_items:
        if item not in user.inventory:
            to_have.append(item)
    if len(to_have) > 0:
        str = "You're missing the following items required for this job:"
        for item in to_have:
            data = ITEM_MANAGER.get_item(item)
            str = str + "\n" + "- " + f"**{data.display_name}** ({data.name})"
        embed = disnake.Embed(title="Rejected",description=str,color=disnake.Color.red())
        embed.set_footer(text="Please buy them and run this command again if you'd like to reapply.")
        await i.send(embed=embed)
        return
    user.job = job.name
    embed = disnake.Embed(title="Accepted",description=f"You've been accepted for the **{job.display_name}** ({job.name}) job!",color=disnake.Color.green())
    embed.set_footer(text="Use /currency work to work.")
    await i.send(embed=embed)
    
@currency.sub_command()
async def leaderboard(i:disnake.ApplicationCommandInteraction,debt:bool=False):
    """View the leaderboard."""
    global CURRENCY_MANAGER
    embed = disnake.Embed(title=f"{'Currency' if not debt else 'Debt'} Leaderboard",colour=disnake.Color.blurple())
    leaderboard = sorted(CURRENCY_MANAGER.data,key=lambda k: k.money)
    if not debt:
        leaderboard.reverse()
    placement = 1
    placement_mod = 1
    my_placement = placement
    lb_limit = 10
    shown = 1
    for place in leaderboard:
        if shown <= lb_limit:
            embed.add_field(f"{placement}.",f"<@{place.id}>: `{CURRENCY_MANAGER.format_price(place.money)}`",inline=False)
        if place.id == str(i.author.id):
            my_placement = placement
        placement += placement_mod
        shown += 1
    embed.set_footer(text=f"Your placement is #{my_placement} "+f"{f'| Balance {CURRENCY_MANAGER.format_price(CURRENCY_MANAGER.get_user(i.author.id).money)}' if my_placement > lb_limit else ''}")
    await i.send(embed=embed)
    

bot.run(os.environ["CDC_TOKEN"])
