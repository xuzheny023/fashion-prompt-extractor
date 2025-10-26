# src/utils/img_dataurl.py
import base64, io
from PIL import Image

def pil_to_data_url(img: Image.Image, fmt: str = "PNG") -> str:
    """
    Convert PIL Image to data URL for reliable rendering in streamlit-drawable-canvas.
    
    Args:
        img: PIL Image object
        fmt: Image format (default: "PNG")
    
    Returns:
        Data URL string (e.g., "data:image/png;base64,...")
    """
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/{fmt.lower()};base64,{b64}"


