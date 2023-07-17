from abc import ABCMeta


class ValidationMeta(ABCMeta):
    def __new__(cls: type, name: str, bases: tuple, dct: dict):
        # if "__annotations__" in dct:
        #     parent_annotations = [b.__annotations__ for b in bases if '__annotations__' in b.__dict__]
        #     dct["__annotations__"] = parent_annotations

        if "__slots__" not in dct and "__annotations__" in dct:
            dct["__slots__"] = (f"_{name}" for name in dct["__annotations__"])

        return super().__new__(cls, name, bases, dct)

