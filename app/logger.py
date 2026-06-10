import json
import os

from app.config import LOG_PATH


def log_interaction(payload: dict) -> None:
    record = dict(payload)
    if 'patient_email' in record:
        record['patient_email'] = '***REDACTED***'

    log_dir = os.path.dirname(LOG_PATH)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')
