@echo off
setlocal EnableDelayedExpansion
pushd %~dp0

set COVERAGE_FILE=build/.coverage

rem Set needed environment variables.
set PTEST_TEMPFILE=temp_ptest.txt
set PTEST_SCRIPT_DIRECTORY=%~dp0
set PTEST_PYSCAN_SCRIPT_PATH=%PTEST_SCRIPT_DIRECTORY%..\pyscan\pyscan\main.py

rem Look for options on the command line.
set PTEST_PUBLISH_SUMMARIES=
:process_arguments
if "%1" == "-h" (
    echo Command: %0 [options]
    echo   Usage:
    echo     - Execute the tests for this project.
    echo   Options:
    echo     -h                This message.
	echo     -p				   Publish project summaries instead of running tests.
    GOTO real_end
) else if "%1" == "-p" (
	set PTEST_PUBLISH_SUMMARIES=1
) else if "%1" == "" (
    goto after_process_arguments
) else (
    echo Argument '%1' not understood.  Stopping.
	echo Type '%0 -h' to see valid arguments.
    goto error_end
)
shift
goto process_arguments
:after_process_arguments

if defined PTEST_PUBLISH_SUMMARIES (
	goto publish_start
)

rem Enter main part of script.
echo {Executing full test suite.}
set TEST_EXECUTION_FAILED=
pipenv run pytest > %PTEST_TEMPFILE% 2>&1
if ERRORLEVEL 1 (
	type %PTEST_TEMPFILE%
	echo.
	echo {Executing full test suite failed.}
	set TEST_EXECUTION_FAILED=1
)

echo {Summarizing changes in execution of full test suite.}
pipenv run python %PTEST_PYSCAN_SCRIPT_PATH% --only-changes --junit report\tests.xml --cobertura=report\coverage.xml
if ERRORLEVEL 1 (
	echo.
	echo {Summarizing changes in execution of full test suite failed.}
	goto error_end
)

if defined TEST_EXECUTION_FAILED (
	goto error_end
)

echo {Execution of full test suite succeeded.}
goto success_end

:publish_start
echo {Publishing summaries from previous test runs.}
pipenv run python %PTEST_PYSCAN_SCRIPT_PATH% --publish
if ERRORLEVEL 1 (
	echo.
	echo {Publishing summaries from previous test runs failed.}
	goto error_end
)
echo {Publishing summaries from previous test runs succeeded.}

:success_end
rem Exit main part of script.
echo.
set PC_EXIT_CODE=0
goto real_end

:error_end
set PC_EXIT_CODE=1
if not defined PTEST_PUBLISH_SUMMARIES (
	echo {Execution of full test suite failed.}
)

:real_end
erase /f /q %PTEST_TEMPFILE% > nul 2>&1
popd
exit /B %PC_EXIT_CODE%