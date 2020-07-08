from django.test.runner import DiscoverRunner

from unittest.runner import TextTestRunner, TextTestResult
from time import time


class TimedTextTestResult(TextTestResult):

    def __init__(self, *args, **kwargs):
        super(TimedTextTestResult, self).__init__(*args, **kwargs)
        self.clocks = dict()
        self.sheeps = {}

    def startTest(self, test):
        self.clocks[test] = time()
        super(TextTestResult, self).startTest(test)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(" ... ")
            self.stream.flush()

    def addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        if self.showAll:
            duration = time() - self.clocks[test]
            self.stream.writeln("ok (%.6fs)" % (duration))
            self.sheeps[test] = duration
        elif self.dots:
            self.stream.write('.')
            self.stream.flush()


class TimedTextTestRunner(TextTestRunner):
    resultclass = TimedTextTestResult

    def run(self, test):
        result = super(TimedTextTestRunner, self).run(test)
        black_sheeps = [[k, v] for k, v in sorted(result.sheeps.items(), key=lambda item: item[1])][-10:]
        self.stream.writeln("Top 10 : \n")
        for black_sheep in black_sheeps[::-1]:
            self.stream.writeln("%s : %s s" % (str(black_sheep[0]), black_sheep[1]))
        return result


class TestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
