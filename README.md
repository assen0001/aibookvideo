# AI读书视频创作平台
## 平台简介
- 本平台为一站式全流程生成AI读书短视频，输入1个主题 → 输出1部专业级短视频（含分镜/画面/配音/剪辑）
- 功能定位：基于开源技术栈的本地化部署AI读书短视频创作平台，实现从主题到视频的全流程自动化生产。
- 核心技术
 1. 自研AI读书视频创作平台
 2. N8N智能体流程调度平台
 3. 大语言模型：Ollama+DeepSeek
 4. ComfyUI+Flux生图模型
 5. 通义万相wan2.1视频模型
 6. OpenVoice语音合成
- 平台优势
 1. 本地化部署
  - 全部采用本地化部署，无需调用外部API，无额外成本
 2. AI智能编剧
  - 可按书籍类型定制文案生成模板
 3. 低成本批量创建
  - 本地化部署，无额外视频创作成本
 4. 多平台适配
  - 支持抖音、B站、小红书、今日头条等平台

## 作者联系方式：
 - 作者：assen
 - 官网（演示平台）：https://aibook.shgis.com/
 - B站演示视频链接：https://space.bilibili.com/1105978078/upload/video
 - Github项目链接：https://github.com/assen0001/aibookvideo
 - 联系邮箱：17305566@qq.com
 - 微信扫码加入交流群 ![微信交流群](static/images/wx001.jpg)

## 安装指南
1. 环境准备
   - Python 3.9+
   - Git
   - FFmpeg (用于视频处理)


2. 克隆项目
```bash
git clone https://github.com/assen0001/aibookvideo.git
cd aibookvideo
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境
   - 本地部署Ollama + DeepSeek，并在config.json中配置调用API地址
   - 本地部署ComfyUI + Flux + Wan2.1，并在config.json中配置调用API地址
   - 本地部署OpenVoice，并在config.json中配置调用API地址
   - 修改config.json中数据库配置信息

## 使用说明
1. 启动服务
```bash
python main.py
```

2. 访问平台
   - 打开浏览器访问 http://localhost:5000

3. 基本流程
   - 输入主题/书名
   - 生成文案脚本
   - 生成分镜画面
   - 合成语音
   - 生成最终视频
   - 下载或分享视频

4. 高级功能
   - 批量生成：支持同时处理多个主题
   - 模板定制：可自定义文案生成模板
   - 风格调整：可修改视频风格参数


## 许可协议
- MIT，本项目采用 MIT 许可协议 (LICENSE) 发布。
