show databases;
use my_app_db;
show tables;

select * from tbl_parkinglotowners;
select * from tbl_owner_payments;
select * from tbl_owner_registrations;
ALTER TABLE tbl_transactions
ADD COLUMN owner_email VARCHAR(100) DEFAULT NULL;
INSERT INTO tbl_transactions (user_email, owner_email, start_time, end_time, transaction_mode, amount, status, created_at)
VALUES ('user1@example.com', 'owner@example.com', '2025-03-21 09:50:00', '2025-03-21 10:00:00', 'Wallet', 500.00, 'Successful', '2025-03-21 10:00:00');

select * from tbl_pricing;
select * from tbl_transactions;

CREATE TABLE IF NOT EXISTS tbl_pricing (
    pricing_id INT AUTO_INCREMENT PRIMARY KEY,
    day_of_week VARCHAR(20),        -- e.g., 'Weekday', 'Weekend'
    time_window VARCHAR(20),        -- e.g., 'Peak', 'Off-Peak'
    rate_per_hour DECIMAL(10,2)
);

INSERT INTO tbl_pricing (day_of_week, time_window, rate_per_hour)
VALUES
('Weekday', 'Off-Peak', 50.00),
('Weekday', 'Peak', 65.00),
('Weekend', 'All-Day', 75.00);

select * from tbl_admins;
select * from tbl_users;
select * from payments;
select * from tbl_vehicles;
select * from tbl_wallets;
select * from tbl_credit_transactions;
select * from tbl_debit_transactions;	
select * from tbl_transactions;
select * from tbl_upi_transactions;
select * from tbl_parking_slots;

SELECT transaction_id, user_email, start_time, amount, status FROM tbl_transactions;

drop table tbl_vehicles;
drop table tbl_wallets;

INSERT INTO tbl_users (licence, name, email, password, phone, dob) VALUES
('DL-12345', 'Rajesh Kumar', 'rajesh.kumar@example.in', 'password1', '9876543210', '1980-05-15'),
('DL-23456', 'Suman Sharma', 'suman.sharma@example.in', 'password2', '9876543211', '1985-07-20'),
('DL-34567', 'Amitabh Singh', 'amitabh.singh@example.in', 'password3', '9876543212', '1975-03-10'),
('DL-45678', 'Priya Patel', 'priya.patel@example.in', 'password4', '9876543213', '1990-11-05'),
('DL-56789', 'Anjali Rao', 'anjali.rao@example.in', 'password5', '9876543214', '1992-02-28');

INSERT INTO payments (email, amount, payment_method, promo_code, final_amount, transaction_date) VALUES
('rajesh.kumar@example.in', 500.00, 'Wallet', 'OFF10', 450.00, '2025-03-21 10:00:00'),
('suman.sharma@example.in', 300.00, 'UPI', '', 300.00, '2025-03-21 11:00:00'),
('amitabh.singh@example.in', 700.00, 'Credit Card', 'DISC15', 595.00, '2025-03-20 15:30:00'),
('priya.patel@example.in', 250.00, 'Debit Card', '', 250.00, '2025-03-19 09:45:00'),
('anjali.rao@example.in', 400.00, 'Wallet', 'OFF5', 380.00, '2025-03-21 12:15:00');

INSERT INTO tbl_vehicles (user_email, vehicle_number, vehicle_model, vehicle_color, registration_year) VALUES
('rajesh.kumar@example.in', 'KA01AB1234', 'Maruti Swift', 'White', 2015),
('suman.sharma@example.in', 'KA02CD5678', 'Hyundai i20', 'Silver', 2018),
('amitabh.singh@example.in', 'KA03EF9012', 'Honda City', 'Black', 2012),
('priya.patel@example.in', 'KA04GH3456', 'Tata Nexon', 'Red', 2020),
('anjali.rao@example.in', 'KA05IJ7890', 'Mahindra XUV300', 'Blue', 2019);

INSERT INTO tbl_wallets (user_email, balance) VALUES
('rajesh.kumar@example.in', 1000.00),
('suman.sharma@example.in', 850.00),
('amitabh.singh@example.in', 1200.00),
('priya.patel@example.in', 500.00),
('anjali.rao@example.in', 750.00);

INSERT INTO tbl_admins (email, password) VALUES
('admin1@example.in', 'adminpass1'),
('admin2@example.in', 'adminpass2');

INSERT INTO tbl_transactions (user_email, start_time, end_time, transaction_mode, amount, status, created_at) VALUES
('rajesh.kumar@example.in', '2025-03-21 09:50:00', '2025-03-21 10:00:00', 'Wallet', 500.00, 'Successful', '2025-03-21 10:00:00'),
('suman.sharma@example.in', '2025-03-21 10:45:00', '2025-03-21 11:00:00', 'UPI', 300.00, 'Successful', '2025-03-21 11:00:00'),
('amitabh.singh@example.in', '2025-03-20 15:15:00', '2025-03-20 15:30:00', 'Credit Card', 700.00, 'Successful', '2025-03-20 15:30:00'),
('priya.patel@example.in', '2025-03-19 09:30:00', '2025-03-19 09:45:00', 'Debit Card', 250.00, 'Successful', '2025-03-19 09:45:00'),
('anjali.rao@example.in', '2025-03-21 12:00:00', '2025-03-21 12:15:00', 'Wallet', 400.00, 'Successful', '2025-03-21 12:15:00');

INSERT INTO tbl_upi_transactions (transaction_id, upi_id, promo_code) VALUES
(2, 'sumanupi@oksbi', '');

INSERT INTO tbl_credit_transactions (transaction_id, card_number, card_holder, expiry_date, promo_code) VALUES
(3, '4111111111111111', 'Amitabh Singh', '12/25', 'DISC15');

INSERT INTO tbl_debit_transactions (transaction_id, card_number, card_holder, expiry_date, promo_code) VALUES
(4, '5500000000000004', 'Priya Patel', '11/24', '');

INSERT INTO tbl_login_history (user_email, login_time, ip_address) VALUES
('rajesh.kumar@example.in', '2025-03-21 09:45:00', '192.168.1.101'),
('suman.sharma@example.in', '2025-03-21 10:40:00', '192.168.1.102'),
('amitabh.singh@example.in', '2025-03-20 15:10:00', '192.168.1.103'),
('priya.patel@example.in', '2025-03-19 09:25:00', '192.168.1.104'),
('anjali.rao@example.in', '2025-03-21 11:55:00', '192.168.1.105');

INSERT INTO tbl_slot_reservations (slot_id, user_email, start_time, end_time) VALUES
(1, 'rajesh.kumar@example.in', '2025-03-22 10:00:00', '2025-03-22 11:00:00'),
(2, 'suman.sharma@example.in', '2025-03-22 12:00:00', '2025-03-22 13:00:00'),
(3, 'amitabh.singh@example.in', '2025-03-22 09:30:00', '2025-03-22 10:30:00'),
(4, 'priya.patel@example.in', '2025-03-22 15:00:00', '2025-03-22 16:00:00'),
(5, 'anjali.rao@example.in', '2025-03-22 14:00:00', '2025-03-22 15:00:00');

SELECT * FROM tbl_users WHERE email = 'user1@example.com';

INSERT INTO tbl_users (licence, name, email, password, phone, dob) 
VALUES ('TN01A1234', 'Ravi Kumar', 'user1@example.com', 'securepassword', '9876543210', '1990-05-15');

INSERT INTO tbl_transactions (user_email, start_time, end_time, transaction_mode, amount, status) 
VALUES ('user1@example.com', '2024-03-22 10:00:00', '2024-03-22 12:00:00', 'Wallet', 200.00, 'Successful');

INSERT INTO tbl_wallet_transactions (transaction_id, payment_method, promo_code) 
VALUES (LAST_INSERT_ID(), 'Wallet', 'OFF10');


DELIMITER //

CREATE PROCEDURE insert_random_transaction()
BEGIN
  DECLARE t_mode VARCHAR(50);
  DECLARE t_amount DECIMAL(10,2);
  DECLARE t_email VARCHAR(100);
  DECLARE t_start DATETIME;
  DECLARE t_end DATETIME;
  
  -- Set a sample user email; adjust or randomize as needed.
  SET t_email = 'user1@example.com';
  
  -- Generate a random amount between 50 and 1000.
  SET t_amount = ROUND(50 + RAND() * 950, 2);
  
  -- Generate a random start time on a random day within a range.
  SET t_start = DATE_ADD('2025-01-01 00:00:00', INTERVAL FLOOR(RAND()*365) DAY);
  
  -- Let the transaction last between 15 and 90 minutes.
  SET t_end = DATE_ADD(t_start, INTERVAL FLOOR(RAND()*76)+15 MINUTE);
  
  -- Randomly choose a transaction mode: 1 = Wallet, 2 = UPI, 3 = Credit Card, 4 = Debit Card.
  SET t_mode = ELT(FLOOR(RAND()*4)+1, 'Wallet', 'UPI', 'Credit Card', 'Debit Card');
  
  -- Insert into tbl_transactions including the owner_email.
  INSERT INTO tbl_transactions (user_email, owner_email, start_time, end_time, transaction_mode, amount, status, created_at)
  VALUES (t_email, 'owner@example.com', t_start, t_end, t_mode, t_amount, 'Successful', t_end);
  
  -- Depending on the transaction mode, insert a matching record into the corresponding table.
  IF t_mode = 'UPI' THEN
      INSERT INTO tbl_upi_transactions (transaction_id, upi_id, promo_code)
      VALUES (LAST_INSERT_ID(), CONCAT(LEFT(t_email, LOCATE('@',t_email)-1),'upi@bank'), '');
  ELSEIF t_mode = 'Credit Card' THEN
      INSERT INTO tbl_credit_transactions (transaction_id, card_number, card_holder, expiry_date, promo_code)
      VALUES (LAST_INSERT_ID(), '4111111111111111', 'Test User', '12/25', 'DISC15');
  ELSEIF t_mode = 'Debit Card' THEN
      INSERT INTO tbl_debit_transactions (transaction_id, card_number, card_holder, expiry_date, promo_code)
      VALUES (LAST_INSERT_ID(), '5500000000000004', 'Test User', '11/24', '');
  END IF;
END //

DELIMITER ;
DROP PROCEDURE IF EXISTS insert_random_transaction;

CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();
CALL insert_random_transaction();

