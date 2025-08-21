import nextcord
from nextcord.ext import commands
from nextcord.ui import Modal, TextInput
from nextcord import Embed
import json
import os
import logging
import aiosqlite
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
log_file = os.getenv('LOG_FILE', 'bot.log')
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'homework.db')

# Load configuration
try:
    with open('Config.json', 'r') as f:
        config = json.load(f)
    logger.info("Configuration loaded successfully")
except FileNotFoundError:
    logger.error("Config.json file not found!")
    config = {"homework_channel_id": None, "notification_role_id": None}
except json.JSONDecodeError:
    logger.error("Invalid JSON in Config.json!")
    config = {"homework_channel_id": None, "notification_role_id": None}

homework_list = []

# Database initialization
async def init_database():
    """Initialize the SQLite database for homework storage"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref_number INTEGER UNIQUE NOT NULL,
                subject TEXT NOT NULL,
                details TEXT NOT NULL,
                due_date TEXT NOT NULL,
                type TEXT NOT NULL,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
        logger.info("Database initialized successfully")

async def save_homework_to_db(homework):
    """Save homework to database"""
    try:
        async with aiosqlite.connect(DATABASE_URL) as db:
            await db.execute('''
                INSERT INTO homework (ref_number, subject, details, due_date, type, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                homework['ref_number'],
                homework['subject'],
                homework['details'],
                homework['due_date'],
                homework['type'],
                homework['image_url']
            ))
            await db.commit()
            logger.info(f"Homework saved to database: ref #{homework['ref_number']}")
    except Exception as e:
        logger.error(f"Error saving homework to database: {e}")

async def load_homework_from_db():
    """Load all homework from database to memory"""
    try:
        async with aiosqlite.connect(DATABASE_URL) as db:
            async with db.execute('SELECT ref_number, subject, details, due_date, type, image_url FROM homework ORDER BY ref_number') as cursor:
                rows = await cursor.fetchall()
                homework_list.clear()
                for row in rows:
                    homework = {
                        'ref_number': row[0],
                        'subject': row[1],
                        'details': row[2],
                        'due_date': row[3],
                        'type': row[4],
                        'image_url': row[5]
                    }
                    homework_list.append(homework)
                logger.info(f"Loaded {len(homework_list)} homework items from database")
    except Exception as e:
        logger.error(f"Error loading homework from database: {e}")

async def get_next_ref_number():
    """Get the next reference number for homework"""
    try:
        async with aiosqlite.connect(DATABASE_URL) as db:
            async with db.execute('SELECT MAX(ref_number) FROM homework') as cursor:
                row = await cursor.fetchone()
                return (row[0] or 0) + 1
    except Exception as e:
        logger.error(f"Error getting next ref number: {e}")
        return len(homework_list) + 1

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
        ref_number = await get_next_ref_number()
        homework = {
            "ref_number": ref_number,
            "subject": self.subject.value,
            "details": self.details.value,
            "due_date": self.due_date.value,
            "type": self.type.value,
            "image_url": self.image_url.value if self.image_url.value else None
        }
        
        # Save to database and memory
        await save_homework_to_db(homework)
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
                logger.info(f"Homework added successfully: ref #{ref_number}")
            else:
                await interaction.response.send_message("❌ Error: Homework channel not found.", ephemeral=True)
                logger.error("Homework channel not found")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error adding homework: {str(e)}", ephemeral=True)
            logger.error(f"Error adding homework: {e}")

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

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    logger.info(f'{bot.user} has connected to Discord!')
    await init_database()
    await load_homework_from_db()
    logger.info(f'Bot is ready with {len(homework_list)} homework items loaded')

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        print("Error: Please set DISCORD_TOKEN in your .env file")
        exit(1)
    
    logger.info("Starting bot...")
    bot.run(token)