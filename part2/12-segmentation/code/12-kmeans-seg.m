%% 12-kmeans-seg.m | 1D 特征空间聚类 / 迭代收敛 / 标签图
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; K = 3; max_iter = 30;
% ---- 造图：三级灰度的同心方环 + 轻微噪声 ----
[X, Y] = meshgrid(1:N, 1:N); randn("seed", 82);
d = max(abs(X-N/2), abs(Y-N/2));
f = 0.20*double(d > 30) + 0.50*double(d > 15 & d <= 30) + 0.85*double(d <= 15);
f = min(max(f + 0.02*randn(N,N), 0), 1);
% ---- 算法：交替更新归属与类中心 ----
data = f(:); centers = [0.15; 0.50; 0.90];
for it = 1:max_iter
  dist = abs(data - centers');       % 自动广播成 numel(data) x K
  [~, idx] = min(dist, [], 2);
  new_centers = centers;
  for k = 1:K
    if any(idx == k), new_centers(k) = mean(data(idx == k)); end
  end
  shift = max(abs(new_centers - centers));
  centers = new_centers;
  if shift < 1e-6, break; end
end
seg = reshape(idx, N, N);
% ---- 数值验证 ----
printf("真值灰度级: 0.20 / 0.70 / 0.85\n");
printf("收敛迭代数 = %d, 最终中心位移 = %.3e\n", it, shift);
printf("学到的类中心: "); printf("%.4f ", centers); printf("\n");
printf("各类像素数: "); printf("%d ", arrayfun(@(k) sum(idx==k), 1:K)); printf("\n");
printf("类内平方和 = %.4f\n", sum((data - centers(idx)).^2));
% ---- 可视化 ----
if SHOW
  figure("name", "12 k-means");
  subplot(1, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 2, 2); imagesc(seg); axis image off; title("聚类标签图");
end
