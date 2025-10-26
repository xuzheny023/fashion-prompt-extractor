#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test for web_cropper component
"""
import streamlit as st
from PIL import Image
import io
import base64

st.set_page_config(page_title="Web Cropper Test", layout="wide")

st.title("🎨 Web Cropper Component Test")

# Import component
try:
    from ui.web_cropper import web_cropper
    st.success("✅ Component imported successfully")
except Exception as e:
    st.error(f"❌ Failed to import component: {e}")
    st.stop()

# Create test image
col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Input")
    
    # Option 1: Upload
    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    # Option 2: Generate test image
    if st.button("Generate Test Image"):
        img = Image.new('RGB', (800, 600), color=(255, 100, 100))
        # Draw some patterns
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        for i in range(0, 800, 50):
            draw.line([(i, 0), (i, 600)], fill=(200, 200, 200), width=1)
        for i in range(0, 600, 50):
            draw.line([(0, i), (800, i)], fill=(200, 200, 200), width=1)
        
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        st.session_state['test_image'] = buf.getvalue()
    
    # Get image
    if uploaded:
        image_data = uploaded.read()
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
    elif 'test_image' in st.session_state:
        image_data = st.session_state['test_image']
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
    else:
        st.info("👆 Upload an image or generate a test image")
        st.stop()
    
    st.image(img, caption=f"Original Image ({img.width} × {img.height})", use_container_width=True)
    
    # Convert to base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    
    # Component options
    st.divider()
    st.subheader("⚙️ Options")
    
    use_initial_box = st.checkbox("Use initial box", value=False)
    initial_box = None
    if use_initial_box:
        col_x, col_y = st.columns(2)
        with col_x:
            box_x = st.number_input("X", 0, img.width, 100)
            box_w = st.number_input("Width", 32, img.width, 200)
        with col_y:
            box_y = st.number_input("Y", 0, img.height, 100)
            box_h = st.number_input("Height", 32, img.height, 200)
        initial_box = {"x": box_x, "y": box_y, "w": box_w, "h": box_h}
    
    min_size = st.slider("Min Size", 16, 128, 32)

with col2:
    st.subheader("✂️ Cropper")
    
    # Call component
    result = web_cropper(
        key="test_cropper",
        image_b64=b64,
        box=initial_box,
        minSize=min_size
    )
    
    st.divider()
    
    # Show result
    if result and isinstance(result, dict) and 'rect' in result:
        rect = result['rect']
        st.success("✅ Crop area selected!")
        
        col_info, col_preview = st.columns(2)
        
        with col_info:
            st.metric("X", f"{rect['x']:.0f} px")
            st.metric("Y", f"{rect['y']:.0f} px")
            st.metric("Width", f"{rect['w']:.0f} px")
            st.metric("Height", f"{rect['h']:.0f} px")
            
            # Calculate aspect ratio
            ratio = rect['w'] / rect['h'] if rect['h'] > 0 else 0
            st.metric("Aspect Ratio", f"{ratio:.2f}")
        
        with col_preview:
            st.subheader("🖼️ Cropped Preview")
            try:
                # Crop the image
                x, y, w, h = int(rect['x']), int(rect['y']), int(rect['w']), int(rect['h'])
                
                # Scale coordinates from display size to original size
                # (Note: This assumes the component returns CSS pixel coordinates)
                # For accurate cropping, you may need to scale based on display vs natural size
                
                cropped = img.crop((x, y, x + w, y + h))
                st.image(cropped, caption=f"Cropped ({w} × {h})", use_container_width=True)
                
                # Download button
                crop_buf = io.BytesIO()
                cropped.save(crop_buf, format='PNG')
                st.download_button(
                    "⬇️ Download Cropped Image",
                    crop_buf.getvalue(),
                    "cropped.png",
                    "image/png"
                )
            except Exception as e:
                st.error(f"Failed to crop: {e}")
    else:
        st.info("👈 Drag the rectangle and click Confirm")

# Debug info
with st.expander("🐛 Debug Info"):
    st.write("**Component Result:**")
    st.json(result)
    
    st.write("**Image Info:**")
    st.json({
        "width": img.width,
        "height": img.height,
        "mode": img.mode,
        "format": img.format or "Unknown"
    })
    
    st.write("**Base64 Preview:**")
    st.code(b64[:100] + "..." if len(b64) > 100 else b64)

