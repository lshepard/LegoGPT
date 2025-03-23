from legogpt.models.legogpt import LegoGPT
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


def test_infer():
    """
    Runs LegoGPT inference on a simple prompt.
    """
    legogpt = LegoGPT()
    lego, rejection_reasons = legogpt('A basic chair with four legs.', return_rejection_reasons=True)
    print(lego)
    print(rejection_reasons)
