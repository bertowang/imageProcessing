%% 10-canny-core.m | Canny 核心四步（滞后连接用 3x3 膨胀近似）
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; sigma = 1.2; Th = 0.30; Tl = 0.12; randn("seed", 62);
% ---- 造图 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.25 + 0.55*double((X-64).^2 + (Y-64).^2 < 32^2);
f(15:40, 15:40) = 0.85;
f = min(max(f + 0.015*randn(N,N), 0), 1);
% ---- 1) 高斯平滑 ----
x = -4:4; w = exp(-x.^2/(2*sigma^2)); w = w/sum(w);
s = conv2(conv2(f, w, "same"), w', "same");
% ---- 2) 梯度 ----
Gx = [1 2 1]' * [-1 0 1]; Gy = [-1 0 1]' * [1 2 1];
dx = conv2(s, Gx, "same"); dy = conv2(s, Gy, "same");
mag = sqrt(dx.^2 + dy.^2); ang = mod(atan2(dy,dx)*180/pi, 180);
% ---- 3) 非极大抑制（方向量化到 4 类）----
nms = mag;
for r = 2:N-1
  for c = 2:N-1
    a = ang(r,c);
    if a < 22.5 || a >= 157.5,     n1 = mag(r,c-1);   n2 = mag(r,c+1);
    elseif a < 67.5,               n1 = mag(r-1,c+1); n2 = mag(r+1,c-1);
    elseif a < 112.5,              n1 = mag(r-1,c);   n2 = mag(r+1,c);
    else,                          n1 = mag(r-1,c-1); n2 = mag(r+1,c+1); end
    if mag(r,c) < n1 || mag(r,c) < n2, nms(r,c) = 0; end
  end
end
% ---- 4) 双阈值 + 弱边缘与强边缘连通性（膨胀近似）----
strong = nms > Th; weak = nms > Tl & nms <= Th;
p = ones(3,3); grow = conv2(double(strong), p, "same") > 0;
final = strong | (weak & grow);
% ---- 数值验证 ----
printf("平滑后噪声标准差估计 = %.5f\n", std(s(1:10,1:10)(:)));
printf("NMS 前非零像素 = %d, NMS 后 = %d（细化比例 %.1f%%）\n", ...
       sum(mag(:)>0), sum(nms(:)>0), 100*sum(nms(:)>0)/sum(mag(:)>0));
printf("强边缘 = %d, 弱边缘 = %d, 最终保留 = %d\n", ...
       sum(strong(:)), sum(weak(:)), sum(final(:)));
printf("参数比 Tl/Th = %.3f（常用 0.4）\n", Tl/Th);
% ---- 可视化 ----
if SHOW
  figure("name", "10 Canny 核心");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 3, 2); imagesc(mag); axis image off; title("梯度幅值");
  subplot(1, 3, 3); imagesc(final, [0 1]); axis image off; title("NMS + 双阈值");
end
