DROP DATABASE IF EXISTS product_db;
CREATE DATABASE product_db;
USE product_db;

-- Product table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) CHECK (price >= 0),
    quantity INT DEFAULT 0 CHECK (quantity >= 0)
);

-- Category table for join
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

-- Add category_id to products (FK for join)
ALTER TABLE products
ADD category_id INT,
ADD FOREIGN KEY (category_id) REFERENCES categories(category_id);

-- Insert some categories
INSERT INTO categories (category_name) VALUES ('Electronics'), ('Books'), ('Groceries');

-- Log table
CREATE TABLE product_update_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    old_quantity INT,
    new_quantity INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stored Procedure
DELIMITER //
CREATE PROCEDURE ApplyDiscount(IN discount_percent DECIMAL(5,2))
BEGIN
    UPDATE products
    SET price = price - (price * (discount_percent / 100));
END //
DELIMITER ;

-- Trigger for logs
DELIMITER //
CREATE TRIGGER after_product_update
AFTER UPDATE ON products
FOR EACH ROW
BEGIN
    IF OLD.price != NEW.price OR OLD.quantity != NEW.quantity THEN
        INSERT INTO product_update_log (product_id, old_price, new_price, old_quantity, new_quantity)
        VALUES (OLD.product_id, OLD.price, NEW.price, OLD.quantity, NEW.quantity);
    END IF;
END //
DELIMITER ;
