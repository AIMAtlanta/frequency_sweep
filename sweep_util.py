# -*- coding: utf-8 -*-

import htdds_wrapper
import rigol_usbtmc

import numpy as np
import time

import matplotlib.pyplot as plt


class Sweep(object):

    """Class for managing frequency sweeps and device interfaces."""

    def __init__(self):
        self.scope = rigol_usbtmc.Scope()
        self.ht = htdds_wrapper.HantekDDS()
        self.halt = False

    def __del__(self):
        self.scope.close()

    def sweep(self, fstart=1e3, fend=6e7, nsteps=None, inc=10 ** 0.1, ltype='log',
              amp=2.5, ofs=0, averages=64, dwell=1):

        # set scope averaging
        if averages == 1:
            self.scope.acquireMode = 'NORM'
        if averages in [2 ** p for p in range(0, 8)]:
            self.scope.acquireMode = 'AVER'
            self.scope.averages = averages
        else:
            raise ValueError('Number of samples to average, `averages`, must be a power of 2 between 1 and 256.')

        self.halt = False
        freq_array = gen_frequency_array(fstart, fend, nsteps, inc=inc, ltype=ltype)

        # Initial estimate for vertical scale
        _vdiv = amp / 3.
        self.scope.ch1.verticalGain = _vdiv
        self.scope.ch1.verticalOffset = ofs

        self.scope.acquireMode = 'NORM'

        data = np.zeros_like(freq_array)
        for idx, frq in enumerate(freq_array):
            if self.halt:
                return None
            self.ht.drive_periodic(amplitude=amp, frequency=frq, offset=ofs)
            time.sleep(0.05)
            # Keep between 3 and 6 periods on the scope
            self.scope.timescale = 1. / (2.5 * frq)
            time.sleep(0.5 * dwell)
            v_range = self.scope.ch1.meas_Vpp()
            v_avg = self.scope.ch1.meas_Vavg()
            _vdiv = v_range / 4  # Target 2/3 of display range
            if v_range > 1e37:
                self.scope.auto()  # Use oscilloscope auto function if signal has been lost
                time.sleep(10)
            else:
                self.scope.ch1.verticalGain = _vdiv
                self.scope.ch1.verticalOffset = -v_avg
            time.sleep(0.05)
            if averages == 1:
                datum = self.scope.ch1.meas_Vpp()
            else:
                self.scope.acquireMode = 'AVER'
                self.scope.averages = averages
                datum = self.scope.ch1.meas_Vpp()
                self.scope.acquireMode = 'NORM'
            data[idx] = datum
            time.sleep(0.5 * dwell)

        return(data)

    def stop(self):
        """ Interrupt scan threads (not implemented)."""
        self.halt = True

    def calibrated_sweep(self, fstart=1e3, fend=6e7, nsteps=None, inc=10 ** 0.1, ltype='log',
                         amp=2.5, ofs=0, averages=4, dwell=2, datafile='sweep_data.csv'):
        """ Perform a calibration sweep prior to a sweep on the system under test."""
        print('Connect the oscilloscope directly to the function generator to establish baseline response.')
        _ = input('Press enter to begin scan:')
    
        baseline_response = self.sweep(fstart=fstart, fend=fend, nsteps=nsteps, inc=inc, ltype=ltype,
                                       amp=amp, ofs=ofs, averages=averages, dwell=dwell)
    
        print('Baseline scan complete.\n' +
              'Connect the oscilloscope to the system under test.')
        _ = input('Press enter to begin scan:')
    
        sut_response = self.sweep(fstart=fstart, fend=fend, nsteps=nsteps, inc=inc, ltype=ltype,
                                  amp=amp, ofs=ofs, averages=averages, dwell=dwell)
        print('Scan finished.')
        
        filename = input('Enter the filename to which to save scan data [{:s}]:'.format(datafile))
        if filename in ['', '\n']:
            filename = datafile  # Use datafile parameter if no input is provided

        freq_array = gen_frequency_array(fstart=fstart, fend=fend, nsteps=nsteps, inc=inc, ltype=ltype)
        gain = sut_response / baseline_response
        header_string = '{:17s}{:17s}{:17s}{:17s}'.format('Frequency [Hz]', 'Baseline [V]', 'SUT Raw [V]', 'Gain')
        print('Filename = {:s}'.format(filename))

        np.savetxt(filename, np.transpose([freq_array, baseline_response, sut_response, gain]),
                   fmt='%16.8g', delimiter=',', header=header_string)

        make_calibration_plot(freq_array, baseline_response, sut_response)

        print('Scan complete.')


def make_calibration_plot(freq_array, baseline_response, sut_response):
    gain = sut_response / baseline_response

    fig, ax1 = plt.subplots()
    ax1.set_xscale('log')
    ax1.set_yscale('linear')
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Gain [dB]')
    ax1.set_title('SUT Frequency Response')
    ax1.plot(freq_array, 10 * np.log10(gain))

    ax2 = ax1.twinx()
    ax2.plot(freq_array, 1e3 * baseline_response, '-r', freq_array, 1e3 * sut_response, ':r')
    ax2.set_yscale('log')
    ax2.set_ylabel('Raw Voltage [mV]', color='r')

    plt.show()


def gen_frequency_array(fstart, fend, nsteps, inc=None, ltype='log'):
    if ltype == 'log':
        if inc is None:
            freq_array = np.logspace(np.log10(fstart), np.log10(fend), nsteps)
        else:
            nsteps = 1 + int(np.log(fend / fstart) / np.log(np.abs(inc)))
            freq_array = np.logspace(np.log10(fstart), np.log10(fend * inc), nsteps, endpoint=False)
    if ltype in ['linear', None]:
        if inc is None:
            freq_array = np.linspace(fstart, fend, nsteps)
        else:
            nsteps = 1 + int((fend - fstart) / inc)
            freq_array = np.linspace(fstart, fend + inc, nsteps, endpoint=False)
    return freq_array


def help():
    """ Display usage instructions."""
    sweep_instances = []
    for key, val in list(locals().items()):
        if val is Sweep:
            if key[0] != '_':
                sweep_instances.append[key]
    if sweep_instances:
        sweep_instance = sweep_instances[0]
        print('Instantiated sweep controllers:\n' +
              '[' + ', '.join(sweep_instances) + ']')
    else:
        sweep_instance = 'sw'
        print('Create a new sweep instance by typing\n' +
              '  sw = sweep_util.Sweep()\n')

    print('To initiate a new sweep, type `{:s}.sweep()`.\n'.format(sweep_instance) +
          'The method `{:s}.sweep()` can also be called with keyword arguments:\n'.format(sweep_instance) +
          '    > {:s}.sweep( key1=val1, key2=val2, etc...) \n\n'.format(sweep_instance) +
          'Valid keywords are:\n' +
          '  fstart  - Sweep starting frequency.\n' +
          '  fend    - Sweep ending frequency.\n' +
          '  nsteps  - number of frequencies at which to sample between \n' +
          '            fstart and fend, inclusive of endpoints.\n' +
          '  inc     - Specifying inc overrides nsteps.  If ltype is `linear`,\n' +
          '            inc is the arithmetic step between frequencies.\n' +
          '            (i.e., freq_array[n+1] = f[n] + inc).  If ltype is `log`, inc\n' +
          '            is the geometric step between frequencies.\n' +
          '            (i.e., f[n+1] = f[n] * inc).\n' +
          '  ltype   - Specify `linear` or `log`.  Determines arithmetic\n' +
          '            or geometric frequency spacing.\n' +
          '  amp     - Amplitude of sinusoidal signal in Volts.\n' +
          '  ofs     - Offset of signal zero-point from ground in Volts.\n' +
          '  dwell   - Time in seconds to wait between frequency changes.\n\n' +
          'To display this help message again, type `sweep_util.help()`.'
          )

if __name__ == '__main__':
    sw = Sweep()
    print('New sweep controller `sw` created.\n')
    help()