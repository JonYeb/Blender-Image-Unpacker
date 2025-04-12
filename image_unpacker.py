bl_info = {
    "name": "Image Unpacker",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Image Tools",
    "description": "Unpack all images used in materials for all objects",
    "warning": "",
    "doc_url": "",
    "category": "Material",
}

import bpy
import os
from bpy.types import Panel, Operator
from bpy.props import StringProperty, BoolProperty

class MATERIAL_OT_unpack_all_images(Operator):
    """Unpack all images used in materials across all objects in the scene"""
    bl_idname = "material.unpack_all_images"
    bl_label = "Unpack All Material Images"
    bl_options = {'REGISTER', 'UNDO'}
    
    create_dir: BoolProperty(
        name="Create Texture Directory",
        description="Create a textures directory if it doesn't exist",
        default=True
    )
    
    texture_dir: StringProperty(
        name="Texture Directory",
        description="Directory to save unpacked textures (relative to blend file)",
        default="//textures"
    )
    
    def execute(self, context):
        # Get the directory of the current blend file
        blend_filepath = bpy.data.filepath
        if not blend_filepath:
            self.report({'ERROR'}, "Blend file must be saved before unpacking textures")
            return {'CANCELLED'}
        
        directory = os.path.dirname(blend_filepath)
        texture_path = self.texture_dir
        
        # If the path is relative (starts with //), make it absolute
        if texture_path.startswith("//"):
            texture_path = os.path.join(directory, texture_path[2:])
        
        # Create textures directory if it doesn't exist and option is enabled
        if self.create_dir and not os.path.exists(texture_path):
            try:
                os.makedirs(texture_path)
                self.report({'INFO'}, f"Created texture directory: {texture_path}")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to create directory: {e}")
                return {'CANCELLED'}
        
        # Track all images processed
        unpacked_count = 0
        already_unpacked = 0
        failed_count = 0
        
        # Process all images in the Blender file
        for img in bpy.data.images:
            if img.source == 'FILE' and img.packed_file:
                try:
                    # Set the filepath to save in the textures folder
                    filename = img.name
                    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.exr')):
                        filename += ".png"  # Add extension if missing
                    
                    # Use relative path (//textures/...)
                    img.filepath = os.path.join(self.texture_dir, filename)
                    
                    # Unpack the image
                    img.unpack(method='USE_ORIGINAL')
                    unpacked_count += 1
                except Exception as e:
                    self.report({'WARNING'}, f"Error unpacking {img.name}: {e}")
                    failed_count += 1
            elif img.source == 'FILE' and not img.packed_file:
                already_unpacked += 1
        
        # Report results
        self.report({'INFO'}, f"Unpacked {unpacked_count} images, {already_unpacked} already unpacked, {failed_count} failed")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class MATERIAL_PT_image_unpacker(Panel):
    """Creates a Panel in the Material properties window"""
    bl_label = "Image Unpacker"
    bl_idname = "MATERIAL_PT_image_unpacker"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Image Tools'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("material.unpack_all_images")

def menu_func(self, context):
    self.layout.operator(MATERIAL_OT_unpack_all_images.bl_idname)

classes = (
    MATERIAL_OT_unpack_all_images,
    MATERIAL_PT_image_unpacker,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.MATERIAL_MT_context_menu.append(menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.MATERIAL_MT_context_menu.remove(menu_func)

if __name__ == "__main__":
    register()
