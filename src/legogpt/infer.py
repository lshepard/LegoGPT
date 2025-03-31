import sys

from legogpt.models.legogpt import LegoGPT


def main(prompt: str):
    legogpt = LegoGPT()
    output = legogpt(prompt)
    print(output['lego'])


if __name__ == '__main__':
    main(sys.argv[1])
