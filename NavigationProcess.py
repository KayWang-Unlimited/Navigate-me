from gps import *

import json
import sys
import time

import threading
import atexit


# Some global variables for GPS tracking
current_value = None
running = True
gpsd = None

last_update = 0
lock = threading.Lock()

def setup_gps():
    global gpsd
    try:
        print(json.dumps({"debug": "Initializing GPSD connection"}), file=sys.stderr)
        gpsd = gps(mode=WATCH_ENABLE | WATCH_NEWSTYLE)
        
        #wait for 10 times to get a valid TPV report
        for _ in range(10):
            report = gpsd.next()
            print(json.dumps({"debug": f"Initialization report: {report['class']}"}), file=sys.stderr)
            if report['class'] == 'TPV':
                print(json.dumps({"debug": "GPSD connection fully established"}), file=sys.stderr)
                return
            time.sleep(0.1)
        
        print(json.dumps({"debug": "GPSD connection established, waiting for TPV data"}), file=sys.stderr)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": "GPS initialization failed",
            "message": str(e)
        }))
        sys.exit(1)

def update_gps():

#Continuously update GPS data in background thread
#for new GPS reports and updates current_value with latest position

    global current_value, last_update
    while running:
        try:
            report = gpsd.next()
            #Skip non-TPV reports
            if report['class'] != 'TPV':
                continue
            
            lat = getattr(report, 'lat', None)
            lon = getattr(report, 'lon', None)
            
            #Only update if we have valid coordinates
            if lat is not None and lon is not None:
                with lock:
                    current_value = {
                        'lat': float(lat),
                        'lng': float(lon),
                        'speed': float(getattr(report, 'speed', 0.0) or 0.0),
                        'track': float(getattr(report, 'track', 0.0) or 0.0),
                        'altitude': float(getattr(report, 'alt', 0.0) or 0.0),
                        'timestamp': time.time(),
                        'fix': getattr(report, 'mode', 0)
                    }
                    last_update = time.time()
        except Exception as e:
            print(json.dumps({"debug": f"GPS update error: {str(e)}"}), file=sys.stderr)
        time.sleep(0.2)

#Start background thread for GPS updates
def start_update_thread():
    update_thread = threading.Thread(target=update_gps)
    update_thread.daemon = True
    update_thread.start()
    return update_thread

def get_current_location():
# returns current GPS data if available and recent
    with lock:
        if current_value is None:
            return {"status": "error", "message": "No GPS data available"}
        
        if time.time() - last_update > 5:
            return {"status": "error", "message": "GPS data outdated"}
            
        return {
            "status": "success",
            "data": current_value
        }

def get_gps_location():
    # Attempts to get GPS location for up to 5 seconds

    print(json.dumps({"debug": "Starting GPS location request"}), file=sys.stderr)
    max_wait = 5
    start_time = time.time()
        
    while time.time() - start_time < max_wait:
        location_data = get_current_location()
        if location_data['status'] == 'success':
            print(json.dumps(location_data))
            return
        time.sleep(0.5)
            
    print(json.dumps({
        "status": "error",
        "message": "Timeout waiting for GPS data"
    }))
        


# Cleanup function
def cleanup():
    global running
    running = False

#For the initialization of GPS and start background updates
setup_gps()
start_update_thread()
atexit.register(cleanup)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'get_gps':
        get_gps_location()


