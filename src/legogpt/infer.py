import sys

from legogpt.models.legogpt import LegoGPT


def main(prompt: str):
    legogpt = LegoGPT()
    output_txt = legogpt(prompt)
    print(output_txt)


if __name__ == '__main__':
    main(sys.argv[1])
