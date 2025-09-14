@echo off
echo ====================================
echo  TESTE DE INICIALIZACAO FOODERAMA
echo ====================================

echo.
echo [1/4] Parando containers existentes...
docker compose down -v

echo.
echo [2/4] Iniciando aplicacao...
docker compose up -d

echo.
echo [3/4] Aguardando MySQL inicializar (30 segundos)...
timeout /t 30 /nobreak > nul

echo.
echo [4/4] Testando conexao com banco...
docker compose exec db mysql -u root -p%MYSQL_ROOT_PASSWORD% -e "USE fooderama; SELECT 'TESTE OK' as status, COUNT(*) as tipos_prato FROM tipo_prato;"

echo.
echo ====================================
echo  TESTE CONCLUIDO!
echo ====================================
echo.
echo Para acessar:
echo - Aplicacao: http://localhost:5000
echo - Adminer:   http://localhost:8080
echo.
echo Para verificar logs:
echo   docker compose logs db
echo   docker compose logs web
echo.
pause