# User Guide | 使用指南

## 🌐 English Guide

### Getting Started

#### 1. Initial Setup

After installing the application following the README instructions, ensure:
- Your virtual environment is activated
- API key is properly configured in `.streamlit/secrets.toml` or as an environment variable
- All dependencies are installed via `pip install -r requirements.txt`

#### 2. Launching the Application

**Windows Users:**
```powershell
.\run.ps1
```

**macOS/Linux Users:**
```bash
streamlit run app_new.py
```

The application will automatically open in your default browser at `http://localhost:9000` (Windows via run.ps1) or `http://localhost:8501` (direct Streamlit).

### Interface Overview

#### Sidebar (Left Panel)

**Language Selection** 🌐
- Located at the very top
- Toggle between `zh` (Chinese) and `en` (English)
- Changes both UI and AI output language

**Upload Section** 📤
- Click "Browse files" or drag-and-drop
- Supported formats: JPG, JPEG, PNG
- Recommended resolution: 800x800 pixels or higher

**Analysis Parameters** ⚙️

1. **ROI Type** 📍
   - **Auto Detect**: Let AI determine if it's fabric, print, or construction
   - **Fabric Analysis**: Focus on material properties
   - **Print Process**: Analyze printing/pattern details
   - **Construction**: Examine stitching and assembly methods

2. **Production Context** 🎯
   - **Budget Level**: 
     - 💰 Low Cost: Budget-friendly options
     - 💎 Mid Range: Balanced quality and price
     - 👑 High End: Premium materials and processes
   
   - **Use Case**:
     - 👕 Casual: Everyday wear
     - 👗 Evening: Formal occasions
     - 🏃 Activewear: Sports and fitness
     - 💼 Office: Professional attire
     - 🏠 Home: Sleepwear and loungewear
     - 💒 Wedding: Bridal and ceremonial
     - 🎭 Stage: Performance costumes
   
   - **Constraints** (Multi-select):
     - Eco-friendly: Sustainable materials
     - Washable: Machine washable
     - Durable: Long-lasting construction
     - 4-way Stretch: Full elasticity
     - Wrinkle-resistant: No-iron fabrics
     - Quick-dry: Fast moisture wicking
     - UV-resistant: Sun protection
     - Anti-bacterial: Odor control

**Basic Settings** 🔧
- **Cloud Model**: Select AI model (qwen-vl or qwen-vl-plus)
- **Enable Web Search**: Augment analysis with online information
- **Search Results**: Number of web results to retrieve (1-10)

**API Status** ✅
- Green checkmark: API key configured correctly
- Red X: API key missing or invalid

#### Main Panel (Center and Right)

**Left: Design Image & Cropping** 📸
- Your uploaded image appears here
- Orange crop box for region selection:
  - **Drag the box**: Move to different areas
  - **Drag corners**: Resize the selection box
  - **Real-time preview**: See selected area immediately

**Right: AI Analysis Results** 🎯
- Initially empty until analysis is run
- After analysis, displays:
  - Summary
  - Detailed specifications
  - Budget recommendations
  - DFM risks
  - Next actions

### Step-by-Step Workflow

#### Step 1: Upload Your Design

1. Click "📤 Upload Design Image" in the sidebar
2. Select an image file from your computer
3. Wait for the image to load in the main panel

**Tips:**
- Use high-resolution images for better analysis
- Crop close to the area of interest before uploading for faster processing
- Clear, well-lit photos produce more accurate results

#### Step 2: Configure Analysis Parameters

1. **Select ROI Type**: 
   - If analyzing fabric texture → Choose "📐 Fabric Analysis"
   - If analyzing a print pattern → Choose "🎨 Print Process"
   - If analyzing seams/stitching → Choose "🔧 Construction"
   - If unsure → Choose "🤖 Auto Detect"

2. **Set Budget Level**: Match your target market
   - Fast fashion → Low Cost
   - Contemporary brands → Mid Range
   - Luxury fashion → High End

3. **Choose Use Case**: Select the garment's intended purpose
   - Example: Yoga wear → Activewear
   - Example: Cocktail dress → Evening

4. **Add Constraints** (if applicable):
   - Athleisure? → Check "4-way Stretch" + "Quick-dry"
   - Sustainable fashion? → Check "Eco-friendly"
   - Children's wear? → Check "Washable" + "Durable"

#### Step 3: Select Region of Interest

**Using Interactive Cropper (Recommended):**
1. Once image loads, an orange crop box appears
2. Click and drag the box to your area of interest
3. Drag corner handles to resize
4. The selected region updates in real-time

**Using Manual Input (Fallback):**
1. If cropper doesn't load, you'll see numerical inputs
2. Enter coordinates:
   - **Start X/Y**: Top-left corner position
   - **End X/Y**: Bottom-right corner position
3. Use pixel values relative to image dimensions

**Selection Tips:**
- **For Fabric**: Select a clear, flat area showing texture
- **For Prints**: Include the complete pattern repeat if possible
- **For Construction**: Focus on one seam or detail at a time
- **For Full Garment**: Skip cropping and analyze the full image

#### Step 4: Run AI Analysis

1. Review your selected region in the preview
2. Click the blue "🤖 Analyze Selected Region" button
3. Wait for the AI to process (usually 3-10 seconds)
4. Results appear in the right panel

**If No Region Selected:**
- The button changes to "🤖 Analyze Full Image"
- Analyzes the entire uploaded image

#### Step 5: Review Results

The results are organized into expandable sections:

**📋 Summary**
- One-sentence core conclusion
- Quickly understand the main finding

**🔍 Detailed Analysis**
- Expanded by default
- Shows comprehensive specifications based on analysis type:

*For Fabric:*
- Material composition
- Weave/knit structure
- Weight range (gsm)
- Gloss level, stretch, handfeel
- Finishing processes
- Alternative fabrics

*For Print:*
- Print process type
- Color count
- Resolution requirements
- Repeat size
- Recommended base fabrics
- Complete workflow
- Potential risks

*For Construction:*
- Stitch types
- Needle and thread specs
- Seam classifications
- Edge finishing methods
- Interlining requirements
- Tolerance standards

**💡 Recommendations**
- Three columns for Low Cost / Mid Range / High End
- Each includes:
  - Material or process description
  - Estimated cost implications
  - Sourcing/workflow suggestions

**⚠️ DFM Risks**
- Collapsed by default
- Lists potential manufacturing challenges:
  - Shrinkage issues
  - Color fastness concerns
  - Pilling tendencies
  - Registration difficulties
  - And more...

**📌 Next Actions**
- Collapsed by default
- Numbered list of recommended next steps
- Example: "Order lab-dips for color matching"
- Example: "Request pre-production samples"

### Advanced Features

#### Multi-Region Analysis

Analyze different parts of the same garment separately:

1. Analyze fabric → Save/screenshot results
2. Crop to print area → Analyze again
3. Crop to construction detail → Final analysis
4. Compare all results for comprehensive understanding

#### Comparing Budget Options

Use the three-column recommendations to:
- Present options to clients
- Make informed sourcing decisions
- Understand cost-quality tradeoffs
- Plan product line variations (good/better/best)

#### Export Results

Currently, results are displayed in the browser:
- **Screenshot**: Use browser or OS screenshot tools
- **Copy Text**: Select and copy specific sections
- **Print**: Use browser print function (Ctrl+P / Cmd+P)

*Note: Built-in export feature coming in future updates*

### Tips & Best Practices

#### For Best Analysis Results:

1. **Image Quality Matters**
   - Use well-lit, in-focus photos
   - Avoid heavy shadows or glare
   - Minimum 800x800 pixels recommended

2. **Crop Precisely**
   - Select only the area you want analyzed
   - Avoid including unrelated elements
   - Larger selections provide more context

3. **Choose Right ROI Type**
   - "Auto" works well for mixed elements
   - Specific types give more detailed analysis

4. **Context is Key**
   - Accurate budget/use case selection improves recommendations
   - Constraints help AI filter suitable options

5. **Iterate and Refine**
   - Try different crop regions
   - Adjust parameters if results seem off
   - Compare multiple analyses

#### Common Use Cases:

**Fabric Sourcing:**
1. Upload fabric swatch photo
2. Select "Fabric Analysis"
3. Set your target budget
4. Get material names and alternatives

**Print Production:**
1. Upload design with pattern
2. Crop to print area
3. Select "Print Process"
4. Review workflow and color count

**Quality Control:**
1. Upload production sample photo
2. Compare AI analysis with specs
3. Check DFM risks section
4. Verify construction details

**Design Validation:**
1. Upload AI-generated design render
2. Use "Auto Detect" mode
3. Review all recommendations
4. Assess feasibility before sampling

### Troubleshooting

**Problem: Cropper doesn't appear**
- Solution: Use manual coordinate input below
- Or: Refresh the page and re-upload

**Problem: Analysis takes too long (>30 seconds)**
- Check your internet connection
- Verify API key has available quota
- Try with a smaller image or crop region

**Problem: Results are in wrong language**
- Ensure language is selected at top of sidebar
- Restart application after language change
- Clear browser cache if issue persists

**Problem: Generic or vague results**
- Provide clearer image/crop region
- Specify ROI type instead of Auto
- Add more relevant constraints

**Problem: API Key error**
- Verify key in `.streamlit/secrets.toml`
- Or check environment variable is set
- Confirm key is active on DashScope console

### Keyboard Shortcuts

- `Ctrl + R` / `Cmd + R`: Refresh page
- `F11`: Fullscreen mode
- `Ctrl + P` / `Cmd + P`: Print results

---

## 🇨🇳 中文指南

### 入门指南

#### 1. 初始设置

按照 README 说明安装应用后，确保：
- 虚拟环境已激活
- API 密钥已在 `.streamlit/secrets.toml` 或环境变量中正确配置
- 所有依赖已通过 `pip install -r requirements.txt` 安装

#### 2. 启动应用

**Windows 用户：**
```powershell
.\run.ps1
```

**macOS/Linux 用户：**
```bash
streamlit run app_new.py
```

应用将自动在默认浏览器中打开，地址为 `http://localhost:9000`（Windows 通过 run.ps1）或 `http://localhost:8501`（直接使用 Streamlit）。

### 界面概览

#### 侧边栏（左侧面板）

**语言选择** 🌐
- 位于最顶部
- 在 `zh`（中文）和 `en`（英文）之间切换
- 同时改变界面和 AI 输出语言

**上传区域** 📤
- 点击"浏览文件"或拖放上传
- 支持格式：JPG、JPEG、PNG
- 推荐分辨率：800x800 像素或更高

**分析参数** ⚙️

1. **ROI 区域类型** 📍
   - **自动识别**：让 AI 判断是面料、印花还是工艺
   - **面料分析**：专注于材质特性
   - **印花工艺**：分析印刷/图案细节
   - **结构做法**：检查缝制和组装方法

2. **生产上下文** 🎯
   - **预算档位**：
     - 💰 低成本：经济实惠的选择
     - 💎 中等：质量与价格平衡
     - 👑 高端：优质材料和工艺
   
   - **使用场景**：
     - 👕 日常休闲：日常穿着
     - 👗 晚礼服：正式场合
     - 🏃 运动装：体育健身
     - 💼 商务正装：职业装
     - 🏠 家居服：睡衣休闲服
     - 💒 婚礼服装：婚纱礼服
     - 🎭 舞台表演：演出服装
   
   - **约束条件**（多选）：
     - 环保：可持续材料
     - 可水洗：机洗
     - 耐磨：持久耐用
     - 四向弹：完全弹性
     - 防皱：免熨烫面料
     - 快干：快速排湿
     - 抗UV：防晒
     - 抗菌：气味控制

**基础设置** 🔧
- **云端模型**：选择 AI 模型（qwen-vl 或 qwen-vl-plus）
- **启用联网增强**：使用在线信息增强分析
- **检索条数**：获取网络结果数量（1-10）

**API 状态** ✅
- 绿色勾号：API 密钥配置正确
- 红色叉号：API 密钥缺失或无效

#### 主面板（中间和右侧）

**左侧：设计图与裁剪** 📸
- 上传的图片显示在此
- 橙色裁剪框用于区域选择：
  - **拖动框体**：移动到不同区域
  - **拖动角点**：调整选择框大小
  - **实时预览**：立即查看选中区域

**右侧：AI 分析结果** 🎯
- 分析前为空
- 分析后显示：
  - 总结
  - 详细规格
  - 预算推荐
  - DFM 风险
  - 下一步行动

### 分步操作流程

#### 步骤 1：上传设计图

1. 点击侧边栏的"📤 上传设计图/效果图"
2. 从计算机选择图片文件
3. 等待图片加载到主面板

**提示：**
- 使用高分辨率图片以获得更好的分析
- 上传前裁剪到感兴趣区域可加快处理速度
- 清晰、光线充足的照片产生更准确的结果

#### 步骤 2：配置分析参数

1. **选择 ROI 类型**：
   - 分析面料纹理 → 选择"📐 面料分析"
   - 分析印花图案 → 选择"🎨 印花工艺"
   - 分析缝线/拼接 → 选择"🔧 结构做法"
   - 不确定 → 选择"🤖 自动识别"

2. **设置预算档位**：匹配目标市场
   - 快时尚 → 低成本
   - 中端品牌 → 中等
   - 奢侈时尚 → 高端

3. **选择使用场景**：选择服装的预期用途
   - 例如：瑜伽服 → 运动装
   - 例如：鸡尾酒裙 → 晚礼服

4. **添加约束条件**（如适用）：
   - 运动休闲？→ 勾选"四向弹" + "快干"
   - 可持续时尚？→ 勾选"环保"
   - 童装？→ 勾选"可水洗" + "耐磨"

#### 步骤 3：选择感兴趣区域

**使用交互式裁剪器（推荐）：**
1. 图片加载后，出现橙色裁剪框
2. 点击并拖动框到感兴趣区域
3. 拖动角点手柄调整大小
4. 选中区域实时更新

**使用手动输入（备用）：**
1. 如果裁剪器未加载，将看到数值输入框
2. 输入坐标：
   - **起点 X/Y**：左上角位置
   - **终点 X/Y**：右下角位置
3. 使用相对于图片尺寸的像素值

**选择技巧：**
- **面料**：选择显示纹理的清晰、平整区域
- **印花**：尽可能包含完整的图案重复
- **工艺**：一次专注于一个缝线或细节
- **整体服装**：跳过裁剪，分析完整图片

#### 步骤 4：运行 AI 分析

1. 在预览中查看选中的区域
2. 点击蓝色"🤖 AI 分析选中区域"按钮
3. 等待 AI 处理（通常 3-10 秒）
4. 结果显示在右侧面板

**如果未选择区域：**
- 按钮变为"🤖 分析整张图片"
- 分析整个上传的图片

#### 步骤 5：查看结果

结果组织成可展开的部分：

**📋 总结**
- 一句话核心结论
- 快速理解主要发现

**🔍 详细分析**
- 默认展开
- 根据分析类型显示全面规格：

*面料：*
- 材质成分
- 织法/针织结构
- 克重范围（gsm）
- 光泽度、弹性、手感
- 后整理工艺
- 替代面料

*印花：*
- 印花工艺类型
- 套色数
- 分辨率要求
- 重复尺寸
- 推荐底布
- 完整工艺流程
- 潜在风险

*工艺：*
- 针型
- 针线规格
- 缝型分类
- 边缝处理方法
- 衬料要求
- 公差标准

**💡 推荐方案**
- 低成本/中等/高端三列
- 每个包括：
  - 材料或工艺描述
  - 预估成本影响
  - 采购/工艺建议

**⚠️ DFM 风险**
- 默认折叠
- 列出潜在制造挑战：
  - 缩水问题
  - 色牢度关注
  - 起球倾向
  - 对位困难
  - 更多...

**📌 下一步行动**
- 默认折叠
- 编号推荐后续步骤列表
- 例如："订购对色样"
- 例如："要求产前样品"

### 高级功能

#### 多区域分析

分别分析同一服装的不同部分：

1. 分析面料 → 保存/截图结果
2. 裁剪到印花区域 → 再次分析
3. 裁剪到工艺细节 → 最终分析
4. 对比所有结果以全面理解

#### 比较预算选项

使用三列推荐来：
- 向客户展示选择
- 做出明智的采购决策
- 理解成本质量权衡
- 规划产品线变化（好/更好/最好）

#### 导出结果

当前结果显示在浏览器中：
- **截图**：使用浏览器或系统截图工具
- **复制文本**：选择并复制特定部分
- **打印**：使用浏览器打印功能（Ctrl+P / Cmd+P）

*注意：内置导出功能将在未来更新中提供*

### 技巧与最佳实践

#### 获得最佳分析结果：

1. **图片质量很重要**
   - 使用光线充足、对焦清晰的照片
   - 避免重阴影或眩光
   - 推荐最小 800x800 像素

2. **精确裁剪**
   - 仅选择要分析的区域
   - 避免包含无关元素
   - 更大的选择提供更多上下文

3. **选择正确的 ROI 类型**
   - "自动"适用于混合元素
   - 特定类型提供更详细的分析

4. **上下文是关键**
   - 准确的预算/使用场景选择改善推荐
   - 约束条件帮助 AI 过滤合适选项

5. **迭代和优化**
   - 尝试不同的裁剪区域
   - 如果结果似乎不对，调整参数
   - 比较多个分析

#### 常见使用场景：

**面料采购：**
1. 上传面料色卡照片
2. 选择"面料分析"
3. 设置目标预算
4. 获取材料名称和替代品

**印花生产：**
1. 上传带图案的设计
2. 裁剪到印花区域
3. 选择"印花工艺"
4. 查看工艺流程和套色数

**质量控制：**
1. 上传生产样品照片
2. 将 AI 分析与规格对比
3. 检查 DFM 风险部分
4. 验证工艺细节

**设计验证：**
1. 上传 AI 生成的设计渲染图
2. 使用"自动识别"模式
3. 查看所有推荐
4. 在打样前评估可行性

### 故障排除

**问题：裁剪器未出现**
- 解决方案：使用下方的手动坐标输入
- 或：刷新页面并重新上传

**问题：分析时间过长（>30 秒）**
- 检查互联网连接
- 验证 API 密钥有可用配额
- 尝试使用更小的图片或裁剪区域

**问题：结果语言错误**
- 确保在侧边栏顶部选择了语言
- 更改语言后重启应用
- 如果问题持续，清除浏览器缓存

**问题：结果过于笼统或模糊**
- 提供更清晰的图片/裁剪区域
- 指定 ROI 类型而不是自动
- 添加更多相关约束

**问题：API 密钥错误**
- 验证 `.streamlit/secrets.toml` 中的密钥
- 或检查环境变量是否设置
- 确认密钥在灵积控制台中处于活动状态

### 键盘快捷键

- `Ctrl + R` / `Cmd + R`：刷新页面
- `F11`：全屏模式
- `Ctrl + P` / `Cmd + P`：打印结果

---

<div align="center">

**Happy Analyzing! | 分析愉快！** 🎨

</div>

