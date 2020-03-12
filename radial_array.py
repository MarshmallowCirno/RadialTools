import bpy
from math import radians
from mathutils import Matrix, Vector
from .functions import draw_text_line, draw_text, get_text_dimensions, get_safe_draw_x


def get_radial_array(ob):
    array = None
    for mod in reversed(ob.modifiers):
        if mod.type == 'ARRAY' and "Radial Array" in mod.name:
            array = mod
            break
    return array
    
    
def sort_array(ob, array):
    array_pos = ob.modifiers.find(array.name)
    others_ob_mods = list(reversed(ob.modifiers[:-1]))
    
    mirror = None
    for mod in others_ob_mods:
        if mod.type == 'MIRROR' and mod.mirror_object is None:
            mirror = mod
            mirror_pos = ob.modifiers.find(mirror.name)
            break
            
    another_array = None
    for mod in others_ob_mods:
        if mod.type == 'ARRAY':
            another_array = mod
            another_array_pos = ob.modifiers.find(another_array.name)
            break

    def move_mod_up(mod, iters):
        for i in range(iters):
            bpy.ops.object.modifier_move_up(modifier=mod.name)

    if another_array is not None:
        iters = array_pos - another_array_pos - 1 # right after array
        move_mod_up(array, iters)
    elif mirror is not None:
        iters = array_pos - mirror_pos - 1 # right after mirror
        move_mod_up(array, iters)
    else:
        iters = array_pos 
        move_mod_up(array, iters) # top
        

def add_radial_array(context, segments, spin_axis, force_new, center_on_cursor):
    view3d = context.space_data
    ob = context.object
    ob_mx = ob.matrix_world
    ob_loc = ob_mx.translation
    cursor_loc = context.scene.cursor.location
    
    array_center = cursor_loc if center_on_cursor else ob_loc

    # Adjust modifiers
    array = get_radial_array(ob)
    if array is None or force_new:
        array = ob.modifiers.new(name="Radial Array", type='ARRAY')
        array.use_object_offset = True
        array.use_relative_offset = False
        array.use_merge_vertices = True
        array.use_merge_vertices_cap = True
        array.merge_threshold = 0.0001/context.scene.unit_settings.scale_length # .1mm

        sort_array(ob, array)

    array.count = segments

    # Get / add empty
    empty = array.offset_object
    if not empty:
        empty = bpy.data.objects.new(ob.name + " [Array Helper]", None)
        empty.empty_display_type = 'SPHERE'

        # Calculate empty radius - distance from the bounding box center of the mesh to the object origin
        def get_mesh_center(ob):
            vcos = [ob.matrix_world @ v.co for v in ob.data.vertices]
            find_center = lambda l: ( max(l) + min(l) ) / 2

            x,y,z  = [[v[i] for v in vcos] for i in range(3)]
            mesh_center = Vector(([find_center(axis) for axis in [x,y,z]]))
            return mesh_center
           
        empty.empty_display_size = (get_mesh_center(ob) - array_center).length*.75
        
        ob.users_collection[0].objects.link(empty)
        if view3d.local_view:
            empty.local_view_set(view3d, True)
        
        array.offset_object = empty
    
    # Get matrices and spin vector
    if spin_axis == 'LOCAL_X':
        spin_vec = (ob_mx[0][0], ob_mx[1][0], ob_mx[2][0])
    elif spin_axis == 'LOCAL_Y':
        spin_vec = (ob_mx[0][1], ob_mx[1][1], ob_mx[2][1])
    elif spin_axis == 'LOCAL_Z':
        spin_vec = (ob_mx[0][2], ob_mx[1][2], ob_mx[2][2])
    elif spin_axis == 'VIEW_Z':
        view_mx = view3d.region_3d.view_matrix
        spin_vec = Vector((0,0,1)) @ view_mx
     
    # Transform empty
    empty.matrix_world = ob_mx
    empty.scale = 1,1,1

    spin_angle = 360/segments
    spin_mx = (Matrix.Translation(array_center) @ Matrix.Rotation(radians(spin_angle), 4, spin_vec) @ Matrix.Translation(-array_center))
    empty.matrix_world = spin_mx @ empty.matrix_world
    
    return empty, array


class OBJECT_OT_radial_array(bpy.types.Operator):
    bl_description = ("LMB: Edit radial array or add a new one if it doesn't exist.\n"
    "+ Shift: Add a new radial array instead of trying to edit existing.\n"
    "+ Ctrl: Set array center to the 3D cursor instead of object pivot")
    bl_idname = "object.add_radial_array"
    bl_label = "Radial Array"
    bl_options = {'REGISTER', 'UNDO'}
    
    segments: bpy.props.IntProperty(                        
        name = "Segments",       
        default = 6,
        min = 1,
        description = "Number of segments")
        
    spin_axis: bpy.props.EnumProperty(                        
        name = "Spin Axis", 
        items = [('LOCAL_X', "Local X", "Local X"),
             ('LOCAL_Y', "Local Y", "Local Y"),
             ('LOCAL_Z', "Local Z", "Local Z"),
             ('VIEW_Z', "View Z", "View Z")],
        description = "Spin axis",
        default = 'LOCAL_Z')
        
    force_new: bpy.props.BoolProperty(                        
        name = "Force New Modifier",       
        default = False,
        description = "Add a new radial array modifier instead of trying to pick up and edit existing")
        
    center_on_cursor: bpy.props.BoolProperty(                        
        name = "Center on Cursor",       
        default = False,
        description = "Set the center of the radial array to the 3D cursor location")
        
    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.area.type == 'VIEW_3D' and context.object.type in ('MESH', 'CURVE'))

    def execute(self, context):
        add_radial_array(context, self.segments, self.spin_axis, self.force_new, self.center_on_cursor)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_radial_array_modal(bpy.types.Operator):
    bl_description = ("LMB: Edit radial array or add a new one if it doesn't exist.\n"
    "+ Shift: Add a new radial array instead of trying to edit existing.\n"
    "+ Ctrl: Set array center to the 3D cursor instead of object pivot")
    bl_idname = "object.radial_array_modal"
    bl_label = "Radial Array Modal"
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}
    
    segments: bpy.props.IntProperty(                        
        name = "Segments",       
        default = 6,
        min = 1,
        description = "Number of segments",
        options={'SKIP_SAVE'} )
        
    spin_axis: bpy.props.EnumProperty(                        
        name = "Spin Axis", 
        items = [('LOCAL_X', "Local X", "Local X"),
             ('LOCAL_Y', "Local Y", "Local Y"),
             ('LOCAL_Z', "Local Z", "Local Z"),
             ('VIEW_Z', "View Z", "View Z")],
        description = "Spin axis",
        default = 'LOCAL_Z')
        
    force_new: bpy.props.BoolProperty(                        
        name = "Force New Modifier",       
        default = False,
        description = "Add a new radial array modifier instead of trying to pick up and edit existing")
        
    center_on_cursor: bpy.props.BoolProperty(                        
        name = "Center on Cursor",       
        default = False,
        description = "Set the center of the radial array to the 3D cursor location")
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.area.type == 'VIEW_3D' and context.object.type in ('MESH', 'CURVE'))
        
    def __init__(self):
        self.type_count = 0

    def get_init_array(self, context):
        init_array = None
        init_array_count = None
        init_empty = None
        init_empty_mx = None
    
        ob = context.object
        init_array = get_radial_array(ob)
        if init_array is not None:
            init_array_count = init_array.count
            init_empty = init_array.offset_object
            if init_empty is not None:
                init_empty_mx = init_empty.matrix_world.copy()
                
        return init_array, init_array_count, init_empty, init_empty_mx
        
    def invoke(self, context, event):
        self.force_new = event.shift 
        self.center_on_cursor = event.ctrl

        if not self.force_new:
            self.init_array, self.init_array_count, self.init_empty, self.init_empty_mx = self.get_init_array(context)
            if self.init_array is not None:
                self.segments = self.init_array_count

        self.empty, self.array = add_radial_array(context, self.segments, self.spin_axis, self.force_new, self.center_on_cursor)
        
        self.mouse_region_x = event.mouse_region_x
        self.mouse_region_y = event.mouse_region_y
        
        context.window_manager.modal_handler_add(self)
        context.area.header_text_set("Segments: %s   Spin Axis: %s" % (self.segments, self.spin_axis.title()))
        context.workspace.status_text_set(text="LMB, ENTER: Confirm | RMB, ESC: Cancel | X: Local X | Y: Local Y | Z: Local Z | V: View Z | Del: Delete active array") 
        self.handler = context.space_data.draw_handler_add(self.draw_ui, (context,), 'WINDOW', 'POST_PIXEL')
        return {'RUNNING_MODAL'}
        
    def update_array(self, context):
        add_radial_array(context, self.segments, self.spin_axis, False, self.center_on_cursor)
        context.area.header_text_set("Segments: %s   Spin Axis: %s" % (self.segments, self.spin_axis.title()))
    
    def modal(self, context, event):
        if event.value == 'PRESS':
            if event.type == 'MIDDLEMOUSE':
                return {'PASS_THROUGH'}
                
            elif event.type == 'WHEELUPMOUSE':
                self.segments += 1
                self.update_array(context)
                self.type_count = 0
                
            elif event.type == 'WHEELDOWNMOUSE':
                self.segments = max(2, self.segments-1)
                self.update_array(context)
                self.type_count = 0
                
            elif event.type in ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE'):
                digit = ('ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE').index(event.type)
                if self.type_count == 0:
                    if digit == 0:
                        return {'RUNNING_MODAL'}
                    else:
                        self.segments = digit
                else:
                    self.segments = int(str(self.segments) + str(digit))
                self.type_count += 1
                self.update_array(context)
                
            elif event.type == 'BACK_SPACE':
                if self.type_count > 0:
                    self.segments = int(str(self.segments)[:-1]) if self.segments > 10 else 1
                    self.type_count -= 1
                    self.update_array(context)
                
            elif event.type == 'X':
                self.spin_axis = 'LOCAL_X'
                self.update_array(context)
                
            elif event.type == 'Y':
                self.spin_axis = 'LOCAL_Y'
                self.update_array(context)
        
            elif event.type == 'Z':
                self.spin_axis = 'LOCAL_Z'
                self.update_array(context)
                
            elif event.type == 'V':
                self.spin_axis = 'VIEW_Z'
                self.update_array(context)
                
            elif event.type == 'DEL':
                self.delete(context)
                self.finish_modal(context)
                return {'FINISHED'}
        
            elif event.type in ('ESC', 'RIGHTMOUSE'):
                self.restore_init(context)
                self.finish_modal(context)
                return {'CANCELLED'}
                
            elif event.type in ('SPACE', 'LEFTMOUSE'):
                self.finish_modal(context)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}


    def finish_modal(self, context):
        context.area.header_text_set(text=None)
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()
        
    def restore_init(self, context):
        # restore array parameters or delete it if it didn't exist before running modal
        if not self.force_new and self.init_array:
            self.init_array.count = self.init_array_count
            # restore empty transforms or delete it if it didn't exist before running modal
        else:
            context.object.modifiers.remove(self.array)
            
        if not self.force_new and self.init_empty :
            self.init_empty.matrix_world = self.init_empty_mx
        else:
            bpy.data.objects.remove(self.empty, do_unlink=True)
            
    def delete(self, context):
        context.object.modifiers.remove(self.array)
        bpy.data.objects.remove(self.empty, do_unlink=True)
        
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
            ("Segments: ", main_color), 
            ("(Scroll) ", key_color),
            (str(self.segments), val_color)],
            newline_x, newline_y, align, font, font_size)

        newline_y = draw_text_line([
            ("Spin Axis: ", main_color), 
            ("(XYZV) ", key_color),
            (str(self.spin_axis.title()), val_color)],
            newline_x, newline_y, align, font, font_size)
            
            
classes = (
    OBJECT_OT_radial_array,
    OBJECT_OT_radial_array_modal
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls) 


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
