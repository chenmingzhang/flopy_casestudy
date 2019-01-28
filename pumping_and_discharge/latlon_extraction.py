import json
import numpy as np
import time
import geopy.distance
import LatLon
import requests
import matplotlib.pyplot as plt
import os
import sys

# for import latlon and converting
sys.path.append   (os.environ['pyduino']+os.path.join('python','post_processing'))
import constants

import flopy
from flopy.utils.gridgen import Gridgen 


with open('latlon.json') as f:
    data = json.load(f)

with open('keys.json') as f:
    key = json.load(f)

for i,key in enumerate(data['latlon']):
    print i,key
    latlon_str=LatLon.string2latlon(data['latlon'][key]['lat'], data['latlon'][key]['lon'], 'd% %m% %S% %H').to_string()
    data['latlon'][key]['lat_str']=latlon_str[0]
    data['latlon'][key]['lon_str']=latlon_str[1]
    data['latlon'][key]['lat_float']=float(latlon_str[0])
    data['latlon'][key]['lon_float']=float(latlon_str[1])


lat_base=data['latlon']['b1']['lat_float']
lon_base=data['latlon']['b1']['lon_float']
lat_dx=(data['latlon']['b3']['lat_float']-data['latlon']['b1']['lat_float'])/(data['no_lat_x_discretisation']-1)
lon_dx=(data['latlon']['b3']['lon_float']-data['latlon']['b1']['lon_float'])/(data['no_lon_y_discretisation']-1)


#https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
cds1=(data['latlon']['b1']['lat_float'],data['latlon']['b1']['lon_float'])
cds2=(data['latlon']['b2']['lat_float'],data['latlon']['b2']['lon_float'])
data['x_range']=geopy.distance.geodesic(  cds1,cds2).m
data['dx']=data['x_range']/float(data['no_lat_x_discretisation']-1)

cds1=(data['latlon']['b1']['lat_float'],data['latlon']['b1']['lon_float'])
cds2=(data['latlon']['b4']['lat_float'],data['latlon']['b4']['lon_float'])
data['y_range']=geopy.distance.geodesic(  cds1,cds2).m
data['dy']=data['y_range']/float(data['no_lon_y_discretisation']-1)


data['x_ay']=np.linspace(0,data['x_range'],num=data['no_lat_x_discretisation'])
data['y_ay']=np.linspace(0,data['y_range'],num=data['no_lon_y_discretisation'])


data['x_mtx'],data['y_mtx']=np.meshgrid(data['x_ay'],data['y_ay'])
data['z_mtx']=np.zeros([data['no_lat_x_discretisation'],data['no_lon_y_discretisation']])




for i,key in enumerate(data['borehole']):
    print i,key
    data['borehole'][key]['lat_float']=float(data['borehole'][key]['lat'])
    data['borehole'][key]['lon_float']=float(data['borehole'][key]['lon'])
    xy=constants.latlon_two_ponts_to_delta_xy_m( (data['latlon']['b1']['lat_float'],data['latlon']['b1']['lon_float']), \
            (data['borehole'][key]['lat_float'],data['borehole'][key]['lon_float']) )
    data['borehole'][key]['x']=xy[0]
    data['borehole'][key]['y']=xy[1]





river_latlon_ay= [x.strip() for x in data['river'].split(' ')]
no_river_points=len(river_latlon_ay)



#https://stackoverflow.com/questions/45200428/how-to-find-intersection-of-a-line-with-a-mesh/45203700
#https://stackoverflow.com/questions/3303936/how-to-find-all-grid-squares-on-a-line
data['river_points']={}
data['river_points_xy_ay']= []
## finally found that 
#adpoly = [[[(0, 0), (0, 60), (40, 80), (60, 0), (0, 0)]]]
#adpoly_intersect = g.intersect(adpoly, 'polygon', 0)
#adpoly_intersect.nodenumber

river_latlon_ay= [x.strip() for x in data['river'].split(' ')]

for i,key in enumerate(river_latlon_ay):
    print i,key
    itr=str(i)
    key_split=key.split(',')
    lon=np.float(key_split[0])
    lat=np.float(key_split[0])
    data['river_points'][itr]={}
    data['river_points'][itr]['lat_float']= float(key_split[1])
    data['river_points'][itr]['lon_float']= float(key_split[0])
    data['river_points'][itr]['latlon_float']= ( data['river_points'][itr]['lat_float'],data['river_points'][itr]['lon_float']   )
    xy=constants.latlon_two_ponts_to_delta_xy_m(  (data['latlon']['b1']['lat_float'],data['latlon']['b1']['lon_float']) \
            , data['river_points'][itr]['latlon_float'])
    data['river_points'][itr]['x']=xy[0]
    data['river_points'][itr]['y']=xy[1]
    data['river_points_xy_ay'].append((xy[0],xy[1]))



# dealing with the eastern regions
data['eastern_region_points']={}
data['eastern_region_points_xy_ay']= []

eastern_region_latlon_ay= [x.strip() for x in data['eastern_region'].split(' ')]

for i,key in enumerate(eastern_region_latlon_ay):
    print i,key
    itr=str(i)
    key_split=key.split(',')
    lon=np.float(key_split[0])
    lat=np.float(key_split[0])
    data['eastern_region_points'][itr]={}
    data['eastern_region_points'][itr]['lat_float']= float(key_split[1])
    data['eastern_region_points'][itr]['lon_float']= float(key_split[0])
    data['eastern_region_points'][itr]['latlon_float']= ( data['eastern_region_points'][itr]['lat_float'], \
            data['eastern_region_points'][itr]['lon_float']   )
    xy=constants.latlon_two_ponts_to_delta_xy_m(  (data['latlon']['b1']['lat_float'],data['latlon']['b1']['lon_float']) \
            , data['eastern_region_points'][itr]['latlon_float'])
    data['eastern_region_points'][itr]['x']=xy[0]
    data['eastern_region_points'][itr]['y']=xy[1]
    data['eastern_region_points_xy_ay'].append((xy[0],xy[1]))





'''
### below are for assessing google data useful for the first time to construct the model
google_data={}
for i in np.arange(data['no_lat_x_discretisation']): 
    google_data[i]={}
    for j in np.arange(data['no_lon_y_discretisation']):
        google_data[i][j]={}

for i in np.arange(data['no_lat_x_discretisation']): 
    for j in np.arange(data['no_lon_y_discretisation']):
        google_data[i][j]['lat_float']=lat_base+float(i)*lat_dx
        google_data[i][j]['lon_float']=lon_base+float(j)*lon_dx
        google_data[i][j]['access_address']=data['google_address_prefix']+str(google_data[i][j]['lat_float'])+','+str(google_data[i][j]['lon_float'])+ \
            key['google_address_suffix']
        if data['Download_from_google']:
            r = requests.get( google_data[i][j]['access_address']   )
            google_data[i][j]['access_result']=r.json()
            print r.json()
            data['z_mtx'][i][j]=google_data[i][j]['access_result']['results'][0]['elevation']
            time.sleep(1)
print 'google data extraction is completed'

if data['Download_from_google']:
    with open('google_data.json', 'w') as outfile:
            json.dump(google_data, outfile, indent=4, sort_keys=True)
'''



# construct the google based on assessed data
if ~data['Download_from_google']:
    with open('google_data.json') as f:
            google_data = json.load(f)
    for i in np.arange(data['no_lat_x_discretisation']): 
        for j in np.arange(data['no_lon_y_discretisation']):
            print google_data[str(i)][str(j)]['access_result']
            data['z_mtx'][i][j]=google_data[str(i)][str(j)]['access_result']['results'][0]['elevation']
    print 'google data extraction is completed'



from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
fig = plt.figure()
ax = fig.gca(projection='3d')

surf = ax.plot_surface(data['x_mtx'], data['y_mtx'], data['z_mtx'], cmap=cm.coolwarm,
                               linewidth=0, antialiased=False)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show(block=False)
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('ELEVATION (m)')


# below shows the contour plot
fig=plt.figure
plt.contourf(data['x_mtx'], data['y_mtx'], data['z_mtx'])
plt.show(block=False)


'''
with open('google_data.json') as f:
        gd = json.load(f)
'''
'''
with open('google_data2.json', 'w') as outfile:
        json.dump(gd, outfile, indent=4, sort_keys=True)
'''



