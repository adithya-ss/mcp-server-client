from ollama import chat
from ollama import ChatResponse

LLM_MODEL = "llama3.2"
USER_QUESTIONS = [
    "What is life's best motto?",
    "Who do you think has the best chance of becoming the 2026 Formula 1 Driver's World Champion?",
    "Which is the best Generative AI model?",
]

def prompt_response():
    for question in USER_QUESTIONS:
        response: ChatResponse = chat(
            model=LLM_MODEL,
            messages=[
                # system: Expectation from the LLM.
                {"role": "system", "content": "Answers in one sentence only, with less than 20 words."},
                # user: The question to be answered by the LLM.
                {"role": "user", "content": question},
            ],
        )
        print(f"\nQuestion: {question}\n"
              f"Response from {LLM_MODEL}: {response.message.content}\n")
        print(f"Number of tokens evaluated in the prompt: {response.prompt_eval_count}")
        print(f"Total duration: {response.total_duration / 1_000_000_000:.2f} seconds\n"
              f"------")


if __name__ == "__main__":
    prompt_response()
