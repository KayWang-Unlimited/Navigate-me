
const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

//create the express app
const app = express();
const port = 8080;

//Check and create navigation data file when server starts
//Send the navigation data to the python folder, capturing by the display program
const navDataPath = path.join(__dirname, 'python', 'navigation_data.json');
if (!fs.existsSync(navDataPath)) {
    // Create empty navigation data file
    fs.writeFileSync(navDataPath, '{}');
}

//Enable CORS and JSON parsing
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

//Call the static files to display the web page HTML
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

//Handle navigation instruction routes
app.post('/navigation-instruction', (req, res) => {
    const pythonProcess = spawn('python3', ['navigation_processor.py', req.body.instruction]);
    pythonProcess.stdout.on('data', data => console.log(`Process result: ${data}`));
    res.json({ status: 'success' });
});

//Add GPS location route
app.get('/gps-location', (req, res) => {
    const pythonProcess = spawn('python3', [
        path.join(__dirname, 'python', 'NavigationProcess.py'),
        'get_gps'
    ]);
    
    //Capture the output of the Python program
    let dataString = '';
    
    pythonProcess.stdout.on('data', data => {
        dataString += data.toString();
    });
    
    pythonProcess.on('close', () => {
        try {
            res.json(JSON.parse(dataString));
        } catch (e) {
            res.status(500).json({ status: 'error' });
        }
    });
});

//Update navigation data
app.post('/update-navigation', (req, res) => {
    fs.writeFileSync(navDataPath, JSON.stringify(req.body));
    
    const pythonProcess = spawn('python3', [
        path.join(__dirname, 'python', 'InstructionDisplay.py')
    ], {
        cwd: path.join(__dirname, 'python')
    });
    
    pythonProcess.on('close', code => {
        res.json({ 
            status: code === 0 ? 'success' : 'error'
        });
    });
});

//Directly use express to listen
app.listen(port, '0.0.0.0', () => {
    console.log(`Server running on port:${port}`);
});