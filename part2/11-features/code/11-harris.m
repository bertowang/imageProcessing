%% 11-harris.m | 自相关矩阵 / Harris 响应 / 角点定位
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; k = 0.05; thresh = 0.005;
% ---- 造图：一个矩形（4 个直角）+ 一个圆盘（无角点）----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.15 + 0.65*double(X>20 & X<45 & Y>20 & Y<45);
f = f + 0.5*double((X-70).^2 + (Y-65).^2 < 15^2);
f = min(max(f, 0), 1);
% ---- 算法：梯度 -> M 的三个分量 -> R = det - k*trace^2 ----
Gx = [-1 0 1]; Gy = Gx';
dx = conv2(f, Gx, "same"); dy = conv2(f, Gy, "same");
w = ones(5,5)/25;
A = conv2(dx.^2, w, "same");
B = conv2(dy.^2, w, "same");
C = conv2(dx.*dy, w, "same");
R = A.*B - C.^2 - k*(A + B).^2;
% ---- 非极大抑制（3x3）----
% 手写 3x3 非极大抑制，不依赖 image 包
% 手写等价实现（始终有效，覆盖上一行结果）
p = 1; rp = zeros(N+2, N+2); rp(2:N+1, 2:N+1) = R;
peak = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = rp(r:r+2, c:c+2);
    peak(r,c) = double(R(r,c) == max(blk(:)) && R(r,c) > thresh);
  end
end
[rr, cc] = find(peak);
% ---- 数值验证 ----
printf("Harris 响应: min=%.6f max=%.6f\n", min(R(:)), max(R(:)));
printf("平坦区响应 (5,5) = %.6f, 边缘响应 (30,20) = %.6f\n", R(5,5), R(30,20));
printf("检测到的角点数 = %d（矩形约 4 个）\n", numel(rr));
printf("前几个角点坐标 (行,列): ");
for t = 1:min(6, numel(rr)), printf("(%d,%d) ", rr(t), cc(t)); end
printf("\n");
% ---- 可视化 ----
if SHOW
  figure("name", "11 Harris 角点"); imagesc(f, [0 1]); colormap gray; axis image off;
  hold on; plot(cc, rr, "r+", "markersize", 12); hold off; title("角点响应峰值");
end
