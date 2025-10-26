# src/utils/canvas_compat.py
from typing import Any
import io

def _to_pil(image, output_format: str = "PNG"):
    """
    Convert various image-like inputs to PIL.Image.
    Accepts PIL.Image, numpy ndarray, bytes, or anything Pillow can open.
    """
    from PIL import Image
    import numpy as np
    if isinstance(image, Image.Image):
        pil = image
    elif isinstance(image, np.ndarray):
        pil = Image.fromarray(image)
    else:
        if isinstance(image, (bytes, bytearray, io.BytesIO)):
            buf = image if isinstance(image, io.BytesIO) else io.BytesIO(image)
            pil = Image.open(buf)
        else:
            pil = Image.open(image)
    return pil.convert("RGB")

def _store_and_get_rel_url(pil_img, fmt: str = "PNG") -> str:
    """
    Store image via Streamlit media file manager and return a **relative URL**.
    
    For Streamlit 1.32.2, the API is:
    - MediaFileManager is a singleton class
    - Access via: from streamlit.runtime.media_file_manager import MediaFileManager
    - Get instance: MediaFileManager().add(...)
    """
    import hashlib
    
    # Prepare image data
    buf = io.BytesIO()
    fmt = (fmt or "PNG").upper()
    pil_img.save(buf, format=fmt)
    data = buf.getvalue()
    
    # Try multiple API versions
    try:
        # Streamlit 1.32.x: MediaFileManager singleton class
        from streamlit.runtime.media_file_manager import MediaFileManager
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        
        ctx = get_script_run_ctx()
        manager = MediaFileManager()
        
        # Generate a stable file ID based on content
        file_id = hashlib.md5(data).hexdigest()
        mimetype = f"image/{fmt.lower()}"
        
        # Try different method signatures for add()
        try:
            # Newer signature: add(file_id, data, mimetype, ...)
            media_file = manager.add(
                file_id=file_id,
                data=data,
                mimetype=mimetype,
            )
        except TypeError:
            # Fallback: add(data, mimetype, file_id)
            try:
                media_file = manager.add(data, mimetype, file_id)
            except TypeError:
                # Last resort: add(data, mimetype)
                media_file = manager.add(data, mimetype)
        
        # Return relative URL
        if hasattr(media_file, 'url'):
            return media_file.url
        elif hasattr(media_file, 'id'):
            return f"/media/{media_file.id}.{fmt.lower()}"
        else:
            # Construct URL from file_id
            return f"/media/{file_id}.{fmt.lower()}"
            
    except Exception as e:
        # Fallback to data URL if media manager fails
        import base64
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:image/{fmt.lower()};base64,{b64}"

def _install_on(target_mod) -> None:
    """
    Patch target module with a permissive image_to_url signature that matches canvas usage.
    Returns a **relative URL** (not data URL) that the component concatenates with baseUrlPath.
    """
    if target_mod is None:
        return
    def image_to_url(image: Any,
                     width: Any = None,
                     clamp: Any = None,
                     channels: str = "RGB",
                     output_format: str = "PNG",
                     image_id: Any = None,
                     *args: Any, **kwargs: Any) -> str:
        """
        Convert image to a relative media URL via Streamlit's media file manager.
        
        Args:
            image: PIL.Image, numpy array, bytes, or path-like
            width: Target width (ignored, for compatibility)
            clamp: Clamp values (ignored, for compatibility)
            channels: Color channels (default: "RGB")
            output_format: Image format (default: "PNG")
            image_id: Image ID (ignored, for compatibility)
            *args, **kwargs: Extra args (ignored, for compatibility)
        
        Returns:
            Relative URL string (e.g., '/media/abcd1234.png')
        """
        fmt = output_format or kwargs.get("output_format") or "PNG"
        pil = _to_pil(image, fmt)
        return _store_and_get_rel_url(pil, fmt)
    
    # Replace unconditionally to guarantee compatibility
    try:
        target_mod.image_to_url = image_to_url  # type: ignore[attr-defined]
    except Exception:
        pass

def install_image_to_url_shim():
    """
    Install a robust shim for Streamlit's internal image_to_url in both possible import paths.
    
    The shim:
    - Accepts 6+ positional arguments (compatible with all versions)
    - Returns a **relative URL** (not data URL) via Streamlit's media file manager
    - Works with both streamlit.elements.image and streamlit.elements.lib.image
    - Handles multiple Streamlit API versions (1.32.x, 1.33+)
    
    Must be called BEFORE importing streamlit_drawable_canvas.st_canvas.
    """
    # Path 1
    try:
        from streamlit.elements import image as st_image_mod
    except Exception:
        st_image_mod = None
    _install_on(st_image_mod)
    
    # Path 2 (some versions use elements.lib.image)
    try:
        from streamlit.elements.lib import image as st_image_lib_mod  # type: ignore
    except Exception:
        st_image_lib_mod = None
    _install_on(st_image_lib_mod)
