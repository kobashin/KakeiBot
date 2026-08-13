@echo off
echo Installing git hooks...
copy /Y ".github\hooks\pre-commit" ".git\hooks\pre-commit"
echo Done. pre-commit hook installed.
pause
