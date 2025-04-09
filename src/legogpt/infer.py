import transformers
from transformers import HfArgumentParser

from legogpt.models import LegoGPT, LegoGPTConfig


def main():
    parser = HfArgumentParser(LegoGPTConfig)
    (cfg,) = parser.parse_args_into_dataclasses()
    transformers.set_seed(42)

    legogpt = LegoGPT(cfg)
    while True:
        prompt = input('Enter a prompt, or <Return> to exit: ')
        if not prompt:
            break
        print('Generating...')
        output = legogpt(prompt)

        print(output['lego'])
        print('# of bricks:', len(output['lego']))
        print('Brick rejection reasons:', output['rejection_reasons'])
        print('# regenerations:', output['n_regenerations'])


if __name__ == '__main__':
    main()
