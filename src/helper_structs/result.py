import traceback
from typing import Any, Generic, Callable
from ._types import T, E, U, F


class Result(Generic[T, E]):
    """
    This is an adapted version of the Rust Resulst enum, which has the
    signature Result<T, E>, with some added sugar of my personal
    liking, in particular the bing/map part with the rshift dunder
    method.

    This class should not be instantiated directly, instead the user
    should use the class method Result.Ok() for a success value or the
    Result.Err() for a failure value. This serves to handle errors in
    programs without causing a panic at any potential issue.
    """

    __slots__ = ("_val", "_is_ok", "_type", "_failure")
    def __init__(
            self,
            _val: T | E,
            _is_ok: bool,
            _build: bool = False,
            _failure: dict[str, Any] = {}
        ) -> None:
        if not _build:
            raise TypeError(
                "This class can't be initialized directly; please use one of "
                "the constructor methods Result.Ok() or Result.Err()."
            )
        self._val = _val
        self._is_ok = _is_ok
        self._type = type(_val)
        self._failure = _failure


    @classmethod
    def Ok(cls, val: T) -> "Result[T, E]":
        return cls(val, True, _build=True)

    @classmethod
    def Err(cls, err: E, failure: dict[str, Any])-> "Result[T, E]":
        return cls(err, False, _build=True, _failure=failure)

    @property
    def is_ok(self) -> bool:
        return self._is_ok

    @property
    def is_err(self) -> bool:
        return not self._is_ok

    def __repr__(self) -> str:
        return f"Ok({self._val!r})" if self._is_ok else f"Err({self._val!r})"
        # return (
        #     f"Result(\n{self._val=},\n{self._type=},"
        #     f"\n{self._is_ok=},\n{self._failure=})"
        # )

    def __bool__(self) -> bool:
        return self._is_ok
    
    def unwrap(self) -> T:
        if self._is_ok:
            return self._val # type: ignore
        raise ValueError(f"Contents of Result is Err: {self._val}")

    def unwrap_or(self, default: T) -> T:
        return self._val if self._is_ok else default # type: ignore

    def unwrap_or_else(self, op: Callable[[E], U]) -> T | U:
        return self._val if self._is_ok else op(self._val) # type: ignore

    def expect(self, msg: object) -> T:
        if self._is_ok:
            return self._val # type: ignore
        raise ValueError(msg)

    def unwrap_err(self) -> E:
        if not self._is_ok:
            return self._val # type: ignore
        raise ValueError(f"Contents of Result is OK: {self._val}")

    def expect_err(self, msg: object) -> E:
        if not self._is_ok:
            return self._val # type: ignore
        raise ValueError(msg)

    def map(
            self,
            func: Callable[[T], U],
            *args: Any,
            **kwargs: Any,
        ) -> "Result[U, E] | Result[T, E]":
        if not self._is_ok:
            return self
        try:
            # the value passed to the func here will ALWAYS be T, never E
            my_val = func(self._val, *args, **kwargs) # type: ignore
            return self.Ok(my_val)
        except Exception as e:
            # this branch will only ever be reached if the func call results
            # in an error
            failure = {
                "trace": traceback.format_exc(),
                "_val": self._val,
                "exception": e,
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
            return self.Err(e, failure=failure) # type: ignore

    def __rshift__(
            self,
            func: Callable[[T], U],
            *args: Any,
            **kwargs: Any,
        ) -> "Result[U, E] | Result[T, E]":
        return self.map(func, *args, **kwargs)

    def map_err(
            self,
            func: Callable[[E], F],
            *args: Any,
            **kwargs: Any
        ) -> "Result[T, E] | Result[T, F]":
        if self._is_ok:
            return self
        try:
            my_val = func(self._val, *args, **kwargs) # type: ignore
            return self.Err(my_val, failure=self._failure)
        except Exception as e:
            failure = {
                "trace": traceback.format_exc(),
                "_val": self._val,
                "exception": e,
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs,
            }
            return self.Err(e, failure=failure) # type: ignore

