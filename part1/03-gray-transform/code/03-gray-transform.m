%% 03-gray-transform.m | 点运算：线性 / gamma / 对数映射
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
gamma = 0.45; a = 1.2; b = -0.1; N = 256;
% ---- 造图：偏暗的渐变 + 亮圆盘 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.05 + 0.35 * (X / N) + 0.45*double((X-170).^2 + (Y-120).^2 < 45^2);
f = min(max(f, 0), 1);
% ---- 算法：四种 LUT 映射 ----
g_lin    = min(max(a*f + b, 0), 1);
g_gamma  = f .^ gamma;
g_invgan = f .^ (1/gamma);
g_log    = log(1 + f) / log(2);
r = linspace(0, 1, 256);
lut_gamma = r .^ gamma;
g_lut = reshape(interp1(r, lut_gamma, f(:)), size(f));   % 用查找表实现同一映射
% ---- 数值验证 ----
printf("原图       mean=%.4f std=%.4f\n", mean(f(:)), std(f(:)));
printf("线性拉伸   mean=%.4f std=%.4f\n", mean(g_lin(:)), std(g_lin(:)));
printf("gamma=%.2f  mean=%.4f std=%.4f\n", gamma, mean(g_gamma(:)), std(g_gamma(:)));
printf("gamma>1    mean=%.4f std=%.4f\n", mean(g_invgan(:)), std(g_invgan(:)));
printf("对数映射   mean=%.4f std=%.4f\n", mean(g_log(:)), std(g_log(:)));
printf("LUT 与逐像素映射最大差 = %.3e\n", max(abs(g_lut(:)-g_gamma(:))));
printf("f=0.25 时 gamma 输出 = %.4f (0.25^%.2f)\n", 0.25^gamma, gamma);
% ---- 可视化 ----
if SHOW
  figure("name", "03 灰度映射");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图（偏暗）");
  subplot(2, 2, 2); imagesc(g_gamma, [0 1]); axis image off; title("gamma<1 提亮暗部");
  subplot(2, 2, 3); imagesc(g_log, [0 1]); axis image off; title("对数压缩");
  subplot(2, 2, 4); plot(r, r.^gamma, "linewidth", 2); grid on; xlabel("输入 r"); ylabel("T(r)"); title("gamma LUT");
end
