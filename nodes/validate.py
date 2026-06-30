from jsonschema import validate, ValidationError

def build_schema(config):
    fields = config.get("fields", [])
    properties = {}
    required = []
    for fdef in fields:
        prop = {}
        ftype = fdef.get("type", "string")
        is_required = fdef.get("required", False)

        # Allow null for optional fields
        if not is_required:
            prop["type"] = [ftype, "null"]
        else:
            prop["type"] = ftype

        # Handle arrays / objects properly
        if ftype == "string[]":
            prop["type"] = "array" if is_required else ["array", "null"]
            prop["items"] = {"type": "string"}
        elif ftype == "object":
            prop["type"] = "object" if is_required else ["object", "null"]
        elif ftype == "object[]":
            prop["type"] = "array" if is_required else ["array", "null"]
            prop["items"] = {"type": "object"}
        elif ftype == "number":
            pass  # already set type above

        properties[fdef["path"]] = prop
        if is_required:
            required.append(fdef["path"])

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }
def validate_output(ctx):
    schema = build_schema(ctx["config"])
    try:
        validate(instance=ctx["output"], schema=schema)
    except ValidationError as e:
        ctx["errors"].append({"node": "validate", "error": str(e)})
        # decide: raise or continue
    return ctx