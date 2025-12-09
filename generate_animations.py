# generate_animations.py - simple headless Blender animation exporter
import bpy, sys, os
argv = sys.argv
if '--' in argv:
    outdir = argv[argv.index('--') + 1]
else:
    outdir = '/tmp'
os.makedirs(outdir, exist_ok=True)
arm_name = 'Armature'
arm = bpy.data.objects.get(arm_name)
if not arm:
    print('Armature not found:', arm_name)
else:
    # Create a simple idle animation by keyframing spine/head if available
    def keyframe_bone(bone_name, frames):
        pb = arm.pose.bones.get(bone_name)
        if not pb: return
        for f, rot in frames:
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = rot
            pb.keyframe_insert(data_path='rotation_euler', frame=f)
    idle_frames = {'spine': [(1,(0,0,0)), (30,(0.02,0,0)), (60,(0,0,0))], 'head': [(1,(0,0,0)), (30,(-0.02,0,0)), (60,(0,0,0))]}
    attack_frames = {'spine': [(1,(0,0,0)), (10,(0.6,0,0)), (20,(0,0,0))], 'head': [(1,(0,0,0)), (10,(0.2,0,0)), (20,(0,0,0))]}
    for bone, frames in idle_frames.items():
        keyframe_bone(bone, frames)
    action = bpy.data.actions.new('Idle_AI')
    arm.animation_data_create()
    arm.animation_data.action = action
    # Export selection (armature + meshes)
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.select_set(True)
    outname = os.path.join(outdir, 'Idle_AI.fbx')
    bpy.ops.export_scene.fbx(filepath=outname, use_selection=True, bake_anim=True, bake_anim_use_all_bones=True)
    print('Exported', outname)
