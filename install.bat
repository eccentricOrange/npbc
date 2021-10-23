git clone https://github.com/eccentricOrange/npbc.git %PROGRAMFILES%\npbc

if exist %userprofile%\.npbc (
    echo "Not updating user directory."
) else (
    xcopy /s %PROGRAMFILED%\npbc\data %userprofile%\.npbc
)

setx path "%PATH%;%PROGRAMFILES%\npbc\bin" /M