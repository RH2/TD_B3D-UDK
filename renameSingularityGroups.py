import bpy

for go in bpy.data.groups:
    if go.users==1:
        for ob in go.objects:
            if hasattr(ob, "name"):
                go.name=ob.name
                
            else:
                print("object had no name")