git clone https://github.com/eccentricOrange/npbc.git "%APPDATA%\npbc"

if exist "%USERPROFILE%\.npbc\" (
    echo "Not updating user directory."
) else (
    echo "1"
    echo "2"
    xcopy /s "%APPDATA%\npbc\data\." "%USERPROFILE%\.npbc\"
)

@REM setx path "%PATH%;%APPDATA%\npbc\bin"
@REM
@REM This is disabled right now because I am struggling
@REM with the 1024 character limit of setx.