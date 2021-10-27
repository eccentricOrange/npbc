if %1=="update" (
    git %APPDATA%/npbc pull
)
else (
    executables/npbc.exe %*
)