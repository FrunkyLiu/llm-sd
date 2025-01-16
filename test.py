import streamlit as st
from settings.configs.placeholder import Placeholder

def modify_config(original_config, **updates):
    """Create a copy of slider config with updated parameters"""
    new_config = original_config.copy()
    new_config['kwargs'].update(updates)
    return new_config

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
    }
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
    }
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
    }
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
    }
}

text_area_query = {
    "class": st.text_area,
    "args": (),
    "kwargs": {
        "label": "輸入要潤飾的問題",
        "value": "請問我要如何請特休？",
        "height": 300,
        "response_key": Placeholder.QUERY,
    }
}

text_area_answer = {
    "class": st.text_area,
    "args": (),
    "kwargs": {
        "label": "請輸入要潤飾的答案",
        "value": """報告文章：AI技術應用與企業轉型挑戰...""",
        "height": 300,
        "response_key": Placeholder.HISTORY_ANSWER,
    }
}

text_area_instructions = {
    "class": st.text_area,
    "args": (),
    "kwargs": {
        "label": "請輸入要潤飾的指示",
        "value": "請綜合問題和潤飾回覆的答案做統整，並生成出三個延伸問題。",
        "height": 300,
        "response_key": Placeholder.INSTRUCTIONS,
    }
}

text_area_response = {
    "class": st.text_area,
    "args": (),
    "kwargs": {
        "label": "回應",
        "value": Placeholder.GENERATE_RESPONSE,
        "height": 300,
    }
}

multiselect_template_order = {
    "class": st.multiselect,
    "args": (),
    "kwargs": {
        "label": "請按照順序選擇模板",
    }
}

text_area_total_prompt = {
    "class": st.text_area,
    "args": (),
    "kwargs": {
        "label": "完整 Prompt",
        "height": 300,
    }
}

button_call_llm = {
    "class": st.button,
    "args": (),
    "kwargs": {
        "label": "生成回覆",
        "type": "primary",
        "response_key": Placeholder.GENERATE_BUTTON,
    }
}

button_confirm_for_param_logic = {
    "class": st.button,
    "args": (),
    "kwargs": {
        "label": "確認調整參數",
        "type": "primary",
        "response_key": Placeholder.CONFIRM_FOR_PARAM_LOGIC,
    }
}

warning_text = {
    "class": st.warning,
    "args": ("⚠️調整模型生成參數會影響 prompt 的實驗信度，造成前後生成結果不一致。請問您是否還執意要調整參數？",),
    "kwargs": {},
}

button_confirm_param_logic = {
    "class": st.button,
    "args": (),
    "kwargs": {
        "label": "確認調整參數",
        "type": "primary",
        "response_key": Placeholder.CONFIRM_PARAM_LOGIC,
    }
}

generate_logic = {
    "condition": Placeholder.GENERATE_BUTTON,
    "class": "generate_logic",
    "args": (),
    "kwargs": {
        "top_p": Placeholder.GENERATE_TOP_P,
        "top_k": Placeholder.GENERATE_TOP_K,
        "temperature": Placeholder.GENERATE_TEMPERATURE,
        "max_token": Placeholder.GENERATE_MAX_TOKEN,
        "query": Placeholder.QUERY,
        "instructions": Placeholder.INSTRUCTIONS,
        "response_key": Placeholder.GENERATE_RESPONSE,
    }
}


# Layout config
generate_param_layout_config = [
    modify_config(slider_top_p, disabled=Placeholder.CONFIRM_PARAM_LOGIC),
    modify_config(slider_top_k, disabled=Placeholder.CONFIRM_PARAM_LOGIC),
    modify_config(slider_temperature, disabled=Placeholder.CONFIRM_PARAM_LOGIC),
    modify_config(slider_max_token, disabled=Placeholder.CONFIRM_PARAM_LOGIC),
]

generate_system_prompt_layout_config = [
    button_confirm_for_param_logic,
    {
        "condition": Placeholder.CONFIRM_FOR_PARAM_LOGIC,
        "class": st.dialog,
        "args": ("調整參數"),
        "kwargs": {},
        "children": [
            warning_text,
            button_confirm_param_logic,
        ]

    }
]

system_prompt_placeholder_layout = [
    {
        "class": st.columns,
        "args": (2),
        "kwargs": {},
        "children": [
            text_area_query,
            text_area_unkonw,
        ]
    },
    text_area_instructions,
]

# Page config

prompt_lab_config = {
    "session_name": "prompt_lab",
    "main": [
        {
            "class": st.sidebar,
            "args": (),
            "kwargs": {},
            "children": [
                *generate_system_prompt_layout_config,
                *generate_param_layout_config
            ]
        },
        {
            "class": st.title,
            "args": ("Prompt Lab",),
            "kwargs": {},
        },
        {
            "class": st.markdown,
            "args": ("用來測試大語言模型的回覆能力",),
            "kwargs": {},
        },
        *system_prompt_placeholder_layout,
    ],
}
st.container