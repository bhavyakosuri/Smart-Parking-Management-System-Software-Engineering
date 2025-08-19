CREATE DATABASE Login_Deets;
USE Login_Deets;

CREATE TABLE users_ps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    licence VARCHAR(20),
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    phone VARCHAR(15),
    dob DATE
);

INSERT INTO users_ps (license_number, name, email, password, phone, dob) VALUES
('KA05MG1234', 'Aarav Sharma', 'aarav.sharma@gmail.com', 'Pa$$w0rd1', '9876543210', '1995-06-12'),
('MH12AB5678', 'Priya Iyer', 'priya.iyer@yahoo.com', 'Secure@123', '9834567890', '1998-04-25'),
('DL01CD9876', 'Rajesh Verma', 'rajesh.verma@hotmail.com', 'Pass@word99', '9812345678', '1992-12-15'),
('TN09EF6543', 'Sneha Nair', 'sneha.nair@outlook.com', 'MyP@ssword7', '9787654321', '1997-03-08'),
('WB20GH3210', 'Vikram Singh', 'vikram.singh@gmail.com', 'Qwerty#789', '9876123456', '1993-09-20'),
('AP30IJ8765', 'Kavya Reddy', 'kavya.reddy@yahoo.com', 'Strong@Pass1', '9945123678', '1999-07-05'),
('GJ15KL4321', 'Arjun Patel', 'arjun.patel@hotmail.com', 'SecurePWD123', '9823456789', '1994-11-30'),
('RJ25MN2109', 'Meera Joshi', 'meera.joshi@gmail.com', 'Joshi@2023', '9815674321', '1991-05-18'),
('KL10OP7654', 'Aditya Menon', 'aditya.menon@outlook.com', 'M3n0n@pass', '9847654321', '1996-08-22'),
('MP18QR9870', 'Simran Kaur', 'simran.kaur@yahoo.com', 'S!mran@456', '9873456781', '1993-10-10');

SHOW databases;
SHOW TABLES;
SELECT * FROM users_ps;


DROP TABLE users_ps;
DROP DATABASE sample;