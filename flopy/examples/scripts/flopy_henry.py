import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import flopy




workspace = os.path.join('henry')

# make sure workspace directory exists
if not os.path.exists(workspace):
    os.makedirs(workspace)

fext = 'png'
#narg = len(sys.argv)
#iarg = 0
#if narg > 1:
#    while iarg < narg - 1:
#        iarg += 1
#        basearg = sys.argv[iarg].lower()
#        if basearg == '--pdf':
#            fext = 'pdf'

# Input variables for the Henry Problem
Lx = 2.
Lz = 1.
nlay = 50
nrow = 1
ncol = 100
delr = Lx / ncol  # lenth of each cell
delc = 1.0
delv = Lz / nlay  #  elevation of each cell
henry_top = 1.
henry_botm = np.linspace(henry_top - delv, 0., nlay)   # bottom elevation of each cell
qinflow = 5.702  # m3/day # flow from the left
dmcoef = 0.57024  # m2/day  Could also try 1.62925 as another case of the Henry problem
# diffusivity
hk = 864.  # m/day this is hydraulic conductivity

# Create the basic MODFLOW model data
modelname = 'henry'
m = flopy.seawat.Seawat(modelname, exe_name="swt_v4", model_ws=workspace)

# Add DIS package to the MODFLOW model
dis = flopy.modflow.ModflowDis(m, nlay, nrow, ncol, nper=1, delr=delr,
                               delc=delc, laycbd=0, top=henry_top,
                               botm=henry_botm, perlen=1.5, nstp=15)
# An array of the stress period lengths.   # the time here is days and so 1.5 days for all simulation
# nstp= Number of time steps in each stress period

# Variables for the BAS package
# this is how it works (nlay, nrow_which is 1 in this case, ncol) 
ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
ibound[:, :, -1] = -1    # fix the bottom boundary value
bas = flopy.modflow.ModflowBas(m, ibound, 0)  # the last 0 is the started head

# Add LPF package to the MODFLOW model
lpf = flopy.modflow.ModflowLpf(m, hk=hk, vka=hk, ipakcb=53)

# Add PCG Package to the MODFLOW model
pcg = flopy.modflow.ModflowPcg(m, hclose=1.e-8)
# hclose is the head change criterion for convergence. (default is 1e-5).

# Add OC package to the MODFLOW model
oc = flopy.modflow.ModflowOc(m,
                             stress_period_data={
                                 (0, 0): ['save head', 'save budget']},
                             compact=True)

# Create WEL and SSM data
itype = flopy.mt3d.Mt3dSsm.itype_dict()
wel_data = {}
ssm_data = {}
wel_sp1 = []
ssm_sp1 = []
for k in range(nlay):
    wel_sp1.append([k, 0, 0, qinflow / nlay])     #inflow from left
    ssm_sp1.append([k, 0, 0, 0., itype['WEL']])   # background concentration from left
    ssm_sp1.append([k, 0, ncol - 1, 35., itype['BAS6']])   # background concentration from right
wel_data[0] = wel_sp1   
ssm_data[0] = ssm_sp1
wel = flopy.modflow.ModflowWel(m, stress_period_data=wel_data)

# Create the basic MT3DMS model data
btn = flopy.mt3d.Mt3dBtn(m, nprs=-5, prsity=0.35, sconc=35., ifmtcn=0,
                         chkmas=False, nprobs=10, nprmas=10, dt0=0.001)
# nprs -- A flag indicating (i) the frequency of the output  NPRS < 0, simulation results will be saved whenever the number of transport steps is an even multiple of nprs.
# sconc is the starting concentration for the first species. To specify starting concentrations for other species in a multi-species simulation, include additional keywords, such as sconc2, sconc3, and so forth.
# ifmtcn  A flag/format code indicating how the calculated concentration should be printed to the standard output text file.  if ifmtcn = 0 concentrations are not printed. (default is 0).
#chkmas A logical flag indicating whether a one-line summary of mass balance information should be printed. (default is True).
# nprobs An integer indicating how frequently the concentration at the specified observation points should be saved. (default is 1).
# nprmas An integer indicating how frequently the mass budget information should be saved. (default is 1).
# dt0 The user-specified initial transport step size within each time-step of the flow solution. (default is 0).
adv = flopy.mt3d.Mt3dAdv(m, mixelm=0)
# MIXELM is an integer flag for the advection solution option. MIXELM = 0, 
dsp = flopy.mt3d.Mt3dDsp(m, al=0., trpt=1., trpv=1., dmcoef=dmcoef)
# AL is the longitudinal dispersivity
# trpt is a 1D real array defining the ratio of the horizontal transverse dispersivity to the longitudinal dispersivity.
# trpv is the ratio of the vertical transverse dispersivity to the longitudinal dispersivity.
#dmcoef=DMCOEF is the effective molecular diffusion coefficient (unit, L2T-1).
gcg = flopy.mt3d.Mt3dGcg(m, iter1=500, mxiter=1, isolve=1, cclose=1e-7)
# iter1 -- max number of inner iteration
# mxiter -- is the maximum number of outer iterations non-linear iteration
# isolve Lanczos/ORTHOMIN acceleration scheme: = 1
# cclose=1e-7 is the convergence criterion in terms of relative concentration; a real value between 10-4 and 10-6 is generally adequate.
ssm = flopy.mt3d.Mt3dSsm(m, stress_period_data=ssm_data)
# adv dsp gcg ssm are all required package in seawat

# Create the SEAWAT model data
vdf = flopy.seawat.SeawatVdf(m, iwtable=0, densemin=0, densemax=0,
                             denseref=1000., denseslp=0.7143, firstdt=1e-3)

# Write the input files
m.write_input()

# Try to delete the output files, to prevent accidental use of older files
try:
    os.remove(os.path.join(workspace, 'MT3D001.UCN'))
    os.remove(os.path.join(workspace, modelname + '.hds'))
    os.remove(os.path.join(workspace, modelname + '.cbc'))
except:
    pass

# run the model
m.run_model()

# Post-process the results

# Load data
ucnobj = flopy.utils.binaryfile.UcnFile(
    os.path.join(workspace, 'MT3D001.UCN'),
    model=m)
times = ucnobj.get_times()
concentration = ucnobj.get_data(totim=times[-1])
cbbobj = flopy.utils.binaryfile.CellBudgetFile(
    os.path.join(workspace, 'henry.cbc'))
times = cbbobj.get_times()
qx = cbbobj.get_data(text='flow right face', totim=times[-1])[0]
qz = cbbobj.get_data(text='flow lower face', totim=times[-1])[0]

# Average flows to cell centers
qx_avg = np.empty(qx.shape, dtype=qx.dtype)
qx_avg[:, :, 1:] = 0.5 * (qx[:, :, 0:ncol - 1] + qx[:, :, 1:ncol])
qx_avg[:, :, 0] = 0.5 * qx[:, :, 0]
qz_avg = np.empty(qz.shape, dtype=qz.dtype)
qz_avg[1:, :, :] = 0.5 * (qz[0:nlay - 1, :, :] + qz[1:nlay, :, :])
qz_avg[0, :, :] = 0.5 * qz[0, :, :]

# Make the plot
# import matplotlib.pyplot as plt
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
ax.imshow(concentration[:, 0, :], interpolation='nearest',
          extent=(0, Lx, 0, Lz))
y, x, z = dis.get_node_coordinates()
X, Z = np.meshgrid(x, z[:, 0, 0])
iskip = 3
ax.quiver(X[::iskip, ::iskip], Z[::iskip, ::iskip],
          qx_avg[::iskip, 0, ::iskip], -qz_avg[::iskip, 0, ::iskip],
          color='w', scale=5, headwidth=3, headlength=2,
          headaxislength=2, width=0.0025)

outfig = os.path.join(workspace, 'henry_flows.{0}'.format(fext))
fig.savefig(outfig, dpi=300)
print('created...', outfig)

# Extract the heads
fname = os.path.join(workspace, 'henry.hds')
headobj = flopy.utils.binaryfile.HeadFile(fname)
times = headobj.get_times()
head = headobj.get_data(totim=times[-1])

# Make a simple head plot
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
im = ax.imshow(head[:, 0, :], interpolation='nearest',
               extent=(0, Lx, 0, Lz))
ax.set_title('Simulated Heads')

outfig = os.path.join(workspace, 'henry_heads.{0}'.format(fext))
fig.savefig(outfig, dpi=300)
print('created...', outfig)


