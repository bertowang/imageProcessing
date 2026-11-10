%% 09-label-regions.m | 4 连通 flood fill 标记 + 面积筛选
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; min_area = 100;
% ---- 造图：3 个矩形目标 + 2 个噪点 ----
[X, Y] = meshgrid(1:N, 1:N);
bw = double((X>8 & X<30 & Y>8 & Y<32) | (X>40 & X<66 & Y>40 & Y<70) ...
          | (X>72 & X<90 & Y>10 & Y<28));
bw(85, 85) = 1; bw(5, 90) = 1;
% ---- 算法：逐像素扫描，遇未标记前景就做一次 flood fill ----
labels = zeros(N, N); count = 0; areas = [];
for r = 1:N
  for c = 1:N
    if bw(r,c) == 1 && labels(r,c) == 0
      count = count + 1;
      stack = [r, c]; labels(r,c) = count; area = 0;
      while ~isempty(stack)
        cur = stack(end, :); stack(end, :) = [];
        rr = cur(1); cc = cur(2); area = area + 1;
        nb = [rr-1 cc; rr+1 cc; rr cc-1; rr cc+1];
        for t = 1:4
          nr = nb(t,1); nc = nb(t,2);
          if nr >= 1 && nr <= N && nc >= 1 && nc <= N
            if bw(nr,nc) == 1 && labels(nr,nc) == 0
              labels(nr,nc) = count;
              stack = [stack; nr, nc];
            end
          end
        end
      end
      areas(count) = area;
    end
  end
end
big = zeros(N, N);
for k = 1:count
  if areas(k) >= min_area, big(labels == k) = 1; end
end
% ---- 数值验证 ----
printf("连通域总数 = %d（3 个目标 + 2 个噪点）\n", count);
printf("各连通域面积: "); printf("%d ", areas); printf("\n");
printf("面积 >= %d 的域数 = %d, 筛后前景 = %d\n", min_area, sum(areas >= min_area), sum(big(:)));
printf("噪点 (85,85) 的标签 = %d, 筛后灰度 = %d\n", labels(85,85), big(85,85));
printf("最大目标面积 = %d（理论 26x30=780 附近）\n", max(areas));
% ---- 可视化 ----
if SHOW
  figure("name", "09 连通域");
  subplot(1, 2, 1); imagesc(labels); axis image off; title("标记图（颜色=域编号）");
  subplot(1, 2, 2); imagesc(big, [0 1]); colormap gray; axis image off; title("面积筛选后");
end
