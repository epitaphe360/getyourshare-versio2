@echo off
REM Script pour executer le scenario de test SQL
REM Assurez-vous que 'psql' est dans votre PATH systeme (installe avec PostgreSQL)

echo ==========================================
echo EXECUTION DU SCENARIO DE TEST AUTOMATISE
echo ==========================================

set /p DB_NAME="Nom de la base de donnees (defaut: getyourshare): "
if "%DB_NAME%"=="" set DB_NAME=getyourshare

set /p DB_USER="Utilisateur Postgres (defaut: postgres): "
if "%DB_USER%"=="" set DB_USER=postgres

echo.
echo Connexion a %DB_NAME% en tant que %DB_USER%...
echo Lancement du script automation_scenario.sql...
echo.

psql -U %DB_USER% -d %DB_NAME% -f "automation_scenario.sql"

echo.
echo ==========================================
echo FIN DU TEST - Verifiez les resultats ci-dessus
echo ==========================================
pause
