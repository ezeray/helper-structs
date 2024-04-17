from functools import wraps
from typing import Any, Callable
from .result import Ok, Err, Result
from .failure import FailureContainer
from ._types import P, T


def safe_exec(
        func: Callable[P, T]
    ) -> Callable[P , Result[T, Any]]:
    """
    This wrapper provides a "safe execution" context for the function
    passed, hence the name. This means that it executes `func` within
    a try-except block, and returns a Result.

    With regards to type hinting, it is structured in such a way that
    the type checker and hinter is able to track what is the return
    type of the `func(P) -> T` that is getting wrapped, and places
    that type within the Result container, so the signature of the
    wrapped function is `wrapped(P) -> Result[T, Any]`.

    For example, if we have

    >>> @safe_exec
    ... def sq(x: int) -> int:
    ...     return x * x
    >>> sq.__annotations__
    {'x': <class 'int'>, 'return': result.Result[int, typing.Any]}
    >>> type(r1)
    <class 'result.Result'>
    >>> r1 = sq(2)
    >>> r1
    Ok(4)
    >>> r1c = r1.unwrap_or(0)
    >>> r1c
    4

    """
    # ) -> _Wrapped[Any, Any, (args: Any, kwrgs: Any), Result[Any, Any]]:

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, Any]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:
            f = FailureContainer(
                func=func.__name__,
                args=args,
                kwargs=kwargs,
                exception=e,
            )
            return Err(
                    e,
                    failure=f.as_dict()
                )

    ret_type = func.__annotations__.get("return")
    if ret_type is None:
        wrapper.__annotations__["return"] = Result[Any, Any]
    else:
        wrapper.__annotations__["return"] = Result[ret_type, Any]
    return wrapper


@safe_exec
def add_one(a):
    return a + 1


@safe_exec
def sq(x: int) -> int:
    return x * x


@safe_exec
def greet(x: str) -> str:
    return f"Hello {x}!"


def main():
    print(add_one(2))
    print(add_one("hello world"))
    an_err = add_one("hello_world")
    print(an_err.is_ok)
    print(an_err._failure)

    # this call is properly annotated
    g = greet("ezequiel")
    g_c = g.unwrap_or("couldn't greet")
    g_c.lower()


if __name__ == "__main__":
    main()

