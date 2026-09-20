# Optional WeMM semantic backend

The default installation is CPU keyword search. This optional mode loads the actual
WeMM-Embedding-9B query encoder and compares it to the archived vectors, then combines
semantic and lexical ranks. It does not rebuild the document vectors.

The original encoder ran on Linux, an NVIDIA RTX 5090 with 32 GB VRAM, PyTorch
2.13.0+cu132, Transformers 5.15.0, NumPy 2.4.4 and Accelerate 1.14.0. This is a tested
reference environment, not a claim of compatibility with every GPU. A 9B bf16 model
has substantial memory and disk needs; reserve tens of GB for the model download and
cache, and avoid loading a second copy alongside another GPU service. macOS Metal
and CPU model execution are not implemented by this optional backend. Windows users
can use the basic mode natively; the semantic reference environment is Linux/WSL2.

1. Create and activate a Python 3.11+ virtual environment.
2. Install matching CUDA builds of PyTorch and torchvision using the official selector for your GPU/driver:
   https://pytorch.org/get-started/locally/ . Do not blindly install a different CUDA
   wheel just because it is in an old transcript.
3. Install `python -m pip install -r requirements-wemm.txt`.
4. After the user accepts the model download, run:

```sh
python archive.py --backend wemm search '巴菲特如何理解保险浮存金？'
```

On first use this downloads `tencent/WeMM-Embedding-9B` at revision
`00c52839de57a6d4fd5b78cf5522ccf0ac8ea482` from Hugging Face. The upstream model includes
custom Python code loaded with `trust_remote_code=True`; the pinned revision prevents
silently following later upstream code changes. Review model code and license if
required by your environment. Model weights are not redistributed in this repository.

With an existing matching model directory:

```sh
python archive.py --backend wemm --model-path /path/to/WeMM-Embedding-9B search 'insurance float'
python archive.py --backend wemm --model-path /path/to/WeMM-Embedding-9B mcp
```

For MCP, install `requirements-mcp.txt` too and add `--backend`, `wemm` before `mcp` in
the command arguments. Keep the server alive so each query does not reload the model.

Embedding contract: `wemm-text-rightpad-fp32norm-v2`; upstream text chat template,
right padding, final `<embedding>` token, first 1024 output dimensions, float32 L2
normalization, no silent input truncation, maximum 8192 input model tokens. Existing
vectors use little-endian float32. Replacing WeMM with another model, dimension or
prompt format invalidates vector comparisons.

Official sources:
- https://github.com/Tencent/WeMM-Embedding
- https://huggingface.co/tencent/WeMM-Embedding-9B
