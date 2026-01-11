import bpy
import json
import base64
import mimetypes
import urllib.request
import urllib.error
from pathlib import Path

from .preferences import _prefs


def _json_post(url: str, payload: dict, timeout=120) -> bytes:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _multipart_form_post(url: str, fields: dict, files: dict, timeout=120) -> bytes:
    boundary = "----BlenderSAM3DBoundary7MA4YWxkTrZu0gW"
    crlf = "\r\n"

    body = bytearray()

    for k, v in fields.items():
        body.extend(f"--{boundary}{crlf}".encode())
        body.extend(f'Content-Disposition: form-data; name="{k}"{crlf}{crlf}'.encode())
        body.extend(str(v).encode())
        body.extend(crlf.encode())

    for field_name, (filename, file_bytes, content_type) in files.items():
        body.extend(f"--{boundary}{crlf}".encode())
        body.extend(
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"{crlf}'.encode()
        )
        body.extend(f"Content-Type: {content_type}{crlf}{crlf}".encode())
        body.extend(file_bytes)
        body.extend(crlf.encode())

    body.extend(f"--{boundary}--{crlf}".encode())

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _file_to_data_url(path: Path) -> str:
    b = path.read_bytes()
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(b).decode("ascii")


class SAM3DSceneProps(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(
        name="Prompt",
        description="Text prompt for segmentation",
        default="object",
    )  # pyright: ignore[reportInvalidTypeForm]

    image_path: bpy.props.StringProperty(
        name="Image",
        description="Input image file",
        subtype="FILE_PATH",
        default="",
    )  # pyright: ignore[reportInvalidTypeForm]

    output_type: bpy.props.EnumProperty(
        name="Output Type",
        items=[
            ("mesh", "Mesh", "Generate a mesh output"),
            ("splat", "Splat", "Generate a splat output (if supported by server)"),
        ],
        default="mesh",
    )  # pyright: ignore[reportInvalidTypeForm]

    seed: bpy.props.IntProperty(
        name="Seed",
        default=42,
        min=0,
        max=2**31 - 1,
    )  # pyright: ignore[reportInvalidTypeForm]

    texture_baking: bpy.props.BoolProperty(
        name="Texture Baking",
        default=False,
    )  # pyright: ignore[reportInvalidTypeForm]


class SAM3D_OT_run(bpy.types.Operator):
    bl_idname = "sam3d.run"
    bl_label = "Run SAM3D → Generate 3D"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.sam3d_props
        prefs = _prefs(context)

        img_path = Path(bpy.path.abspath(props.image_path)).expanduser()
        if not img_path.exists():
            self.report({"ERROR"}, f"Image file not found: {img_path}")
            return {"CANCELLED"}

        try:
            image_bytes = img_path.read_bytes()
            mime, _ = mimetypes.guess_type(str(img_path))
            if not mime:
                mime = "application/octet-stream"

            seg_url = prefs.mask_endpoint.rstrip("/") + "/segment"
            seg_resp_bytes = _multipart_form_post(
                seg_url,
                fields={
                    "prompt": props.prompt,
                    "confidence_threshold": str(prefs.confidence_threshold),
                },
                files={
                    "image": (img_path.name, image_bytes, mime),
                },
                timeout=300,
            )
        except urllib.error.HTTPError as e:
            detail = (
                e.read().decode("utf-8", "replace") if hasattr(e, "read") else str(e)
            )
            self.report({"ERROR"}, f"Segmentation HTTPError {e.code}: {detail}")
            return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"Segmentation failed: {e}")
            return {"CANCELLED"}

        try:
            seg_json = json.loads(seg_resp_bytes.decode("utf-8"))
        except Exception:
            self.report({"ERROR"}, "Segmentation response was not valid JSON.")
            return {"CANCELLED"}

        mask = (
            seg_json.get("mask")
            or seg_json.get("mask_base64")
            or seg_json.get("mask_png_base64")
            or seg_json.get("mask_image")
        )

        if not mask:
            self.report(
                {"ERROR"}, f"No mask found in response keys: {list(seg_json.keys())}"
            )
            return {"CANCELLED"}

        if isinstance(mask, str):
            if mask.startswith("data:"):
                mask_data_url = mask
            else:
                mask_data_url = "data:image/png;base64," + mask
        else:
            self.report({"ERROR"}, "Mask format unsupported (expected string).")
            return {"CANCELLED"}

        try:
            gen_url = prefs.model_endpoint.rstrip("/") + "/generate_3d"
            payload = {
                "image": _file_to_data_url(img_path),
                "mask": mask_data_url,
                "output_type": props.output_type,
                "seed": props.seed,
                "texture_baking": props.texture_baking,
            }
            gen_resp = _json_post(gen_url, payload, timeout=600)
        except urllib.error.HTTPError as e:
            detail = (
                e.read().decode("utf-8", "replace") if hasattr(e, "read") else str(e)
            )
            self.report({"ERROR"}, f"3D HTTPError {e.code}: {detail}")
            return {"CANCELLED"}
        except Exception as e:
            self.report({"ERROR"}, f"3D generation failed: {e}")
            return {"CANCELLED"}

        out_dir = Path(bpy.path.abspath("//"))
        out_dir.mkdir(parents=True, exist_ok=True)

        saved_path = None
        try:
            gen_json = json.loads(gen_resp.decode("utf-8"))
            file_b64 = (
                gen_json.get("file_base64")
                or gen_json.get("mesh_base64")
                or gen_json.get("data_base64")
            )
            filename = (
                gen_json.get("filename")
                or gen_json.get("file_name")
                or f"sam3d_output.{props.output_type}"
            )
            if file_b64:
                raw = base64.b64decode(file_b64)
                saved_path = out_dir / filename
                saved_path.write_bytes(raw)
        except Exception:
            ext = ".ply" if props.output_type == "mesh" else ".bin"
            saved_path = out_dir / f"sam3d_output{ext}"
            saved_path.write_bytes(gen_resp)

        self.report({"INFO"}, f"Saved output: {saved_path}")

        if saved_path.suffix.lower() == ".obj":
            bpy.ops.wm.obj_import(filepath=str(saved_path))
        elif saved_path.suffix.lower() == ".ply":
            bpy.ops.wm.ply_import(filepath=str(saved_path))

        return {"FINISHED"}


class SAM3D_PT_panel(bpy.types.Panel):
    bl_label = "SAM3D"
    bl_idname = "SAM3D_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SAM3D"

    def draw(self, context):
        layout = self.layout
        props = context.scene.sam3d_props
        prefs = _prefs(context)

        layout.prop(props, "prompt")
        layout.prop(props, "image_path")

        col = layout.column(align=True)
        col.label(text="3D Settings")
        col.prop(props, "output_type")
        col.prop(props, "seed")
        col.prop(props, "texture_baking")

        layout.separator()
        layout.label(text="Endpoints (from Preferences):")
        layout.label(text=f"Mask:  {prefs.mask_endpoint}")
        layout.label(text=f"3D:    {prefs.model_endpoint}")
        layout.label(text=f"Conf:  {prefs.confidence_threshold:.2f}")

        layout.separator()
        layout.operator("sam3d.run", icon="PLAY")
