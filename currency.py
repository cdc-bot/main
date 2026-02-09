import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import time
import random
import datetime
import cdc_utils

bot = None

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
        return f"{cdc_utils.number_abbreviation.abbrevate(p)}{self.currency}"

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
    def set_balance(self,id,amt):
        user = self.get_user(id)
        user.money = amt
        self.save()
        return user.money
    
    def update_balance(self,id,amt):
        user = self.get_user(id)
        transaction = CurrencyTransaction(user.money)
        new = self.set_balance(id,user.money+amt)
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
def on_syringe(user):
    return ["You injected yourself with it.. But, nothing happened. Ow...",False]
def on_lie(user):
    user.add_item("lie")
    return ["You lied again.",False]
def on_debt_protector(user):
    if user.money >= 0:
        return ["But you weren't in debt.",False]
    CURRENCY_MANAGER.set_balance(user.id,0)
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
JOB_MANAGER.add_job("politician","Politician",500).add_required_item("lie").add_required_item("lie").add_required_item("lie").add_required_item("lie").add_required_item("lie").add_required_item("lie")
JOB_MANAGER.hour_is(5)
ITEM_MANAGER = CurrencyItemManager()
ITEM_MANAGER.add_item("poop_stain","Poop Stain",False)
ITEM_MANAGER.add_item("computer","Computer",True).set_usage_callback(on_computer)
ITEM_MANAGER.add_item("msvs","Microsoft Visual Studio",False)
ITEM_MANAGER.add_item("debt_protector","Debt Protector",True).set_usage_callback(on_debt_protector)
ITEM_MANAGER.add_item("debt_shield","Debt Shield",True).set_usage_callback(on_debt_shield)
ITEM_MANAGER.add_item("g_syringe","Golden Syringe",True).set_usage_callback(on_syringe)
ITEM_MANAGER.add_item("lie","Lie",True).set_usage_callback(on_lie)

async def buy_autocomp(i:discord.Interaction,current:str):
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
            choice_str = f"{item.name} - {item.display_name}: {CURRENCY_MANAGER.format_price(price)}"
            choice = app_commands.Choice(name=choice_str,value=choice_str)
            ret.append(choice)
    return ret[:10]

async def item_autocomp(i:discord.Interaction,current:str):
    global ITEM_MANAGER
    global CURRENCY_MANAGER
    user = CURRENCY_MANAGER.get_user(i.user.id)
    mc = []
    for item in user.inventory:
        if item.find(current) != -1 or current == "":
            mc.append(item)
    ret = []
    for item in mc:
        item_data = ITEM_MANAGER.get_item(item)
        choice_str = f"{item_data.name} - {item_data.display_name}"
        choice = app_commands.Choice(name=choice_str,value=choice_str)
        ret.append(choice)
    return ret[:10]

async def item_autocomp_usable(i:discord.Interaction,current:str):
    global ITEM_MANAGER
    global CURRENCY_MANAGER
    user = CURRENCY_MANAGER.get_user(i.user.id)
    mc = []
    for item in user.inventory:
        if item.find(current) != -1 or current == "":
            mc.append(item)
    ret = []
    for item in mc:
        item_data = ITEM_MANAGER.get_item(item)
        if not item_data.usable:
            continue
        choice_str = f"{item_data.name} - {item_data.display_name}"
        choice = choice = app_commands.Choice(name=choice_str,value=choice_str)
        ret.append(choice)
    return ret[:10]

async def job_autocomplete(i:discord.Interaction,curr:str):
    global JOB_MANAGER
    ret = []
    for job in JOB_MANAGER.jobs:
        if job.name.find(curr) != -1 or curr == "":
            choice_str = f"{job.name} - {job.display_name}"
            choice = app_commands.Choice(name=choice_str,value=choice_str)
            ret.append(choice)
    return ret

class Currency(commands.Cog):
    currency = app_commands.Group(name="currency",description="Currency commands")

    @currency.command()
    async def gamble(self,i: discord.Interaction):
        """Let's go gambling!"""
        global CURRENCY_MANAGER
        await i.response.send_message("*Spinning the wheel...*")
        time.sleep(0.5)
        user = CURRENCY_MANAGER.get_user(i.user.id)
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
        str = CURRENCY_MANAGER.update_balance(i.user.id,gamble)
        await i.edit_original_response(content=f"{':chart_with_upwards_trend: You got' if gamble > 0 else ':chart_with_downwards_trend: You lost'} {CURRENCY_MANAGER.format_price(abs(gamble))}\n-# {str.as_codeblock()} \n{'-# Woah! Stuck in debt while gambling? Use a **Debt Prodector** or buy the **Debt Shield** and NEVER go in debt again!' if ultra_debt == True else ''}")

    @currency.command()
    async def balance(self,i:discord.Interaction,u:discord.Member=None):
        """Check yours or someone else's balance."""
        global CURRENCY_MANAGER
        if u == None:
            u = i.user
        user = CURRENCY_MANAGER.get_user(u.id)
        await i.response.send_message(f"""{f"{u.mention}'s" if u.id != i.user.id else "Your"} balance is {CURRENCY_MANAGER.format_price(user.money)}""")

    @currency.command()
    async def pay(self,i:discord.Interaction,u:discord.Member,amt:str):
        """Pay someone."""
        payment = cdc_utils.number_abbreviation.unpack(amt)
        amt = payment
        if amt < 0:
            await i.response.send_message("You can't pay negative money")
            return
        global CURRENCY_MANAGER
        user1 = CURRENCY_MANAGER.get_user(i.user.id)
        if user1.money < amt:
            await i.response.send_message("You don't have enough money for this transaction.")
            return
        transaction1 = CURRENCY_MANAGER.update_balance(i.user.id,-amt)
        transaction2 = CURRENCY_MANAGER.update_balance(u.id,amt)
        await i.response.send_message(f"You paid {u.mention} {CURRENCY_MANAGER.format_price(amt)}\n-# Transactions made:\n-# {i.user.mention}: {transaction1.as_codeblock()}\n-# {u.mention}: {transaction2.as_codeblock()}")

    @currency.command()
    async def work(self,i:discord.Interaction):
        """Work."""
        global CURRENCY_MANAGER
        global JOB_MANAGER
        user = CURRENCY_MANAGER.get_user(i.user.id)
        job = JOB_MANAGER.get_job(user.job)
        time_now = datetime.datetime.now().timestamp()
        diff = time_now - user.last_worked
        if diff < JOB_MANAGER.hour:
            await i.response.send_message(f"You've only started working, wait for the hour to end ({round(JOB_MANAGER.hour-diff)} seconds)")
            return
        extra = random.randint(-round(job.wage/2),round(job.wage/2))
        transaction = CURRENCY_MANAGER.update_balance(i.user.id,job.wage+extra)
        work_msgs = ["You worked tirelessly..","You worked.......","You went to work!"]
        await i.response.send_message(f"-# *{random.choice(work_msgs)}*\nYour **{job.display_name}** job has earned you {CURRENCY_MANAGER.format_price(job.wage+extra)}!\n-# {transaction.as_codeblock()}")
        user.last_worked = time_now

    @currency.command()
    @app_commands.autocomplete(item=buy_autocomp)
    async def buy(self,i:discord.Interaction,item:str):
        """Buy something from the shop."""
        global ITEM_MANAGER
        global CURRENCY_SHOP
        global CURRENCY_MANAGER
        d = item.split(" - ")
        item = CURRENCY_SHOP.get_item(d[0])
        if item == None:
            await i.response.send_message("Bad item")
            return
        item2 = ITEM_MANAGER.get_item(d[0])
        user = CURRENCY_MANAGER.get_user(i.user.id)
        if user.money < item.price:
            await i.response.send_message(f"You don't have enough money to buy **{item2.display_name}**!")
            return
        transaction = CURRENCY_MANAGER.update_balance(i.user.id,-item.price)
        user.add_item(item.name)
        await i.response.send_message(f"You bought **{item2.display_name}** for {CURRENCY_MANAGER.format_price(item.price)}!\n-# {transaction.as_codeblock()}")

    @currency.command()
    @app_commands.autocomplete(item=item_autocomp_usable)
    async def use_item(self,i:discord.Interaction,item:str):
        """Use an item."""
        d = item.split(" - ")
        global ITEM_MANAGER
        global CURRENCY_MANAGER
        item = ITEM_MANAGER.get_item(d[0])
        if item == None:
            await i.response.send_message("Bad item")
            return
        user = CURRENCY_MANAGER.get_user(i.user.id)
        if item.name not in user.inventory:
            await i.response.send_message("You don't have this item")
            return
        if not item.usable:
            await i.response.send_message("You can't use this item")
            return
        use = item.on_use(user)
        await i.response.send_message(f"-# *You used the **{item.display_name}**.*\n{use[0]}")
        if use[1]:
            user.remove_item(item.name)

    @currency.command()
    @app_commands.autocomplete(item=item_autocomp)
    async def give_item(self,i:discord.Interaction,u:discord.Member,item:str):
        """Give someone an item."""
        d = item.split(" - ")
        global ITEM_MANAGER
        global CURRENCY_MANAGER
        item = ITEM_MANAGER.get_item(d[0])
        if item == None:
            await i.response.send_message("Bad item")
            return
        user = CURRENCY_MANAGER.get_user(i.user.id)
        user2 = CURRENCY_MANAGER.get_user(u.id)
        if item.name not in user.inventory:
            await i.response.send_message("You don't have this item")
            return
        user.remove_item(item.name)
        user2.add_item(item.name)
        await i.response.send_message(f"You gave {u.mention} the **{item.display_name}**, you're so kind!")

    @currency.command()
    async def inventory(self,i:discord.Interaction):
        """Check your inventory."""
        global CURRENCY_MANAGER
        global ITEM_MANAGER
        user = CURRENCY_MANAGER.get_user(i.user.id)
        ret = "Your items:"
        ret_initial = ret
        footer = "You can use /currency use_item on some of these!"
        for it in user.inventory:
            item = ITEM_MANAGER.get_item(it)
            ret = ret + "\n" + "- " + f"**{item.display_name}** ({item.name})"
        if ret == ret_initial:
            ret = "You have no items."
            footer = None
        embed = discord.Embed(title="Inventory",description=ret,color=discord.Color.gold())
        if footer != None:
            embed.set_footer(text=footer)
        await i.response.send_message(embed=embed)

    @currency.command()
    async def shop(self,i:discord.Interaction):
        """Check the item shop."""
        global CURRENCY_SHOP
        global CURRENCY_MANAGER
        global ITEM_MANAGER
        items = CURRENCY_SHOP.items
        ret = "Available items:"
        for it in items:
            item = ITEM_MANAGER.get_item(it.name)
            ret = ret + "\n" + "- " + f"**{item.display_name}** ({item.name}) - {CURRENCY_MANAGER.format_price(it.price)}"
        embed = discord.Embed(title="Shop",description=ret,color=discord.Color.purple())
        balance = CURRENCY_MANAGER.format_price(CURRENCY_MANAGER.get_user(i.user.id).money)
        embed.set_footer(text=f"Your balance: {balance} | Use /currency buy to buy an item from here!")
        await i.response.send_message(embed=embed)

    @currency.command()
    @app_commands.autocomplete(job=job_autocomplete)
    async def job_apply(self,i:discord.Interaction,job:str):
        """Apply for a job"""
        global JOB_MANAGER
        global ITEM_MANAGER
        global CURRENCY_MANAGER
        p = job.split(" - ")
        job = JOB_MANAGER.get_job(p[0])
        if job == None:
            await i.response.send_message("bad job")
            return
        user = CURRENCY_MANAGER.get_user(i.user.id)
        to_have = []
        inv = user.inventory.copy()
        for item in job.required_items:
            if item not in inv:
                to_have.append(item)
            else:
                inv.remove(item)
        if len(to_have) > 0:
            str = "You're missing the following items required for this job:"
            for item in to_have:
                data = ITEM_MANAGER.get_item(item)
                str = str + "\n" + "- " + f"**{data.display_name}** ({data.name})"
            embed = discord.Embed(title="Rejected",description=str,color=discord.Color.red())
            embed.set_footer(text="Please buy them and run this command again if you'd like to reapply.")
            await i.response.send_message(embed=embed)
            return
        user.job = job.name
        embed = discord.Embed(title="Accepted",description=f"You've been accepted for the **{job.display_name}** ({job.name}) job!",color=discord.Color.green())
        embed.set_footer(text="Use /currency work to work.")
        await i.response.send_message(embed=embed)
    
    @currency.command()
    async def leaderboard(self,i:discord.Interaction,debt:bool=False):
        """View the leaderboard."""
        global CURRENCY_MANAGER
        embed = discord.Embed(title=f"{'Currency' if not debt else 'Debt'} Leaderboard",colour=discord.Color.blurple())
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
                money = CURRENCY_MANAGER.format_price(place.money)
                embed.add_field(name=f"{placement}. <@{place.id}>",value=money,inline=False)
            if place.id == str(i.user.id):
                my_placement = placement
            placement += placement_mod
            shown += 1
        embed.set_footer(text=f"Your placement is #{my_placement} "+f"{f'| Balance {CURRENCY_MANAGER.format_price(CURRENCY_MANAGER.get_user(i.user.id).money)}' if my_placement > lb_limit else ''}")
        await i.response.send_message(embed=embed)

    @currency.command()
    async def lie(self,i:discord.Interaction):
        global CURRENCY_MANAGER
        await i.response.send_message("You lied.")
        CURRENCY_MANAGER.get_user(i.user.id).add_item("lie")

async def setup(_bot: commands.Bot):
    global bot
    bot = _bot
    await _bot.add_cog(Currency())