model_name=modelname
mp_namea = model_name + 'a_mp'
mp_nameb = model_name + 'b_mp'
pcoord = np.array([[0.000, 0.125, 0.500],
                   [0.000, 0.375, 0.500],
                   [0.000, 0.625, 0.500],
                   [0.000, 0.875, 0.500],
                   [1.000, 0.125, 0.500],
                   [1.000, 0.375, 0.500],
                   [1.000, 0.625, 0.500],
                   [1.000, 0.875, 0.500],
                   [0.125, 0.000, 0.500],
                   [0.375, 0.000, 0.500],
                   [0.625, 0.000, 0.500],
                   [0.875, 0.000, 0.500],
                   [0.125, 1.000, 0.500],
                   [0.375, 1.000, 0.500],
                   [0.625, 1.000, 0.500],
                   [0.875, 1.000, 0.500]])
#nodew = gwf.disv.ncpl.array * 2 + welcells['nodenumber'][0]
#plocs = [nodew for i in range(pcoord.shape[0])]

#plocs=np.ones(16)+10   np array is not working
nodew=10
plocs=[10]*16   # list is fine
# create particle data
pa = flopy.modpath.ParticleData(plocs, structured=False,
                                localx=pcoord[:, 0],
                                localy=pcoord[:, 1],
                                localz=pcoord[:, 2],
                                drape=0)
# what is plocs?
# plocs  --  Particle locations (zero-based) that are either layer, row, column locations or nodes.
# Local x-location of the particle in the cell. If a single value is provided all particles will have the same localx position. If a list, tuple, or np.ndarray is provided a localx position must be provided for each partloc. If localx is None, a value of 0.5 (center of the cell) will be used (default is None).

# create backward particle group
fpth = mp_namea + '.sloc'
pga = flopy.modpath.ParticleGroup(particlegroupname='BACKWARD1', particledata=pa,
                                  filename=fpth)
facedata = flopy.modpath.FaceDataType(drape=0,
                                      verticaldivisions1=10, horizontaldivisions1=10,
                                      verticaldivisions2=10, horizontaldivisions2=10,
                                      verticaldivisions3=10, horizontaldivisions3=10,
                                      verticaldivisions4=10, horizontaldivisions4=10,
                                      rowdivisions5=0, columndivisons5=0,
                                      rowdivisions6=4, columndivisions6=4)
pb = flopy.modpath.NodeParticleData(subdivisiondata=facedata, nodes=nodew)
# create forward particle group
fpth = mp_nameb + '.sloc'
pgb = flopy.modpath.ParticleGroupNodeTemplate(particlegroupname='BACKWARD2', 
                                              particledata=pb,
                                              filename=fpth)


# create modpath files
mp = flopy.modpath.Modpath7(modelname=mp_namea, flowmodel=ms,
                            exe_name='mp7', model_ws='.')
flopy.modpath.Modpath7Bas(mp, porosity=0.1)
flopy.modpath.Modpath7Sim(mp, simulationtype='combined',
                          trackingdirection='backward',
                          weaksinkoption='pass_through',
                          weaksourceoption='pass_through',
                          referencetime=0.,
                          stoptimeoption='extend',
                          timepointdata=[500, 1000.],
                          particlegroups=pga)

# write modpath datasets
mp.write_input()

# run modpath
mp.run_model()
