# LiDAR Data Traces for the F1/10 Autonomous Racing Car

This repository contains the data traces collected during experiments for the paper titled "Case Study: Verifying the Safety of an Autonomous Racing Car with a Neural Network Controller", submitted to HSCC '20.

All traces from experiments performed in the modified environment are in the "covered" folder, whereas traces from experiments in the unmodified environment are stored in the "uncovered" folder. Each subfolder is named after the setup it represents, namely the name contains the training algorithm, the number of LiDAR rays used, the neural network architecture and the index of the controller trained for that setup.

Each line in a file corresponds to one LiDAR scan; each line is comma-separated in the following format:

tv_sec,tv_usec, y1, ..., y1081, 

where tv_sec and tv_usec are seconds and microseconds, respectively, since Jan. 1, 1970 (note that the board
time is not updated, so relative times should be considered only), followed by the 1081 LiDAR rays for this scan. Note that LiDAR measurements are sampled at rouhgly 40Hz, but the controller is executed at roughly 10Hz (although both of these vary slightly from run to run).
