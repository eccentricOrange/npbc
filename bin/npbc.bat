if %1=="update" (
    git -C .. pull
)
else (
    executables/npbc.exe %*
)