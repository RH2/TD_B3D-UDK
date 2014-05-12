import bpy
import math
from mathutils import Vector
import copy
import bpy_extras
#main function handles fbx export process. 
def main(context):
    print("FBX EXPORT BLOCK ------------------------------------------------")
    #for ob in context.scene.objects:
    #    print(ob)
    #goes through all groups
    for go in bpy.data.groups:
        go.name = go.name.replace(".","_")
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
        TD_SCALE=bpy.context.scene['tdscale']
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
                    
#exports instances into udk scene format (only static mesh instances at the moment)
def instanceExport(context):
    print("T3D EXPORT BLOCK ------------------------------------------------")  
    TD_SCALE=bpy.context.scene['tdscale']  
    #TD_STRING="Begin Map Name=MyMapName\n\tBegin Level NAME=PersistentLevel\n"
    TD_STRING="Begin Map\n"
    TD_PACKAGE=bpy.context.scene['udkPackage']
    TD_TAG='"StaticMeshActor"'
    
    #begin exporting group instances
    #copy to buffer?
    
    #old style selection
    #bpy.ops.object.select_all(action="DESELECT")###TOGGLE/DESELECT/SELECT###
    #bpy.ops.object.select_linked(extend=False, type='DUPGROUP')
    
    
    for ob in bpy.context.selected_objects:
        ob.rotation_mode='QUATERNION'
        obQuaternion=copy.copy(ob.rotation_quaternion.normalized())
        obXYZ=copy.copy(obQuaternion.to_euler('XYZ'))
            
            
        rollNum=     int(math.ceil(65535*((obXYZ.x%(2*math.pi))/(math.pi*2))))
        pitchNum= -1*int(math.ceil(65535*((obXYZ.y%(2*math.pi))/(math.pi*2))))
        yawNum=   -1*int(math.ceil(65535*((obXYZ.z%(2*math.pi))/(math.pi*2))))
        ob.rotation_mode='XYZ'
        #ob.rotation_euler[0]=int(obXYZ[0])
        #ob.rotation_euler[1]=int(obXYZ[1])
        #ob.rotation_euler[2]=int(obXYZ[2])
        
        
        
        if not hasattr(ob.dupli_group, "name"):
            print(ob.name+": was not an instance")
        else:
            print(ob.dupli_group.name)
            TD_STRING+="Begin Actor Class=StaticMeshActor Name="+ob.name+ob.dupli_group.name+"\n"
            TD_STRING+="\tStaticMesh=StaticMesh'"+TD_PACKAGE+"."+ob.dupli_group.name+"'\n"
            #bLightchanged=
            #Level=
            #Region=
            TD_STRING+="\tTag="+TD_TAG+"\n"
           
            #PhysicsVolume=
            isWall=False
            nameSegments = ob.dupli_group.name.replace(".","_")
            nameSegments = nameSegments.split('_')#ob.name.split('_')
            for seg in nameSegments:
                if ( seg in ['wall','Wall','WALL']):
                    isWall = True
            if isWall==False:
                TD_STRING+="\tLocation=(X="+str(ob.location.x*TD_SCALE)+",Y="+str(-1*ob.location.y*TD_SCALE)+",Z="+str(ob.location.z*TD_SCALE)+")\n"
            if isWall==True:
                if (yawNum>=65530 or yawNum<=10):#0||360#forward
                    TD_STRING+="\tLocation=(X="+str((ob.location.x+0.08)*TD_SCALE)+",Y="+str(-1*(ob.location.y-0.04)*TD_SCALE)+",Z="+str(ob.location.z*TD_SCALE)+")\n"        
                if (yawNum<=32790 and yawNum>=32750) or (yawNum<=-32790 and yawNum>=-32750) :#180#back   
                    TD_STRING+="\tLocation=(X="+str((ob.location.x+0)*TD_SCALE)+",Y="+str(-1*(ob.location.y-0.04)*TD_SCALE)+",Z="+str(ob.location.z*TD_SCALE)+")\n"        
                if (yawNum<=16390 and yawNum>=16380) or (yawNum<=-65540 and yawNum>=-65530):#90#left  16383.75 -270
                    TD_STRING+="\tLocation=(X="+str((ob.location.x+0.04)*TD_SCALE)+",Y="+str(-1*(ob.location.y+0)*TD_SCALE)+",Z="+str(ob.location.z*TD_SCALE)+")\n"        
                if (yawNum<=65540 and yawNum>=65530) or (yawNum<=-16390 and yawNum>=-16380):#270||-90#right   65535
                    TD_STRING+="\tLocation=(X="+str((ob.location.x+0.04)*TD_SCALE)+",Y="+str(-1*(ob.location.y-0.08)*TD_SCALE)+",Z="+str(ob.location.z*TD_SCALE)+")\n"        
            #360/65536 65536=2^16=2bytes
            isWall = False
            
            
           

            if (rollNum!=0)or(pitchNum!=0)or(yawNum!=0):
                TD_STRING+="\tRotation=(" 
                if rollNum!=0:
                    TD_STRING+="Roll="+str(rollNum)
                if pitchNum!=0:
                    if rollNum == 0:
                        TD_STRING+="Pitch="+str(pitchNum)
                    else:
                        TD_STRING+=", "+"Pitch="+str(pitchNum)
                if yawNum!=0:
                    if (rollNum==0 and pitchNum==0):
                        TD_STRING+="Yaw="+str(yawNum)
                    else:
                        TD_STRING+=", "+"Yaw="+str(yawNum) 
                TD_STRING+=")\n"
            TD_STRING+="\tDrawScale3D=(X="+str(ob.scale.x)+",Y="+str(ob.scale.y)+",Z="+str(ob.scale.z)+")\n"
            TD_STRING+="\tColLocation=(X="+str(ob.location.x*TD_SCALE)+",Y="+str(-1*ob.location.y*TD_SCALE)+",Z="+str(ob.location.z*TD_SCALE)+")\n"            
            #bSelected
            
            TD_STRING+="End Actor\n"
    #TD_STRING+="\tEnd Level\n"
    TD_STRING+="Begin Surface\nEnd Surface\n"
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
        row.prop(context.scene, "tdscale")
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
    bpy.types.Scene.tdscale = bpy.props.FloatProperty(name="Scale", description="Export Scale", default=50.0, min=0.001, max=1000)
    bpy.types.Scene.fbxFilePath = bpy.props.StringProperty(subtype="DIR_PATH")
    bpy.types.Scene.udkPackage = bpy.props.StringProperty()
    bpy.utils.register_module(__name__)
    bpy.utils.register_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)
def unregister():
    del(bpy.types.Scene.tdscale)
    del(bpy.types.Scene.fbxFilePath)
    del(bpy.types.Scene.udkPackage)
    bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(OBJECT_OT_exportinstance)
    bpy.utils.register_class(OBJECT_OT_exportfbx)    
#bpy.utils.register_module(__name__)
if __name__ == "__main__":
    register()