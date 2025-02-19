import json
import time
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

# Set up logging
logging.basicConfig(
    filename='cs2_gsi.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to update RGB devices
def update_rgb_color(color, flash_duration=None):
    try:
        for device in rgb_client.devices:
            if "direct" in [mode.name.lower() for mode in device.modes]:
                device.set_mode("Direct")
            device.set_color(color)
            logging.info("✅ %s set to %s", device.name, color)
        
        if flash_duration:
            time.sleep(flash_duration)
            # Reset to default color after flash
            default_color = RGBColor(255, 0, 255)  # Blue
            for device in rgb_client.devices:
                device.set_color(default_color)
    except Exception as e:
        logging.error("⚠️ Error updating OpenRGB devices: %s", e)

# OpenRGB Client setup
try:
    rgb_client = OpenRGBClient()
    logging.info("🔗 Connected to OpenRGB. Devices detected: %s", [device.name for device in rgb_client.devices])
    
    # Test connection with orange color
    test_color = RGBColor(255, 165, 0)  # 🟠 Orange
    update_rgb_color(test_color)
except Exception as e:
    logging.error("❌ Error connecting to OpenRGB: %s", e)
    exit(1)

# CS2 Secret Key (Must match gamestate_integration_openrgb.cfg)
SECRET_KEY = "rx5w2bXmCCWJu6"

# Store last known states
last_known_states = {
    "round_phase": None,
    "player_health": 100,
    "match_phase": None,
    "previous_kills": 0
}

# Function to determine colors based on game state
def get_color(gsi_data):
    player = gsi_data.get("player", {})
    map_data = gsi_data.get("map", {})
    round_data = gsi_data.get("round", {})

    # Check for flashbang effect
    if player.get("state", {}).get("flashed", 0) > 0:
        return RGBColor(255, 255, 255), 1.5
     
    if player.get("state", {}).get("burning", 0) > 0:
        return RGBColor(255, 178, 0), .6 # White flash for 0.5s
    
    if player.get("state", {}).get("smoked", 0) > 0:
        return RGBColor(100, 100, 100), .6 #
    


    # Player activity checks
    activity = player.get("activity", "")
    if activity == "menu":
        phase = map_data.get("phase", "")
        if phase == "loadingscreen":
            return RGBColor(147, 112, 219), None  # 💜 Purple for loading
        elif phase == "searching":
            return RGBColor(255, 215, 0), None  # 💛 Gold for searching
        return RGBColor(0, 255, 0), None  # 🟢 Green for main menu

    # Get current health
    current_health = player.get("state", {}).get("health", 100)

    # Health-based color logic
    if current_health >= 80:
        color = RGBColor(0, 255, 0)  # 🟢 Green
    elif current_health >= 50:
        color = RGBColor(255, 255, 0)  # 💛 Yellow
    elif current_health >= 20:
        color = RGBColor(255, 165, 0)  # 🟠 Orange
    else:
        color = RGBColor(255, 0, 0)  # 🔴 Red

    # Update last known health state
    last_known_states["player_health"] = current_health

    # Check for new kill
    current_kills = player.get("match_stats", {}).get("kills", 0)
    if current_kills > last_known_states["previous_kills"]:
        last_known_states["previous_kills"] = current_kills
        return RGBColor(145, 200, 66), 0.5  # 🟢 Green flash for kill

    # Bomb states
    bomb = round_data.get("bomb")
    if bomb == "planted":
        return RGBColor(0, 224, 245), None  # Cyan when bomb is planted
    elif bomb == "exploded":
        return RGBColor(255, 200, 0), 1.0  # Orange for bomb explosion

    # Round win states
    win = round_data.get("win_team")
    if win == "T":
        return RGBColor(235, 160, 0), None  # Orange for Terrorist win
    elif win == "CT":
        return RGBColor(0, 255, 255), None  # Cyan for Counter-Terrorist win

    return color, None

     

# GSI Handler
class GSIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            gsi_data = json.loads(post_data.decode('utf-8'))
            logging.info("📩 Received GSI Data: %s", json.dumps(gsi_data, indent=4))
            
            # Validate secret key
            received_token = gsi_data.get("auth", {}).get("key1", "")
            if received_token != SECRET_KEY:
                logging.warning("❌ Unauthorized request received! Got token: %s", received_token)
                self.send_response(403)
                self.end_headers()
                return
            
            # Get appropriate color based on game state
            color, flash_duration = get_color(gsi_data)
            update_rgb_color(color, flash_duration)
            
        except json.JSONDecodeError as e:
            logging.error("⚠️ Invalid JSON received: %s", e)
        except Exception as e:
            logging.error("⚠️ Error processing GSI data: %s", e)
        
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging to avoid duplicate logs
        pass

# Start HTTP Server
def run_server():
    server_address = ('', 5000)
    httpd = HTTPServer(server_address, GSIHandler)
    logging.info("🚀 CS2 GSI server running on port 5000...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("👋 Server shutting down...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()