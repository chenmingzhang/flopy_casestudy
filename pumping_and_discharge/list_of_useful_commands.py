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
#m.nrow_ncol_nlay_nper
baskkkk

# we first creat the model to get meshgrid, then do it again
#ms = flopy.modflow.Modflow(rotation=-20.)
#ms = flopy.modflow.Modflow()
#ms = flopy.modflow.Modflow(model_ws=model_ws, modelname='mfusg',exe_name='mf2005')
# model_ws is the director that the results stores
m_get_package_list()
 headobj.get_kstpkper()

m.dis.steady.array
