import disnake
from disnake.ext import commands, tasks
import json

bot = None

class Preference:
    def __init__(self,name,type,default=None):
        self.name = name
        self.type = type
        self.default = default
        if default == None:
            self.value = type()
        else:
            self.value = default
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
        self.polyamorous = Preference("Polyamorous",bool,False)
        self.disable_proposals = Preference("Disable Proposals",bool,False)
        self.defer_cheating_alerts = Preference("Defer Cheating Alerts",bool,False)
        self.size = Preference("Size",float,1)
    def from_json(self,dict):
        for key in dict:
            self.__dict__[key].set_impl(dict[key])
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

class SelectDropdown(disnake.ui.StringSelect):
    settings = None
    def carry_settings(self,settings):
        self.settings = settings
    async def callback(self, interaction:disnake.MessageInteraction):
        settingname = interaction.values[0]
        setting = None
        for stg in self.settings.__dict__:
            if self.settings.__dict__[stg].name == settingname:
                setting = self.settings.__dict__[stg]
        modal = ChangeModal(setting,interaction)
        await interaction.response.send_modal(modal)

class ChangeModal(disnake.ui.Modal):
    def __init__(self,setting,dd_interaction):
        self.setting = setting
        self.dd_interaction = dd_interaction
        super().__init__(title=f"Modifying '{setting.name}'",components=[])
        self.add_text_input(label="New value",custom_id="new_value")
    async def callback(self, interaction:disnake.ModalInteraction):
        text_given = interaction.values["new_value"]
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
                await interaction.send("_ _",ephemeral=True,delete_after=0)
                return
        
        if not dont_convert:
            try:
                conversion = self.setting.type(text_given)
            except:
                conversion = self.setting.type(self.setting.default)
            self.setting.set(conversion)
        
        await self.dd_interaction.edit_original_response(content=f"**{self.setting.name}** is now set to `{self.setting.value}`.",embeds=[],view=None)
        await interaction.send("_ _",ephemeral=True,delete_after=0)
        

class SelectView(disnake.ui.View):
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
                options.append(disnake.SelectOption(label=label,emoji=emoji,description=description))
        #disnake.SelectOption(label="Option 1",emoji="👌",description="This is option 1!"),
        dropdown = SelectDropdown(placeholder="Select a setting to change",max_values=1,min_values=1,options=options)
        dropdown.carry_settings(user_config)
        self.add_item(dropdown)
        #self.add_string_select(placeholder="a",max_values=1,min_values=1,options=["true","false"])
    async def interaction_check(self,i:disnake.MessageInteraction):
        if i.author.id != self.author_id:
            await i.send(content="this isn't yours",ephemeral=True)
            return False
        return True

async def preference_autocomp(i:disnake.Interaction,current:str):
    global manager
    user_config = manager.get_user(i.author.id)
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
    @commands.slash_command()
    async def config(self,i):
        """View and configure your user settings."""
        global manager
        user_config = manager.get_user(i.author.id)
        desc = ""
        for key in user_config.__dict__:
            val = user_config.__dict__[key]
            if isinstance(val,Preference):
                desc = desc + "\n" + "**" + val.name + "**" + ": " + str(val.value)
        embed = disnake.Embed(title="Current Configuration",description=desc)
        await i.send(embed=embed,view=SelectView(i.author.id),ephemeral=True)



def setup(_bot:commands.Bot):
    global bot
    bot = _bot
    bot.add_cog(Config())