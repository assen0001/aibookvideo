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
 6. Coqui-TTS语音合成

## 平台优势
 1. 开源本地化部署
  - 采用开源技术栈+本地部署，无需依赖外部服务，数据安全可控
 2. AI智能编剧
  - 可按书籍类型定制文案生成模板
 3. 低成本批量创建
  - 本地化部署（或算力租赁部署），无额外视频创作成本
 4. 多平台适配
  - 支持抖音、B站、小红书、今日头条等平台

## 作者联系方式：
 - 作者：assen
 - 官网（演示平台）：https://aibook.shgis.com/
 - B站演示视频链接：https://space.bilibili.com/1105978078/upload/video
 - Github项目链接：https://github.com/assen0001/aibookvideo
 - 赞助我们：https://shgis.com/58524.html
 - 联系邮箱：17305566@qq.com
 - 有任何问题欢迎联系我们，提供技术支持。
 - 微信扫码加入交流群 
 <img src="static/images/wx001.jpg" width=100 height=100>

## 安装指南
1. 环境准备
   - Python >=3.9, <3.12
   - Git
   - FFmpeg
   - Moviepy
   - MySQL

2. 克隆项目
```bash
git clone https://github.com/assen0001/aibookvideo.git
cd aibookvideo
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 环境相关问题
- 安装 PyTorch：Coqui TTS 依赖 PyTorch。建议先根据你的环境（是否使用 GPU）安装合适的 PyTorch 版本。
```bash
# 对于 CUDA 11.8 的 GPU 环境：
pip install torch==2.7.1+cu118 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu118
# 对于 仅 CPU 环境：
pip install torch==2.7.1+cpu torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cpu
```

5. 配置环境
   - 本地部署Ollama + DeepSeek，并在.env中配置调用API地址
   - 本地部署ComfyUI + Flux + Wan2.1，并在.env中配置调用API地址
   - 本地部署N8N智能体流程调度平台，并在.env中配置调用API地址
   - 本地部署Coqui-TTS语音合成模型，并在.env中配置调用API地址（详见：）
   - 修改.env中数据库配置信息

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
   - 可一键生成视频，也可以分步骤生成

4. 高级功能（部分开发中）
   - 批量生成：支持同时处理多个主题
   - 模板定制：可自定义文案生成模板
   - 风格调整：可修改视频风格参数


## 许可协议
- MIT，本项目采用 MIT 许可协议 (LICENSE) 发布。


## 版本更新日志
- 1.3.1 2025.8.25
  - 优化coqui-tts语音生成代码
  - 优化n8n流程调度地址参数
  - 优化.venv环境中包版本匹配
  - 优化了视频生成流程

- 1.3.0 功能优化 2025.8.20
  - 增加生成视频任务查看管理功能
  - 视频合成分辨率调整为1080
  - 其他功能和样式优化
  - 更新演示平台代码

- 1.2.0 一键生成视频功能 2025.8.15
  - 新增了一键生成视频功能
  - 已生成视频列表
  - 切换开发环境到Trae

- 1.1.0 语音模型切换 2025.8.5
  - 切换语音生成模型为Coqui-TTS
  - 新增语音合成功能
  - 优化了性能

- 1.0.0 初始版本发布 2025.7.30
  - 书单管理：书单、文案、字幕、风格管理
  - 图片管理：字幕段落、提示词手动优化、翻译、图片重做、运镜动作
  - 视频创作：视频分镜、字幕配音、视频剪辑合成
  - 演示平台上线：https://aibook.shgis.com/

- 0.4.0 N8N工作流配置 2025.7.12
  - 配置了N8N智能体流程调度平台工作流
  - 调用ollama模型生成书单文案
  - 调用ComfyUI+Flux模型生成图片
  - 调用通义万相模型生成视频

- 0.3.0 项目优化 2025.7.10
  - 实现基本书单到视频生成功能
  - 完成ollama、comfyui、通义万相等部署和测试

- 0.2.0 功能开发 2025.7.7
  - 图片和视频管理功能开发

- 0.1.0 功能开发 2025.7.4
  - 书单管理功能开发

- 0.0.1 项目初始化 2025.7.3
  - 项目初始化，配置了基础的项目结构和文件
  - 配置了Flask框架，实现了基本的路由和视图函数
  - 配置了mysql数据库，创建基本表结构
