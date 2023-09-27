
-- prepares a MySQL server for the project PiyasaFashion

CREATE DATABASE IF NOT EXISTS Dilsebo_shop;
CREATE USER IF NOT EXISTS 'piyasa_dev'@'localhost' IDENTIFIED BY 'piyasa_dev_pwd';
GRANT ALL PRIVILEGES ON `Dilsebo_shop`.* TO 'piyasa_dev'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'piyasa_dev'@'localhost';
FLUSH PRIVILEGES;
