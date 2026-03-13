import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import random

#if Min tank is 0: rainfall not enough
#if Min tank is 1: rainfall replenishes water needs every week


data = pd.read_csv("Beckley Rainwater Daily data.csv")

# rainfall_monthly = pd.to_numeric(data["Precipitation (inches)"].to_numpy())

# rainfall_weekly = np.zeros(rainfall_monthly.size * 4)

# for i in range(rainfall_weekly.size):
#     rainfall_weekly[i] = rainfall_monthly[i//4]/4




#print(np.sum(rainfall_weekly))  # total inches over the period

# Scale rainfall to realistic WV weekly inches
# rainfall_weekly = rainfall_weekly / 20.0  # roughly 0.1–1.5 inches/week

roof_area = 320                 # ft²
roof_area_in = roof_area * 144 # in^2

capture_efficiency = 0.85
daily_use_per_person = 3     # gallons/day
people = 3
weeks = np.linspace(1,rainfall_weekly.size, rainfall_weekly.size)

weeks_targets = np.array([50])
tanks_targets = np.array([100, 200, 500])

IN_TO_GALLONS = 0.004329
weekly_demand = daily_use_per_person * people * 7
min_allowable_tank_vol = 10

#print(harvested_water)

# -----------------------------
# SIMULATION FUNCTION (combined array)
# -----------------------------
def simulate_tank(tank_size, rainwater_data):
    """
    Returns [(tank volume per week), how many weeks volume remains above 0]
    week range is 0-end of rainfall data
    """
    tank = 0
    weeksReliable = 0
    tank_array = np.zeros(rainwater_data.size)
    i = 0
    for harvest in (rainwater_data):  
        tank += harvest
        tank = max(tank, 0)
        if i!=0: #assume we are only harvesting for first week of year
            tank -= weekly_demand
        tank = min(tank, tank_size) 
         
        tank_array[i] = tank
        i += 1
        
        if tank <= min_allowable_tank_vol:
            return tank_array, weeksReliable
        if i > 0:
            weeksReliable += 1
            
    return tank_array, weeksReliable


#randomize rainfall for a "bad" rain year
def bad_rain_year():
    worst_rainfall = rainfall_weekly.copy()
    score = sum(worst_rainfall)
    for i in range(5):
        temp = rainfall_weekly.copy()
        for x in range(rainfall_weekly.size):
            if x>2: #keep first couple weeks for collection safe
                temp[x] = (rainfall_weekly[x]) * (random.uniform(.4,1.4))
        if sum(temp) < score and sum(temp) > sum(rainfall_weekly)-5: #worst score that doesn't drop 5 total inches below (max variation)
            worst_rainfall = temp.copy()
            score = sum(worst_rainfall)

    return worst_rainfall

# -----------------------------
# OPTIMIZER
# returns tank vol per week and min tank size if possible
# returns 0 if impossible
# -----------------------------
def find_minimum_tank(desired_weeks_reliable, step=5):
    tank_guess = 0
    harvested_water = rainfall_weekly * roof_area_in * IN_TO_GALLONS * capture_efficiency #in gallons
    while True:
        tank_vol_per_week, weeks_reliable = simulate_tank(tank_guess, harvested_water)
        if weeks_reliable >= desired_weeks_reliable:
            return tank_vol_per_week, tank_guess
        if (tank_guess >= 2500):
            return np.zeros(rainfall_weekly.size), 0
        tank_guess += step

# -----------------------------
# RUN FOR DIFFERENT RELIABILITY TARGETS
# -----------------------------

# plt.figure()
# for w in weeks_targets:
#     max_tank_vol = -1
#     max_vol_data = np.zeros(rainfall_weekly.size)
#     for i in range(1000):
#         vol_data, tank_vol = find_minimum_tank(w)
#         #print(vol_data)
#         if max_tank_vol == -1:
#             max_tank_vol = tank_vol
#             max_vol_data = vol_data.copy()
#         elif tank_vol > max_tank_vol:
#             max_tank_vol = tank_vol
#             max_vol_data = vol_data.copy()
#     print(max_vol_data)  
#     plt.plot(weeks,max_vol_data, label = f"{w} weeks (tank {max_tank_vol} gal)")
#     print(f"Weeks reliable: {w}, Minimum Tank: {max_tank_vol} gallons")
# plt.title(f"Tank Lifespan Under {roof_area} sq ft Roof & {daily_use_per_person} Gals Per Person")
# plt.xlabel("Week")
# plt.ylabel("Tank Volume (gallons)")
# plt.legend()
# plt.grid(True)
# plt.show()  

# -----------------------------
# RUN FOR DIFFERENT TANK VOLUME TARGETS
# -----------------------------
plt.figure()
for tank_vol in tanks_targets:
    min_weeks_reliable = 50
    min_vol_data = np.zeros(rainfall_weekly.size)
    # for i in range(500):
    harvested_water = rainfall_weekly * roof_area_in * IN_TO_GALLONS * capture_efficiency #in gallons
    vol_data, weeks_reliable = simulate_tank(tank_vol, harvested_water)
    #     #print(vol_data)
    #     if weeks_reliable < min_weeks_reliable:
    #         min_weeks_reliable = weeks_reliable
    #         min_vol_data = vol_data
    plt.plot(weeks,vol_data, label = f"{weeks_reliable} weeks reliable @ {tank_vol} gal tank")
    print(f"Tank Size: {tank_vol} gallons. Weeks reliable: {weeks_reliable}")
plt.title(f"Tank Lifespan Under {roof_area} sq ft Roof & {daily_use_per_person} Gals Per Person")
plt.xlabel("Week")
plt.ylabel("Tank Volume (gallons)")
plt.legend()
plt.grid(True)
plt.show()  
