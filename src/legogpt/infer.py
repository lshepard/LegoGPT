from transformers import HfArgumentParser

from legogpt.models.legogpt import LegoGPT, LegoGPTConfig


def main():
    parser = HfArgumentParser(LegoGPTConfig)
    cfg, extra_args = parser.parse_args_into_dataclasses(return_remaining_strings=True)

    legogpt = LegoGPT(cfg)
    while True:
        prompt = input('Enter a prompt, or <Return> to exit: ')
        if not prompt:
            break
        print('Generating...')
        output = legogpt(prompt)
        print(output['lego'])


if __name__ == '__main__':
    main()
