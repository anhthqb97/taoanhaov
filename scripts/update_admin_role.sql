-- SQL script to update admin user role from "user" to "admin"
-- Run this in Adminer or any MySQL client

USE lienquan;

-- Check current admin user
SELECT id, username, email, role, is_active, created_at 
FROM users 
WHERE id = 2;

-- Update admin user role to admin
UPDATE users 
SET role = 'admin', updated_at = NOW() 
WHERE id = 2;

-- Verify the update
SELECT id, username, email, role, is_active, updated_at 
FROM users 
WHERE id = 2;

-- Show all users for verification
SELECT id, username, email, role, is_active, created_at 
FROM users 
ORDER BY id;
