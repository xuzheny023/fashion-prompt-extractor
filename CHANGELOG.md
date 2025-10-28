# Changelog | 更新日志

All notable changes to this project will be documented in this file.

本文件记录项目的所有重要更改。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-10-28

### Added | 新增
- ✨ **Complete bilingual support** (Chinese/English) for UI and AI outputs
  - 完整的双语支持（中文/英文）界面和 AI 输出
- 🔧 **Three analysis modes**: Fabric, Print, Construction with auto-detection
  - 三种分析模式：面料、印花、工艺，支持自动识别
- 💰 **Multi-budget recommendations**: Low-cost, Mid-range, and High-end options
  - 多预算推荐：低成本、中等、高端三档选择
- 🎯 **Context-aware analysis**: Budget level, use case, and constraints integration
  - 场景化分析：集成预算档位、使用场景和约束条件
- ⚠️ **DFM risk assessment**: Identify potential manufacturability issues
  - DFM 风险评估：识别潜在可制造性问题
- 📌 **Next actions**: Automated workflow recommendations
  - 下一步行动：自动化工作流程建议
- 📖 **Comprehensive documentation**: README, User Guide, and CHANGELOG
  - 全面文档：README、使用指南和更新日志
- ✂️ **Interactive cropping tool**: streamlit-cropper integration
  - 交互式裁剪工具：集成 streamlit-cropper

### Changed | 更改
- 🎨 **Redesigned UI layout**: Left panel for image/cropping, right panel for results
  - 重新设计 UI 布局：左侧图片/裁剪，右侧结果显示
- 🚀 **Upgraded to qwen-vl-max**: Better accuracy and performance
  - 升级到 qwen-vl-max：更高准确度和性能
- 📝 **Enhanced prompts**: Detailed, task-specific prompt templates
  - 增强提示词：详细的任务特定提示词模板
- 🌐 **Language switcher**: Moved to top of sidebar for better accessibility
  - 语言切换器：移至侧边栏顶部，更易访问

### Fixed | 修复
- 🐛 **JSON parsing**: Robust extraction from various API response formats
  - JSON 解析：鲁棒提取各种 API 响应格式
- 🔧 **Port conflicts**: Automatic port selection and process management
  - 端口冲突：自动端口选择和进程管理
- 🖼️ **Image encoding**: Correct base64 data URI format for DashScope API
  - 图像编码：DashScope API 的正确 base64 data URI 格式
- 🌍 **English output**: Enforced English-only content in EN mode
  - 英文输出：EN 模式强制纯英文内容

### Removed | 移除
- 🗑️ **Local LLM support**: Focused on cloud-only architecture
  - 本地 LLM 支持：专注于纯云端架构
- 🗑️ **Redundant documentation**: Cleaned up outdated .txt and .md files
  - 冗余文档：清理过时的 .txt 和 .md 文件
- 🗑️ **Unused dependencies**: Streamlined requirements.txt
  - 未使用依赖：精简 requirements.txt

---

## [1.0.0] - 2025-10 (Initial Version | 初始版本)

### Added | 新增
- 🎉 **Initial release**: Basic fabric recognition functionality
  - 初始发布：基础面料识别功能
- 📸 **Image upload**: Support for JPG, JPEG, PNG formats
  - 图片上传：支持 JPG、JPEG、PNG 格式
- 🤖 **AI analysis**: Integration with DashScope API
  - AI 分析：集成灵积 API
- 📊 **Basic results display**: Material identification and recommendations
  - 基础结果显示：材质识别和推荐

---

## Upcoming Features | 即将推出

### [2.1.0] - Planned | 计划中
- 📥 **Export functionality**: PDF and JSON export of analysis results
  - 导出功能：分析结果的 PDF 和 JSON 导出
- 📊 **Batch processing**: Analyze multiple images in one session
  - 批量处理：一次会话分析多张图片
- 💾 **History**: Save and review past analyses
  - 历史记录：保存和查看过往分析
- 🔄 **Comparison mode**: Side-by-side analysis of multiple regions
  - 对比模式：多区域并排分析

### [3.0.0] - Future Vision | 未来愿景
- 🎨 **Design generation**: AI-suggested fabric combinations
  - 设计生成：AI 建议的面料组合
- 🏭 **Supplier database**: Direct sourcing recommendations
  - 供应商数据库：直接采购推荐
- 💬 **Chatbot interface**: Conversational analysis workflow
  - 聊天机器人界面：对话式分析工作流
- 📱 **Mobile app**: Native iOS and Android applications
  - 移动应用：原生 iOS 和 Android 应用

---

## Development Notes | 开发说明

### Technical Stack | 技术栈
- **Frontend | 前端**: Streamlit 1.32+
- **AI Model | AI 模型**: Qwen-VL-Max (Alibaba Cloud)
- **Image Processing | 图像处理**: PIL/Pillow
- **Cropping | 裁剪**: streamlit-cropper
- **Language | 语言**: Python 3.8+

### Known Issues | 已知问题
- ⚠️ **Cropper compatibility**: May fall back to manual input on some systems
  - 裁剪器兼容性：某些系统可能回退到手动输入
- ⚠️ **Large images**: Processing time increases with image size (>2MB)
  - 大图片：图片大小超过 2MB 时处理时间增加
- ⚠️ **API rate limits**: Subject to DashScope API quotas
  - API 限流：受灵积 API 配额限制

### Contributing | 贡献
We welcome contributions! Please see our contribution guidelines in the repository.

欢迎贡献！请查看仓库中的贡献指南。

### License | 许可证
MIT License - See LICENSE file for details

MIT 许可证 - 详见 LICENSE 文件

---

<div align="center">

**For support, please open an issue on GitHub**

**如需支持，请在 GitHub 上开启 issue**

Made with ❤️ by AI Fashion Tech Team

AI 时尚科技团队用 ❤️ 制作

</div>

