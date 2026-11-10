%% 00-hello-image.m | 第一个图像程序：矩阵即图像
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 8;
% ---- 造图：左半 1（白），右半 0（黑）----
[X, Y] = meshgrid(1:N, 1:N);
img = double(X <= 4);
% ---- 数值验证 ----
printf("尺寸: %d x %d (行 x 列)\n", rows(img), columns(img));
printf("min=%.2f max=%.2f mean=%.4f\n", min(img(:)), max(img(:)), mean(img(:)));
printf("第 1 行: "); printf("%.0f ", img(1, :)); printf("\n");
printf("第 1 列之和（应等于行数）: %.0f\n", sum(img(:, 1)));
% ---- 可视化 ----
if SHOW
  figure("name", "00 矩阵即图像");
  imagesc(img, [0 1]); colormap gray; axis image off;
  title("8x8 二值图像：f(r,c)"); colorbar;
end
