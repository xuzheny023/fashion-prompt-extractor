from __future__ import annotations
import os
from pathlib import Path
from typing import List
import numpy as np
import torch
from PIL import Image

# Transformers(OpenAI) CLIP
from transformers import CLIPModel, CLIPImageProcessor
# LAION open_clip
import open_clip

def _to_numpy(x: torch.Tensor) -> np.ndarray:
    return x.detach().cpu().numpy().astype("float32")

class DualCLIPEncoder:
    """
    双通道特征融合：
      - chan1: Transformers(OpenAI) ViT-B/32  → 全局语义
      - chan2: open_clip LAION ViT-H/14       → 纹理细节
    融合：cat([z1,z2]) 后 L2 归一化，输出 float32 [1536]
    """
    def __init__(
        self,
        hf_model_dir: str | Path = r"C:\Users\洋\.cache\open_clip\ViT-B-32\openai",  # 你的本地 HF 权重目录（含 pytorch_model.bin / config.json）
        oc_arch: str = "ViT-H-14",
        oc_pretrained: str = "laion2b_s32b_b79k",
        device: str | None = None,
        fp16: bool = True,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        # --- chan1: HF(OpenAI) ---
        try:
            self.hf_model = CLIPModel.from_pretrained(hf_model_dir, local_files_only=True).to(self.device)
        except Exception:
            self.hf_model = CLIPModel.from_pretrained(hf_model_dir).to(self.device)
        self.hf_model.eval()
        if fp16 and self.device == "cuda":
            self.hf_model = self.hf_model.half()
        self.hf_proc = CLIPImageProcessor.from_pretrained(hf_model_dir, local_files_only=False)

        # --- chan2: open_clip(LAION) ---
        cache_dir = os.getenv("OPENCLIP_CACHE_DIR", None)
        self.oc_model, _, self.oc_preproc = open_clip.create_model_and_transforms(
            oc_arch, pretrained=oc_pretrained, cache_dir=cache_dir
        )
        self.oc_model = self.oc_model.to(self.device).eval()
        if fp16 and self.device == "cuda":
            self.oc_model = self.oc_model.half()

    @torch.no_grad()
    def _encode_hf(self, img: Image.Image) -> torch.Tensor:
        px = self.hf_proc(images=img.convert("RGB"), return_tensors="pt")
        model_dtype = self.hf_model.dtype
        px = {k: (v.to(self.device).half() if (model_dtype==torch.float16 and v.dtype==torch.float32) else v.to(self.device)) for k,v in px.items()}
        z = self.hf_model.get_image_features(**px)
        return torch.nn.functional.normalize(z, dim=-1)  # [1,512]

    @torch.no_grad()
    def _encode_oc(self, img: Image.Image) -> torch.Tensor:
        px = self.oc_preproc(img.convert("RGB")).unsqueeze(0).to(self.device)
        # Check model parameter dtype instead of model.dtype
        model_dtype = next(self.oc_model.parameters()).dtype
        if model_dtype == torch.float16 and px.dtype == torch.float32:
            px = px.half()
        z = self.oc_model.encode_image(px)
        return torch.nn.functional.normalize(z, dim=-1)  # [1,1024]

    @torch.no_grad()
    def image_to_emb(self, img: Image.Image) -> np.ndarray:
        z1 = self._encode_hf(img)
        z2 = self._encode_oc(img)
        z  = torch.cat([z1, z2], dim=-1)      # [1, 1536]
        z  = torch.nn.functional.normalize(z, dim=-1)
        return _to_numpy(z.squeeze(0))

_encoder_singleton: DualCLIPEncoder | None = None

def get_encoder() -> DualCLIPEncoder:
    global _encoder_singleton
    if _encoder_singleton is None:
        _encoder_singleton = DualCLIPEncoder()
    return _encoder_singleton

def image_to_emb(img: Image.Image) -> np.ndarray:
    return get_encoder().image_to_emb(img)

