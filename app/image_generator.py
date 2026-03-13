from __future__ import annotations

import hashlib
from io import BytesIO
from typing import Protocol

from PIL import Image, ImageDraw

from app import config


class ImageGenerator(Protocol):
    backend: str
    model_id: str
    device: str

    def generate(self, prompt: str, negative_prompt: str) -> Image.Image:
        ...


class MockImageGenerator:
    backend = "mock"
    model_id = "mock-preview"
    device = "cpu"

    def generate(self, prompt: str, negative_prompt: str) -> Image.Image:
        # 使用prompt hash生成稳定配色，便于无GPU环境演示。
        digest = hashlib.md5(prompt.encode("utf-8")).hexdigest()
        r = int(digest[:2], 16)
        g = int(digest[2:4], 16)
        b = int(digest[4:6], 16)

        image = Image.new("RGB", (768, 512), color=(r, g, b))
        draw = ImageDraw.Draw(image)
        draw.rectangle([(20, 20), (748, 190)], fill=(0, 0, 0))

        # 默认字体在部分环境无法渲染中文，先转为ASCII可显示文本避免异常。
        safe_prompt = prompt.encode("ascii", errors="replace").decode("ascii")
        text = f"GameArtGen Preview\n{safe_prompt[:120]}"
        try:
            draw.text((30, 30), text, fill=(255, 255, 255))
        except Exception:
            draw.text((30, 30), "GameArtGen Preview", fill=(255, 255, 255))
        return image


class StableDiffusionImageGenerator:
    backend = "stable-diffusion"

    def __init__(self) -> None:
        import os
        import torch
        from diffusers import StableDiffusionPipeline

        # 使用国内镜像（hf-mirror.com），解决大陆无法访问 HuggingFace 的问题
        if config.HF_ENDPOINT and config.HF_ENDPOINT != "0":
            os.environ.setdefault("HF_ENDPOINT", config.HF_ENDPOINT)

        self.model_id = config.SD_MODEL_ID
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = self.pipe.to(self.device)

    def generate(self, prompt: str, negative_prompt: str) -> Image.Image:
        result = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=config.SD_STEPS,
            guidance_scale=config.SD_GUIDANCE,
        )
        return result.images[0]


def get_image_generator() -> ImageGenerator:
    if config.USE_SD:
        try:
            return StableDiffusionImageGenerator()
        except Exception:
            if config.SD_STRICT:
                raise
            return MockImageGenerator()
    return MockImageGenerator()


def image_to_base64_png(image: Image.Image) -> str:
    import base64

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
