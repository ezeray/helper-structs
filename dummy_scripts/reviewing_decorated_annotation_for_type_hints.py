from result import Result
from safe_exec import safe_exec


@safe_exec
def greet(x: str) -> str:
    x = f"Hello {x}!"
    return x


def unwrapped_greet(x: str) -> str:
    x = f"Hello {x}!"
    return x

def do_none() -> Result[int, int]:
    return Result.Ok(0)

@safe_exec
def no_an(x):
    return x * x

if __name__ == "__main__":
    print(do_none.__name__)
    print(do_none.__annotations__)

    name = "ezequiel"

    print(greet.__name__)
    print(greet.__annotations__)
    n_two = greet(name)
    print(type(n_two))

    print(n_two.is_ok)

    print(no_an.__name__)
    print(no_an.__annotations__)
