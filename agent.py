import os, shutil, subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
BLENDER = os.environ.get('BLENDER_PATH', r"C:\Program Files\Blender Foundation\Blender\blender.exe")
BLEND_SCRIPT = BASE / 'blender' / 'anim_scripts' / 'generate_animations.py'
BLEND_FILE = BASE / 'blender' / 'templates' / 'character_template.blend'
OUT_DIR = BASE / 'blender' / 'exported_fbx'
ROBO_ASSETS_ANIMS = BASE / 'robo_assets' / 'animations'

def run_blender():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cmd = [BLENDER, '--background', str(BLEND_FILE), '--python', str(BLEND_SCRIPT), '--', str(OUT_DIR)]
    print('Running Blender:', ' '.join(cmd))
    subprocess.check_call(cmd)
    print('Blender finished.')

def move_outputs():
    ROBO_ASSETS_ANIMS.mkdir(parents=True, exist_ok=True)
    for f in OUT_DIR.glob('*.fbx'):
        shutil.copy2(f, ROBO_ASSETS_ANIMS / f.name)
    print('Copied FBX to robo_assets/animations')

if __name__ == '__main__':
    try:
        run_blender()
    except Exception as e:
        print('Blender failed:', e)
    try:
        move_outputs()
    except Exception as e:
        print('Move failed:', e)
