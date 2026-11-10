%% 13-moments-lbp.m | 面积/质心/中心矩 + 3x3 LBP 编码直方图
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; bins = 256;
% ---- 造图：椭圆掩模，并做一个平移副本 ----
[X, Y] = meshgrid(1:N, 1:N);
bw = double(((X-40)/20).^2 + ((Y-45)/30).^2 <= 1);
shifted = zeros(N, N);
shifted(9:N, 13:N) = bw(1:N-8, 1:N-12);
g = 0.30 + 0.40*bw + 0.10*sin(X/3).*sin(Y/4);
% ---- 算法 1：面积 / 质心 / 二阶中心矩 ----
% 面积 / 质心 / 二阶中心矩（匿名函数）
mm = @(a) [sum(a(:)), ...
           sum(X(:).*a(:))/sum(a(:)), sum(Y(:).*a(:))/sum(a(:)), ...
           sum(((X(:)-sum(X(:).*a(:))/sum(a(:))).^2).*a(:))/sum(a(:)), ...
           sum(((Y(:)-sum(Y(:).*a(:))/sum(a(:))).^2).*a(:))/sum(a(:))];
m1 = mm(bw); m2 = mm(shifted);
printf("原图: 面积=%.0f 质心=(%.2f, %.2f) mu20=%.2f mu02=%.2f\n", m1(1),m1(2),m1(3),m1(4),m1(5));
printf("平移: 面积=%.0f 质心=(%.2f, %.2f) mu20=%.2f mu02=%.2f\n", m2(1),m2(2),m2(3),m2(4),m2(5));
printf("质心差 = (%.2f, %.2f)（应等于平移量 12, 8）\n", m2(2)-m1(2), m2(3)-m1(3));
printf("中心矩差 = (%.6f, %.6f)（中心矩对平移不变）\n", m2(4)-m1(4), m2(5)-m1(5));
% ---- 算法 2：3x3 LBP（8 邻域，边界补零）----
p = 1; a = zeros(N+2, N+2); a(2:N+1, 2:N+1) = g;
off = [-1 -1; -1 0; -1 1; 0 1; 1 1; 1 0; 1 -1; 0 -1];
lbp = zeros(N, N);
for r = 1:N
  for c = 1:N
    code = 0;
    for t = 1:8
      code = code + double(a(r+1+off(t,1), c+1+off(t,2)) >= a(r+1, c+1)) * 2^(t-1);
    end
    lbp(r,c) = code;
  end
end
hist_lbp = zeros(bins,1);
for i = 1:numel(lbp), hist_lbp(lbp(i)+1) = hist_lbp(lbp(i)+1) + 1; end
printf("LBP 编码种类 = %d / %d, 最常见编码 = %d（占比 %.3f）\n", ...
       sum(hist_lbp>0), bins, find(hist_lbp==max(hist_lbp),1)-1, max(hist_lbp)/numel(lbp));
printf("编码 0 与 255 的像素数 = %d / %d（平坦区占多数）\n", hist_lbp(1), hist_lbp(256));
% ---- 可视化 ----
if SHOW
  figure("name", "13 描述与纹理");
  subplot(1, 3, 1); imagesc(bw, [0 1]); colormap gray; axis image off; title("椭圆掩模");
  subplot(1, 3, 2); imagesc(lbp); axis image off; title("LBP 编码图");
  subplot(1, 3, 3); bar(hist_lbp); xlim([0 bins]); title("LBP 直方图（特征向量）");
end
