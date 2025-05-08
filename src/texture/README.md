# Textured and Colored LEGO Model Generation

## Getting Started

### Dependencies

This project requires the following dependencies:

1. **FlashTex, ImportLDraw, and blender-render-toolkit.** These are provided as Git submodules; install them with
   `git submodule update --init`.
    - Some files in the ImportLDraw submodule are stored using the Git LFS system. To download these files,
      install [Git LFS](https://git-lfs.com), `cd` into the ImportLDraw directory, and run
      `git lfs pull`.
2. **LDraw library.** Download the LDraw parts library `complete.zip`
   from [here](https://library.ldraw.org/updates?latest), and
   extract it in your *home directory*.
3. **Blender.** Install [Blender](https://www.blender.org/download).
4. **Python dependencies.** This repo uses the project manager [uv](https://docs.astral.sh/uv/) to manage Python
   dependencies. [Install uv](https://docs.astral.sh/uv/getting-started/installation/), and run
   `uv sync --extra build && uv sync --extra compile` to create a Python virtual environment with all
   dependencies installed.

---

### Textured LEGO Model Generation

Given a LEGO LDR file and a text prompt as input, generate the UV texture for it.

```zsh
INPUT="./examples/chair.ldr"     # Input LDR file
OUTPUT="./out/chair"             # Output dir
TXT_PROMPT="Rustic farmhouse armchair built from reclaimed wood, showing pixelated grain patterns and warm distressed textures, best quality, hd"                        # Text Prompt

uv run scripts/generate_texture.py "${INPUT}" "${OUTPUT}" "${TXT_PROMPT}"
```

### Colored LEGO Model Generation

TBD