const express = require('express');
const bodyParser = require('body-parser');
const { Pool } = require('pg');

// Configuración de la base de datos PostgreSQL
const pool = new Pool({
    user: 'postgres',
    host: 'localhost',
    database: 'BD_trabajadores',
    password: 'Gabriel_oli66',
    port: 5432
});

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname)); // Servir archivos estáticos como HTML

// Página principal con la barra lateral
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

// Página para agregar datos
app.get('/add', (req, res) => {
    res.sendFile(__dirname + '/add_info.html');
});

// Página para eliminar datos
app.get('/delete', (req, res) => {
    res.sendFile(__dirname + '/delete_info.html');
});

// Página para editar datos
app.get('/edit', (req, res) => {
    res.sendFile(__dirname + '/edit_info.html');
});

// Ruta para agregar datos
app.post('/performAdd', async (req, res) => {
    const { id_trabajador, Nombre, Apellido_P, Apellido_M, Fecha_N, cod_rol, Correo } = req.body;

    try {
        // Verifica si el ID o correo ya existen en la base de datos
        const checkQuery = 'SELECT * FROM trabajadores WHERE id_trabajador = $1 OR correo = $2';
        const checkValues = [id_trabajador, Correo];
        const result = await pool.query(checkQuery, checkValues);

        if (result.rows.length > 0) {
            // Si existe algún registro con el mismo ID o correo
            return res.status(400).send('Error: El ID de trabajador o el correo ya están registrados.');
        }

        // Inserta los nuevos datos
        const query = 
            `INSERT INTO trabajadores (id_trabajador, "Nombre", "Apellido_P", "Apellido_M", "Fecha_N", "cod_rol", "correo")
            VALUES ($1, $2, $3, $4, $5, $6, $7)`;
        const values = [id_trabajador, Nombre, Apellido_P, Apellido_M, Fecha_N, cod_rol, Correo];
        await pool.query(query, values);
        res.sendFile(__dirname + '/success_add.html'); // Redirige al nuevo HTML
    } catch (err) {
        console.error('Error al insertar datos:', err.message);
        res.status(500).send('Error al insertar datos');
    }
});

// Ruta para obtener datos del usuario específico
app.get('/getUserData', async (req, res) => {
    const { fullName } = req.query;

    if (!fullName) {
        return res.status(400).send('Nombre es obligatorio.');
    }

    try {
        const result = await pool.query(
            `SELECT id_trabajador, "Nombre", "Apellido_P", "Apellido_M", "Fecha_N", "cod_rol", "correo"
            FROM trabajadores
            WHERE CONCAT("Nombre", ' ', "Apellido_P", ' ', "Apellido_M") = $1`, [fullName]);

        if (result.rows.length > 0) {
            res.json(result.rows[0]);
        } else {
            res.status(404).send('Usuario no encontrado');
        }
    } catch (err) {
        console.error('Error obteniendo datos del usuario:', err.message);
        res.status(500).send('Error al obtener datos del usuario');
    }
});

// Ruta para eliminar datos
app.post('/performDelete', async (req, res) => {
    const { fullName } = req.body;

    // Suponiendo que el formato es "Nombre Apellido_P Apellido_M"
    // Dividir el nombre en partes y extraer los últimos dos elementos como apellidos
    const parts = fullName.split(' ');
    console.log('Full Name Parts:', parts);  // Para depuración

    if (parts.length < 3) {
        return res.status(400).json({ success: false, message: 'Nombre completo inválido.' });
    }

    // Extraer los valores
    const Apellido_M = parts.pop();  // Último apellido
    const Apellido_P = parts.pop();  // Segundo apellido
    const Nombre = parts.join(' ');  // Nombre es todo lo que queda

    console.log('Extracted:', { Nombre, Apellido_P, Apellido_M });  // Para depuración

    // Consulta para eliminar el trabajador basado en Nombre, Apellido_P y Apellido_M
    const query = 
        `DELETE FROM trabajadores 
        WHERE "Nombre" = $1 AND "Apellido_P" = $2 AND "Apellido_M" = $3`;
    const values = [Nombre, Apellido_P, Apellido_M];

    try {
        const result = await pool.query(query, values);

        if (result.rowCount > 0) {
            res.json({ success: true, message: 'Trabajador eliminado con éxito.' });
        } else {
            res.status(404).json({ success: false, message: 'No se encontró el trabajador con ese nombre completo.' });
        }
    } catch (err) {
        console.error('Error al eliminar registro:', err.message);
        res.status(500).json({ success: false, message: 'Error al eliminar el registro' });
    }
});

app.get('/getNames', async (req, res) => {
    const query = 'SELECT "Nombre", "Apellido_P", "Apellido_M" FROM trabajadores';

    try {
        const result = await pool.query(query);

        // Devolvemos los nombres completos concatenados
        const names = result.rows.map(row => `${row.Nombre} ${row.Apellido_P} ${row.Apellido_M}`);

        res.json(names);  // Enviamos un arreglo de nombres completos como strings
    } catch (err) {
        console.error('Error al obtener nombres:', err.message);
        res.status(500).json({ success: false, message: 'Error al obtener los nombres' });
    }
});


// Ruta para editar datos
app.post('/editData', async (req, res) => {
    const { originalId, newId, newName, newLastName, newMotherLastName, newDate, newRole, newEmail } = req.body;

    try {
        const query = 
            `UPDATE trabajadores
            SET id_trabajador = $1, "Nombre" = $2, "Apellido_P" = $3, "Apellido_M" = $4, "Fecha_N" = $5, "cod_rol" = $6, "correo" = $7
            WHERE id_trabajador = $8`;
        const values = [newId, newName, newLastName, newMotherLastName, newDate, newRole, newEmail, originalId];
        const result = await pool.query(query, values);

        if (result.rowCount > 0) {
            res.sendFile(__dirname + '/success_edit.html');
        } else {
            res.status(404).send('No se encontró el trabajador para actualizar.');
        }
    } catch (err) {
        console.error('Error al editar datos:', err.message);
        res.status(500).send('Error al editar datos.');
    }
});

// Iniciar el servidor
const port = 3000;
app.listen(port, () => {
    console.log(`Servidor escuchando en http://localhost:${port}`);
});
