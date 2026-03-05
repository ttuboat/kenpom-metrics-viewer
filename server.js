const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 10000;

// OPTION 1: Simple CORS - Allow all origins (easiest to verify)
// Uncomment this to test if it works:
 app.use(cors());

// OPTION 2: Explicit CORS configuration (more secure)
const corsOptions = {
    origin: function (origin, callback) {
        const allowedOrigins = [
            'https://ttuboat.github.io',
            'http://localhost:3000',
            'http://localhost:5000'
        ];
        
        // Allow requests with no origin (like mobile apps or curl)
        if (!origin) return callback(null, true);
        
        if (allowedOrigins.indexOf(origin) !== -1) {
            callback(null, true);
        } else {
            console.log('Blocked origin:', origin);
            callback(new Error('Not allowed by CORS'));
        }
    },
    credentials: true,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));

// FALLBACK: Manual CORS headers (in case cors package fails)
app.use((req, res, next) => {
    const origin = req.headers.origin;
    const allowedOrigins = [
        'https://ttuboat.github.io',
        'http://localhost:3000'
    ];
    
    if (allowedOrigins.includes(origin)) {
        res.setHeader('Access-Control-Allow-Origin', origin);
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        res.setHeader('Access-Control-Allow-Credentials', 'true');
    }
    
    // Handle preflight
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    
    console.log(`Request from origin: ${origin || 'undefined'}`);
    next();
});

app.use(express.json());

const KENPOM_API_BASE = 'https://kenpom.com/api.php';
const API_KEY = process.env.KENPOM_API_KEY;

// Health check endpoint
app.get('/', (req, res) => {
    res.json({ 
        status: 'KenPom API Backend is running',
        version: '2.1-cors-double-fixed',
        corsEnabled: true,
        timestamp: new Date().toISOString()
    });
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

// New endpoint for current ratings (not archived)
app.get('/api/ratings/current', async (req, res) => {
    try {
        const { y, team } = req.query;
        
        if (!y) {
            return res.status(400).json({ error: 'Year (y) is required' });
        }

        // Build URL for current ratings endpoint (don't filter by team in the API call)
        const url = `${KENPOM_API_BASE}?endpoint=ratings&y=${y}`;
        
        const response = await axios.get(url, {
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            }
        });

        // If team is specified, filter for that team by NAME
        if (team) {
            const teamData = response.data.find(t => 
                t.TeamName && t.TeamName.toLowerCase() === decodeURIComponent(team).toLowerCase()
            );
            
            if (!teamData) {
                return res.status(404).json({ error: 'Team not found in current ratings' });
            }
            
            return res.json(teamData);
        }

        res.json(response.data);
        
    } catch (error) {
        console.error('KenPom Ratings API Error:', error.message);
        
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

// Get team data for a specific date (legacy endpoint)
app.get('/api/team/:teamName', async (req, res) => {
    try {
        const { teamName } = req.params;
        const { date, year } = req.query;
        
        if (!date || !year) {
            return res.status(400).json({ error: 'Date and year are required' });
        }

        const url = `${KENPOM_API_BASE}?endpoint=archive&d=${date}&y=${year}`;
        
        const response = await axios.get(url, {
            headers: {
                'Authorization': `Bearer ${API_KEY}`
            }
        });

        const teamData = response.data.find(t => 
            t.TeamName && t.TeamName.toLowerCase() === decodeURIComponent(teamName).toLowerCase()
        );

        if (!teamData) {
            return res.status(404).json({ error: 'Team not found' });
        }

        res.json(teamData);
        
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
    console.log(`CORS enabled for: https://ttuboat.github.io`);
});
