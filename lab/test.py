import streamlit as st
from settings.configs.placeholder import Placeholder

from tiny_lab import LayoutRenderer


def modify_config(original_config, **updates):
    """Create a copy of slider config with updated parameters"""
    new_config = original_config.copy()
    new_config["kwargs"].update(updates)
    return new_config


def enable_params(params):
    return params
# Elements config

slider_top_p = {
    "class": st.slider,
    "args": (),
    "kwargs": {
        "label": "Top-p",
        "value": 0.50,
        "min_value": 0.01,
        "max_value": 1.0,
        "step": 0.01,
        "format": "%.2f",
        "response_key": Placeholder.GENERATE_TOP_P,
    },
}

slider_top_k = {
    "class": st.slider,
    "args": (),
    "kwargs": {
        "label": "Top-k",
        "value": 50,
        "min_value": 1,
        "max_value": 100,
        "step": 1,
        "response_key": Placeholder.GENERATE_TOP_K,
    },
}

slider_temperature = {
    "class": st.slider,
    "args": (),
    "kwargs": {
        "label": "Temperature",
        "value": 0.50,
        "min_value": 0.01,
        "max_value": 1.0,
        "step": 0.01,
        "format": "%.2f",
        "response_key": Placeholder.GENERATE_TEMPERATURE,
    },
}

slider_max_token = {
    "class": st.slider,
    "args": (),
    "kwargs": {
        "label": "Max token",
        "value": 1000,
        "min_value": 1,
        "max_value": 8000,
        "step": 1,
        "response_key": Placeholder.GENERATE_MAX_TOKEN,
    },
}

generate_param_layout_config = [
    slider_top_p,
    slider_top_k,
    slider_temperature,
    slider_max_token,
    {
        "class": st.button,
        "args": (),
        "kwargs": {
            "label": "Generate",
            "type": "primary",
            "response_key": Placeholder.GENERATE_RESPONSE,
        },
    },
    {
        "condition": Placeholder.GENERATE_RESPONSE,
        "class": enable_params,
        "args": (Placeholder.GENERATE_RESPONSE,),
        "kwargs": {"response_key": Placeholder.HISTORY_ANSWER},
    },
    {
        "condition": Placeholder.HISTORY_ANSWER,
        "class": st.text_area,
        "args": (),
        "kwargs": {
            "label": "Query",
        },
    }
]

LayoutRenderer().render_page(generate_param_layout_config)
def is_context_manager(obj) -> bool:
    return hasattr(obj, '__enter__') and hasattr(obj, '__exit__')

obj = st.container()  # 或其他可能是/不是 Context Manager 的物件

if is_context_manager(obj):
    with obj:
        st.write("obj 可以用 with！")
else:
    st.write("obj 不支援 with！")

dd = st.dialog('test')
def A():
    st.write('A')
dd(A)