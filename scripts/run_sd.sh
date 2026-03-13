#!/usr/bin/env bash
# 以 Stable Diffusion 模式启动 GameArtGen（国内镜像加速）
set -e

cd "$(dirname "$0")/.."

# ── HuggingFace 国内镜像 ──────────────────────────────────────────────────────
export HF_ENDPOINT="https://hf-mirror.com"
export HUGGINGFACE_HUB_VERBOSITY="info"

# ── 生成器配置 ────────────────────────────────────────────────────────────────
export GAG_USE_SD=1
export GAG_SD_MODEL_ID="${GAG_SD_MODEL_ID:-runwayml/stable-diffusion-v1-5}"
export GAG_SD_STRICT=1          # SD 加载失败时直接报错，不静默回退 Mock
export GAG_SD_STEPS="${GAG_SD_STEPS:-30}"
export GAG_SD_GUIDANCE="${GAG_SD_GUIDANCE:-7.5}"

echo "=================================================="
echo "  GameArtGen - Stable Diffusion 模式"
echo "  模型 : $GAG_SD_MODEL_ID"
echo "  镜像 : $HF_ENDPOINT"
echo "=================================================="
echo ""
echo "提示：首次运行会从镜像下载模型（约 4GB），请耐心等待。"
echo "      模型下载后会缓存到 ~/.cache/huggingface/，之后秒启动。"
echo ""

python run.py

