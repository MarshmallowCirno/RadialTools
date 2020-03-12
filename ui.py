import bpy

class RADTOOLS_PT_sidebar(bpy.types.Panel):
    bl_label = "Radial Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.mode == 'OBJECT')

    def draw(self, context):
        layout = self.layout
        layout.operator("object.duplicate_radially_modal", text="Duplicate Radially", icon='CURVE_NCIRCLE')
        layout.operator("object.radial_array_modal", text="Radial Array", icon='PHYSICS')
       

classes = (
    RADTOOLS_PT_sidebar,
)

        
def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
