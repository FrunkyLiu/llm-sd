from typing import Any, Callable, Dict, List, Union

import streamlit as st
from settings.configs.placeholder import Placeholder, PlaceholderValue


class LayoutRenderer:

    def _placeholder_wrapper(
        self, st_element: Callable, *args, response_key=None, **kwargs
    ):
        args, kwargs = Placeholder.update_param_placeholders(*args, **kwargs)

        result = st_element(*args, **kwargs)

        if response_key:
            response_key.set(result)
        return result

    def _check_condition(
        self, condition: Union[PlaceholderValue, Dict[str, Any]]
    ) -> bool:
        if isinstance(condition, PlaceholderValue):
            return bool(condition.get())

        st_element = condition["class"]
        args = condition.get("args", ())
        kwargs = condition.get("kwargs", {})
        response_key = condition.get("response_key", None)

        return self._build_streamlit(
            st_element, *args, response_key=response_key, **kwargs
        )

    def __is_context_manager(self, obj) -> bool:
        return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")

    def _build_streamlit(self, st_element: Callable, *args, **kwargs):
        result = self._placeholder_wrapper(st_element, *args, **kwargs)
        return result

    def _handle_streamlit_objects(
        self, st_obj: Any, children: List[Dict]
    ) -> None:
        if isinstance(st_obj, (list, tuple)):
            for i, obj in enumerate(st_obj):
                if children[i] is not None:
                    with obj:
                        self.render_layout([children[i]])
        elif self.__is_context_manager(st_obj):
            with st_obj:
                self.render_layout(children)
        else:
            st_obj(self.render_layout)(children)

    def _children_parser(self, config: Dict):
        st_element = config["class"]
        args = config.get("args", ())
        kwargs: Dict = config.get("kwargs", {})
        st_obj = st_element(*args, **kwargs)
        children = config.get("children", [])

        if not st_obj or not children:
            return

        self._handle_streamlit_objects(st_obj, children)

    def render_layout(self, configs: List[Dict[str, Any]]) -> None:
        for config in configs:
            # Check conditions early and continue if not met
            if "condition" in config:
                if not self._check_condition(config["condition"]):
                    continue

            # Handle children configurations
            if "children" in config:
                self._children_parser(config)
                continue

            # Process regular streamlit elements
            st_element = config["class"]
            args = config.get("args", ())
            kwargs = config.get("kwargs", {})
            response_key = config.get("response_key")
            self._build_streamlit(
                st_element, *args, response_key=response_key, **kwargs
            )
        st.write(st.session_state)
        return

    def render_page(self, configs: Dict[str, List[Dict[str, Any]]]) -> None:
        sidebar_configs = configs.get("sidebar", [])
        body_configs = configs.get("body", [])
        if sidebar_configs:
            with st.sidebar:
                self.render_layout(sidebar_configs)
        self.render_layout(body_configs)
        st.write(st.session_state)
        return
