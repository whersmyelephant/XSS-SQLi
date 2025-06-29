@echo off
REM Création de l'arborescence de fichiers

mkdir templates
mkdir attaquant_server

REM Création des fichiers racine
type nul > app.py
type nul > database.db
type nul > requirements.txt

REM Création des fichiers templates
type nul > templates\base.html
type nul > templates\index.html
type nul > templates\login.html
type nul > templates\profile.html
type nul > templates\admin.html
type nul > templates\search.html

REM Création du fichier pour le serveur attaquant
type nul > attaquant_server\app.py

REM Affichage de la structure créée
echo Structure créée :
tree /F