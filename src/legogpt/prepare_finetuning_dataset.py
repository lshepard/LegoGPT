import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from datasets import load_dataset
from transformers import HfArgumentParser

from legogpt.models import create_instruction


@dataclass
class PrepareDatasetArguments:
    input_path: str = field(
        metadata={'help': 'Path to the directory containing the LEGO dataset to be processed. '
                          'This dataset should contain at least the fields "caption" and "lego".'},
    )
    output_path: str = field(
        metadata={'help': 'Path to the directory in which to save the processed fine-tuning dataset. '
                          'The fine-tuning dataset will contain the field "messages", a conversational exchange where '
                          'the user prompts the assistant with a "caption" and the assistant provides a "lego" '
                          'following that caption.'},
    )


def main():
    """
    This script converts a LEGO dataset into the conversational format required for fine-tuning with TRL SFT.
    """

    parser = HfArgumentParser(PrepareDatasetArguments)
    (cfg,) = parser.parse_args_into_dataclasses()

    input_dataset = load_dataset(cfg.input_path)

    def convert_sample(x: dict[str, Any]) -> dict:
        """
        Converts a sample from the input dataset into the conversational format required for fine-tuning.
        """
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': create_instruction(x['caption'])},
            {'role': 'assistant', 'content': x['lego']},
        ]
        return {'messages': messages}

    os.makedirs(cfg.output_path, exist_ok=True)
    for split_name, split in input_dataset.items():
        output_split = split.map(
            convert_sample,
            remove_columns=split.column_names,
            desc=f'Converting dataset split "{split_name}"',
        )
        output_split.to_json(Path(cfg.output_path) / f'{split_name}.jsonl')


if __name__ == '__main__':
    main()
