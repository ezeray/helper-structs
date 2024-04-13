from typing import Any, Generic, TypeVar, Callable
import traceback

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class MyResult(Generic[T, E]):
    def __init__(
            self,
            _val: T,
            _err: E,
            _is_ok: bool,
            _build: bool = False,
            _failure: dict[str, Any] = {}
    ) -> None:
        if not _build:
            print("NO")
        self._val = _val
        self._err = _err
        self._is_ok = _is_ok
        self._type = type(_val)
        self._failure = _failure

    @classmethod
    def Ok(cls, _val: T) -> "MyResult[T, E]":
        return cls(_val, None, True, True)

    @classmethod
    def Err(cls, _err: E, _failure: dict[str, Any] = {}) -> "MyResult[T, E]":
        return cls(None, _err, False, True, _failure=_failure)

    def bind(
            self,
            func: Callable[[T], U],
            *args: Any,
            **kwargs: Any,
    ) -> "MyResult[T, E] | MyResult[U, E]":
        if not self._is_ok:
            return self
        try:
            res = func(self._val, *args, **kwargs)
            return self.Ok(res)
        except Exception as e:
            _failure = {
                "trace": traceback.format_exc(),
                "value": self._val,
                "exception": e,
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
            return self.Err(e, _failure)



# def dummy_func(flag: bool) -> MyResult[float, ZeroDivisionError]:
#     den = 0 if flag else 1
    
#     res = MyResult.Ok(2)

#     try:
#         res = res.
