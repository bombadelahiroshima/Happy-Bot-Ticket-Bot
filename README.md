# Happy Bot

**Happy Bot** is a free, open-source, self-hostable Discord ticket bot built with Python and `discord.py`.

It is designed for servers that want a simple but powerful ticket system without paid APIs, subscriptions, or external databases.

> **Happy Bot is not affiliated with, endorsed by, or sponsored by Discord.**

---

## Features

- Ticket creation through a Discord panel
- Ticket subject and description modal
- Staff role support
- Dedicated ticket category
- Optional transcript channel
- Ticket claiming and unclaiming
- Ticket renaming
- Add members to tickets
- Remove members from tickets
- Ticket priority system
- Ticket transcripts
- Ticket closing and automatic channel deletion
- Ticket statistics
- Per-user open-ticket limit
- Ticket blacklist
- Persistent buttons and menus after bot restarts
- JSON file storage
- No external database required
- No paid API required
- Server-count presence
- Slash commands
- Open-source and self-hostable

---

# Requirements

Before installing Happy Bot, you need:

- A Discord account
- A Discord server where you have permission to manage the server
- A Discord application/bot created in the Discord Developer Portal
- Python **3.10 or newer**
- Internet access
- `pip`
- `discord.py 2.x`

Python 3.12 or newer is recommended.

---

# 1. Create the Discord Bot

Go to the official Discord Developer Portal:

https://discord.com/developers/applications

## Step 1 — Create an application

1. Open the Developer Portal.
2. Click **New Application**.
3. Give your application a name.
4. Create the application.

## Step 2 — Create the bot

Open:

**Your Application → Bot**

Click:

**Add Bot**

Confirm the creation.

## Step 3 — Get your bot token

In the **Bot** page, find the token section.

Copy your bot token.

### IMPORTANT

Never publish your bot token.

Do not:

- Upload it to GitHub
- Send it in Discord
- Put it in screenshots
- Share it with other people
- Commit it to a public repository

If your token is leaked, immediately regenerate it from the Discord Developer Portal.

Happy Bot expects the token to be placed in the Python file as:

```python
TOKEN = ""
```

Put your real token between the quotes.

Example:

```python
TOKEN = "YOUR_BOT_TOKEN_HERE"
```

Do not use the example token as a real token.

---

# 2. Enable Required Intents

Open:

**Developer Portal → Your Application → Bot**

Find:

**Privileged Gateway Intents**

Happy Bot uses member information, so enable:

- **Server Members Intent**

Then save the changes.

You do not need to enable every privileged intent.

---

# 3. Install Python

## Windows

Download Python from:

https://www.python.org/downloads/

During installation, make sure you enable:

**Add Python to PATH**

Then open PowerShell or Command Prompt and check:

```powershell
python --version
```

If that does not work, try:

```powershell
py --version
```

You should see a Python version such as:

```text
Python 3.12.x
```

---

## Debian / Ubuntu / Linux Mint / Pop!_OS

Update your packages:

```bash
sudo apt update
```

Install Python, pip, and virtual environment support:

```bash
sudo apt install python3 python3-pip python3-venv
```

Check:

```bash
python3 --version
```

and:

```bash
pip3 --version
```

---

## Fedora

```bash
sudo dnf install python3 python3-pip
```

Check:

```bash
python3 --version
```

---

## Arch Linux / Manjaro / EndeavourOS

Install Python and pip:

```bash
sudo pacman -Syu python python-pip
```

Check:

```bash
python --version
```

and:

```bash
pip --version
```

---

## openSUSE

```bash
sudo zypper install python3 python3-pip
```

Check:

```bash
python3 --version
```

---

## Alpine Linux

```bash
sudo apk add python3 py3-pip
```

Check:

```bash
python3 --version
```

---

# 4. Download Happy Bot

Download or clone the project.

If you are using Git:

```bash
git clone YOUR_HAPPY_BOT_REPOSITORY
cd YOUR_HAPPY_BOT_REPOSITORY
```

If you downloaded a ZIP:

1. Extract the ZIP.
2. Open the extracted folder.
3. Make sure `happy_bot_clean.py` is inside the project folder.

The basic structure can look like:

```text
HappyBot/
├── happy_bot_clean.py
├── README.md
├── guild_configs.json
├── tickets.json
└── blacklist.json
```

The JSON files can be created automatically by the bot.

---

# 5. Create a Virtual Environment

Using a virtual environment is recommended because it keeps Happy Bot's Python packages separate from the rest of your system.

## Windows

Open PowerShell in the Happy Bot folder:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, you can use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

You can also allow local PowerShell scripts with:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

---

## Debian / Ubuntu / Linux

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

## Fedora / Arch / Other Linux

```bash
python3 -m venv .venv
```

or, on systems where Python is called `python`:

```bash
python -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

When the virtual environment is active, your terminal will usually show:

```text
(.venv)
```

---

# 6. Install Dependencies

Happy Bot uses `discord.py`.

Install it with:

## Windows

```powershell
python -m pip install -U discord.py
```

If you use the Python launcher:

```powershell
py -m pip install -U discord.py
```

## Linux

```bash
python3 -m pip install -U discord.py
```

If your virtual environment is active:

```bash
python -m pip install -U discord.py
```

Verify:

```bash
python -m pip show discord.py
```

You should see information about the installed package.

---

# 7. Configure Happy Bot

Open:

```text
happy_bot_clean.py
```

Find:

```python
TOKEN = ""
```

Put your bot token inside the quotes:

```python
TOKEN = "YOUR_BOT_TOKEN"
```

Do not add your token anywhere else.

Happy Bot does not require an external database.

It stores its configuration and ticket data in JSON files.

---

# 8. Start the Bot

## Windows

Open PowerShell in the project directory:

```powershell
python happy_bot_clean.py
```

or:

```powershell
py happy_bot_clean.py
```

---

## Linux

```bash
python3 happy_bot_clean.py
```

If your virtual environment is active:

```bash
python happy_bot_clean.py
```

---

# 9. Invite the Bot

Go to:

**Discord Developer Portal → Your Application → Installation**

Configure the installation settings for your server.

The bot needs enough permissions to:

- View Channels
- Send Messages
- Read Message History
- Embed Links
- Attach Files
- Manage Channels
- Manage Roles

The exact permissions required can depend on how your server's roles and channel permissions are configured.

Avoid giving Administrator unless you intentionally want to use it.

After generating the installation/invite link, open it and add the bot to your server.

---

# 10. Configure Your Server

Once the bot is online, use:

```text
/setup
```

The command requires:

### Staff Role

Choose the role that should manage tickets.

Example:

```text
@Support
```

### Category

Choose the Discord category where ticket channels should be created.

Example:

```text
SUPPORT TICKETS
```

### Transcript Channel

Optional.

Choose the channel where closed ticket transcripts should be sent.

Example:

```text
#ticket-logs
```

---

# 11. Recommended Server Structure

A clean setup could look like:

```text
SUPPORT
│
├── #ticket-panel
├── #ticket-logs
│
└── SUPPORT TICKETS
    ├── ticket-0001
    ├── ticket-0002
    └── ticket-0003
```

You do not have to use these exact names.

---

# 12. Create the Ticket Panel

Use:

```text
/ticket-panel
```

You can select:

- Channel
- Title
- Description

Example:

```text
Title:
Need Help?

Description:
Need assistance? Click the button below to create a support ticket.
```

Happy Bot will send a ticket panel with an **Open Ticket** button.

---

# 13. How Users Create Tickets

A user clicks:

**Open Ticket**

A form appears.

The user enters:

### Subject / Topic

Example:

```text
Technical Problem
```

### Description

Example:

```text
My verification system is not working.
```

After submitting, Happy Bot creates a private ticket channel.

The ticket owner and configured staff role can access it.

---

# 14. Ticket Controls

Inside a ticket, staff can use the available controls.

## Claim

Claims the ticket for the current staff member.

## Unclaim

Releases the ticket so another staff member can claim it.

## Rename

Changes the ticket channel name.

Example:

```text
ticket-0001
```

can become:

```text
billing-problem
```

## Add Member

Adds another Discord member to the ticket.

The member's Discord User ID is required.

## Remove Member

Removes a member's ticket access.

The ticket owner cannot be removed.

## Priority

Ticket priority can be changed between:

```text
Low
Normal
High
Urgent
```

## Transcript

Generates a text transcript containing the ticket conversation and attachments.

## Close Ticket

Closes the ticket, creates a transcript if a transcript channel is configured, and removes the ticket channel.

---

# 15. Commands

## `/setup`

Configure Happy Bot for the current server.

Options:

```text
staff_role
category
transcript_channel
```

---

## `/ticket-panel`

Send a ticket panel to a channel.

Options:

```text
channel
title
description
```

---

## `/ticket-config`

View or update the ticket configuration.

Options:

```text
max_tickets_per_user
staff_role
category
transcript_channel
```

---

## `/ticket-stats`

Show ticket statistics for the server.

Statistics include:

- Total tickets
- Open tickets
- Closed tickets
- Claimed tickets
- Ticket counter

---

## `/ticket-blacklist`

Block or unblock a member from creating tickets.

Options:

```text
member
action
```

Actions:

```text
add
remove
```

---

# 16. Ticket Data

Happy Bot uses JSON files instead of an external database.

The bot uses:

```text
guild_configs.json
tickets.json
blacklist.json
```

These files contain server configuration, ticket information, and blacklist information.

### Do not delete them while the bot is running.

If you move Happy Bot to another computer, move the JSON files with it if you want to keep the existing data.

---

# 17. Backups

Because the bot stores its data locally, backing up the JSON files is recommended.

Back up:

```text
guild_configs.json
tickets.json
blacklist.json
```

A simple backup can be:

```bash
cp guild_configs.json guild_configs.backup.json
cp tickets.json tickets.backup.json
cp blacklist.json blacklist.backup.json
```

On Windows, you can simply copy the files to another folder.

---

# 18. Running Happy Bot on a VPS

A VPS is useful if you want the bot online 24/7.

Recommended Linux distributions include:

- Debian
- Ubuntu
- Ubuntu Server
- Fedora Server
- Arch Linux

The general process is:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

Clone or upload the project:

```bash
git clone YOUR_HAPPY_BOT_REPOSITORY
cd YOUR_HAPPY_BOT_REPOSITORY
```

Create the environment:

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Install the dependency:

```bash
python -m pip install -U discord.py
```

Configure the token:

```python
TOKEN = "YOUR_BOT_TOKEN"
```

Start:

```bash
python happy_bot_clean.py
```

---

# 19. Keep the Bot Running with systemd

For a Linux VPS, `systemd` is a good way to keep the bot running after you disconnect from SSH.

Create a service:

```bash
sudo nano /etc/systemd/system/happybot.service
```

Example:

```ini
[Unit]
Description=Happy Bot Discord Ticket Bot
After=network.target

[Service]
Type=simple
User=YOUR_LINUX_USERNAME
WorkingDirectory=/home/YOUR_LINUX_USERNAME/HappyBot
ExecStart=/home/YOUR_LINUX_USERNAME/HappyBot/.venv/bin/python /home/YOUR_LINUX_USERNAME/HappyBot/happy_bot_clean.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace:

```text
YOUR_LINUX_USERNAME
```

with your actual Linux username.

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable happybot
sudo systemctl start happybot
```

Check the status:

```bash
sudo systemctl status happybot
```

View live logs:

```bash
sudo journalctl -u happybot -f
```

Restart:

```bash
sudo systemctl restart happybot
```

Stop:

```bash
sudo systemctl stop happybot
```

---

# 20. Running with tmux

If you do not want to create a systemd service, you can use `tmux`.

Install:

```bash
sudo apt install tmux
```

Start a session:

```bash
tmux new -s happybot
```

Start Happy Bot:

```bash
python happy_bot_clean.py
```

Detach without stopping the bot:

```text
CTRL + B
D
```

Reconnect:

```bash
tmux attach -t happybot
```

---

# 21. Running with screen

Install:

```bash
sudo apt install screen
```

Start:

```bash
screen -S happybot
```

Run:

```bash
python happy_bot_clean.py
```

Detach:

```text
CTRL + A
D
```

Reconnect:

```bash
screen -r happybot
```

---

# 22. Updating Happy Bot

If you installed the project using Git:

```bash
git pull
```

Then update dependencies:

```bash
source .venv/bin/activate
python -m pip install -U discord.py
```

Restart the bot.

If you have local JSON data, keep your:

```text
guild_configs.json
tickets.json
blacklist.json
```

Back them up before replacing project files.

---

# 23. Troubleshooting

## `python` is not recognized on Windows

Try:

```powershell
py --version
```

If `py` works:

```powershell
py -m pip install -U discord.py
py happy_bot_clean.py
```

If neither command works, reinstall Python and enable:

**Add Python to PATH**

---

## `pip` is not recognized

Instead of:

```bash
pip install discord.py
```

use:

```bash
python -m pip install discord.py
```

Linux:

```bash
python3 -m pip install discord.py
```

---

## `ModuleNotFoundError: No module named 'discord'`

Install the package:

```bash
python -m pip install -U discord.py
```

Linux:

```bash
python3 -m pip install -U discord.py
```

Make sure you install it into the same Python environment that runs the bot.

---

## `Invalid token`

Check:

```python
TOKEN = "YOUR_TOKEN"
```

Make sure:

- The token is correct.
- There are no extra spaces.
- The token has not been regenerated.
- You are using the bot token, not the application ID.

If the token was publicly exposed, regenerate it.

---

## The bot is offline

Check the terminal.

Run:

```bash
python happy_bot_clean.py
```

If you are using systemd:

```bash
sudo systemctl status happybot
```

Then:

```bash
sudo journalctl -u happybot -n 100 --no-pager
```

---

## Slash commands do not appear

Make sure the bot was invited with the appropriate application command scope.

Reinvite the bot using your Discord Developer Portal installation settings.

Also make sure the bot is actually online.

Discord may take time to display command changes depending on how commands are synchronized.

---

## `/setup` does not work

Make sure you have the required server management permission.

The command is intended for server managers.

Also verify that:

- The staff role exists.
- The ticket category exists.
- The bot can view the category.
- The bot can create channels.

---

## Tickets cannot be created

Check the bot's permissions.

The bot needs to be able to:

- View the category
- Create channels
- Send messages
- Read message history
- Embed links
- Attach files
- Manage channel permissions

Also verify that `/setup` has already been run.

---

## The bot cannot create a ticket channel

Make sure the bot's highest role is positioned correctly in the server's role hierarchy.

Also check the category permissions.

The bot needs permission to manage channels.

---

## Transcripts do not work

Make sure the configured transcript channel still exists.

The bot needs permission to:

- View the channel
- Send messages
- Attach files
- Embed links

Run:

```text
/ticket-config
```

and verify the transcript channel.

---

# 24. Security

Treat your bot token like a password.

Never commit it to Git.

A recommended `.gitignore` is:

```gitignore
.venv/
__pycache__/
*.pyc
guild_configs.json
tickets.json
blacklist.json
.env
```

If you decide to publish your source code, make absolutely sure your real token is not included.

If a token has ever been exposed publicly:

1. Open the Discord Developer Portal.
2. Open your application.
3. Open **Bot**.
4. Reset/regenerate the token.
5. Replace the old token in your local file.
6. Restart Happy Bot.

---

# 25. GitHub

If you plan to publish Happy Bot on GitHub, initialize the repository:

```bash
git init
```

Add the files:

```bash
git add .
```

Create the first commit:

```bash
git commit -m "Initial Happy Bot release"
```

Connect your GitHub repository:

```bash
git remote add origin YOUR_REPOSITORY_URL
```

Push:

```bash
git branch -M main
git push -u origin main
```

Before pushing, check your source carefully for:

- Bot tokens
- Passwords
- API keys
- Private credentials
- Personal information

---

# 26. Development

Recommended development setup:

```text
HappyBot/
├── happy_bot_clean.py
├── README.md
├── .gitignore
├── guild_configs.json
├── tickets.json
└── blacklist.json
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it and install:

```bash
python -m pip install -U discord.py
```

Run:

```bash
python happy_bot_clean.py
```

---

# 27. Windows Quick Start

For a quick installation:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -U discord.py
```

Put your token in:

```python
TOKEN = "YOUR_BOT_TOKEN"
```

Then:

```powershell
python happy_bot_clean.py
```

---

# 28. Debian / Ubuntu Quick Start

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

Then:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U discord.py
python happy_bot_clean.py
```

---

# 29. Arch Quick Start

```bash
sudo pacman -Syu
sudo pacman -S python python-pip
```

Then:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U discord.py
python happy_bot_clean.py
```

---

# 30. Docker

Happy Bot can also be containerized.

A basic Dockerfile can look like:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -U discord.py

CMD ["python", "happy_bot_clean.py"]
```

Build:

```bash
docker build -t happy-bot .
```

Run:

```bash
docker run -d --name happy-bot happy-bot
```

For production use, make sure your JSON files are stored in a persistent volume so container recreation does not remove your bot data.

---

# 31. Windows Task Scheduler

If you want Happy Bot to start automatically on Windows:

1. Open **Task Scheduler**.
2. Create a new task.
3. Choose **Run whether user is logged on or not** if appropriate.
4. Add a trigger such as **At startup**.
5. Set the action to start Python.
6. Set the working directory to your Happy Bot folder.
7. Use your virtual environment Python executable.

Example executable:

```text
C:\HappyBot\.venv\Scripts\python.exe
```

Arguments:

```text
C:\HappyBot\happy_bot_clean.py
```

---

# 32. Updating Python Dependencies

You can check the installed version:

```bash
python -m pip show discord.py
```

Upgrade:

```bash
python -m pip install -U discord.py
```

Do not blindly upgrade every dependency in a production installation without testing first.

---

# 33. Data and Privacy

Happy Bot stores ticket-related information locally in JSON files.

The bot may store information necessary for its ticket functionality, including:

- Discord server IDs
- Discord user IDs
- Ticket IDs
- Ticket subjects
- Ticket descriptions
- Ticket status
- Claim information
- Ticket timestamps
- Transcript information

Server owners are responsible for handling and protecting the data stored by their own Happy Bot installation.

If you self-host Happy Bot, the data is stored on your own machine/server rather than in a Happy Bot-hosted database.

---

# 34. Open Source

Happy Bot is intended to be open source.

That means the source code can be:

- Inspected
- Modified
- Forked
- Self-hosted
- Improved
- Contributed to

Always check the repository's license before redistributing modified versions.

---

# 35. Common Commands Cheat Sheet

```text
/setup
```

Configure the ticket system.

```text
/ticket-panel
```

Create a ticket panel.

```text
/ticket-config
```

Configure ticket settings.

```text
/ticket-stats
```

View ticket statistics.

```text
/ticket-blacklist
```

Block or unblock members from opening tickets.

---

# 36. Recommended First Setup

After installing Happy Bot:

1. Create the Discord application.
2. Create the bot.
3. Enable Server Members Intent.
4. Copy the bot token.
5. Put the token into `happy_bot_clean.py`.
6. Install Python.
7. Create a virtual environment.
8. Install `discord.py`.
9. Invite the bot.
10. Start the bot.
11. Run `/setup`.
12. Select the staff role.
13. Select the ticket category.
14. Select a transcript channel if wanted.
15. Run `/ticket-panel`.
16. Send the panel to your support channel.
17. Test opening a ticket.
18. Test claiming the ticket.
19. Test transcripts.
20. Test closing the ticket.

---

# 37. Support / Contributions

If you find a bug, open an issue in the project's repository with:

- Operating system
- Python version
- `discord.py` version
- Error message
- Steps to reproduce the problem

Do not include your Discord bot token in bug reports.

Pull requests and improvements are welcome.

---

# License

Add your project's license here.

If you are publishing Happy Bot publicly, choose and include an appropriate open-source license before distributing the project.

---

## Happy Bot

**Free. Open source. Self-hosted.**

Built for communities that want full control over their support system.
