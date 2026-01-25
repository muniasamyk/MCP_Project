-- PostgreSQL initialization script.
--
-- Run with:
--   psql -U postgres -d mcp_db -f datas_insert/sample_data.sql
--
-- Note:
-- - Creating the database itself is intentionally NOT done here.
-- - Ensure `mcp_db` exists before running this script.

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10, 2),
    hire_date DATE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2),
    lead_id INTEGER REFERENCES employees(id)
);

-- Create issues table
CREATE TABLE IF NOT EXISTS issues (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20),
    status VARCHAR(20),
    assigned_to INTEGER REFERENCES employees(id),
    project_id INTEGER REFERENCES projects(id),
    created_date DATE,
    due_date DATE
);

-- Insert sample employee data
INSERT INTO employees (name, email, department, salary, hire_date, is_active) VALUES
('Alice Johnson', 'alice@company.com', 'AI', 95000, '2022-01-15', TRUE),
('Bob Smith', 'bob@company.com', 'AI', 92000, '2022-03-20', TRUE),
('Carol White', 'carol@company.com', 'Backend', 88000, '2021-06-10', TRUE),
('David Brown', 'david@company.com', 'Frontend', 85000, '2021-09-05', TRUE),
('Eva Martinez', 'eva@company.com', 'AI', 98000, '2022-02-01', TRUE),
('Frank Wilson', 'frank@company.com', 'DevOps', 90000, '2021-12-15', TRUE),
('Grace Lee', 'grace@company.com', 'Backend', 87000, '2022-04-20', TRUE),
('Henry Chen', 'henry@company.com', 'Frontend', 84000, '2022-05-10', FALSE);

-- Insert sample project data
INSERT INTO projects (name, description, status, start_date, end_date, budget, lead_id) VALUES
('AI Model Development', 'Developing ML models for prediction', 'In Progress', '2023-01-01', '2024-12-31', 500000, 1),
('Web Portal Redesign', 'Redesigning company web portal', 'Completed', '2022-06-01', '2023-06-30', 150000, 4),
('Infrastructure Migration', 'Migrating to cloud infrastructure', 'In Progress', '2023-03-01', '2024-06-30', 300000, 6),
('Mobile App Development', 'Building iOS and Android apps', 'Planning', '2024-01-01', '2025-06-30', 400000, 5);

-- Insert sample issue data
INSERT INTO issues (title, description, priority, status, assigned_to, project_id, created_date, due_date) VALUES
('Database optimization needed', 'Optimize slow queries in ML pipeline', 'High', 'Open', 1, 1, '2024-01-10', '2024-02-10'),
('Frontend button styling issue', 'Fix button alignment on mobile', 'Medium', 'In Progress', 4, 2, '2024-01-12', '2024-01-25'),
('API rate limiting', 'Implement rate limiting for API', 'High', 'Open', 3, 3, '2024-01-15', '2024-02-15'),
('User authentication flow', 'Implement OAuth2 authentication', 'Critical', 'In Progress', 5, 4, '2024-01-20', '2024-02-20'),
('Documentation update', 'Update API documentation', 'Low', 'Open', 6, 1, '2024-01-22', '2024-02-05');
