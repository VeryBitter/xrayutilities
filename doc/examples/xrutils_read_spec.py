import numpy
import tables
import matplotlib as mpl
import matplotlib.pyplot as plt
import xrutils as xu
import os

# plot settings for matplotlib
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 20.0
mpl.rcParams['axes.labelsize'] = 'large'
mpl.rcParams['figure.subplot.bottom'] = 0.16
mpl.rcParams['figure.subplot.left'] = 0.17
mpl.rcParams['savefig.dpi'] = 200
mpl.rcParams['axes.grid'] = False


# global setting for the experiment
sample = "test" # sample name used also as file name for the data file
en = 8042.5 # x-ray energy in eV
center_ch = 715.9 # center channel of the linear detector used in the experiment
chpdeg = 345.28 # channels per degree of the linear detector (mounted along z direction, which corresponds to twotheta)
roi=[100,1340] # region of interest of the detector

# intensity normalizer function responsible for count time and absorber correction
normalizer_detcorr = xu.IntensityNormalizer("MCA",mon="Monitor",time="Seconds",absfun=lambda d: d["detcorr"]/d["psd2"].astype(numpy.float))

# substrate material used for Bragg peak calculation to correct for experimental offsets
InP = xu.materials.InP

hxrd = xu.HXRD(InP.Q(1,1,-2),InP.Q(1,1,1),en=en)

# configure linear detector
hxrd.Ang2Q.init_linear('z-',center_ch,1500.,chpdeg=chpdeg,roi=roi)

# read spec file and save to HDF5-file 
# since reading is much faster from HDF5 once the data are transformed
h5file = os.path.join("data",sample+".h5")
try: s  # try if spec file object already exist from a previous run of the script ("run -i" in ipython)
except NameError: s = xu.io.SPECFile(sample+".spec",path="data")
else: s.Update()
s.Save2HDF5(h5file)

#################################
# InP (333) reciprocal space map
omalign = 43.0529 # experimental aligned values
ttalign = 86.0733 
[omnominal,dummy,dummy,ttnominal] = hxrd.Q2Ang(InP.Q(3,3,3)) # nominal values of the substrate peak

# read the data from the HDF5 file (scan number:36, names of motors in spec file: omega= sample rocking, gamma = twotheta)
[om,tt],MAP = xu.io.geth5_map(h5file,36,'omega','gamma')
# normalize the intensity values (absorber and count time corrections)                                                       
psdraw = normalizer_detcorr(MAP)
# remove unusable detector channels/regions (no averaging of detector channels)
psd = xu.blockAveragePSD(psdraw, 1, roi=roi)

# determine offset of substrate peak from experimental values (optional)
omalign,ttalign,p,cov = xu.analysis.fit_bragg_peak(om,tt,psd,omalign,ttalign,hxrd,plot=False)

# convert angular coordinates to reciprocal space + correct for offsets
[qx,qy,qz] = hxrd.Ang2Q.linear(om,tt,delta=[omalign-omnominal, ttalign-ttnominal])

# calculate data on a regular grid of 200x201 points
gridder = xu.Gridder2D(200,201)
gridder(qy,qz,psd)
INT = xu.maplog(gridder.gdata.transpose(),8.5,0)

# plot the intensity as contour plot
plt.figure(); plt.clf()
cf = plt.contourf(gridder.xaxis, gridder.yaxis,INT,100,extend='min')
plt.xlabel(r'$Q_{[11\bar2]}$ ($\AA^{-1}$)')
plt.ylabel(r'$Q_{[\bar1\bar1\bar1]}$ ($\AA^{-1}$)')
cb = plt.colorbar(cf)
cb.set_label(r"$\log($Int$)$ (cps)")


# The same again for a second (asymmetric peak)

# reciprocal space map around the InP (224)
omalign = 59.550 # experimental aligned values
ttalign = 80.099

[omnominal,dummy,dummy,ttnominal] = hxrd.Q2Ang(InP.Q(2,2,4)) # nominal values of the substrate peak

# read the data from the HDF5 file (scan number:36, names of motors in spec file: omega= sample rocking, gamma = twotheta)
[om,tt],MAP = xu.io.geth5_map(h5file,(33,34,35),'omega','gamma')
# normalize the intensity values (absorber and count time corrections)                                                       
psdraw = normalizer_detcorr(MAP)
# remove unusable detector channels/regions (no averaging of detector channels)
psd = xu.blockAveragePSD(psdraw, 1, roi=roi)

# determine offset of substrate peak from experimental values (optional)
omalign,ttalign,p,cov = xu.analysis.fit_bragg_peak(om,tt,psd,omalign,ttalign,hxrd,plot=False)

# convert angular coordinates to reciprocal space + correct for offsets
[qx,qy,qz] = hxrd.Ang2Q.linear(om,tt,delta=[omalign-omnominal, ttalign-ttnominal])

# calculate data on a regular grid of 400x600 points
gridder = xu.Gridder2D(400,600)
gridder(qy,qz,psd)
# calculate intensity which should be plotted
INT = xu.maplog(gridder.gdata.transpose(),8.5,0)

# plot the intensity as contour plot
plt.figure(); plt.clf()
cf = plt.contourf(gridder.xaxis, gridder.yaxis,INT,100,extend='min')  
# levels = numpy.logspace(numpy.log10(INT[INT>0].min()/2.),numpy.log10(INT.max()),num=100)
# norm = mpl.colors.LogNorm() should be used in future (not yet working in matplotlib)
plt.xlabel(r'$Q_{[11\bar2]}$ ($\AA^{-1}$)')
plt.ylabel(r'$Q_{[\bar1\bar1\bar1]}$ ($\AA^{-1}$)')
cb = plt.colorbar(cf)
cb.set_label(r"$\log($Int$)$ (cps)")

