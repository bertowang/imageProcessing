%% 04-median-sharpen.m | 中值滤波 / 拉普拉斯 / USM 对照
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
salt_rate = 0.06; win = 3; lambda = 0.8; N = 128;
rand("seed", 33);
% ---- 造图：阶跃 + 细线 + 椒盐噪声 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.25 + 0.45*double(X > N/2);
f(abs(Y - N/2) < 2) = 0.9;                     % 一根细线，用来观察是否被抹掉
sp = rand(N, N);
noisy = f;
noisy(sp < salt_rate/2) = 0; noisy(sp > 1-salt_rate/2) = 1;
% ---- 算法 1：手写中值滤波（补 replicate 边界）----
p = (win-1)/2;
a = [repmat(noisy(1,:), p, 1); noisy; repmat(noisy(end,:), p, 1)];
a = [repmat(a(:,1), 1, p), a, repmat(a(:,end), 1, p)];
med = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = a(r:r+win-1, c:c+win-1);
    med(r,c) = median(blk(:));
  end
end
% ---- 算法 2：线性均值滤波（作对照）----
mean3 = conv2(a, ones(win,win)/(win^2), "valid");
% ---- 算法 3：拉普拉斯 + USM 锐化 ----
lap = [0 1 0; 1 -4 1; 0 1 0];
sharp = med + lambda * conv2(med, lap, "same");
blur = conv2(med, ones(3,3)/9, "same");
usm = med + lambda * (med - blur);
% ---- 数值验证 ----
printf("椒盐污染像素比例 = %.4f\n", mean(sp < salt_rate/2 | sp > 1-salt_rate/2));
printf("对干净图的 MSE: 加噪 %.6f -> 中值 %.6f -> 均值 %.6f\n", ...
       mean((noisy(:)-f(:)).^2), mean((med(:)-f(:)).^2), mean((mean3(:)-f(:)).^2));
printf("中值结果中的 0/1 极值像素数 = %d（应远少于加噪图 %d）\n", ...
       sum(med(:)==0 | med(:)==1), sum(noisy(:)==0 | noisy(:)==1));
printf("锐化后 min=%.4f max=%.4f（越界说明有 overshoot）\n", min(sharp(:)), max(sharp(:)));
a = sharp(:) - mean(sharp(:)); b = usm(:) - mean(usm(:));
cc = sum(a .* b) / sqrt(sum(a.^2) * sum(b.^2));
printf("USM 与拉普拉斯锐化的相关系数 = %.4f\n", cc);
% ---- 可视化 ----
if SHOW
  figure("name", "04 中值与锐化");
  subplot(2, 2, 1); imagesc(noisy, [0 1]); colormap gray; axis image off; title("椒盐噪声");
  subplot(2, 2, 2); imagesc(med, [0 1]); axis image off; title("3x3 中值");
  subplot(2, 2, 3); imagesc(mean3, [0 1]); axis image off; title("3x3 均值（对照）");
  subplot(2, 2, 4); imagesc(usm, [0 1]); axis image off; title("USM 锐化");
end
