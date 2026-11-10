%% 04-linear-filter.m | 高斯核 / 可分离性 / 加噪图的平滑
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
sigma = 2.0; radius = 6; noise_sigma = 0.08; N = 128;
randn("seed", 21);
% ---- 造图：阶跃边缘 + 高斯噪声 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.3 + 0.4*double(X > N/2);
noisy = min(max(f + noise_sigma*randn(N,N), 0), 1);
% ---- 算法 1：由公式构造可分离高斯核 ----
x = -radius:radius;
w1 = exp(-x.^2 / (2*sigma^2)); w1 = w1 / sum(w1);
w2 = w1' * w1;                                  % 外积 = 二维高斯核
% ---- 算法 2：两次一维卷积 == 一次二维卷积 ----
sep  = conv2(conv2(noisy, w1, "same"), w1', "same");
full = conv2(noisy, w2, "same");
% ---- 数值验证 ----
printf("一维核长度 = %d, 和 = %.6f\n", numel(w1), sum(w1));
printf("二维核尺寸 = %dx%d, 和 = %.6f\n", rows(w2), columns(w2), sum(w2(:)));
printf("可分离与二维卷积最大差 = %.3e\n", max(abs(sep(:)-full(:))));
printf("噪声标准差: 平滑前 %.4f -> 平滑后 %.4f\n", std(noisy(:)), std(full(:)));
printf("边缘两侧均值: %.4f / %.4f (原始 0.3000 / 0.7000)\n", ...
       mean(mean(full(:, 20:40))), mean(mean(full(:, 90:110))));
printf("加噪 MSE=%.6f 平滑后 MSE=%.6f\n", ...
       mean((noisy(:)-f(:)).^2), mean((full(:)-f(:)).^2));
% ---- 可视化 ----
if SHOW
  figure("name", "04 线性滤波");
  subplot(1, 3, 1); imagesc(noisy, [0 1]); colormap gray; axis image off; title("加噪图");
  subplot(1, 3, 2); imagesc(w2, [0 max(w2(:))]); axis image off; title("高斯核");
  subplot(1, 3, 3); imagesc(full, [0 1]); axis image off; title("高斯平滑后");
end
