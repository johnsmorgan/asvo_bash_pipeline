import sys
from astropy.io import fits
import aocal
import numpy as np
import warnings

warnings.filterwarnings("ignore")

REFANT=0
REFTIME=2
obsid=sys.argv[1]
ms=sys.argv[2]

bin = aocal.fromfile("%s_multi.bin" % obsid)
# select XX and YY and average over all channels
cplx = np.nanmean(bin[..., ::3], axis=2)

# divide through by reference antenna
cplx /= cplx[:, REFANT, :].reshape(cplx.shape[0], 1, cplx.shape[2])
# divide through by reference time
cplx /= cplx[REFTIME, :, :].reshape(1, cplx.shape[1], cplx.shape[2])
# average over polarisations and get phase
phase = np.angle(np.nanmean(cplx, axis=2), deg=True)

phase_std = np.nanstd(phase, axis=0)
phase_std[np.isnan(phase_std)]=0

badtiles = np.where(phase_std >= 3)

flagtiles = ("flagantennae %s " % ms)
for i in range(len(badtiles[0])):
	flagtiles+=str(badtiles[0][i])+" "

print(flagtiles)
