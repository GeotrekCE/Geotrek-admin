from time import time
from unittest.runner import TextTestResult, TextTestRunner

from django.test.runner import DiscoverRunner


class TimedTextTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clocks = dict()
        self.sheeps = {}

    def startTest(self, test):
        self.clocks[test] = time()
        super().startTest(test)

    def addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        if self.showAll:
            duration = time() - self.clocks[test]
            self.stream.writeln(f"ok ({duration:.6f}s)")
            self.sheeps[test] = duration
        elif self.dots:
            self.stream.write(".")
            self.stream.flush()


class TimedTextTestRunner(TextTestRunner):
    resultclass = TimedTextTestResult

    def run(self, test):
        result = super().run(test)
        if result.showAll:
            black_sheeps = [
                [k, v]
                for k, v in sorted(result.sheeps.items(), key=lambda item: item[1])
            ][-10:]
            self.stream.writeln("Top 10 : \n")
            for black_sheep in black_sheeps[::-1]:
                self.stream.writeln(f"{str(black_sheep[0])} : {black_sheep[1]} s")
        return result


class TestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
