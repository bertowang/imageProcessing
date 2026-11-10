%% 15-full-pipeline.m | 传统算法综合流水线（颗粒计数与测量）
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区（消融实验只改这里）----
N = 160; sigma = 1.2; min_area = 150; noise_sigma = 0.05;
randn("seed", 151); rand("seed", 151);
centers = [40 40; 105 45; 65 105; 120 120];   % 4 个真值颗粒 (列, 行)
R = 16;
% ---- 1) 造图：4 个圆盘 + 亮度漂移 + 噪声 + 孤立亮点 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.18 + 0.10*(X/N);                          % 缓慢亮度漂移
for k = 1:rows(centers)
  f = f + 0.55*double((X-centers(k,1)).^2 + (Y-centers(k,2)).^2 < R^2);
end
f = min(max(f + noise_sigma*randn(N,N), 0), 1);
sp = rand(N,N);
f(sp < 0.001) = 1;                              % 少量孤立亮点
% ---- 2) 平滑：可分离高斯 ----
x = -4:4; w = exp(-x.^2/(2*sigma^2)); w = w/sum(w);
s = conv2(conv2(f, w, "same"), w', "same");
% ---- 3) Otsu 阈值 ----
bins = 64; q = round(s(:)*(bins-1)) + 1;
h = zeros(bins,1);
for i = 1:numel(q), h(q(i)) = h(q(i)) + 1; end
levels = (0:bins-1)'/(bins-1); total = numel(q);
best = -1; bt = 2;
for t = 2:bins
  w0 = sum(h(1:t-1))/total; w1 = 1-w0;
  if w0 == 0 || w1 == 0, continue; end
  m0 = sum(levels(1:t-1).*h(1:t-1))/sum(h(1:t-1));
  m1 = sum(levels(t:bins).*h(t:bins))/sum(h(t:bins));
  v = w0*w1*(m0-m1)^2;
  if v > best, best = v; bt = t; end
end
bw = s > levels(bt);
% ---- 4) 形态学开运算（3x3 腐蚀再膨胀，内联实现）----
p = 1; ae = zeros(N+2, N+2); ae(2:N+1, 2:N+1) = bw;
ero = zeros(N,N);
for r = 1:N
  for c = 1:N, blk = ae(r:r+2, c:c+2); ero(r,c) = double(all(blk(:)==1)); end
end
ad = zeros(N+2, N+2); ad(2:N+1, 2:N+1) = ero;
clean = zeros(N,N);
for r = 1:N
  for c = 1:N, blk = ad(r:r+2, c:c+2); clean(r,c) = double(any(blk(:)==1)); end
end
% ---- 5) 4 连通域标记 ----
labels = zeros(N,N); count = 0; areas = []; cents = [];
for r = 1:N
  for c = 1:N
    if clean(r,c) == 1 && labels(r,c) == 0
      count = count + 1; stack = [r, c]; labels(r,c) = count;
      area = 0; sr = 0; sc = 0;
      while ~isempty(stack)
        cur = stack(end,:); stack(end,:) = [];
        rr = cur(1); cc = cur(2); area = area + 1; sr = sr + rr; sc = sc + cc;
        nb = [rr-1 cc; rr+1 cc; rr cc-1; rr cc+1];
        for t = 1:4
          nr = nb(t,1); nc = nb(t,2);
          if nr>=1 && nr<=N && nc>=1 && nc<=N && clean(nr,nc)==1 && labels(nr,nc)==0
            labels(nr,nc) = count; stack = [stack; nr, nc];
          end
        end
      end
      areas(count) = area; cents(count,:) = [sc/area, sr/area];
    end
  end
end
keep = find(areas >= min_area);
% ---- 6) 统计输出 ----
printf("==== 颗粒计数流水线报告 ====\n");
printf("参数: sigma=%.2f min_area=%d noise=%.3f | Otsu 阈值=%.4f\n", sigma, min_area, noise_sigma, levels(bt));
printf("真值颗粒数 = %d, 阈值后连通域 = %d, 面积筛后 = %d\n", rows(centers), count, numel(keep));
printf("理论单颗粒面积 = %.0f (pi*R^2, R=%d)\n", pi*R^2, R);
printf("保留域面积: "); printf("%d ", areas(keep)); printf("\n");
printf("保留域质心 (列,行):\n"); printf("  (%.1f, %.1f)\n", cents(keep,1), cents(keep,2));
printf("保留域平均面积 = %.1f, 面积标准差 = %.1f\n", mean(areas(keep)), std(areas(keep)));
printf("计数误差 = %d\n", abs(numel(keep) - rows(centers)));
% ---- 可视化 ----
if SHOW
  figure("name", "15 综合流水线");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("输入图");
  subplot(2, 2, 2); imagesc(bw, [0 1]); axis image off; title("Otsu 掩模");
  subplot(2, 2, 3); imagesc(clean, [0 1]); axis image off; title("开运算后");
  subplot(2, 2, 4); imagesc(labels); axis image off; title("连通域标记");
end
