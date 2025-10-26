# Web Cropper - Streamlit Custom Component

A professional image cropping component for Streamlit with magnifier lens support.

## Features

- ✅ **React + react-easy-crop** - Smooth, modern cropping experience
- ✅ **Pixel-perfect coordinates** - Returns actual image pixels (not CSS pixels)
- ✅ **Magnifier lens** - Optional hover magnifier for precise adjustments
- ✅ **Responsive design** - Works on all screen sizes
- ✅ **TypeScript** - Full type safety
- ✅ **Vite** - Fast builds and hot reload

## Installation

### 1. Build the component

```powershell
cd ui/web_cropper
.\build.ps1
```

### 2. Use in your Streamlit app

```python
from ui.web_cropper import st_web_cropper
from PIL import Image

# Load your image
img = Image.open("photo.jpg")

# Display the cropper
rect = st_web_cropper(
    image=img,
    init_box=250,
    key="my_cropper"
)

# Use the crop coordinates
if rect:
    x, y, w, h = rect
    cropped = img.crop((x, y, x + w, y + h))
    st.image(cropped, caption="Cropped Result")
```

## API Reference

### `st_web_cropper()`

**Parameters:**

- `image` (PIL.Image.Image): PIL Image to crop
- `init_box` (int, default=200): Initial size of the crop box in pixels
- `key` (str, optional): Unique key for this component instance (use stable key!)
- `container_width` (int, default=800): Width of the container in pixels
- `enable_magnifier` (bool, default=True): Whether to show the magnifier lens

**Returns:**

- `tuple` or `None`: Tuple `(x, y, width, height)` in image pixel coordinates, or `None`

## Development

### Start dev server

```powershell
cd ui/web_cropper
.\dev.ps1
```

Then in your Python code, set `_RELEASE = False` in `__init__.py` to use the dev server.

### Project Structure

```
ui/web_cropper/
├── __init__.py              # Python wrapper
├── build.ps1                # Production build script
├── dev.ps1                  # Development server script
├── README.md                # This file
└── frontend/
    ├── package.json         # npm dependencies
    ├── vite.config.ts       # Vite configuration
    ├── tsconfig.json        # TypeScript configuration
    ├── index.html           # HTML entry point
    └── src/
        ├── index.tsx        # React entry point
        ├── WebCropper.tsx   # Main component
        └── WebCropper.css   # Component styles
```

## Technical Details

### Coordinate System

The component returns **image pixel coordinates**, not CSS/display coordinates. This means:

- If your image is 3000×2000 pixels but displayed at 900×600 pixels
- The returned coordinates are in the original 3000×2000 space
- No manual scaling needed!

### Media Management

The component automatically:
1. Converts PIL Image to PNG bytes
2. Registers with Streamlit's media file manager
3. Generates a relative URL (e.g., `/media/abc123.png`)
4. Passes the URL to the React component

This ensures proper URL handling with `baseUrlPath` concatenation.

### Magnifier Lens

The magnifier lens:
- Shows a 2× zoomed view of the area under the cursor
- 100px diameter circular lens
- Blue border (#54a7ff)
- Only visible when `enable_magnifier=True`
- Pure CSS implementation (no extra libraries)

### Performance

- Built with Vite for fast load times
- React 18 with concurrent features
- Optimized bundle size (~50KB gzipped)
- Smooth 60fps interactions

## Dependencies

### Frontend
- `react` ^18.2.0
- `react-dom` ^18.2.0
- `react-easy-crop` ^5.0.4
- `streamlit-component-lib` ^2.0.0

### Build Tools
- `vite` ^5.0.0
- `typescript` ^5.0.0
- `@vitejs/plugin-react` ^4.2.0

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT

## Credits

Built with:
- [react-easy-crop](https://github.com/ValentinH/react-easy-crop) by Valentin Hervieu
- [Streamlit](https://streamlit.io/) by Snowflake

