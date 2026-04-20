# Identity-conditioned accumulator

Implements **observed** counts for `(source_id, content_id, outcome_key)` — see [`docs/IDENTITY_CONDITIONED_CONTINUATION.md`](../../docs/IDENTITY_CONDITIONED_CONTINUATION.md).

```python
from threshold_onset.identity_conditioned import IdentityConditionedAccumulator

acc = IdentityConditionedAccumulator()
acc.record("speaker_a", "hash_content_x", "engaged")
acc.record("speaker_b", "hash_content_x", "ignored")
print(acc.outcome_distribution("speaker_a", "hash_content_x"))
print(acc.to_jsonable())
```

**Tests:** `pytest threshold_onset/identity_conditioned/tests/test_accumulator.py`
