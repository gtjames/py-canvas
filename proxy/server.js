const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

app.use(cors());
console.log("Server started with token:", process.env.byupw);
console.log("Server started with canvasURL:", process.env.canvasURL);

canvasURL = process.env.canvasURL;

app.get('/test', async (req, res) => {
    res.json({ message: 'Hello, World!' });
});

app.get('/api/canvas/', async (req, res) => {
    try {
        const canvasPath = req.params[0];

        const queryString = new URLSearchParams(req.query).toString();

        const url =
            `${process.env.CANVAS_URL}/api/v1/${canvasPath}` +
            (queryString ? `?${queryString}` : '');

        const response = await fetch(url, {
            headers: {
                Authorization: `Bearer ${process.env.CANVAS_TOKEN}`
            }
        });

        const data = await response.json();

        res.status(response.status).json(data);
    } catch (error) {
        res.status(500).json({
            error: error.message
        });
    }
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});
