# upd8

Simple version tracking and thread-safe access for Python objects.

## Features

- Track version numbers for state changes
- Thread-safe access with reentrant locks
- Declarative field definitions with versioning
- Batch multiple changes as a single version update
- Works with both synchronous and asynchronous code
- Hash and equality based on version and identity

## Installation

```bash
pip install upd8
```

## Quick Start

```python
from upd8 import Versioned, field, changes, waits

class Person(Versioned):
    name: str = field("Anonymous")
    age: int = field(0)

    @changes
    def have_birthday(self):
        self.age += 1
        return self.age

    @waits
    def get_summary(self):
        return f"{self.name} is {self.age} years old"

# Create instance with default values
person = Person()
print(person.version)  # 0

# Modify field (auto-increments version)
person.name = "Alice"
print(person.version)  # 1

# Batch multiple changes as one version increment
with person.change:
    person.name = "Bob"
    person.age = 30
print(person.version)  # 2

# Call method that changes state
person.have_birthday()
print(person.version)  # 3

# Read state safely
print(person.get_summary())  # "Bob is 31 years old"
```

## Async Support

`upd8` works seamlessly with async code:

```python
import asyncio
from upd8 import Versioned, field, changes, waits

class AsyncCounter(Versioned):
    count: int = field(0)

    @changes
    async def increment(self):
        await asyncio.sleep(0.1)  # Some async operation
        self.count += 1
        return self.count

    @waits
    async def get_count(self):
        await asyncio.sleep(0.1)  # Some async read
        return self.count

async def main():
    counter = AsyncCounter()

    # Use async methods
    await counter.increment()

    # Use async context manager
    async with counter.change:
        counter.count = 10
        await asyncio.sleep(0.1)  # Async operations in the context

    print(f"Final count: {await counter.get_count()}")

asyncio.run(main())
```

## License

Licensed under the WTFPL with one additional clause: Don't blame me.

Do whatever the fuck you want, just don't blame me.