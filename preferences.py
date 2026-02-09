import discord
from discord.ext import commands, tasks
from discord import app_commands
import json

bot = None

class Preference:
    def __init__(self,name,type,default,desc):
        self.name = name
        self.type = type
        self.default = default
        if default == None:
            self.value = type()
        else:
            self.value = default
        self.description = desc
    def get(self):
        return self.value
    def set(self,value):
        global manager
        self.set_impl(value)
        manager.save()
    def set_impl(self,value):
        if isinstance(value,self.type):
            self.value = value
            

class UserPreferences:
    def __init__(self):
        self.polyamorous = Preference("Polyamorous",bool,False,"Allows you to date multiple people. (Everyone in a marriage needs to have this on)")
        self.disable_proposals = Preference("Disable Proposals",bool,False,"Disallows people from proposing to you.")
        self.defer_cheating_alerts = Preference("Defer Cheating Alerts",bool,False,"Disable sending cheating alerts in real time, only deliver them every 24 hours.")
    def from_json(self,dict):
        for key in dict:
            try:
                self.__dict__[key].set_impl(dict[key])
            except KeyError:
                print("key",key,"removed - preferences")
    def to_json_safe_dict(self):
        dict = {}
        for key in self.__dict__:
            if isinstance(self.__dict__[key],Preference):
                dict[key] = self.__dict__[key].get()
        return dict
            
    
class UserPreferencesManager:
    def __init__(self):
        global manager
        manager = self
        self.users = {}
        self.try_load()
        self.save()
    def get_user(self,id) -> UserPreferences:
        try:
            return self.users[str(id)]
        except:
            self.users[str(id)] = UserPreferences()
            self.save()
            return self.users[str(id)]
    def save(self):
        file = open("./preferences.json","w")
        c = self.to_json()
        file.write(c)
        file.close()
    def try_load(self):
        try:
            file = open("./preferences.json","r")
            c = file.read()
            file.close()
            j = json.loads(c)
            for user in j:
                up = UserPreferences()
                up.from_json(j[user])
                self.users[user] = up
        except:
            print("just loading default data")
        
    def to_json(self):
        dict = {}
        for key in self.users:
            dict[key] = self.users[key].to_json_safe_dict()
        return json.dumps(dict,indent=4)

manager = UserPreferencesManager()

class SelectDropdown(discord.ui.Select):
    settings = None
    def carry_settings(self,settings):
        self.settings = settings
    async def callback(self, interaction:discord.Interaction):
        settingname = self.values[0]
        setting = None
        for stg in self.settings.__dict__:
            if self.settings.__dict__[stg].name == settingname:
                setting = self.settings.__dict__[stg]
        modal = ChangeModal(setting,interaction)
        await interaction.response.send_modal(modal)

class ChangeModal(discord.ui.Modal):
    new_value = discord.ui.TextInput(label="New value",custom_id="new_value")
    def __init__(self,setting,dd_interaction:discord.Interaction):
        self.setting = setting
        self.dd_interaction = dd_interaction
        super().__init__(title=f"Modifying '{setting.name}'")
    async def on_submit(self, interaction:discord.Interaction):
        text_given = self.new_value.value
        dont_convert = False

        if self.setting.type.__name__ == "bool":
            if text_given.lower() == "true":
                self.setting.set(True)
                dont_convert = True
            elif text_given.lower() == "false":
                self.setting.set(False)
                dont_convert = True
            else:
                await self.dd_interaction.edit_original_response(content=":x: The value as to be `True` or `False`.",embeds=[],view=None)
                await interaction.response.send_message("_ _",ephemeral=True,delete_after=0)
                return
        
        if not dont_convert:
            try:
                conversion = self.setting.type(text_given)
            except:
                conversion = self.setting.type(self.setting.default)
            self.setting.set(conversion)
        
        await self.dd_interaction.edit_original_response(content=f"**{self.setting.name}** is now set to `{self.setting.value}`.",embeds=[],view=None)
        await interaction.response.send_message("_ _",ephemeral=True,delete_after=0)
        
class SelectView(discord.ui.View):
    def __init__(self,uid):
        self.author_id = uid
        super().__init__()
        options=[]
        user_config = manager.get_user(uid)
        for key in user_config.__dict__:
            val = user_config.__dict__[key]
            if isinstance(val,Preference):
                label = val.name
                emoji = "🎛️"
                description = f"{val.value} | {val.type.__name__}"
                options.append(discord.SelectOption(label=label,emoji=emoji,description=description))
        #discord.SelectOption(label="Option 1",emoji="👌",description="This is option 1!"),
        dropdown = SelectDropdown(placeholder="Select a setting to change",max_values=1,min_values=1,options=options)
        dropdown.carry_settings(user_config)
        self.add_item(dropdown)
        #self.add_string_select(placeholder="a",max_values=1,min_values=1,options=["true","false"])
    async def interaction_check(self,i:discord.MessageInteraction):
        if i.user.id != self.author_id:
            await i.response.send_message(content="this isn't yours",ephemeral=True)
            return False
        return True

async def preference_autocomp(i:discord.Interaction,current:str):
    global manager
    user_config = manager.get_user(i.user.id)
    mc = []
    for key in user_config.__dict__:
            val = user_config.__dict__[key]
            if isinstance(val,Preference):
                if val.name.lower().find(current) != -1 or current == "":
                    mc.append(val)
    ret = []
    for item in mc:
        ret.append(f"{item.name} - {item.type.__name__}")
    return ret[:10]

class Config(commands.Cog):
    @app_commands.command()
    async def config(self,i):
        """View and configure your user settings."""
        global manager
        user_config = manager.get_user(i.user.id)
        desc = ""
        for key in user_config.__dict__:
            val = user_config.__dict__[key]
            if isinstance(val,Preference):
                desc = desc + "\n" + "**" + val.name + "**" + ": " + str(val.value) + "\n-# " + val.description
        embed = discord.Embed(title="Current Configuration",description=desc)
        await i.response.send_message(embed=embed,view=SelectView(i.user.id),ephemeral=True)



async def setup(_bot:commands.Bot):
    global bot
    bot = _bot
    await bot.add_cog(Config())