import math
import time
import board, busio, digitalio
import adafruit_ds3231
import adafruit_pcd8544

# Instantiate the real time clock
i2c = busio.I2C(board.GP15, board.GP14)  # SCL, SDA
rtc = adafruit_ds3231.DS3231(i2c)

# Instantiate the display driver (Phillips PCD8544)
spi = busio.SPI(board.GP6, MOSI=board.GP7)  # serial clock, data output from main (TX)  "CLK" & "DIN"
dc = digitalio.DigitalInOut(board.GP4)  # data/command, data output from sub (RX)  "DC"
cs = digitalio.DigitalInOut(board.GP5)  # chip select  "CE"
reset = digitalio.DigitalInOut(board.GP0)  # reset  "RST"
display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)

# Display settings
display.bias = 5
display.contrast = 55

display.fill(0)
display.show()

# Uncomment the following line to set the time
# rtc.datetime = time.struct_time((2024, 1, 16, 00, 46, 30, 6, -1, -1)) # year, month, date, hour, minutes, seconds, week day

# Set timezone if the time above is set to local time. Do not consider daylight savings. If the time above is set to GMT, set tz = 0.
tz = 0 # negative for east of GMT 

# Lookup table for names of months
months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

def julian_century(year, month, day, hour, minutes, seconds, tz):
    
    # If the date is in January or February, it is considered to be in the 13th or 14th month of the preceding year.
    if month <= 2:
        year = year - 1
        month = month + 12
    
    A = int(year/100)
    B = 2 - A + int(A/4)
    
    # Julian day
    JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B -1524.5
    JD = JD + (hour - tz + minutes / 60 + seconds / 3600) / 24  # add the hour, minutes, seconds, and make the timezone correction

    T = (JD - 2451545.) / 36525  # convert Julian Day to Julian Century
    return T

def sun_eq_ctr(JC, M):
    C = (1.914602 - 0.004817 * JC - 0.000014 * JC ** 2) * math.sin(math.radians(M))\
    + (0.019993 - 0.000101 * JC) * math.sin(math.radians(2 * M))\
    + 0.000289 * math.sin(math.radians(3 * M)) 
    return C

def obliquity(JC):
    term_1 = 23 + 26 / 60 + 21.448 / 3600
    term_2 = 46.8150 / 3600
    term_3 = 0.00059 / 3600
    term_4 = 0.001813 / 3600
    epsilon = term_1 - term_2 * JC - term_3 * JC ** 2 + term_4 * JC ** 3
    return epsilon

def eqn_of_time(epsilon, L_0, e, M):
    
    y = math.tan(math.radians(epsilon / 2)) ** 2
    
    eot = y * math.sin(2 * math.radians(L_0)) - 2 * e * math.sin(math.radians(M)) + 4 * e * y * math.sin(math.radians(M)) * math.cos(2 * math.radians(L_0)) - 0.5 * y ** 2 * math.sin(4 * math.radians(L_0)) - 1.25 * e ** 2 * math.sin(2 * math.radians(M))
    # Convert from radians to degrees
    eot = math.degrees(eot)
    return eot

# Convert decimal degrees to degrees, minutes, seconds
def dd_to_dms(dd):
    d = math.floor(abs(dd))
    s = math.floor((abs(dd) - d) * 3600)
    m, s = divmod(s, 60)
    return d, m, s

# Main loop
while True:
    t = rtc.datetime
    
    # Julian centuries since 2000 January 1.5 TD
    JC = julian_century(year=t.tm_year, month=t.tm_mon, day=t.tm_mday, hour=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec, tz=tz)
    
    # Heliocentric longitude
    L_0 = (280.46646 + 36000.76983 * JC + 0.0003032 * JC ** 2) % 360
    
    # Mean anomaly of the sun
    M = (357.52911 + 35999.05029 * JC - 0.0001537 * JC ** 2) % 360
    
    # Eccentricity of the earth's orbit
    e = 0.016708634 - 0.000042037 * JC - 0.000000127 * JC ** 2
    
    # Sun's equation of the centre
    C = sun_eq_ctr(JC, M)
    
    # Sun's true longitude (geometric longitude)
    L = L_0 + C
    
    # Sun's true anomaly
    v = M + C
    
    # Distance between the centres of the sun and the earth (astronomical units)
    R = 1.000001018 * (1 - e ** 2) / (1 + e * math.cos(math.radians(v)))
    
    # Obliquity of the ecliptic
    epsilon = obliquity(JC)
    
    # Declination
    declination = math.degrees(math.asin(math.sin(math.radians(epsilon)) * math.sin(math.radians(L))))
    
    # Equation of time
    eot = eqn_of_time(epsilon, L_0, e, M)
        
    # Format declination
    declination_sign = 'S' if declination < 0. else 'N'
    declination_deg, declination_minutes, declination_seconds = dd_to_dms(declination)
    
#   Format EoT
    eot_sign = 'E' if eot < 0. else 'W'
    eot_deg, eot_minutes, eot_seconds = dd_to_dms(eot) # degrees, arc minutes, arc seconds
    # Convert from degrees to decimal seconds
    eot_t_minutes, eot_t_seconds = divmod(math.floor(abs(eot * 4 * 60)), 60) # time the sun is fast or slow 
    
#     print(dd_to_dms(eot), dd_to_dms(declination))
    
    display.fill(0)
    display.text(f"{months[int(t.tm_mon)-1]} {t.tm_mday} {t.tm_year}", 9, 0, 1)
    display.text("{}:{:0>2}:{:0>2}".format(t.tm_hour, t.tm_min, t.tm_sec), 18, 10, 1)
    display.text("EoT {:0>2}m {:0>2}s {}".format(eot_t_minutes, eot_t_seconds, eot_sign), 0, 20, 1)
    display.text("EoT {:0>2} {:0>2}'{:0>2}{}{}".format(eot_deg, eot_minutes, eot_seconds, '"', eot_sign), 0, 30, 1)
    display.text("Dec {:0>2} {:0>2}'{:0>2}{}{}".format(declination_deg, declination_minutes, declination_seconds, '"', declination_sign), 0, 40, 1)
    display.show()
    time.sleep(0.72)  # calibrated for 1s including execution time
