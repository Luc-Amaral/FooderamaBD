USE fooderama;


INSERT INTO tipo_prato (ID_TipoPrato, Tipo) VALUES
('1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p', 'Árabe'),
('2b3c4d5e-6f7g-8h9i-0j1k-2l3m4n5o6p7q', 'Churrasco'),
('3c4d5e6f-7g8h-9i0j-1k2l-3m4n5o6p7q8r', 'Comida Caseira'),
('4d5e6f7g-8h9i-0j1k-2l3m-4n5o6p7q8r9s', 'Doce'),
('5e6f7g8h-9i0j-1k2l-3m4n-5o6p7q8r9s0t', 'Frutos do Mar'),
('6f7g8h9i-0j1k-2l3m-4n5o-6p7q8r9s0t1u', 'Japonesa'),
('7g8h9i0j-1k2l-3m4n-5o6p-7q8r9s0t1u2v', 'Lanche'),
('8h9i0j1k-2l3m-4n5o-6p7q-8r9s0t1u2v3w', 'Massa'),
('9i0j1k2l-3m4n-5o6p-7q8r-9s0t1u2v3w4x', 'Mexicana'),
('0j1k2l3m-4n5o-6p7q-8r9s-0t1u2v3w4x5y', 'Pizza'),
('1k2l3m4n-5o6p-7q8r-9s0t-1u2v3w4x5y6z', 'Sorvete'),
('2l3m4n5o-6p7q-8r9s-0t1u-2v3w4x5y6z7a', 'Vegetariana');

SELECT 'Tipos de prato inseridos com sucesso!' as status, COUNT(*) as total FROM tipo_prato;