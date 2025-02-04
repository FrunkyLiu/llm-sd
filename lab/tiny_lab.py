from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
)

import streamlit as st
from layout_schema import LayoutConfig, PageConfig
from placeholder import Placeholder, PlaceholderValue


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

    def _build_component(
        self,
        component: Callable,
        args: Iterable,
        kwargs: Mapping,
        result_key: Optional[PlaceholderValue] = None,
    ):
        result = self._placeholder_wrapper(component, args, kwargs, result_key)
        return result

    def __is_context_manager(self, obj) -> bool:
        return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")

    def _handle_objects(self, obj: Any, children: List[LayoutConfig]) -> None:
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

    def _children_parser(self, config: LayoutConfig):
        component = config.component
        args = config.args
        kwargs = config.kwargs
        children = config.children

        obj = component(*args, **kwargs)

        if not obj or not children:
            return

        self._handle_objects(obj, children)

    def _check_condition(
        self, condition: Union[PlaceholderValue, LayoutConfig, None]
    ) -> bool:
        if condition is None:
            return True

        if isinstance(condition, PlaceholderValue):
            return bool(condition.get())

        component = condition.component
        args = condition.args
        kwargs = condition.kwargs
        result_key = condition.result_key

        return self._build_component(
            component, args, kwargs, result_key=result_key
        )

    def render_layout(self, configs: Sequence[LayoutConfig | None]) -> None:
        for config in configs:
            if config is None:
                continue

            # Check conditions early and continue if not met
            if not self._check_condition(config.condition):
                continue

            # Handle children configurations
            if config.children:
                self._children_parser(config)
                continue

            # Process regular streamlit elements
            self._build_component(
                config.component,
                config.args,
                config.kwargs,
                result_key=config.result_key,
            )
        return

    def render_page(self, configs: PageConfig) -> None:
        page_title = configs.title
        sidebar_configs = configs.sidebar
        body_configs = configs.body
        Placeholder._CURRENT_PAGE.set(page_title)
        if sidebar_configs:
            with st.sidebar:
                self.render_layout(sidebar_configs)
        self.render_layout(body_configs)
        st.write(st.session_state)
        return
