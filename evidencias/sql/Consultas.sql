SET DEFINE ON

CREATE TABLE job_grades (
    grade_level VARCHAR2(3),
    lowest_sal  NUMBER,
    highest_sal NUMBER
);

INSERT INTO job_grades VALUES ('A', 1000, 2999);
INSERT INTO job_grades VALUES ('B', 3000, 5999);
INSERT INTO job_grades VALUES ('C', 6000, 9999);
INSERT INTO job_grades VALUES ('D', 10000, 14999);
INSERT INTO job_grades VALUES ('E', 15000, 24999);
INSERT INTO job_grades VALUES ('F', 25000, 40000);
COMMIT;

SELECT l.location_id, l.street_address, l.city, l.state_province, c.country_name
FROM locations l
JOIN countries c ON l.country_id = c.country_id;

SELECT e.last_name, e.department_id, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id;

SELECT e.last_name, j.job_title, e.department_id, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN locations l ON d.location_id = l.location_id
JOIN jobs j ON e.job_id = j.job_id
WHERE l.city = 'Toronto';

SELECT e.last_name AS "Employee", e.employee_id AS "Emp#", m.last_name AS "Manager", m.employee_id AS "Mgr#"
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id;

SELECT e.last_name AS "Employee", e.employee_id AS "Emp#", m.last_name AS "Manager", m.employee_id AS "Mgr#"
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.employee_id
ORDER BY e.employee_id;

SELECT e.department_id AS "Departamento", e.last_name AS "Empleado", c.last_name AS "Colega"
FROM employees e
JOIN employees c ON e.department_id = c.department_id AND e.employee_id <> c.employee_id
ORDER BY e.department_id, e.last_name, c.last_name;

DESCRIBE job_grades;

SELECT e.last_name, j.job_title, d.department_name, e.salary, g.grade_level
FROM employees e
JOIN jobs j ON e.job_id = j.job_id
LEFT JOIN departments d ON e.department_id = d.department_id
JOIN job_grades g ON e.salary BETWEEN g.lowest_sal AND g.highest_sal;

SELECT e.first_name || ' ' || e.last_name AS nombre, e.hire_date
FROM employees e
JOIN employees dv ON dv.last_name = 'Davies' AND dv.hire_date < e.hire_date;

SELECT e.first_name || ' ' || e.last_name AS "Empleado", e.hire_date AS "Contratacion Empleado",
       m.first_name || ' ' || m.last_name AS "Supervisor", m.hire_date AS "Contratacion Supervisor"
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
WHERE e.hire_date < m.hire_date;

SELECT last_name, hire_date
FROM employees
WHERE department_id IN (SELECT department_id FROM employees WHERE last_name = '&&apellido')
AND last_name <> '&&apellido';

UNDEFINE apellido

SELECT employee_id, last_name
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary ASC;

SELECT employee_id, last_name
FROM employees
WHERE department_id IN (SELECT department_id FROM employees WHERE LOWER(last_name) LIKE '%u%');

SELECT last_name, department_id, job_id
FROM employees
WHERE department_id IN (SELECT department_id FROM departments WHERE location_id = 1700);

SELECT last_name, salary
FROM employees
WHERE manager_id IN (SELECT employee_id FROM employees WHERE last_name = 'King');

SELECT e.department_id, e.last_name, e.job_id
FROM employees e
JOIN departments d ON e.department_id = d.department_id
WHERE d.department_name = 'Executive';
