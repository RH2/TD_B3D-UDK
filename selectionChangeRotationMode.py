import bpy
for ob in bpy.context.selected_objects:
    a = 3
    if(a==1):
        ob.rotation_mode='QUATERNION'
    if(a==2):    
        ob.rotation_mode='XYZ'
    if(a==3):
        ob.rotation_mode='XZY'
    