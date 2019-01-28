#os.remove('gelita.hds')
# if one uses add_refinement_featurs a shape file will be produced
# setting up modflow model
Lx = data['x_range']
Ly = data['y_range']
nlay = 1
nrow = 100
ncol = 100
delr = Lx / ncol
delc = Ly / nrow
h0 = 80
h1 = 5
#hk=10
#vka=10
hk=0.1
vka=0.1
sy=0.20
ss=0.0001
top = h0
botm = np.zeros((nlay, nrow, ncol), dtype=np.float32)
botm[0, :, :] = -10.
laytyp = np.ones(nlay) 
nper = 1  # a single value
perlen =[20000]  # in days i guess
#perlen =[200]  # in days i guess
nstp = [10]
steady=[True]
modelname='gelita'
recharge=0.0001 # get data close to 
#recharge=0.01

## get the surface elevation from 2D interpolation

model_ws = os.path.join('.', 'data')
#dis.sr.xcentergrid
#dis.sr.ycentergrid
#dis.sr.xgrid
#dis.sr.ygrid
#np.ma.masked_equal(dis.sr.ygrid,1000) # very useful command to find specific file locations
#modelmap.sr.vertices
#flopy.plot.plotutil.cell_value_points
#
#
#modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'Row': 0})
#modelxsect.elev
#
#modelxsect.dis
#modelxsect.xpts
#modelxsect.xcentergrid
#modelxsect.zcentergrid

# we first creat the model to get meshgrid, then do it again
#ms = flopy.modflow.Modflow(rotation=-20.)
#ms = flopy.modflow.Modflow()
#ms = flopy.modflow.Modflow(model_ws=model_ws, modelname='mfusg',exe_name='mf2005')
# model_ws is the director that the results stores
ms = flopy.modflow.Modflow(modelname=modelname,exe_name='mf2005')

#dis = flopy.modflow.ModflowDis(ms, nlay=nlay, nrow=nrow, ncol=ncol, delr=delr,
#                                       delc=delc, top=top, botm=botm)

#dis = flopy.modflow.ModflowDis(ms, nlay=nlay, nrow=nrow, ncol=ncol, delr=delr, \
#                                       delc=delc, top=top_elev, botm=botm,perlen=perlen,\
#                                       nper=nper,nstp=nstp, steady=steady,itmuni=4)
dis = flopy.modflow.ModflowDis(ms, nlay=nlay, nrow=nrow, ncol=ncol, delr=delr, \
                                       delc=delc, top=top, botm=botm,perlen=perlen,\
                                       nper=nper,nstp=nstp, steady=steady,itmuni=4)
from scipy import interpolate

f = interpolate.interp2d(data['x_ay'], data['y_ay'], data['z_mtx'], kind='cubic')

top_elev= f(dis.sr.xcenter,dis.sr.ycenter[::-1])


#fig=plt.figure
#plt.contourf(dis.sr.xcenter,dis.sr.ycenter[::-1],top_elev)
#plt.show(block=False)
#
#fig=plt.figure
#plt.contourf(data['x_mtx'], data['y_mtx'], data['z_mtx'])
#plt.show(block=False)
#



#dshp = os.path.join(model_ws, 'ad0')
g = Gridgen(dis, model_ws=model_ws)

g.build()
#disu = g.get_disu(ms)   # g.nodes will be assigned only when this line is executed
# i have to mannually remove 
# instead of using g.nodes, i am now using ncol*nrow to replace all g.nodes
adriver = [[data['river_points_xy_ay']]]   # why three layers is required?
ad_eastern_region=[[data['eastern_region_points_xy_ay']]]
ad_borehole_loc=[ ( data['borehole']['12']['x'], data['borehole']['12']['y']   )  ]
ad_pump_loc=[ ( data['borehole']['pump']['x'], data['borehole']['pump']['y']   )  ]

adriver_intersect = g.intersect(adriver, 'line', 0)
ad_eastern_region_intersect = g.intersect(ad_eastern_region, 'polygon', 0)
ad_borehole_intersect = g.intersect(ad_borehole_loc, 'point', 0)
ad_pump_intersect = g.intersect(ad_pump_loc, 'point', 0)

rivershp = os.path.join(model_ws, 'river1')

print(adriver_intersect.dtype.names)
print(ad_eastern_region_intersect.dtype.names)

#ibound_ay=np.ones(nrow*ncol)
#
#for i in ad_eastern_region_intersect.nodenumber: 
#    ibound_ay[i]=-1
#
#for i in adriver_intersect.nodenumber: 
#    ibound_ay[i]=3
#
#ibound_mtx=ibound_ay.reshape(nrow,ncol)   # double check which index goes first
#
#
#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as plt
#from matplotlib import cm
#from matplotlib.ticker import LinearLocator, FormatStrFormatter
#import numpy as np
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#surf = ax.plot_surface(dis.sr.xcentergrid,dis.sr.ycentergrid, ibound_mtx, cmap=cm.coolwarm,
#                                       linewidth=0, antialiased=False)
#plt.show(block=False)


ibound_ay=np.zeros((ncol*nrow), dtype=np.int)+3  # active cell
ibound_ay[ad_eastern_region_intersect.nodenumber]=0 # ibound==0 inactive cell
ibound_ay[adriver_intersect.nodenumber]=-1   #ibound<0 constant head
ibound_ay[ad_borehole_intersect.nodenumber]=5 
ibound_ay[ad_pump_intersect.nodenumber]=7 
ibound_mtx=ibound_ay.reshape(nrow,ncol)

fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
g.plot(ax, a=ibound_ay, masked_values=[0], edgecolor='none', cmap='jet')
mm = flopy.plot.ModelMap(model=ms)
mm.plot_grid()
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
fig.show()


a = np.zeros((ncol*nrow), dtype=np.int)
a[ad_eastern_region_intersect.nodenumber]=1
a[adriver_intersect.nodenumber]=2
fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
g.plot(ax, a=a, masked_values=[0], edgecolor='none', cmap='jet')
mm = flopy.plot.ModelMap(model=ms)
mm.plot_grid()
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
fig.show()



#https://stackoverflow.com/questions/24617013/convert-latitude-and-longitude-to-x-and-y-grid-system-using-python
#dx = (lon2-lon1)*40000*np.cos((lat1+lat2)*np.pi/360)/360
#dy = (lat1-lat2)*40000/360
#
#dx_m = ( data['latlon']['b3']['lon_float']-data['latlon']['b1']['lon_float'] )*40000*  \
#        np.cos(( data['latlon']['b3']['lat_float']+data['latlon']['b1']['lat_float'] )*np.pi/360)/360 *1000.
#dy_m = (data['latlon']['b3']['lat_float']-data['latlon']['b1']['lat_float'])*40000/360 *1000.

#constants.latlon_two_ponts_to_delta_xy( (data['latlon']['b1']['lat_float'],data['latlon']['b1']['lon_float']) ,(data['latlon']['b3']['lat_float'],data['latlon']['b3']['lon_float']))
# get river points


dis = flopy.modflow.ModflowDis(ms, nlay=nlay, nrow=nrow, ncol=ncol, delr=delr, \
                                       delc=delc, top=top_elev, botm=botm,perlen=perlen,\
                                       nper=nper,nstp=nstp, steady=steady,itmuni=4)
strt= np.zeros((nlay, nrow, ncol), dtype=np.float32) + 40.87 # data from surveyed result
bas = flopy.modflow.ModflowBas(ms, ibound=ibound_mtx, strt=strt)

lpf = flopy.modflow.ModflowLpf(ms, hk=hk, vka=vka, sy=sy, ss=ss, laytyp=laytyp, ipakcb=53,
        hdry=+1e-30,wetfct=0.1,iwetit=3,laywet=1,wetdry=-1)
pcg = flopy.modflow.ModflowPcg(ms)


# plot the data setup
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
#modelmap = flopy.plot.ModelMap(sr=mf.dis.sr)
modelmap = flopy.plot.ModelMap(model=ms,rotation=0)  #suggested by flopy3_MapExample.ipynb
linecollection = modelmap.plot_grid()  # this line is the plotting line
quadmesh = modelmap.plot_ibound()  # a useful command to check all the ibounds
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
fig.show()




stress_period_data = {}
for kper in np.arange(nper):
    for kstp in np.arange(nstp[kper]):
        #if np.mod(kstp,50)==0:
            stress_period_data[(kper, kstp)] = ['save head',
                                                'save drawdown',
                                                'save budget',
                                                'print head',
                                                'print budget']
oc = flopy.modflow.ModflowOc(ms, stress_period_data=stress_period_data,compact=True)

rch=flopy.modflow.ModflowRch(ms,rech=recharge)

# this is my way to get the index location of the well
well_row_col=np.where(ibound_mtx==7)
#pumping_rate_m3Pday=-2000
pumping_rate_m3Pday=-1500
wel = flopy.modflow.ModflowWel(ms, stress_period_data=[0,well_row_col[0][0],well_row_col[1][0],pumping_rate_m3Pday])

ms.write_input()


# Run the model
success, mfoutput = ms.run_model(silent=True, pause=False, report=True)
if not success:
        raise Exception('MODFLOW did not terminate normally.')




