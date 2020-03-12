import bpy
from math import radians
from mathutils import Matrix, Vector
from .functions import draw_text_line, draw_text, get_text_dimensions, get_safe_draw_x


def duplicate_radially(context, linked_count, spin_axis):
    ob = context.object
    ob_mx = ob.matrix_world
    cursor_loc = context.scene.cursor.location
    view3d = context.space_data
    dupli_obs = []
    
    if linked_count > 0:
        if spin_axis == 'LOCAL_X':
            rot_vec = (ob_mx[0][0], ob_mx[1][0], ob_mx[2][0])
        elif spin_axis == 'LOCAL_Y':
            rot_vec = (ob_mx[0][1], ob_mx[1][1], ob_mx[2][1])
        elif spin_axis == 'LOCAL_Z':
            rot_vec = (ob_mx[0][2], ob_mx[1][2], ob_mx[2][2])
        elif spin_axis == 'VIEW_Z':
            view_mx = view3d.region_3d.view_matrix
            rot_vec = Vector((0,0,1)) @ view_mx
            
        rot_angle = 360/linked_count
        for i in range(linked_count - 1):
            dupli_ob = ob.copy()
            ob.users_collection[0].objects.link(dupli_ob)
            dupli_obs.append(dupli_ob)
            
            if ob.parent:
                dupli_ob.parent = ob.parent
                dupli_ob.matrix_parent_inverse = ob.matrix_parent_inverse
            
            rot_mx = (Matrix.Translation(cursor_loc) @ Matrix.Rotation(radians(rot_angle*(i+1)), 4, rot_vec) @ Matrix.Translation(-cursor_loc))
            dupli_ob.matrix_world = rot_mx @ dupli_ob.matrix_world
            
            if view3d.local_view:
                dupli_ob.local_view_set(view3d, True)
                
    return dupli_obs
            

class OBJECT_OT_duplicate_radially(bpy.types.Operator):
    '''Add linked duplicates radially around the 3D cursor'''
    bl_idname = "object.duplicate_radially"
    bl_label = "Duplicate Radially"
    bl_options = {'REGISTER', 'UNDO'}
    
    linked_count: bpy.props.IntProperty(                        
        name = "Count",       
        default = 6,
        min = 1,
        description = "Total number of linked objects")
        
    spin_axis: bpy.props.EnumProperty(                        
        name = "Spin Axis", 
        items = [('LOCAL_X', "Local X", "Local X"),    
             ('LOCAL_Y', "Local Y", "Local Y"),    
             ('LOCAL_Z', "Local Z", "Local Z"), 
             ('VIEW_Z', "View Z", "View Z")],
        description = "Rotation axis",
        default = 'LOCAL_Z')
        
    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.area.type == 'VIEW_3D')

    def execute(self, context):
        duplicate_radially(context, self.linked_count, self.spin_axis)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_duplicate_radially_modal(bpy.types.Operator):
    '''Add linked duplicates radially around the 3D cursor'''
    bl_idname = "object.duplicate_radially_modal"
    bl_label = "Duplicate Radially Modal"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.area.type == 'VIEW_3D')
        
    linked_count: bpy.props.IntProperty(                        
        name = "Count",       
        default = 6,
        min = 1,
        description = "Total number of linked objects")
        
    spin_axis: bpy.props.EnumProperty(                        
        name = "Spin Axis", 
        items = [('LOCAL_X', "Local X", "Local X"),    
             ('LOCAL_Y', "Local Y", "Local Y"),    
             ('LOCAL_Z', "Local Z", "Local Z"), 
             ('VIEW_Z', "View Z", "View Z")],
        description = "Rotation axis",
        default = 'LOCAL_Z')
        
    def __init__(self):
        self.type_count = 0
        
    def invoke(self, context, event):
        self.dupli_obs = duplicate_radially(context, self.linked_count, self.spin_axis)
        
        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y

        context.window_manager.modal_handler_add(self)
        context.area.header_text_set("Total count: %s   Spin axis: %s" % (self.linked_count, self.spin_axis.title()))
        context.workspace.status_text_set(text="LMB, ENTER: Confirm | RMB, ESC: Cancel | X: Local X | Y: Local Y | Z: Local Z | V: View Z") 
        self.handler = context.space_data.draw_handler_add(self.draw_ui, (context,), 'WINDOW', 'POST_PIXEL')
        return {'RUNNING_MODAL'}

    def reduplicate(self, context):
        self.remove_duplicates(context)
        self.dupli_obs = duplicate_radially(context, self.linked_count, self.spin_axis)
        context.area.header_text_set("Total count: %s   Spin axis: %s" % (self.linked_count, self.spin_axis.title()))

    def modal(self, context, event):

        if event.value == 'PRESS':
            if event.type == 'MIDDLEMOUSE':
                return {'PASS_THROUGH'}
                
            elif event.type == 'WHEELUPMOUSE':
                self.linked_count += 1
                self.reduplicate(context)
                self.type_count = 0
                
            elif event.type == 'WHEELDOWNMOUSE':
                self.linked_count = max(2, self.linked_count-1)
                self.reduplicate(context)
                self.type_count = 0

            elif event.type in ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE'):
                digit = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE').index(event.type)
                if self.type_count == 0:
                    if digit == 0:
                        return {'RUNNING_MODAL'}
                    else:
                        self.linked_count = digit
                else:
                    self.linked_count = int(str(self.linked_count) + str(digit))
                self.type_count += 1
                self.reduplicate(context)
                
            elif event.type == 'BACK_SPACE':
                if self.type_count > 0:
                    self.linked_count = int(str(self.linked_count)[:-1]) if self.linked_count > 10 else 0
                    self.type_count -= 1
                    self.reduplicate(context)

            elif event.type == 'X':
                self.spin_axis = 'LOCAL_X'
                self.reduplicate(context)
                
            elif event.type == 'Y':
                self.spin_axis = 'LOCAL_Y'
                self.reduplicate(context)
        
            elif event.type == 'Z':
                self.spin_axis = 'LOCAL_Z'
                self.reduplicate(context)
                
            elif event.type == 'V':
                self.spin_axis = 'VIEW_Z'
                self.reduplicate(context)
        
            elif event.type in ('ESC', 'RIGHTMOUSE'):
                self.remove_duplicates(context)
                self.finish_modal(context)
                return {'CANCELLED'}
                
            elif event.type in ('SPACE', 'LEFTMOUSE'):
                self.finish_modal(context)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}
        
    def remove_duplicates(self, context):
        for ob in self.dupli_obs:
            bpy.data.objects.remove(ob, do_unlink=True)

    def finish_modal(self, context):
        context.area.header_text_set(text=None)
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()
        
    def draw_ui(self, context):
        ui_scale = context.preferences.view.ui_scale
    
        main_color = (1.0, 1.0, 1.0, 1.0)
        val_color = (*context.preferences.themes[0].view_3d.object_active, 1)
        key_color = context.preferences.themes[0].view_3d.face_select
        
        ui_width, ui_height = 250, 50
        ui_offset = 50*ui_scale
    
        font = 0
        font_size = int(18*ui_scale)
        align = "LEFT"
        
        safe_x, safe_y = get_safe_draw_x(context, ui_width + ui_offset), ui_height + ui_offset
        mouse_offset_x = self.mouse_region_x + ui_offset
        mouse_offset_y = self.mouse_region_y - ui_offset
        newline_x = min(safe_x, mouse_offset_x)
        newline_y = max(safe_y, mouse_offset_y)

        newline_y = draw_text_line([
            ("Total Count: ", main_color), 
            ("(Scroll) ", key_color),
            (str(self.linked_count), val_color)],
            newline_x, newline_y, align, font, font_size)

        newline_y = draw_text_line([
            ("Spin Axis: ", main_color), 
            ("(XYZV) ", key_color),
            (str(self.spin_axis.title()), val_color)],
            newline_x, newline_y, align, font, font_size)


classes = (
    OBJECT_OT_duplicate_radially,
    OBJECT_OT_duplicate_radially_modal
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
