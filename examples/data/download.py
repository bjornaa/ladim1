#! /usr/bin/env python

# Download example ROMS forcing file for the LADiM examples

# -----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2017-08-21
# -----------------------------------

import ftplib
import io
import gzip

ftp_site = 'ftp.imr.no'
datadir = 'bjorn/ladim-data'
datafile = 'ocean_avg_0014.nc'

ftp = ftplib.FTP(ftp_site)
ftp.login('anonymous', 'ladim')
ftp.cwd(datadir)

gzfile = datafile + '.gz'

# TODO: make progress bar
print('Downloading', gzfile)
f0 = io.BytesIO()
ftp.retrbinary('RETR ' + gzfile, f0.write)
f0.seek(0)

print('Decompressing',  datafile)
with open(datafile, 'wb') as outfile:
    outfile.write(gzip.decompress(f0.read()))
