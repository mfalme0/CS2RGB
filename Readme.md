# CS2 OpenRGB Game State Integration

This project integrates Counter-Strike 2 (CS2) with OpenRGB to dynamically change RGB lighting effects based on game events using the Game State Integration (GSI) API.

## Features
- Sync RGB lighting with CS2 game events
- Flash RGB effects for in-game actions (flashbangs, kills, bomb events, etc.)
- Detects and applies colors based on health, round status, and environment effects
- Logs all received game state data for debugging
- Secure authentication using a secret key

## Prerequisites
- Python 3.x
- OpenRGB installed and running
- CS2 with Game State Integration enabled

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/mfalme0/cs2rgb.git
   cd cs2rgb
   ```
2. Install dependencies:
   ```sh
   pip install openrgb-python
   ```
3. Set up CS2 Game State Integration:
   - Navigate to your CS2 config folder (usually `C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg`)
   - Create a file named `gamestate_integration_openrgb.cfg` with the following content:
     ```json
     "CSGO_GSI": {
         "uri": "http://localhost:5000",
         "timeout": 5.0,
         "auth": {
             "key1": "rx5w2bXmCCWJu6"
         },
         "heartbeat": 10.0,
         "data": {
             "provider": true,
             "player": true,
             "round": true,
             "map": true
         }
     }
     ```

## Usage
1. Start the OpenRGB application.
2. Run the script:
   ```sh
   python cs2rgb.py
   ```
3. Launch CS2 and start a match. Your RGB devices should react to in-game events.

## Game Event Mappings
- **Health Status:**
  - 🟢 Green (Healthy, 80-100 HP)
  - 💛 Yellow (Medium, 50-79 HP)
  - 🟠 Orange (Low, 20-49 HP)
  - 🔴 Red (Critical, 1-19 HP)
- **Environment Effects:**
  - ⚪ White Flash (Flashed)
  - 🔥 Orange Flicker (Burning)
  - 🌫️ Gray (Smoked)
- **Game Phases:**
  - 💜 Purple (Loading Screen)
  - 💛 Gold (Searching)
  - 🟢 Green (Main Menu)
- **Round Events:**
  - 🔵 Cyan (Bomb Planted)
  - 🟠 Orange (Bomb Exploded)
  - 🟢 Green Flash (Kill Confirmed)
  - 🟠 Orange (Terrorists Win)
  - 🔵 Cyan (Counter-Terrorists Win)

## Logs
Game events and system logs are stored in `cs2_gsi.log`.

## Troubleshooting
- Ensure OpenRGB is running before starting the script.
- Check the `cs2_gsi.log` file for errors.
- Verify the `gamestate_integration_openrgb.cfg` file is correctly placed and formatted.

## License
This project is open-source and available under the MIT License.

## Author
[Your Name](https://github.com/mfalme0)

