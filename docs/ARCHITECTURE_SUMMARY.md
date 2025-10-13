# 架构总览

## 📐 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                            │
│                  app.py (Streamlit UI)                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      统一引擎层                              │
│              src/core/recommender.py                        │
│          recommend(image) → (Result, Meta)                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────┐    ┌──────────────────┐    ┌─────────────┐
│  CLIP 编码   │    │   向量检索       │    │  AI 复核    │
│ dual_clip.py │    │ fabric_clip_     │    │ ai_boost.py │
│              │    │   ranker.py      │    │  (可选)     │
│ 1536 维向量  │    │ 两阶段检索       │    │ LMM 复核    │
└──────────────┘    └──────────────────┘    └─────────────┘
        ↓                     ↓                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                              │
│  • types.py       - 标准数据类型                            │
│  • config.py      - 统一配置                                │
│  • utils/logger   - 日志系统                                │
│  • fabric_labels  - 中文标签                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        数据层                                │
│  • data/fabric_bank.npz       - 向量库                      │
│  • data/fabric_centroids.npz  - 类中心                      │
│  • data/fabric_labels.json    - 中文名                      │
│  • data/fabrics/              - 原始图片                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗂️ 目录结构

```
fashion-prompt-extractor/
├── app.py                          # Streamlit UI 主入口
├── src/                            # 核心代码
│   ├── core/                       # 核心引擎层 ⭐
│   │   ├── __init__.py
│   │   └── recommender.py          # 统一推荐入口
│   ├── types.py                    # 标准数据类型 ⭐
│   ├── config.py                   # 统一配置中心 ⭐
│   ├── dual_clip.py                # 双通道 CLIP 编码器
│   ├── fabric_clip_ranker.py       # 向量检索
│   ├── ai_boost.py                 # AI 复核 ⭐
│   ├── fabric_labels.py            # 中文标签管理
│   └── utils/                      # 工具模块
│       ├── __init__.py
│       └── logger.py               # 日志系统 ⭐
├── data/                           # 数据目录
│   ├── fabric_bank.npz             # 向量库
│   ├── fabric_centroids.npz        # 类中心向量
│   ├── fabric_labels.json          # 中文标签
│   └── fabrics/                    # 面料图片库
│       ├── cotton/
│       ├── linen/
│       └── ...
├── tools/                          # 工具脚本
│   ├── build_fabric_bank.py        # 构建向量库
│   ├── test_recommender.py         # 推荐引擎测试 ⭐
│   ├── verify_recommender.py       # 快速验证 ⭐
│   ├── test_types.py               # 数据类型测试 ⭐
│   ├── test_logger.py              # 日志测试 ⭐
│   └── test_config.py              # 配置测试 ⭐
├── docs/                           # 文档
│   ├── RECOMMENDER_GUIDE.md        # 推荐引擎指南 ⭐
│   ├── TYPES_GUIDE.md              # 数据类型指南 ⭐
│   └── ARCHITECTURE_SUMMARY.md     # 本文件 ⭐
├── .env.example                    # 配置示例
├── requirements.txt                # Python 依赖
└── README.md                       # 项目说明

⭐ = 本次重构新增/重要更新
```

---

## 🎯 核心模块

### 1. 统一引擎层 (`src/core/recommender.py`)

**职责：** 整合完整推荐流程

```python
from src.core.recommender import recommend

result, meta = recommend(image)
```

**内部流程：**
1. CLIP 编码（1536 维）
2. 向量检索（两阶段）
3. AI 复核（可选）
4. 标准化输出

**优势：**
- ✅ 单一入口，简化调用
- ✅ 自动优化流程
- ✅ 统一错误处理
- ✅ 完整日志记录

---

### 2. 标准数据类型 (`src/types.py`)

**职责：** 定义统一的数据结构

```python
from src.types import ScoreItem, RankedResult, QueryMeta

# 评分项
item = ScoreItem(label="cotton", score=0.85)

# 排名结果
result = RankedResult(
    items=[item1, item2, item3],
    ai_reason="CLIP 检索"
)

# 性能指标
meta = QueryMeta(ms=185, coarse_max=0.92)
```

**优势：**
- ✅ 类型安全
- ✅ 数据验证
- ✅ 内置便捷方法
- ✅ IDE 自动补全

---

### 3. 统一配置 (`src/config.py`)

**职责：** 集中管理所有配置

```python
from src.config import cfg

print(cfg.TOPK)          # 返回结果数
print(cfg.AI_BACKEND)    # AI 后端
print(cfg.FABRIC_BANK)   # 向量库路径
```

**支持：**
- ✅ 默认值
- ✅ 环境变量覆盖
- ✅ .env 文件
- ✅ 类型验证

---

### 4. 日志系统 (`src/utils/logger.py`)

**职责：** 统一日志管理

```python
from src.utils.logger import get_logger

log = get_logger("my_module")
log.info("启动成功")
log.warning("检索较慢")
log.error("向量库不存在")
```

**特性：**
- ✅ 控制台彩色输出
- ✅ 文件自动轮转
- ✅ 模块化标识
- ✅ 异步写入

---

### 5. AI 复核 (`src/ai_boost.py`)

**职责：** 多模态大模型辅助

```python
from src.ai_boost import LMMReranker

reranker = LMMReranker()
if reranker.should_rerank(scores):
    candidates = reranker.rerank(image, candidates)
```

**支持后端：**
- OpenAI (gpt-4o-mini)
- Ollama (llava)
- None (禁用)

**触发条件：**
- 最高分 < 0.30（低置信度）
- 前两名差距 < 0.03（边界模糊）

---

## 🔄 数据流

### 典型推荐流程

```
用户上传图片
    ↓
app.py 调用 recommend(image)
    ↓
┌─────────────────────────────────────┐
│ FabricRecommendEngine               │
│                                     │
│ 1. _encode_image()                 │
│    → 1536 维向量 (L2 归一化)       │
│                                     │
│ 2. retrieve_topk()                 │
│    → 粗排: 类中心相似度            │
│    → 精排: 完整样本相似度          │
│                                     │
│ 3. LMMReranker.should_rerank()     │
│    → 判断是否需要 AI 复核          │
│                                     │
│ 4. LMMReranker.rerank()            │
│    → 调用多模态大模型              │
│    → 调整排名                       │
│                                     │
│ 5. 构建结果                         │
│    → RankedResult + QueryMeta      │
└─────────────────────────────────────┘
    ↓
返回给 app.py
    ↓
UI 渲染结果
```

---

## 📊 性能指标

### 典型性能表现

| 阶段 | 耗时 | 说明 |
|------|------|------|
| CLIP 编码 | 50-100ms | 首次调用需加载模型（~2s） |
| 粗排（类中心） | 5-10ms | 仅计算 64 个类中心相似度 |
| 精排（完整样本） | 20-50ms | 计算 12×10 个样本相似度 |
| AI 复核（可选） | 2-5s | 网络延迟主导 |
| **总计（无 AI）** | **100-200ms** | ✅ |
| **总计（含 AI）** | **2-5s** | 低频触发 |

### 优化建议

1. **首次加载慢** → 应用启动时预热引擎
2. **检索慢** → 启用 FAISS 加速
3. **AI 慢** → 使用本地 Ollama 或禁用

---

## 🧪 测试覆盖

### 单元测试

| 模块 | 测试脚本 | 覆盖内容 |
|------|----------|----------|
| types.py | `tools/test_types.py` | 数据验证、方法功能 |
| config.py | `tools/test_config.py` | 配置加载、环境变量 |
| logger.py | `tools/test_logger.py` | 日志输出、文件轮转 |
| recommender.py | `tools/test_recommender.py` | 完整推荐流程 |

### 集成测试

```bash
# 快速验证（10秒）
python tools/verify_recommender.py

# 完整测试（30秒）
python tools/test_recommender.py

# 端到端测试（手动）
streamlit run app.py
```

---

## 🔧 配置管理

### 配置优先级

```
代码默认值 < .env 文件 < 环境变量 < 函数参数
```

### 关键配置项

```bash
# .env 示例

# ========== 检索参数 ==========
TOPK=5                    # 返回结果数
TOPC=12                   # 粗排候选数
LOW_CONF=0.30             # 低置信度阈值
CLOSE_GAP=0.03            # 分数差阈值

# ========== AI 复核 ==========
AI_BACKEND=none           # none | openai | ollama
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini

# ========== 性能开关 ==========
ENABLE_FAISS=true         # FAISS 加速
ENABLE_CACHE=true         # 缓存
ENABLE_CLIP=true          # CLIP 检索

# ========== 日志 ==========
LOG_LEVEL=INFO            # DEBUG | INFO | WARNING
LOG_FILE=logs/app.log

# ========== 路径 ==========
FABRIC_BANK=data/fabric_bank.npz
FABRIC_CENTROIDS=data/fabric_centroids.npz
```

---

## 📈 扩展性

### 添加新的 AI 后端

```python
# src/ai_boost.py

def _rerank_custom(self, image, candidates):
    """使用自定义后端"""
    # 实现你的逻辑
    pass

def rerank(self, image, candidates):
    if self.backend == "custom":
        return self._rerank_custom(image, candidates)
    # ...
```

### 添加新的检索策略

```python
# src/core/recommender.py

def recommend(self, image, strategy="clip"):
    if strategy == "clip":
        results = retrieve_topk(...)
    elif strategy == "hybrid":
        # 结合规则和向量
        clip_results = retrieve_topk(...)
        rule_results = recommend_by_rules(...)
        results = merge_results(clip_results, rule_results)
    # ...
```

### 添加新的数据类型

```python
# src/types.py

@dataclass
class DetailedMeta(QueryMeta):
    """扩展的性能指标"""
    encode_ms: int = 0
    coarse_ms: int = 0
    fine_ms: int = 0
    ai_ms: int = 0
```

---

## 🚀 部署建议

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 构建向量库
python tools/build_fabric_bank.py

# 启动 UI
streamlit run app.py
```

### 生产环境

```bash
# 使用 gunicorn + Streamlit
pip install gunicorn

# 预热引擎
python -c "from src.core.recommender import get_engine; get_engine()"

# 启动服务
streamlit run app.py --server.port 8501
```

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 预构建向量库
RUN python tools/build_fabric_bank.py

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [RECOMMENDER_GUIDE.md](./RECOMMENDER_GUIDE.md) | 推荐引擎使用指南 |
| [TYPES_GUIDE.md](./TYPES_GUIDE.md) | 数据类型详解 |
| [LOGGER_GUIDE.md](./LOGGER_GUIDE.md) | 日志系统说明 |
| [CONFIG_GUIDE.md](./CONFIG_GUIDE.md) | 配置管理 |
| [CLIP_IMPLEMENTATION_SUMMARY.md](../CLIP_IMPLEMENTATION_SUMMARY.md) | CLIP 技术细节 |

---

## 🎓 开发指南

### 代码风格

```python
# ✅ 推荐
from src.core.recommender import recommend
from src.types import RankedResult, QueryMeta
from src.utils.logger import get_logger

log = get_logger(__name__)

def process_image(img_path: str) -> RankedResult:
    img = Image.open(img_path)
    result, meta = recommend(img)
    log.info(f"处理完成: {meta.ms}ms")
    return result
```

### 错误处理

```python
from src.core.recommender import recommend
from src.utils.logger import get_logger

log = get_logger("app")

try:
    result, meta = recommend(image)
except FileNotFoundError:
    log.error("向量库不存在，请先构建")
    raise
except Exception as e:
    log.exception("推荐失败")
    raise
```

### 性能监控

```python
from src.core.recommender import recommend
from src.utils.logger import get_logger

log = get_logger("monitor")

result, meta = recommend(image)

if meta.ms > 500:
    log.warning(f"检索过慢: {meta.ms}ms")
if result.top1.score < 0.50:
    log.warning(f"置信度低: {result.top1.score:.2f}")
```

---

## ✅ 重构完成清单

- [x] 统一配置中心 (`src/config.py`)
- [x] 统一日志系统 (`src/utils/logger.py`)
- [x] 标准化数据类型 (`src/types.py`)
- [x] AI 复核模块 (`src/ai_boost.py`)
- [x] 统一引擎层 (`src/core/recommender.py`)
- [x] 完整测试套件
- [x] 详细文档

---

## 🎯 下一步

1. **迁移 app.py** - 使用 `recommend()` 替换现有逻辑
2. **性能优化** - 启用 FAISS、预热引擎
3. **功能扩展** - 添加批量处理、结果缓存
4. **生产部署** - Docker 容器化、监控告警

---

✅ **重构架构已完成！** 现在整个系统结构清晰、易于维护和扩展。 🎉

