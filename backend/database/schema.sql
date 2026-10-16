-- =====================================
-- Create Users Table
-- =====================================

CREATE TABLE users (

    id SERIAL PRIMARY KEY,

    username VARCHAR(100) UNIQUE NOT NULL,

    password VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =====================================
-- Create Machines Table
-- =====================================

CREATE TABLE machines (

    id SERIAL PRIMARY KEY,

    machine_name VARCHAR(100),

    location VARCHAR(100),

    status VARCHAR(50)

);

-- =====================================
-- Create Sensor Data Table
-- =====================================

CREATE TABLE sensor_data (

    id SERIAL PRIMARY KEY,

    machine_id INT REFERENCES machines(id),

    temperature FLOAT,

    pressure FLOAT,

    humidity FLOAT,

    speed FLOAT,

    vibration FLOAT,

    material FLOAT,

    power FLOAT,

    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =====================================
-- Create Prediction Table
-- =====================================

CREATE TABLE predictions (

    id SERIAL PRIMARY KEY,

    machine_id INT REFERENCES machines(id),

    model_type VARCHAR(20),

    efficiency FLOAT,

    waste FLOAT,

    failure FLOAT,

    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);
