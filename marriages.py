import disnake
from disnake.ext import commands, tasks
import json
import preferences

bot = None

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

WAITING_FOR_REACTION = []

MARRIAGES = load_marriages()

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

def get_partner_legacy(id):
    partners = get_partners(id)
    try:
        return partners[0]
    except:
        return None

def get_partners(id):
    ret = []
    marriage = get_marriage(id)
    for partner in marriage:
        if partner != id:
            ret.append(id)
    return ret

def get_marriage(id):
    for marriage in MARRIAGES:
        for partner in marriage:
            if partner == id:
                return marriage
    return None

def create_marriage(person1,person2):
    MARRIAGES.append([person1,person2])
    dump_marriages()

def add_to_marriage(person1,person2):
    marriage = get_marriage(person1)
    marriage.append(person2)
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

class Marriages(commands.Cog):
    @commands.slash_command()
    async def marriages(self,i:disnake.ApplicationCommandInteraction):
        pass
    @marriages.sub_command()
    async def view(self,i):
        """See who's married!"""
        marriages = ""
        for marriage in MARRIAGES:
            marriages = marriages + "\n" + f"<@{marriage[0]}> 💍 <@{marriage[1]}>"
        await i.send(f"# Current marriages{marriages}",ephemeral=True)
    
    @marriages.sub_command()
    async def divorce(self,i,reason=None):
        """Divorce your partner if you feel that it's necessary. (only usable if married)"""
        if is_married(i.author.id):
            partner = get_partner_legacy(i.author.id)
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

    @marriages.sub_command()
    async def propose(self,i,user: disnake.Member):
        """Propose to someone, maybe you'll get married!"""
        if user.id == get_partner_legacy(i.author.id):
            await i.send("ur already married to them, lmao.",ephemeral=True)
            return
        if is_married(i.author.id):
            await i.send("you cheater, of course you cant marry them!!\nyour partner will be notified about this.",ephemeral=True)

            partner_obj = await bot.fetch_user(get_partner_legacy(i.author.id))
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


    @commands.Cog.listener()
    async def on_reaction_add(self,reaction,user):
        if is_married(user.id):
            if reaction.message.author.id != get_partner_legacy(user.id):
                partner_u = await bot.fetch_user(get_partner_legacy(user.id))
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
    @commands.Cog.listener()
    async def on_message(self,m: disnake.Message):
        if is_married(m.author.id):
            # cheating checks
            is_mention_cheating = False
            is_reply_cheating = False
            mentions = get_mentioned_ids(m.content)
            for mention in mentions:
                if mention != str(get_partner_legacy(m.author.id)):
                    is_mention_cheating=True
            if m.reference != None:
                message = await m.channel.fetch_message(m.reference.message_id)
                if message.author.id != get_partner_legacy(m.author.id):
                    is_reply_cheating = True
            if is_reply_cheating or is_mention_cheating:
                partner_u = await bot.fetch_user(get_partner_legacy(m.author.id))
                await partner_u.send(f"# Possible cheating suspected\nYour partner has replied to/mentioned another person, you might want to go take a look! {m.jump_url}")

def setup(_bot:commands.Bot):
    global bot
    bot = _bot
    bot.add_cog(Marriages())