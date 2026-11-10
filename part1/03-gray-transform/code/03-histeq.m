%% 03-histeq.m | 直方图均衡化：统计 h -> CDF -> LUT -> 映射
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
bins = 256; N = 256;
% ---- 造图：窄动态范围的偏暗图 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.30 + 0.20*(X/N) + 0.12*double((X-120).^2 + (Y-140).^2 < 50^2);
f = min(max(f, 0), 1);
% ---- 算法：直方图 -> 归一化 CDF -> 查表 ----
q = round(f(:) * (bins-1)) + 1;         % 量化到 1..bins
h = zeros(bins, 1);
for i = 1:numel(q)
  h(q(i)) = h(q(i)) + 1;               % 显式统计，便于对照公式
end
cdf = cumsum(h) / numel(q);
g = reshape(cdf(q), size(f));
% ---- 数值验证 ----
printf("直方图总和 = %d，像素总数 = %d\n", sum(h), numel(f));
printf("CDF 末项 = %.6f（应为 1）\n", cdf(end));
printf("原图 mean=%.4f std=%.4f  均衡后 mean=%.4f std=%.4f\n", ...
       mean(f(:)), std(f(:)), mean(g(:)), std(g(:)));
printf("原图占用的灰度级数 = %d / %d\n", sum(h > 0), bins);
hg = zeros(bins,1); qg = round(g(:)*(bins-1)) + 1;
for i = 1:numel(qg), hg(qg(i)) = hg(qg(i)) + 1; end
printf("均衡后占用的灰度级数 = %d / %d\n", sum(hg > 0), bins);
printf("理想均匀时每级像素数 = %.1f，实测最大级 = %d\n", numel(f)/bins, max(hg));
% ---- 可视化 ----
if SHOW
  figure("name", "03 直方图均衡");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(2, 2, 2); imagesc(g, [0 1]); axis image off; title("均衡后");
  subplot(2, 2, 3); bar(h); xlim([0 bins]); title("原直方图");
  subplot(2, 2, 4); bar(hg); xlim([0 bins]); title("均衡后直方图");
end
