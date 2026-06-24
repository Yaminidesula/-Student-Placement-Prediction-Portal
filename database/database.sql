-- Student Placement Prediction Portal - Database Schema
-- Run this SQL file to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS placement_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE placement_portal;

-- Users table - stores registered users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Predictions table - stores prediction history
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    gender VARCHAR(10),
    tenth_percentage DECIMAL(5,2),
    twelfth_percentage DECIMAL(5,2),
    degree_percentage DECIMAL(5,2),
    mba_percentage DECIMAL(5,2),
    specialization VARCHAR(50),
    work_experience VARCHAR(10),
    skills TEXT,
    result VARCHAR(20) NOT NULL,
    probability DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data for testing (optional)
-- INSERT INTO users (name, email, password) VALUES 
-- ('Test User', 'test@example.com', 'hashed_password_here');
