# KanBarnPY - Discord Homework Bot

A Discord bot for managing homework assignments with persistent storage and easy deployment.

## Features

- 📝 Add homework assignments with details, due dates, and optional images
- 🔍 Check homework by reference number
- 📊 View homework count by subject
- 🔔 Notification role management
- 💾 Persistent SQLite database storage
- 📋 Comprehensive logging
- 🌍 Environment-based configuration

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord bot token
- Discord server with appropriate permissions

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/mdccvii/KanBarnPY.git
   cd KanBarnPY
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

4. **Configure the bot**
   
   Edit `Config.json` with your Discord server IDs:
   ```json
   {
     "homework_channel_id": YOUR_HOMEWORK_CHANNEL_ID,
     "notification_role_id": YOUR_NOTIFICATION_ROLE_ID
   }
   ```

5. **Run the bot**
   ```bash
   python homework.py
   ```

## Deployment

### Deploy to Replit

[![Run on Repl.it](https://replit.com/badge/github/mdccvii/KanBarnPY)](https://replit.com/new/github/mdccvii/KanBarnPY)

1. Click the "Run on Repl.it" button above
2. Fork the repository to your Replit account
3. In Replit's Secrets tab, add:
   - `DISCORD_TOKEN`: Your Discord bot token
4. Update `Config.json` with your server IDs
5. Click the "Run" button

### Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/mdccvii/KanBarnPY)

1. Click the "Deploy to Heroku" button above
2. Set the config vars:
   - `DISCORD_TOKEN`: Your Discord bot token
3. Update `Config.json` with your server IDs
4. Deploy the app

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/6h8dQX)

1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Set environment variables:
   - `DISCORD_TOKEN`: Your Discord bot token
4. Update `Config.json` with your server IDs
5. Deploy

## Bot Commands

### Slash Commands

- `/addhomework` - Add a new homework assignment (Admin only)
- `/checkhw <ref_number>` - Check homework details by reference number
- `/hmnhomework` - View homework count by subject
- `/hwnotify` - Get the homework notification role

## Configuration Files

### `.env` File
```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here

# Database Configuration
DATABASE_URL=homework.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Optional: Development Settings
DEBUG=False
```

### `Config.json` File
```json
{
  "homework_channel_id": 1240859350407446690,
  "notification_role_id": 1240817218443284487
}
```

## Database Schema

The bot uses SQLite to store homework data persistently:

```sql
CREATE TABLE homework (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_number INTEGER UNIQUE NOT NULL,
    subject TEXT NOT NULL,
    details TEXT NOT NULL,
    due_date TEXT NOT NULL,
    type TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Discord bot token | - | ✅ |
| `DATABASE_URL` | SQLite database file path | `homework.db` | ❌ |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | ❌ |
| `LOG_FILE` | Log file path | `bot.log` | ❌ |
| `DEBUG` | Enable debug mode | `False` | ❌ |

## Development

### Setting up for Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up pre-commit hooks (optional):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

### Project Structure

```
KanBarnPY/
├── homework.py          # Main bot file
├── Config.json          # Bot configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── Procfile            # Heroku deployment
├── replit.nix          # Replit configuration
└── .replit             # Replit settings
```

## Logging

The bot includes comprehensive logging with:
- File logging to `bot.log` (configurable)
- Console logging for development
- Configurable log levels
- Structured log format with timestamps

## Security

- Environment variables for sensitive data
- Token management through `.env` files
- Database sanitization for user inputs
- Error handling to prevent crashes

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/mdccvii/KanBarnPY/issues) page
2. Create a new issue if needed
3. Join our Discord server for community support

## Changelog

### v2.0.0
- Added persistent SQLite database storage
- Implemented environment variable configuration
- Added comprehensive logging
- Improved error handling
- Added deployment configurations for Replit and Heroku

### v1.0.0
- Initial release with basic homework management
- Discord slash commands
- In-memory storage