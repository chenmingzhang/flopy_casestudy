import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf


# Create the headfile and budget file objects
headobj = bf.HeadFile(modelname+'.hds')
times = headobj.get_times()
cbb = bf.CellBudgetFile(modelname+'.cbc')


mytimes = [1.0, 50.0, 100.0]


fig = plt.figure(figsize=(8, 3))
ax = fig.add_subplot(1, 1, 1)
##modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'Column': 5})  # this will only work when nrow is more than 1
##modelxsect = flopy.plot.ModelCrossSection(model=ms, line={'Row': 0})
#patches = modelxsect.plot_ibound()
#linecollection = modelxsect.plot_grid()
#t = ax.set_title('Row 0 Cross-Section with IBOUND Boundary Conditions')

#plot(dis.sr.xcentergrid.shape,head[0,0,:])
#head = headobj.get_data(totim=mytimes[2])
#ax.plot(dis.sr.xcentergrid[0,:],head[-1,0,:])
#head = headobj.get_data(totim=mytimes[1])
#ax.plot(dis.sr.xcentergrid[0,:],head[-1,0,:])
#
#fig.show()
#


#head = headobj.get_data(totim=mytimes[0])
head = headobj.get_data()
head[head==-999.99]=np.nan

fig = plt.figure(figsize=(5,5))
ax = fig.add_subplot(1, 1, 1)
#modelmap = flopy.plot.ModelMap(model=ms,rotation=0)  #suggested by flopy3_MapExample.ipynb
#linecollection = modelmap.plot_grid()  # this line is the plotting line
quadmesh = modelmap.plot_ibound()  # a useful command to check all the ibounds
plt.contourf(dis.sr.xcentergrid,dis.sr.ycentergrid,head[0,::])
plt.colorbar()
ax.set_xlabel('X (m)')
ax.set_ylabel('X (m)')
fig.show()


#head = headobj.get_data(totim=mytimes[1])
#
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'Row': 0})
#surf = ax.plot_surface(modelxsect.xcentergrid, modelxsect.zcentergrid, head[:,0,:], cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)
#plt.show(block=False)
#
#
#head = headobj.get_data(totim=mytimes[2])
#head[head==1e-30]=np.nan
#
#fig = plt.figure()
#ax = fig.gca(projection='3d')
#modelxsect = flopy.plot.ModelCrossSection(model=mf, line={'Row': 0})
#surf = ax.plot_surface(modelxsect.xcentergrid, modelxsect.zcentergrid, head[:,0,:], cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)
#plt.show(block=False)
#
head1d=head.ravel()
print recharge*365.,'m/year',head1d[ad_borehole_intersect.nodenumber]


#hds = headobj.get_data(kstpkper=(50, 0)) 
