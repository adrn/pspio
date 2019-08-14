"""
Python PSP (Phase-Space Protocol) reader.

PSP is a file format used by the EXP basis function expansion N-body code
written by Martin Weinberg.

"""

# Third-party
from astropy.constants import G
import astropy.table as at
import astropy.units as u
from gala.units import UnitSystem
import numpy as np
import yaml


class PSPReader:
    """A Python reader for Phase-Space Protocol (PSP) files used by EXP.

    Parameters
    ----------
    filename : str
        The PSP filename to load.

    """

    def __init__(self, filename,
                 pos_unit=None, vel_unit=None,
                 mass_scale_unit=u.Msun, time_scale_unit=u.Myr):

        self.filename = filename

        # TODO: add options like psp_io:
        #     - if nbodies is set, only read that many bodies
        #     - if comp is set, only read that component

        self.pos_unit = pos_unit
        self.vel_unit = vel_unit
        if ((pos_unit is None and vel_unit is not None) or
            (vel_unit is None and pos_unit is not None)):
            raise ValueError("If you specify a pos or vel unit, you "
                             "must specify both.")

        # Start by reading the header:
        self.comp_header = self._load_header()
        self.comp_data = self._load_data()

        if pos_unit is not None:
            m_unit = (vel_unit**2 * pos_unit / G).to(mass_scale_unit)
            t_unit = np.sqrt((pos_unit**3) / (G*m_unit)).to(time_scale_unit)
            self._usys = UnitSystem(t_unit, m_unit, pos_unit, vel_unit)
        else:
            self._usys = None


    def _load_component_header(self, f, comp_idx):
        comp_pos = f.tell()  # byte position of this component

        # TODO: if PSP changes, this will have to be altered
        if self._float_len == 4:
            *_, nbodies, nint_attr, nfloat_attr, infostringlen = np.fromfile(
                f, dtype=np.uint32, count=6)
        else:
            nbodies, nint_attr, nfloat_attr, infostringlen = np.fromfile(
                f, dtype=np.uint32, count=4)

        # information string from the header
        head = np.fromfile(f, dtype=np.dtype((np.bytes_, infostringlen)),
                           count=1)
        head_normal = head[0].decode()
        head_dict = yaml.load(head_normal)

        comp_data_pos = f.tell()  # byte position where component data begins

        # the default fields are (m, x, y, z, vx, vy, vz, p)
        nfields = 8
        comp_length = nbodies * (8 * int(head_dict['parameters']['indexing']) +
                                 self._float_len * nfields +
                                 4 * nint_attr +
                                 self._float_len * nfloat_attr)
        comp_data_end = f.tell() + comp_length  # byte pos. of comp. data end

        data = dict()
        data['index'] = comp_idx
        for k in head_dict:
            data[k] = head_dict[k]
        data['nint_attr'] = nint_attr
        data['nfloat_attr'] = nfloat_attr
        data['nbodies'] = nbodies
        data['data_start'] = comp_data_pos
        data['data_end'] = comp_data_end

        return data

    def _load_header(self):
        """Load the master header of the PSP file"""

        comp_header = dict()
        nbodies = 0

        with open(self.filename, 'rb') as f:
            # --- This code taken from psp_io.py ---
            f.seek(16)  # find magic number
            cmagic, = np.fromfile(f, dtype=np.uint32, count=1)

            # check if it is float vs. double
            if cmagic == 2915019716:
                self._float_len = 4
                self._float_str = 'f'
            else:
                self._float_len = 8
                self._float_str = 'd'

            # reset to beginning and proceed
            f.seek(0)
            _ = np.fromfile(f, dtype='<f8', count=1)
            self._nbodies_tot, self._ncomp = np.fromfile(f, dtype=np.uint32,
                                                         count=2)

            for i in range(self._ncomp):
                data = self._load_component_header(f, i)
                comp_header[data.pop('name')] = data
                nbodies += data['nbodies']

        self.nbodies = nbodies

        return comp_header

    def _load_component_data(self, comp_header):

        # TODO: have to deal with indexing=True
        dtype_str = []
        colnames = []
        if comp_header['parameters']['indexing']:
            # if indexing is on, the 0th column is Long
            dtype_str = dtype_str + ['l']
            colnames = colnames + ['index']

        # default number of columns is 8 - TODO: this should be a variable
        dtype_str = dtype_str + [self._float_str] * 8
        colnames = colnames + ['m', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'potE']

        dtype_str = dtype_str + ['i'] * comp_header['nint_attr']
        colnames = colnames + ['i_attr{}'.format(i)
                               for i in range(comp_header['nint_attr'])]

        dtype_str = dtype_str + [self._float_str] * comp_header['nfloat_attr']
        colnames = colnames + ['f_attr{}'.format(i)
                               for i in range(comp_header['nfloat_attr'])]

        dtype = np.dtype(','.join(dtype_str))

        out = np.memmap(self.filename,
                        dtype=dtype,
                        shape=(1, comp_header['nbodies']),
                        offset=int(comp_header['data_start']),
                        order='F', mode='r')

        tbl = {}
        for i, name in enumerate(colnames):
            tbl[name] = np.array(out['f{}'.format(i)][0], copy=True)

        del out  # close the memmap instance

        return at.Table(tbl)

    def _load_data(self):
        comp_data = dict()

        ndatabodies = 0
        for name, hdr in self.comp_header.items():
            comp_data[name] = self._load_component_data(hdr)
            ndatabodies += len(comp_data[name])

        assert self.nbodies == ndatabodies

        return comp_data

    # Display:
    def __repr__(self):
        thing = ('<PSP {} bodies; {} components: {}>'
                 .format(self.nbodies, len(self.comp_header),
                         ', '.join(['"{}"'.format(k)
                                    for k in self.comp_header.keys()])))
        return thing

    def __str__(self):
        return self.__repr__()
