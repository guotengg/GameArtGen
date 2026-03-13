# GameArtGen

基于 RAG 增强 Prompt 的游戏概念图生成系统（Flask版）。

## 功能
- 风格知识库检索（RAG）
- Prompt 自动增强（中文输入，英文输出）
- 图像生成（默认尝试 Stable Diffusion，失败时回退 Mock）
- 历史记录与点赞/点踩反馈

## 项目结构
- `app/rag.py`: 风格知识库加载与检索
- `app/prompt_enhancer.py`: Prompt 增强逻辑
- `app/image_generator.py`: 生成器适配（Mock/Stable Diffusion）
- `app/pipeline.py`: 业务编排与历史/反馈落盘
- `app/web.py`: Flask 接口
- `templates/index.html` + `static/app.js`: 前端页面

## 快速开始（默认尝试 Stable Diffusion）
```bash
cd /home/RAID5/gt/LocalProjects/GameArtGen
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

打开 `http://127.0.0.1:5000`。

## 安装 Stable Diffusion 依赖

CPU 版本：
```bash
pip install -r requirements-sd-cpu.txt
```

GPU 版本（CUDA 12.1）：
```bash
pip install -r requirements-sd-gpu-cu121.txt
```

## 运行参数
```bash
export GAG_USE_SD=1
export GAG_SD_MODEL_ID=runwayml/stable-diffusion-v1-5
# 可选：严格模式，SD加载失败时直接报错，不回退Mock
export GAG_SD_STRICT=1
python run.py
```

## 如何确认当前真在用 Stable Diffusion
`/generate` 返回字段里会包含：
- `backend`: `stable-diffusion` 或 `mock`
- `model_id`: 实际模型ID
- `device`: `cuda` 或 `cpu`

若你看到 `backend=mock`，表示 SD 初始化失败并已回退。

## 测试
```bash
cd /home/RAID5/gt/LocalProjects/GameArtGen
python3 -m unittest discover -s tests -v
```
