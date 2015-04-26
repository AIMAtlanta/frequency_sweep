# frequency_sweep
Python utility coordinating HT1025G and DS1102E to measure frequency
response

## Overview
This utility makes use of the
[rigol_usbtmc](https://github.com/AIMAtlanta/Rigol_USBTMC)
(oscilloscope) and
[htdds_wrapper](https://github.com/AIMAtlanta/Hantek_1025G)
(function generator) modules to sweep both instruments over a range of
frequencies in order to determine the electronic frequency response of
a system under test (SUT).

The oscilloscope in particular is instructed to follow the response of
the SUT by guessing the expected output from the function generator
setting, and adjusting the acquisition settings if the expected signal
is not observed.

## Usage
A sweep controller can be instantiated with

    import sweep_util
    sweep = sweep_util.Sweep()

The sweep controller will automatically attempt to connect to a Hantek
1025G DDS function generator and a Rigol DS1000 oscilloscope.

Calling `sweep_util.help()` will provide some basic usage information.

See the README files for rigol_usbtmc and htdds_wrapper for additional
information about device setup.

## License
The MIT License (MIT)

Copyright (c) 2015, Atlanta Instrumentation and Measurement, LLC

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the
following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Author
Kevin D. Nielson (2015.04.19)

[AIM - Atlanta Instrumentation and Measurement, LLC](www.aimatlanta.com)

