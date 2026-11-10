%% 01-types-and-range.m | uint8 / double / logical 的行为差异
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
v = 200;
% ---- 算法：观察 uint8 的饱和与 double 的线性 ----
u = uint8(v);
printf("uint8(%d) + uint8(100) = %d  (饱和到 255)\n", v, u + uint8(100));
printf("double(%d)/255 + 0.4   = %.4f\n", v, double(v)/255 + 0.4);
g = (0:255) / 255;                     % 0~1 渐变
clipped = min(max(g * 2, 0), 1);       % 超过 1 的部分必须裁掉
printf("渐变 g: min=%.3f max=%.3f mean=%.4f\n", min(g), max(g), mean(g));
printf("放大 2 倍后未裁剪的比例: %.2f%%\n", 100 * mean(g * 2 > 1));
mask = g > 0.5;
printf("logical 掩模: class=%s 命中 %d / %d\n", class(mask), sum(mask(:)), numel(mask));
printf("掩模均值（double 化后）: %.4f\n", mean(double(mask(:))));
% ---- 可视化 ----
if SHOW
  figure("name", "01 范围与裁剪");
  subplot(1, 2, 1); plot(g * 2); grid on; title("未裁剪：最大值 2"); ylim([0 2.2]);
  subplot(1, 2, 2); plot(clipped); grid on; title("裁剪到 [0,1]"); ylim([0 1.2]);
end
