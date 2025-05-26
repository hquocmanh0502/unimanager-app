-- Xoá & tạo lại database
DROP DATABASE IF EXISTS university_management;
CREATE DATABASE university_management;
USE university_management;

-- 1. Bảng Khoa (departments)
CREATE TABLE departments (
    dept_id VARCHAR(10) PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    dept_abbr VARCHAR(10) NOT NULL,
    dept_description TEXT
);

-- 2. Bảng Trình độ học vấn (degrees)
CREATE TABLE degrees (
    degree_id VARCHAR(10) PRIMARY KEY,
    degree_name VARCHAR(100) NOT NULL,
    degree_abbr VARCHAR(10) NOT NULL,
    coefficient FLOAT NOT NULL DEFAULT 1.0
);

-- 3. Bảng Giảng viên (teachers)
CREATE TABLE teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id VARCHAR(10) UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    phone VARCHAR(15),
    email VARCHAR(100),
    degree_id VARCHAR(10),
    dept_id VARCHAR(10),
    teacher_coefficient FLOAT NOT NULL DEFAULT 1.0,
    FOREIGN KEY (degree_id) REFERENCES degrees(degree_id),
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);

-- 4. Bảng Học phần (course_modules)
CREATE TABLE course_modules (
    module_id VARCHAR(10) PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL CHECK (credits > 0),
    coefficient FLOAT NOT NULL DEFAULT 1.0,  -- Hệ số học phần
    periods INT NOT NULL CHECK (periods > 0) -- Số tiết dự kiến
);

-- 5. Bảng Kỳ học (semesters)
CREATE TABLE semesters (
    semester_id VARCHAR(9) PRIMARY KEY,
    semester_name VARCHAR(50) NOT NULL,
    year VARCHAR(9) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CHECK (start_date < end_date)
);

-- 6. Bảng Lớp học phần (classes)

CREATE TABLE classes (
    class_id VARCHAR(9) PRIMARY KEY,
    semester_id VARCHAR(9) NOT NULL,
    module_id VARCHAR(10) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    num_students INT NOT NULL CHECK (num_students >= 0),
    FOREIGN KEY (semester_id) REFERENCES semesters(semester_id),
    FOREIGN KEY (module_id) REFERENCES course_modules(module_id)
);
-- 7. Bảng Phân công giảng viên (assignments)

CREATE TABLE assignments (
    assignment_id VARCHAR(9) PRIMARY KEY,
    class_id VARCHAR(9) NOT NULL,
    teacher_id VARCHAR(10) NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    UNIQUE (class_id)
);
-- 8. Bảng Tính lương (salaries)
CREATE TABLE salaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id VARCHAR(10),
    class_id VARCHAR(10),
    semester_id VARCHAR(9),
    salary_amount DECIMAL(10,2) NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (semester_id) REFERENCES semesters(semester_id)
);

-- 9. Bảng Người dùng (users)
CREATE TABLE users (
    user_id VARCHAR(10) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- -----------------------------------------
-- DỮ LIỆU MẪU
-- -----------------------------------------

-- Departments
INSERT INTO departments VALUES 
('DEPT2321', 'Khoa Công nghệ Thông tin', 'CNTT', 'Quản lý các ngành liên quan đến CNTT'),
('DEPT4847', 'Khoa Kinh tế', 'KT', 'Quản lý các ngành liên quan đến Kinh tế');

-- Degrees
INSERT INTO degrees VALUES 
('DEG82838', 'Đại học', 'ĐH', 1.3),
('DEG12238', 'Thạc sĩ', 'ThS', 1.5),
('DEG34993', 'Tiến sĩ', 'TS', 1.7),
('DEG21434', 'Phó Giáo sư', 'PGS', 2.0),
('DEG92138', 'Giáo sư', 'GS', 2.5);

-- Teachers
INSERT INTO teachers (teacher_id, full_name, date_of_birth, phone, email, degree_id, dept_id, teacher_coefficient)
VALUES 
('TCH93289', 'Nguyễn Văn A', '1985-05-20', '0905123456', 'nguyenvana@example.com', 'DEG82838', 'DEPT4847', 1.3),
('TCH94393', 'Trần Thị B', '1990-03-15', '0916123456', 'tranthib@example.com', 'DEG12238', 'DEPT4847', 1.5);



-- Semesters
INSERT INTO semesters VALUES
('SEM20251', 'Học kỳ 1', '2025', '2025-01-06', '2025-05-20'),
('SEM20252', 'Học kỳ 2', '2025', '2025-06-01', '2025-12-15'),
('SEM20261', 'Học kỳ 1', '2026', '2026-01-05', '2026-05-20');

-- Users
INSERT INTO users VALUES
('DEPT2321', 'a', 'a', 'Department'),
('TCH93289', 'nguyenvana_teacher', 'default123', 'Teacher'),
('TCH94393', 'tranthib_teacher', 'default123', 'Teacher');
SELECT semester_id, start_date, end_date FROM semesters;
SELECT semester_id, start_date, end_date FROM semesters;

-- Thêm dữ liệu mẫu cho course_modules
INSERT INTO course_modules (module_id, module_name, credits, coefficient, periods) VALUES
('MOD29934', 'Lập trình Python', 3, 1.0, 45),
('MOD93923', 'Cơ sở dữ liệu', 3, 1.5, 60);

-- Thêm dữ liệu mẫu cho classes
INSERT INTO classes (class_id, semester_id, module_id, class_name, num_students) VALUES
('CLS39293', 'SEM20251', 'MOD29934', 'Lớp Python 1', 40),
('CLS92948', 'SEM20251', 'MOD93923', 'Lớp CSDL 1', 35);

-- Thêm dữ liệu mẫu cho assignments
INSERT INTO assignments (assignment_id, class_id, teacher_id, assigned_at) VALUES
('ASN39293', 'CLS39293', 'TCH93289', '2025-05-23 03:07:00'),
('ASN92948', 'CLS92948', 'TCH94393', '2025-05-23 03:07:00');

-- Thêm dữ liệu mẫu cho salaries
INSERT INTO salaries (teacher_id, class_id, semester_id, salary_amount, calculated_at) VALUES
('TCH93289', 'CLS39293', 'SEM20251', 4500000, '2025-05-17 04:05:00'),
('TCH94393', 'CLS92948', 'SEM20251', 6000000, '2025-05-17 04:05:00');

