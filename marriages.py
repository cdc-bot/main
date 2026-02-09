import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import preferences

bot = None

class Availability:
    available = False
    cheating = False
    reason = ""
    def __init__(self):
        self.available = False
        self.cheating = False
        self.reason = ""

class MarriageProposal:
    proposer = 0
    recipient = 0
    channel_id = 0
    message_id = 0
    processing = False
    def __init__(self):
        self.proposer = 0
        self.recipient = 0
        self.channel_id = 0
        self.message_id = 0
        self.processing = False

WAITING_FOR_REACTION: list[MarriageProposal] = []

class Marriage:
    def __init__(self,people):
        self.people = people
        self.cheating = {}
    
    def has_user(self,id) -> bool:
        for person in self.people:
            if person == id:
                return True
        return False
    
    def all_polyamorous(self) -> bool:
        for person in self.people:
            if not preferences.manager.get_user(person).polyamorous.get():
                return False
        return True
    
    def register_cheating(self,user):
        try:
            self.cheating[str(user)] += 1
        except:
            self.cheating[str(user)] = 1
        MARRIAGE_MANAGER.save()

    def flush_cheating(self):
        for cheating_entry in self.cheating:
            self.cheating[cheating_entry] = 0
        MARRIAGE_MANAGER.save()
    
    def is_full(self) -> bool:
        poly = self.all_polyamorous()
        if poly:
            return False
        elif len(self.people) < 2:
            return False
        else:
            return True
    
    def add_user(self,id) -> bool:
        full = self.is_full()
        if not full:
            self.people.append(id)
            MARRIAGE_MANAGER.save()
            return True
        else:
            return False
        
    def get_user_partners(self,user) -> list[int]:
        ret = []
        for member in self.people:
            if member != user:
                ret.append(member)
        return ret
    
    def remove_user(self,id) -> bool:
        if self.has_user(id):
            self.people.remove(id)
            if len(self.people) <= 1:
                MARRIAGE_MANAGER.marriages.remove(self)
            MARRIAGE_MANAGER.save()
            return True
        else:
            return False
        
    def to_string(self) -> str:
        i = 0
        ret = ""
        for person in self.people:
            separator = " :ring: "
            if i == len(self.people) - 1:
                separator = ""
            ret = ret + f"<@{person}>" + separator
            i += 1
        return ret


    def from_data(self,data):
        for field in data:
            value = data[field]
            self.__dict__[field] = value
    def to_dict(self) -> dict:
        ret = {}
        for field in self.__dict__:
            value = self.__dict__[field]
            ret[field] = value
        return ret

class MarriageManager:
    def __init__(self):
        global MARRIAGE_MANAGER
        MARRIAGE_MANAGER = self
        self.marriages = []
        self.try_load()
        self.save()
    
    def add_marriage(self,user1,user2) -> bool:
        user1_married = self.is_married(user1)
        user2_married = self.is_married(user2)
        if user1_married:
            marriage = self.get_marriage(user1)
            self.save()
            return marriage.add_user(user2)
        elif user2_married:
            marriage = self.get_marriage(user2)
            self.save()
            return marriage.add_user(user1)
        else:
            marriage = Marriage([user1,user2])
            self.marriages.append(marriage)
            self.save()
            return True
    
    def is_married(self,user) -> bool:
        for marriage in self.marriages:
            if marriage.has_user(user):
                return True
        return False
    
    def get_marriages(self) -> list[Marriage]:
        return self.marriages
    
    async def send_to_partners(self,user,msg) -> None:
        partners = self.get_marriage(user).get_user_partners(user)
        for partner in partners:
            user = await bot.fetch_user(partner)
            await user.send(msg)

    async def send_cheating_msg_to_partners(self,user,msg) -> None:
        marriage = self.get_marriage(user)
        partners = marriage.get_user_partners(user)
        marriage.register_cheating(user)
        for partner in partners:
            if not preferences.manager.get_user(partner).defer_cheating_alerts.get() and len(marriage.people)<=2:
                user = await bot.fetch_user(partner)
                await user.send(msg)
    
    def get_marriage(self,user) -> Marriage:
        for marriage in self.marriages:
            if marriage.has_user(user):
                return marriage
        return None
    
    def partners_polyamorous(self,user) -> bool:
        partners = self.get_marriage(user).get_user_partners(user)
        for partner in partners:
            poly = preferences.manager.get_user(partner).polyamorous.get()
            if not poly:
                return False
        return True
    
    def will_be_poly(self,user1,user2) -> bool:
        if self.is_married(user1) or self.is_married(user2):
            return True
        return False
    
    def can_marry(self,proposer,user) -> Availability:
        result = Availability()
        result.available = True
        proposer_poly = preferences.manager.get_user(proposer).polyamorous.get()
        user_poly = preferences.manager.get_user(user).polyamorous.get()
        user_proposable = not preferences.manager.get_user(user).disable_proposals.get()
        proposer_married = self.is_married(proposer)
        user_married = self.is_married(user)
        user_obj = bot.get_user(user)

        if proposer_married:
            if user in self.get_marriage(proposer).get_user_partners(proposer):
                result.available = False
                result.reason = "they're already your partner"
                return result
            if not self.partners_polyamorous(proposer):
                result.available = False
                result.reason = "you're a cheater"
                result.cheating = True
                return result
            if not user_poly:
                result.available = False
                result.reason = "they're not polyamorous"
                return result
            if not proposer_poly:
                result.available = False
                result.reason = "you're not polyamorous"
                return result

        if not user_proposable:
            result.available = False
            result.reason = "they have disallowed people from proposing to them"
            return result

        for proposal in WAITING_FOR_REACTION:
            if proposal.proposer == proposer:
                result.available = False
                result.reason = "you've already made a proposal"
                return result
        
        if user_obj != None:
            if user_obj.bot:
                result.available = False
                result.reason = "they're a bot bro"
                return result
        
        if proposer == user:
            result.available = False
            result.reason = "you can't marry yourself"
            return result
        
        if user_married:
            if not proposer_poly:
                result.available = False
                result.reason = "you're not polyamorous"
                return result
            if not user_poly:
                result.available = False
                result.reason = "they're not polyamorous"
                return result
            if not self.get_marriage(user).all_polyamorous():
                result.available = False
                result.reason = "not all of their partners are polyamorous"
                return result
        
        if user_married and proposer_married:
            result.available = False
            result.reason = "both of you are married"
            return result
        
        return result




    def save(self):
        file = open("./marriages.json","w")
        c = self.to_json()
        file.write(c)
        file.close()
    def try_load(self):
        try:
            file = open("./marriages.json","r")
            c = file.read()
            file.close()
            j = json.loads(c)
            for k in j:
                v = j[k]
                if k == "marriages":
                    for marriage in v:
                        _marriage = Marriage([])
                        _marriage.from_data(marriage)
                        self.marriages.append(_marriage)
                else:
                    self.__dict__[k] = v
        except:
            print("loading default config - marriages")
    def to_json(self):
        dict = {}
        for key in self.__dict__:
            value = self.__dict__[key]
            if key == "marriages":
                array = []
                for marriage in value:
                    array.append(marriage.to_dict())
                dict[key] = array
            else:
                dict[key] = value
        return json.dumps(dict,indent=4)
    
MARRIAGE_MANAGER = MarriageManager()
MARRIAGE_MANAGER.save()
    
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
    marriages = app_commands.Group(name="marriages",description="Marriage commands.")
    @marriages.command()
    async def view(self,i: discord.Interaction):
        """See who's married!"""
        header = "# Current marriages"
        body = ""
        for marriage in MARRIAGE_MANAGER.get_marriages():
            body += "\n" + marriage.to_string()
        await i.response.send_message(header+body,ephemeral=True)

            

    @marriages.command()
    async def request_cheating_stats(self,i:discord.Interaction):
        """Request cheating statistics for the last 24h"""
        if not MARRIAGE_MANAGER.is_married(i.user.id):
            await i.response.send_message("you're not married",ephemeral=True)
        send_cheating_stats(MARRIAGE_MANAGER.get_marriage(i.user.id),i.user.id)
        await i.response.send_message("cheating stats sent")
    
    @marriages.command()
    @app_commands.describe(reason="The reason for the divorce")
    async def divorce(self,i,reason: str=None):
        """Divorce your partner if you feel that it's necessary. (only usable if married)"""
        if MARRIAGE_MANAGER.is_married(i.user.id):
            marriage = MARRIAGE_MANAGER.get_marriage(i.user.id)
            marriage.remove_user(i.user.id)
            partners = marriage.get_user_partners(i.user.id)
            reason_text = "They haven't given a reason as to why."
            reason_text2 = ""
            if reason != None:
                reason_text = "This was their reasoning: \"" + reason + "\""
                reason_text2 = "> " + reason
            for partner in partners:
                partner_u = await bot.fetch_user(partner)
                await partner_u.send(f"# Your partner has divorced you\n{i.user.mention} has divorced you. {reason_text}")
            divorcee = f"<@{partner}>"
            if len(partners) > 1:
                divorcee = "your partners and left the marriage."
            await i.response.send_message(f"# Divorce succeded.\nYou've successfully divorced {divorcee}.",ephemeral=True)
            await i.user.send(f"# Divorced\nYou've divorced {divorcee}\n{reason_text2}")
        else:
            await i.response.send_message(f"this isnt meant for u, ur not married yet!",ephemeral=True)

    @marriages.command()
    @app_commands.describe(user="The person to propose to")
    async def propose(self,i: discord.Interaction,user: discord.Member):
        """Propose to someone, maybe you'll get married!"""
        availability = MARRIAGE_MANAGER.can_marry(i.user.id,user.id)
        if availability.available:
            greeting = f"Dear {user.mention}, {i.user.mention} would like"
            action = " to marry you."
            if MARRIAGE_MANAGER.will_be_poly(i.user.id,user.id):
                if MARRIAGE_MANAGER.is_married(user.id):
                    action = " to join your marriage."
                if MARRIAGE_MANAGER.is_married(i.user.id):
                    action = " you to join their marriage."
            instruction_ring = "React with :ring: to accept this proposal."
            instruction_stop = "React with :no_entry: to reject/retract it."
            full_message = greeting+action+"\n"+instruction_ring+"\n"+instruction_stop

            await i.response.send_message(full_message)
            message = await i.original_response()
            await message.add_reaction("💍")
            await message.add_reaction("⛔")

            proposal = MarriageProposal()
            proposal.proposer = i.user.id
            proposal.recipient = user.id
            proposal.channel_id = message.channel.id
            proposal.message_id = message.id
            proposal.processing = False

            WAITING_FOR_REACTION.append(proposal)
        else:
            await i.response.send_message(availability.reason,ephemeral=True)
            if availability.cheating:
                await MARRIAGE_MANAGER.send_cheating_msg_to_partners(i.user.id,f"# Cheating notice\nYour partner, {i.user.mention}, has attempted to cheat on you by proposing to {user.mention}.")
            
    
        


    @commands.Cog.listener()
    async def on_reaction_add(self,reaction: discord.Reaction,user: discord.User):
        proposal = None
        for p in WAITING_FOR_REACTION:
            if p.message_id == reaction.message.id and not p.processing:
                proposal = p
                break
        if proposal == None:
            # not a proposal message
            marriage = MARRIAGE_MANAGER.get_marriage(user.id)
            
            if marriage != None:
                if not reaction.message.author.bot and reaction.message.author.id not in marriage.get_user_partners(user.id):
                    await MARRIAGE_MANAGER.send_cheating_msg_to_partners(user.id,f"# Possible cheating suspected\nYour partner, <@{user.id}>, has reacted to another person outside of your marriage's message. You can review it here: {reaction.message.jump_url}")
                
            return
        
        is_accept = reaction.emoji == "💍"
        is_deny = reaction.emoji == "⛔"
        by_proposer = user.id == proposal.proposer
        by_recipient = user.id == proposal.recipient
        proposal_message = reaction.message

        if by_recipient:
            if is_accept:
                proposal.processing = True
                poly = False
                invited = MARRIAGE_MANAGER.is_married(proposal.proposer)
                await proposal_message.edit(content="proposal accepted")
                consequence = f"<@{proposal.proposer}> and <@{proposal.recipient}> are now married!"
                if MARRIAGE_MANAGER.will_be_poly(proposal.proposer,proposal.recipient):
                    poly = True
                    if invited:
                        consequence = f"<@{proposal.recipient}> has joined <@{proposal.proposer}>'s marriage!"
                    else:
                        consequence = f"<@{proposal.proposer}> has joined <@{proposal.recipient}>'s marriage!"
                await proposal_message.reply(f"Proposal accepted! {consequence}")
                await proposal_message.clear_reactions()
                success = MARRIAGE_MANAGER.add_marriage(proposal.proposer,proposal.recipient)
                resulting_marriage = MARRIAGE_MANAGER.get_marriage(proposal.proposer)
                WAITING_FOR_REACTION.remove(proposal)

                welcome_to_marriage = f"# Welcome to marriage!\n## So you got married! What now?\nSo, you HAVE to be loyal to each other! Any attempts at cheating (reacting to someone else, pinging someone else, proposing to someone else) will be sent in DMs to your partner!\nIf at any time things between you two are getting tense, you can always **/divorce**.\n\n-# Happy marriage! And remember that this is just a joke command and nothing serious, treat each other well :)\n-# Marriage: {resulting_marriage.to_string()} 💍"

                #remove active proposals for non polyamorous couples
                if not poly:
                    for p in WAITING_FOR_REACTION:
                        if p.recipient == proposal.proposer or p.recipient == proposal.recipient:
                            channel = await bot.fetch_channel(p.channel_id)
                            message = await channel.fetch_message(p.message_id)
                            await message.reply(f"Sorry, <@{p.proposer}>, <@{p.recipient}> got married.")
                            await message.edit(content="Proposal canceled!")
                            await message.clear_reactions()
                            WAITING_FOR_REACTION.remove(p)
                        if p.proposer == proposal.proposer or p.proposer == proposal.recipient:
                            channel = await bot.fetch_channel(p.channel_id)
                            message = await channel.fetch_message(p.message_id)
                            await message.edit(content="Proposal canceled!")
                            await message.clear_reactions()
                            WAITING_FOR_REACTION.remove(p)
                    proposeruser = await bot.fetch_user(proposal.proposer)
                    await proposeruser.send(welcome_to_marriage)
                    await MARRIAGE_MANAGER.send_to_partners(proposeruser.id,welcome_to_marriage)
                else:
                    proposeruser = await bot.fetch_user(proposal.proposer)
                    otheruser = proposal.proposer
                    if invited:
                        otheruser = proposal.recipient
                        proposeruser = await bot.fetch_user(proposal.recipient)
                    await proposeruser.send(welcome_to_marriage)
                    await MARRIAGE_MANAGER.send_to_partners(proposeruser.id,f"# New member in marriage!\n <@{otheruser}> has joined your marriage! {proposal_message.jump_url}")
                proposal.processing = False
                return
            if is_deny:
                await proposal_message.reply(f"Sorry <@{proposal.proposer}>, your proposal was declined.")
                await proposal_message.edit(content="Proposal declined")
                await proposal_message.clear_reactions()
                WAITING_FOR_REACTION.remove(proposal)
                proposal.processing = False
                return
        elif by_proposer and is_deny:
            proposal.processing = True
            await proposal_message.edit(content="Proposal retracted")
            await proposal_message.clear_reactions()
            WAITING_FOR_REACTION.remove(proposal)
            proposal.processing = False
            return
        else:
            await reaction.remove(user)
            proposal.processing = False
            return
        
    @commands.Cog.listener()
    async def on_message(self,m: discord.Message):
        marriage = MARRIAGE_MANAGER.get_marriage(m.author.id)
        if marriage != None:
            partners = marriage.get_user_partners(m.author.id)
            is_mention_cheating = False
            is_reply_cheating = False
            mentions = get_mentioned_ids(m.content)
            for mention in mentions:
                if int(mention) not in partners:
                    is_mention_cheating=True
            if m.reference != None:
                try:
                    message = await m.channel.fetch_message(m.reference.message_id)
                    if message.author.id not in partners and not message.author.bot:
                        is_reply_cheating = True
                except:
                    print("failed to get reply")
            if is_mention_cheating or is_reply_cheating:
                await MARRIAGE_MANAGER.send_cheating_msg_to_partners(m.author.id,f"# Possible cheating suspected\nYour partner, <@{m.author.id}>, has replied to/mentioned another person outside of your marriage, you might want to go take a look! {m.jump_url}")

async def send_cheating_stats(marriage: Marriage,member:int):
    deferred = preferences.manager.get_user(member).defer_cheating_alerts.get()
    if deferred or len(marriage.people) > 2:
        header = "# Cheating stats for the last 24h"
        embed = discord.Embed(title=None)
        bad_relationship_score = 0
        total_cheats = 0
        for cheater in marriage.cheating:
            value = marriage.cheating[cheater]
            if cheater != str(member):
                total_cheats += value
                plural = "s"
                if value == 1:
                    plural = ""
                embed.add_field(inline=True,name="Cheater",value=f"> <@{cheater}>\n> Cheated: {value} time{plural}")
        if total_cheats > 50:
            bad_relationship_score = 1
        if total_cheats > 100:
            bad_relationship_score = 2
        if total_cheats > 200:
            bad_relationship_score = 3
        if total_cheats > 500:
            bad_relationship_score = 4
        if total_cheats > 1000:
            bad_relationship_score = 5
        message_text = header+f"\n- Total cheating incidents: {total_cheats}\n- Bad relationship score: {bad_relationship_score}/5"
        user = await bot.fetch_user(member)
        try:
            await user.send(content=message_text,embed=embed)
        except:
            await user.send(content=message_text+"\n-# (no one cheated)",embed=embed)

@tasks.loop(hours=24)
async def send_out_deferred_cheating():
    all_marriages = MARRIAGE_MANAGER.get_marriages()
    for marriage in all_marriages:
        for member in marriage.people:
            await send_cheating_stats(marriage,member)
        marriage.flush_cheating()
                

async def setup(_bot:commands.Bot):
    global bot
    bot = _bot
    await bot.add_cog(Marriages())
    send_out_deferred_cheating.start()