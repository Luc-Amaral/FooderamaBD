CREATE TABLE `cliente` (
  `ID_Cliente` char(36) NOT NULL,
  `CPF` bigint NOT NULL,
  `Email` varchar(50) NOT NULL,
  `Senha` varchar(255) NOT NULL,
  `Telefone` bigint NOT NULL,
  `Nome` varchar(40) NOT NULL,
  `Sobrenome` varchar(40) NOT NULL,
  PRIMARY KEY (`ID_Cliente`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `Telefone` (`Telefone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `endereco` (
  `ID_Endereco` char(36) NOT NULL,
  `Rua` varchar(100) NOT NULL,
  `Numero` bigint NOT NULL,
  `Bairro` varchar(100) NOT NULL,
  `CEP` varchar(10) NOT NULL,
  PRIMARY KEY (`ID_Endereco`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `restaurante` (
  `ID_Restaurante` char(36) NOT NULL,
  `ID_Endereco_FK` char(36) NOT NULL,
  `NomeRestaurante` varchar(100) NOT NULL,
  `Email` varchar(40) NOT NULL,
  `Senha` varchar(255) NOT NULL,
  `Telefone` bigint NOT NULL,
  PRIMARY KEY (`ID_Restaurante`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `Telefone` (`Telefone`),
  CONSTRAINT `restaurante_ibfk_1` FOREIGN KEY (`ID_Endereco_FK`) REFERENCES `endereco` (`ID_Endereco`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `tipo_prato` (
  `ID_TipoPrato` char(36) NOT NULL,
  `Tipo` varchar(50) NOT NULL,
  PRIMARY KEY (`ID_TipoPrato`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `prato` (
  `ID_Prato` char(36) NOT NULL,
  `ID_Restaurante_FK` char(36) NOT NULL,
  `ID_TipoPrato_FK` char(36) NOT NULL,
  `Nome` varchar(100) NOT NULL,
  `Descricao` varchar(300) NOT NULL,
  `Preco` double NOT NULL,
  `Estoque` int NOT NULL DEFAULT '0',
  `StatusDisponibilidade` tinyint(1) NOT NULL,
  PRIMARY KEY (`ID_Prato`),
  CONSTRAINT `prato_ibfk_1` FOREIGN KEY (`ID_Restaurante_FK`) REFERENCES `restaurante` (`ID_Restaurante`) ON DELETE CASCADE,
  CONSTRAINT `prato_ibfk_2` FOREIGN KEY (`ID_TipoPrato_FK`) REFERENCES `tipo_prato` (`ID_TipoPrato`) ON DELETE CASCADE,
  CONSTRAINT `prato_chk_1` CHECK ((`Preco` > 0)),
  CONSTRAINT `prato_chk_2` CHECK ((`Estoque` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `metodo_pagamento` (
  `ID_MetodoPagamento` char(36) NOT NULL,
  `ID_Cliente_FK` char(36) NOT NULL,
  `TipoMetodo` enum('PIX','Debito','Credito') NOT NULL,
  PRIMARY KEY (`ID_MetodoPagamento`),
  CONSTRAINT `metodo_pagamento_ibfk_1` FOREIGN KEY (`ID_Cliente_FK`) REFERENCES `cliente` (`ID_Cliente`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `cartao` (
  `ID_Cartao` char(36) NOT NULL,
  `ID_MetodoPagamento_FK` char(36) NOT NULL,
  `NumeroCartao` varchar(20) NOT NULL,
  `NomePortador` varchar(100) NOT NULL,
  `DataVencimento` date NOT NULL,
  `CVV` varchar(4) NOT NULL,
  `TipoCartao` varchar(7) NOT NULL,
  PRIMARY KEY (`ID_Cartao`),
  UNIQUE KEY `NumeroCartao` (`NumeroCartao`),
  CONSTRAINT `cartao_ibfk_1` FOREIGN KEY (`ID_MetodoPagamento_FK`) REFERENCES `metodo_pagamento` (`ID_MetodoPagamento`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `pedido` (
  `ID_Pedido` char(36) NOT NULL,
  `ID_Cliente_FK` char(36) NOT NULL,
  `ID_Endereco_FK` char(36) NOT NULL,
  `ID_MetodoPagamento_FK` char(36) NOT NULL,
  `Data` date NOT NULL,
  `Hora` time NOT NULL,
  `status` varchar(255) NOT NULL,
  PRIMARY KEY (`ID_Pedido`),
  CONSTRAINT `pedido_ibfk_1` FOREIGN KEY (`ID_Cliente_FK`) REFERENCES `cliente` (`ID_Cliente`),
  CONSTRAINT `pedido_ibfk_2` FOREIGN KEY (`ID_Endereco_FK`) REFERENCES `endereco` (`ID_Endereco`) ON DELETE CASCADE,
  CONSTRAINT `pedido_ibfk_3` FOREIGN KEY (`ID_MetodoPagamento_FK`) REFERENCES `metodo_pagamento` (`ID_MetodoPagamento`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `item` (
  `ID_Item` char(36) NOT NULL,
  `ID_Pedido_FK` char(36) NOT NULL,
  `ID_Prato_FK` char(36) NOT NULL,
  `Quantidade` int NOT NULL,
  PRIMARY KEY (`ID_Item`),
  CONSTRAINT `item_ibfk_1` FOREIGN KEY (`ID_Pedido_FK`) REFERENCES `pedido` (`ID_Pedido`),
  CONSTRAINT `item_ibfk_2` FOREIGN KEY (`ID_Prato_FK`) REFERENCES `prato` (`ID_Prato`),
  CONSTRAINT `item_chk_1` CHECK ((`Quantidade` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `horafuncionamento` (
  `ID_HoraFuncionamento` char(36) NOT NULL,
  `ID_Restaurante_FK` char(36) NOT NULL,
  `DiaSemana` enum('Segunda', 'Terca', 'Quarta', 'Quinta', 'Sexta', 'Sabado', 'Domingo') NOT NULL,
  `HoraAbertura` time NOT NULL,
  `HoraFechamento` time NOT NULL,
  `Status` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`ID_HoraFuncionamento`),
  CONSTRAINT `horafuncionamento_ibfk_1` FOREIGN KEY (`ID_Restaurante_FK`) REFERENCES `restaurante` (`ID_Restaurante`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `feedback` (
  `ID_Cliente_FK` char(36) NOT NULL,
  `ID_Restaurante_FK` char(36) NOT NULL,
  `Avaliacao` int NOT NULL,
  `Feedback` varchar(200) DEFAULT NULL,
  `Data` date NOT NULL,
  `Hora` time NOT NULL,
  PRIMARY KEY (`ID_Restaurante_FK`,`ID_Cliente_FK`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`ID_Cliente_FK`) REFERENCES `cliente` (`ID_Cliente`),
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`ID_Restaurante_FK`) REFERENCES `restaurante` (`ID_Restaurante`),
  CONSTRAINT `feedback_chk_1` CHECK ((`Avaliacao` between 0 and 5))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `endereco_cliente` (
  `ID_Endereco_FK` char(36) NOT NULL,
  `ID_Cliente_FK` char(36) NOT NULL,
  `Data_Atualizacao` timestamp NOT NULL,
  PRIMARY KEY (`ID_Endereco_FK`,`ID_Cliente_FK`),
  CONSTRAINT `endereco_cliente_ibfk_1` FOREIGN KEY (`ID_Cliente_FK`) REFERENCES `cliente` (`ID_Cliente`) ON DELETE CASCADE,
  CONSTRAINT `endereco_cliente_ibfk_2` FOREIGN KEY (`ID_Endereco_FK`) REFERENCES `endereco` (`ID_Endereco`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;