% Jim Weimer and Kyoungwon Kim
% and Rado Ivanov

clc
clearvars

all_data = load('uncovered/DDPG_L21_64x64_Controller1/run1.csv');

data = all_data(240, :)';

indices = (2 + 20 * 4): (11.5 * 4):(1084 - 4 * 20);

data = data(indices);

data(data > 5) = 5;

theta = [(-115:11.5:115)'];

theta_actual = (-135:0.25:135)';
[~,idx,~] = intersect(theta_actual,theta);

fig = figure('Color', [1,1,1]);
set(fig, 'Position', [100 100 800 600])
plot(data.*cos((theta+90)*pi/180) , data.*sin((theta+90)*pi/180),'m.','MarkerSize',20)
hold on
plot(0,0,'^','MarkerSize',20,'LineWidth',10)
title('LiDAR Scan in Unmodified Environment', 'FontSize',24);
xlim([-5 5])

%export_fig('scan_unmodified_environment.pdf', '-transparent')