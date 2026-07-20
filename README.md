# RoadSense - Hardware Prototype

This folder has two parts:
- `raspberry_pi/` - the Python code that runs on your Pi (reads sensors, decides on a near-miss, logs it, triggers the buzzer + motor)
- `esp32/roadsense_esp32/` - the Arduino sketch that runs on your ESP32 (heartbeat matrix + buzzer)

## Part A - Flash the ESP32 first

1. Open `esp32/roadsense_esp32/roadsense_esp32.ino` in the Arduino IDE.
2. Install the library it needs: **Sketch > Include Library > Manage Libraries**, search `LedControl` (by Eberhard Fahle), click Install.
3. Check the wiring matches the comment at the top of the `.ino` file (matrix on GPIO 23/18/5, buzzer on GPIO 4). Change the pin numbers in the code if you wired it differently.
4. Select your board (**Tools > Board > ESP32 Dev Module**, or your NodeMCU-32S equivalent) and the correct COM/USB port.
5. Click Upload.
6. Once it's uploaded, open the Serial Monitor (top-right icon, set baud rate to `115200`). You should see `ESP32_READY` printed, and the dot-matrix should already be pulsing like a heartbeat. **Close the Serial Monitor afterwards** - only one program can use the serial port at a time, and the Pi will need it next.

## Part B - Set up the Raspberry Pi

1. Copy the `raspberry_pi/` folder onto your Pi (via `scp`, a USB drive, or `git clone` if you push this to a repo).

2. Install the Python packages that come from pip:
   ```
   cd raspberry_pi
   pip install -r requirements.txt
   ```

3. Install these two separately via `apt` instead of `pip` - they're much more reliable this way on a Raspberry Pi:
   ```
   sudo apt update
   sudo apt install -y python3-opencv python3-picamera2
   ```

4. Plug in the ESP32 via USB, then find its port:
   ```
   ls /dev/tty*
   ```
   unplug it, run the command again, and see which entry disappeared - that's your ESP32 (usually `/dev/ttyUSB0`). Open `config.py` and update `ESP32_SERIAL_PORT` if it's different.

5. If you have a GPS module, do the same thing to find its port and update `GPS_SERIAL_PORT` in `config.py`. If you don't have GPS connected yet, don't worry - the code handles that gracefully and just logs events without a location.

6. Double check the GPIO pin numbers in `config.py` match how you actually wired the ultrasonic sensor and motor driver. The motor pins already match your `motor_test.py` (17, 27, 22, 25).

**(Optional, skip this for now)** — Real object classification on the camera needs two extra files (`MobileNetSSD_deploy.prototxt` and `MobileNetSSD_deploy.caffemodel`) placed in the `models/` folder. Without them, the camera just reports "unknown", and near-miss detection still works fine using the IMU + ultrasonic sensors alone. Add this later once the core pipeline is working - it's not needed to test or demo the system today.

## Part C - Test it, step by step

**Test 1: Does the response pipeline work at all?** (buzzer, motor, logging - without needing real sensor conditions)
1. Run: `python3 simulate_near_miss.py`
2. You should hear the buzzer beep, see the car reverse for 2 seconds and stop, and see a message saying the event was saved.
3. Run: `python3 view_events.py` — you should see that fake event listed.

If this works, your whole response chain (ESP32 link, motor, storage) is solid, and any issues after this point are purely about sensor tuning, not wiring.

**Test 2: Does live detection work?**
1. Run: `python3 main.py`
2. Leave it running and watch the terminal - it will print sensor readings continuously.
3. To simulate a real near-miss: pick the rig up and give it a sharp, sudden jerk/shake (to trigger the IMU) **at the same time as** moving your hand or an object very close (within ~40cm) to the ultrasonic sensor. Both need to happen close together for it to count - that's intentional, it's the same two-part rule real cars use to avoid false alarms.
4. Within about a second, you should see:
   - A `NEAR-MISS DETECTED` message printed in the terminal, with a severity score
   - The buzzer on the ESP32 beeping
   - The car reversing for 2 seconds, then stopping
5. Press `Ctrl+C` to stop the program at any time.
6. Run `python3 view_events.py` again - your real test event should now be listed alongside the earlier fake one.

**If nothing triggers:** open `config.py` and lower `MPU6050_JERK_THRESHOLD` (try 5.0) and/or raise `ULTRASONIC_NEAR_MISS_CM` (try 60) - your rig's motion is gentler than a full-size car so the default numbers may be too strict.

**If the ESP32 doesn't respond:** check `config.py`'s `ESP32_SERIAL_PORT` is correct, and make sure the Arduino Serial Monitor is closed on your computer (it locks the port).

## What happens to the data, right now

Since your Express backend isn't built yet, everything just stays safely on the Pi in a local SQLite file at `data/events.db` - nothing is lost, you can inspect it any time with `view_events.py`. Once your backend is running, open `config.py`, set `SEND_TO_BACKEND = True` and update `BACKEND_URL`, and every new event will automatically also get POSTed there. Nothing else about this code needs to change for that to work.
