DELIMITER //

ALTER TABLE `pedido` 
ADD COLUMN `observacoes` TEXT NULL AFTER `status`;

DESCRIBE `pedido`;
DELIMITER ;
