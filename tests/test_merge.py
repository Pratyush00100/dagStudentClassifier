def test_merge_scalar_priority():
    cands = [
        {"source": "github", "full_name": "John", "emails": []},
        {"source": "ats", "full_name": "Jonathan", "emails": []}
    ]
    # merge should pick ats (higher priority)
    ...