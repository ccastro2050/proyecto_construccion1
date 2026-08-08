/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.8-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: bdfacturas_mariadb_local
-- ------------------------------------------------------
-- Server version	11.8.8-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `credito` decimal(18,2) NOT NULL DEFAULT 0.00,
  `fkcodpersona` varchar(10) NOT NULL,
  `fkcodempresa` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cliente_persona` (`fkcodpersona`),
  KEY `fk_cliente_empresa` (`fkcodempresa`),
  CONSTRAINT `fk_cliente_empresa` FOREIGN KEY (`fkcodempresa`) REFERENCES `empresa` (`codigo`),
  CONSTRAINT `fk_cliente_persona` FOREIGN KEY (`fkcodpersona`) REFERENCES `persona` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES
(1,520000.00,'P001','E001'),
(2,250000.00,'P003','E002'),
(3,400000.00,'P005','E001'),
(5,700000.00,'P006','E001');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `empresa`
--

DROP TABLE IF EXISTS `empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresa` (
  `codigo` varchar(10) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empresa`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `empresa` WRITE;
/*!40000 ALTER TABLE `empresa` DISABLE KEYS */;
INSERT INTO `empresa` VALUES
('E001','Comercial Los Andes S.A.'),
('E002','Distribuciones El Centro S.A.'),
('E999','Empresa Test');
/*!40000 ALTER TABLE `empresa` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `factura`
--

DROP TABLE IF EXISTS `factura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `factura` (
  `numero` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `total` decimal(18,2) NOT NULL DEFAULT 0.00,
  `estado` varchar(10) NOT NULL DEFAULT 'activa',
  `fkidcliente` int(11) NOT NULL,
  `fkidvendedor` int(11) NOT NULL,
  PRIMARY KEY (`numero`),
  KEY `fk_factura_cliente` (`fkidcliente`),
  KEY `fk_factura_vendedor` (`fkidvendedor`),
  CONSTRAINT `fk_factura_cliente` FOREIGN KEY (`fkidcliente`) REFERENCES `cliente` (`id`),
  CONSTRAINT `fk_factura_vendedor` FOREIGN KEY (`fkidvendedor`) REFERENCES `vendedor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `factura`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `factura` WRITE;
/*!40000 ALTER TABLE `factura` DISABLE KEYS */;
INSERT INTO `factura` VALUES
(1,'2025-12-03 12:57:19',5000000.00,'activa',1,1),
(2,'2025-12-03 12:57:19',1250000.00,'activa',2,2),
(3,'2025-12-03 12:57:19',2030000.00,'activa',3,3),
(4,'2025-12-03 13:04:59',950000.00,'activa',1,1),
(5,'2025-12-03 13:05:17',2740000.00,'activa',2,2),
(6,'2025-12-03 13:05:35',4850000.00,'activa',3,3);
/*!40000 ALTER TABLE `factura` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `persona`
--

DROP TABLE IF EXISTS `persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona` (
  `codigo` varchar(10) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `telefono` varchar(20) NOT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `persona` WRITE;
/*!40000 ALTER TABLE `persona` DISABLE KEYS */;
INSERT INTO `persona` VALUES
('P001','Ana Torres','ana.torres@correo.com','3011111111'),
('P002','Carlos Pérez','carlos.perez@correo.com','3022222222'),
('P003','María Gómez','maria.gomez@correo.com','3033333333'),
('P004','Juan Díaz','juan.diaz@correo.com','3044444444'),
('P005','Laura Rojas','laura.rojas@correo.com','3055555555'),
('P006','Pedro Castillo','pedro.castillo@correo.com','3066666666');
/*!40000 ALTER TABLE `persona` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `codigo` varchar(10) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `stock` int(11) NOT NULL,
  `valorunitario` decimal(18,2) NOT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES
('PR001','Laptop Lenovo IdeaPad',17,2500000.00),
('PR002','Monitor Samsung 24\"',27,800000.00),
('PR003','Teclado Logitech K380',42,150000.00),
('PR004','Mouse HP',55,90000.00),
('PR005','Impresora Epson EcoTank1',14,1100000.00),
('PR006','Auriculares Sony WH-CH510',23,240000.00),
('PR007','Tablet Samsung Tab A9',15,950000.00),
('PR008','Disco Duro Seagate 1TB',32,280000.00);
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `productosporfactura`
--

DROP TABLE IF EXISTS `productosporfactura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `productosporfactura` (
  `fknumfactura` int(11) NOT NULL,
  `fkcodproducto` varchar(10) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `subtotal` decimal(18,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`fknumfactura`,`fkcodproducto`),
  KEY `fk_prodfact_producto` (`fkcodproducto`),
  CONSTRAINT `fk_prodfact_factura` FOREIGN KEY (`fknumfactura`) REFERENCES `factura` (`numero`) ON DELETE CASCADE,
  CONSTRAINT `fk_prodfact_producto` FOREIGN KEY (`fkcodproducto`) REFERENCES `producto` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productosporfactura`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `productosporfactura` WRITE;
/*!40000 ALTER TABLE `productosporfactura` DISABLE KEYS */;
INSERT INTO `productosporfactura` VALUES
(1,'PR001',2,5000000.00),
(2,'PR002',1,800000.00),
(2,'PR003',3,450000.00),
(3,'PR004',5,450000.00),
(3,'PR005',1,1100000.00),
(3,'PR006',2,480000.00),
(4,'PR007',1,950000.00),
(5,'PR007',2,1900000.00),
(5,'PR008',3,840000.00),
(6,'PR001',1,2500000.00),
(6,'PR002',2,1600000.00),
(6,'PR003',5,750000.00);
/*!40000 ALTER TABLE `productosporfactura` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_prodfact_before_insert
BEFORE INSERT ON productosporfactura
FOR EACH ROW
BEGIN
    DECLARE v_precio DECIMAL(18,2);
    DECLARE v_stock INT;
    DECLARE v_msg VARCHAR(500);

    SELECT valorunitario, stock INTO v_precio, v_stock
    FROM producto WHERE codigo = NEW.fkcodproducto;

    IF v_stock < NEW.cantidad THEN
        SET v_msg = CONCAT('Stock insuficiente para producto ', NEW.fkcodproducto,
            '. Stock disponible: ', v_stock, ', cantidad solicitada: ', NEW.cantidad);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    SET NEW.subtotal = NEW.cantidad * v_precio;
    UPDATE producto SET stock = stock - NEW.cantidad WHERE codigo = NEW.fkcodproducto;
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_prodfact_after_insert
AFTER INSERT ON productosporfactura
FOR EACH ROW
BEGIN
    UPDATE factura
    SET total = (SELECT COALESCE(SUM(subtotal), 0) FROM productosporfactura WHERE fknumfactura = NEW.fknumfactura)
    WHERE numero = NEW.fknumfactura;
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_prodfact_before_update
BEFORE UPDATE ON productosporfactura
FOR EACH ROW
BEGIN
    DECLARE v_precio DECIMAL(18,2);
    DECLARE v_stock INT;
    DECLARE v_msg VARCHAR(500);

    SELECT valorunitario INTO v_precio FROM producto WHERE codigo = NEW.fkcodproducto;
    SELECT stock INTO v_stock FROM producto WHERE codigo = NEW.fkcodproducto;

    IF v_stock + OLD.cantidad < NEW.cantidad THEN
        SET v_msg = CONCAT('Stock insuficiente para producto ', NEW.fkcodproducto,
            '. Stock disponible: ', v_stock + OLD.cantidad, ', cantidad solicitada: ', NEW.cantidad);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    SET NEW.subtotal = NEW.cantidad * v_precio;
    UPDATE producto
    SET stock = stock + OLD.cantidad - NEW.cantidad
    WHERE codigo = NEW.fkcodproducto;
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_prodfact_after_update
AFTER UPDATE ON productosporfactura
FOR EACH ROW
BEGIN
    UPDATE factura
    SET total = (SELECT COALESCE(SUM(subtotal), 0) FROM productosporfactura WHERE fknumfactura = NEW.fknumfactura)
    WHERE numero = NEW.fknumfactura;
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_prodfact_before_delete
BEFORE DELETE ON productosporfactura
FOR EACH ROW
BEGIN
    UPDATE producto
    SET stock = stock + OLD.cantidad
    WHERE codigo = OLD.fkcodproducto;
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER trg_prodfact_after_delete
AFTER DELETE ON productosporfactura
FOR EACH ROW
BEGIN
    UPDATE factura
    SET total = (SELECT COALESCE(SUM(subtotal), 0) FROM productosporfactura WHERE fknumfactura = OLD.fknumfactura)
    WHERE numero = OLD.fknumfactura;
END 
*/;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES
(1,'Administrador'),
(2,'Vendedor'),
(3,'Cajero'),
(4,'Contador'),
(5,'Cliente');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `rol_usuario`
--

DROP TABLE IF EXISTS `rol_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol_usuario` (
  `fkemail` varchar(100) NOT NULL,
  `fkidrol` int(11) NOT NULL,
  PRIMARY KEY (`fkemail`,`fkidrol`),
  KEY `fk_rolusuario_rol` (`fkidrol`),
  CONSTRAINT `fk_rolusuario_rol` FOREIGN KEY (`fkidrol`) REFERENCES `rol` (`id`),
  CONSTRAINT `fk_rolusuario_usuario` FOREIGN KEY (`fkemail`) REFERENCES `usuario` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol_usuario`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `rol_usuario` WRITE;
/*!40000 ALTER TABLE `rol_usuario` DISABLE KEYS */;
INSERT INTO `rol_usuario` VALUES
('admin@correo.com',1),
('carlos.castro@usbmed.edu.co',1),
('carloscastro5033@correo.itm.edu.co',1),
('jefe@correo.com',1),
('nuevo@correo.com',1),
('test_encript@correo.com',1),
('carlos.castro@usbmed.edu.co',2),
('carloscastro5033@correo.itm.edu.co',2),
('nuevo@correo.com',2),
('vendedor1@correo.com',2),
('carlos.castro@usbmed.edu.co',3),
('carloscastro5033@correo.itm.edu.co',3),
('jefe@correo.com',3),
('nuevo@correo.com',3),
('vendedor1@correo.com',3),
('carlos.castro@usbmed.edu.co',4),
('carloscastro5033@correo.itm.edu.co',4),
('jefe@correo.com',4),
('carlos.castro@usbmed.edu.co',5),
('carloscastro5033@correo.itm.edu.co',5),
('cliente1@correo.com',5);
/*!40000 ALTER TABLE `rol_usuario` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `ruta`
--

DROP TABLE IF EXISTS `ruta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ruta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruta` varchar(100) NOT NULL,
  `descripcion` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ruta` (`ruta`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ruta`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `ruta` WRITE;
/*!40000 ALTER TABLE `ruta` DISABLE KEYS */;
INSERT INTO `ruta` VALUES
(1,'/home','Página principal - Dashboard'),
(2,'/usuario','Gestión de usuarios'),
(3,'/factura','Gestión de facturas'),
(4,'/cliente','Gestión de clientes'),
(5,'/vendedor','Gestión de vendedores'),
(6,'/persona','Gestión de personas'),
(7,'/empresa','Gestión de empresas'),
(8,'/producto','Gestión de productos'),
(9,'/rol','Gestión de roles'),
(10,'/permiso','Gestión de permisos (asignación rol-ruta)'),
(11,'/permiso/crear','Crear permiso (POST)'),
(12,'/permiso/eliminar','Eliminar permiso (POST)'),
(13,'/ruta','Gestión de rutas del sistema'),
(14,'/ruta/crear','Crear ruta (POST)'),
(15,'/ruta/eliminar','Eliminar ruta (POST)');
/*!40000 ALTER TABLE `ruta` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `rutarol`
--

DROP TABLE IF EXISTS `rutarol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `rutarol` (
  `fkidruta` int(11) NOT NULL,
  `fkidrol` int(11) NOT NULL,
  PRIMARY KEY (`fkidruta`,`fkidrol`),
  KEY `fk_rutarol_rol` (`fkidrol`),
  CONSTRAINT `fk_rutarol_rol` FOREIGN KEY (`fkidrol`) REFERENCES `rol` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_rutarol_ruta` FOREIGN KEY (`fkidruta`) REFERENCES `ruta` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rutarol`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `rutarol` WRITE;
/*!40000 ALTER TABLE `rutarol` DISABLE KEYS */;
INSERT INTO `rutarol` VALUES
(1,1),
(2,1),
(3,1),
(4,1),
(5,1),
(6,1),
(7,1),
(8,1),
(9,1),
(10,1),
(11,1),
(12,1),
(13,1),
(14,1),
(15,1),
(1,2),
(3,2),
(4,2),
(1,3),
(3,3),
(1,4),
(4,4),
(8,4),
(1,5),
(8,5);
/*!40000 ALTER TABLE `rutarol` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `email` varchar(100) NOT NULL,
  `contrasena` varchar(200) NOT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES
('admin@correo.com','$2a$12$3UgI.Eof.FhzsYUWESI9n.qFaqkV2JPhvW3L/1GTKowNJnGaD8F.G'),
('carlos.castro@usbmed.edu.co','$2a$10$YYl6bHCflCnk8suUrms3ie.rnpLvfD9nHJtehZwhcSkINelGwt6iC'),
('carloscastro5033@correo.itm.edu.co','$2a$10$YYl6bHCflCnk8suUrms3ie.rnpLvfD9nHJtehZwhcSkINelGwt6iC'),
('cliente1@correo.com','cli123'),
('jefe@correo.com','jefe123'),
('nuevo@correo.com','$2a$11$cmtGBxllwc7MCzpnKVSWuumiOgCaG6PaKWcN1z9N0bjjnkobbFDzO'),
('test_encript@correo.com','$2a$11$Ci0J2yBltDgQHfjadgkl0OtbcF5pUf97vTq/4Xr0KEU/86l8ybjBe'),
('vendedor1@correo.com','$2a$12$Dgog4VaHqMzhliPVJy1BcOMd6.izEGNeRDtZ.O7SPmBLc6UVthVTG');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `vendedor`
--

DROP TABLE IF EXISTS `vendedor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendedor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `carnet` int(11) NOT NULL,
  `direccion` varchar(100) NOT NULL,
  `fkcodpersona` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_vendedor_persona` (`fkcodpersona`),
  CONSTRAINT `fk_vendedor_persona` FOREIGN KEY (`fkcodpersona`) REFERENCES `persona` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendedor`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `vendedor` WRITE;
/*!40000 ALTER TABLE `vendedor` DISABLE KEYS */;
INSERT INTO `vendedor` VALUES
(1,1001,'Calle 10 #5-33','P002'),
(2,1002,'Carrera 15 #7-20','P004'),
(3,1003,'Avenida 30 #18-09','P006');
/*!40000 ALTER TABLE `vendedor` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Dumping routines for database 'bdfacturas_mariadb_local'
--
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `actualizar_roles_usuario` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_roles_usuario`(
    IN p_email VARCHAR(100),
    IN p_roles_json JSON,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_index INT DEFAULT 0;
    DECLARE v_count INT;
    DECLARE v_idrol INT;
    DECLARE v_roles_json_result TEXT;
    DECLARE v_msg VARCHAR(500);

    IF NOT EXISTS (SELECT 1 FROM usuario WHERE email = p_email) THEN
        SET v_msg = CONCAT('Usuario ', p_email, ' no existe');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    
    DELETE FROM rol_usuario WHERE fkemail = p_email;

    
    SET v_count = JSON_LENGTH(p_roles_json);

    WHILE v_index < v_count DO
        SET v_idrol = JSON_EXTRACT(p_roles_json, CONCAT('$[', v_index, '].fkidrol'));
        INSERT INTO rol_usuario (fkemail, fkidrol) VALUES (p_email, v_idrol);
        SET v_index = v_index + 1;
    END WHILE;

    
    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT('idrol', r.id, 'nombre', r.nombre)
    ), ''), ']')
    INTO v_roles_json_result
    FROM rol_usuario ru
    JOIN rol r ON r.id = ru.fkidrol
    WHERE ru.fkemail = p_email;

    SET p_resultado = CONCAT('{"email":"', p_email, '","roles":', COALESCE(v_roles_json_result, '[]'), '}');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `actualizar_usuario_con_roles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `actualizar_usuario_con_roles`(
    IN p_email VARCHAR(100),
    IN p_contrasena VARCHAR(200),
    IN p_roles JSON,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_index INT DEFAULT 0;
    DECLARE v_count INT;
    DECLARE v_idrol INT;
    DECLARE v_roles_json TEXT;

    
    IF p_contrasena IS NOT NULL AND p_contrasena != '' THEN
        UPDATE usuario SET contrasena = p_contrasena WHERE email = p_email;
    END IF;

    
    DELETE FROM rol_usuario WHERE fkemail = p_email;

    
    SET v_count = JSON_LENGTH(p_roles);

    WHILE v_index < v_count DO
        SET v_idrol = JSON_EXTRACT(p_roles, CONCAT('$[', v_index, '].fkidrol'));
        INSERT INTO rol_usuario (fkemail, fkidrol) VALUES (p_email, v_idrol);
        SET v_index = v_index + 1;
    END WHILE;

    
    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT('idrol', r.id, 'nombre', r.nombre)
    ), ''), ']')
    INTO v_roles_json
    FROM rol_usuario ru
    JOIN rol r ON r.id = ru.fkidrol
    WHERE ru.fkemail = p_email;

    SET p_resultado = CONCAT('{"email":"', p_email, '","roles":', COALESCE(v_roles_json, '[]'), '}');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `consultar_usuario_con_roles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `consultar_usuario_con_roles`(
    IN p_email VARCHAR(100),
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_roles_json TEXT;
    DECLARE v_msg VARCHAR(500);

    IF NOT EXISTS (SELECT 1 FROM usuario WHERE email = p_email) THEN
        SET v_msg = CONCAT('Usuario ', p_email, ' no existe');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT('idrol', r.id, 'nombre', r.nombre)
    ), ''), ']')
    INTO v_roles_json
    FROM rol_usuario ru
    JOIN rol r ON r.id = ru.fkidrol
    WHERE ru.fkemail = p_email;

    SET p_resultado = CONCAT('{"email":"', p_email, '","roles":', COALESCE(v_roles_json, '[]'), '}');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `crear_rutarol` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `crear_rutarol`(
    IN p_fkidruta INT,
    IN p_fkidrol INT,
    OUT p_resultado JSON
)
proc_body: BEGIN
    
    IF NOT EXISTS (SELECT 1 FROM ruta WHERE id = p_fkidruta) THEN
        SET p_resultado = JSON_OBJECT('success', false, 'message', 'La ruta especificada no existe');
        LEAVE proc_body;
    END IF;

    
    IF NOT EXISTS (SELECT 1 FROM rol WHERE id = p_fkidrol) THEN
        SET p_resultado = JSON_OBJECT('success', false, 'message', 'El rol especificado no existe');
        LEAVE proc_body;
    END IF;

    
    IF EXISTS (SELECT 1 FROM rutarol WHERE fkidruta = p_fkidruta AND fkidrol = p_fkidrol) THEN
        SET p_resultado = JSON_OBJECT('success', false, 'message', 'El permiso ya existe');
        LEAVE proc_body;
    END IF;

    INSERT INTO rutarol (fkidruta, fkidrol) VALUES (p_fkidruta, p_fkidrol);
    SET p_resultado = JSON_OBJECT('success', true, 'message', 'Permiso creado exitosamente');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `crear_usuario_con_roles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `crear_usuario_con_roles`(
    IN p_email VARCHAR(100),
    IN p_contrasena VARCHAR(200),
    IN p_roles_json JSON,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_index INT DEFAULT 0;
    DECLARE v_count INT;
    DECLARE v_idrol INT;
    DECLARE v_roles_json TEXT;

    
    INSERT INTO usuario (email, contrasena) VALUES (p_email, p_contrasena);

    
    SET v_count = JSON_LENGTH(p_roles_json);

    WHILE v_index < v_count DO
        SET v_idrol = JSON_EXTRACT(p_roles_json, CONCAT('$[', v_index, '].fkidrol'));
        INSERT INTO rol_usuario (fkemail, fkidrol) VALUES (p_email, v_idrol);
        SET v_index = v_index + 1;
    END WHILE;

    
    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT('idrol', r.id, 'nombre', r.nombre)
    ), ''), ']')
    INTO v_roles_json
    FROM rol_usuario ru
    JOIN rol r ON r.id = ru.fkidrol
    WHERE ru.fkemail = p_email;

    SET p_resultado = CONCAT('{"email":"', p_email, '","roles":', COALESCE(v_roles_json, '[]'), '}');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `eliminar_rutarol` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `eliminar_rutarol`(
    IN p_fkidruta INT,
    IN p_fkidrol INT,
    OUT p_resultado JSON
)
proc_body: BEGIN
    
    IF NOT EXISTS (SELECT 1 FROM rutarol WHERE fkidruta = p_fkidruta AND fkidrol = p_fkidrol) THEN
        SET p_resultado = JSON_OBJECT('success', false, 'message', 'El permiso no existe');
        LEAVE proc_body;
    END IF;

    DELETE FROM rutarol WHERE fkidruta = p_fkidruta AND fkidrol = p_fkidrol;
    SET p_resultado = JSON_OBJECT('success', true, 'message', 'Permiso eliminado exitosamente');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `eliminar_usuario_con_roles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `eliminar_usuario_con_roles`(
    IN p_email VARCHAR(100),
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_msg VARCHAR(500);

    IF NOT EXISTS (SELECT 1 FROM usuario WHERE email = p_email) THEN
        SET v_msg = CONCAT('Usuario ', p_email, ' no existe');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    
    DELETE FROM rol_usuario WHERE fkemail = p_email;
    DELETE FROM usuario WHERE email = p_email;

    SET p_resultado = JSON_OBJECT(
        'mensaje', 'Usuario eliminado exitosamente',
        'email_eliminado', p_email
    );
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `listar_rutarol` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `listar_rutarol`(
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_resultado TEXT;

    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT(
            'fkidruta', rr.fkidruta,
            'ruta', rt.ruta,
            'fkidrol', rr.fkidrol,
            'rol', r.nombre
        )
        ORDER BY rt.ruta, r.nombre
    ), ''), ']')
    INTO v_resultado
    FROM rutarol rr
    JOIN ruta rt ON rt.id = rr.fkidruta
    JOIN rol r ON r.id = rr.fkidrol;

    SET p_resultado = COALESCE(v_resultado, '[]');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `listar_usuarios_con_roles` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `listar_usuarios_con_roles`(
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_resultado TEXT;

    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        CONCAT(
            '{"email":"', sub.email, '"',
            ',"roles":', COALESCE(sub.roles_json, '[]'),
            '}'
        )
    ), ''), ']')
    INTO v_resultado
    FROM (
        SELECT u.email,
            (SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
                JSON_OBJECT('idrol', r.id, 'nombre', r.nombre)
            ), ''), ']')
            FROM rol_usuario ru
            JOIN rol r ON r.id = ru.fkidrol
            WHERE ru.fkemail = u.email
            ) AS roles_json
        FROM usuario u
        ORDER BY u.email
    ) AS sub;

    SET p_resultado = COALESCE(v_resultado, '[]');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_actualizar_factura_y_productosporfactura` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_actualizar_factura_y_productosporfactura`(
    IN p_numero INT,
    IN p_fkidcliente INT,
    IN p_fkidvendedor INT,
    IN p_productos JSON,
    IN p_minimo_detalle INT,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_index INT DEFAULT 0;
    DECLARE v_count INT;
    DECLARE v_codproducto VARCHAR(10);
    DECLARE v_cantidad INT;
    DECLARE v_minimo INT;
    DECLARE v_factura_json TEXT;
    DECLARE v_productos_json TEXT;
    DECLARE v_msg VARCHAR(500);

    IF NOT EXISTS (SELECT 1 FROM factura WHERE numero = p_numero) THEN
        SET v_msg = CONCAT('Factura ', p_numero, ' no existe');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    SET v_minimo = COALESCE(NULLIF(p_minimo_detalle, 0), 1);

    IF p_productos IS NULL OR JSON_LENGTH(p_productos) < v_minimo THEN
        SET v_msg = CONCAT('La factura requiere minimo ', v_minimo, ' producto(s).');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    
    DELETE FROM productosporfactura WHERE fknumfactura = p_numero;

    
    SET v_count = JSON_LENGTH(p_productos);

    WHILE v_index < v_count DO
        SET v_codproducto = JSON_UNQUOTE(JSON_EXTRACT(p_productos, CONCAT('$[', v_index, '].codigo')));
        SET v_cantidad = JSON_EXTRACT(p_productos, CONCAT('$[', v_index, '].cantidad'));

        INSERT INTO productosporfactura (fknumfactura, fkcodproducto, cantidad, subtotal)
        VALUES (p_numero, v_codproducto, v_cantidad, 0);

        SET v_index = v_index + 1;
    END WHILE;

    
    UPDATE factura
    SET fkidcliente = p_fkidcliente,
        fkidvendedor = p_fkidvendedor
    WHERE numero = p_numero;

    
    SELECT CONCAT(
        '{"numero":', f.numero,
        ',"fecha":"', DATE_FORMAT(f.fecha, '%Y-%m-%dT%H:%i:%s'), '"',
        ',"total":', f.total,
        ',"estado":"', f.estado, '"',
        ',"fkidcliente":', f.fkidcliente,
        ',"fkidvendedor":', f.fkidvendedor, '}'
    ) INTO v_factura_json
    FROM factura f WHERE f.numero = p_numero;

    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT(
            'codigo_producto', pf.fkcodproducto,
            'nombre_producto', pr.nombre,
            'cantidad', pf.cantidad,
            'valorunitario', pr.valorunitario,
            'subtotal', pf.subtotal
        )
    ), ''), ']')
    INTO v_productos_json
    FROM productosporfactura pf
    JOIN producto pr ON pr.codigo = pf.fkcodproducto
    WHERE pf.fknumfactura = p_numero;

    SET p_resultado = CONCAT('{"factura":', v_factura_json, ',"productos":', COALESCE(v_productos_json, '[]'), '}');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_anular_factura` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_anular_factura`(
    IN p_numero INT,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_total DECIMAL(18,2);
    DECLARE v_cantidad_productos INT;
    DECLARE v_estado VARCHAR(10);
    DECLARE v_msg VARCHAR(500);

    
    IF NOT EXISTS (SELECT 1 FROM factura WHERE numero = p_numero) THEN
        SET v_msg = CONCAT('Factura ', p_numero, ' no existe');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    
    SELECT estado INTO v_estado FROM factura WHERE numero = p_numero;
    IF v_estado = 'anulada' THEN
        SET v_msg = CONCAT('Factura ', p_numero, ' ya está anulada');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    
    UPDATE producto p
    JOIN productosporfactura pf ON p.codigo = pf.fkcodproducto
    SET p.stock = p.stock + pf.cantidad
    WHERE pf.fknumfactura = p_numero;

    
    SELECT total INTO v_total FROM factura WHERE numero = p_numero;
    SELECT COUNT(*) INTO v_cantidad_productos FROM productosporfactura WHERE fknumfactura = p_numero;

    
    UPDATE factura SET estado = 'anulada' WHERE numero = p_numero;

    
    SET p_resultado = JSON_OBJECT(
        'mensaje', 'Factura anulada exitosamente',
        'numero_anulado', p_numero,
        'total_anulado', v_total,
        'productos_afectados', v_cantidad_productos,
        'estado', 'anulada'
    );
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_borrar_factura_y_productosporfactura` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_borrar_factura_y_productosporfactura`(
    IN p_numero INT,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_total DECIMAL(18,2);
    DECLARE v_cantidad_productos INT;
    DECLARE v_msg VARCHAR(500);

    IF NOT EXISTS (SELECT 1 FROM factura WHERE numero = p_numero) THEN
        SET v_msg = CONCAT('Factura ', p_numero, ' no existe');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    
    SELECT COUNT(*) INTO v_cantidad_productos
    FROM productosporfactura WHERE fknumfactura = p_numero;

    SELECT total INTO v_total FROM factura WHERE numero = p_numero;

    
    
    DELETE FROM factura WHERE numero = p_numero;

    
    SET p_resultado = JSON_OBJECT(
        'mensaje', 'Factura eliminada exitosamente',
        'numero_eliminado', p_numero,
        'total_eliminado', v_total,
        'productos_eliminados', v_cantidad_productos
    );
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_consultar_factura_y_productosporfactura` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_consultar_factura_y_productosporfactura`(
    IN p_numero INT,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_detalle_json TEXT;
    DECLARE v_msg VARCHAR(500);

    IF NOT EXISTS (SELECT 1 FROM factura WHERE numero = p_numero) THEN
        SET v_msg = CONCAT('Factura ', p_numero, ' no existe');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT(
            'codigo_producto', d.fkcodproducto,
            'nombre_producto', p.nombre,
            'cantidad', d.cantidad,
            'valorunitario', p.valorunitario,
            'subtotal', d.subtotal
        )
    ), ''), ']')
    INTO v_detalle_json
    FROM productosporfactura d
    INNER JOIN producto p ON p.codigo = d.fkcodproducto
    WHERE d.fknumfactura = p_numero;

    SELECT CONCAT(
        '{"factura":{"numero":', f.numero,
        ',"fecha":"', DATE_FORMAT(f.fecha, '%Y-%m-%dT%H:%i:%s'), '"',
        ',"total":', f.total,
        ',"estado":"', f.estado, '"',
        ',"fkidcliente":', f.fkidcliente,
        ',"nombre_cliente":"', pc.nombre, '"',
        ',"fkidvendedor":', f.fkidvendedor,
        ',"nombre_vendedor":"', pv.nombre, '"',
        '},"productos":', COALESCE(v_detalle_json, '[]'),
        '}'
    ) INTO p_resultado
    FROM factura f
    JOIN cliente c ON c.id = f.fkidcliente
    JOIN persona pc ON pc.codigo = c.fkcodpersona
    JOIN vendedor v ON v.id = f.fkidvendedor
    JOIN persona pv ON pv.codigo = v.fkcodpersona
    WHERE f.numero = p_numero;
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_insertar_factura_y_productosporfactura` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_insertar_factura_y_productosporfactura`(
    IN p_fkidcliente INT,
    IN p_fkidvendedor INT,
    IN p_productos JSON,
    IN p_minimo_detalle INT,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_numfactura INT;
    DECLARE v_index INT DEFAULT 0;
    DECLARE v_count INT;
    DECLARE v_codproducto VARCHAR(10);
    DECLARE v_cantidad INT;
    DECLARE v_minimo INT;
    DECLARE v_factura_json TEXT;
    DECLARE v_productos_json TEXT;
    DECLARE v_msg VARCHAR(500);

    SET v_minimo = COALESCE(NULLIF(p_minimo_detalle, 0), 1);

    IF p_productos IS NULL OR JSON_LENGTH(p_productos) < v_minimo THEN
        SET v_msg = CONCAT('La factura requiere minimo ', v_minimo, ' producto(s).');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    
    INSERT INTO factura (fkidcliente, fkidvendedor, total)
    VALUES (p_fkidcliente, p_fkidvendedor, 0);

    SET v_numfactura = LAST_INSERT_ID();
    SET v_count = JSON_LENGTH(p_productos);

    
    
    WHILE v_index < v_count DO
        SET v_codproducto = JSON_UNQUOTE(JSON_EXTRACT(p_productos, CONCAT('$[', v_index, '].codigo')));
        SET v_cantidad = JSON_EXTRACT(p_productos, CONCAT('$[', v_index, '].cantidad'));

        INSERT INTO productosporfactura (fknumfactura, fkcodproducto, cantidad, subtotal)
        VALUES (v_numfactura, v_codproducto, v_cantidad, 0);

        SET v_index = v_index + 1;
    END WHILE;

    
    SELECT CONCAT(
        '{"numero":', f.numero,
        ',"fecha":"', DATE_FORMAT(f.fecha, '%Y-%m-%dT%H:%i:%s'), '"',
        ',"total":', f.total,
        ',"estado":"', f.estado, '"',
        ',"fkidcliente":', f.fkidcliente,
        ',"fkidvendedor":', f.fkidvendedor, '}'
    ) INTO v_factura_json
    FROM factura f WHERE f.numero = v_numfactura;

    SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
        JSON_OBJECT(
            'codigo_producto', pf.fkcodproducto,
            'nombre_producto', pr.nombre,
            'cantidad', pf.cantidad,
            'valorunitario', pr.valorunitario,
            'subtotal', pf.subtotal
        )
    ), ''), ']')
    INTO v_productos_json
    FROM productosporfactura pf
    JOIN producto pr ON pr.codigo = pf.fkcodproducto
    WHERE pf.fknumfactura = v_numfactura;

    SET p_resultado = CONCAT('{"factura":', v_factura_json, ',"productos":', COALESCE(v_productos_json, '[]'), '}');
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_listar_facturas_y_productosporfactura` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_listar_facturas_y_productosporfactura`(
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_result TEXT DEFAULT '';
    DECLARE v_factura TEXT;
    DECLARE v_detalle TEXT;
    DECLARE v_done INT DEFAULT FALSE;
    DECLARE v_numero INT;
    DECLARE cur CURSOR FOR SELECT numero FROM factura ORDER BY numero;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_numero;
        IF v_done THEN LEAVE read_loop; END IF;

        SELECT CONCAT('[', COALESCE(GROUP_CONCAT(
            JSON_OBJECT(
                'codigo_producto', d.fkcodproducto,
                'nombre_producto', p.nombre,
                'cantidad', d.cantidad,
                'valorunitario', p.valorunitario,
                'subtotal', d.subtotal
            )
        ), ''), ']')
        INTO v_detalle
        FROM productosporfactura d
        INNER JOIN producto p ON p.codigo = d.fkcodproducto
        WHERE d.fknumfactura = v_numero;

        SELECT CONCAT(
            '{"numero":', f.numero,
            ',"fecha":"', DATE_FORMAT(f.fecha, '%Y-%m-%dT%H:%i:%s'), '"',
            ',"total":', f.total,
            ',"fkidcliente":', f.fkidcliente,
            ',"nombre_cliente":"', pc.nombre, '"',
            ',"fkidvendedor":', f.fkidvendedor,
            ',"nombre_vendedor":"', pv.nombre, '"',
            ',"productos":', COALESCE(v_detalle, '[]'),
            '}'
        )
        INTO v_factura
        FROM factura f
        JOIN cliente c ON c.id = f.fkidcliente
        JOIN persona pc ON pc.codigo = c.fkcodpersona
        JOIN vendedor v ON v.id = f.fkidvendedor
        JOIN persona pv ON pv.codigo = v.fkcodpersona
        WHERE f.numero = v_numero;

        IF v_result != '' THEN SET v_result = CONCAT(v_result, ','); END IF;
        SET v_result = CONCAT(v_result, v_factura);
    END LOOP;
    CLOSE cur;

    IF v_result = '' THEN
        SET p_resultado = '[]';
    ELSE
        SET p_resultado = CONCAT('[', v_result, ']');
    END IF;
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
/*!50003 DROP PROCEDURE IF EXISTS `verificar_acceso_ruta` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_uca1400_ai_ci */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `verificar_acceso_ruta`(
    IN p_email VARCHAR(100),
    IN p_fkidruta INT,
    OUT p_resultado JSON
)
BEGIN
    DECLARE v_tiene_acceso BOOLEAN DEFAULT FALSE;

    SELECT EXISTS(
        SELECT 1
        FROM usuario u
        INNER JOIN rol_usuario ur ON u.email = ur.fkemail
        INNER JOIN rutarol rr ON ur.fkidrol = rr.fkidrol
        WHERE u.email = p_email AND rr.fkidruta = p_fkidruta
    ) INTO v_tiene_acceso;

    SET p_resultado = JSON_OBJECT(
        'tiene_acceso', v_tiene_acceso,
        'email', p_email,
        'fkidruta', p_fkidruta
    );
END
;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-08-08  6:12:54
