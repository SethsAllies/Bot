# Horror Game Project (Discord-driven Automation)

This project contains tools to automate parts of a hyper-realistic horror Roblox game pipeline.
It is designed to be triggered from a Discord bot which runs tasks locally (or on a server with Blender installed).

## Included tools
- `blender/anim_scripts/generate_animations.py` - Blender headless script that creates simple animations and exports FBX.
- `ai_agent/agent.py` - Orchestration script to run Blender and move outputs.
- `bot.py` - A Discord bot that exposes slash commands to trigger generation and return results.
- `requirements.txt` - Python dependencies for the bot and scripts.

## Usage (overview)
1. Install dependencies: `pip install -r requirements.txt`
2. Ensure Blender is installed and the `BLENDER_PATH` in `bot.py` is correct (or set environment variable).
3. Run the bot: `python bot.py`
4. Use the slash commands in your Discord server to generate animations or request the project ZIP.

**Security note:** The bot executes local commands (Blender, Python). Only run it in safe, trusted environments and never expose it to untrusted users.
