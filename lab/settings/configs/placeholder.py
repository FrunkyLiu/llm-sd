from enum import Enum, auto

from utils.session_state_registry import Registry


class Placeholder(Enum):
    GENERATE_TOP_P = auto()
    GENERATE_TOP_K = auto()
    GENERATE_TEMPERATURE = auto()
    GENERATE_MAX_TOKEN = auto()
    GENERATE_RESPONSE = auto()

    QUERY = auto()

    HISTORY_ANSWER = auto()
    INSTRUCTIONS = auto()
    FILLED_PROMPT = auto()
    ENABLE = auto()

    def __call__(self, *args, **kwargs):
        # val = Registry.get(self)
        return _PlaceholderCall(self, **kwargs)

    @classmethod
    def bind_placeholder(cls, placeholder, value):
        Registry.register(placeholder, value)

    @classmethod
    def update_param_placeholders(cls, *args, **kwargs):
        def _resolve(item):
            # 如果是我們的包裝物件，呼叫它的 get_value() 拿最終結果
            if isinstance(item, _PlaceholderCall):
                return item.get_value()
            # 如果是原本的 Placeholder，直接取
            elif isinstance(item, cls):
                return Registry.get(item)
            else:
                return item

        new_args = [_resolve(arg) for arg in args]
        new_kwargs = {k: _resolve(v) for k, v in kwargs.items()}
        return new_args, new_kwargs

    @classmethod
    def get_value(cls, placeholder):
        return Registry.get(placeholder)


class _PlaceholderCall:
    """
    專門包裝「Placeholder + 額外參數」的物件。
    當最終在 update_param_placeholders 時，
    才會真的呼叫 get_value() 來從 Registry 拿值並做轉換。
    """
    def __init__(self, placeholder, invert=False):
        self.placeholder = placeholder
        self.invert = invert

    def __str__(self):
        return f"PlaceholderCall({self.placeholder})"

    def get_value(self):
        val = Registry.get(self.placeholder)
        # 例如做反轉布林
        if self.invert:
            val = not val
        return val
