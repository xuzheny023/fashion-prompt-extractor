import streamlit as st
from PIL import Image
from src.structure_detect import analyze_structure
from src.prompt_builder import generate_prompt

st.title("AI服装图像结构关键词提取系统")

uploaded_file = st.file_uploader("上传一张服装图像", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption='上传图像', use_column_width=True)

    structure_info = analyze_structure(image)
    st.write("结构关键词：", structure_info)

    prompt = generate_prompt(structure_info)
    st.markdown(f"**推荐Prompt：** `{prompt}`")
