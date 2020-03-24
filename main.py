import pickle
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from rotations import angle_normalize, rpy_jacobian_axis_angle, skew_symmetric, Quaternion
import csv
import pymap3d as pm
from scipy.spatial.transform import Rotation
from read_ublox import read_ublox

#Define variables
file_RTK_path = 'Data/Walking_around_university_12_Feb/Tero/GPS-2020-02-12-1234_ublox.csv'
file_TeroPhone_path = "Data/Walking_around_university_12_Feb/Tero/Sensor_record_20200212_123213_Nokia8.csv"
file_NhanPhone_path = "Data/Walking_around_university_12_Feb/Nhan/Sensor_record_20200212_123233_AndroSensor.csv"
message = '$GNGGA'
update_gnss_time = 40*100   #40s with 100 Hz Sampling rate

#### 1. Data ###################################################################################
#RTK data
lat, lon, alt, t, hor_dilut, h_geoid = read_ublox(file_RTK_path,message)
x,y,z = pm.geodetic2enu(lat,lon,alt,lat[0],lon[0],alt[0])

gnss_rtk = {
    "data":np.array([x,y,z]),
    "t":np.array(t),
}

#Tero's phone
lat = []
lon = []
alt = []            #m
accuracy = []       #m
t = []              #ms
t_offset = 50.0     #ms, source time = Device time + t_offset
with open(file_TeroPhone_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                lat.append(float(row[18]))
                lon.append(float(row[19]))
                alt.append(float(row[20]))
                accuracy.append(float(row[23]))
                t.append(float(row[-2]))
            if line_count == 1:
                t_start = row[-1]
            line_count += 1

x,y,z = pm.geodetic2enu(lat,lon,alt,lat[0],lon[0],alt[0])

gnss_phone = {
    "data":np.array([x,y,z]),
    "accuracy": accuracy,
    "t":np.array(t),
    "t_start":t_start,
    "t_offset":t_offset
}

#Nhan's phone
acc = []
gyro = []
gra = []
ori = []
t = []              #ms
t_offset = 196.0    #ms, source time = Device time + t_offset

with open(file_NhanPhone_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 1: #0 is 'sep='', 1 is the header
                acc.append([float(row[0]), float(row[1]), float(row[2])]) #x -> y -> z
                gyro.append([float(row[9]), float(row[10]), float(row[11])])        #x -> y -> z
                t.append(float(row[-2]))
                gra.append([float(row[3]), float(row[4]), float(row[5])])
                ori.append([float(row[17]), float(row[18]), float(row[16])])
            if line_count == 2:
                t_start = row[-1]
            # if line_count == 1:
            #     check = row
            line_count += 1


imu_phone = {
    "imu_f":np.array(acc),
    "imu_w":np.array(gyro),
    "gra":np.array(gra),
    "ori":np.array(ori),
    "t":np.array(t),
    "t_start": t_start,
    "t_offset": t_offset
}


#### 6. Visualization ###################################################################

################################################################################################
# Now that we have state estimates for all of our sensor data, let's plot the results. This plot
# will show the ground truth and the estimated trajectories on the same plot.
################################################################################################
#3D
est_traj_fig = plt.figure()
ax = est_traj_fig.add_subplot(111, projection='3d')
ax.plot(gnss_phone["data"][0,:], gnss_phone["data"][1,:], gnss_phone["data"][2,:], label='Phone GNSS 1 Hz')
ax.plot(gnss_phone["data"][0,range(0,len(gnss_phone["t"]),update_gnss_time)], gnss_phone["data"][1,range(0,len(gnss_phone["t"]),update_gnss_time)], gnss_phone["data"][2,range(0,len(gnss_phone["t"]),update_gnss_time)], label='Phone GNSS 0.025 Hz')
#ax.plot(p_est[:,0], p_est[:,1], p_est[:,2], label='Phone IMU + GNSS Estimation')
ax.plot(gnss_rtk["data"][0,:], gnss_rtk["data"][1,:], gnss_rtk["data"][2,:], label='RTK GNSS')
ax.set_xlabel('Easting [m]')
ax.set_ylabel('Northing [m]')
ax.set_zlabel('Up [m]')
ax.set_title('Ground Truth and Estimated Trajectory')
ax.legend(loc=(0.62,0.77))
ax.view_init(elev=45, azim=-50)
#plt.savefig('3D.png',dpi=2000)
plt.show()

#2D
est_traj_fig = plt.figure()
ax = est_traj_fig.add_subplot(111)
ax.plot(gnss_phone["data"][0,:], gnss_phone["data"][1,:], label='Phone GNSS 1 Hz')
ax.plot(gnss_phone["data"][0,range(0,len(gnss_phone["t"]),update_gnss_time)], gnss_phone["data"][1,range(0,len(gnss_phone["t"]),update_gnss_time)], label='Phone GNSS 0.025 Hz')
#ax.plot(p_est[:,1], p_est[:,0], label='Phone IMU + GNSS Estimation')
ax.plot(gnss_rtk["data"][0,:], gnss_rtk["data"][1,:], label='RTK GNSS')
ax.set_xlabel('Easting [m]')
ax.set_ylabel('Northing [m]')
ax.set_title('Ground Truth and Estimated Trajectory')
ax.legend(loc=(0.62,0.77))
#plt.savefig('2D.png',dpi=2000)
plt.show()