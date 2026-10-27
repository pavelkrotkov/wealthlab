"""The gates must reject bad code, including nested and asynchronous functions."""

from tools.quality_metrics import measure, violations


def test_small_function_passes():
    assert violations(measure("def double(value):\n    return value * 2\n")) == []


def test_complexity_rejects_ninth_path():
    source = "def choose(x):\n" + "".join(f"    if x == {n}: return {n}\n" for n in range(8))
    assert any(v.startswith("CC=") for v in violations(measure(source)))


def test_low_maintainability_rejected():
    source = "\n".join(f"x{n} = ({n} + 3) * (5 - {n}) / 7" for n in range(120))
    assert any(v.startswith("MI=") for v in violations(measure(source)))


def test_module_size_rejected():
    assert any(v.startswith("SLOC=") for v in violations(measure("x = 1\n" * 301)))


def test_long_async_function_rejected():
    source = "async def work():\n" + "    x = 1\n" * 60
    assert any(v.startswith("function_lines=") for v in violations(measure(source)))


def test_nested_function_and_class_are_measured():
    branches = "".join(f"        if x == {n}: return {n}\n" for n in range(8))
    source = "def outer():\n    def inner(x):\n" + branches
    assert measure(source)["CC"] == 9
    method = "class Example:\n    def method(self, x):\n" + branches
    assert measure(method)["CC"] >= 9


def test_gate_boundaries():
    assert violations({"CC": 8, "MI": 50, "SLOC": 300, "function_lines": 60}) == []
    assert len(violations({"CC": 9, "MI": 49, "SLOC": 301, "function_lines": 61})) == 4
