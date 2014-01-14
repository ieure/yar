```
 ,ggg,         gg            ,ggg, ,ggggggggggg,
dP""Y8a        88           dP""8IdP"""88""""""Y8,
Yb, `88        88          dP   88Yb,  88      `8b
 `"  88        88         dP    88 `"  88      ,8P
     88        88        ,8'    88     88aaaad8P"
     88        88        d88888888     88""""Yb,
     88       ,88  __   ,8"     88     88     "8b
     Y8b,___,d888 dP"  ,8P      Y8     88      `8i
      "Y88888P"88,Yb,_,dP       `8b,   88       Yb,
           ,ad8888 "Y8P"         `Y8   88        Y8
          d8P" 88
        ,d8'   88
        d8'    88
        88     88
        Y8,_ _,88
         "Y888P"
```

Yar is a tool for communicating with 1980s Data I/O universal
programmers. The original software is written for DOS and does not
work on modern hardware.


## Features

 - Works on modern hardware
 - Device family / pinout detection (with UniPak 2B)
 - Device lookup on GangPak, LogicPak, and UniPak 2B.
 - Can calculate checksums locally, including in ZIP archives.

## Status

Yar is rough around the edges, but can get from a host machine to the
programmer, and vice-versa. Dumping and programming devices can be
done from the programmer keypad.

 - Upload data to programmer: **WORKING**
 - Download data: **99% WORKING**. Dumps entire RAM contents, not
   just device contents, so it’s too slow.
 - Compute local checksums: **WORKING**
 - Device autodetection: **WORKING** (but untested)
 - Device lookup: **WORKING**.
 - Checksum files in ZIP archives: **WORKING**
 - Load device to RAM, dump to file (in one step): **WORKING**
 - Initiate device programming: **NOT WORKING**
 - Load file to RAM, program device: **NOT WORKING**
 - UniPak / UniPak 2 device lookup: **NOT WORKING** (I don’t have
   device lists for these)

## Hardware support

It works with the Data I/O 29B. Any Data I/O device which implements
the Computer Remote Control (CRC) protocol from the 29B manual should
work, but I haven’t tested this. Theoreticaly, it will work with the
29A.

Device autodetection requires a UniPak 2B; all other Paks require you
to specify the family and pinout, or device type. UniPak/UniPak 2
support is spotty, since I don’t have device lists for them.

## OS support

Yar is written in Python, and should be fairly portable. It uses
[PySerial](http://pyserial.sourceforge.net/index.html) to communicate
with the programmer, so if PySerial supports your OS, Yar should,
too. That being said, I have not tested it on any platform other than
Mac OS X.

## Installation

Not recommended at this time, but on UNIX-like systems:

```
$ git clone git@github.com:ieure/yar.git
$ cd yar
$ python setup.py bdist_egg
$ sudo easy_install dist/yar*.egg
```

(This will get easier as YAR matures)

## Examples

### Checksum ROMs



## Hacking

If you want to hack on yar, you should set up a Python virtual environment:

```
$ git clone git@github.com:ieure/yar.git
$ cd yar
$ virtualenv --no-site-packages .
$ . bin/activate
$ python setup.py develop
```

