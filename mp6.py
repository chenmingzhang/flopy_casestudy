mp = flopy.modpath.Modpath(modelname='ex6',
                           exe_name='mp6',
                           modflowmodel=ms,
                           dis_file=ms.name+'.dis',
                           head_file=ms.name+'.hds')
#                           budget_file=ms.name+'.bud')
#                           model_ws='data',


#mpb = flopy.modpath.ModpathBas(mp, hdry=ms.lpf.hdry, laytyp=ms.lpf.laytyp, ibound=1, prsity=0.1)
mpb = flopy.modpath.ModpathBas(mp, hdry=ms.lpf.hdry, laytyp=ms.lpf.laytyp, ibound=ibound_mtx, prsity=sy)
#mpb = flopy.modpath.ModpathBas(mp, hdry=ms.lpf.hdry, laytyp=ms.lpf.laytyp, ibound=3, prsity=sy)


#hdry is the head assiged to dry cell

# start the particles at begining of per 3, step 1, as in example 3 in MODPATH6 manual
# (otherwise particles will all go to river)
#sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages='RCH', start_time=(2, 0, 1.))
sim = mp.create_mpsim(trackdir='forward', simtype='pathline', packages='RCH')#, start_time=(2, 0, 1.))
#packages Keyword defining the modflow packages used to create initial particle locations. Supported packages are WEL, MNW2 and RCH. (default is WEL).



mp.write_input()
mp.run_model(silent=False)

fpth = os.path.join('ex6.mpend')
epobj = flopy.utils.EndpointFile(fpth)
#well_epd = epobj.get_destination_endpoint_data(dest_cells=[(0, 99, 4)])
#well_epd = epobj.get_destination_endpoint_data(dest_cells=[(0, 4, 99)])
#well_epd = epobj.get_destination_endpoint_data(dest_cells=[(0, 4, 99)])
#well_epd = epobj.get_destination_endpoint_data(dest_cells=[(0, 1, 6)])
well_epd = epobj.get_destination_endpoint_data(dest_cells=[(0, 99, 3)])
#well_epd = epobj.get_destination_endpoint_data(dest_cells=[(0, 8, 98)])

#
#epobj.get_alldata()
#well_epd = epobj.get_data(partid=1)
#rec.array([( 50, 0, 2, 0., 29565.62, 1, 0,  2, 0, 6, 0, 0.5, 0.5, 1.,  200., 9000., 339.1231, 1, 4, 12, 12, 2, 0, 1.        , 0.9178849 , 0.09755219, 5200.   , 5167.154,   9.755219, 'rch'),
#           ( 75, 0, 2, 0., 26106.59, 1, 0,  3, 0, 6, 0, 0.5, 0.5, 1.,  200., 8600., 339.1203, 1, 4, 12, 12, 4, 0, 0.7848778 , 1.        , 0.1387314 , 5113.951, 5200.   ,  13.87314 , 'rch'),
#           ( 76, 0, 2, 0., 22285.47, 1, 0,  3, 1, 6, 0, 0.5, 0.5, 1.,  600., 8600., 339.0849, 1, 4, 12, 12, 2, 0, 1.        , 0.90018   , 0.3697533 , 5200.   , 5160.072,  36.97533 , 'rch'),
#1,0,2 is the location
#rec.array([(  1, 0, 2, 0., 412355.1, 1, 0,  0, 1, 6, 0, 0.5, 0.5, 1., 22.53539, 1018.425, 43.4204, 1, 0, 81, 28, 1, 0, 0., 0.8193251, 0.999, 420.6605, 192.6241, 40.81913, 'rch')],


fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
fpth = os.path.join('ex6.mpend')
modelmap = flopy.plot.ModelMap(model=ms, layer=0)   # perhapse first layer is needed. 
quadmesh = modelmap.plot_ibound()
linecollection = modelmap.plot_grid()
contour_set = modelmap.contour_array(hds,levels=np.arange(np.min(hds),np.max(hds),0.5), colors='b')
plt.clabel(contour_set, inline=1, fontsize=14)
modelmap.plot_endpoint(well_epd, direction='starting', colorbar=True)
fig.show()

fpth = os.path.join('starting_locs.shp')
type(fpth)
epobj.write_shapefile(well_epd, direction='starting', shpname=fpth, sr=ms.sr)


pthobj = flopy.utils.PathlineFile(os.path.join('ex6.mppth'))


well_pathlines = pthobj.get_destination_pathline_data(dest_cells=[(0, 50, 50)])
well_pathlines = pthobj.get_destination_pathline_data(dest_cells=[(0, 20, 20)])


well_pathlines = pthobj.get_destination_pathline_data(dest_cells=[(0, 80, 0)]) 
well_pathlines = pthobj.get_destination_pathline_data(dest_cells=[(0, 0,80)])  # (lay, row, colomn) 
# it shows all the paths lines that goes through this point
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1, aspect='equal')
modelmap = flopy.plot.ModelMap(model=ms, layer=0)
quadmesh = modelmap.plot_ibound()
linecollection = modelmap.plot_grid()
#riv = modelmap.plot_bc('RIV', color='g', plotAll=True)
#quadmesh = modelmap.plot_bc('WEL', kper=1, plotAll=True)
contour_set = modelmap.contour_array(hds,levels=np.arange(np.min(hds),np.max(hds),0.5), colors='b')
plt.clabel(contour_set, inline=1, fontsize=14)
modelmap.plot_pathline(well_pathlines, layer='all', colors='red');
fig.show()

