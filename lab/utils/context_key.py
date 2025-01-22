import inspect
import os


def create_context_key(*args, **kwargs) -> str:
    # stack = inspect.stack()[2:]
    # frames = []
    # for frame_info in stack:
    #     lineno = frame_info.lineno
    #     file_name = os.path.basename(frame_info.filename)
    #     frames.append(f"{file_name}:{lineno}")

    args_repr = "|".join(map(str, args))
    kwargs_repr = "|".join(
        f"{k}={v}" for k, v in sorted(kwargs.items())
    )
    key = "|".join((args_repr, kwargs_repr))
    return key
