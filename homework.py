import nextcord
from nextcord.ext import commands
from nextcord.ui import Modal, TextInput
from nextcord import Embed
import json
import os

intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Load configuration
try:
    with open('Config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: Config.json file not found!")
    config = {"homework_channel_id": None, "notification_role_id": None}
except json.JSONDecodeError:
    print("Error: Invalid JSON in Config.json!")
    config = {"homework_channel_id": None, "notification_role_id": None}

homework_list = []

# Modal for adding homework
class HomeworkModal(Modal):
    def __init__(self):
        super().__init__(
            "Add Homework",
            timeout=300
        )
        self.subject = TextInput(
            label="ชื่อวิชา",
            placeholder="กรอกชื่อวิชา"
        )
        self.details = TextInput(
            label="รายละเอียดงาน",
            placeholder="กรอกรายละเอียดงาน"
        )
        self.due_date = TextInput(
            label="กำหนดส่ง",
            placeholder="กรอกกำหนดส่ง (yyyy-mm-dd)"
        )
        self.type = TextInput(
            label="รูปแบบของงาน",
            placeholder="กรอกรูปแบบของงาน"
        )
        self.image_url = TextInput(
            label="ลิงค์รูปภาพ (optional)",
            placeholder="กรอกลิงค์รูปภาพ (ถ้ามี)",
            required=False
        )
        self.add_item(self.subject)
        self.add_item(self.details)
        self.add_item(self.due_date)
        self.add_item(self.type)
        self.add_item(self.image_url)

    async def callback(self, interaction: nextcord.Interaction):
        # Add homework to the list with a reference number
        ref_number = len(homework_list) + 1
        homework = {
            "ref_number": ref_number,
            "subject": self.subject.value,
            "details": self.details.value,
            "due_date": self.due_date.value,
            "type": self.type.value,
            "image_url": self.image_url.value if self.image_url.value else None
        }
        homework_list.append(homework)
        
        # Send embed to the specified channel
        embed = Embed(title=f"Homework Added - Ref #{ref_number}", color=0x00ff00)
        embed.add_field(name="ชื่อวิชา", value=self.subject.value, inline=False)
        embed.add_field(name="รายละเอียดงาน", value=self.details.value, inline=False)
        embed.add_field(name="กำหนดส่ง", value=self.due_date.value, inline=False)
        embed.add_field(name="รูปแบบของงาน", value=self.type.value, inline=False)
        embed.add_field(name="Reference Number", value=str(ref_number), inline=False)
        if self.image_url.value:
            embed.set_image(url=self.image_url.value)
        
        try:
            channel_id = config['homework_channel_id']
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)
                await interaction.response.send_message(f"✅ Homework added successfully! Reference number: {ref_number}", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Error: Homework channel not found.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error adding homework: {str(e)}", ephemeral=True)

@bot.slash_command(name="addhomework", description="Add homework (Admins only)")
@commands.has_permissions(administrator=True)
async def add_homework(interaction: nextcord.Interaction):
    modal = HomeworkModal()
    await interaction.response.send_modal(modal)

@bot.slash_command(name="hwnotify", description="Get notification role for homework")
async def hw_notify(interaction: nextcord.Interaction):
    try:
        role_id = config['notification_role_id']
        role = interaction.guild.get_role(role_id)
        if role:
            if role in interaction.user.roles:
                await interaction.response.send_message("You already have the homework notification role.", ephemeral=True)
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("✅ You have been assigned the homework notification role.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Notification role not found.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error assigning role: {str(e)}", ephemeral=True)

@bot.slash_command(name="hmnhomework", description="Notify the number of homeworks")
async def hmn_homework(interaction: nextcord.Interaction):
    subject_count = {}
    for hw in homework_list:
        subject = hw['subject']
        if subject in subject_count:
            subject_count[subject] += 1
        else:
            subject_count[subject] = 1
    
    embed = Embed(title="Homework Count", color=0x00ff00)
    for subject, count in subject_count.items():
        embed.add_field(name=subject, value=f"{count} assignments", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.slash_command(name="checkhw", description="Check homework details by reference number")
async def check_hw(interaction: nextcord.Interaction, ref_number: int):
    homework = next((hw for hw in homework_list if hw['ref_number'] == ref_number), None)
    if homework:
        embed = Embed(title=f"Homework Details - Ref #{ref_number}", color=0x00ff00)
        embed.add_field(name="ชื่อวิชา", value=homework['subject'], inline=False)
        embed.add_field(name="รายละเอียดงาน", value=homework['details'], inline=False)
        embed.add_field(name="กำหนดส่ง", value=homework['due_date'], inline=False)
        embed.add_field(name="รูปแบบของงาน", value=homework['type'], inline=False)
        if homework['image_url']:
            embed.set_image(url=homework['image_url'])
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"Homework with reference number {ref_number} not found.", ephemeral=True)

bot.run(os.getenv('DISCORD_TOKEN', 'token'))