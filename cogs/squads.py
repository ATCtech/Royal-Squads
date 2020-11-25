import discord
from discord.ext import commands
import pyrebase
import json
from decouple import config
from disputils import *

firebase = pyrebase.initialize_app(json.loads(config("FIREBASE")))
db=firebase.database()

weeblet=666578281142812673
roleid =780092798942445615

def isOP(user):
  has_role = roleid in [role.id for role in user.roles] 
  return user.id==weeblet or user.permissions.administrator or has_role
  
def squad_exists(name:str):
  sqds = dict(db.child("SQUADS").get().val())
  return name in sqds

class Squads(commands.Cog):
  def __init__(self,bot):
    self.bot=bot
    
  @commands.command()
  async def create(self,ctx,leader:discord.User=None,*,name:str=None):
    if isOP(ctx.author):
      if leader==None or name==None:
        emb=discord.Embed(title=f"Error",description=f"Correct useage : `create @leader squad name`",color=0xFF0000)
        emb.set_footer(text=f"{str(ctx.author)}")
        await ctx.send(embed=emb)
        return
      db.child("SQUADS").child(name).set(leader.id)
      emb=discord.Embed(title=f"{str(ctx.author)} created a squad",description=f"Name : **{name}**\nLeader : {leader.mention}",color=0x00FF00)
      emb.set_footer(text="use squads command to see a list of squads")
      await ctx.send(embed=emb)
      
  @commands.command()
  async def delete(self,ctx,*,name:str=None):
    if isOP(ctx.author):
      if name==None:
        emb=discord.Embed(title=f"Error",description=f"Correct useage : `delete squad name`",color=0xFF0000)
        emb.set_footer(text=f"{str(ctx.author)}")
        await ctx.send(embed=emb)
        return
        
      confirmation = BotConfirmation(ctx, 0xFF0000)
      await confirmation.confirm(f"Are you sure you want to delete {name}?")

      if confirmation.confirmed:
          await confirmation.update("Confirmed deletion", color=0x00FF00)
          #if(squad_exists(name)):
          if True:
            db.child("SQUADS").child(name).remove()
            try:
              mbrs = dict(db.child("MEMBERS").get().val())
              for mem in mbrs:
                if mbrs[mem].lower()==name.lower():
                  db.child("MEMBERS").child(mem).remove()
            except:
              pass

            emb=discord.Embed(title=f"{str(ctx.author)} deleted a squad",description=f"Name : **{name}**",color=0xFF0000)
            emb.set_footer(text="use squads command to see a list of squads")
            await ctx.send(embed=emb)
          else:
            emb=discord.Embed(title=f"That squad doesnot exist",description="Did you forget to create a squad?\nUse `create` command",color=0xFF0000)
            await ctx.send(embed=emb)
      else:
          await confirmation.update("Not confirmed", hide_author=False, color=0x0000FF)
          
      
      
      
    
  @commands.command(aliases=["sqd"])
  async def squad(self,ctx,*,name=""):
    name=name.lower()
    if name=="":
      sqd = dict(db.child("SQUADS").get().val())
      dsc=""
      for sq in sqd:
        m = await ctx.guild.fetch_member(sqd[sq])
        dsc+=f"**{sq}** - {m.mention}\n"
      emb=discord.Embed(title="Squad List",description=dsc+"\nTo join a squad DM the <@&780092798942445615>",color=0x0000FF)
      emb.set_footer(text=f"Total squads : {len(sqd)}")
    else:
      dsc=""
      try:
        sqd = dict(db.child("MEMBERS").get().val())
        sqd = [k for k,v in sqd.items() if v.lower()==name]
      except:
        dsc="No Members"
        sqd=[]
      for member in sqd:
        m = await ctx.guild.fetch_member(member)
        dsc+=f"{str(m)}\n"
      emb=discord.Embed(title=name,description=dsc,color=0x0000FF)
      l=len(dsc.split('\n'))-1
      emb.set_footer(text=f"{l}/5 members")
    await ctx.send(embed=emb)
    
    
  @commands.command()
  async def add(self,ctx,mbr:discord.User=None,*,name:str=None):
    if isOP(ctx.author):
      if mbr==None or name==None:
        emb=discord.Embed(title=f"Error",description=f"Correct useage : `add @member squad name`")
        emb.set_footer(text=f"{str(ctx.author)}")
        await ctx.send(embed=emb)
        return
      if squad_exists(name):
        db.child("MEMBERS").child(mbr.id).set(name)
        emb=discord.Embed(title=f"{str(ctx.author)} added a member to {name}",description="")
        await ctx.send(embed=emb)
      else:
        emb=discord.Embed(title=f"That squad doesnot exist",description="Did you forget to create a squad?\nUse `create` command")
        await ctx.send(embed=emb)
        
  @commands.command()
  async def remove(self,ctx,mbr:discord.User=None,*,name:str=None):
    if isOP(ctx.author):
      if mbr==None or name==None:
        emb=discord.Embed(title=f"Error",description=f"Correct useage : `remove @member squad name`")
        emb.set_footer(text=f"{str(ctx.author)}")
        await ctx.send(embed=emb)
        return
      if squad_exists(name):
        db.child("MEMBERS").child(mbr.id).remove()
        emb=discord.Embed(title=f"{str(ctx.author)} removed a member from {name}",description="")
        await ctx.send(embed=emb)
      else:
        emb=discord.Embed(title=f"That squad doesnot exist",description="Did you forget to create a squad?\nUse `create` command",color=0xFF0000)
        await ctx.send(embed=emb)
    
    
    
  
def setup(bot):
  bot.add_cog(Squads(bot))
  print("COG : SQUADS LOADED")
