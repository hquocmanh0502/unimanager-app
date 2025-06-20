-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: university_management
-- ------------------------------------------------------
-- Server version	8.0.37

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `assignments`
--

DROP TABLE IF EXISTS `assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignments` (
  `assignment_id` varchar(9) NOT NULL,
  `class_id` varchar(9) NOT NULL,
  `teacher_id` varchar(10) NOT NULL,
  `assigned_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`assignment_id`),
  UNIQUE KEY `class_id` (`class_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `assignments_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`) ON DELETE CASCADE,
  CONSTRAINT `assignments_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`teacher_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assignments`
--

LOCK TABLES `assignments` WRITE;
/*!40000 ALTER TABLE `assignments` DISABLE KEYS */;
INSERT INTO `assignments` VALUES ('ASN00001','CLS42815','TCH44297','2025-06-08 22:14:05'),('ASN00002','CLS91635','TCH94486','2025-06-08 22:13:14'),('ASN00003','CLS49507','TCH62958','2025-06-08 22:13:30'),('ASN00004','CLS41988','TCH62958','2025-06-12 16:24:21'),('ASN00005','CLS21622','TCH62958','2025-06-13 08:37:35'),('ASN00006','CLS51506','TCH62958','2025-06-13 08:21:56'),('ASN00007','CLS66001','TCH62958','2025-06-13 08:22:00'),('ASN00008','CLS17402','TCH62958','2025-06-13 08:37:50'),('ASN00009','CLS11339','TCH62958','2025-06-13 08:38:01'),('ASN00010','CLS37605','TCH72148','2025-06-13 08:38:42'),('ASN00013','CLS10904','TCH62958','2025-06-16 12:46:05'),('ASN76244','CLS77062','TCH72148','2025-06-16 12:54:17'),('ASN76245','CLS96459','TCH09803','2025-06-17 22:36:40'),('ASN76246','CLS51815','TCH09803','2025-06-17 23:24:30'),('ASN76247','CLS69615','TCH94486','2025-06-17 23:24:30'),('ASN76248','CLS88073','TCH94486','2025-06-18 09:40:06'),('ASN76249','CLS54577','TCH44297','2025-06-18 09:41:11'),('ASN76250','CLS57785','TCH44297','2025-06-18 09:41:11'),('ASN76251','CLS00003','TCH44297','2025-06-20 01:00:02'),('ASN76252','CLS00004','TCH44297','2025-06-20 01:00:02'),('ASN76253','CLS33983','TCH62958','2025-06-20 01:00:11'),('ASN76254','CLS43099','TCH62958','2025-06-20 01:00:11'),('ASN76255','CLS54935','TCH62958','2025-06-20 01:00:11');
/*!40000 ALTER TABLE `assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_coefficients`
--

DROP TABLE IF EXISTS `class_coefficients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_coefficients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `year` varchar(9) NOT NULL,
  `student_range` varchar(20) NOT NULL,
  `coefficient` decimal(3,1) NOT NULL DEFAULT '0.0',
  `is_standard` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `year` (`year`,`student_range`)
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_coefficients`
--

LOCK TABLES `class_coefficients` WRITE;
/*!40000 ALTER TABLE `class_coefficients` DISABLE KEYS */;
INSERT INTO `class_coefficients` VALUES (11,'2025-2026','<20 sinh viên',-0.3,0),(12,'2025-2026','20-29 sinh viên',-0.2,0),(13,'2025-2026','30-39 sinh viên',-0.1,0),(14,'2025-2026','40-49 sinh viên',0.0,1),(15,'2025-2026','50-59 sinh viên',0.1,0),(16,'2025-2026','60-69 sinh viên',0.2,0),(17,'2025-2026','70-79 sinh viên',0.3,0),(18,'2025-2026','80-89 sinh viên',0.4,0),(19,'2025-2026','90-99 sinh viên',0.5,0),(20,'2025-2026','>=100 sinh viên',0.6,0),(73,'2020-2021','<20 sinh viên',-0.4,0),(74,'2020-2021','20-29 sinh viên',-0.3,0),(75,'2020-2021','30-39 sinh viên',-0.2,0),(76,'2020-2021','40-49 sinh viên',-0.1,0),(77,'2020-2021','50-59 sinh viên',0.0,1),(78,'2020-2021','60-69 sinh viên',0.1,0),(79,'2020-2021','70-79 sinh viên',0.2,0),(80,'2020-2021','80-89 sinh viên',0.3,0),(81,'2020-2021','90-99 sinh viên',0.4,0),(82,'2020-2021','>=100 sinh viên',0.5,0),(93,'2029-2030','<20 sinh viên',-0.4,0),(94,'2029-2030','20-29 sinh viên',-0.3,0),(95,'2029-2030','30-39 sinh viên',-0.2,0),(96,'2029-2030','40-49 sinh viên',-0.1,0),(97,'2029-2030','50-59 sinh viên',0.0,1),(98,'2029-2030','60-69 sinh viên',0.1,0),(99,'2029-2030','70-79 sinh viên',0.2,0),(100,'2029-2030','80-89 sinh viên',0.3,0),(101,'2029-2030','90-99 sinh viên',0.4,0),(102,'2029-2030','>=100 sinh viên',0.5,0),(113,'2028-2029','<20 sinh viên',-0.4,0),(114,'2028-2029','20-29 sinh viên',-0.3,0),(115,'2028-2029','30-39 sinh viên',-0.2,0),(116,'2028-2029','40-49 sinh viên',-0.1,0),(117,'2028-2029','50-59 sinh viên',0.0,1),(118,'2028-2029','60-69 sinh viên',0.1,0),(119,'2028-2029','70-79 sinh viên',0.2,0),(120,'2028-2029','80-89 sinh viên',0.3,0),(121,'2028-2029','90-99 sinh viên',0.4,0),(122,'2028-2029','>=100 sinh viên',0.5,0),(123,'2021-2022','<20 sinh viên',-0.5,0),(124,'2021-2022','20-29 sinh viên',-0.4,0),(125,'2021-2022','30-39 sinh viên',-0.3,0),(126,'2021-2022','40-49 sinh viên',-0.2,0),(127,'2021-2022','50-59 sinh viên',-0.1,0),(128,'2021-2022','60-69 sinh viên',0.0,1),(129,'2021-2022','70-79 sinh viên',0.1,0),(130,'2021-2022','80-89 sinh viên',0.2,0),(131,'2021-2022','90-99 sinh viên',0.3,0),(132,'2021-2022','>=100 sinh viên',0.4,0);
/*!40000 ALTER TABLE `class_coefficients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_enrollments`
--

DROP TABLE IF EXISTS `class_enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_enrollments` (
  `class_id` varchar(9) NOT NULL,
  `enrolled_students` int NOT NULL DEFAULT '0',
  `last_updated` date DEFAULT NULL,
  PRIMARY KEY (`class_id`),
  CONSTRAINT `class_enrollments_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `classes` (`class_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_enrollments`
--

LOCK TABLES `class_enrollments` WRITE;
/*!40000 ALTER TABLE `class_enrollments` DISABLE KEYS */;
INSERT INTO `class_enrollments` VALUES ('CLS00003',42,'2025-06-15'),('CLS00004',35,'2025-06-15'),('CLS00005',47,'2025-06-15'),('CLS00006',39,'2025-06-15'),('CLS10904',44,'2025-06-15'),('CLS11339',31,'2025-06-15'),('CLS14755',50,'2025-06-15'),('CLS17402',36,'2025-06-15'),('CLS21622',48,'2025-06-15'),('CLS32765',45,'2025-06-15'),('CLS33983',40,'2025-06-15'),('CLS34207',37,'2025-06-16'),('CLS37605',43,'2025-06-15'),('CLS41988',46,'2025-06-15'),('CLS42815',38,'2025-06-15'),('CLS43099',41,'2025-06-15'),('CLS49507',34,'2025-06-15'),('CLS50138',49,'2025-06-15'),('CLS50724',30,'2025-06-15'),('CLS51506',44,'2025-06-15'),('CLS51815',35,'2025-06-15'),('CLS54577',42,'2025-06-15'),('CLS54935',36,'2025-06-15'),('CLS57053',33,'2025-06-15'),('CLS57785',45,'2025-06-15'),('CLS57918',31,'2025-06-15'),('CLS66001',48,'2025-06-15'),('CLS66772',40,'2025-06-15'),('CLS69568',37,'2025-06-15'),('CLS69615',43,'2025-06-15'),('CLS77062',32,'2025-06-15'),('CLS82536',34,'2025-06-15'),('CLS83661',49,'2025-06-15'),('CLS84308',30,'2025-06-15'),('CLS88073',44,'2025-06-15'),('CLS89601',38,'2025-06-15'),('CLS91635',47,'2025-06-15'),('CLS94139',35,'2025-06-15'),('CLS96157',42,'2025-06-15'),('CLS96459',39,'2025-06-15'),('CLS96841',50,'2025-06-15'),('CLS98826',36,'2025-06-15');
/*!40000 ALTER TABLE `class_enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classes`
--

DROP TABLE IF EXISTS `classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classes` (
  `class_id` varchar(10) NOT NULL,
  `semester_id` varchar(9) NOT NULL,
  `module_id` varchar(10) NOT NULL,
  `class_name` varchar(100) NOT NULL,
  `num_students` int NOT NULL,
  PRIMARY KEY (`class_id`),
  KEY `semester_id` (`semester_id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `classes_ibfk_1` FOREIGN KEY (`semester_id`) REFERENCES `semesters` (`semester_id`),
  CONSTRAINT `classes_ibfk_2` FOREIGN KEY (`module_id`) REFERENCES `course_modules` (`module_id`),
  CONSTRAINT `classes_chk_1` CHECK ((`num_students` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classes`
--

LOCK TABLES `classes` WRITE;
/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
INSERT INTO `classes` VALUES ('CLS00003','HK2-28','MOD29934','CESMOD29934-LT-7-16(N03)',50),('CLS00004','HK2-28','MOD29934','CESMOD29934-LT-7-16(N04)',50),('CLS00005','HK2-28','MOD29934','CESMOD29934-LT-7-16(N05)',50),('CLS00006','HK2-28','MOD29934','CESMOD29934-LT-7-16(N06)',50),('CLS01421','HK1-25','MOD93925','FBEMOD93925-LT-6-2024-2025(N04)',30),('CLS10904','HK1-25','MOD93923','CESMOD93923-LT-3-17(N05)',40),('CLS11339','HK1-25','MOD93923','CESMOD93923-LT-3-17(N02)',40),('CLS14755','HK1-25','MOD93927','MOD93927-LT-3-17(N06)',40),('CLS17402','HK3-22','MOD29934','CESMOD29934-LT-7-22(N02)',40),('CLS21622','HK3-22','MOD93923','MOD93923-LT-3-22(N03)',40),('CLS32007','HK1-25','MOD93925','FBEMOD93925-LT-6-2024-2025(N03)',30),('CLS32765','HK1-25','MOD93926','MOD93926-LT-5-17(N02)',40),('CLS33983','HK2-28','MOD29934','CESMOD29934-LT-7-16(N04)',50),('CLS34207','HK1-25','MOD93927','MOD93927-LT-3-17(N05)',40),('CLS37605','HK1-25','MOD93925','MOD93925-LT-6-17(N02)',40),('CLS41988','HK3-22','MOD93923','MOD93923-LT-3-22(N02)',40),('CLS42782','HK1-25','MOD93925','FBEMOD93925-LT-6-2024-2025(N05)',30),('CLS42815','HK1-25','MOD93923','CESMOD93923-LT-3-17(N04)',40),('CLS43099','HK2-28','MOD29934','CESMOD29934-LT-7-16(N03)',50),('CLS49507','HK3-22','MOD29934','CESMOD29934-LT-7-22(N04)',40),('CLS50138','HK1-25','MOD93923','CESMOD93923-LT-3-17(N01)',40),('CLS50724','HK1-25','MOD93927','MOD93927-LT-3-17(N02)',40),('CLS51506','HK1-22','MOD93927','MOD93927-LT-3-22(N01)',40),('CLS51815','HK3-22','MOD29934','CESMOD29934-LT-7-22(N05)',40),('CLS53615','HK1-25','MOD93925','FBEMOD93925-LT-6-2024-2025(N02)',30),('CLS54577','HK1-25','MOD93927','MOD93927-LT-3-17(N04)',40),('CLS54935','HK2-28','MOD29934','CESMOD29934-LT-7-16(N02)',50),('CLS57053','HK1-22','MOD93925','MOD93925-LT-6-22(N04)',50),('CLS57785','HK1-25','MOD93927','MOD93927-LT-3-17(N07)',40),('CLS57918','HK1-25','MOD93923','CESMOD93923-LT-3-17(N03)',40),('CLS66001','HK1-22','MOD93927','MOD93927-LT-3-22(N03)',40),('CLS66772','HK1-25','MOD93926','MOD93926-LT-5-17(N03)',40),('CLS69568','HK1-25','MOD93926','MOD93926-LT-5-17(N01)',40),('CLS69615','HK3-22','MOD93923','MOD93923-LT-3-22(N01)',40),('CLS77062','HK1-22','MOD93925','MOD93925-LT-6-22(N01)',50),('CLS82536','HK1-22','MOD93925','MOD93925-LT-6-22(N02)',50),('CLS83661','HK3-22','MOD29934','CESMOD29934-LT-7-22(N01)',40),('CLS84308','HK2-28','MOD29934','CESMOD29934-LT-7-16(N01)',50),('CLS88073','HK1-22','MOD93927','MOD93927-LT-3-22(N02)',40),('CLS89601','HK1-25','MOD93927','MOD93927-LT-3-17(N03)',40),('CLS91635','HK1-25','MOD93923','CESMOD93923-LT-3-17(N03)',40),('CLS94139','HK3-22','MOD29934','CESMOD29934-LT-7-22(N03)',40),('CLS96157','HK1-22','MOD93925','MOD93925-LT-6-22(N03)',50),('CLS96459','HK1-25','MOD93923','CESMOD93923-LT-3-17(N01)',40),('CLS96783','HK1-25','MOD93925','FBEMOD93925-LT-6-2024-2025(N01)',30),('CLS96841','HK1-25','MOD93925','MOD93925-LT-6-17(N03)',40),('CLS98826','HK1-25','MOD93925','MOD93925-LT-6-17(N01)',40);
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_modules`
--

DROP TABLE IF EXISTS `course_modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_modules` (
  `module_id` varchar(10) NOT NULL,
  `module_name` varchar(100) NOT NULL,
  `credits` int NOT NULL,
  `coefficient` float NOT NULL DEFAULT '1',
  `periods` int NOT NULL,
  `dept_id` varchar(10) NOT NULL,
  PRIMARY KEY (`module_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `course_modules_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `departments` (`dept_id`),
  CONSTRAINT `course_modules_chk_1` CHECK ((`credits` > 0)),
  CONSTRAINT `course_modules_chk_2` CHECK ((`periods` > 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_modules`
--

LOCK TABLES `course_modules` WRITE;
/*!40000 ALTER TABLE `course_modules` DISABLE KEYS */;
INSERT INTO `course_modules` VALUES ('MOD29934','Lập trình Python',7,1,60,'DEPT2321'),('MOD93923','Cơ sở dữ liệu',3,1.5,60,'DEPT2321'),('MOD93925','Quản trị hay kinh tế',6,1.5,50,'DEPT4849'),('MOD93926','Quản trị kd',5,1.5,60,'DEPT4849'),('MOD93927','Toán rời rạc',3,1.5,40,'DEPT2321'),('MOD93928','Pháp luật đại cương',3,1.5,45,'DEPT2321'),('MOD93929','Đệ nhất phở',5,1.5,75,'DEPT2321'),('MOD93930','Lập trình C',3,1.5,45,'DEPT2321');
/*!40000 ALTER TABLE `course_modules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `degrees`
--

DROP TABLE IF EXISTS `degrees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `degrees` (
  `degree_id` varchar(10) NOT NULL,
  `degree_name` varchar(100) NOT NULL,
  `degree_abbr` varchar(10) NOT NULL,
  `coefficient` float NOT NULL DEFAULT '1',
  PRIMARY KEY (`degree_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `degrees`
--

LOCK TABLES `degrees` WRITE;
/*!40000 ALTER TABLE `degrees` DISABLE KEYS */;
INSERT INTO `degrees` VALUES ('DEG12238','Thạc sĩ','ThS',1.5),('DEG18331','ABC','sss',1.6),('DEG21434','Phó Giáo sư','PGS',2),('DEG34993','Tiến sĩ','TS',1.7),('DEG82838','Đại học','ĐH',1.3),('DEG92138','Giáo sư','GS',2.5);
/*!40000 ALTER TABLE `degrees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `dept_id` varchar(10) NOT NULL,
  `dept_name` varchar(100) NOT NULL,
  `dept_abbr` varchar(10) NOT NULL,
  `dept_description` text,
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
INSERT INTO `departments` VALUES ('DEPT2321','Khoa Công nghệ Thông tin','CES','Quản lý các ngành liên quan đến CNTT'),('DEPT4847','Khoa Kinh tế','KT','Quản lý các ngành liên quan đến Kinh tế'),('DEPT4849','Khoa Kinh tế kinh doanh','FBE','Quản lý các nghành liên quan đến KTKD');
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `semesters`
--

DROP TABLE IF EXISTS `semesters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `semesters` (
  `semester_id` varchar(9) NOT NULL,
  `semester_name` varchar(50) NOT NULL,
  `year` varchar(9) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  PRIMARY KEY (`semester_id`),
  CONSTRAINT `semesters_chk_1` CHECK ((`start_date` < `end_date`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `semesters`
--

LOCK TABLES `semesters` WRITE;
/*!40000 ALTER TABLE `semesters` DISABLE KEYS */;
INSERT INTO `semesters` VALUES ('HK1-22','Học kỳ 1','2021-2022','2021-01-14','2021-03-17'),('HK1-25','Học kỳ 1','2024-2025','2024-06-06','2025-06-09'),('HK2-28','Học kỳ 2','2027-2028','2027-06-17','2028-06-27'),('HK3-22','Học kỳ 3','2021-2022','2021-06-23','2022-06-29');
/*!40000 ALTER TABLE `semesters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher_coefficients`
--

DROP TABLE IF EXISTS `teacher_coefficients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher_coefficients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `degree_id` varchar(10) NOT NULL,
  `year` varchar(9) NOT NULL,
  `coefficient` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `degree_id` (`degree_id`,`year`),
  CONSTRAINT `teacher_coefficients_ibfk_1` FOREIGN KEY (`degree_id`) REFERENCES `degrees` (`degree_id`),
  CONSTRAINT `teacher_coefficients_chk_1` CHECK ((`coefficient` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher_coefficients`
--

LOCK TABLES `teacher_coefficients` WRITE;
/*!40000 ALTER TABLE `teacher_coefficients` DISABLE KEYS */;
INSERT INTO `teacher_coefficients` VALUES (16,'DEG82838','2025-2026',1.3),(17,'DEG12238','2025-2026',1.5),(18,'DEG34993','2025-2026',1.7),(19,'DEG21434','2025-2026',2),(20,'DEG92138','2025-2026',2.5),(28,'DEG82838','2020-2021',1.3),(29,'DEG12238','2020-2021',1.5),(30,'DEG34993','2020-2021',1.7),(31,'DEG21434','2020-2021',2),(32,'DEG92138','2020-2021',2.5),(33,'DEG82838','2021-2022',1.3),(34,'DEG12238','2021-2022',1.5),(35,'DEG34993','2021-2022',1.9),(36,'DEG21434','2021-2022',2),(37,'DEG92138','2021-2022',2.5),(38,'DEG82838','2026-2027',1.3),(39,'DEG12238','2026-2027',1.5),(40,'DEG34993','2026-2027',1.7),(41,'DEG21434','2026-2027',2),(42,'DEG92138','2026-2027',2.5),(43,'DEG82838','2029-2030',1.3),(44,'DEG12238','2029-2030',1.5),(45,'DEG34993','2029-2030',1.7),(46,'DEG21434','2029-2030',2),(47,'DEG92138','2029-2030',2.5),(48,'DEG82838','2028-2029',1.3),(49,'DEG12238','2028-2029',1.5),(50,'DEG34993','2028-2029',1.7),(51,'DEG21434','2028-2029',2),(52,'DEG92138','2028-2029',2.5),(53,'DEG82838','2022-2023',1.3),(54,'DEG12238','2022-2023',1.5),(55,'DEG34993','2022-2023',1.7),(56,'DEG21434','2022-2023',2),(57,'DEG92138','2022-2023',2.5),(58,'DEG82838','2024-2025',1.3),(59,'DEG12238','2024-2025',1.5),(60,'DEG34993','2024-2025',1.7),(61,'DEG21434','2024-2025',2),(62,'DEG92138','2024-2025',2.5),(63,'DEG18331','2028-2029',1.6),(69,'DEG18331','2025-2026',1.6);
/*!40000 ALTER TABLE `teacher_coefficients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` varchar(10) DEFAULT NULL,
  `full_name` varchar(100) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `degree_id` varchar(10) DEFAULT NULL,
  `dept_id` varchar(10) DEFAULT NULL,
  `teacher_coefficient` float NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `teacher_id` (`teacher_id`),
  KEY `degree_id` (`degree_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`degree_id`) REFERENCES `degrees` (`degree_id`),
  CONSTRAINT `teachers_ibfk_2` FOREIGN KEY (`dept_id`) REFERENCES `departments` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (6,'TCH62958','Hoàng Quốc Mạnh','2004-05-02','0343848339','manh@gmail.com','DEG34993','DEPT2321',1.7),(7,'TCH72148','Trần Cường An','1981-05-05','2994834989','an@gmail.com','DEG21434','DEPT4849',2),(8,'TCH09803','A chẻng','2026-05-13','0329498939','cheng@gmail.com','DEG92138','DEPT2321',2.5),(10,'TCH94486','Hoàng Quốc Đẹp Trai','2024-06-13','9430838311','deptrai@gmail.com','DEG21434','DEPT2321',2),(16,'TCH94393','Trần Thị B','1990-03-15','0916123456','tranthib@example.com','DEG12238','DEPT4847',1.5),(17,'TCH44297','Dương Thị Quỳnh Anh','2023-06-22','0384384388','anh@gmail.com','DEG92138','DEPT2321',2.5),(18,'TCH26361','Nguyễn Hoàng Bách','2003-06-14','0938883493','bach@gmail.com','DEG21434','DEPT2321',2),(19,'TCH29087','Trần Tuấn Anh','2009-06-18','0248383349','tuananh@gmail.com','DEG21434','DEPT4847',2);
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teaching_rate`
--

DROP TABLE IF EXISTS `teaching_rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teaching_rate` (
  `id` int NOT NULL AUTO_INCREMENT,
  `year` varchar(9) NOT NULL,
  `amount_per_period` decimal(10,2) NOT NULL DEFAULT '0.00',
  `setup_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `year` (`year`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teaching_rate`
--

LOCK TABLES `teaching_rate` WRITE;
/*!40000 ALTER TABLE `teaching_rate` DISABLE KEYS */;
INSERT INTO `teaching_rate` VALUES (1,'2020-2021',210000.00,'2025-06-13'),(2,'2021-2022',200000.00,'2025-06-13'),(6,'2026-2027',400000.00,'2025-06-12'),(8,'2027-2028',600000.00,'2025-06-13'),(9,'2025-2026',500000.00,'2025-06-12'),(10,'2023-2024',600000.00,'2025-06-12'),(11,'2028-2029',100000.00,'2025-06-13'),(15,'2024-2025',100000.00,'2025-06-20');
/*!40000 ALTER TABLE `teaching_rate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` varchar(10) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` varchar(20) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('ACCT12345','aa','aa','Accountant'),('ADMIN','admin','admin','Admin'),('DEPT2321','a','a','Department'),('TCH09803','TCH09803','default123','Teacher'),('TCH26361','TCH26361','Manhdz2k4','Teacher'),('TCH29087','TCH29087','default123','Teacher'),('TCH44297','TCH44297','Manhdz2k4','Teacher'),('TCH62958','TCH62958','manhdz2k4','Teacher'),('TCH72148','TCH72148','default123','Teacher');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-20 22:03:39
