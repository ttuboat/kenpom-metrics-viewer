const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 10000;

// Enable CORS for your GitHub Pages site
app.use(cors({
    origin: ['https://ttuboat.github.io', 'http://localhost:3000'],
    credentials: true
}));

app.use(express.json());

const KENPOM_API_BASE = 'https://kenpom.com/api.php';
const API_KEY = process.env.KENPOM_API_KEY;

// Health check endpoint
app.get('/', (req, res) => {
    res.json({ status: 'KenPom API Backend is running' });
});

// Get archive data for a specific date
app.get('/api/archive', async (req, res) => {
    try {
        const { d, y, team } = req.query;
        
        if (!d || !y) {
            return res.status(400).json({ error: 'Date (d) and year (y) are required' });
        }

        const url = `${KENPOM_API_BASE}?endpoint=archive&d=${d}&y=${y}`;
        
        const response = await axios.get(url, {
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            }
        });

        // If team is specified, filter for that team
        if (team) {
            const teamData = response.data.find(t => t.TeamName === team);
            if (!teamData) {
                return res.status(404).json({ error: 'Team not found' });
            }
            return res.json(teamData);
        }

        res.json(response.data);
        
    } catch (error) {
        console.error('KenPom API Error:', error.message);
        
        if (error.response) {
            res.status(error.response.status).json({ 
                error: 'KenPom API error',
                details: error.response.data 
            });
        } else {
            res.status(500).json({ error: 'Server error' });
        }
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
