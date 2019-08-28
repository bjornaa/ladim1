import pytest
from postladim import ParticleFile


def test_open():
    # File not found
    with pytest.raises(SystemExit):
        pf = ParticleFile("no_such_file.nc")
    # Wrong file type
    with pytest.raises(SystemExit):
        pf = ParticleFile("test_ParticleFile.py")
