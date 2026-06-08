const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

app.use(cors());

let canvasToken = process.env.byupw;
let canvasURL = process.env.canvasURL;
console.log("Server started with token:", canvasToken);
console.log("Server started with canvasURL:", canvasURL);

canvasURL = process.env.canvasURL;

app.get('/test', async (req, res) => {
    res.json({ message: 'Hello, World!' });
});

app.get('/me', async (req, res) => {

    let url = `${canvasURL}/users/self`;
    console.log("Fetching URL:", url);

    const response = await fetch(url, { headers: { Authorization: `Bearer ${canvasToken}` } });
    const data = await response.json();
    res.status(response.status).json(data);
});

app.get('/api/canvas/*path', async (req, res) => {

    // path will be an array of segments
    const canvasPath  = req.params.path.join('/');
    const queryString = new URLSearchParams(req.query).toString();
    const url         = `${canvasURL}/${canvasPath}` + (queryString ? `?${queryString}` : '');

    console.log(url);
    try {
        const response = await fetch(url, { headers: { Authorization: `Bearer ${canvasToken}` } });
        console.log("Status:", response.status);
        const data = await response.json();
        console.log("Status:", data);
        res.status(response.status).json(data);
    } catch (error) {
        res.status(500).json({
            error: error.message
        });
    }
});

app.listen(3000);