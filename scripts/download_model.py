"""Download the pinned MLX 4-bit Qwen3-8B checkpoint."""
import json,os
from pathlib import Path
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
from huggingface_hub import snapshot_download
root=Path(__file__).resolve().parents[1]
metadata=json.loads((root/'datasets/metadata/model.json').read_text())
snapshot_download(metadata['id'],revision=metadata['sha'],local_dir=root/'models/Qwen3-8B-4bit',allow_patterns=['*.json','*.safetensors','*.txt','LICENSE'],max_workers=2)
