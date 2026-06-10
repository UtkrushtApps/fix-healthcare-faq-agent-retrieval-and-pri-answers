def call_llm(prompt: str) -> str:
    import re

    match = re.search(r'\[([A-Z0-9-]+)\]', prompt)
    citation = f' (Source: {match.group(1)})' if match else ''
    return f'Based on our clinic information, here is what I found{citation}.'
