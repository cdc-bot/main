import discord
from discord.ext import commands, tasks
from discord import app_commands
import json

bot = None

class ServerPreference:
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
            

class ServerServerPreferences:
    def __init__(self):
        self.enable_wordgames = ServerPreference("Enable Wordgames",bool,True,"Enabled wordgames in the current server.")
        self.enable_auto_responses = ServerPreference("Enable Auto-responses",bool,True,"Enabled cdc-bot auto responses in the current server.")
        self.cat_posting_on = ServerPreference("Enable Cat Posting",bool,False,"Enabled cat posting in the current server.")
        self.cat_posting_id = ServerPreference("Cat Posting Channel ID",int,0,"The ID for the channel where the cats should be sent.")
        self.cat_submissions_id = ServerPreference("Cat Submission Channel ID",int,0,"The ID for the channel where the cat submissions will be reviewed.")
    def from_json(self,dict):
        for key in dict:
            try:
                self.__dict__[key].set_impl(dict[key])
            except KeyError:
                print("key",key,"removed - ServerPreferences")
    def to_json_safe_dict(self):
        dict = {}
        for key in self.__dict__:
            if isinstance(self.__dict__[key],ServerPreference):
                dict[key] = self.__dict__[key].get()
        return dict
            
    
class ServerServerPreferencesManager:
    def __init__(self):
        global manager
        manager = self
        self.servers = {}
        self.try_load()
        self.save()
    def get_server(self,id) -> ServerServerPreferences:
        try:
            return self.servers[str(id)]
        except:
            self.servers[str(id)] = ServerServerPreferences()
            self.save()
            return self.servers[str(id)]
    def save(self):
        file = open("./server-ServerPreferences.json","w")
        c = self.to_json()
        file.write(c)
        file.close()
    def try_load(self):
        try:
            file = open("./server-ServerPreferences.json","r")
            c = file.read()
            file.close()
            j = json.loads(c)
            for server in j:
                up = ServerServerPreferences()
                up.from_json(j[server])
                self.servers[server] = up
        except:
            print("just loading default data")
        
    def to_json(self):
        dict = {}
        for key in self.servers:
            dict[key] = self.servers[key].to_json_safe_dict()
        return json.dumps(dict,indent=4)

manager = ServerServerPreferencesManager()

class SPSelectDropdown(discord.ui.Select):
    settings = None
    def carry_settings(self,settings):
        self.settings = settings
    async def callback(self, interaction:discord.Interaction):
        settingname = self.values[0]
        setting = None
        for stg in self.settings.__dict__:
            if self.settings.__dict__[stg].name == settingname:
                setting = self.settings.__dict__[stg]
        modal = SPChangeModal(setting,interaction)
        await interaction.response.send_modal(modal)

class SPChangeModal(discord.ui.Modal):
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
        
class SPSelectView(discord.ui.View):
    def __init__(self,uid,userid):
        self.author_id = userid
        super().__init__()
        options=[]
        server_config = manager.get_server(uid)
        for key in server_config.__dict__:
            val = server_config.__dict__[key]
            if isinstance(val,ServerPreference):
                label = val.name
                emoji = "🎛️"
                description = f"{val.value} | {val.type.__name__}"
                options.append(discord.SelectOption(label=label,emoji=emoji,description=description))
        #discord.SelectOption(label="Option 1",emoji="👌",description="This is option 1!"),
        dropdown = SPSelectDropdown(placeholder="Select a setting to change",max_values=1,min_values=1,options=options)
        dropdown.carry_settings(server_config)
        self.add_item(dropdown)
        #self.add_string_select(placeholder="a",max_values=1,min_values=1,options=["true","false"])
    async def interaction_check(self,i:discord.MessageInteraction):
        if i.user.id != self.author_id:
            await i.response.send_message(content="this isn't yours",ephemeral=True)
            return False
        return True

async def ServerPreference_autocomp(i:discord.Interaction,current:str):
    global manager
    server_config = manager.get_server(i.guild.id)
    mc = []
    for key in server_config.__dict__:
            val = server_config.__dict__[key]
            if isinstance(val,ServerPreference):
                if val.name.lower().find(current) != -1 or current == "":
                    mc.append(val)
    ret = []
    for item in mc:
        ret.append(f"{item.name} - {item.type.__name__}")
    return ret[:10]

class ServerConfig(commands.Cog):
    @app_commands.command()
    async def server_config(self,i):
        """View and configure your server settings."""
        global manager
        server_config = manager.get_server(i.guild.id)
        desc = ""
        for key in server_config.__dict__:
            val = server_config.__dict__[key]
            if isinstance(val,ServerPreference):
                desc = desc + "\n" + "**" + val.name + "**" + ": " + str(val.value) + "\n-# " + val.description
        embed = discord.Embed(title="Current Configuration",description=desc)
        await i.response.send_message(embed=embed,view=SPSelectView(i.guild.id,i.user.id),ephemeral=True)



async def setup(_bot:commands.Bot):
    global bot
    bot = _bot
    await bot.add_cog(ServerConfig())