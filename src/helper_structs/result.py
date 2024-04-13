import traceback
from typing import Any, Generic, Callable
from helper_structs._types import T, E, U, F


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

    >>> Result.Ok(10)
    Ok(10)
    >>> Result.Err("failure!")
    Err('failure!')
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
        """
        Returns a Result Ok container for a success value.

        >>> r = Result.Ok(10)
        >>> r
        Ok(10)
        >>> r.is_ok
        True
        """
        return cls(val, True, _build=True)

    @classmethod
    def Err(cls, err: E, failure: dict[str, Any] = {})-> "Result[T, E]":
        """
        Returns a Result Err container for a failure value, with added
        data related to the failure in the form of a dictionary as an
        optional value; default is an empty dict.

        >>> e = Result.Err("an error occurred!")
        >>> e
        Err('an error occurred!')
        >>> e._failure
        {}
        >>> e = Result.Err("failure!", failure={"err": "Error"})
        >>> e
        Err('failure!')
        >>> e._failure
        {'err': 'Error'}
        """
        return cls(err, False, _build=True, _failure=failure)

    @property
    def is_ok(self) -> bool:
        """
        Method returns True if the Result is of the Ok variant

        >>> r = Result.Ok(10)
        >>> r.is_ok
        True
        >>> e = Result.Err("fail")
        >>> e.is_ok
        False

        """
        return self._is_ok

    @property
    def is_err(self) -> bool:
        """
        Method returns True if the Result is of the Err variant

        >>> r = Result.Ok(10)
        >>> r.is_err
        False
        >>> e = Result.Err("fail")
        >>> e.is_err
        True

        """
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
        """
        Extracts the contained value of an Ok variant, or panics with a
        generic message if an Err variant.

        Following the Rust docs, since this panics the use of it is 
        discouraged; instead better to use pattern matching and handle
        the error case explicitly, or calling another method.

        >>> r = Result.Ok(10)
        >>> r.unwrap()
        10
        >>> e = Result.Err("fail")
        >>> e.unwrap()
        Traceback (most recent call last):
            ...
        ValueError: Contents of Result is Err: fail
        """
        if self._is_ok:
            return self._val # type: ignore
        raise ValueError(f"Contents of Result is Err: {self._val}")

    def unwrap_or(self, default: T) -> T:
        """
        Extracts the contained value of an Ok variant, or returns a
        default value passed if an Err variant

        >>> r = Result.Ok(10)
        >>> r.unwrap_or(2)
        10
        
        >>> e = Result.Err("fail")
        >>> e.unwrap_or(2)
        2
        """
        return self._val if self._is_ok else default # type: ignore

    def unwrap_or_else(self, op: Callable[[E], U]) -> T | U:
        """
        Extracts the contained value of an Ok variant, or computes it
        from a callable passed, can be a function or a lambda.

        >>> r = Result.Ok(10)
        >>> r.unwrap_or_else(print)
        10

        >>> e = Result.Err("fail")
        >>> e.unwrap_or_else(lambda x: len(x))
        4
        """
        return self._val if self._is_ok else op(self._val) # type: ignore

    def expect(self, msg: object) -> T:
        """
        Extracts the contained value of an Ok variant, or panics with
        a custom message if an Err variant.

        Following the Rust docs, since this panics the use of it is 
        discouraged; instead better to use pattern matching and handle
        the error case explicitly, or calling another method.

        >>> r = Result.Ok(10)
        >>> r.expect("Something failed")
        10

        >>> e = Result.Err("fail")
        >>> e.expect("Something failed")
        Traceback (most recent call last):
            ...
        ValueError: Something failed
        """
        if self._is_ok:
            return self._val # type: ignore
        raise ValueError(msg)

    def unwrap_err(self) -> E:
        """
        Extract the contained value if an Err variant, or panics with
        a generic message if an Ok variant.

        Following the Rust docs, since this panics the use of it is 
        discouraged; instead better to use pattern matching and handle
        the error case explicitly, or calling another method.

        >>> r = Result.Ok(10)
        >>> r.unwrap_err()
        Traceback (most recent call last):
            ...
        ValueError: Contents of Result is Ok: 10

        >>> e = Result.Err("fail")
        >>> e.unwrap_err()
        'fail'
        """
        if not self._is_ok:
            return self._val # type: ignore
        raise ValueError(f"Contents of Result is Ok: {self._val}")

    def expect_err(self, msg: object) -> E:
        """
        Extract the contained value if an Err variant, or panics with
        a generic message if an Ok variant.

        Following the Rust docs, since this panics the use of it is 
        discouraged; instead better to use pattern matching and handle
        the error case explicitly, or calling another method.

        >>> r = Result.Ok(10)
        >>> r.expect_err(msg="there is an error here")
        Traceback (most recent call last):
            ...
        ValueError: there is an error here

        >>> e = Result.Err("fail")
        >>> e.expect_err(msg="there is an error here")
        'fail'
        """
        if not self._is_ok:
            return self._val # type: ignore
        raise ValueError(msg)

    def map(self, func: Callable[[T], U]) -> "Result[U, E] | Result[T, E]":
        """
        Feeds the contained value of an Ok variant into a callable,
        basically mapping a Result<T, E> to a Result<U, E> (following
        the rust docs). If it's an Err variant, leaves the container
        unchanged.

        >>> r = Result.Ok(10)
        >>> r.map(lambda x: x ** 2)
        Ok(100)

        >>> e = Result.Err("fail")
        >>> e.map(lambda x: x ** 2)
        Err('fail')
        """
        return Result.Ok(func(self._val)) if self._is_ok else self # type: ignore

    def map_err(self, func: Callable[[E], F]) -> "Result[T, E] | Result[T, F]":
        """
        Feeds the contained value of an Ok variant into a callable,
        basically mapping a Result<T, E> to a Result<U, E> (following
        the rust docs). If it's an Err variant, leaves the container
        unchanged.

        >>> r = Result.Ok(10)
        >>> r.map_err(len)
        Ok(10)

        >>> e = Result.Err("fail")
        >>> e.map_err(len)
        Err(4)
        """
        return Result.Err(func(self._val)) if not self._is_ok else self # type:ignore

    def bind(
            self,
            func: Callable[[T], U],
            *args: Any,
            **kwargs: Any,
        ) -> "Result[U, E] | Result[T, E]":
        """
        Feeds the contained value of an Ok variant into a callable,
        basically mapping a Result<T, E> to a Result<U, E> (following
        the rust docs). If it's an Err variant, leaves the container
        unchanged. This mostly follows what map does, but adds to it.

        This is the biggest point of difference with the Rust result
        enum, since the bind in this instance allows passing arbitrary
        args and kwargs, but also has an included try-catch block to
        ensure that if there is any kind of failure the program doesn't
        panic, instead returns an Err variant with a failure dictionary
        that tracks the traceback, the callable, the Ok value, the
        exception that was raised, and all args. These data can be
        accessed from the self._failure dictionary

        The idea here is to provide better coverage for dealing with
        unexpected values passed and letting the program exit while 
        fully logging any expection.

        >>> sq = lambda x: x * x
        >>> r = Result.Ok(10)
        >>> r.bind(sq)
        Ok(100)
        >>> r = r.bind(sq).bind(sq)
        >>> r
        Ok(10000)
        >>> gives_err = r.bind(len)
        >>> gives_err
        Err(TypeError("object of type 'int' has no len()"))
        >>> gives_err._failure.get("func")
        'len'
        >>> e = Result.Err("fail")
        >>> e.bind(sq)
        Err('fail')
        """
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
        """
        This is a wrapper over the bind method that overrides the right
        shift operator to be able to chain bind calls using said
        operator. I wanted to have something that was similar to the 
        pipe operator, in particular for times when using the REPL.

        >>> sq = lambda x: x * x
        >>> r = Result.Ok(10)
        >>> r >> (sq) >> (sq)
        Ok(10000)
        >>> new = r >> (sq) >> (len)
        >>> new
        Err(TypeError("object of type 'int' has no len()"))
        >>> e = Result.Err("fail")
        >>> e >> (sq) >> (sq)
        Err('fail')
        >>> e >> (len)
        Err('fail')
        """
        return self.bind(func, *args, **kwargs)

    def bind_err(
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


def Ok(val: T) -> Result[T, Any]:
    return Result.Ok(val)

def Err(err: E, failure: dict[str, Any] = {})-> Result[Any, E]:
    return Result.Err(err, failure)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
