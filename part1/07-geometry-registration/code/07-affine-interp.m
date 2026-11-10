%% 07-affine-interp.m | 齐次坐标 / 反向映射 / 两种插值对比
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; theta = pi/6;         % 旋转 30 度
% ---- 造图：棋盘 + 细线（便于观察锯齿）----
[X, Y] = meshgrid(1:N, 1:N);
f = double(mod(floor(X/16) + floor(Y/16), 2) == 0);
f = 0.15 + 0.7*f;
f(abs(Y - N/2) < 2) = 0.9;
% ---- 算法：输出坐标 -> 逆旋转 -> 输入坐标 ----
R = [cos(theta) -sin(theta); sin(theta) cos(theta)];
cx = N/2; cy = N/2;
x = X(:)' - cx; y = Y(:)' - cy;
src = R' * [x; y];                       % 逆变换（旋转矩阵的逆 = 转置）
sx = reshape(src(1,:), N, N) + cx;
sy = reshape(src(2,:), N, N) + cy;
inside = sx >= 1 & sx <= N & sy >= 1 & sy <= N;
g_near = interp2(f, sx, sy, "nearest", 0);
g_lin  = interp2(f, sx, sy, "linear", 0);
% ---- 数值验证 ----
printf("旋转角 = %.1f 度, 落在图内的输出像素比例 = %.4f\n", theta*180/pi, mean(inside(:)));
printf("原图唯一灰度级数 = %d, 双线性后 = %d（插值产生了中间灰度）\n", ...
       numel(unique(f(:))), numel(unique(round(g_lin(:)*1000))));
printf("最近邻 / 双线性 的均值 = %.4f / %.4f\n", mean(g_near(:)), mean(g_lin(:)));
printf("细线处灰度: 最近邻 %.3f ~ 双线性 %.3f\n", ...
       max(g_near(abs(Y-N/2)<3)), max(g_lin(abs(Y-N/2)<3)));
% ---- 可视化 ----
if SHOW
  figure("name", "07 反向映射");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 3, 2); imagesc(g_near, [0 1]); axis image off; title("最近邻（锯齿）");
  subplot(1, 3, 3); imagesc(g_lin, [0 1]); axis image off; title("双线性（平滑）");
end
