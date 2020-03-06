import pytest
import time
import os
import webbrowser

from _pytest.runner import pytest_sessionstart
from _pytest.runner import pytest_runtest_setup
from _pytest.runner import runtestprotocol
from _pytest.runner import pytest_runtest_teardown
from _pytest.runner import pytest_runtest_teardown

_total = 0
_executed = 0
_pass = 0
_fail = 0
_skip = 0
_error = 0
_xpass = 0
_xfail = 0
_content = ""
_current_error = ""
_test_name = None
_test_status = None
_duration = ""
_test_start_time = None
_now = 0
live_status = False

def pytest_addoption(parser):
    group = parser.getgroup('live')
    group.addoption(
        '--live',
        action='store',
        dest='live',
        default="False",
        help='Enable or disable live report'
    )

@pytest.hookimpl()
def pytest_sessionstart(session):

    global live_status
    live_status = session.config.option.live

    if live_status == "True":
        print("++++++++++++++ Inside True block ++++++++++++++ ")
        # create live logs report and close
        live_logs_file = open('LiveLogs.html','w')
        message = get_updated_html_text()
        live_logs_file.write(message)
        live_logs_file.close()

        # get location of livelogs
        current_dir = os.getcwd()
        filename =  current_dir + '/LiveLogs.html'

        # launch browser with livelogs
        webbrowser.open_new_tab(filename)

def pytest_runtest_setup(item):
    if live_status == "True":
        global _test_start_time
        _test_start_time = time.time()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    if live_status == "True":
        rep = outcome.get_result()
        global _test_status
        global _current_error
        global _xpass
        global _pass
        global _fail
        global _xfail
        global _error
        global _skip
        global _now

        current_time = time.localtime()
        _now = time.strftime("%d %b, %H:%M:%S", current_time)

        if rep.when == "call" and rep.passed:
            if hasattr(rep, "wasxfail"):
                _xpass += 1
                _test_status = "xPASS"
                _current_error = ""
            else:
                _pass += 1
                _test_status = "PASS"
                _current_error = ""

        if rep.failed:
            if getattr(rep, "when", None) == "call":
                if hasattr(rep, "wasxfail"):
                    _xpass += 1
                    _test_status = "xPASS"
                    _current_error = ""
                else:
                    _fail += 1
                    _test_status = "FAIL"
                    if rep.longrepr:
                        for line in rep.longreprtext.splitlines():
                            exception = line.startswith("E   ")
                            if exception:
                                _current_error = line.replace("E    ","")
            else:
                _error += 1
                _test_status = "ERROR"
                if rep.longrepr:
                    for line in rep.longreprtext.splitlines():
                        _current_error = line

        if rep.skipped:
            if hasattr(rep, "wasxfail"):
                _xfail += 1
                _test_status = "xFAIL"
                if rep.longrepr:
                    for line in rep.longreprtext.splitlines():
                        exception = line.startswith("E   ")
                        if exception:
                            _current_error = line.replace("E    ","")
            else:
                _skip += 1
                _test_status = "SKIP"
                if rep.longrepr:
                    for line in rep.longreprtext.splitlines():
                        _current_error = line

def pytest_runtest_teardown(item, nextitem):

    if live_status == "True":

        _test_end_time = time.time()

        global _test_name
        _test_name = item.name

        global _total
        _total =  _pass + _fail + _xpass + _xfail + _skip + _error

        global _executed
        _executed = _pass + _fail + _xpass + _xfail

        global _duration
        _duration = _test_end_time - _test_start_time

        table_text = generate_table_row()

        global _content
        _content += table_text

        live_logs_file = open('LiveLogs.html','w')
        message = get_updated_html_text()
        live_logs_file.write(message)
        live_logs_file.close()


def get_html_template():
    my_template = """
    <html>

    <head>
        <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
    <link href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.min.css" rel="stylesheet"/>
    <link href="https://cdn.datatables.net/buttons/1.5.2/css/buttons.dataTables.min.css" rel="stylesheet"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
      <!-- Bootstrap core Datatable-->
    <script src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js" type="text/javascript"></script>
    <script src="https://cdn.datatables.net/buttons/1.5.2/js/dataTables.buttons.min.js" type="text/javascript"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js" type="text/javascript"></script>
    <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.html5.min.js" type="text/javascript"></script>
    <script src="https://cdn.datatables.net/buttons/1.5.2/js/buttons.print.min.js" type="text/javascript"></script>
    <script src="https://cdn.datatables.net/buttons/1.6.1/js/buttons.colVis.min.js" type="text/javascript"></script>

	<style>
        .dt-buttons {
            margin-left: 5px;
        }
    </style>
    </head>

    <body>

        <table style="width: 100%;">
            <tbody>
                <tr>
                    <td>
                        <h2 style="color:Brown;padding-left: 10px;">Live Execution Results</h2></td>
                    <td style="text-align: right;padding-right: 30px;">Set Page Refresh Rate:
                        <input type="button" class="btn btn-primary" value="1 Minute" onclick="setRe(60);" />
                        <input type="button" class="btn btn-primary" value="5 Minute" onclick="setRe(300);"/>
                        <input type="button" class="btn btn-danger" value="No Refresh" onclick="setRe(0);" />
                    </td>
                </tr>
            </tbody>
        </table>
        </br>
        <table width="100%;">
            <tbody>
                <tr style="text-align: center; height:40px;color:white">
                    <td style="border-radius: 25px;width: 12.5%;background: DARKSLATEBLUE;">TOTAL</td>
                    <td style="border-radius: 25px;width: 12.5%;background: DARKCYAN;">EXECUTED</td>
                    <td style="border-radius: 25px;width: 12.5%;background: FORESTGREEN;">PASS</td>
                    <td style="border-radius: 25px;width: 12.5%;background: RED;">FAIL</td>
                    <td style="border-radius: 25px;width: 12.5%;background: DARKKHAKI;">SKIP</td>
                    <td style="border-radius: 25px;width: 12.5%;background: GRAY;">ERROR</td>
                    <td style="border-radius: 25px;width: 12.5%;background: SEAGREEN;">xPASS</td>
                    <td style="border-radius: 25px;width: 12.5%;background: TOMATO;">xFAIL</td>
                </tr>
                <tr style="text-align: center; height: 40px; font-weight:bold">
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__total__</td>
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__executed__</td>
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__pass__</td>
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__fail__</td>
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__skip__</td>
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__error__</td>
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__xpass__</td>
                    <td style="border-radius: 25px;width: 12.5%;background: LAVENDER;">__xfail__</td>
                </tr>
            </tbody>
        </table>
        </br>
        <table id="example" class="display" style="width:100%">
            <thead>
                <tr>
                    <th style="width: 8%">SN</th>
                    <th style="width: 10%">Time</th>
                    <th style="width: 30%">Test Case</th>
                    <th style="width: 10%">Status</th>
                    <th style="width: 10%">Duration (s)</th>
                    <th style="width: 30%">Error Message</th>
                </tr>
            </thead>
            <tbody style=>
            __content__
        </table>
        <script>
            $(document).ready(function() {
                $('#example').DataTable({
                    "order": [
                        [0, "desc"]
                    ],
					"lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
					dom: 'l<".margin" B>frtip',
                    buttons: [
                         {
							extend:    'copyHtml5',
							text:      '<i class="fa fa-files-o"></i>',
							titleAttr: 'Copy',
							exportOptions: {
								columns: ':visible'
							}
						},
                        {
                            extend:    'csvHtml5',
							text:      '<i class="fa fa-file-text-o"></i>',
							titleAttr: 'CSV',
                            filename: function() {
                                return fileTitle + '-' + new Date().toLocaleString();
                            },
							exportOptions: {
								columns: ':visible'
							}
                        },
                        {
                            extend:    'excelHtml5',
							text:      '<i class="fa fa-file-excel-o"></i>',
							titleAttr: 'Excel',
                            filename: function() {
                                return fileTitle + '-' + new Date().toLocaleString();
                            },
							exportOptions: {
								columns: ':visible'
							}
                        },
                        {
							extend:    'print',
							text:      '<i class="fa fa-print"></i>',
							titleAttr: 'Print',
							exportOptions: {
								columns: ':visible',
                                alignment: 'left',
							}
                        },
						{
							extend:    'colvis',
							collectionLayout: 'fixed two-column',
							text:      '<i class="fa fa-low-vision"></i>',
							titleAttr: 'Hide Column',
							exportOptions: {
								columns: ':visible'
							},
							postfixButtons: [ 'colvisRestore' ]
                        },
                    ],
					columnDefs: [ {
						visible: false,
					} ]
                });
            });
        </script>
        <script type="text/javascript">
            var reIt

            function doit() {
                if (window.location.reload)
                    window.location.reload(true);
                else if (window.location.replace)
                    window.location.replace(unescape(location.href))
                else
                    window.location.href = unescape(location.href)
            }

            function startUp() {
                if (unescape(document.cookie).split(';')[1])
                    reIt = setTimeout("doit()", unescape(document.cookie).split(';')[1])
                else
                    reIt = setTimeout("doit()", 60000)
            }

            function setRe(val) {
                clearTimeout(reIt)
                if (val == 0) {
                    document.cookie = ''
                    return;
                } else
                    document.cookie = val * 1000
                startUp();
            }

            onload = startUp
        </script>
    </body>

    </html>
    """
    return my_template

def get_updated_html_text():
    template_text = get_html_template()
    template_text = template_text.replace("__total__", str(_total))
    template_text = template_text.replace("__executed__", str(_executed))
    template_text = template_text.replace("__pass__", str(_pass))
    template_text = template_text.replace("__fail__", str(_fail))
    template_text = template_text.replace("__skip__", str(_skip))
    template_text = template_text.replace("__error__", str(_error))
    template_text = template_text.replace("__xpass__", str(_xpass))
    template_text = template_text.replace("__xfail__", str(_xfail))
    template_text = template_text.replace("__content__", _content)
    return template_text

def generate_table_row():
    row_text = """
        <tr>
            <td style="width: 8%; text-align:center;">__id__</td>
            <td style="width: 10%; text-align:center;">__now__</td>
            <td style="width: 30%;">__name__</td>
            <td style="width: 10%; "text-align:center;">__stat__</td>
            <td style="width: 10%; text-align:center;">__dur__</td>
            <td style="width: 30%;">__msg__</td>
        </tr>
    """

    row_text = row_text.replace("__id__",str(_total))
    row_text = row_text.replace("__now__",str(_now))
    row_text = row_text.replace("__name__",str(_test_name))
    row_text = row_text.replace("__stat__",str(_test_status))
    row_text = row_text.replace("__dur__",str(round(_duration,2)))
    row_text = row_text.replace("__msg__",str(_current_error))

    return row_text