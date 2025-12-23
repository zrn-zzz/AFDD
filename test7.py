import xarray as xr
import glob
import os
import matplotlib.pyplot as plt

data_root = r"C:/Users/86131/Desktop/era5data/data"
start_year = 2015
end_year = 2024

all_files = glob.glob(
    f"{data_root}/**/data_stream-oper_stepType-instant.nc",
    recursive=True
)
print(f"Total valid nc files: {len(all_files)}")
ds = xr.open_mfdataset(
    all_files,
    combine="by_coords"
)#把所有文件打开按时间维度拼成连续的

ds["t2m"] = ds["t2m"] - 273.15
print(ds["t2m"])
daily_temperature= ds['t2m'].resample(valid_time='1D').mean()
print(daily_temperature)
print(ds)
time=daily_temperature["valid_time"]

freezing_year=xr.where(
    time.dt.month >=7,
    time.dt.year,
    time.dt.year -1
)

daily_temperature=daily_temperature.assign_coords(
    freezing_year=("valid_time", freezing_year.data)
)

#assign.coords进行分组，按时间维度分在哪个冻结年内
daily_neg=xr.where(daily_temperature<0,-daily_temperature,0)
AFDD=daily_neg.groupby("freezing_year").sum(dim="valid_time")
print(AFDD)

# for fy in AFDD.freezing_year.values:
#     days = daily_neg.where(daily_neg.freezing_year == fy, drop=True)  #保留冻结年的日数据
#     print(fy, days.valid_time.min().values, days.valid_time.max().values)
#验证以下冻结年日期在在7月1日到次年6月30日之内
AFDD_mean = AFDD.mean(dim=["latitude", "longitude"])#把格点取平均
print(AFDD_mean)
for fy, val in zip(AFDD_mean.freezing_year.values, AFDD_mean.values):
    print(f"冻结年 {fy}: AFDD = {val:.2f}")
years = AFDD_mean.freezing_year.values
values = AFDD_mean.values
year_labels = [f"{y}-{y+1}" for y in years]

plt.figure(figsize=(9, 5))
plt.plot(year_labels, values, marker='o')
plt.xlabel("Freezing Year")
plt.ylabel("AFDD (°C·day)")
plt.title("AFDD by Freezing Year")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()





