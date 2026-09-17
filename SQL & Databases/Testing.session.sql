----Create users table
CREATE TABLE IF NOT EXISTS users (
id INTEGER  PRIMARY KEY AUTOINCREMENT,
name VARCHAR (50)  NOT NULL ,
email VARCHAR (200) NOT NULL,
national_number VARCHAR (14)  NOT NULL UNIQUE, 
accounts_number INTEGER , --not correct
age INTEGER NOT NULL 
);

----Create accounts table
CREATE TABLE IF NOT EXISTS accounts (
id INTEGER  PRIMARY KEY AUTOINCREMENT, 
user_id INTEGER  NOT NULL,
type TEXT  NOT NULL,
money DECIMAL(12,2)  DEFAULT 0 ,
dept DECIMAL(12,2) DEFAULT 0,
expire_date DATE ,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

----Create compaines table
CREATE TABLE IF NOT EXISTS companies(
id INTEGER  PRIMARY KEY AUTOINCREMENT, 
name VARCHAR (100) NOT NULL UNIQUE, 
money DECIMAL(12,2) DEFAULT 0 ,
share_ratio REAL NOT NULL,
profit_margin REAL NOT NULL
);

INSERT INTO users 
  (name , email ,national_number , accounts_number,age) VALUES  
  ("Bisto" , "Quere@bisto.com" , "30130126667118" , 1 , 21);

INSERT INTO accounts 
  (user_id , type , money , expire_date) VALUES
  (1,"Saving_Account" , 20000.00 , '2030-12-18');

INSERT INTO companies 
  (name , money , profit_margin , share_ratio) VALUES
  ("Startup_gain" , 3500000 , 5.6 , 10.0);

-- 1. Inserting 10 users with realistic and diverse data
INSERT INTO users (name, email, national_number, accounts_number, age) VALUES  
("Ahmed Mahmoud Ibrahim", "ahmed.m@gmail.com", "29912150102345", 2, 26),
("Sara Abdullah Hassan", "sara.hassan@yahoo.com", "30205100201234", 3, 24),
("Mohamed Tareq El-Sherif", "m.tareq@outlook.com", "28509010304567", 1, 41),
("Yasmin Khaled Fouad", "yasmin.khaled@business.org", "30511220107890", 2, 21),
("Mahmoud Saeed Abdelrazek", "m.saeed@hotmail.com", "27812030203456", 2, 48),
("Nour El-Hoda Moustafa", "nour.m@gmail.com", "30402140301122", 3, 22),
("Kareem El-Hoseiny Osman", "k.husseiny@yahoo.com", "29206180105567", 2, 34),
("Dalia Raef Sabry", "dalia.raef@gmail.com", "29603250209988", 2, 30),
("Islam Emad Eldin", "islam.emad@outlook.com", "28910120104433", 2, 36),
("Reem Fayez Bahgat", "reem.fayez@gmail.com", "30307150306655", 1, 23),
("Reem Mohamed Elazhry", "reem.eng@gmail.com", "30309950306655", 2, 40),
("Akrm Gaber Mahfouz", "Krmogal@yahoo.com", "20307150306955", 1, 18);

-- 2. Inserting 20 accounts with varied types (savings, current, investment, loans)
INSERT INTO accounts (user_id, type, money, dept, expire_date) VALUES
-- Ahmed's accounts (2)
(1, "Saving_Account", 45000.00, 0.00, '2031-05-12'),
(1, "Current_Account", 12500.50, 0.00, '2029-08-20'),
-- Sara's accounts (3)
(2, "Investment_Account", 120000.00, 0.00, '2032-11-01'),
(2, "Saving_Account", 15000.00, 0.00, '2030-03-15'),
(2, "Loan_Account", 0.00, 25000.00, '2028-06-10'),
-- Mohamed's account (1)
(3, "Current_Account", 85000.00, 5000.00, '2027-12-31'),
-- Yasmin's accounts (2)
(4, "Saving_Account", 32000.00, 0.00, '2033-01-10'),
(4, "Student_Account", 5400.00, 0.00, '2029-09-01'),
-- Mahmoud's accounts (2)
(5, "Investment_Account", 450000.00, 0.00, '2035-04-20'),
(5, "Current_Account", 23000.00, 12000.00, '2028-02-14'),
-- Nour's accounts (3)
(6, "Saving_Account", 18500.00, 0.00, '2031-07-19'),
(6, "Current_Account", 4200.00, 0.00, '2028-10-05'),
(6, "Loan_Account", 0.00, 15000.00, '2027-11-20'),
-- Kareem's accounts (2)
(7, "Investment_Account", 95000.00, 0.00, '2032-06-18'),
(7, "Current_Account", 31000.00, 0.00, '2030-01-25'),
-- Dalia's accounts (2)
(8, "Saving_Account", 67000.00, 0.00, '2031-12-01'),
(8, "Current_Account", 14300.00, 2500.00, '2029-04-11'),
-- Islam's accounts (2)
(9, "Investment_Account", 210000.00, 0.00, '2034-08-15'),
(9, "Loan_Account", 0.00, 50000.00, '2029-05-30'),
-- Reem's account (1)
(10, "Saving_Account", 28000.00, 0.00, '2030-09-12'),
-- Reem2's account (2)
(11, "Current_Account", 30000.00, 0.00, '2032-08-21'),
(11, "Saving_Account", 100000.00, 0.00, '2028-01-02'),
-- Akrm's account (1)
(12, "Saving_Account", 8000, 0.00, '2032-08-09');


-- 3. Inserting 5 companies with diverse fields and investment scales
INSERT INTO companies (name, money, profit_margin, share_ratio) VALUES  
("Nile_Tech_Solutions", 8500000.00, 14.5, 25.0),
("Delta_Agro_Industries", 15000000.00, 8.2, 40.0),
("Cairo_Logistics_Hub", 4200000.00, 11.0, 15.0),
("Pharma_Care_Group", 12000000.00, 18.7, 30.0),
("Green_Energy_Egypt", 6000000.00, 22.4, 20.0);

SELECT * FROM accounts;
SELECT * FROM companies;
SELECT * FROM users;

SELECT type , money,  dept , id 
  FROM accounts
  ORDER BY money ASC;

SELECT COUNT(*) FROM companies;
SELECT COUNT(*) FROM accounts;

SELECT * FROM sqlite_sequence;

UPDATE accounts SET money = money + 100;

SELECT * FROM accounts;
UPDATE accounts SET money = money + 1000;
SELECT * FROM accounts;

UPDATE users SET age = age+1;
SELECT * FROM users;

UPDATE users SET name = "Rodaina momo khaled" WHERE id = 9;

SELECT * FROM users LIMIT 10;

UPDATE accounts SET type = "Debting_Account" WHERE type = "Loan_Account";

SELECT * FROM accounts;

CREATE TABLE IF NOT EXISTS fake (
id INTEGER  PRIMARY KEY AUTOINCREMENT,
name VARCHAR (50)  NOT NULL ,
email VARCHAR (200) NOT NULL,
national_number VARCHAR (14)  NOT NULL UNIQUE, 
accounts_number INTEGER , --not correct
age INTEGER NOT NULL 
);

INSERT INTO fake (name, email, national_number, accounts_number, age) VALUES  
("Ahmed Mahmoud Ibrahim", "ahmed.m@gmail.com", "29912150102345", 2, 26),
("Sara Abdullah Hassan", "sara.hassan@yahoo.com", "30205100201234", 3, 24),
("Mohamed Tareq El-Sherif", "m.tareq@outlook.com", "28509010304567", 1, 41);

DELETE FROM fake; 
DROP TABLE IF EXISTS fake;

--18 Ac , 10 use
DELETE FROM users WHERE id in (2,3,4);
SELECT COUNT(*) FROM accounts;

PRAGMA foreign_keys = ON;
DELETE FROM users WHERE id = 5;

DELETE FROM accounts WHERE user_id in (2,3,4);

UPDATE companies SET money = money + 10000;

SELECT * FROM users WHERE age BETWEEN 18 AND 30;
SELECT * FROM users WHERE age >= 30 OR age <=18;

SELECT * FROM accounts WHERE id in (1,12,10,16);
SELECT * FROM accounts WHERE money in (22000 , 32000 , 30000 , 10000);

SELECT * FROM users WHERE name LIKE "M%";
SELECT * FROM users WHERE name LIKE "%a%";
SELECT * FROM users WHERE name LIKE "%y";

