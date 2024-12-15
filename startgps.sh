echo "gps will begin"

#Set maximum restart count
MAX_RESTARTS=20
RESTART_COUNT=0

cleanup() {
    # Clean up all cgps processes
    pkill cgps
    echo "Cleaning up GPS processes..."
}


trap cleanup EXIT

#Loop to restart GPS services
while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
    echo "GPS restart count: $((RESTART_COUNT + 1))/$MAX_RESTARTS"
    
    #Clean up existing cgps processes
    pkill cgps
    
    #Stop existing GPS services
    sudo systemctl stop gpsd.socket
    sudo systemctl stop gpsd.service
    
    #Wait for services to completely stop
    sleep 2
    
    #Restart GPS services
    sudo systemctl start gpsd.socket
    sudo systemctl start gpsd.service
    
    #Start cgps and record PID
    cgps -s &
    CGPS_PID=$!
    
    #Wait for 30 seconds
    sleep 30
    
    #Terminate current cgps process
    kill $CGPS_PID 2>/dev/null
    
    RESTART_COUNT=$((RESTART_COUNT + 1))
done

echo "GPS service has completed $MAX_RESTARTS restarts, program ending"
