# Web Cropper - Quick Start

## 🚀 5-Minute Setup

### 1. Build the Component (One-time)

```powershell
cd ui\web_cropper
.\build.ps1
```

**Expected output:**
```
✓ Node.js version: v18.x.x
✓ Dependencies installed
✓ Build completed
✓ bundle.js: 45.23 KB
✓ bundle.css: 2.15 KB
```

### 2. Test with Demo App

```powershell
streamlit run ui\web_cropper\demo.py
```

**What to expect:**
- Upload an image or use the sample
- Drag the crop box
- Resize by dragging corners
- Hover to see magnifier lens
- See live coordinates update

### 3. Use in Your App

```python
from ui.web_cropper import st_web_cropper
from PIL import Image

# In your Streamlit app
img = Image.open("your_image.jpg")

rect = st_web_cropper(
    image=img,
    init_box=250,
    key="cropper"  # Stable key is important!
)

if rect:
    # Crop the image
    x, y, w, h = rect
    cropped = img.crop((x, y, x + w, y + h))
    st.image(cropped, caption="Cropped Image")
```

## 📦 What You Get

- ✅ **Modern cropper** with smooth interactions
- ✅ **Magnifier lens** for precision
- ✅ **Pixel-perfect coordinates**
- ✅ **Responsive design**
- ✅ **TypeScript + React 18**

## 🔧 Requirements

- **Node.js 18+** (for building)
- **Python 3.8+**
- **Streamlit 1.32+**

## 📚 Full Documentation

- `README.md` - Complete API reference
- `INTEGRATION_GUIDE.md` - Integrate into app_new.py
- `demo.py` - Interactive demo

## 🐛 Troubleshooting

### "Node.js not found"
Install from: https://nodejs.org/

### "Component not found"
Run: `.\build.ps1` in `ui\web_cropper\`

### "Image not displaying"
Check data URL format: should start with `data:image/png;base64,`

## 💡 Pro Tips

1. **Stable key**: Always use a stable key to prevent remounting: `key="cropper"`
2. **Development mode**: Set `_RELEASE = False` in `__init__.py` and run `.\dev.ps1`
3. **Container width**: Adjust based on image size: `container_width=min(900, img.width)`

## 🎯 Next Steps

1. ✅ Build the component
2. ✅ Test with demo
3. ✅ Integrate into your app
4. 🎉 Enjoy smooth cropping!

---

**Questions?** Check `README.md` or `INTEGRATION_GUIDE.md`

