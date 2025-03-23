import sys

from legogpt.models.legogpt import LegoGPT


def main(prompt: str):
    legogpt = LegoGPT()
    lego = legogpt(prompt)
    print(lego)


if __name__ == '__main__':
    main(sys.argv[1])
