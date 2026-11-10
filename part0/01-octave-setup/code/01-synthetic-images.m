%% 01-synthetic-images.m | 阶跃 / 条纹 / 圆盘 + 高斯与椒盐噪声
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 256; sigma = 0.06; salt_rate = 0.02; rand("seed", 7); randn("seed", 7);
% ---- 造图 ----
[X, Y] = meshgrid(1:N, 1:N);
step  = double(X > N/2);
stripe = 0.5 + 0.35 * sin(2*pi*X/24);
disk  = double((X - 0.5*N).^2 + (Y - 0.5*N).^2 < (0.28*N)^2);
base  = 0.25 + 0.6 * disk;
% ---- 噪声：高斯加性 + 椒盐脉冲 ----
noisy = base + sigma * randn(N, N);
sp = rand(N, N);
noisy(sp < salt_rate/2) = 0;
noisy(sp > 1 - salt_rate/2) = 1;
noisy = min(max(noisy, 0), 1);
% ---- 数值验证 ----
printf("step : mean=%.4f (期望 0.5)\n", mean(step(:)));
printf("stripe: min=%.3f max=%.3f mean=%.4f\n", min(stripe(:)), max(stripe(:)), mean(stripe(:)));
printf("disk : 面积占比=%.4f (pi*0.28^2=%.4f)\n", mean(disk(:)), pi*0.28^2);
printf("noisy: 与干净图的 MSE=%.6f, PSNR=%.2f dB\n", ...
       mean((noisy(:)-base(:)).^2), 10*log10(1/mean((noisy(:)-base(:)).^2)));
% ---- 可视化 ----
if SHOW
  figure("name", "01 合成测试图");
  subplot(2, 2, 1); imagesc(step, [0 1]); colormap gray; axis image off; title("阶跃");
  subplot(2, 2, 2); imagesc(stripe, [0 1]); axis image off; title("正弦条纹");
  subplot(2, 2, 3); imagesc(disk, [0 1]); axis image off; title("圆盘掩模");
  subplot(2, 2, 4); imagesc(noisy, [0 1]); axis image off; title("高斯 + 椒盐噪声");
end
