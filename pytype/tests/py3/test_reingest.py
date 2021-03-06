"""Tests for reloading generated pyi."""

from pytype import file_utils
from pytype.pytd import pytd_utils
from pytype.tests import test_base


class ReingestTest(test_base.TargetPython3BasicTest):
  """Tests for reloading the pyi we generate."""

  def testTypeParameterBound(self):
    foo = self.Infer("""
      from typing import TypeVar
      T = TypeVar("T", bound=float)
      def f(x: T) -> T: return x
    """, deep=False)
    with file_utils.Tempdir() as d:
      d.create_file("foo.pyi", pytd_utils.Print(foo))
      _, errors = self.InferWithErrors("""
        import foo
        foo.f("")  # wrong-arg-types[e]
      """, pythonpath=[d.path])
      self.assertErrorRegexes(errors, {"e": r"float.*str"})

  def testDefaultArgumentType(self):
    foo = self.Infer("""
      from typing import Any, Callable, TypeVar
      T = TypeVar("T")
      def f(x):
        return True
      def g(x: Callable[[T], Any]) -> T: ...
    """)
    with file_utils.Tempdir() as d:
      d.create_file("foo.pyi", pytd_utils.Print(foo))
      self.Check("""
        import foo
        foo.g(foo.f).upper()
      """, pythonpath=[d.path])


class ReingestTestPy3(test_base.TargetPython3FeatureTest):
  """Python 3 tests for reloading the pyi we generate."""

  def testInstantiatePyiClass(self):
    foo = self.Infer("""
      import abc
      class Foo(metaclass=abc.ABCMeta):
        @abc.abstractmethod
        def foo(self):
          pass
      class Bar(Foo):
        def foo(self):
          pass
    """)
    with file_utils.Tempdir() as d:
      d.create_file("foo.pyi", pytd_utils.Print(foo))
      _, errors = self.InferWithErrors("""
        import foo
        foo.Foo()  # not-instantiable[e]
        foo.Bar()
      """, pythonpath=[d.path])
      self.assertErrorRegexes(errors, {"e": r"foo\.Foo.*foo"})


test_base.main(globals(), __name__ == "__main__")
