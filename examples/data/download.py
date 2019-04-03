#! /usr/bin/env python

# Download and gunzip an example ROMS forcing file

# -----------------------------------
# Bjørn Ådlandsvik <bjorn@imr.no>
# Institute of Marine Research
# 2017-08-21
# -----------------------------------

import ftplib
import io
import gzip

ftp_site = "ftp.imr.no"
datadir = "bjorn/ladim-data"
datafile = "ocean_avg_0014.nc"
gzipped_file = datafile + ".gz"

# --- Download by ftp ---
# TODO: make progress bar
print("Downloading", gzipped_file)
f0 = io.BytesIO()
with ftplib.FTP(ftp_site) as ftp:
    ftp.login("anonymous", "ladim")
    ftp.cwd(datadir)
    ftp.retrbinary("RETR " + gzipped_file, f0.write)

# --- gunzip the file ---
print("Decompressing", datafile)
f0.seek(0)
with open(datafile, "wb") as outfile:
    outfile.write(gzip.decompress(f0.read()))
