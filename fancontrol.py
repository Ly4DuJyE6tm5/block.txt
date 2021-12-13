from bs4 import BeautifulSoup
from datetime import datetime
from gpiozero import OutputDevice
import requests
import subprocess
import time


ON_THRESHOLD = 52  # (degrees Celsius) Fan kicks on at this temperature.
OFF_THRESHOLD = 37  # (degress Celsius) Fan shuts off at this temperature.
SLEEP_INTERVAL = 15  # (seconds) How often we check the core temperature.
GPIO_PIN = 14  # Which GPIO pin you're using to control the fan.
piholes = ["10.0.0.2", "10.0.0.3"]


def get_temp():
    """Get the core temperature.
    Run a shell script to get the core temp and parse the output.
    Raises:
        RuntimeError: if response cannot be parsed.
    Returns:
        float: The core temperature in degrees Celsius.
    """
    temperatures = []
    output = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True)
    temp_str = output.stdout.decode()
    for pis in piholes:
        response = requests.get("http://" + pis + "/admin")
        soup = BeautifulSoup(response.text, "html.parser")
        temperature = float(soup.find(id="rawtemp").getText())
        temperatures.append(temperature)
    temperatures.append(float(temp_str.split("=")[1].split("'")[0]))
    highest = max(temperatures, key=lambda x: float(x))
    # print("highest: " + str(highest))
    try:
        return highest
        # return float(temp_str.split("=")[1].split("'")[0])
    except (IndexError, ValueError):
        raise RuntimeError("Could not parse temperature output.")


if __name__ == "__main__":
    # Validate the on and off thresholds
    if OFF_THRESHOLD >= ON_THRESHOLD:
        raise RuntimeError("OFF_THRESHOLD must be less than ON_THRESHOLD")

    fan = OutputDevice(GPIO_PIN)

    while True:
        temp = get_temp()
        # print("temp " + str(temp) + " ON_THRESHOLD: " + str(ON_THRESHOLD))
        # print('fan value: ' + str(fan.value))

        # Start the fan if the temperature has reached the limit and the fan
        # isn't already running.
        # NOTE: `fan.value` returns 1 for "on" and 0 for "off"
        # if temp > ON_THRESHOLD:
        if temp > ON_THRESHOLD and not fan.value:
            fan.on()
            #time.sleep(SLEEP_INTERVAL)
            print("fan on " + str(temp) + " is > than " + str(ON_THRESHOLD))
            with open("fancontrol.log", "a") as file:
                file.write("Turned on with %d at: %s\n" % (temp, datetime.now()))

        # Stop the fan if the fan is running and the temperature has dropped
        # to 10 degrees below the limit.
        elif fan.value and temp < OFF_THRESHOLD:
            fan.off()
            print("fan off " + str(temp) + " is < than " + str(ON_THRESHOLD))
            with open("fancontrol.log", "a") as file:
                file.write("Turned off with %d at: %s\n" % (temp, datetime.now()))

        time.sleep(SLEEP_INTERVAL)
        print("sleeping " + str(SLEEP_INTERVAL) + " temperature: " + str(temp))
