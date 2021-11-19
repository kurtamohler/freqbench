# FreqBench

Frequency response test bench for audio electronics

If you want to measure a frequency response curve for some audio signal
processing device (like a guitar pedal), this tool can do that for you.

## Hardware Setup

Obviously, you must have an audio electronic device that you want to test.
We'll refer to this device as the DUT (device under test).

Next, you'll need a real time audio interface. Something like a Focusrite
Scarlett 2i2 will work. If you don't want to buy a separate audio interface,
you could probably get away with using your computer's builtin audio interface.
However, (at least on most Linux distros) you would probably need to install
and run a real-time audio driver like [JACK Audio Connection
Kit](https://jackaudio.org/).

Plug the output of your audio interface into the input of the DUT. Then plug
the output of the DUT to the input of the audio interface. This will allow us
to generate a signal with your computer, send it through the DUT, capture the
DUT's output, and process it with your computer.

## Software Requirements

[Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) must be installed.

## Installation

Run the following command to create and activate a conda environment.

```
$ conda env create -n freqbench -f environment.yaml
$ conda activate freqbench
```

Install the freqbench module.

```
$ python setup.py install
```

## Usage

First, you must find out the input and output device IDs for your audio
interface. You can run the following in your terminal.

```
$ python
>>> import freqbench
>>> freqbench.get_audio_devices()
```

This gives us all the audio input and output devices available on the system.
The number assocated with each of them on the left hand side is the ID of the
device.

Here is an example output:

```
DevicesInfo(
  input:
    6: "Scarlett 2i2 USB: Audio (hw:2,0)"
    7: "sysdefault"
    12: "default"
  output:
    0: "HDA NVidia: HDMI 0 (hw:1,3)"
    1: "HDA NVidia: HDMI 1 (hw:1,7)"
    2: "HDA NVidia: HDMI 2 (hw:1,8)"
    3: "HDA NVidia: HDMI 3 (hw:1,9)"
    4: "HDA NVidia: HDMI 4 (hw:1,10)"
    5: "HDA NVidia: HDMI 5 (hw:1,11)"
    6: "Scarlett 2i2 USB: Audio (hw:2,0)"
    7: "sysdefault"
    8: "front"
    9: "surround40"
    10: "surround51"
    11: "surround71"
    12: "default"
    13: "dmix"
)
```


In this example, we want to use the Scarlett 2i2 interface. We have to take
note that the input device ID is 6 and the output device ID is 6. Note that
the input and output IDs may not always be equal to each other. It depends on
your setup.
