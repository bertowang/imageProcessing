%% 10-gradient.m | Sobel 梯度 / 幅值 / 方向 / 阈值边缘
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; thresh = 0.35;
% ---- 造图：圆盘 + 矩形，带一点噪声 ----
[X, Y] = meshgrid(1:N, 1:N); randn("seed", 61);
f = 0.25 + 0.5*double((X-70).^2 + (Y-64).^2 < 30^2);
f(20:45, 15:40) = 0.85;
f = min(max(f + 0.01*randn(N,N), 0), 1);
% ---- 算法：Sobel = 平滑 x 差分的外积 ----
smooth = [1 2 1]; diff = [-1 0 1];
Gx = smooth' * diff;  Gy = diff' * smooth;
dx = conv2(f, Gx, "same"); dy = conv2(f, Gy, "same");
mag = sqrt(dx.^2 + dy.^2);
dirn = atan2(dy, dx) * 180 / pi;
edges = mag > thresh;
% ---- 数值验证 ----
printf("Sobel Gx 元素和 = %.1f, Gy 元素和 = %.1f（差分核和为 0）\n", sum(Gx(:)), sum(Gy(:)));
printf("梯度幅值: max=%.4f mean=%.4f\n", max(mag(:)), mean(mag(:)));
printf("平坦区域中心幅值 = %.6f（应接近噪声量级）\n", mag(5,5));
printf("阈值 %.2f 下的边缘像素数 = %d / %d (%.2f%%)\n", ...
       thresh, sum(edges(:)), N*N, 100*mean(edges(:)));
printf("圆盘边界点 (70,34) 的梯度方向 = %.1f 度\n", dirn(34,70));
% ---- 可视化 ----
if SHOW
  figure("name", "10 Sobel 梯度");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(2, 2, 2); imagesc(abs(dx)); axis image off; title("|Gx| 竖直边缘响应");
  subplot(2, 2, 3); imagesc(mag); axis image off; title("梯度幅值");
  subplot(2, 2, 4); imagesc(edges, [0 1]); axis image off; title("阈值边缘（未细化）");
end
