# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Radial Array and Radial Instances",
    "author": "MarshmallowCirno",
    "version": (1, 2),
    "blender": (2, 81, 0),
    "location": "",
    "description": "Add linked duplicates of selected object and place them radially around the 3D cursor or create radial array",
    "warning": "",
    "wiki_url": "https://gumroad.com/products/KkDcd",
    "category": "Object",
    }
    
    
if "bpy" in locals():
    import importlib
    reloadable_modules = [
        "functions",
        "radial_array",
        "radial_instances",
        "ui"
    ]
    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])
else:
    from . import functions, radial_array, radial_instances, ui


import bpy


def register():
    radial_array.register()
    radial_instances.register()
    ui.register()


def unregister():
    radial_array.unregister()
    radial_instances.unregister()
    ui.unregister()
    