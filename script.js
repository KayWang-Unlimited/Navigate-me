let map;

let directionsService;
let directionsRenderer;

//define current position marker
let currentMarker = null;
//store current destination
let currentDestination = null;  

//Obtain current GPS location from server
async function getCurrentLocation() {

    const response = await fetch('/gps-location');
    const data = await response.json();

    return data.data;
}

function extractDirection(instruction) {
    instruction = instruction.toLowerCase();

    if (instruction.includes('north')) 
        return 'north';
    if (instruction.includes('south')) 
        return 'south';
    if (instruction.includes('east')) 
        return 'east';
    if (instruction.includes('west')) 
        return 'west';

    return null;
}
//Calculate difference between current heading and target direction
function getDirectionDifference(currentHeading, targetDirection) {

    const directionToAngle = {
        'north': 0,
        'northeast': 45,
        'east': 90,
        'southeast': 135,
        'south': 180,
        'southwest': 225,
        'west': 270,
        'northwest': 315
    };
    
    let targetAngle = directionToAngle[targetDirection.toLowerCase()];
    let diff = Math.abs(currentHeading - targetAngle);

    if (diff > 180) {
        diff = 360 - diff;
    }

    return diff;
}

// calculate and display route on map
async function calculateAndDisplayRoute(destination = null) {

    // Use provided destination or get from input
    const dest = destination || document.getElementById('destination').value;
    currentDestination = dest;

    const gpsData = await getCurrentLocation();
    const origin = { lat: gpsData.lat, lng: gpsData.lng };
    const currentHeading = gpsData.track;

    // Request route from Google Maps Directions API
    directionsService.route(
        {
            origin: origin,
            destination: dest,
            travelMode: google.maps.TravelMode.DRIVING,
        },

        async (response, status) => {
            if (status === "OK") {
                directionsRenderer.setDirections(response);
                const route = response.routes[0];
                displayRouteInstructions(route);
                
                if (route.legs[0] && route.legs[0].steps.length > 0) {
                    await updateNavigationInstructions(route, currentHeading);
                }
            }
        }
    );
}


// send updated navigation instructions to server
async function updateNavigationInstructions(route, currentHeading) {

    const firstStep = route.legs[0].steps[0];
    let instruction = firstStep.instructions;
    
    await fetch('/update-navigation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            navigation: {
                instruction: instruction.replace(/<[^>]*>/g, ''),
                distance: firstStep.distance.text,
                duration: firstStep.duration.text,
                total_distance: route.legs[0].distance.text,
                total_duration: route.legs[0].duration.text
            },
            gps: {
                current_heading: currentHeading,
                heading_timestamp: new Date().toISOString()
            }
        })
    });
}

//The route instructions display function
function displayRouteInstructions(route) {
    const instructionsPanel = document.getElementById('instructions');
    let instructions = '<h2>Navigation Instructions:</h2>';
    
    if (route.legs[0]) {
        instructions += `<p>Total Distance: ${route.legs[0].distance.text}</p>`;
        instructions += `<p>Estimated Time: ${route.legs[0].duration.text}</p>`;
        
        route.legs[0].steps.forEach((step, i) => {
            instructions += `<p>${i + 1}. ${step.instructions}</p>`;
        });
    }
    
    instructionsPanel.innerHTML = instructions;
}

//Update current position and recalculate route
async function updateGPSPosition() {
    const gpsData = await getCurrentLocation();
    
    if (currentMarker) {
        currentMarker.setPosition(gpsData);
    } else {
        currentMarker = new google.maps.Marker({
            position: gpsData,
            map: map,
            title: 'Current Location'
        });
    }
    
    map.setCenter(gpsData);
    
    if (currentDestination) {
        await calculateAndDisplayRoute(currentDestination);
    }
}

//Initialize the map informaton
function initMap() {

    // Set default location
    const defaultLocation = { lat: 42.436014996, lng: -76.486332196 };
    
    map = new google.maps.Map(document.getElementById("mapCanvas"), {
        zoom: 15,
        center: defaultLocation,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    
    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true
    });
    
    //Initial GPS position update
    updateGPSPosition();
    
    //Set up periodic GPS and route updates every 10 seconds
    setInterval(updateGPSPosition, 10000);
    
    //route planning button event listener
    document.getElementById('showRoute').addEventListener('click', () => {
        calculateAndDisplayRoute();
    });
}

