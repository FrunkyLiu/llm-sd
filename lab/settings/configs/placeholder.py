import logging

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
            st.session_state.setdefault("persist", {})

    def _get_key(self):
        if self._name == "_CURRENT_PAGE":
            return self._name
        current_page = Placeholder._CURRENT_PAGE.get()
        return f"{current_page}_{self._name}"

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, obj, value):
        self.set(value)

    def set(self, value):
        key = self._get_key()
        st.session_state.setdefault("_placeholder_values", {})
        st.session_state["_placeholder_values"][key] = value
        self._value = value

    def __get__(self, obj, objtype=None):
        return self

    def get(self):
        key = self._get_key()
        placeholder_values = st.session_state.get("_placeholder_values", {})
        logging.debug(f"Get Persisting {key} with value {placeholder_values}")
        if key not in placeholder_values:
            return None
        val = placeholder_values.get(key, None)

        if self.persist:
            if "first" not in st.session_state["persist"].get(key, {}):
                st.session_state["persist"][key] = {"first": val}
            elif "last" not in st.session_state["persist"].get(key, {}):
                if st.session_state["persist"][key]["first"] != val:
                    st.session_state["persist"][key].update({"last": val})
            else:
                val = st.session_state["persist"][key]["last"]
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
    GENERATE_RESPONSE = PlaceholderValue()
    QUERY = None
    HISTORY_ANSWER = None
    INSTRUCTIONS = None
    FILLED_PROMPT = None
    ENABLE = None
