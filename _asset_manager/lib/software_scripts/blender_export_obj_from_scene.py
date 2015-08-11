import bpy
import sys

file_path = sys.argv[-2]
export_path = sys.argv[-1]

bpy.ops.wm.open_mainfile(filepath=file_path)
bpy.ops.object.select_all(action='TOGGLE')
bpy.ops.object.shade_smooth()
bpy.ops.object.select_all(action='TOGGLE')
bpy.ops.object.shade_smooth()
bpy.ops.export_scene.obj(filepath=export_path, use_materials=False, use_mesh_modifiers=False, use_blen_objects=False, group_by_object=True)
