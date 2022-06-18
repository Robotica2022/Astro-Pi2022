# code written by team JASE (Junior Association for Space Exploration), from Guimaraes, Portugal
from pathlib import Path
from logzero import logger, logfile
from sense_hat import SenseHat
from orbit import ISS
from time import sleep
from datetime import datetime, timedelta
from skyfield.api import load
from random import randint
from gpiozero import MotionSensor
import csv

r = (155, 0, 0)
g = (0, 155, 0)
b = (0, 0, 155)
y = (155, 155, 0)
p = (0, 0, 0)
H = (153, 76, 0)
S = (255, 179, 102)
W = (155, 155, 155)
E = (0, 102, 0)

# Image of Portuguese flag
flag = [
    g,g,g,r,r,r,r,r,
    g,g,g,r,r,r,r,r,
    g,g,g,r,r,r,r,r,
    g,g,y,y,r,r,r,r,
    g,g,y,y,r,r,r,r,
    g,g,g,r,r,r,r,r,
    g,g,g,r,r,r,r,r,
    g,g,g,r,r,r,r,r
    ]

# Image of astronaut
astro = [
     p, H, H, H, H, H, H, p,
     S, S, S, S, S, S, S, H,
     S, p, p, S, p, p, S, H,
     S, p, E, S, p, E, S, H,
     S, S, S, S, S, S, S, S,
     S, S, S, S, S, S, S, S,
     S, S, S, p, S, S, S, H,
     p, S, S, S, S, S, S, p
     ]

# Set up Sense Hat
sh = SenseHat()

def create_csv_file(data_file):
    """Create a new CSV file and add the header row"""
    with open(data_file, 'w') as f:
        writer = csv.writer(f)
        header = ("Counter","Date/time", "Location", "Temperature", "Humidity", "acc_x", "acc_y", "acc_z", "yaw", "pitch",
                  "roll", "gyro_x", "gyro_y", "gyro_z")
        writer.writerow(header)

def add_csv_data(data_file, data):
    """Add a row of data to the data_file CSV"""
    with open(data_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)
    

def get_sh_data():
    sh_data = []

    acc = sh.get_accelerometer_raw()
    acc_x = round(acc.get('x'), 3)
    acc_y = round(acc.get('y'), 3)
    acc_z = round(acc.get('z'), 3)
        
    orientation = sh.get_orientation()
    yaw = round(orientation.get('yaw'), 3)
    pitch = round(orientation.get('pitch'), 3)
    roll = round(orientation.get('roll'), 3)
        
    gyro = sh.get_gyroscope_raw()
    gyro_x =round(gyro.get('x'), 3)
    gyro_y =round(gyro.get('y'), 3)
    gyro_z =round(gyro.get('z'), 3)
    
    return (acc_x, acc_y, acc_z, yaw, pitch, roll, gyro_x, gyro_y, gyro_z)

# Set accelerometer parameters
def get_acc_meas():    
    acc = sh.get_accelerometer_raw()
    x1 = round(acc.get('x'), 3)
    y1 = round(acc.get('y'), 3)
    z1 = round(acc.get('z'), 3)
    #sleep(1)
    return (x1, y1, z1)


#--------------Main----------------------------------
if __name__ == "__main__":
    # Display Portuguese flag and introduction
    sh.set_pixels(flag)
    sleep(1)
    sh.show_message("Program Start", scroll_speed=0.09, text_colour=b)
    
    base_folder = Path(__file__).parent.resolve()

    # Set a logfile name
    logfile(base_folder/"JASE.log")
    logger.info(f"Mission Status: Initiated")
    
    # Initialise the CSV file
    data_file = base_folder/"data.csv"
    create_csv_file(data_file)


    # Initialise the counter
    counter = 1
    # Record the start and current time
    start_time = datetime.now()
    now_time = datetime.now()
    # Run a loop for (almost) three hours

    # Create empty list for baseline values              
    base_value_x = []
    base_value_y = []
    base_value_z = [] 

    pir = MotionSensor(pin=12)
    
while (now_time < start_time + timedelta(minutes=175)):
    try:
        sl = 2 # sleep time, takes 2 to 3 seconds for each acquiring 
        # randomly iluminates color pixels on LED matrix to show that the code is running
        a = randint(0, 7)
        b = randint(0, 7)
        c = randint(10,155)
        d = randint(10,155)
        e = randint(10, 155)
        sh.set_pixel(a, b, c, d, e)
      
        # check the pir sensor for movement and display image if true
        if pir.motion_detected:
            sh.set_pixels(astro)
            sleep(1)
            sh.clear()
            logger.info(f"Astronaut detected")
        
        # Get temperature and humidity data
        temperature = round(sh.temperature, 4)
        humidity = round(sh.humidity, 4)
        # Get coordinates of location on Earth below the ISS
        # Obtain the current time `t`
        t = load.timescale().now()
        # Compute where the ISS is at time `t`
        position = ISS.at(t)
        # Compute the coordinates of the Earth location directly beneath the ISS
        location = position.subpoint()
        
        # get acceleration, orientation and gyroscope data
        acc_x, acc_y, acc_z, yaw, pitch, roll, gyro_x, gyro_y, gyro_z = get_sh_data()
        
        # Save the data to the file
        data = (
            counter,
            datetime.now(),
            location,
            temperature,
            humidity,
            acc_x,
            acc_y,
            acc_z,
            yaw,
            pitch,
            roll,
            gyro_x,
            gyro_y,
            gyro_z
        )
        add_csv_data(data_file, data)
        # Measures accelerometer values
        base_value_x, base_value_y, base_value_z = get_acc_meas()
        
        mov = []
        
        if len(mov) ==0 :
                
            accel_x, accel_y, accel_z = get_acc_meas()  

            # Compares values with baseline
            ax=round(accel_x - base_value_x, 3)
            ay=round(accel_y - base_value_y, 3)
            az=round(accel_z - base_value_z, 3)
         
            if abs(ax) > 0.005:
                sh.clear()
                mov += "x"
              
            if abs(ay)> 0.005:
                sh.clear()
                mov += "y"

            if abs(az) > 0.005:
                sh.clear()
                mov += "z"

            # Display message if ISS motion is detected and store data        
            if len(mov)>0:    
                logger.info(f"ISS motion detected in: {str(mov)}")
                logger.info(f"x=%s, y=%s, z=%s" % (ax, ay, az))
                sh.show_message("ISS Motion detected", scroll_speed=0.04, text_colour=r)
                sl=0  # not to wait to long
                    
        sleep(sl)
        
        counter += 1
        sleep(2)
        # Update the current time
        now_time = datetime.now()
        
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}')
        

logger.info(f"Mission Status: Complete")