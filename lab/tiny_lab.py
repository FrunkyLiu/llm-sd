import inspect
from typing import Callable, Dict

import streamlit as st
from settings.configs.placeholder import Placeholder
from utils.context_key import create_context_key
from utils.session_state_registry import Registry


class LayoutRenderer:
    def __init__(self):
        self._layout = None

    def __call__(self, layout, **kwargs):
        self._layout = layout
        self._layout(**kwargs)

    def _placeholder_wrapper(
        self, st_element: Callable, *args, response_key=None, **kwargs
    ):
        sig = inspect.signature(st_element)
        has_key_param = "key" in sig.parameters
        if "key" not in kwargs:
            args_repr = "|".join(map(str, args))
            kwargs_repr = "|".join(
                f"{k}={v}" for k, v in sorted(kwargs.items())
            )
            key = create_context_key()
            key = key + args_repr + kwargs_repr
            if has_key_param:
                kwargs["key"] = key
        else:
            key = kwargs["key"]

        if response_key:
            Registry.register(response_key, key)

        args, kwargs = Placeholder.update_param_placeholders(*args, **kwargs)

        result = st_element(*args, **kwargs)

        if not has_key_param:
            st.session_state[key] = result
        return result

    def _build_streamlit(self, st_element: Callable, *args, **kwargs):
        result = self._placeholder_wrapper(st_element, *args, **kwargs)
        return result

    def render_page(self, configs: list[Dict]):
        for config in configs:
            if "condition" in config:
                condition = config["condition"]
                if not Placeholder.get_value(condition):
                    continue
            st_element = config["class"]
            args = config.get("args", ())
            kwargs: Dict = config.get("kwargs", {})
            response_key = kwargs.pop("response_key", None)
            self._build_streamlit(
                st_element, *args, response_key=response_key, **kwargs
            )
        st.write(st.session_state)
        return
