%% 02-conv-and-psnr.m | 二维卷积 / 边界策略 / MSE-PSNR 的一致性
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 64; noise_sigma = 0.05; k = 3; randn("seed", 11);
% ---- 造图：中心方块 ----
[X, Y] = meshgrid(1:N, 1:N);
f = double(X > N/4 & X < 3*N/4 & Y > N/4 & Y < 3*N/4);
% ---- 算法 1：盒式核 + 补零卷积（与 conv2 对照）----
w = ones(k, k) / (k*k);
g_zero = conv2(f, w, "same");
pad = (k-1)/2;
fp = zeros(N + 2*pad, N + 2*pad);
fp(pad+1:pad+N, pad+1:pad+N) = f;       % zero padding
g_manual = zeros(N, N);
for r = 1:N
  for c = 1:N
    g_manual(r,c) = sum(sum(fp(r:r+k-1, c:c+k-1) .* w));
  end
end
printf("核元素和 = %.6f（应为 1）\n", sum(w(:)));
printf("手写卷积与 conv2 的最大差 = %.3e\n", max(abs(g_manual(:)-g_zero(:))));
% ---- 算法 2：replicate 边界 ----
fr = [repmat(f(1,:), pad, 1); f; repmat(f(end,:), pad, 1)];
fr = [repmat(fr(:,1), 1, pad), fr, repmat(fr(:,end), 1, pad)];
g_rep = conv2(fr, w, "valid");
printf("角落像素 zero=%.4f replicate=%.4f（差异来自边界）\n", g_zero(1,1), g_rep(1,1));
% ---- 算法 3：MSE / PSNR ----
g_noisy = min(max(f + noise_sigma*randn(N,N), 0), 1);
mse = mean((g_noisy(:) - f(:)).^2);
printf("加噪后 MSE=%.6f, PSNR=%.2f dB（理论约 %.2f dB）\n", ...
       mse, 10*log10(1/mse), 10*log10(1/noise_sigma^2));
% ---- 可视化 ----
if SHOW
  figure("name", "02 卷积与边界");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 3, 2); imagesc(g_zero, [0 1]); axis image off; title("zero 卷积");
  subplot(1, 3, 3); imagesc(g_rep, [0 1]); axis image off; title("replicate 卷积");
end
