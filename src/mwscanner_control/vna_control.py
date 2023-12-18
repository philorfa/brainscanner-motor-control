import pyvisa
import numpy as np
import warnings
import datetime
import functools


def _check_connected(func):
    """Check if the VNA is connected, if not thow an exception.

    Function wrapper to be used a decorator and check if the VNA is able to
    communicate.

    Args:
        func (function or method): The callable to be wrapped.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if args[0]._vna is None:
            msg = 'You have to connection to the VNA to perform this action!'
            raise RuntimeError(msg)
        return func(*args, **kwargs)
    return wrapper


# TODO: change data format to block data (faster?, manual p. 846)
class RSVNAControl(object):
    """Remote control for the Rohde & Schwarz VNA.

    Object to communicate with the VNA either through the LAN or USB. To
    connect through the LAN interface, make sure that the instrument and the
    PC are connected to the same network. The instrument's IP address is
    displayed in the front panel. For USB connection, just plug the USB cable
    in the rear port of the instrument, marked as 'USB Device'.

    Note:
        The communication with the VNA utilizes the VISA interface, through
        the :external+pyvisa:doc:`pyvisa <index>` module. Please ensure that
        you have installed an appropriate backend
        :external+pyvisa:doc:`backend <introduction/getting>` for ``pyvisa``
        to work properly (the ``pyvisa`` module itself is installed
        automatically when installing the current package).

    Attributes:
        freq_points (int, optional): Number of frequency points for
            S-parameters acquisition. Default is 201.
        freq_min (float, optional): Starting frequency for the sweep in GHz.
            Default is 0.5.
        freq_max (float, optional): Stopping frequency for the sweep in GHz.
            Default is 3.0.
        averaging (int, optional): Number of sweeps for the averaging. Set to
            ``None`` to disable averaging. Default is 10.
    """
    def __init__(self):
        self._ip_address = '192.168.1.58'
        self.freq_points = 201
        self.freq_min = 0.5           # min frequency in GHz
        self.freq_max = 3.0           # max frequency in GHz
        self.averaging = 10           # number of sweeps for averaging

        self._rm = pyvisa.ResourceManager()
        self._vna = None
        self._calibrated = False
        self._lib_py = (self._rm.visalib.library_path == 'py')
        self._num_channels = None
        self._event_data = None

    @property
    def ip_address(self):
        """str: IP address of the instrument. Should be set before trying to
        connect."""
        return self._ip_address

    @ip_address.setter
    def ip_address(self, val):
        if not isinstance(val, str):
            raise TypeError('Expecting string input for IP address')
        self._ip_address = val

    @staticmethod
    def _index2traceid(ik, ij, total):
        if (ik < 1) or (ij < 1) or (ik > total) or (ij > total):
            msg = 'S-parameter out of range, S{:d}{:d}'
            raise IndexError(msg.format(ik, ij))
        if ij < ik:
            msg = 'Invalid S-parameter indeces, S{:d}{:d}'
            raise RuntimeError(msg.format(ik, ij))
        return ((ik - 1) * (2 * total - ik + 2)) // 2 + ij

    @staticmethod
    def _eventhandle(resource, event, user_handle):
        resp = resource.query(':SYSTem:USER:KEY?')
        print('The resp', resp)
        resp = resp[:-2].split(',')
        resource._buttons_handlers[resp[1][1:]]()

    def _addtrace2window(self, wid, trclist, dbmin, dbmax, title=None):
        # NOTE: check if trace already in window, or get error (manual p.1116)
        cmd_prefix = ':DISPlay:WINDow{:d}'.format(wid)

        # open window, ask for existing traces and clear
        self._vna.write(cmd_prefix + ':STATe ON')
        resp = self._vna.query(cmd_prefix + ':TRACe:CATalog?')
        data = resp[1:-2].split(',')
        data = [data[::2], data[1::2]]
        nmax_trace = len(data[0])
        len_list = len(trclist)
        trclist = ['Trc{:d}'.format(itrc) for itrc in trclist]
        print('Data before', data)
        print('Trace list', trclist)

        # loop over traces and add if not there
        cmd = cmd_prefix + ':TRACe{:s}:FEED \'{:s}\''
        cmd2 = cmd_prefix + ':TRACe{:s}'
        cmd2 += ':Y:BOTTom {:f}; TOP {:f}'.format(dbmin, dbmax)
        cmd3 = cmd_prefix + ':TRACe{:s}:DELete'
        for ik, trc_name in enumerate(trclist):
            ik_num = str(ik + 1)

            # decide to keep, delete or assign new trace
            trc_in_window = (ik < nmax_trace)
            trc_match = (trc_name in data[1])
            num_match = False
            if trc_match:
                idx = data[1].index(trc_name)
                num_match = (data[0][idx] == ik_num)
            if trc_match and num_match:
                self._vna.write(cmd2.format(ik_num))
                continue
            elif trc_in_window:
                # NOTE: check for trace number, maybe it was deleted before
                if ik_num in data[0]:
                    idx = data[0].index(ik_num)
                    print('Deleting', data[0][idx], data[1][idx])
                    self._vna.write(cmd3.format(ik_num))
                    del data[0][idx]
                    del data[1][idx]
                if trc_name in data[1]:
                    idx = data[1].index(trc_name)
                    print('Deleting again', data[0][idx], data[1][idx])
                    self._vna.write(cmd3.format(data[0][idx]))
                    del data[0][idx]
                    del data[1][idx]
                    nmax_trace -= 1

            # assign and scale
            self._vna.write(cmd.format(ik_num, trc_name))
            print('The format', cmd2.format(ik_num))
            self._vna.write(cmd2.format(ik_num))
            data[0].append(ik_num)
            data[1].append(trc_name)

        # remove all extra traces
        resp = self._vna.query(cmd_prefix + ':TRACe:CATalog?')
        data = resp[1:-2].split(',')
        data = [data[::2], data[1::2]]
        nmax_trace = len(data[0])
        print('Data after', data)
        if len_list < nmax_trace:
            for ik, trc_name in enumerate(data[1]):
                if not (trc_name in trclist):
                    print(ik, 'Removing', cmd3.format(data[0][ik]))
                    self._vna.write(cmd3.format(data[0][ik]))
        # add the title
        if title is not None:
            self._vna.write(cmd_prefix + ':TITLe:DATA \'{:s}\''.format(title))

    def _set_averaging(self):
        if self.averaging is not None:
            cmd = ':SENSe1:AVERage:COUNt {:d}'.format(self.averaging)
            self._vna.write(cmd)
            self._vna.write(':SENSe1:AVERage:MODE REDuce')
            self._vna.write(':SENSe1:AVERage:STATe ON')
            self._vna.write(':SENSe1:AVERage:CLEar')
        else:
            self._vna.write(':SENSe1:AVERage:STATe OFF')

    def connect(self, link='usb'):
        """Connect to the VNA to send and receive data.

        Args:
            link (str, optional): Which interface to use. Possible values are
                'usb', 'lan' or 'hislip'. Defaults to 'usb'.

        Raises:
            ValueError: If the link argument has the wrong value.
        """
        if self._vna is not None:
            warnings.warn('VNA is already connected', RuntimeWarning)
            return

        lnk = str(link).lower()
        if lnk == 'usb':
            rsrc = 'USB0::0x0AAD::0x01BE::102631'
        elif lnk == 'lan':
            rsrc = 'TCPIP0::' + self._ip_address + '::inst0'
        elif lnk == 'hislip':
            rsrc = 'TCPIP0::' + self._ip_address + '::hislip0'
        else:
            raise ValueError('Could not connect. Unknown link ' + link)
        rsrc += '::INSTR'
        self._vna = self._rm.open_resource(rsrc)

    def disconnect(self):
        """Disconnects from the VNA (only if it is already connected)"""
        if self._vna is None:
            warnings.warn('VNA is not connected', RuntimeWarning)
            return

        # detach event
        if self._event_data is not None:
            self._vna.disable_event(self._event_data[0], self._event_data[1])
            self._vna.uninstall_handler(self._event_data[0],
                                        self._event_data[2],
                                        self._event_data[3])
            self._event_data = None

        self._vna.close()
        self._vna = None

    @_check_connected
    def setup(self, num_channels=8):
        """Setup for VNA for measurement.

        First, this method will split the screen and add traces. For more than
        3 antennas, there will be three panels: one with the antenna
        reflection, one with the neighboring antenna signals and the third
        with the rest of the S-parameters. Moreover, the sweep parameters are
        set (minimum and maximum frequency, number of frequnecy points, etc).
        For less than three antennas, there will be two or even a single panel.

        Args:
            num_channels (int, optional): Number of channesl. Defaults to 8.

        Raises:
            RuntimeError: If you are connected to the VNA.
        """
        # activate single sweep mode for all channels
        self._vna.write('*RST')
        self._vna.write(':INITiate:CONTinuous:ALL OFF')

        # create all traces
        cmd = ':CALCulate1:PARameter:SDEFine \'Trc{:d}\', \'S{:d}{:d}\''
        for ik in range(1, num_channels + 1):
            for ij in range(ik, num_channels + 1):
                idtrc = self._index2traceid(ik, ij, num_channels)
                self._vna.write(cmd.format(idtrc, ik, ij))

        # configure layout: 2 windows top row, 1 window bottom row
        if num_channels == 1:
            cmd = ' \'1.00,1.00\''
        elif num_channels < 4:
            cmd = ' \'1.00,0.50,0.50\''
        else:
            cmd = ' \'0.50,0.50,0.50;0.50,1.00\''
        self._vna.write(':DISPlay:LAYout:DEFine 1, Horizontal,' + cmd)
        self._vna.write(':DISPlay:LAYout:APPLy 1')

        # add traces to windows
        trc_list = []
        for ik in range(1, num_channels + 1):
            trc_list.append(self._index2traceid(ik, ik, num_channels))
        self._addtrace2window(1, trc_list, -60., 10., 'Reflection')

        if num_channels > 1:
            trc_list = []
            for ik in range(1, num_channels+1):
                if ik < num_channels:
                    trc_list.append(self._index2traceid(ik, ik+1,
                                                        num_channels))
                else:
                    trc_list.append(self._index2traceid(1, ik, num_channels))
            self._addtrace2window(2, trc_list, -120., 0., 'Neighbour')

        if num_channels > 2:
            trc_list = []
            for ik in range(1, num_channels-1):
                ijend = num_channels if ik == 1 else num_channels + 1
                for ij in range(ik+2, ijend):
                    trc_list.append(self._index2traceid(ik, ij, num_channels))
            self._addtrace2window(3, trc_list, -120., 0., 'Transmission')

        # configure sweep parameters
        # FIXME: you are missing some configuration here!
        cmd = ':SENSe1:FREQuency:STARt {:f}GHz'.format(self.freq_min)
        self._vna.write(cmd)
        cmd = ':SENSe1:FREQuency:STOP {:f}GHz'.format(self.freq_max)
        self._vna.write(cmd)
        self._vna.write(':SENSe1:SWEep:TYPE LINear')
        self._vna.write(':SENSe1:SWEep:POINTs {:d}'.format(self.freq_points))
        self._set_averaging()

        # switch display on (may slow down measurement)
        self._vna.write(':SYSTem:DISPlay:UPDate ON')

        # update members
        self._num_channels = num_channels

    @_check_connected
    def setup_user_interface(self, buttons):
        """Setup the VNA user interface (on the VNA monitor).

        When you connect remotely to the VNA, the usual user interface is
        disabled and the VNA only accepts remote commands. There is still the
        option to add up to 8 buttons to VNA monitor that can trigger some
        functionality on the connected PC. In other words, the push of the
        button on the VNA screen can execute some function on the host PC. This
        method connects the VNA buttons to the requested function.

        Note:
            The way the host PC is notified that a button has been pushed
            differs for different ``pyvisa`` backends. The NI backend is able
            to attach the function handlers to the VNA events (see
            :external+pyvisa:doc:`event handling
            <introduction/event_handling>`), and the call is performed by the
            backend. The :external+PyVISA-Py:doc:`pyvisa-py <index>` backend
            does not support this functionality and the user has to poll for
            button presses periodically using :meth:`poll_user_keys`.

        Args:
            buttons (dict): A dictionary of function handlers. The key of the
                dictionary will be displayed on the VNA button. Note that the
                function should not accept any arguments.

        Raises:
            ValueError: If you are dictionary has the wrong format or length.
            RuntimeError: If you are connected to the VNA.
        """
        # some checks
        if not isinstance(buttons, dict):
            if self._vna is not None:
                self.disconnect()
            msg = 'Buttons should be a dictionary of function handlers'
            raise ValueError(msg)
        nb = len(buttons)
        self._vna.write(':SYSTem:USER:KEY 0')
        if nb == 0:
            return
        if nb > 8:
            if self._vna is not None:
                self.disconnect()
            msg = 'The VNA support at most 8 buttons. {:d} requested'
            raise ValueError(msg.format(nb))

        # add user keys
        self._vna.write(':SYSTem:USER:KEY 0')
        cmd = ':SYSTem:USER:KEY {:d}, \'{:s}\''
        for ik, key in enumerate(buttons):
            self._vna.write(cmd.format(ik+1, key))
            func = buttons[key]
            if isinstance(func, str):
                # NOTE: if wrong it will raise AttributeError
                func = getattr(self, func)
                buttons[key] = func

        # lib('py') does not implements events, use polling
        if not self._lib_py:
            event_type = pyvisa.constants.EventType.service_request
            event_mech = pyvisa.constants.EventMechanism.handler
            wrapped = self._vna.wrap_handler(self._eventhandle)
            user_handle = self._vna.install_handler(event_type, wrapped)
            self._vna.enable_event(event_type, event_mech)

            # configure the instrument registers, manual p. 830
            self._vna.write('*CLS')
            self._vna.write('*SRE 32')
            self._vna.write('*ESE 64')

            # save data, so as to uninstall the event
            self._event_data = [event_type, event_mech, wrapped, user_handle]
            # save on pyvisa.Resource to use events
            self._vna._buttons_handlers = buttons
        else:
            self._buttons_handlers = buttons

    @_check_connected
    def calibrate(self):
        # TODO: test this function
        today = datetime.date.today()
        calname = 'autoCal' + today.strftime('%Y%m%d')

        # NOTE: other calibrations in manual p. 1218
        self._vna.write(':SENSe1:CORRection:COLLect:AUTO:CONFigure FNPort,'
                        ' \'' + calname + '\'')

        # auto-detected connected ports
        ports = ['{:d}'.format(ik + 1) for ik in range(self._num_channels)]
        ports = ', '.join(ports)
        self._vna.write(':SENSe1:CORRection:COLLect:AUTO:'
                        'ASSignment1:DEFine:TPORt ' + ports)
        # NOTE: set delay high here, query should wait for calibration unit
        resp = self._vna.query(':SENSe:CORRection:COLLect:AUTO:'
                               'PORTs:CONNection?; *WAI', delay=35.)
        data = np.asarray(resp.split(','), dtype=int)

        # some checks
        if np.count_nonzero(data[1::2]) == 0:
            msg = 'Cannot assign calibration unit port to VNA.'
            msg += ' Maybe you forgot to connect the cables! Aborting'
            warnings.warn(msg, RuntimeWarning)
            return
        ncal = data.shape[0] // 2
        if ncal != self._num_channels:
            msg = 'Found {:d} ports connected to calibration unit, but'
            msg += ' created traces for {:d} test ports. Please check'
            warnings.warn(msg, RuntimeWarning)

        # calibrate
        msg = 'Test port {:d} -> calibration port {:d}'
        print('Calibrating ...')
        for ik in range(ncal):
            print(msg.format(data[2 * ik], data[2 * ik + 1]))
        self._vna.write(':SENSe1:CORRection:COLLect:AUTO:ASSignment1:ACQuire')
        self._vna.write(':SENSe1:CORRection:COLLect:AUTO:SAVE')
        self._calibrated = True

    @_check_connected
    def save_calibration(self, calfile=None):
        """Save the current calibration to a file.

        Args:
            calfile (str, optional): The name of the file to be exported. If
                ``None``, the file will be named ``autocal_NNchan_XXXXXXXX``,
                with ``NN`` the number of channes and ``XXXXXXXX`` the current
                date. Defaults to ``None``.

        Raises:
            RuntimeError: If you are connected to the VNA.
        """
        if not self._calibrated:
            msg = 'No calibration data present. Skip saving'
            warnings.warn(msg, RuntimeWarning)
            return

        if calfile is None:
            today = datetime.date.today()
            calfile = 'autoCal' + '_{:d}chan_'.format(self._num_channels)
            calfile += today.strftime('%Y%m%d')
        cmd = ':MMEMory:STORe:CORRection 1, \'{:s}.cal\''.format(calfile)
        self._vna.write(cmd)

    @_check_connected
    def load_calibration(self, calfile):
        """Load a calibration from a file.

        Args:
            calfile (str): The name of the file that the calibration is stored.

        Raises:
            RuntimeError: If you are connected to the VNA.
        """
        cmd = ':MMEMory:LOAD:CORRection 1, \'{:s}\''.format(calfile)
        self._vna.write(cmd)

    @_check_connected
    def save_state(self, statefile):
        r"""Save the current VNA state to a file.

        The state of the VNA stores the calibration, but also the channel and
        the screen configuration. The callibration files are stored by default
        to ``C:\Users\Public\Documents\Rohde-Schwarz\Vna\RecallSets\``.

        Args:
            statefile (str): The name of the file to be exported.

        Raises:
            RuntimeError: If you are connected to the VNA.
        """
        cmd = 'MMEMory:STORe:STATe 1, \'C:\\Users\\Public\\Documents\\' \
            'Rohde-Schwarz\\Vna\\RecallSets\\{:s}\''
        self._vna.write(cmd.format(statefile))

    @_check_connected
    def load_state(self, statefile):
        r"""Load the VNA state from a file.

        The state of the VNA stores the calibration, but also the channel and
        the screen configuration. The callibration files are stored by default
        to ``C:\Users\Public\Documents\Rohde-Schwarz\Vna\RecallSets\``.

        Args:
            statefile (str): The name of the file that the state is stored.

        Raises:
            RuntimeError: If you are connected to the VNA.
        """
        cmd = 'MMEMory:LOAD:STATe 1, \'C:\\Users\\Public\\Documents\\' \
            'Rohde-Schwarz\\Vna\\RecallSets\\{:s}\''
        self._vna.write(cmd.format(statefile))
        resp = self._vna.query('CALCulate1:PARameter:CATalog?')
        nsp = float(len(resp.strip().split(',')))
        self._num_channels = int((np.sqrt(1. + 4. * nsp) - 1.) / 2.)
        resp = self._vna.query(':SENSe1:SWEep:POINTs?')
        self.freq_points = int(resp.strip())
        resp = self._vna.query(':SENSe1:FREQuency:STARt?')
        self.freq_min = float(resp.strip()) * 1.e-9
        resp = self._vna.query(':SENSe1:FREQuency:STOP?')
        self.freq_max = float(resp.strip()) * 1.e-9
        self._set_averaging()

    @_check_connected
    def measure(self):
        """Perform a measurement.

        Returns:
            frequency (type): Description.
            data (type): Description.

        Raises:
            RuntimeError: If you are connected to the VNA.
        """
        self._vna.write('INITiate1:IMMediate; *WAI')
        resp = self._vna.query(':CALCulate1:DATA:ALL? SDATa')
        data = np.asarray(resp.split(','), dtype=float)
        data = data[::2] + 1j*data[1::2]
        nmeas = (self._num_channels * (self._num_channels + 1)) // 2
        data = np.reshape(data, (nmeas, self.freq_points))

        resp = self._vna.query(':CALCulate1:DATA:STIMulus?')
        frequency = np.asarray(resp.split(','), dtype=float)
        return frequency, data

    def poll_user_keys(self):
        """Poll the VNA for a pressed button.

        If a button is pressed the associated function is executed. See
        :meth:`setup_user_interface` for more information.

        Note:
            Polling only captures the last event (button press), discarding
            all the previous events.
        """
        resp = self._vna.query(':SYSTem:USER:KEY?')
        print('The resp', resp)
        resp = resp[:-2].split(',')
        self._buttons_handlers[resp[1][1:]]()
