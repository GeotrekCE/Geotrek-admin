"""
Python compatibility functions.
"""
import sys
import os
import warnings
from typing import Any, Callable

# ------------------------------------------------------------------------------
# Python 2/3 compatibility
fs_encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()


def relpath(path: str, start: str = os.curdir) -> str:
    """Return a relative version of a path"""
    try:
        return os.path.relpath(path, start)
    except ValueError:
        return path


# convert_with_2to3():
# support for running 2to3 over config files
def convert_with_2to3(filepath: str) -> str:
    from lib2to3.refactor import RefactoringTool, get_fixers_from_package
    from lib2to3.pgen2.parse import ParseError
    fixers = get_fixers_from_package('lib2to3.fixes')
    refactoring_tool = RefactoringTool(fixers)
    source = refactoring_tool._read_python_source(filepath)[0]
    try:
        tree = refactoring_tool.refactor_string(source, 'conf.py')
    except ParseError as err:
        # do not propagate lib2to3 exceptions
        lineno, offset = err.context[1]
        # try to match ParseError details with SyntaxError details
        raise SyntaxError(err.msg, (filepath, lineno, offset, err.value))
    return str(tree)


def execfile_(filepath: str, _globals: Any, open: Callable = open) -> None:
    with open(filepath, 'rb') as f:
        source = f.read()

    # compile to a code object, handle syntax errors
    filepath_enc = filepath.encode(fs_encoding)
    try:
        code = compile(source, filepath_enc, 'exec')
    except SyntaxError:
        # maybe the file uses 2.x syntax; try to refactor to
        # 3.x syntax using 2to3
        source = convert_with_2to3(filepath)
        code = compile(source, filepath_enc, 'exec')
        warnings.warn('Support for evaluating Python 2 syntax is deprecated '
                      'and will be removed in sphinx-intl 4.0. '
                      'Convert %s to Python 3 syntax.',
                      source=filepath)
    exec(code, _globals)
