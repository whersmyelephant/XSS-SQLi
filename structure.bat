@echo off
set "ROOT=XSS&SQLi"

rem === Création des dossiers ===
mkdir "%ROOT%"
mkdir "%ROOT%\static"
mkdir "%ROOT%\static\css"
mkdir "%ROOT%\static\img"
mkdir "%ROOT%\templates"
mkdir "%ROOT%\attaquant_server"
mkdir "%ROOT%\attaquant_server\templates"

rem === Création des fichiers principaux ===
call :createFile "%ROOT%\app.py"
call :createFile "%ROOT%\database.db"
call :createFile "%ROOT%\requirements.txt"

rem === Fichiers dans static ===
call :createFile "%ROOT%\static\css\style.css"
call :createFile "%ROOT%\static\img\logo.png"

rem === Fichiers dans templates ===
call :createFile "%ROOT%\templates\base.html"
call :createFile "%ROOT%\templates\index.html"
call :createFile "%ROOT%\templates\login.html"
call :createFile "%ROOT%\templates\profile.html"
call :createFile "%ROOT%\templates\search.html"
call :createFile "%ROOT%\templates\admin.html"

rem === Fichiers attaquant_server ===
call :createFile "%ROOT%\attaquant_server\app.py"
call :createFile "%ROOT%\attaquant_server\templates\home.html"
call :createFile "%ROOT%\attaquant_server\templates\dashboard.html"
call :createFile "%ROOT%\attaquant_server\stolen_cookies.txt"

goto :eof

:createFile
if not exist %1 (
    echo. > %1
    echo Created: %1
) else (
    echo Exists: %1
)
exit /b
