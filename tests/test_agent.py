import json
from unittest.mock import patch

from app.agent import run_agent
from app.config import FALLBACK_MESSAGE
from app.logger import log_interaction
from app.retrieval import build_context


# Retrieval tests

def test_relevant_public_articles_only():
    result = build_context('how do I pay my bill')
    assert result is not None, 'Expected at least one matching public article'
    for sid in result['source_ids']:
        assert sid != 'FAQ-STAFF-001', 'Staff article must not appear in context'
    assert 'billing' in result['context'].lower() or 'payment' in result['context'].lower(), (
        'Context should contain billing-related content'
    )


def test_staff_articles_excluded():
    result = build_context('billing override')
    if result is not None:
        assert 'FAQ-STAFF-001' not in result['source_ids'], (
            'Staff article leaked into patient context'
        )


# Agent fallback test

def test_no_match_returns_fallback():
    query = 'hardship exemption override code'

    with patch('app.agent.call_llm') as mock_llm, patch('app.agent.log_interaction') as mock_log:
        result = run_agent(query, patient_email='patient@example.com')

    assert result['answer'] == FALLBACK_MESSAGE
    assert result['source_ids'] == []
    mock_llm.assert_not_called()

    mock_log.assert_called_once()
    logged_payload = mock_log.call_args.args[0]
    assert logged_payload['query'] == query
    assert logged_payload['patient_email'] == 'patient@example.com'
    assert logged_payload['source_ids'] == []
    assert logged_payload['answer'] == FALLBACK_MESSAGE
    assert 'FAQ-STAFF-001' not in json.dumps(logged_payload)


# Privacy / logging test

def test_patient_email_redacted(tmp_path, monkeypatch):
    log_file = tmp_path / 'interactions.jsonl'
    monkeypatch.setattr('app.logger.LOG_PATH', str(log_file))

    log_interaction({
        'query': 'What are your opening hours?',
        'patient_email': 'jane.doe@example.com',
        'source_ids': ['FAQ-002'],
        'answer': 'We are open Monday to Friday.',
    })

    assert log_file.exists(), 'Log file was not created'
    with open(log_file, encoding='utf-8') as f:
        row = json.loads(f.readline())

    assert row['patient_email'] == '***REDACTED***', (
        f"Expected redacted email, got: {row['patient_email']}"
    )
    assert row['query'] == 'What are your opening hours?'
    assert row['answer'] == 'We are open Monday to Friday.'
