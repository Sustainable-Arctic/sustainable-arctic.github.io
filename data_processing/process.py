from scipy.io import netcdf
import json
import numpy as np
f = netcdf.NetCDFFile('adaptor.mars.external-1636244622.663271-28346-11-9d161581-22de-4d21-a742-d5913bec0831.nc','r')

# v10 - v component of wind speed
# u10 - u component of wind speed
# t2m - temperature in 2m
# sr - Surface Roughness
# sp - Surface presure
# cvh - High vegetation
# msl - Mean sea level presure

print(dir(f.variables['cvh']))
print(f.variables['cvh'].units)

x_shape = f.variables['v10'].shape[2]
y_shape = f.variables['v10'].shape[1]
days = f.variables['v10'].shape[0]

v_wind = f.variables['v10'].data * f.variables['v10'].scale_factor + f.variables['v10'].add_offset
u_wind = f.variables['u10'].data * f.variables['u10'].scale_factor + f.variables['u10'].add_offset
temperature = f.variables['t2m'].data * f.variables['t2m'].scale_factor + f.variables['t2m'].add_offset
vegetation = f.variables['cvh'].data * f.variables['cvh'].scale_factor + f.variables['cvh'].add_offset
presure = f.variables['sp'].data * f.variables['sp'].scale_factor + f.variables['sp'].add_offset


wind_speed = np.zeros((days,y_shape, x_shape))
air_density = np.zeros((days,y_shape, x_shape))
Rspec = 287.058
for day in range(days):
    for x in range(x_shape):
        for y in range(y_shape):
            wind_speed[day,y,x] = np.sqrt(v_wind[day,y,x]**2 + u_wind[day,y,x]**2) 
            air_density[day,y,x] = presure[day,y,x]/(temperature[day,y,x] * Rspec)


data = {'wind_speed': wind_speed, 'temperature': temperature, 'vegetation': vegetation, 'air_density': air_density}


#attributes = ['t2m', 'v10', 'u10']
#attr_names = {'t2m':'temperature', 'v10':'v_wind', 'u10':'u_wind'}

attributes = ['wind_speed', 'temperature', 'vegetation', 'air_density']
units = ['m/s', 'K', 'm^2/m^2', 'kg/m^3']

distortion = 3
cellWidthDegrees = 0.3

bb_max_lon = f.variables['longitude'].data[-1]
bb_max_lat = f.variables['latitude'].data[0]
bb_min_lon = f.variables['longitude'].data[0]
bb_min_lat = f.variables['latitude'].data[-1]

leftTopGeoPosLon = bb_min_lon + (cellWidthDegrees * distortion)
leftTopGeoPosLat = bb_max_lat - (0.5 * cellWidthDegrees * np.sqrt(3))
hex_grid_width = int(np.floor((bb_max_lon - leftTopGeoPosLon) / (0.75 * cellWidthDegrees * distortion)))
hex_grid_height = int(np.floor((leftTopGeoPosLat - bb_min_lat) / (0.5 * cellWidthDegrees * np.sqrt(3))))

jsonData = {
   "leftTopGeoPos": [
     leftTopGeoPosLon,
     leftTopGeoPosLat
   ],
   "distortion": distortion,
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

for attr in attributes:
    means[attr] = np.mean(data[attr], axis = 0)
    mins[attr] = np.min(data[attr], axis = 0)
    maxes[attr] = np.max(data[attr], axis = 0)
    stds[attr] = np.std(data[attr], axis = 0)

def getNearestLon(hex_lon):
    for i,lon in enumerate(f.variables['longitude'].data):
        if lon > hex_lon:
            weight_of_prev = np.abs(f.variables['longitude'].data[i] - hex_lon) / np.abs(f.variables['longitude'].data[i] - f.variables['longitude'].data[i-1])
            return i-1, i, weight_of_prev

def getNearestLat(hex_lat):
    for i,lat in enumerate(f.variables['latitude'].data):
        if lat < hex_lat:
            weight_of_prev = np.abs(f.variables['latitude'].data[i] - hex_lat) / np.abs(f.variables['latitude'].data[i] - f.variables['latitude'].data[i-1])
            return i-1, i, weight_of_prev

def bilinearInterpolation(data, dxmin, dxmax, alpha_x, dymin, dymax, alpha_y):
    value_x = data[dymin, dxmin] * alpha_x + data[dymin, dxmax] * (1 - alpha_x)
    value_y = data[dymax, dxmin] * alpha_x + data[dymax, dxmax] * (1 - alpha_x)
    return value_x * alpha_y + value_y * (1 - alpha_y)

def getAttribute(att_name, hex_lon, hex_lat):      
    dxmin, dxmax, alpha_x = getNearestLon(hex_lon)
    dymin, dymax, alpha_y = getNearestLat(hex_lat)

    mean_value = bilinearInterpolation(means[att_name], dxmin, dxmax, alpha_x, dymin, dymax, alpha_y)
    min_value = bilinearInterpolation(mins[att_name], dxmin, dxmax, alpha_x, dymin, dymax, alpha_y)
    max_value = bilinearInterpolation(maxes[att_name], dxmin, dxmax, alpha_x, dymin, dymax, alpha_y)
    std_value = bilinearInterpolation(stds[att_name], dxmin, dxmax, alpha_x, dymin, dymax, alpha_y)

    return mean_value, min_value, max_value, std_value

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