from dataclasses import dataclass

class MyClass:
    @classmethod
    def my_class_method(cls):
        ...


@dataclass(frozen=True)
class Part:
    part_id: int
    part_description:str


part1 = Part(123, 'Rolig hammare')

print(part1)
part1.part_id = 321
print(part1.part_id)
print(part1.part_description)
