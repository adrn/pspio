# pspio

A simplified Python reader for EXP Phase-Space Protocol (PSP) files.

Installation
------------

The easiest way to install is via `pip`::

    pip install git+https://github.com/adrn/pspio


Usage
-----

The current package doesn't support much (much less than Mike Petersen's
`psp_io.py` script!), but here are some examples of things you can do. If you
want to execute this code yourself, [download this
file](https://users.flatironinstitute.org/~apricewhelan/data/exp/OUT.demo.psp)

Create a PSP file instance in Python:

    >>> from pspio import PSPFile
    >>> psp = PSPFile('OUT.demo.psp')

Print out the component names:

    >>> psp.component_names
    ['dark halo', 'star disk']

Get the header (as a Python dictionary) for a given component:

    >>> psp.headers['dark halo']
    {'index': 0,
     'parameters': {'nlevel': 1,
        'EJ': 2,
        'EJdamp': 1.0,
        ...etc...

Get the particle data for a given component, as an Astropy `Table`:

    >>> psp.data['dark halo']
    index        m             x       ...      vy          vz          potE
    ------ -------------- ------------ ... ----------- ------------ -----------
        1   9.651515e-06    0.9121899 ... -0.17850323  -0.22415227  -0.9963998
        2   6.243539e-07 0.0013042426 ...    0.668233 -0.104819864   -9.837082
        3  1.4266431e-05    0.6265081 ...   -0.379821   0.46982223   -1.138966
        4  1.9156283e-05   0.23180965 ... -0.17863524   0.18202542  -3.3090158
        5 1.05651625e-05   0.99168795 ... 0.004732454  -0.46637312  -1.1453477
        6  1.8979388e-05  -0.12203812 ...  0.31301686   -1.4198093  -4.1117673
    ...etc...


License
-------

Copyright 2019 Adrian Price-Whelan.

pspio is free software made available under the MIT License. For details see the
LICENSE file.
