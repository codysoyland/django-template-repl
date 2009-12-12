def pdb_with_context(context):
    vars = []
    for context_dict in context.dicts:
        for k, v in context_dict.items():
            vars.append(k)
            locals()[k] = v
    try:
        import ipdb as pdb
    except ImportError:
        import pdb
    pdb.set_trace()
