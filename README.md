# FreqBench

Frequency response test bench for audio electronics

You have a guitar pedal or some other audio signal processing device with an
input and an output, and you're interested in finding out which audio
frequencies it accentuates and which ones it dimishes. In other words, you want
to create a frequency response curve. You can do this with FreqBench.

## Hardware Setup

Obviously, you must have an audio electronic device that you want to test.
For instance, a guitar pedal. I'll refer to this device as the DUT (device
under test).

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

