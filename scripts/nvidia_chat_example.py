import os
from openai import OpenAI


def main() -> None:
    client = OpenAI(
        base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        api_key=os.environ["NVIDIA_API_KEY"],
    )

    completion = client.chat.completions.create(
        model=os.getenv("NVIDIA_MODEL", "openai/gpt-oss-20b"),
        messages=[{"role": "user", "content": os.getenv("PROMPT", "Hello from Forge")}],
        temperature=1,
        top_p=1,
        max_tokens=4096,
        stream=True,
    )

    for chunk in completion:
        if not getattr(chunk, "choices", None):
            continue
        reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
        if reasoning:
            print(reasoning, end="")
        content = chunk.choices[0].delta.content
        if content is not None:
            print(content, end="")


if __name__ == "__main__":
    main()
