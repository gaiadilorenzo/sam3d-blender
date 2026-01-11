bl_info = {
    "name": "SAM3D Blender",
    "blender": (2, 80, 0),
    "category": "Object",
}

from .preferences import SAM3DPreferences  # noqa: E402
from .panel import SAM3DSceneProps, SAM3D_OT_run, SAM3D_PT_panel  # noqa: E402

import bpy  # noqa: E402

classes = [
    SAM3DPreferences,
    SAM3DSceneProps,
    SAM3D_OT_run,
    SAM3D_PT_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.sam3d_props = bpy.props.PointerProperty(type=SAM3DSceneProps)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.sam3d_props


if __name__ == "__main__":
    register()
