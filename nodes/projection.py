import re

def resolve_path(obj, path):
    """
    Resolves a dotted/bracket path against an object.
    Supports:
      - 'emails[0]'            => list index
      - 'skills[].name'        => extract 'name' from each skill object
      - 'links.github'         => dict key
    """
    tokens = re.findall(r'\w+|\[\d+\]|\[\]', path)
    current = obj
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "[]":
            # We expect a following token that is the key to pluck from each item
            if i + 1 < len(tokens):
                next_token = tokens[i + 1]
                if isinstance(current, list):
                    # Map over list, extract next_token from each item
                    new_list = []
                    for item in current:
                        if isinstance(item, dict):
                            val = item.get(next_token)
                            if val is not None:
                                new_list.append(val)
                    current = new_list
                else:
                    current = None
                i += 2  # skip both '[]' and the next token
                continue
            else:
                # '[]' at the end means return the whole list (unlikely but safe)
                break
        elif re.match(r'\[\d+\]', token):
            idx = int(token[1:-1])
            if isinstance(current, list) and idx < len(current):
                current = current[idx]
            else:
                current = None
        else:
            # dict key
            if isinstance(current, dict):
                current = current.get(token)
            else:
                current = None
        if current is None:
            break
        i += 1
    return current

def project(ctx):
    config = ctx["config"]
    canonical = ctx["canonical"]
    output = {}

    fields = config.get("fields", [])
    on_missing = config.get("on_missing", "null")
    include_confidence = config.get("include_confidence", False)

    for field_def in fields:
        path = field_def["path"]
        from_path = field_def.get("from", path)  # if no "from", use path
        raw_value = resolve_path(canonical, from_path)

        # Apply on_missing
        if raw_value is None:
            if on_missing == "null":
                value = None
            elif on_missing == "omit":
                continue
            elif on_missing == "error":
                raise ValueError(f"Missing required field: {path}")
        else:
            value = raw_value

        # Normalize if specified
        norm = field_def.get("normalize")
        if norm == "E164":
            # already normalized, but we could re-ensure
            pass
        elif norm == "canonical" and "skills" in path:
            # skills already canonicalized, but we could map again if needed
            pass

        # Assign to output
        output[path] = value

    # Include confidence if requested
    if include_confidence:
        output["confidence"] = canonical.get("_confidence", {})
        output["overall_confidence"] = canonical.get("overall_confidence", 0)

    ctx["output"] = output
    return ctx