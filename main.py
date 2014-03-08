import bpy
import math
from mathutils import Vector

TD_SCALE=50.000
#main function handles fbx export process. 
def main(context):
    print("FBX EXPORT BLOCK ------------------------------------------------")
    #for ob in context.scene.objects:
    #    print(ob)
    #goes through all groups
    for go in bpy.data.groups:
        transformLocation= Vector((0.00,0.00,0.00))
        transformRotation= Vector((0.00,0.00,0.00))


        #goes through all objects in this group
        #until it reaches a pivot object,
        #then it records transforms and ends the loop.  
        for ob in go.objects:
            nameSegments = ob.name.replace(".","_")
            nameSegments = nameSegments.split('_')#ob.name.split('_')

            for seg in nameSegments:
                if ( seg in [
                'pivot','Pivot','PIVOT',
                'transform','Transform',"TRANSFORM",
                'center',"Center","CENTER"]):
                    transformLocation[0] = ob.location[0]
                    transformLocation[1] = ob.location[1]
                    transformLocation[2] = ob.location[2]
                    transformRotation[0] = ob.rotation_euler[0]
                    transformRotation[1] = ob.rotation_euler[1]
                    transformRotation[2] = ob.rotation_euler[2]
                    break
                         
                #so.select=True
        #adjust transforms of each object in group
        bpy.ops.object.select_all(action='DESELECT')       
        for ob in go.objects:
            ob.select=True              
            ob.location[0]-=transformLocation[0]
            ob.location[1]-=transformLocation[1]
            ob.location[2]-=transformLocation[2]
            
            ob.rotation_euler[0]-=transformRotation[0]
            ob.rotation_euler[1]-=transformRotation[1]
            ob.rotation_euler[2]-=transformRotation[2]
        #export group to .fbx
        TD_FILEPATH=bpy.context.scene['fbxFilePath']+go.name+".fbx"
        bpy.ops.export_scene.fbx(check_existing=False,filepath=TD_FILEPATH,filter_glob="*.fbx",use_selection=True,global_scale=TD_SCALE,
        axis_forward='-Z',axis_up='Y',object_types={'LAMP', 'CAMERA', 'ARMATURE', 'EMPTY', 'MESH'},use_mesh_modifiers=True,mesh_smooth_type='FACE',
        use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO', batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)
        #negate transform adjustment
        for ob in go.objects:          
            ob.location[0]+=transformLocation[0]
            ob.location[1]+=transformLocation[1]
            ob.location[2]+=transformLocation[2]
            
            ob.rotation_euler[0]+=transformRotation[0]
            ob.rotation_euler[1]+=transformRotation[1]
            ob.rotation_euler[2]+=transformRotation[2]
                    
#exports instances into udk scene format (only static mesh instances at the moment)
def instanceExport(context):
    print("T3D EXPORT BLOCK ------------------------------------------------")    
    TD_STRING="Begin Map Name=MyMapName\n\tBegin Level NAME=PersistentLevel\n"
    TD_PACKAGE=bpy.context.scene['udkPackage']
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
            TD_STRING+="\t\tLocation=(X="+str(ob.location.x*TD_SCALE)+",Y="+str(-1*ob.location.y*TD_SCALE)+",Z="+str(ob.location.z*TD_SCALE)+")\n"
            #360/65536 65536=2^16=2bytes
            TD_STRING+="\t\tRotation=(Roll="+str(int(65535*(ob.rotation_euler.x/(math.pi*2))))+",Pitch="+str(int(65535*(ob.rotation_euler.y/(math.pi*2))))+",Yaw="+str(int(65535*(ob.rotation_euler.z/(math.pi*2))))+")\n" 
            TD_STRING+="\t\tDrawScale3D=(X="+str(ob.scale.x)+",Y="+str(ob.scale.y)+",Z="+str(ob.scale.z)+")\n"
            TD_STRING+="\t\tTag="+TD_TAG+"\n"
            TD_STRING+="\t\tEnd Actor\n"
    TD_STRING+="\tEnd Level\n"
    TD_STRING+="End Map\n"
    print(TD_STRING)
    bpy.context.window_manager.clipboard = TD_STRING

class ToolsPanel(bpy.types.Panel):
    bl_label = "UDK EXPORT UTILITY"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
 
    def draw(self, context):
        layout = self.layout
        row=layout.row()
        row.prop(context.scene, 'fbxFilePath')
        row=layout.row()
        row.prop(context.scene, 'udkPackage')        
        row=layout.row()
       #row.operator("operator's bl_idname", icon="")
        row.operator("object.export_instance",icon="STICKY_UVS_DISABLE")
        row=layout.row()
        row.operator("object.export_fbx",icon="STICKY_UVS_LOC")
 
        #do: layout.prop(object, 'propertyname') where the property is of type StringProperty with subtype='DIR_PATH'
        # or FILE_PATH i think, depending which one you want
 
 
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
    bpy.types.Scene.fbxFilePath = bpy.props.StringProperty(subtype="DIR_PATH")
    bpy.types.Scene.udkPackage = bpy.props.StringProperty()
    bpy.utils.register_module(__name__)
    bpy.utils.register_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)
def unregister():
    del(bpy.types.Scene.fbxFilePath)
    del(bpy.types.Scene.udkPackage)
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)    
#bpy.utils.register_module(__name__)
if __name__ == "__main__":
    register()