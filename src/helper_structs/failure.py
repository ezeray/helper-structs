from typing import Any, Optional
from traceback import  format_exc
from collections.abc import Sequence


class FailureContainer():
    def __init__(
        self,
        func: Optional[str] = None,
        args: Optional[Sequence[Any]] = None,
        kwargs: Optional[dict[Any, Any]] = None,
        exception: Optional[Any] = None,
        val: Optional[Any] = None,
        **add_kwargs,
    ) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.exception = exception
        self.val = val
        self.trace = format_exc()
        self._additional = add_kwargs

    def __repr__(self):
        return (
            f"Failure(\n\t{self.func=},\n\t{self.args=},\n\t{self.kwargs=},"
            f"\n\t{self.exception=},\n\t{self.val=},\n\t{self.trace=},"
            f"\n\t{self._additional=}\n)"
        )
    
    def as_dict(self):
        tmp_d = self.__dict__.copy()
        tmp_add = tmp_d.pop("_additional")
        if len(tmp_add.keys()) == 0:
            return tmp_d
        else:
            tmp_d.update(tmp_add)
            return tmp_d


    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key):
        return self.__dict__.get(key)




def add_one(a):
    return a + 1


def main():
    try:
        add_one(2)
    except Exception as e:
        fail = FailureContainer(
            add_one.__name__,
            args=[],
            kwargs={},
            exception=e,
        )
        print(fail)

    try:
        add_one("hello")
    except Exception as e:
        fail = FailureContainer(
            add_one.__name__,
            args=[],
            kwargs={},
            exception=e,
        )
        # print(fail.__dict__)
        print(fail["func"])
        print(fail["exception"])
        print(fail.get("non-existent"))

if __name__ == "__main__":
    main()

