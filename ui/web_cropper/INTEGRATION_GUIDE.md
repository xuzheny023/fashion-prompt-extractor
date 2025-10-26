# Integration Guide for app_new.py

## Step 1: Build the Component

```powershell
cd ui/web_cropper
.\build.ps1
```

## Step 2: Import in app_new.py

Add this import at the top of `app_new.py`:

```python
from ui.web_cropper import st_web_cropper
```

## Step 3: Replace draw_cropper() Usage

### Before (using streamlit-drawable-canvas):

```python
rect = draw_cropper(img, init_box=init_size, key="crop")
```

### After (using st_web_cropper):

```python
rect = st_web_cropper(
    image=img,
    init_box=init_size,
    key="crop",  # Stable key prevents remounting
    container_width=min(900, img.width),
    enable_magnifier=True
)
```

**That's it!** The return format is identical: `(x, y, width, height)` or `None`.

---

## Complete Integration Example

```python
# In app_new.py, replace the cropper section:

# === Image Display & Cropper ===
with col_img:
    st.caption("原始图像" if lang == "zh" else "Original Image")
    
    # Display web_cropper (no data URL conversion needed!)
    rect = st_web_cropper(
        image=img,
        init_box=init_size,
        key="crop",  # Stable key is critical
        container_width=min(900, img.width),
        enable_magnifier=True
    )

# === Preview & Action ===
with col_info:
    if rect:
        x, y, w, h = rect
        patch = img.crop((x, y, x + w, y + h))
        
        # Display preview
        show_w = int(init_size * zoom)
        caption = "预览区域" if lang == "zh" else "Preview"
        st.image(patch.resize((show_w, show_w)), caption=caption)
        
        # Recognition button
        if st.button("识别该区域", use_container_width=True):
            # ... existing recognition code ...
            # No changes needed here!
```

---

## Key Differences from Old Implementation

### ✅ Simpler API

**Old** (streamlit-drawable-canvas):
```python
# Required data URL conversion
def pil_to_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

image_url = pil_to_data_url(img)
rect = draw_cropper(img, init_box=init_size, key="crop")
```

**New** (st_web_cropper):
```python
# Direct PIL Image input
rect = st_web_cropper(
    image=img,
    init_box=init_size,
    key="crop"
)
```

### ✅ Automatic Media Management

The component automatically:
1. Converts PIL Image to PNG bytes
2. Registers with Streamlit's media file manager
3. Generates a relative URL (e.g., `/media/abc123.png`)
4. Passes the URL to the React component
5. Returns pixel coordinates as a tuple

### ✅ Stable Key Handling

The component uses a **stable key** internally, which means:
- Slider changes don't remount the component
- No flickering or loss of state
- Smooth user experience

---

## Benefits of st_web_cropper

1. ✅ **No canvas compatibility issues** - Pure React component
2. ✅ **Better UX** - Smooth drag & zoom with react-easy-crop
3. ✅ **Magnifier lens** - Built-in hover magnifier
4. ✅ **Pixel-perfect** - Returns actual image coordinates
5. ✅ **Modern stack** - React 18 + TypeScript + Vite
6. ✅ **Responsive** - Works on all screen sizes
7. ✅ **Simpler API** - Direct PIL Image input
8. ✅ **Automatic media management** - No manual URL conversion

---

## Removing Old Dependencies

After integration, you can remove:

### From app_new.py:
```python
# Remove these lines:
from src.utils.canvas_compat import install_image_to_url_shim
install_image_to_url_shim()
from streamlit_drawable_canvas import st_canvas

# Remove the draw_cropper() function definition
```

### From requirements.txt:
```
# Remove this line:
streamlit-drawable-canvas==0.9.3.post2
```

### Delete these files:
```
src/utils/canvas_compat.py
test_canvas_compat.py
```

---

## Testing

1. Build the component: `.\ui\web_cropper\build.ps1`
2. Run the app: `.\run.ps1`
3. Upload an image
4. Verify:
   - ✅ Cropper displays correctly
   - ✅ Drag & resize works smoothly
   - ✅ Magnifier lens appears on hover
   - ✅ Preview updates immediately
   - ✅ Slider changes don't cause flickering
   - ✅ Recognition works with cropped area

---

## Troubleshooting

### Component not found

Make sure you've built the component:
```powershell
cd ui/web_cropper
.\build.ps1
```

### Image not displaying

Check that the PIL Image is valid:
```python
print(f"Image size: {img.size}")
print(f"Image mode: {img.mode}")
```

### Coordinates seem wrong

The component returns **image pixel coordinates**, not display coordinates. No scaling needed!

### Component remounts on slider change

Make sure you're using a **stable key**:
```python
# Good: stable key
rect = st_web_cropper(image=img, key="crop")

# Bad: dynamic key (will remount)
rect = st_web_cropper(image=img, key=f"crop_{init_size}")
```

---

## Development Mode

To work on the component while developing:

1. In `ui/web_cropper/__init__.py`, set `_RELEASE = False`
2. Start dev server: `.\ui\web_cropper\dev.ps1`
3. Make changes to `frontend/src/WebCropper.tsx`
4. Changes hot-reload automatically
5. When done, set `_RELEASE = True` and run `.\build.ps1`

---

## Migration Checklist

- [ ] Build the component: `.\ui\web_cropper\build.ps1`
- [ ] Add import: `from ui.web_cropper import st_web_cropper`
- [ ] Replace `draw_cropper()` with `st_web_cropper()`
- [ ] Remove `pil_to_data_url()` helper (not needed)
- [ ] Remove canvas compatibility shim imports
- [ ] Remove `streamlit-drawable-canvas` from requirements.txt
- [ ] Delete `src/utils/canvas_compat.py`
- [ ] Delete `test_canvas_compat.py`
- [ ] Test the app thoroughly
- [ ] Enjoy the improved UX! 🎉

---

## Side-by-Side Comparison

### Old Implementation
```python
# app_new.py (old)

# Compatibility shim
from src.utils.canvas_compat import install_image_to_url_shim
install_image_to_url_shim()

# Canvas import
from streamlit_drawable_canvas import st_canvas

# Helper function
def pil_to_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

# Usage
image_url = pil_to_data_url(img)
rect = draw_cropper(img, init_box=init_size, key="crop")
```

### New Implementation
```python
# app_new.py (new)

# Simple import
from ui.web_cropper import st_web_cropper

# Usage (that's it!)
rect = st_web_cropper(
    image=img,
    init_box=init_size,
    key="crop"
)
```

**Lines of code**: 20+ → 5  
**Dependencies**: 2 → 1  
**Complexity**: High → Low  
**Maintainability**: Hard → Easy  

---

## Summary

The new `st_web_cropper` component provides:

- ✅ **Simpler API** - Direct PIL Image input
- ✅ **Better UX** - Smooth interactions with react-easy-crop
- ✅ **No compatibility issues** - No shims needed
- ✅ **Automatic media management** - Uses Streamlit's media file manager
- ✅ **Stable key handling** - No remounting on slider changes
- ✅ **Modern tech stack** - React 18 + TypeScript + Vite

**Migration is straightforward and brings significant improvements!**
