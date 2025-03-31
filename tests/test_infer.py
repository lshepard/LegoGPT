from legogpt.models.legogpt import LegoGPT, create_instruction
from legogpt.models.llm import LLM


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
    llm = LLM('/data/apun/finetuned_hf/Llama-3.2-1B-Instruct_finetuned_combined_2')
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': create_instruction('A basic chair with four legs.')},
    ]
    prompt = llm.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors='pt')
    output = llm(prompt, max_new_tokens=8192)
    print(output)


def test_infer():
    """
    Runs LegoGPT inference on a simple prompt.
    """
    legogpt = LegoGPT()
    output = legogpt('A basic chair with four legs.')

    print(output['lego'])
    print('# of bricks:', len(output['lego']))
    print('Brick rejection reasons:', output['rejection_reasons'])
    print('# regenerations:', output['n_regenerations'])
