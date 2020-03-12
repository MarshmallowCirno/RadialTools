# RadialTools

Blender addon for duplicating object radially and creating radial array.

## Radial instances
![Radial_Instances_Demo](https://github.com/MarshmallowCirno/RadialTools/blob/master/docs/radial_instances.gif)

Adds linked duplicates of the object radially around the 3D cursor.
You can change a number of duplicates with a mouse scroll or type it on a keyboard. Rotation is performed around local X, Y, Z axis or view Z axis (which can be switched by XYZV keys).

Duplicated objects will be added to selected object collection, and if it has a parent, then duplicates will inherit it.

## Radial Array
![Radial_Array_Demo](https://github.com/MarshmallowCirno/RadialTools/blob/master/docs/radial_array.gif)

Adds an array modifier to selected object with easily adjustable segments number.
Center of the array will be located on the object pivot.
You can change a number of segments by scrolling or typing a number on a keyboard. 
Axis of the array can be changed to object X, Y or Z local axis or view Z axis (can be choosed with XYZV keys).

If you try to add another radial array to an object that already has it, tool will pick up the existing modifier and allow you to edit it.

ctrl+click on the button create a modifier with the center on the 3D cursor instead of object pivot.

shift+click on the button create a new radial array modifier on top of existing one.

ctrl+shift click on the button create a new radial array modifier on top of existing one with the center on the 3D cursor.

### Installation
After unpacking the .py file to the scripts folder, you can find addon in the "Object" addons category.

### Location
Sidebar "Item" tab > "Radial Tools" panel

### Links
Gumroad https://gumroad.com/products/KkDcd

BlenderArtist https://blenderartists.org/t/radial-instances/1212033
