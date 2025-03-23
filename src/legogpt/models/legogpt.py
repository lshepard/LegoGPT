import functools
from collections import Counter
from typing import Callable

import torch
from transformers.generation.logits_process import PrefixConstrainedLogitsProcessor, LogitsProcessorList

from legogpt.data.lego_library import max_brick_dimension
from legogpt.data.lego_structure import LegoStructure, LegoBrick
from legogpt.models.llm import LLM


def create_instruction(caption: str) -> str:
    instruction = ('Create a LEGO model of the input. Format your response as a list of bricks: '
                   '<brick dimensions> <brick position>, where the brick position is (x,y,z).\n'
                   'Allowed brick dimensions are 2x4, 4x2, 2x6, 6x2, 1x2, 2x1, 1x4, 4x1, 1x6, 6x1, 1x8, 8x1, 1x1, 2x2.\n'
                   'All bricks are 1 unit tall.\n\n'
                   '### Input:\n'
                   f'{caption}')
    return instruction


class LegoGPT:
    def __init__(
            self,
            *,
            world_dim: int = 20,
            temperature: float = 0.6,
            device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
    ):
        self.world_dim = world_dim
        self.temperature = temperature
        self.device = device

        self.llm = LLM('meta-llama/Llama-3.2-1B-Instruct', self.device)

    def __call__(self, caption: str) -> LegoStructure:
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': create_instruction(caption)},
        ]
        prompt = self.llm.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors='pt')

        lego = LegoStructure([])
        for brick_num in range(100):
            brick, rejection_reasons = self.generate_brick_with_rejection_sampling(
                prompt if brick_num == 0 else None, lego=lego
            )
            if not brick:
                break
            lego.add_brick(LegoBrick.from_txt(brick))

        return lego

    def generate_brick_with_rejection_sampling(
            self,
            prompt: str | None = None,
            lego: LegoStructure = LegoStructure([]),
            max_generations_per_brick: int = 10,
    ) -> (str, Counter):
        """
        Generates a LEGO brick to add to the LEGO structure, using rejection sampling to ensure the brick is valid.
        """
        rejection_reasons = Counter()
        rejected_bricks = set()

        brick = ''
        for generation_num in range(max_generations_per_brick):
            self.llm.save_state()
            brick = self.generate_brick(prompt)
            if not brick:  # Generation is finished
                break

            add_brick_result = self._try_adding_brick(brick, lego, rejected_bricks)
            if add_brick_result == 'success' or generation_num == max_generations_per_brick - 1:
                break

            self.llm.rollback_to_saved_state()
            rejection_reasons.update([add_brick_result])
            rejected_bricks.add(brick)

        return brick, rejection_reasons

    @staticmethod
    def _try_adding_brick(brick_str: str, lego: LegoStructure, rejected_bricks: set[str]) -> str:
        """
        Tries to add the brick, represented by a string, to the given LEGO structure.
        Returns the result: 'success' if the add was successful, and the failure reason otherwise.
        """
        if brick_str in rejected_bricks:
            return 'already_rejected'

        try:
            brick = LegoBrick.from_txt(brick_str)
        except ValueError:  # Brick is badly formatted
            return 'ill_formatted'

        if not lego.brick_in_bounds(brick):
            return 'out_of_bounds'
        if lego.brick_collides(brick):
            return 'collision'
        return 'success'

    def generate_brick(self, prompt: str | None = None) -> str:
        """
        Generates a LEGO brick in txt format, using inference masking to enforce compliance with the LEGO brick syntax.
        WARNING: Assumes each number in the brick dimensions and positions is represented by 1 token.
        :param prompt: The prompt to be given to the LLM preceding brick generation.
        :return: A LEGO brick in txt format, or the empty string if generation is finished.
        """
        allowed_dims = tuple(str(i) for i in range(1, max_brick_dimension + 1))
        allowed_posns = tuple(str(i) for i in range(self.world_dim))

        # Generate tokens one by one to fit the format "hxw (x,y,z)\n"
        result_ids = []
        for allowed_strs in [
            allowed_dims + (self.llm.tokenizer.eos_token,), ('x',), allowed_dims, (' (',), allowed_posns, (',',),
            allowed_posns, (',',), allowed_posns, (')\n',),
        ]:
            next_token_id = self.llm(
                prompt,
                return_as_ids=True,
                max_new_tokens=1,
                temperature=self.temperature,
                logits_processor=self._build_allow_tokens_logits_processor(allowed_strs)
            )[0]
            result_ids.append(next_token_id)

            if next_token_id == self.llm.tokenizer.eos_token_id:  # Generation is finished
                break
            if prompt is not None:
                prompt = None  # Only use prompt on first iteration; continue generation thereafter

        return self.llm.tokenizer.decode(result_ids, skip_special_tokens=True)

    @functools.cache
    def _build_allow_tokens_logits_processor(self, allowed_strs: tuple[str]) -> LogitsProcessorList:
        """
        Builds a logits processor that constrains the next token to be one of the allowed strings.
        """
        return LogitsProcessorList(
            [PrefixConstrainedLogitsProcessor(self._build_allowed_token_ids_fn(allowed_strs), num_beams=1)]
        )

    @functools.cache
    def _build_allowed_token_ids_fn(self, allowed_strs: tuple[str]) -> Callable[[int, torch.Tensor], list[int]]:
        """
        Builds a function that returns a set of allowed token IDs, to be used by PrefixConstrainedLogitsProcessor.
        """
        allowed_tokens = [self.llm.tokenizer.tokenize(s) for s in allowed_strs]
        if not all(len(tokens) == 1 for tokens in allowed_tokens):
            raise ValueError('Each allowed string must tokenize to exactly 1 token')
        allowed_ids = self.llm.tokenizer.convert_tokens_to_ids(tokens[0] for tokens in allowed_tokens)

        def allowed_token_ids_fn(_: int, __: torch.Tensor) -> list[int]:
            return allowed_ids

        return allowed_token_ids_fn
