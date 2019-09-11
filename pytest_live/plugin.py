import pytest
import time

from _pytest.runner import pytest_sessionstart
from _pytest.runner import pytest_runtest_setup
from _pytest.runner import runtestprotocol
from _pytest.runner import pytest_runtest_teardown
from _pytest.runner import pytest_runtest_teardown

def pytest_addoption(parser):
    group = parser.getgroup('live')
    group.addoption(
        '--live_enable',
        action='store',
        dest='metrics_enable',
        default="True",
        help='Enable or disable metrics report'
    )

def pytest_sessionstart(session):
    print "Live - Execution session starts here - Will execute only once at first"

def pytest_runtest_setup(item):
    print "Live - Test setup - Test starts here"

def pytest_runtest_protocol(item, log=True, nextitem=None):
    # Provide's test case execution details
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        if report.when == 'call':
            # get test case name and test case status
            print '\n%s --- %s' % (item.name, report.outcome)
    return True

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # Error message if test case failed
        print rep.longreprtext

def pytest_runtest_teardown(item, nextitem):
    print "Live - Test teardown - Test ends here"

def pytest_sessionfinish(session):
    print "Live - Execution session ends here - Will execute only once at last"