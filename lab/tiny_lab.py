from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Union,
)

import streamlit as st
from settings.configs.placeholder import Placeholder, PlaceholderValue


class LayoutRenderer:

    def _placeholder_wrapper(
        self,
        obj: Callable,
        obj_args: Iterable,
        obj_kwargs: Mapping,
        result_key: Optional[PlaceholderValue] = None,
    ):
        obj_args, obj_kwargs = Placeholder.update_param_placeholders(
            obj, obj_args, obj_kwargs, result_key
        )
        result = obj(*obj_args, **obj_kwargs)
        if result_key:
            result_key.set(result)
        return result

    def _check_condition(
        self, condition: Union[PlaceholderValue, Dict[str, Any]]
    ) -> bool:
        if isinstance(condition, PlaceholderValue):
            return bool(condition.get())

        component = condition["component"]
        args = condition.get("args", ())
        kwargs = condition.get("kwargs", {})
        result_key = condition.get("result_key", None)

        return self._build_obj(
            component, args, kwargs, result_key=result_key
        )

    def __is_context_manager(self, obj) -> bool:
        return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")

    def _build_obj(
        self,
        obj: Callable,
        obj_args: Iterable,
        obj_kwargs: Mapping,
        result_key: Optional[PlaceholderValue] = None,
    ):
        result = self._placeholder_wrapper(obj, obj_args, obj_kwargs, result_key)
        return result

    def _handle_objects(
        self, obj: Any, children: List[Dict]
    ) -> None:
        if isinstance(obj, (list, tuple)):
            for i, obj in enumerate(obj):
                if children[i] is not None:
                    with obj:
                        self.render_layout([children[i]])
        elif self.__is_context_manager(obj):
            with obj:
                self.render_layout(children)
        else:
            obj(self.render_layout)(children)

    def _children_parser(self, config: Dict):
        component = config["component"]
        args = config.get("args", ())
        kwargs: Dict = config.get("kwargs", {})
        obj = component(*args, **kwargs)
        children = config.get("children", [])

        if not obj or not children:
            return

        self._handle_objects(obj, children)

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
            component = config["component"]
            args = config.get("args", ())
            kwargs = config.get("kwargs", {})
            result_key = config.get("result_key")
            self._build_obj(
                component, args, kwargs, result_key=result_key
            )
        return

    def render_page(self, configs: Dict[str, List[Dict[str, Any]]]) -> None:
        page_name = configs.get("page_name", "Page")
        sidebar_configs = configs.get("sidebar", [])
        body_configs = configs.get("body", [])
        Placeholder._CURRENT_PAGE.set(page_name)
        if sidebar_configs:
            with st.sidebar:
                self.render_layout(sidebar_configs)
        self.render_layout(body_configs)
        st.write(st.session_state)
        return
