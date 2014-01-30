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

 - Upload data to programmer: **WORKING**. Uses binary format only.
 - Download data: **99% WORKING**. Dumps entire RAM contents, not
   just device contents, so it’s too slow.
 - Compute local checksums: **WORKING**
 - Checksum files in ZIP archives: **WORKING**
 - Get programmer RAM checksum: **WORKING**
 - Device autodetection: **WORKING** (but untested)
 - Device lookup: **WORKING**
 - Load device to RAM, dump to file (in one step): **WORKING**
 - Detect device connection: **SORT OF WORKING**. Always fails the
   first time for some reason, so you get a prompt saying to put the
   device in remote mode before it notices that it’s connected.
 - Initiate device programming: **NOT WORKING**. Plumbing is there,
   just need a CLI command hooked up.
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

```
$ git clone git@github.com:ieure/yar.git
$ cd yar
$ python setup.py bdist_egg
$ sudo easy_install dist/yar*.egg
```

(This will get easier as YAR matures)

## Example Commands

### Checksumming

You can checksum files inside ZIP archives:

```
$ yar checksum digdugat.zip
digdugat.zip:136007.107 059faa
digdugat.zip:136007.108 030191
digdugat.zip:136007.114 03500c
digdugat.zip:136007.115 060744
digdugat.zip:136007.116 04018e
digdugat.zip:136007.117 02fab8
digdugat.zip:136007.118 043d78
digdugat.zip:136007.119 036491
digdugat.zip:136007.201 062775
digdugat.zip:136007.202 0618fc
digdugat.zip:136007.203 067a5f
digdugat.zip:136007.204 05a4aa
digdugat.zip:136007.205 06bf0a
digdugat.zip:136007.206 06c2aa
```

Or plain files:

```
$ yar checksum 136007.104
136007.104 05b8aa
```

Wildcards work how you’d expect:
```
$ yar checksum 136007.*
136007.104 05b8aa
136007.107 059faa
136007.108 030191
136007.114 03500c
136007.115 060744
136007.116 04018e
136007.117 02fab8
136007.118 043d78
136007.119 036491
136007.201 062775
136007.202 0618fc
136007.203 067a5f
136007.204 05a4aa
136007.205 06bf0a
136007.206 06c2aa
```

### Look up device

You can look up the family/pinout of devices based on the part number:

```
$ yar --pak unipak2b lookup am2732
am2732 family 019 pinout 024
```

Incomplete part numbers will show similar parts:

```
$ yar --pak unipak2b lookup am273
No device `am273' found. Similar devices:
AMD 2732
AMD 1736
AMD 2708
AMD 2716
AMD 2732A
AMD 2732B
AMD 2764
AMD 2764
AMD 27C43
AMD 27S13
```

If multiple incompatible parts match, it will tell you:
```
$ yar --pak unipak2b lookup 2732
Ambiguous device `2732', matches: AMD 2732, FUJ 2732, INT 2732, MIK 2732, MIT 2732, NAT 2732, NEC 2732, SGS 2732, TEX 2732, TOS 2732
```

If multiple parts are matched, but have the same family/pinout, it
just works:
```
$ yar --pak unipak2b lookup 2716
2716 family 019 pinout 023
```

### Upload data to programmer

The `upload` command will zero out the programmer RAM and load the
specified file:

```
$ yar upload 136007.104
Put device in remote mode: SELECT F1 START START...connected.
4096 bytes in 0m04s @1001b/s
```

### Load device into programmer RAM

This command zeroes the programmer RAM, then loads a device’s
contents:

```
$ yar --pak unipak2b --device am2732 read
Insert device into indicated socket, then press START...ok.
Checksum: B8AA
```

### Download programmer RAM

Dump RAM contents to a file:

```
$ yar download rom_dump.bin
[1/262144] bytes, 00% @82241b/s, eta 0m03s
[97/262144] bytes, 00% @967b/s, eta 4m30s
...
[262053/262144] bytes, 99% @959b/s, eta 0m00s
262144 bytes in 4m33s @959b/s
```

### Read device, download RAM

The previous two examples, in one step:

```
$ yar --pak unipak2b --device am2732 download_device rom_dump.bin
```

## Hacking

If you want to hack on yar, you should set up a Python virtual environment:

```
$ git clone git@github.com:ieure/yar.git
$ cd yar
$ virtualenv --no-site-packages .
$ . bin/activate
$ python setup.py develop
```

