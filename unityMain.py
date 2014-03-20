#########################
# UNITY-3D MODIFICATION #
#########################
import bpy
import bpy_extras
import copy
import math
import mathutils
from mathutils import Vector
from math import radians


TD_SCALE=1
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
    #all layers visible
        layerBool= list(bpy.context.scene.layers)
        for i in range(0,len(bpy.context.scene.layers)):
            bpy.context.scene.layers[i]=True 
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
    #go back to previous layer visibility    
        for i in range(0,len(bpy.context.scene.layers)):
            bpy.context.scene.layers[i]=layerBool[i]                       
        #negate transform adjustment
        for ob in go.objects:          
            ob.location[0]+=transformLocation[0]
            ob.location[1]+=transformLocation[1]
            ob.location[2]+=transformLocation[2]
            
            ob.rotation_euler[0]+=transformRotation[0]
            ob.rotation_euler[1]+=transformRotation[1]
            ob.rotation_euler[2]+=transformRotation[2]
                    
#exports instances into .lvl (xml file) scene format (only static mesh instances at the moment)
def instanceExport(context):
    print("UNITY>PLAYUP>LVL_FORMAT EXPORT BLOCK ------------------------------------------------")    
    TD_STRING="<?xml version="+'"1.0"'+" ?>\n<LEVELSETTINGS>\n\t<ENTITIES>\n"
    TD_TAG='"ExportedComponent"'
    
    bpy.ops.object.select_all(action="DESELECT")###TOGGLE/DESELECT/SELECT###
    bpy.ops.object.select_linked(extend=False, type='DUPGROUP')
    
    for ob in bpy.data.objects:
        if not hasattr(ob.dupli_group, "name"):
            print(ob.name+": was not an instance")
        else:
            TD_STRING+='\t\t<OBJECT NAME="'+ob.dupli_group.name+'" '
            exportLocation = copy.copy(ob.location)
            exportLocation.x *= 1.0
            exportLocation.y *= 1.0
            exportLocation.z *= 1.0 #swap the z and y axis.
            TD_STRING+='POSITION="'+str(exportLocation.x*TD_SCALE)+", "+str(exportLocation.z*TD_SCALE)+", "+str(exportLocation.y*TD_SCALE)+'" '
            bpy.context.scene.objects.active = ob
            previousRotationMode = ob.rotation_mode

            ob.rotation_mode='QUATERNION'
            obQuaternion=copy.copy(ob.rotation_quaternion)          
            ob_XYZ=copy.copy(obQuaternion.to_euler('XYZ'))
            ob_XYZ_QUATERNION=copy.copy(ob_XYZ.to_quaternion())
            export_matrix=bpy_extras.io_utils.axis_conversion(from_forward='-Y', from_up='Z', to_forward='-Z', to_up='Y')*copy.copy(ob_XYZ_QUATERNION.to_matrix())            
            ob_XZY_QUATERNION = export_matrix.to_quaternion()
            finalizedQ =copy.copy(ob_XZY_QUATERNION.normalized())
            qW = finalizedQ[0]
            qX = finalizedQ[1]
            qY = finalizedQ[2]
            qZ = finalizedQ[3]            
            TD_STRING+='ROTATION="'+str(qW)+", "+str(qX)+", "+str(qY)+", "+str(qZ)+'" '
            ob.rotation_mode='QUATERNION'
            ob.rotation_mode=previousRotationMode


            TD_STRING+='SCALE="'+str(ob.scale.x)+", "+str(ob.scale.y)+", "+str(ob.scale.z)+'" />\n'            
    TD_STRING+="\t</ENTITIES>\n</LEVELSETTINGS>"
    #print(TD_STRING)
    #bpy.context.window_manager.clipboard = TD_STRING
    
    #EXPORT string to file
    folder=bpy.context.scene['fbxFilePath']
    file=bpy.context.scene['lvlName']
    writebuffer = open(folder+"/"+file+".lvl",'w')
    writebuffer.write(TD_STRING)
    
class ToolsPanel(bpy.types.Panel):
    bl_label = "UNITY EXPORT UTILITY"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
 
    def draw(self, context):
        layout = self.layout
        row=layout.row()
        row.prop(context.scene, 'fbxFilePath')
        row=layout.row()
        row.prop(context.scene, 'lvlName')        
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
    bl_label = "EXPORT .LVL"
 
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
 
    def execute(self, context):
        instanceExport(context)
        return {'FINISHED'}
    
class OBJECT_OT_exportfbx(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "object.export_fbx"
    bl_label = "EXPORT .FBX (Groups)"
 
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
 
    def execute(self, context):
        bpy.ops.export_scene.fbx
        main(context)
        return {'FINISHED'}        
    
 
def register():
    bpy.types.Scene.fbxFilePath = bpy.props.StringProperty(subtype="DIR_PATH")
    bpy.types.Scene.lvlName = bpy.props.StringProperty()
    bpy.utils.register_module(__name__)
    bpy.utils.register_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)
def unregister():
    del(bpy.types.Scene.fbxFilePath)
    del(bpy.types.Scene.lvlName)
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)    
#bpy.utils.register_module(__name__)
if __name__ == "__main__":
    register()