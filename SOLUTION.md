# Solution Steps

1. Update retrieval so it loads the KB, ignores any article whose visibility is not 'public', tokenizes the query and each article title/body case-insensitively, scores matches by simple word overlap, sorts by relevance, and returns only the top MAX_CONTEXT_ARTICLES as a combined context plus their source_id values.

2. Add lightweight token normalization in retrieval to avoid false matches on common filler words; returning None when there is no meaningful overlap ensures the fallback path is reachable for unrelated or staff-only queries.

3. Modify run_agent(query) so it calls build_context(query) first and immediately returns the configured FALLBACK_MESSAGE with an empty source_ids list when retrieval returns None, without calling the LLM.

4. Keep logging in both success and fallback paths, but only build the LLM prompt and call call_llm() when retrieval returns public context.

5. Fix log_interaction() by copying the payload, replacing patient_email with '***REDACTED***' when present, creating the log directory if needed, and writing the redacted JSON line with a context-managed file handle.

6. Complete the missing agent test by using a query that matches only private/staff content, patching app.agent.call_llm and app.agent.log_interaction, then asserting the fallback answer is returned, the LLM is never called, and no private source IDs leak into the logged or returned data.

7. Run the test suite with pytest to confirm retrieval relevance, fallback behavior, and email redaction all work together.

