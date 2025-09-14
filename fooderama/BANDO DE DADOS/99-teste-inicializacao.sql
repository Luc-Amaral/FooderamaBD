USE fooderama;

SELECT 'VERIFICAÇÃO DE TABELAS' as status;
SELECT 
    TABLE_NAME as tabela_criada,
    TABLE_ROWS as total_linhas
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'fooderama'
ORDER BY TABLE_NAME;
SELECT 'VERIFICAÇÃO DE DADOS INICIAIS' as status;
SELECT 'Tipos de prato' as item, COUNT(*) as total FROM tipo_prato;

SELECT 'VERIFICAÇÃO DE TRIGGERS' as status;
SELECT 
    TRIGGER_NAME as trigger_criado,
    EVENT_MANIPULATION as evento,
    EVENT_OBJECT_TABLE as tabela
FROM information_schema.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'fooderama'
ORDER BY TRIGGER_NAME;

SELECT 'VERIFICAÇÃO DE PROCEDURES' as status;
SELECT 
    ROUTINE_NAME as procedure_criada,
    ROUTINE_TYPE as tipo
FROM information_schema.ROUTINES 
WHERE ROUTINE_SCHEMA = 'fooderama'
ORDER BY ROUTINE_NAME;

SELECT 'VERIFICAÇÃO DE VIEWS' as status;
SELECT 
    TABLE_NAME as view_criada
FROM information_schema.VIEWS 
WHERE TABLE_SCHEMA = 'fooderama'
ORDER BY TABLE_NAME;

SELECT 'INICIALIZAÇÃO VERIFICADA COM SUCESSO!' as resultado;