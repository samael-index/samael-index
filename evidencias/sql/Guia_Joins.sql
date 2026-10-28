CREATE TABLE clientes (
    cliente_id NUMBER PRIMARY KEY,
    nombre VARCHAR2(50) NOT NULL,
    ciudad VARCHAR2(50)
);

CREATE TABLE productos (
    producto_id NUMBER PRIMARY KEY,
    nombre_producto VARCHAR2(50) NOT NULL,
    precio NUMBER(10,2)
);

CREATE TABLE pedidos (
    pedido_id NUMBER PRIMARY KEY,
    cliente_id NUMBER REFERENCES clientes(cliente_id),
    producto_id NUMBER,
    fecha DATE DEFAULT SYSDATE,
    monto NUMBER(10,2)
);

INSERT INTO clientes VALUES (1, 'Carlos Gómez', 'Bogotá');
INSERT INTO clientes VALUES (2, 'Ana Martínez', 'Medellín');
INSERT INTO clientes VALUES (3, 'Luis Rodríguez', 'Cali');
INSERT INTO clientes VALUES (4, 'Sofia López', 'Barranquilla');

INSERT INTO productos VALUES (10, 'Laptop HP', 3500000);
INSERT INTO productos VALUES (20, 'Mouse Logi', 120000);
INSERT INTO productos VALUES (30, 'Teclado Redragon', 250000);
INSERT INTO productos VALUES (40, 'Monitor Dell', 1200000);

INSERT INTO pedidos VALUES (101, 1, 10, SYSDATE - 5, 3500000);
INSERT INTO pedidos VALUES (102, 1, 20, SYSDATE - 2, 120000);
INSERT INTO pedidos VALUES (103, 2, 30, SYSDATE - 1, 250000);
INSERT INTO pedidos VALUES (104, NULL, 40, SYSDATE, 1200000);
COMMIT;

SELECT
    p.pedido_id,
    c.nombre AS cliente,
    pr.nombre_producto,
    p.monto
FROM pedidos p
INNER JOIN clientes c ON p.cliente_id = c.cliente_id
INNER JOIN productos pr ON p.producto_id = pr.producto_id;

SELECT
    c.nombre AS cliente,
    pr.nombre_producto,
    p.monto
FROM pedidos p
INNER JOIN clientes c ON p.cliente_id = c.cliente_id
INNER JOIN productos pr ON p.producto_id = pr.producto_id
WHERE p.monto > (
    SELECT AVG(monto)
    FROM pedidos
);

SELECT
    c.cliente_id,
    c.nombre AS cliente,
    p.pedido_id,
    p.monto
FROM clientes c
LEFT JOIN pedidos p ON c.cliente_id = p.cliente_id;

SELECT
    c.nombre AS cliente,
    recientes.pedido_id,
    recientes.monto,
    recientes.fecha
FROM clientes c
LEFT JOIN (
    SELECT pedido_id, cliente_id, monto, fecha
    FROM pedidos
    WHERE fecha >= SYSDATE - 3
) recientes ON c.cliente_id = recientes.cliente_id;

SELECT
    pr.producto_id,
    pr.nombre_producto,
    p.pedido_id,
    p.monto
FROM pedidos p
RIGHT JOIN productos pr ON p.producto_id = pr.producto_id;

SELECT
    c_filtrados.nombre AS cliente,
    c_filtrados.ciudad,
    pr.nombre_producto
FROM pedidos p
INNER JOIN (
    SELECT cliente_id, nombre, ciudad
    FROM clientes
    WHERE ciudad IN ('Bogotá', 'Medellín')
) c_filtrados ON p.cliente_id = c_filtrados.cliente_id
RIGHT JOIN productos pr ON p.producto_id = pr.producto_id;

SELECT
    c.nombre AS cliente,
    p.pedido_id,
    p.monto
FROM clientes c
FULL JOIN pedidos p ON c.cliente_id = p.cliente_id;

SELECT
    cb.nombre AS cliente_bogota,
    p.pedido_id,
    p_costosos.nombre_producto,
    p_costosos.precio
FROM (
    SELECT * FROM clientes WHERE ciudad = 'Bogotá'
) cb
FULL JOIN pedidos p ON cb.cliente_id = p.cliente_id
FULL JOIN (
    SELECT * FROM productos WHERE precio > 500000
) p_costosos ON p.producto_id = p_costosos.producto_id;

SELECT
    c.nombre AS cliente,
    pr.nombre_producto
FROM clientes c
CROSS JOIN productos pr;

SELECT
    c.nombre AS cliente,
    c.ciudad,
    pr.nombre_producto,
    pr.precio
FROM (
    SELECT * FROM clientes WHERE ciudad = 'Cali'
) c
CROSS JOIN (
    SELECT * FROM productos WHERE precio < 300000
) pr;

SELECT
    p1.nombre_producto AS producto_mayor,
    p1.precio AS precio_mayor,
    p2.nombre_producto AS producto_menor,
    p2.precio AS precio_menor
FROM productos p1
INNER JOIN productos p2 ON p1.precio > p2.precio;

SELECT
    c1.nombre AS cliente_1,
    c2.nombre AS cliente_2,
    c1.ciudad
FROM clientes c1
INNER JOIN (
    SELECT cliente_id, nombre, ciudad
    FROM clientes
) c2 ON c1.ciudad = c2.ciudad AND c1.cliente_id < c2.cliente_id;
