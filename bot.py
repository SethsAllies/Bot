import os
import asyncio
import subprocess
import shlex
from pathlib import Path
import discord
from discord.ext import commands
from discord import app_commands

# --- Configuration ---
# Either set BLENDER_PATH env var or edit the path below.
BLENDER_PATH = os.environ.get('BLENDER_PATH', r"C:\Program Files\Blender Foundation\Blender\blender.exe")
PROJECT_DIR = Path(__file__).resolve().parents[0]
BLEND_FILE = PROJECT_DIR / 'blender' / 'templates' / 'character_template.blend'
BLEND_SCRIPT = PROJECT_DIR / 'blender' / 'anim_scripts' / 'generate_animations.py'
OUT_DIR = PROJECT_DIR / 'blender' / 'exported_fbx'
ZIP_PATH = PROJECT_DIR / 'HorrorGameProject_with_bot.zip'

# Bot token must be provided as environment variable DISCORD_BOT_TOKEN
DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')  # <-- set this in your environment

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Helper: run a subprocess asynchronously
async def run_subprocess(cmd_args, cwd=None, timeout=300):
    proc = await asyncio.create_subprocess_exec(*cmd_args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=cwd)
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return False, 'Timeout', ''
    return proc.returncode == 0, stdout.decode('utf-8', errors='ignore'), stderr.decode('utf-8', errors='ignore')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (id: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands.')
    except Exception as e:
        print('Failed to sync commands:', e)

# Slash command: generate animations using Blender (headless)
@bot.tree.command(name='generate_animations', description='Run Blender headless to generate FBX animations from template')
async def generate_animations(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    # Ensure output dir exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not BLEND_FILE.exists():
        await interaction.followup.send('Error: blend template not found at: ' + str(BLEND_FILE))
        return

    if not BLEND_SCRIPT.exists():
        await interaction.followup.send('Error: blender script not found at: ' + str(BLEND_SCRIPT))
        return

    cmd = [BLENDER_PATH, '--background', str(BLEND_FILE), '--python', str(BLEND_SCRIPT), '--', str(OUT_DIR)]
    success, stdout, stderr = await run_subprocess(cmd, cwd=str(PROJECT_DIR), timeout=240)
    if not success:
        await interaction.followup.send(f'Blender failed. Stderr:\n```
{stderr[:1900]}
```')
        return

    # Create a zip of the exported FBX files to return
    zip_name = PROJECT_DIR / 'exported_animations.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in OUT_DIR.glob('*.fbx'):
            zf.write(f, f.name)

    await interaction.followup.send('Animations generated successfully. Download the zip:', file=discord.File(str(zip_name)))

# Slash command: run the orchestration agent (calls agent.py)
@bot.tree.command(name='run_agent', description='Run the local orchestration agent (agent.py) to build and move assets')
async def run_agent(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    agent_script = PROJECT_DIR / 'ai_agent' / 'agent.py'
    if not agent_script.exists():
        await interaction.followup.send('Error: agent.py not found.')
        return
    cmd = [shlex.split(f'python "{agent_script}"')[0], str(agent_script)]
    success, stdout, stderr = await run_subprocess(cmd, cwd=str(PROJECT_DIR), timeout=240)
    if not success:
        await interaction.followup.send(f'Agent failed. Stderr:\n```
{stderr[:1900]}
```')
        return
    await interaction.followup.send('Agent ran successfully. Outputs moved to robo_assets/animations (if any).')

# Slash command: get full project zip
@bot.tree.command(name='get_project_zip', description='Get the full project ZIP file')
async def get_project_zip(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    # Recreate zip to include latest files
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(PROJECT_DIR):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, PROJECT_DIR)
                zf.write(full, rel)
    await interaction.followup.send('Here is the full project ZIP:', file=discord.File(str(ZIP_PATH)))

if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print('Error: DISCORD_BOT_TOKEN environment variable not set. Exiting.')
    else:
        bot.run(DISCORD_TOKEN)
