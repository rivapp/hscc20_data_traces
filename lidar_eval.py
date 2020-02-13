from Car import World
import numpy as np
from six.moves import cPickle as pickle
import matplotlib.pyplot as plt
import os
import math

# these values indicate which walls should be used for lidar processing
RL = 0
FL = 1
FB = 2
FRL = 3

LEFT = 0
RIGHT = 1
FRONT = 2

LIDAR_ANGLE_RANGE = 135
LIDAR_DISTANCE_RANGE = 10

def est_dist(data, angles, alpha, wall):

    den = 0
    num = 0
    good_data = 0
    
    for theta in angles:
        value = getRange(data, theta)

        #only use value if positive
        if value > 0 and value < 10:

            good_data += 1
                
            # (1 ./ y).T * (1 ./ y)
            den += (1 / value) ** 2
                
            # C ./ y

            if wall == RIGHT:
                num += math.cos(math.radians(90 + theta + alpha)) * (1 / value)
            elif wall == LEFT:
                num += math.cos(math.radians(90 - theta - alpha)) * (1 / value)
            elif wall == FRONT:
                if np.sign(theta) == np.sign(alpha):
                    num += math.cos(math.radians(alpha + theta)) * (1 / value)
                else:
                    num += math.cos(math.radians(alpha - theta)) * (1 / value)

    return (num, den, good_data)

def getRange(data, angle):

    index = int(4 * (angle + LIDAR_ANGLE_RANGE))

    dist = data[index]

    return dist

def get_dist(data, angles_r, angles_l, mode = RL):

    # initialize variables just in case
    min_e_theta = float("inf")
    accurate_dist_left = 0
    accurate_dist_right = 0
    accurate_alpha = 0
    
    #fix alpha (heading) for the car
    for alpha in np.arange(-45, 45, 0.1):

        # First, estimate right distance by minimizing ||d / y - C||,
        # where y are the LiDAR rays and C are the cos(90 + alpha + theta)
        # the solution is d* = (C ./ y) / ((1./y).T * (1./y))

        if mode == RL:
            wall_1 = RIGHT
            wall_2 = LEFT
        elif mode == FL:
            wall_1 = FRONT
            wall_2 = LEFT
            
        (num, den, good_data_r) = est_dist(data, angles_r, alpha, wall_1)

        # if no useful rays in original range, look further back
        if den == 0:
            
            lookright = angles_r[len(angles_r) - 1]
            lidar_range_right = -115
            
            while lookright > lidar_range_right:

                (num, den, good_data_r) = est_dist(data, np.linspace(lookright, lookright + 30, 30 * 4 + 1), alpha, wall_1)
                                
                lookright -= 1

        # if still nothing, return default values
        if den == 0:
            return (10, 10)
        
        dist_right = num / den

        # Second, estimate left distance
        (num, den, good_data_l) = est_dist(data, angles_l, alpha, wall_2)
                
        # if no useful rays in original range, look further back
        if den == 0:
            
            lookleft = angles_l[0]
            lidar_range_left = 115
        
            while  lookleft < lidar_range_left:
                (num, den, good_data_l) = est_dist(data, np.linspace(lookleft - 30, lookleft, 30 * 4 + 1), alpha, wall_2)
            
                lookleft += 1

        # if still nothing, return default values
        if den == 0:
            return (10, 10)
        
        dist_left = num / den
        
        #find the value of beta at which the error value is minimized   
        e_theta_right = 0
        e_theta_left = 0
        
        #use the beta value to find the minimum error value
        for theta in angles_r:
            value = getRange(data, theta)
            e_theta_right += (math.cos(math.radians(90 + theta + alpha)) - dist_right / value) ** 2

        for theta in angles_l:
            value = getRange(data, theta)
            e_theta_left  += (math.cos(math.radians(90 - theta - alpha)) - dist_left / value) ** 2

        e_theta_right_avg = e_theta_right / good_data_r
        e_theta_left_avg = e_theta_left / good_data_l

        #original code
        if e_theta_left_avg < min(e_theta_right_avg, min_e_theta) :
            min_e_theta = e_theta_left_avg
            accurate_dist_left = dist_left
            accurate_dist_right = dist_right
            accurate_alpha = alpha
            
        elif e_theta_right_avg < min(e_theta_left_avg, min_e_theta):
            min_e_theta = e_theta_right_avg
            accurate_dist_left = dist_left
            accurate_dist_right = dist_right
            accurate_alpha = alpha
            
    return (accurate_dist_left, accurate_dist_right, accurate_alpha)

def cleanup_lidar(scan):
    new_scan = scan

    for i in range(len(scan)):
        
        if float(scan[i]) > 10 or 'Nan' in scan[i] or float(scan[i]) < 0:
            new_scan[i] = -1

        else:
            new_scan[i] = float(scan[i])
            
    return new_scan

def cleanup_lidar_model(scan):
    new_scan = np.array(scan)

    for i in range(len(scan)):
        
        if float(scan[i]) > 5 or float(scan[i]) < 0:
            new_scan[i] = 5.0

        else:
            new_scan[i] = float(scan[i])
            
    return new_scan

def subsample_lidar(scan, fov, deg):

    new_scan = []

    cur_ind = (135 - fov) * 4

    while cur_ind < 1080:

        new_scan.append(scan[cur_ind])

        cur_ind += int(4 * deg)

    return np.array(new_scan)

def eval_traces_in_folder(trace_dir):

    hallWidths = [1.5, 1.5, 1.5, 1.5]
    hallLengths = [20, 20, 20, 20]
    turns = ['right', 'right', 'right', 'right']
    car_dist_s = hallWidths[0]/2.0 - 0.06
    car_dist_f = 9.9
    car_heading = 0
    episode_length = 69
    time_step = 0.1
    time = 0

    lidar_field_of_view = 115
    lidar_num_rays = 21
    lidar_noise = 0
    missing_lidar_rays = 0

    angles_r = np.linspace(-115, -30, 85 * 4 + 1)
    angles_l = np.linspace(30, 115, 85 * 4 + 1)

    all_reflected = []
    all_errors = []

    for setup_dir in os.listdir(trace_dir):

        cur_dir = trace_dir + '/' + setup_dir
        
        for trace_file in os.listdir(cur_dir):

            datafile = cur_dir + '/' + trace_file

            f = open(datafile)

            # this count is used to average the estimates over multiple measurements (car is not moving initially)
            line_count = 0
            num_points_to_average = 10

            dl_sum = 0
            dr_sum = 0
            alpha_sum = 0
            

            for line in f:

                items = line.split(',')

                scan = items[2:1083]
                scan = cleanup_lidar(scan)

                (dl, dr, alpha) = get_dist(scan, angles_r, angles_l, RL)

                dl_sum += dl
                dr_sum += dr
                alpha_sum += alpha

                line_count += 1

                if line_count >= num_points_to_average:

                    car_dist_s = dl_sum / num_points_to_average
                    car_heading = (alpha_sum / num_points_to_average) * np.pi / 180

                    w = World(hallWidths, hallLengths, turns,\
                              car_dist_s, car_dist_f, car_heading,\
                              episode_length, time_step, lidar_field_of_view,\
                              lidar_num_rays, lidar_noise, missing_lidar_rays)

                    lidar_5m = cleanup_lidar_model(scan)

                    lidar_5m_21 = subsample_lidar(lidar_5m, lidar_field_of_view, 11.5)
                    model_scan = w.scan_lidar()

                    num_reflected = 0
                    abs_error = 0

                    for i in range(len(model_scan)):

                        if lidar_5m_21[i] >= 5 and model_scan[i] < 5:

                            num_reflected += 1

                        else:
                            abs_error = abs(lidar_5m_21[i] - model_scan[i])
                            all_errors.append(abs_error)


                    all_reflected.append(num_reflected)

                    print('finished file: ' + str(datafile))

                    break

    return (all_reflected, all_errors)

if __name__ == '__main__':

    covered_trace_dir = 'covered'
    uncovered_trace_dir = 'uncovered'

    (all_reflected_covered, all_errors_covered) = eval_traces_in_folder(covered_trace_dir)
    (all_reflected_uncovered, all_errors_uncovered) = eval_traces_in_folder(uncovered_trace_dir)

    reflected_covered_filename = 'reflected_covered.pickle'
    reflected_uncovered_filename = 'reflected_uncovered.pickle'

    try:
        with open(reflected_covered_filename, 'wb') as f:
            pickle.dump(all_reflected_covered, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print('Unable to save data to', reflected_covered_filename, ':', e)

    try:
        with open(reflected_uncovered_filename, 'wb') as f:
            pickle.dump(all_reflected_uncovered, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print('Unable to save data to', reflected_uncovered_filename, ':', e)

    errors_covered_filename = 'errors_covered.pickle'
    errors_uncovered_filename = 'errors_uncovered.pickle'

    try:
        with open(errors_covered_filename, 'wb') as f:
            pickle.dump(all_errors_covered, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print('Unable to save data to', errors_covered_filename, ':', e)

    try:
        with open(errors_uncovered_filename, 'wb') as f:
            pickle.dump(all_errors_uncovered, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print('Unable to save data to', errors_uncovered_filename, ':', e)
