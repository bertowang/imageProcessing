%% 12-otsu.m | 直方图 / 类间方差 / 自动阈值 / 误分率
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; bins = 256; bg = 0.25; fg = 0.75; noise_sigma = 0.06;
randn("seed", 81);
% ---- 造图：亮目标 + 暗背景 + 高斯噪声 ----
[X, Y] = meshgrid(1:N, 1:N);
truth = double((X-64).^2 + (Y-64).^2 < 30^2);
f = bg + (fg-bg)*truth + noise_sigma*randn(N,N);
f = min(max(f, 0), 1);
% ---- 算法：直方图 -> 遍历阈值 -> 最大类间方差 ----
q = round(f(:)*(bins-1)) + 1;
h = zeros(bins,1);
for i = 1:numel(q), h(q(i)) = h(q(i)) + 1; end
total = numel(q); levels = (0:bins-1)' / (bins-1);
best_var = -1; best_t = 1;
for t = 2:bins
  w0 = sum(h(1:t-1)) / total; w1 = 1 - w0;
  if w0 == 0 || w1 == 0, continue; end
  m0 = sum(levels(1:t-1) .* h(1:t-1)) / sum(h(1:t-1));
  m1 = sum(levels(t:bins) .* h(t:bins)) / sum(h(t:bins));
  v = w0 * w1 * (m0 - m1)^2;
  if v > best_var, best_var = v; best_t = t; end
end
T = levels(best_t);
seg = f > T;
% ---- 数值验证 ----
printf("直方图总和 = %d, 像素总数 = %d\n", sum(h), total);
printf("Otsu 阈值 = %.4f（理论中点在 (%.2f+%.2f)/2 = %.2f）\n", T, bg, fg, (bg+fg)/2);
printf("最大类间方差 = %.6f\n", best_var);
printf("前景占比 = %.4f（真值 %.4f）\n", mean(seg(:)), mean(truth(:)));
printf("误分率 = %.4f%%\n", 100*mean(seg(:) ~= truth(:)));
printf("把噪声提高到 0.20 后误分率会明显上升，可自行验证\n");
% ---- 可视化 ----
if SHOW
  figure("name", "12 Otsu 分割");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("加噪图");
  subplot(1, 3, 2); bar(h); xlim([0 bins]); title("双峰直方图");
  subplot(1, 3, 3); imagesc(seg, [0 1]); axis image off; title("Otsu 掩模");
end
