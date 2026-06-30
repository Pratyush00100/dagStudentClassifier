from jsonschema import validate, ValidationError

def build_schema(config):
    fields = config.get("fields", [])
    properties = {}
    required = []
    for fdef in fields:
        prop = {}
        ftype = fdef.get("type", "string")
        if ftype == "string":
            prop["type"] = "string"
        elif ftype == "number":
            prop["type"] = "number"
        elif ftype == "string[]":
            prop["type"] = "array"
            prop["items"] = {"type": "string"}
        # add more as needed
        properties[fdef["path"]] = prop
        if fdef.get("required"):
            required.append(fdef["path"])

    schema = {
        "type": "object",
        "properties": properties,
        "required": required
    }
    return schema

def validate_output(ctx):
    schema = build_schema(ctx["config"])
    try:
        validate(instance=ctx["output"], schema=schema)
    except ValidationError as e:
        ctx["errors"].append({"node": "validate", "error": str(e)})
        # decide: raise or continue
    return ctx