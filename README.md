# LegoGPT

<div>
<a href="https://avalovelace1.github.io/LegoGPT/"><img src="https://img.shields.io/badge/Project_Page-Website-green?logo=googlechrome&logoColor=white" alt="Project Page" height=22px></a>
<a href="" target="_blank"><img src=https://img.shields.io/badge/ArXiv-Paper-b5212f.svg?logo=arxiv alt="ArXiv" height=22px></a>
<a href="" target="_blank"><img src=https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Demo-blue.svg alt="HuggingFace" height=22px></a>
</div>

This is the official repository for **LegoGPT**, the first approach for generating physically stable LEGO
brick models from text prompts.

<img src="assets/teaser.jpg" alt="Teaser figure"/>

***Generating Physically Stable and Buildable LEGO® Designs from Text***  
[Ava Pun*](https://avapun.com/),
[Kangle Deng*](https://dunbar12138.github.io/),
[Ruixuan Liu*](https://waynekyrie.github.io/),
[Deva Ramanan](https://www.cs.cmu.edu/~deva/),
[Changliu Liu](https://www.ri.cmu.edu/ri-faculty/changliu-liu/),
[Jun-Yan Zhu](https://www.cs.cmu.edu/~junyanz/)  
Carnegie Mellon University

## Installation

### Prerequisites: Gurobi

Running stability analysis requires a [Gurobi licence](https://www.gurobi.com/downloads/) to use Gurobi. Academics may
request a free licence from the Gurobi website [here](https://www.gurobi.com/academia/academic-program-and-licenses/).

### Installing as a standalone project

This repo uses the Python project manager [uv](https://docs.astral.sh/uv/). To install this repo as a standalone
project, first install all prerequisites. Then,

1. Clone the repo: `git clone "https://github.com/AvaLovelace1/LegoGPT.git" && cd LegoGPT`.
2. *(Optional, required for running the `infer` script and texturing)* Follow these instructions to install ImportLDraw,
   required for rendering LEGO visualizations:
    - Install the ImportLDraw submodule with `git submodule update --init`.
        - Some files in the ImportLDraw submodule are stored using the Git LFS system. To download these files,
          install [Git LFS](https://git-lfs.com), `cd` into the ImportLDraw directory, and run
          `git lfs pull`.
    - Download the LDraw parts library `complete.zip` from [here](https://library.ldraw.org/updates?latest), and
      extract it in your *home directory*.
3. Finally, [install uv](https://docs.astral.sh/uv/getting-started/installation/), and run `uv sync` to create a Python
   virtual environment with all dependencies installed. Python dependencies are defined in `pyproject.toml`.

### Installing as a package

To install this repo as a package in your own Python project, first install all prerequisites. Then, run

```zsh
uv add "https://github.com/AvaLovelace1/LegoGPT.git"
```

if using uv, or

```zsh
pip install "https://github.com/AvaLovelace1/LegoGPT.git"
```

if using pip.

## Running inference interactively

You can run inference with the fine-tuned LegoGPT model using:

```zsh
uv run infer
```

This script starts an interactive session where you can input a prompt and get a response from the model.
The model weights will automatically be downloaded from Hugging Face; they can be
found [here](https://huggingface.co/AvaLovelace/LegoGPT).

If you wish to run inference with a different set of model weights, specify them using the `--model_name_or_path`
option. See `uv run infer -h` for a full list of options.

### Example interaction

Here is an example interaction using the `infer` script:

```text
> uv run infer
Enter a prompt, or <Return> to exit: Table featuring a flat rectangular surface over four evenly spaced legs.
Enter a filename to save the output image (default=output.png): output.png
Enter a generation seed (default=42): 42
Generating...
Set parameter Username
Academic license - for non-commercial use only - expires 2026-02-19
--------------------
Finished generating in 63.53s.
Total # bricks: 59
Total # brick rejections: 98
Brick rejection reasons: {'collision': 5, 'already_rejected': 93}
Total # regenerations: 4
Saved results to /home/apun/LegoGPT/output.txt, /home/apun/LegoGPT/output.ldr, and /home/apun/LegoGPT/output.png
--------------------
Enter another prompt, or <Return> to exit:
```

Three output files are created: `output.png`, `output.txt`, and `output.ldr`.

`output.png` contains a rendered image of the generated LEGO structure:

<img src="assets/output_img.png" alt="Rendered LEGO output image" width="256"/>

`output.txt` contains the LEGO structure in brick-by-brick text format, where each line of the form `hxw (x,y,z)`
represents a LEGO brick of height `h` and width `w` at position `(x,y,z)`:

```text
1x2 (16,18,0)
1x2 (16,13,0)
2x2 (0,18,0)
2x2 (0,13,0)
1x2 (16,18,1)
[...]
```

And finally, `output.ldr` contains the LEGO structure in LDraw format, which can be opened with any LDraw-compatible
software.

## Running texturing

The subdirectory `src/texture` contains the code for generating the UV texture or per-brick color given a LEGO design.
To run texturing, `cd` into `src/texture` and follow the instructions in the `README.md` file there.

## Running fine-tuning

LegoGPT was created by
fine-tuning [Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)
on the custom LEGO dataset [StableText2Lego](https://huggingface.co/datasets/AvaLovelace/StableText2Lego), converted
into instructional format. We used Hugging Face [TRL](https://huggingface.co/docs/trl/index)
with [Accelerate](https://huggingface.co/docs/accelerate/index) for fine-tuning.

To replicate the fine-tuning process, first install additional Python dependencies with `uv sync --extra finetuning`.
Then, follow these instructions:

1. Prepare the LEGO dataset for fine-tuning with
   `uv run prepare_finetuning_dataset --input_path AvaLovelace/StableText2Lego --output_path [FINETUNING_DATASET_PATH]`.
   This converts the dataset into the instructional format required for fine-tuning LLaMA.
    - If you wish to run fine-tuning with your own LEGO dataset, replace `AvaLovelace/StableText2Lego` with the path to
      your dataset. This dataset should have the fields "captions" and "lego". The "lego" field should contain a LEGO
      structure in the text format described in the paper, and the "captions" field should contain a list of one or more
      descriptions of the LEGO structure.
2. Download the pretrained [Llama-3.2-1B-Instruct model](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct) to
   some directory `[PRETRAINED_DIR]`.
   **IMPORTANT:** Replace the `config.json`, `special_tokens_map.json`, and `tokenizer_config.json` files with the ones
   in the `finetuning_config_files` directory. This specifies the `pad_token` to be different from the `eos_token`,
   fixing a fine-tuning [issue](https://github.com/unslothai/unsloth/issues/416) where the model will not learn to
   output EOS tokens properly.
3. Initialize the Accelerate config file with `uv run accelerate config`.
4. Run fine-tuning with
   `uv run ./scripts/finetune.zsh [PRETRAINED_DIR] [OUTPUT_DIR] [RUN_NAME] [FINETUNING_DATASET_PATH]`. The
   fine-tuned model will be saved to `[OUTPUT_DIR]/[RUN_NAME]`.

## Citation

If you find this repository useful for your research, please cite the following work.

```bibtex
@article{pun2025legogpt,
    title   = {Generating Physically Stable and Buildable LEGO Designs from Text},
    author  = {Pun, Ava and Deng, Kangle and Liu, Ruixuan and Ramanan, Deva and Liu, Changliu and Zhu, Jun-Yan},
    journal = {arXiv preprint},
    year    = {2025}
}
```

## Acknowledgements

We thank Minchen Li, Ken Goldberg, Nupur Kumari, Ruihan Gao, and Yihao Shi for their discussions and help.  
We also thank Jiaoyang Li, Philip Huang, and Shobhit Aggarwal for developing the bimanual robotic system.
This work is partly supported by the Packard Foundation, Cisco Research Grant, and Amazon Faculty Award. This work is
also in part supported by the Manufacturing Futures Institute, Carnegie Mellon University, through a grant from the
Richard King Mellon Foundation. KD is supported by the Microsoft Research PhD Fellowship.

Our codebase is built upon several amazing repos:  Hugging
Face [TRL](https://huggingface.co/docs/trl/index), [Accelerate](https://huggingface.co/docs/accelerate/index), [ImportLDraw](https://github.com/TobyLobster/ImportLDraw).