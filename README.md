import numpy as np
import xarray as xr
import netCDF4 as nc
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

from test4 import daily_afdd_series, daily_afdd_curves

data_path=r"C:\Users\86131\Desktop\era5data\data"
start_year=2015
end_year=2024

nc_files=glob.glob(os.path.join(data_path, "data_stream-oper_stepType-instant.nc"),recursive=True)

def read_file_(ncfile):
    ds = xr.open_dataset(ncfile)
    time_var="valid_time"
    time = ds.variables[time_var][:]
    temperature=ds.variables[time_var][:]
    ds.close()
    return time, temperature
def calculate_average_temperature(temperature,time):
    n_hours=(temperature.shape[0]/24)*24
    temperature=temperature[:n_hours]
    time=time[:n_hours]
    daily_average_temperature=time.resample('1D').mean()
    return daily_average_temperature
def conversion_unit(daily_average_temperature):
    return daily_average_temperature.apply(lambda x: np.abs(x-273.15))
def calculate_AFDD(daily_average_temperature):
    return daily_average_temperature.apply(lambda x:-x if x<0 else 0)

annual_AFDD={}
daily_AFDD={}

for year in range(start_year,end_year+1):
    print(f"处理{year}-{year+1}")
    start=pd.Timestamp(f"{year}-07-01")
    end=pd.Timestamp(f"{year+1}-6-30")
    daily_list=[]
    for f in nc_files:
        temperature, time=read_file_(f)
        s=calculate_average_temperature(temperature,time)
        s=s.loc[start:end]
        if not s.empty:
            daily_list.append(s)
        if len(daily_list)==0:
            print(f"no data")

    daily_all=pd.concat(daily_list)
    daily_afdd_series=calculate_AFDD(daily_all)
    cumulative_AFDD=daily_afdd_series.cumsum()
    annual_AFDD[year]=cumulative_AFDD.iloc[-1]
    daily_afdd_curves[f"{year}-{year+1}"]=cumulative_AFDD


plt.figure(figsize=(8,6))
plt.plot(list(annual_AFDD.keys()), list(annual_AFDD.values()))
plt.xticks(rotation=90)
plt.vlabel("AFDD(℃-day)")
plt.title("Annual AFDD(freezing year)")
plt.tight_layout()
plt.show()


plt.figure(figsize=(9, 6))
for key, series in daily_afdd_curves.items():
    days = (series.index - series.index[0]).days + 1  # 计算天数
    plt.plot(days, series.values, label=key)

plt.xlabel("Day of Freezing Year (since Jul 1)")
plt.ylabel("Cumulative AFDD (°C·day)")
plt.title("Daily Cumulative AFDD Curves")
plt.legend()
plt.tight_layout()
plt.show()
