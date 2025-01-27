import logging

import streamlit as st


class PlaceholderValue:
    def __init__(self, name=None, default=None, invert=False, persist=False):
        self._name = name
        self._default = None
        self.invert = None
        self.persist = None
        self._configure(default=default, invert=invert, persist=persist)

    def __call__(self, default=None, invert=False, persist=False):
        self._configure(default=default, invert=invert, persist=persist)
        return self

    def _configure(self, default=None, invert=False, persist=False):
        self._default = default
        self.invert = invert
        self.persist = persist

    def _get_key(self):
        if self._name == "_CURRENT_PAGE":
            return self._name
        current_page = Placeholder._CURRENT_PAGE.get()
        return f"{current_page}_{self._name}"

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, obj, value):
        self.set(value)

    def __get__(self, obj, objtype=None):
        return self

    def set(self, value, *, has_key_param=False, key=None):
        if key is None:
            key = self._get_key()

        session_state = st.session_state.setdefault("_placeholder_values", {})
        session_state[key] = value
        if not has_key_param:
            st.session_state[key] = value
        self._value = value

    def get(self, *, key=None):
        if key is None:
            key = self._get_key()

        if key in st.session_state:
            val = st.session_state[key]
        elif key in st.session_state.get("_placeholder_values", {}):
            val = st.session_state["_placeholder_values"].get(key, None)
        else:
            val = self._default

        if self.persist:
            if "first" not in st.session_state.setdefault("_persist", {}).get(
                key, {}
            ):
                st.session_state["_persist"][key] = {"first": val}
            elif "last" not in st.session_state["_persist"].get(key, {}):
                if st.session_state["_persist"][key]["first"] != val:
                    st.session_state["_persist"][key].update({"last": val})
            else:
                val = st.session_state["_persist"][key]["last"]
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
    _CURRENT_PAGE = PlaceholderValue()

    @classmethod
    def update_param_placeholders(
        cls, has_key_param, response_key, *args, **kwargs
    ):
        def _resolve(item):
            if isinstance(item, PlaceholderValue):
                return item.get()
            else:
                return item

        new_args = [_resolve(arg) for arg in args]
        new_kwargs = {k: _resolve(v) for k, v in kwargs.items()}
        if has_key_param and response_key:
            new_kwargs["key"] = response_key._get_key()
        return new_args, new_kwargs


class MyPlaceholder(Placeholder):
    GENERATE_TOP_P = PlaceholderValue()
    GENERATE_TOP_K = PlaceholderValue()
    GENERATE_TEMPERATURE = PlaceholderValue()
    GENERATE_MAX_TOKEN = None
    GENERATE_RESPONSE = PlaceholderValue()
    QUERY = PlaceholderValue()
    HISTORY_ANSWER = None
    INSTRUCTIONS = None
    FILLED_PROMPT = None
    ENABLE = PlaceholderValue()
