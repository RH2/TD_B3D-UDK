import bpy
if (bpy.context.active_object.dupli_type == 'GROUP'):
    if hasattr(bpy.context.active_object.dupli_group, "name"):
        GroupType = bpy.context.active_object.dupli_group
        for ob in bpy.context.selected_objects:
            ob.dupli_type='GROUP'
            ob.dupli_group = GroupType 