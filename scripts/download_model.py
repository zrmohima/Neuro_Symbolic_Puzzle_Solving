"""Download the pinned MLX 4-bit Qwen3-8B checkpoint."""
import json,os
from pathlib import Path
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
from huggingface_hub import HfApi, snapshot_download
root=Path(__file__).resolve().parents[1]
metadata_path=root/'datasets/metadata/model.json'
if metadata_path.exists():
    metadata=json.loads(metadata_path.read_text())
else:
    model_id='mlx-community/Qwen3-8B-4bit'
    metadata={'id':model_id,'sha':HfApi().model_info(model_id).sha}
    metadata_path.parent.mkdir(parents=True,exist_ok=True)
    metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'Pinned {model_id} at {metadata["sha"]} in {metadata_path}')
snapshot_download(metadata['id'],revision=metadata['sha'],local_dir=root/'models/Qwen3-8B-4bit',allow_patterns=['*.json','*.safetensors','*.txt','LICENSE'],max_workers=2)
