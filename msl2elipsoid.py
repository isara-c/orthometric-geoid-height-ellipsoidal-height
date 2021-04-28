import subprocess
import pandas as pd
import pdb
from pyproj import Proj, transform
import os

GEIOEVAL_TGM2017 =  'geoideval -n tgm2017-1 --input-string "{} {}"'
inProj = Proj(init='epsg:32647')
outProj = Proj(init='epsg:4326')

def towgs84(df, col_E, col_N):
    return transform(inProj, outProj, df[col_E], df[col_N])

def GeoidUndul_TGM2017( lat, lng): # ฟังก์ชันในการหาค่า N โดยเรียกใช้ command ด้วย subprocess
    cmd = GEIOEVAL_TGM2017.format( lat, lng )# แทนค่า parameter(lat,lng) ลงในคำสั่ง commmand
    result = subprocess.run( cmd,  shell=True, check=True , capture_output=True )
    # run command แล้วเรียกใช้คำสั่งที่กำหนดไว้ในตัวแปร CMD และเก็บผลลัพธ์ไว้ใน Result
    undul = float( result.stdout)# ตัดตัวอักษรที่ไม่เกี่ยวข้องออกด้วย .stdout และแปลงเป็น float
    return undul # คืนค่า Geoid Undulation ; N (meter)

# path CSV
path = '/Users/isara/Documents/GeographicLib/GCP_CU_Saraburi.csv'

df = pd.read_csv(path)

# transform to wgs84
wgs84_arr = towgs84(df, df.columns[1], df.columns[2])
df['lat'] = wgs84_arr[1]
df['lon'] = wgs84_arr[0]

# get Undulation
df['undulation'] = df.apply( lambda x: GeoidUndul_TGM2017(x.lat, x.lon) , axis=1 )

# get elipsoid
df['h'] = df[df.columns[3]] + df['undulation']
df['h'] = df['h'].round(4)
# Export
df.to_csv(path.replace('.csv', '_elipsoid.csv'))
