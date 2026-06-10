from app.retrieval import build_context
from app.llm import call_llm
from app.logger import log_interaction
from app.prompts import SYSTEM_PROMPT
from app.config import FALLBACK_MESSAGE


def run_agent(query: str, patient_email: str = '') -> dict:
    retrieval = build_context(query)

    if retrieval is None:
        answer = FALLBACK_MESSAGE
        source_ids: list[str] = []

        log_interaction({
            'query': query,
            'patient_email': patient_email,
            'source_ids': source_ids,
            'answer': answer,
        })

        return {'answer': answer, 'source_ids': source_ids}

    context_text = retrieval['context']
    source_ids = retrieval['source_ids']

    prompt = (
        f'{SYSTEM_PROMPT}\n\n'
        f'Context:\n{context_text}\n\n'
        f'Patient question: {query}\n'
        'Answer:'
    )

    answer = call_llm(prompt)

    log_interaction({
        'query': query,
        'patient_email': patient_email,
        'source_ids': source_ids,
        'answer': answer,
    })

    return {'answer': answer, 'source_ids': source_ids}
