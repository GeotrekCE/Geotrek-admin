from django.test.runner import DiscoverRunner

from unittest.runner import TextTestRunner, TextTestResult
from time import time


class TimedTextTestResult(TextTestResult):

    def __init__(self, *args, **kwargs):
        super(TimedTextTestResult, self).__init__(*args, **kwargs)
        self.clocks = dict()
        self.max_time = 0
        self.black_sheep = ""

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
            if duration > self.max_time:
                self.max_time = duration
                self.black_sheep = test
        elif self.dots:
            self.stream.write('.')
            self.stream.flush()


class TimedTextTestRunner(TextTestRunner):
    resultclass = TimedTextTestResult

    def run(self, test):
        result = super(TimedTextTestRunner, self).run(test)
        self.stream.writeln("Longest test : %s" % result.black_sheep)
        return result


class TestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
