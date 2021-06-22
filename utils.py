import typing as t


def chunks(list_: t.Collection[t.Any], n: int) -> t.Generator[t.Collection[t.Any], None, None]:
    for i in range(0, len(list_), n):
        yield list_[i:i + n]
