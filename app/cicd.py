import sys
from subprocess import Popen, PIPE

WIDTH_FINAL_RESULTS: int = 50

RUN: list = []
RUN.append("type_checking_functions")
# RUN.append("type_checking_django")
RUN.append("unit_testing_all_but_git")
# RUN.append("unit_testing_git_only")

outcome = {}
all_pass = True

if "type_checking_functions" in RUN:
    print("---------------------------------")
    print(" Type hint checking of functions ")
    print("---------------------------------")

    process1 = Popen(["mypy", "/dcsp/app/dcsp/app/functions"])
    process1.wait()
    if process1.returncode == 0:
        print("- No errors")
        outcome[" Functions hint typing"] = "Pass"
    else:
        print(f" -Errors, exit code of: { process1.returncode}")
        outcome[
            " Functions hint typing"
        ] = f"Fail - return code: { process1.returncode }"

if "type_checking_django" in RUN:
    print("------------------------------")
    print(" Type hint checking of Django")
    print("------------------------------")
    process2 = Popen(["mypy", "/dcsp/app/dcsp/app/"])
    process2.wait()
    if process2.returncode == 0:
        print("- No errors")
        outcome[" Django hint typing"] = "Pass"
    else:
        print(f" -Errors, exit code of: { process2.returncode}")
        outcome[
            " Django hint typing"
        ] = f"Fail - return code: { process2.returncode }"

if "unit_testing_all_but_git" in RUN:
    print("--------------------------")
    print(" Unit testing all but git ")
    print("--------------------------")

    process3 = Popen(
        ["python3", "manage.py", "test", "--exclude-tag=git"],
        cwd="/dcsp/app/dcsp/",
    )
    process3.wait()
    if process3.returncode == 0:
        print("- No errors")
        outcome[" Unit testing"] = "Pass"
    else:
        print(f" -Errors, exit code of: { process3.returncode}")
        outcome[
            " Unit testing"
        ] = f"Fail - return code: { process3.returncode }"


if "unit_testing_git_only" in RUN:
    print("----------------------------------")
    print(" Unit testing git and GitHub only ")
    print("----------------------------------")

    process4 = Popen(
        ["python3", "manage.py", "test", "app.tests.test_git_control"],
        cwd="/dcsp/app/dcsp",
    )
    process4.wait()
    if process4.returncode == 0:
        print("- No errors")
        outcome["Unit testing git and GitHub only"] = "Pass"
    else:
        print(f" -Errors, exit code of: { process4.returncode}")
        outcome[
            "Unit testing git and GitHub only"
        ] = f"Fail - return code: { process4.returncode }"


print(f"{''.ljust(WIDTH_FINAL_RESULTS, '-') }")
for test, value in outcome.items():
    if value != "pass":
        all_pass = False
    print(f"{ test.ljust(40, ' ') }{ value }")
print(f"{''.ljust(WIDTH_FINAL_RESULTS, '-') }")

if all_pass:
    sys.exit(0)
else:
    sys.exit(1)
