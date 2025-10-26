"""
Demo app for web_cropper component.

Run with: streamlit run ui/web_cropper/demo.py
"""

import streamlit as st
from ui.web_cropper import st_web_cropper
from PIL import Image
import numpy as np

st.set_page_config(page_title="Web Cropper Demo", layout="wide")

st.title("🖼️ Web Cropper Component Demo")
st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    
    # Image source
    image_source = st.radio(
        "Image Source",
        ["Upload", "Sample"]
    )
    
    if image_source == "Upload":
        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    
    st.divider()
    
    # Cropper settings
    init_box = st.slider("Initial Crop Size (px)", 100, 500, 160, 10)
    container_width = st.slider("Container Width (px)", 400, 1200, 900, 50)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Interactive Cropper")
    
    # Determine image
    img = None
    
    if image_source == "Upload" and uploaded_file:
        img = Image.open(uploaded_file)
    elif image_source == "Sample":
        # Create a sample image
        arr = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
        img = Image.fromarray(arr)
    
    if img:
        # Display the cropper with stable key
        rect = st_web_cropper(
            image=img,
            init_box=init_box,
            container_width=container_width,
            key="demo_cropper"  # Stable key prevents remounting
        )
        
        # Store in session state
        if rect:
            st.session_state["last_crop"] = rect
    else:
        st.info("👈 Please select an image source from the sidebar")

with col2:
    st.subheader("Crop Information")
    
    if "last_crop" in st.session_state:
        x, y, w, h = st.session_state["last_crop"]
        
        st.metric("Width", f"{w}px")
        st.metric("Height", f"{h}px")
        st.metric("Position", f"({x}, {y})")
        
        st.divider()
        
        st.subheader("Tuple Output")
        st.code(f"({x}, {y}, {w}, {h})")
        
        st.divider()
        
        st.subheader("Python Code")
        st.code(f"""
# Crop the image using PIL
from PIL import Image

img = Image.open("your_image.jpg")
cropped = img.crop((
    {x},
    {y},
    {x + w},
    {y + h}
))
cropped.save("cropped.jpg")
        """, language="python")
        
        # Show cropped preview if image exists
        if img:
            st.divider()
            st.subheader("Cropped Preview")
            cropped = img.crop((x, y, x + w, y + h))
            st.image(cropped, caption="Cropped Result", use_container_width=True)
    else:
        st.info("Adjust the crop box to see coordinates")

# Footer
st.markdown("---")
st.markdown("""
### Features

- ✅ **Pixel-perfect coordinates** - Returns actual image pixels
- ✅ **Smooth interactions** - 60fps performance with react-easy-crop
- ✅ **Responsive** - Works on all screen sizes
- ✅ **Stable key** - No remounting on slider changes

### Usage

```python
from ui.web_cropper import st_web_cropper
from PIL import Image

img = Image.open("photo.jpg")

rect = st_web_cropper(
    image=img,
    init_box=160,
    key="cropper"  # Stable key is important!
)

if rect:
    x, y, w, h = rect
    cropped = img.crop((x, y, x + w, y + h))
    st.image(cropped)
```

### API

```python
st_web_cropper(
    image: PIL.Image | np.ndarray | bytes,  # Image to crop
    init_box: int = 160,                     # Initial crop box size
    key: str = "web_cropper",                # Stable key (important!)
    container_width: int = 900,              # Container width
) -> Optional[Tuple[int, int, int, int]]
```

**Returns**: `(x, y, w, h)` in image pixel coordinates, or `None`.

### Dev Mode

Set environment variable to use dev server:
```bash
export WEB_CROPPER_DEV="http://localhost:5173"
streamlit run demo.py
```

Then in another terminal:
```bash
cd frontend
npm run dev
```
""")
