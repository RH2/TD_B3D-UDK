#public domain Richard Hale ©2014

import bpy
 
#main function handles fbx export process. 
def main(context):
    print("TEST")
    #for ob in context.scene.objects:
    #    print(ob)
    #goes through all groups
    for ob in bpy.data.groups:
        print(ob) 
        noTransform=True
        transformLocation=[0.000,0.000,0.000]
        transformRotation=[0.000,0.000,0.000]
        
        while(noTransform):  
        #goes through all objects in this group
        #until it reaches a pivot object,
        #then it records transforms and ends the loop.  
            for so in ob.objects:
                print(so.name)
                #nameSegments = bpy.context.object.name.split("_")
                nameSegments = so.name.split("_")
                for seg in nameSegments:
                    if (seg=="pivot"):
                        transformLocation=bpy.context.object.location
                        transformRotation=bpy.context.object.rotation_euler
                        noTransform=False
                    elif(seg=="transform"):
                        transformLocation=bpy.context.object.location
                        transformRotation=bpy.context.object.rotation_euler
                        noTransform=False 
                    elif(seg=="center"):
                        transformLocation=bpy.context.object.location
                        transformRotation=bpy.context.object.rotation_euler
                        noTransform=False                
                #so.select=True
        #adjust transforms of each object in group        
        for so in ob.objects:
            so.location[0]=so.location[0] - transformLocation[0]
            so.location[1]=so.location[1] - transformLocation[1]
            so.location[2]=so.location[2] - transformLocation[2]
            
            so.rotation_euler[0]=so.rotation_euler[0] - transformRotation[0]
            so.rotation_euler[1]=so.rotation_euler[1] - transformRotation[1]
            so.rotation_euler[2]=so.rotation_euler[2] - transformRotation[2]
        #export group to .fbx
        #TODO
            #
            #
        #negate transform adjustment
        for so in ob.objects:
            so.location[0]=so.location[0] + transformLocation[0]
            so.location[1]=so.location[1] + transformLocation[1]
            so.location[2]=so.location[2] + transformLocation[2]
            
            so.rotation_euler[0]=so.rotation_euler[0] + transformRotation[0]
            so.rotation_euler[1]=so.rotation_euler[1] + transformRotation[1]
            so.rotation_euler[2]=so.rotation_euler[2] + transformRotation[2]
                    
def instanceExport(context):
    print("export to .t3d")
    
    TD_STRING="Begin Map Name=MyMapName\n\tBegin Level NAME=PersistentLevel\n"
    TD_PACKAGE=""
    TD_TAG='"ExportedComponent"'
    
    #begin exporting group instances
    #copy to buffer?
    bpy.ops.object.select_all(action="DESELECT")###TOGGLE/DESELECT/SELECT###
    bpy.ops.object.select_linked(extend=False, type='DUPGROUP')
    
    for ob in bpy.data.objects:
        if not hasattr(ob.dupli_group, "name"):
            print(ob.name+": was not an instance")
        else:
            print(ob.dupli_group.name)
            TD_STRING+="\tBegin Actor Class=StaticMeshActor Name="+ob.dupli_group.name+" Archetype=StaticMeshActor'Engine.Default__StaticMeshActor'\n"
            TD_STRING+="\t\tBegin Object Class=StaticMeshComponent Name=StaticMeshComponent0 Archetype=StaticMeshComponent'Engine.Default__StaticMeshActor:StaticMeshComponent0'\n"
            TD_STRING+="\t\tStaticMesh=StaticMesh'"+TD_PACKAGE+"."+ob.dupli_group.name+"'\n"
            TD_STRING+="\t\tEnd Object\n"
            TD_STRING+="\t\tLocation=(X="+bpy.data.objects['Group'].location.x+",Y="+bpy.data.objects['Group'].location.y+",Z="+bpy.data.objects['Group'].location.z+")\n"
            TD_STRING+="\t\tRotation=(Roll="+bpy.data.objects['Group'].rotation_euler.x+",Pitch="+bpy.data.objects['Group'].rotation_euler.y+",Yaw="+bpy.data.objects['Group'].rotation_euler.z+")\n"
            TD_STRING+="\t\tDrawScale3D=(X="+bpy.data.objects['Group'].scale.x+",Y="+bpy.data.objects['Group'].scale.y+",Z="+bpy.data.objects['Group'].scale.z+")\n"
            TD_STRING+="\tTag="+TD_TAG+"\n"
            TD_STRING+="\t\tEnd Actor\n"
    TD_STRING+="\tEnd Level\n"
    TD_STRING+="End Map\n"

class ToolsPanel(bpy.types.Panel):
    bl_label = "UDK EXPORT UTILITY"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        layout = self.layout
        row=layout.row()
       #row.operator("operator's bl_idname", icon="")
        row.operator("object.export_instance",icon="STICKY_UVS_DISABLE")
        row=layout.row()
        row.operator("object.export_fbx",icon="STICKY_UVS_LOC")
 
 
 
class OBJECT_OT_exportinstance(bpy.types.Operator):
    '''Click on ME'''
    bl_idname = "object.export_instance"
    bl_label = "EXPORT .T3D"
 
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
 
    def execute(self, context):
        instanceExport(context)
        return {'FINISHED'}
    
class OBJECT_OT_exportfbx(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "object.export_fbx"
    bl_label = "EXPORT .FBX"
 
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
 
    def execute(self, context):
        print("dis fbx button_update running")
        bpy.ops.export_scene.fbx
        main(context)
        return {'FINISHED'}        
    
 
def register():
    bpy.utils.register_module(__name__)
    bpy.utils.register_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)
    
#bpy.utils.register_module(__name__)
if __name__ == "__main__":
    register()