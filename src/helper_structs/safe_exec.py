from functools import wraps
from .result import Ok, Err, Result
from .failure import FailureContainer


def safe_exec(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> Result:
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
    return wrapper


@safe_exec
def add_one(a):
    return a + 1


def main():
    print(add_one(2))
    print(add_one("hello world"))
    an_err = add_one("hello_world")
    print(an_err.is_ok)
    print(an_err._failure)

    r = add_one(2)
    print(r.is_ok)
    print(r.unwrap_or(0))

if __name__ == "__main__":
    main()

