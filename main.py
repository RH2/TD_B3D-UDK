import bpy
 
#main function handles fbx export process. 
def main(context):
    print("FBX EXPORT BLOCK ------------------------------------------------")
    #for ob in context.scene.objects:
    #    print(ob)
    #goes through all groups
    for go in bpy.data.groups:
        print(go) 
        noTransform=True    #controls the while loop 
        transformLocation=[0.000,0.000,0.000]
        transformRotation=[0.000,0.000,0.000]
        
        while(noTransform):  
        #goes through all objects in this group
        #until it reaches a pivot object,
        #then it records transforms and ends the loop.  
           for ob in go.objects:
                print(ob.name)
                nameSegments = ob.name.split("_",".")
                for seg in nameSegments:
                    if ( seg in ['pivot', 'transform', 'center']):
                        transformLocation=ob.location
                        transformRotation=ob.rotation_euler
                        noTransform=False
                         
                #so.select=True
        #adjust transforms of each object in group        
        for ob in go.objects:
            ob.location[0]=ob.location[0] - transformLocation[0]
            ob.location[1]=ob.location[1] - transformLocation[1]
            ob.location[2]=ob.location[2] - transformLocation[2]
            
            ob.rotation_euler[0]=ob.rotation_euler[0] - transformRotation[0]
            ob.rotation_euler[1]=ob.rotation_euler[1] - transformRotation[1]
            ob.rotation_euler[2]=ob.rotation_euler[2] - transformRotation[2]
        #export group to .fbx
        #TODO
            #
            #
        #negate transform adjustment
        for ob in go.objects:
            ob.location[0]=ob.location[0] + transformLocation[0]
            ob.location[1]=ob.location[1] + transformLocation[1]
            ob.location[2]=ob.location[2] + transformLocation[2]
            
            ob.rotation_euler[0]=ob.rotation_euler[0] + transformRotation[0]
            ob.rotation_euler[1]=ob.rotation_euler[1] + transformRotation[1]
            ob.rotation_euler[2]=ob.rotation_euler[2] + transformRotation[2]
                    
#exports instances into udk scene format (only static mesh instances at the moment)
def instanceExport(context):
    print("T3D EXPORT BLOCK ------------------------------------------------")    
    TD_STRING="Begin Map Name=MyMapName\n\tBegin Level NAME=PersistentLevel\n"
    TD_PACKAGE="BATCHIMPORTTHING_PACKAGENAME"
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
            TD_STRING+="\t\tBegin Actor Class=StaticMeshActor Name="+ob.dupli_group.name+" Archetype=StaticMeshActor'Engine.Default__StaticMeshActor'\n"
            TD_STRING+="\t\tBegin Object Class=StaticMeshComponent Name=StaticMeshComponent0 Archetype=StaticMeshComponent'Engine.Default__StaticMeshActor:StaticMeshComponent0'\n"
            TD_STRING+="\t\tStaticMesh=StaticMesh'"+TD_PACKAGE+"."+ob.dupli_group.name+"'\n"
            TD_STRING+="\t\tEnd Object\n"
            TD_STRING+="\t\tLocation=(X="+str(bpy.data.objects['Group'].location.x)+",Y="+str(bpy.data.objects['Group'].location.y)+",Z="+str(bpy.data.objects['Group'].location.z)+")\n"
            TD_STRING+="\t\tRotation=(Roll="+str(bpy.data.objects['Group'].rotation_euler.x)+",Pitch="+str(bpy.data.objects['Group'].rotation_euler.y)+",Yaw="+str(bpy.data.objects['Group'].rotation_euler.z)+")\n"
            TD_STRING+="\t\tDrawScale3D=(X="+str(bpy.data.objects['Group'].scale.x)+",Y="+str(bpy.data.objects['Group'].scale.y)+",Z="+str(bpy.data.objects['Group'].scale.z)+")\n"
            TD_STRING+="\t\tTag="+TD_TAG+"\n"
            TD_STRING+="\t\tEnd Actor\n"
    TD_STRING+="\tEnd Level\n"
    TD_STRING+="End Map\n"
    print(TD_STRING)

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