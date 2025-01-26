import streamlit as st


class PlaceholderValue:
    def __init__(self, name=None, default=None, invert=False, persist=False):
        self._name = name
        self._value = None
        self._configure(default=default, invert=invert, persist=persist)

    def __call__(self, default=None, invert=False, persist=False):
        self._configure(default=default, invert=invert, persist=persist)
        return self

    def _configure(self, default=None, invert=False, persist=False):
        self.invert = invert
        self.persist = persist
        if default is not None:
            self.set(default)
            self._value = default

        if persist:
            if "persist" not in st.session_state:
                st.session_state["persist"] = {self._name: {}}
            elif self._name not in st.session_state["persist"]:
                st.session_state["persist"][self._name] = {}

    def __set_name__(self, owner, name):
        print(f"[PlaceholderValue] __set_name__ called: {owner}, {name}")
        self._name = name

    def __set__(self, obj, value):
        self.set(value)

    def set(self, value):
        st.session_state.setdefault("_placeholder_values", {})
        st.session_state["_placeholder_values"][self._name] = value
        self._value = value

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.get()

    def get(self):
        placeholder_values = st.session_state.get("_placeholder_values", {})
        if self._name not in placeholder_values:
            return None
        val = placeholder_values.get(self._name, None)
        if self.persist:
            if "first" not in st.session_state["persist"].get(self._name, {}):
                st.session_state["persist"][self._name] = {"first": val}
            elif "last" not in st.session_state["persist"].get(self._name, {}):
                if st.session_state["persist"][self._name]["first"] != val:
                    st.session_state["persist"][self._name].update(
                        {"last": val}
                    )
            else:
                val = st.session_state["persist"][self._name]["last"]
        if self.invert:
            val = not bool(val)
        self._value = val
        return val

    def __repr__(self):
        return f"<PlaceholderValue name={self._name}, value={self._value}>"


class PlaceholderMeta(type):
    def __new__(mcs, name, bases, attrs):
        new_attrs = {}
        for k, v in attrs.items():
            if k.startswith("__") and k.endswith("__"):
                new_attrs[k] = v
                continue

            if not (hasattr(v, "__get__") or hasattr(v, "__set__")):
                new_attrs[k] = PlaceholderValue(default=v)
            else:
                new_attrs[k] = v

        cls = super().__new__(mcs, name, bases, new_attrs)
        return cls

    def __setattr__(cls, name, value):
        if hasattr(cls, name):
            current_attr = getattr(cls, name)
            if isinstance(current_attr, PlaceholderValue):
                current_attr.set(value)
                return
        descriptor = PlaceholderValue(name=name, default=value)
        super(PlaceholderMeta, cls).__setattr__(name, descriptor)


class Placeholder(metaclass=PlaceholderMeta):

    @classmethod
    def update_param_placeholders(cls, *args, **kwargs):
        def _resolve(item):
            if isinstance(item, PlaceholderValue):
                return item.get()
            else:
                return item

        new_args = [_resolve(arg) for arg in args]
        new_kwargs = {k: _resolve(v) for k, v in kwargs.items()}
        return new_args, new_kwargs


class MyPlaceholder(Placeholder):
    GENERATE_TOP_P = PlaceholderValue()
    GENERATE_TOP_K = PlaceholderValue()
    GENERATE_TEMPERATURE = PlaceholderValue()
    GENERATE_MAX_TOKEN = None
    GENERATE_RESPONSE = None
    QUERY = None
    HISTORY_ANSWER = None
    INSTRUCTIONS = None
    FILLED_PROMPT = None
    ENABLE = None
