-- HR dummy data seed for PostgreSQL (pgAdmin)
-- Safe to run multiple times due to ON CONFLICT upserts.

BEGIN;

-- =========================
-- 0) create tables (if not already created)
-- =========================
CREATE TABLE IF NOT EXISTS public.departments (
  department_id VARCHAR(20) PRIMARY KEY,
  department_name VARCHAR(150) NOT NULL,
  hod_id VARCHAR(20) NULL
);

CREATE TABLE IF NOT EXISTS public.employees (
  employee_id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  phone VARCHAR(15),
  gender VARCHAR(10),
  dob DATE,
  department_id VARCHAR(20),
  department VARCHAR(150),
  designation VARCHAR(150),
  role VARCHAR(50),
  employment_type VARCHAR(50),
  date_of_joining DATE,
  reporting_to VARCHAR(20),
  status VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS public.users (
  user_id VARCHAR(20) PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50),
  linked_employee_id VARCHAR(20),
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP NULL
);

ALTER TABLE public.employees
  DROP CONSTRAINT IF EXISTS fk_employees_department;
ALTER TABLE public.employees
  ADD CONSTRAINT fk_employees_department
  FOREIGN KEY (department_id) REFERENCES public.departments(department_id);

ALTER TABLE public.employees
  DROP CONSTRAINT IF EXISTS fk_employees_reporting_to;
ALTER TABLE public.employees
  ADD CONSTRAINT fk_employees_reporting_to
  FOREIGN KEY (reporting_to) REFERENCES public.employees(employee_id);

ALTER TABLE public.departments
  DROP CONSTRAINT IF EXISTS fk_departments_hod;
ALTER TABLE public.departments
  ADD CONSTRAINT fk_departments_hod
  FOREIGN KEY (hod_id) REFERENCES public.employees(employee_id);

ALTER TABLE public.users
  DROP CONSTRAINT IF EXISTS fk_users_linked_employee;
ALTER TABLE public.users
  ADD CONSTRAINT fk_users_linked_employee
  FOREIGN KEY (linked_employee_id) REFERENCES public.employees(employee_id);

-- =========================
-- 1) departments
-- =========================
INSERT INTO public.departments (department_id, department_name, hod_id)
VALUES
  ('DPT001', 'Computer Science and Engineering', NULL),
  ('DPT002', 'Administration', NULL),
  ('DPT003', 'Finance', NULL),
  ('DPT004', 'Director Office', NULL)
ON CONFLICT (department_id)
DO UPDATE SET
  department_name = EXCLUDED.department_name;

-- =========================
-- 2) employees
-- Insert parent rows first to satisfy reporting_to FK where applicable.
-- =========================
INSERT INTO public.employees (
  employee_id,
  name,
  email,
  phone,
  gender,
  dob,
  department_id,
  department,
  designation,
  role,
  employment_type,
  date_of_joining,
  reporting_to,
  status
)
VALUES
  ('EMP1003', 'Dr. Meena Verma', 'director@iiitdmj.ac.in', '9876543212', 'Female', DATE '1975-02-11', 'DPT004', 'Director Office', 'Director', 'Director', 'Permanent', DATE '2019-01-10', NULL, 'Active'),
  ('EMP1002', 'Dr. Anil Kumar', 'anil.kumar@iiitdmj.ac.in', '9876543211', 'Male', DATE '1980-07-20', 'DPT001', 'Computer Science and Engineering', 'Professor and HOD', 'HOD', 'Permanent', DATE '2015-06-15', 'EMP1003', 'Active'),
  ('EMP1004', 'Suresh Verma', 'registrar@iiitdmj.ac.in', '9876543213', 'Male', DATE '1982-03-10', 'DPT002', 'Administration', 'Registrar', 'Registrar', 'Permanent', DATE '2018-01-15', 'EMP1003', 'Active'),
  ('EMP1005', 'Priya Nair', 'hr.admin@iiitdmj.ac.in', '9876543214', 'Female', DATE '1987-09-25', 'DPT002', 'Administration', 'HR Administrator', 'HR Admin', 'Permanent', DATE '2020-11-05', 'EMP1004', 'Active'),
  ('EMP1006', 'Arun Joshi', 'accountant@iiitdmj.ac.in', '9876543215', 'Male', DATE '1985-12-18', 'DPT003', 'Finance', 'Accountant', 'Accountant', 'Permanent', DATE '2019-08-12', 'EMP1004', 'Active'),
  ('EMP1001', 'Rahul Sharma', 'rahul.sharma@iiitdmj.ac.in', '9876543210', 'Male', DATE '1990-05-12', 'DPT001', 'Computer Science and Engineering', 'Assistant Professor', 'Employee', 'Permanent', DATE '2021-08-01', 'EMP1002', 'Active')
ON CONFLICT (employee_id)
DO UPDATE SET
  name = EXCLUDED.name,
  email = EXCLUDED.email,
  phone = EXCLUDED.phone,
  gender = EXCLUDED.gender,
  dob = EXCLUDED.dob,
  department_id = EXCLUDED.department_id,
  department = EXCLUDED.department,
  designation = EXCLUDED.designation,
  role = EXCLUDED.role,
  employment_type = EXCLUDED.employment_type,
  date_of_joining = EXCLUDED.date_of_joining,
  reporting_to = EXCLUDED.reporting_to,
  status = EXCLUDED.status;

-- Update department HODs after employees exist.
UPDATE public.departments
SET hod_id = 'EMP1002'
WHERE department_id = 'DPT001';

UPDATE public.departments
SET hod_id = NULL
WHERE department_id IN ('DPT002', 'DPT003', 'DPT004');

-- =========================
-- 3) users
-- NOTE: password_hash here stores plain text values from your sample data.
-- In production, store proper hashed passwords only.
-- =========================
INSERT INTO public.users (
  user_id,
  username,
  password_hash,
  role,
  linked_employee_id,
  is_active,
  last_login
)
VALUES
  ('EMP1001', 'rahul1001', 'rahul123', 'Employee', 'EMP1001', TRUE, NULL),
  ('EMP1002', 'hod1002', 'hod123', 'HOD', 'EMP1002', TRUE, NULL),
  ('EMP1003', 'director1003', 'director123', 'Director', 'EMP1003', TRUE, NULL),
  ('EMP1004', 'registrar1004', 'registrar123', 'Registrar', 'EMP1004', TRUE, NULL),
  ('EMP1005', 'hradmin1005', 'hradmin123', 'HR Admin', 'EMP1005', TRUE, NULL),
  ('EMP1006', 'accountant1006', 'accountant123', 'Accountant', 'EMP1006', TRUE, NULL)
ON CONFLICT (user_id)
DO UPDATE SET
  username = EXCLUDED.username,
  password_hash = EXCLUDED.password_hash,
  role = EXCLUDED.role,
  linked_employee_id = EXCLUDED.linked_employee_id,
  is_active = EXCLUDED.is_active,
  last_login = EXCLUDED.last_login;

COMMIT;
