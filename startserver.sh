echo "server service will begin"
sleep 4
cd /home/pi/n6

#Start the server in the background
sudo node server.js &
SERVER_PID=$!

#Set cleanup function on exit to clean up server process
cleanup() {
    echo "Cleaning up server process..."
    kill $SERVER_PID 2>/dev/null
    echo "Server process terminated."
}

#Call cleanup function on exit
trap cleanup EXIT

#Wait for the server process to finish
wait $SERVER_PID