from scipy.io import netcdf
import json
import numpy as np
f = netcdf.NetCDFFile('adaptor.mars.external-1636204011.6285844-27815-15-cda100e0-8aee-4144-a72b-8fbda7d88d61.nc','r')


#print(f.variables)
#print(f.variables['longitude'].shape)
# v10 - v component of wind speed
# u10 - u component of wind speed
# t2m - temperature in 2m
# sr - Surface Roughness
# sp - Surface presure
# lai_hv - Leaf index high vegetation
# msl - Mean sea level presure

#['']
#a = np.array([[1,2],[3,-4]])
#print(a**2)
print(f.variables['v10'].units)
#print(dir(f.variables['v10']))
#print(f.variables['v10'].scale_factor)
x_shape = f.variables['v10'].shape[2]
y_shape = f.variables['v10'].shape[1]
days = f.variables['v10'].shape[0]

v_wind = f.variables['v10'].data * f.variables['v10'].scale_factor + f.variables['v10'].add_offset
u_wind = f.variables['u10'].data * f.variables['u10'].scale_factor + f.variables['u10'].add_offset


wind_speed = np.zeros((days,y_shape, x_shape))
for day in range(days):
    for x in range(x_shape):
        for y in range(y_shape):
            wind_speed[day,y,x] = np.sqrt(v_wind[day,y,x]**2 + u_wind[day,y,x]**2) 

temperature = f.variables['t2m'].data * f.variables['t2m'].scale_factor + f.variables['t2m'].add_offset
vegetation = f.variables['lai_hv'].data * f.variables['lai_hv'].scale_factor + f.variables['lai_hv'].add_offset
air_density = np.zeros((days,y_shape, x_shape))
data = {'wind_speed': wind_speed, 'temperature': temperature, 'vegetation': vegetation, 'air_density': air_density}

#print(vegetation)
#print(temperature)
#print(wind_speed)
#print(np.power(f.variables['v10'].data, 2))
#json.loads('')
#attributes = ['t2m', 'v10', 'u10']
#attr_names = {'t2m':'temperature', 'v10':'v_wind', 'u10':'u_wind'}

attributes = ['wind_speed', 'temperature', 'vegetation', 'air_density']
units = ['m s**-1', 'K', 'm**2 m**-2', '']


distortion = 3
#print(f.variables['latitude'].data)
#print(f.variables['longitude'].data)
bb_max_lon = f.variables['longitude'].data[-1]
bb_max_lat = f.variables['latitude'].data[0]
bb_min_lon = f.variables['longitude'].data[0]
bb_min_lat = f.variables['latitude'].data[-1]
cellWidthDegrees = 0.3
leftTopGeoPosLon = bb_min_lon + (cellWidthDegrees * distortion)
leftTopGeoPosLat = bb_max_lat - (0.5 * cellWidthDegrees * np.sqrt(3))
hex_grid_width = int(np.floor((bb_max_lon - leftTopGeoPosLon) / (0.75 * cellWidthDegrees * distortion)))
hex_grid_height = int(np.floor((leftTopGeoPosLat - bb_min_lat) / (0.5 * cellWidthDegrees * np.sqrt(3))))

jsonData = {
   "leftTopGeoPos": [
     leftTopGeoPosLon,
     leftTopGeoPosLat
   ],
   "hexGridResolution": [
     {
       "width": hex_grid_width,
       "height": hex_grid_height
     }
   ],
   "cellWidthDegrees": cellWidthDegrees,
   "data": []}

means = {}
mins = {}
maxes = {}
stds = {}

#means['']
for attr in attributes:
    means[attr] = np.mean(data[attr], axis = 0)
    mins[attr] = np.min(data[attr], axis = 0)
    maxes[attr] = np.max(data[attr], axis = 0)
    stds[attr] = np.std(data[attr], axis = 0)
#print(means['t2m'])
def getNearestLon(hex_lon):
    for i,lon in enumerate(f.variables['longitude'].data):
        #print(lon, hex_lon)
        if lon > hex_lon:
            return i-1,i

def getNearestLat(hex_lat):
    for i,lat in enumerate(f.variables['latitude'].data):
        #print(lat,hex_lat)
        if lat < hex_lat:
            return i-1, i

def getAttribute(att_name, hex_lon, hex_lat):      
    dxmin, dxmax= getNearestLon(hex_lon)
    dymin, dymax= getNearestLat(hex_lat)
    #print(dxmin, dxmax, hex_lon, hex_lat)
    count = 0
    mean_value = 0
    min_value = 0
    max_value = 0
    std_value = 0
    for coord in [(dxmin, dymin), (dxmin, dymax), (dxmax, dymin), (dxmax, dymax)]:   
        if coord[0] >= 0 and coord[1] >=0:
            #print(coord)
            
            mean_value += means[att_name][coord[1], coord[0]]
            min_value += mins[att_name][coord[1], coord[0]]
            max_value += maxes[att_name][coord[1], coord[0]]
            std_value += stds[att_name][coord[1], coord[0]]
            count += 1
    if count == 0:
        count = 1
    return mean_value / count, min_value / count, max_value / count, std_value / count

def calcWindStrength(u,v):
    return np.sqrt(u**2 + v**2)


for hex_x in range(hex_grid_width):
    for hex_y in range(hex_grid_height):
        hex_lon = hex_x * (0.75 * cellWidthDegrees * distortion) + leftTopGeoPosLon
        hex_lat = leftTopGeoPosLat - (hex_y * (0.5 * cellWidthDegrees * np.sqrt(3)))
        if hex_x % 2 != 0:
            hex_lat -= (np.sqrt(3) * 0.5 * cellWidthDegrees) * 0.5

        cell = {'x': hex_x, 'y': hex_y, 'lat': hex_lat, 'lon': hex_lon}
        for attr in attributes:
            attr_stats = getAttribute(attr, hex_lon, hex_lat)
            cell[attr] = {'min': attr_stats[1], 'max': attr_stats[2], 'mean': attr_stats[0], 'std': attr_stats[3]}
        jsonData['data'].append(cell)

with open('data.json', 'w') as f:
    json.dump(jsonData, f)     