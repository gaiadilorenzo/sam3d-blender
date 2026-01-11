import bpy


class SAM3DPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    mask_endpoint: bpy.props.StringProperty(
        name="Mask Endpoint",
        description="Endpoint for the SAM model",
        default="http://localhost:8000",
    )  # pyright: ignore[reportInvalidTypeForm]

    model_endpoint: bpy.props.StringProperty(
        name="3D Model Endpoint",
        description="Endpoint for the 3D model generation",
        default="http://localhost:8001",
    )  # pyright: ignore[reportInvalidTypeForm]

    confidence_threshold: bpy.props.FloatProperty(
        name="Confidence Threshold",
        description="Confidence threshold for mask generation",
        default=0.5,
        min=0.0,
        max=1.0,
    )  # pyright: ignore[reportInvalidTypeForm]

    def draw(self, context):
        layout = self.layout
        layout.label(text="SAM3D Add-on Preferences")
        layout.prop(self, "mask_endpoint")
        layout.prop(self, "model_endpoint")
        layout.prop(self, "confidence_threshold")


def _prefs(context) -> SAM3DPreferences:
    return context.preferences.addons[__package__].preferences
