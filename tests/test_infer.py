from legogpt.data import LegoStructure
from legogpt.models import LLM, LegoGPT, LegoGPTConfig, create_instruction

LEGOGPT_PATH = '/data/apun/finetuned_hf/Llama-3.2-1B-Instruct_finetuned_ShapeNet_hf_captionV3/checkpoint-40000'


def test_llm():
    """
    Tests the LLM model by generating two different continuations from a prompt.
    """
    llm = LLM('meta-llama/Llama-3.2-1B-Instruct')
    prompt = 'A fun fact about llamas is:'
    output = llm(prompt, max_new_tokens=10)

    # First continuation
    llm.save_state()
    output_continuation = llm(max_new_tokens=10)
    print(prompt + '|' + output + '|' + output_continuation)

    # Second continuation
    llm.rollback_to_saved_state()
    output_continuation = llm(max_new_tokens=10)
    print(prompt + '|' + output + '|' + output_continuation)


def test_finetuned_llm():
    """
    Tests running the finetuned LegoGPT model with no other guidance (e.g. rejection sampling).
    """
    llm = LLM(LEGOGPT_PATH)
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': create_instruction('A basic chair with four legs.')},
    ]
    prompt = llm.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors='pt')

    prompt_txt = llm.tokenizer.decode(prompt[0])
    print(prompt_txt)
    output = llm(prompt, max_new_tokens=8192)
    print(output)


def test_infer():
    """
    Runs LegoGPT inference on a simple prompt.
    """
    legogpt = LegoGPT(LegoGPTConfig(LEGOGPT_PATH))
    output = legogpt('A basic chair with four legs.')

    print(output['lego'])
    print('# of bricks:', len(output['lego']))
    print('Brick rejection reasons:', output['rejection_reasons'])
    print('# regenerations:', output['n_regenerations'])


def test_finish_partial_structure():
    partial_structure_txt = '1x1 (2,19,0)\n1x4 (2,15,0)\n1x8 (2,7,0)\n1x1 (1,6,0)\n2x2 (0,18,0)\n2x1 (0,17,0)\n2x6 (0,11,0)\n'
    partial_lego = LegoStructure.from_txt(partial_structure_txt)
    legogpt = LegoGPT(LegoGPTConfig(LEGOGPT_PATH, max_bricks=1, max_regenerations=0))
    lego, rejections = legogpt._generate_structure(
        'An elongated, rectangular vessel with layered construction, central recess, and uniform edges.', partial_lego)

    print(lego)
    print('# of bricks:', len(lego))
    print('Brick rejection reasons:', rejections)
