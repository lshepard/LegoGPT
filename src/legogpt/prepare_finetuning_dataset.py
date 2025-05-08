import os
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from pathlib import Path

from datasets import load_dataset
from transformers import HfArgumentParser


@dataclass
class PrepareDatasetArguments:
    input_path: str = field(
        default='AvaLovelace/StableText2Lego',
        metadata={'help': 'Path to the directory containing the LEGO dataset to be processed. '
                          'This dataset should contain at least the fields "captions" (list[string]) and "lego" (string).'},
    )
    output_path: str = field(
        default='datasets',
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

    def convert_sample(batch: MutableMapping) -> dict:
        return {'messages': [create_messages(caption, lego)
                             for lego, captions in zip(batch['lego'], batch['captions'])
                             for caption in captions]}

    def create_messages(caption: str, lego: str) -> list[dict[str, str]]:
        """
        Converts a sample from the input dataset into the conversational format required for fine-tuning.
        """
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': caption},
            {'role': 'assistant', 'content': lego},
        ]
        return messages

    os.makedirs(cfg.output_path, exist_ok=True)
    for split_name, split in input_dataset.items():
        output_split = split.map(
            convert_sample,
            batched=True,
            remove_columns=split.column_names,
            desc=f'Converting dataset split "{split_name}"',
        )
        output_split.to_json(Path(cfg.output_path) / f'{split_name}.jsonl')

    print(f'Converted dataset saved to {os.path.abspath(cfg.output_path)}')


if __name__ == '__main__':
    main()
