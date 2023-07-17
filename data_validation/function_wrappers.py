from typing import Any, Callable


class FunctionWrapper:
    """
    Enclosing class for calling a specified functions at a later stage with specified *args and **kwargs

    class for validation of arguments Dataclass Args:\n
       Args:
        func (function): callback function which will either run successfully \
            or raise a Value Error
        *args: any additional positional arguments
        **kwargs: any additional keyword arguments

       Note:
        Any Arguments Stored can be of type Function_Mapper as well and will be invoked at \
        Invocation of Master Function Mapper

       Returns:
        any value passed from the wrapped function
    """

    value_kw: str
    args: list
    kwargs: dict

    def __init__(self, func: Callable, *args, **kwargs) -> None:
        self.func = func
        self.init_args = args
        self.args = ()
        self.kwargs = kwargs

    def __call__(self) -> Any:
        """
        invokes the enclosed functions with *args and **kwargs, \n
        resolves any Callables of each kind of Argument
        """
        self.kwargs = {
            k: self._resolve_ref_by_function(v) for k, v in self.kwargs.items()
        }
        self.args = [self._resolve_ref_by_function(item) for item in self.args]
        return_value = self.func(*self.args, **self.kwargs)
        self.args = ()
        return return_value

    def _resolve_ref_by_function(self, item):
        """
        checks if passed item is of self class and if so calls it's invoke Method
        """
        if not isinstance(item, self.__class__.__base__):
            return item
        return item()


class ArgFunctionWrapper(FunctionWrapper):
    """
    Child Class of Function_Mapper which calls the enclosing function with an argument passed to it

    class for validation of arguments Dataclass Args:\n
       Args:
        func (function): callback function which will either run successfully \
            or raise a Value Error
        value_kw (str): Optional keyword of the value in the enclosing function
        *args: any additional positional arguments
        **kwargs: any additional keyword arguments
    
       Note:
        Any Arguments Stored can be of type Function_Mapper as well and will be invoked at \
        Invocation of Master Function Mapper

       Returns:
        any value passed from the wrapped function
    """

    def __init__(
        self, func: Callable[..., Any], value_kw: str = None, *args, **kwargs
    ) -> None:
        self.value_kw = value_kw
        super().__init__(func, *args, **kwargs)

    def __call__(self, value) -> Any:
        """invokes the enclosing function with the value provided at runtime, \n
        the value is incorporated into *arg or **kwargs before the\n
        super-implementation is called"""
        if self.value_kw is None:
            self.args = (value,) + tuple(self.init_args)
        else:
            self.kwargs[self.value_kw] = value
        return super().__call__()
