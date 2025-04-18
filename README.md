# LegoGPT

## Installation

### Prerequisites

You need a Gurobi licence to use Gurobi for stability analysis. Get a free academic
licence [here](https://www.gurobi.com/academia/academic-program-and-licenses/).

### Installing as a standalone project

This repo uses the Python project manager uv. To install this repo as a standalone project,
simply clone the repo:

```zsh
git clone "git@github.com:AvaLovelace1/LegoGPT.git"
```

Then [install uv](https://docs.astral.sh/uv/getting-started/installation/). A virtual environment will be created, and
the remaining dependencies installed automatically, upon invoking `uv run [SCRIPT_NAME]`.

### Installing as a package

To install this repo as a package in your own Python project, run

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