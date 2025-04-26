"""
Tests for asynchronous functionality in the upd8 package.
"""

import asyncio

import pytest

from upd8 import AbortUpdate, Versioned, changes, field, waits


class AsyncTest(Versioned):
    """Test class for async functionality"""

    value = field(0)
    name = field("default")

    @changes
    async def increment(self, amount=1):
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        self.value += amount
        return self.value

    @waits
    async def get_value(self):
        await asyncio.sleep(0.01)  # Small delay to simulate async work
        return self.value

    @changes
    async def abort_if_negative(self, value):
        await asyncio.sleep(0.01)
        if value < 0:
            raise AbortUpdate()
        self.value = value
        return self.value


@pytest.mark.asyncio
async def test_async_changes_decorator():
    """Test that async @changes decorator works correctly"""
    obj = AsyncTest()
    initial_version = obj.version

    result = await obj.increment(5)

    assert result == 5  # Method returns correct value
    assert obj.value == 5  # State is updated
    assert obj.version > initial_version  # Version incremented


@pytest.mark.asyncio
async def test_async_waits_decorator():
    """Test that async @waits decorator works correctly"""
    obj = AsyncTest()
    obj.value = 42
    initial_version = obj.version

    result = await obj.get_value()

    assert result == 42  # Method returns correct value
    assert obj.version == initial_version  # Version unchanged


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test the async context manager works"""
    obj = AsyncTest()
    initial_version = obj.version

    async with obj.change:
        obj.value = 10
        await asyncio.sleep(0.01)  # Do async work inside the context
        obj.name = "test"

    assert obj.value == 10
    assert obj.name == "test"
    assert obj.version > initial_version  # Version incremented


@pytest.mark.asyncio
async def test_async_abort_update():
    """Test that AbortUpdate works with async methods"""
    obj = AsyncTest()
    initial_version = obj.version

    # AbortUpdate should be caught and result should be None
    result = await obj.abort_if_negative(-5)
    assert result is None
    assert obj.version == initial_version  # Version unchanged

    # Normal execution should work and increment version
    result = await obj.abort_if_negative(5)
    assert result == 5
    assert obj.version > initial_version  # Version incremented


@pytest.mark.asyncio
async def test_async_abort_in_context():
    """Test AbortUpdate in async context manager"""
    obj = AsyncTest()
    initial_version = obj.version

    # AbortUpdate should be suppressed by context manager
    async with obj.change:
        obj.value = 5
        await asyncio.sleep(0.01)
        raise AbortUpdate()

    assert obj.version == initial_version + 1
    assert obj.value == 5  # Value was changed


@pytest.mark.asyncio
async def test_concurrent_async_operations():
    """Test multiple async operations running concurrently"""
    obj = AsyncTest()
    initial_version = obj.version

    # Run multiple operations concurrently
    tasks = [
        obj.increment(1),
        obj.increment(2),
        obj.increment(3),
        obj.increment(4),
        obj.increment(5),
    ]

    results = await asyncio.gather(*tasks)

    # Sum of all increment amounts = 15
    assert obj.value == 15
    assert obj.version > initial_version
    assert sorted(results) == [1, 3, 6, 10, 15]  # Cumulative values
