import subprocess
import pandas as pd
from pyproj import Proj, transform


GEIOEVAL_TGM2017 =  'geoideval -n tgm2017-1 --input-string "{} {}"'
inProj = Proj(init='epsg:32647')
outProj = Proj(init='epsg:4326')

def towgs84(df, col_E, col_N):
    return transform(inProj, outProj, df[col_E], df[col_N])

def GeoidUndul_TGM2017( lat, lng):
    cmd = GEIOEVAL_TGM2017.format( lat, lng )
    result = subprocess.run( cmd,  shell=True, check=True , capture_output=True )
    undul = float( result.stdout)
    return undul 

# read CSV
path = '/Users/isara/Documents/GeographicLib/***.csv'
df = pd.read_csv(path)

# transform to wgs84
col_E_name = df.columns[1]
col_N_name = df.columns[2]
wgs84_arr = towgs84(df, col_E_name, col_N_name)
df['lat'], df['lon'] = wgs84_arr[1], wgs84_arr[0]

# get Undulation
df['undulation'] = df.apply( lambda x: GeoidUndul_TGM2017(x.lat, x.lon) , axis=1 )

# get elipsoid height
df['h'] = df[df.columns[3]] + df['undulation']
df['h'] = df['h'].round(4)

# Export to csv
df.to_csv(path.replace('.csv', '_elipsoid.csv'))
