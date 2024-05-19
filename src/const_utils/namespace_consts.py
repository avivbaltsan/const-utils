from utils import is_const


def access_consts(local=False):
    if local:
        # Replace afterward with the inspect module_name
        namespace = locals()
    else:
        namespace = globals()

    return {name: value for name, value in namespace.items()}



