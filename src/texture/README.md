# Textured and Colored LEGO Model Generation.
## Getting Started

### Dependencies

Follow [FlashTex](https://github.com/Roblox/FlashTex/tree/main) to install the dependencies.

---

### Textured LEGO Model Generation

Given a LEGO LDR file and a text prompt as input, generate the UV texture for it.

```
export INPUT="./examples/chair.ldr"     # Input LDR file
export OUTPUT="./out/chair"             # Output dir
export PROMPT="Rustic farmhouse armchair built from reclaimed wood, showing pixelated grain patterns and warm distressed textures, best quality, hd"                        # Text Prompt

bash scripts/generate_texture.sh $INPUT $OUTPUT $PROMPT
```


### Colored LEGO Model Generation

TBD