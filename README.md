# grjonathan/meridianpassage

Displays the current equation of time and solar declination on a Nokia 5110 LCD. Time is kept by a DS3231 real time clock. The equation of time and declination
can be used to determine latitude and longitude at the meridian passage of the sun (aka Local Apparent Noon).

## Hardware
- Raspberry Pi Pico
- ZS-042 DS3231 RTC
- Nokia 5110 LCD with Philips PCD8544 driver
- A sextant

## Software Requirements
- CircuitPython 8.2.9
- [adafruit_ds3231](https://github.com/adafruit/Adafruit_CircuitPython_DS3231)
- [adafruit_pcd8544](https://github.com/adafruit/Adafruit_CircuitPython_PCD8544)
- [5x8 font](https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/font5x8.bin)

## Usage
Techniques for using a sextant to determine location at meridian passage are covered in 
the *[American Practical Navigator](https://msi.nga.mil/Publications/APN), Chapter 19, Meridian Passage*. Another good
reference is the *[Davis Mark 3 Sextant Manual](https://www.davisinstruments.com/products/mark-3-sextant)*.


This program is expected to be less accurate than most almanacs. Calculations are limited by the single precision of
floating point numbers in CircuitPython. 

## References
Formulas are taken from Chapters 7, 25 and 28 of Jean Meeus' *Astronomical Algorithms (2nd edition), 1998*. The low
accuracy methods are used.
