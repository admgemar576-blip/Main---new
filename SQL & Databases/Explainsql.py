import sqlite3

#CREATE --> TABLE --> it's to creat table in your database 
#IF NOT EXISTS --> that's stop creation if the table is already exist in your database (Important )
#Every block in SQL want ended by ; like C++

# << Table Creation>>
"""
CREATE TABLE IF NOT EXISTS table_name (
    column1_name DATA_TYPE CONSTRAINTS,
    column2_name DATA_TYPE CONSTRAINTS,
    column3_name DATA_TYPE CONSTRAINTS
);

table_name , column_name , DATA_TYPE , CONSTRAINTS

table_name like Clintes , Accounts ....
column_name like account_id , name ....

DATA_TYPE --
1- INTEGER , 100,50,0,10
2- TEXT , "Ahmed" , "Saving_Account"
3- REAL , 100.5 , 20.20 , 3.5
4- BLOB , png , mp4 , zip
5- CHAR , STRING .....
6- VARCHAR(limit chars) , varbile text with limit
7- DATE , "2008-12-13" year,month, day
8 DECIMAL(max_num ,max after . ) , "12.00" more efficiently 

CONSTRAINTS --
1- PRIMARY KEY --> means this value don't repeted  and not null  , <you can add it only one time every table>(unique) , Id , National_Number 
2- AUTOINCREMENT--> means it's plus 1 automaticly , id , phone_number 
3- NOT NULL --> means you must add a value here , name , address 
4- UNIQE --> means this value mustn't repet --> you can use it more than one , Key , Player_number
5- DEFAULT VALUE --> means you add default value if you don't add value , Price , discount 
6- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE:{
  FOREIGN KEY (...) --> side key ..
  REFERENCES table1(column1) --> Search for this key in table1 in column1
  ON DELETE CASCADE --> if this key deleted from table1 delete this row
}




you can add more than CONSTRAINTS in the same column 

 
"""

# << Table Inserting>>

"""
INSERT INTO coulmn_name --
1- INSERT INTO coulmn_name VALUES (the values at the same sorting and all values );
2- INSERT INTO coulmn_name (Select params to add) VALUES (add params with the same sorting) 
3- INSERT INTO coulmn_name (Select params to add) VALUES ---> multiple addtion
(add params with the same sort),
(add params with the same sort),
(add params with the same sort),
(add params with the same sort); 

INSERT OR -->OR here means if something wrong what must database do
default --> FALL 
OR IGNORE --> ignore this process and complete anthors
OR REPLACE --> replace new value with old value 
OR FALL --> stop from this line without delete lines before it
OR ROLLBACK--> stop and delete everything done in this lines
"""

# << Table Selecting>>


"""
SELECT * from coulmn_name; -->return all in the coulmn_name
SELECT col1 , col2 ,col3 ....from coulmn_name; -->return columns you selected

WHERE --> use it to select specific items on your conditions 
SELECT col1 , col2 FROM coulmn_name WHERE col2 >100 // col3!=1000 //col1 == "Ahmed

AND / OR
SELECT col4 , col6 , col7 FROM coulmn_name WHERE col4!="yes" AND col7 >=1000
SELECF col2 FROM coulmn_name WHERE col9 == 5 OR col8 == true 

LIKE --> Use AI like re in python but more simple
SELECT * FROM coulmn_name WHERE col1 LIKE ".";

LIMIT --> put limit to results
SELECT col3 , col1 FROM  coulmn_name LIMIT 10;
"""

#Exaple sql =
"""
--CREATING 
CREATE TABLE IF NOT EXISTS profiles(
    id INTEGER PRIMARY KEY AUTOINCREMENT ,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    address TEXT ,
    age INTEGER NOT NULL,
    national_number INTEGER UNIQUE,
    money REAL DEFAULT 0 ,
    gpa REAL DEFAULT 0
);

--Insert
INSERT INTO profiles VALUES
(NULL ,"Ahmed" , "Ahmeder@email.com" , "Giza" , 100 , 9991010 , 2000.50 , 3.4);

INSERT INTO profiles 
(name , email , address, age,national_number,money, gpa) VALUES
("Moahmed" , "Ahm@Ahm@Bistmail.com" , "USA" , 21 , 20229009009 , 100000000 , 4);

INSERT INTO profiles
 (name , email ,national_number , age ) VALUES 
 ("Habiba" , "Queen@yahoo.com" , 01125555889 , 19  );

  INSERT INTO profiles 
  (name , email , address , age , national_number ,money , gpa ) VALUES 
  ("Sara" , "Qtrue@yahoo.com" ,"Cario" ,30, 5555889 , 19000 , 4.0  ),
  ("Hey" , "googel@outlook.com" ,"Adresse ",0, 0112555889 , 19 , 2.0 ),
  ("Melon" , "Bati5" ,"fruit street", 100000,  000000 , 000, 0.0 ),
  ("Englisch" , "3mk.com" , "no" ,100000000, 02335112252242672672 , 100000000000000000 , 10.0);

INSERT  OR IGNORE INTO profiles
  (name , email , address , age , national_number ,money , gpa ) VALUES 
  ("marim" , "Qtrue@yahoo.com" ,"Cario" ,30, 55889 , 19000 , 4.0  );

INSERT  OR REPLACE INTO profiles
  (name , email , address , age , national_number ,money , gpa ) VALUES 
  ("marim" , "Qtrue@yahoo.com" ,"Cario" ,30, 55889 , 19000 , 4.0  );

SELECT * FROM profiles;

SELECT name , email FROM profiles;
SELECT name , address, age , gpa FROM profiles ;
SELECT gpa ,  national_number , money FROM profiles;
SELECT id , national_number FROM profiles;

SELECT * FROM profiles WHERE age >= 20;
SELECT name FROM profiles WHERE name <> "Ahmed";
SELECT national_number,id,gpa FROM profiles WHERE money > 100;

SELECT * FROM profiles WHERE (gpa > 1.2) AND (money > 1000);
SELECT name , national_number From profiles WHERE (gpa >= 4) AND (age < 30);

SELECT * FROM profiles WHERE (name == "Ahmed") OR (name = "marim");
SELECT address , email FROM profiles WHERE (gpa == 4) OR (money >=100000);

SELECT email , name FROM profiles WHERE email LIKE "%@yahoo.com" ;

SELECT * FROM profiles LIMIT 5;
SELECT * FROM profiles LIMIT 8;
SELECT name , gpa  FROM profiles LIMIT 2;
SELECT name , address , email FROM profiles LIMIT 6;
"""

#Table updating
"""
UPADTE table SET col = "...." --> update all rows 
UPADTE table SET age = age+1 "...." --> update all rows 
UPADTE table SET col = "...." WHERE id = ... --> update row that has this  id



"""
