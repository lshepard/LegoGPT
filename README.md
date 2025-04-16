# LegoGPT

## Installation

### Prerequisites

You need a Gurobi licence to use Gurobi for stability analysis. Get a free academic
licence [here](https://www.gurobi.com/academia/academic-program-and-licenses/).

### Installing as a standalone project

This repo uses the Python project manager uv. To install this repo as a standalone project,
simply [install uv](https://docs.astral.sh/uv/getting-started/installation/). The remaining dependencies will be
downloaded and installed upon invoking `uv run`.

### Installing as a package

You can also install this repo as a package in your own project via

```zsh
uv add "git+ssh://git@github.com/AvaLovelace1/LegoGPT.git"
```

if using uv, or

```zsh
pip install "git+ssh://git@github.com/AvaLovelace1/LegoGPT.git"
```

if using pip.

## Finetuning

```zsh
uv run accelerate config  # Initialize the Accelerate config file
uv run ./finetune.zsh
```

## Running inference

Run inference with a finetuned LegoGPT model using:

```zsh
uv run infer --model_name_or_path MODEL_PATH
```

See `uv run infer -h` for a full list of options.