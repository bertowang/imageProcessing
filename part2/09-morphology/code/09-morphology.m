%% 09-morphology.m | 二值形态学四则运算（3x3 结构元素）
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; win = 3;
% ---- 造图：两个方块 + 孤立亮点 + 内部小孔 + 细毛刺 ----
[X, Y] = meshgrid(1:N, 1:N);
bw = double((X>15 & X<45 & Y>15 & Y<45) | (X>55 & X<85 & Y>50 & Y<80));
bw(70, 20) = 1;                       % 孤立亮点
bw(28:31, 28:31) = 0;                % 内部小孔
bw(45:52, 30) = 1;                   % 细毛刺
% ---- 工具：带零填充的局部窗口 ----
p = (win-1)/2;
a = zeros(N + 2*p, N + 2*p);
a(p+1:p+N, p+1:p+N) = bw;
% ---- 算法：腐蚀 = 窗口全 1；膨胀 = 窗口含 1 ----
ero = zeros(N, N); dil = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = a(r:r+win-1, c:c+win-1);
    ero(r,c) = double(all(blk(:) == 1));
    dil(r,c) = double(any(blk(:) == 1));
  end
end
% ---- 开 = 先腐蚀后膨胀；闭 = 先膨胀后腐蚀（同样用 win 邻域）----
ae = zeros(N + 2*p, N + 2*p); ae(p+1:p+N, p+1:p+N) = ero;
opened = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = ae(r:r+win-1, c:c+win-1);
    opened(r,c) = double(any(blk(:) == 1));
  end
end
ad = zeros(N + 2*p, N + 2*p); ad(p+1:p+N, p+1:p+N) = dil;
closed = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = ad(r:r+win-1, c:c+win-1);
    closed(r,c) = double(all(blk(:) == 1));
  end
end
% ---- 数值验证 ----
printf("原图前景 = %d, 腐蚀 = %d, 膨胀 = %d\n", sum(bw(:)), sum(ero(:)), sum(dil(:)));
printf("开运算 = %d（孤立点与毛刺被删：%d 个像素）\n", sum(opened(:)), sum(bw(:))-sum(opened(:)));
printf("闭运算 = %d（内部小孔被填：%d 个像素）\n", sum(closed(:)), sum(closed(:))-sum(bw(:)));
printf("孤立亮点 (70,20): 原 %d -> 开运算后 %d\n", bw(70,20), opened(70,20));
printf("小孔中心 (29,29): 原 %d -> 闭运算后 %d\n", bw(29,29), closed(29,29));
% ---- 可视化 ----
if SHOW
  figure("name", "09 形态学");
  subplot(2, 2, 1); imagesc(bw, [0 1]); colormap gray; axis image off; title("原二值图");
  subplot(2, 2, 2); imagesc(ero, [0 1]); axis image off; title("腐蚀");
  subplot(2, 2, 3); imagesc(opened, [0 1]); axis image off; title("开运算");
  subplot(2, 2, 4); imagesc(closed, [0 1]); axis image off; title("闭运算");
end
