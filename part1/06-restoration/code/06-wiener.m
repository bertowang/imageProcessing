%% 06-wiener.m | 退化模型 / 逆滤波 / 维纳滤波 / PSNR 对照
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; psf_sigma = 1.4; noise_sigma = 0.02; K = 0.02; k = 9;
randn("seed", 41);
% ---- 造图：文字状方块 + 细线 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.20 + 0.55*double(X > N/4 & X < 3*N/4 & Y > N/3 & Y < 2*N/3);
f(abs(Y - N/4) < 2) = 0.85;
% ---- 造 PSF：高斯核放入 NxN 左上角（DFT 周期原点）----
[PX, PY] = meshgrid(-(k-1)/2:(k-1)/2, -(k-1)/2:(k-1)/2);
psf = exp(-(PX.^2 + PY.^2) / (2*psf_sigma^2)); psf = psf / sum(psf(:));
P = zeros(N, N); P(1:k, 1:k) = psf;
H = fft2(P);
% ---- 退化：频域卷积 + 加性高斯噪声 ----
G = H .* fft2(f);
blurred = real(ifft2(G));
g = blurred + noise_sigma * randn(N, N);
G = fft2(g);
% ---- 复原 1：朴素逆滤波（加极小保护避免除零）----
f_inv = real(ifft2(G ./ (H + 1e-12)));
% ---- 复原 2：维纳滤波 ----
f_wie = real(ifft2(conj(H) ./ (abs(H).^2 + K) .* G));
% ---- 数值验证 ----
psnr_ = @(a,b) 10*log10(1 / max(mean((a(:)-b(:)).^2), eps));
printf("PSF 和 = %.6f, |H| 最小值 = %.6f（接近 0 的地方会放大噪声）\n", ...
       sum(psf(:)), min(abs(H(:))));
printf("PSNR: 模糊+噪声 %.2f dB -> 逆滤波 %.2f dB -> 维纳 %.2f dB\n", ...
       psnr_(g, f), psnr_(f_inv, f), psnr_(f_wie, f));
printf("逆滤波结果标准差 = %.4f（远大于原图 %.4f，说明噪声被放大）\n", ...
       std(f_inv(:)), std(f(:)));
printf("维纳结果标准差 = %.4f\n", std(f_wie(:)));
printf("提示：把 K 改成 0 / 0.001 / 0.2，看 PSNR 先升后降\n");
% ---- 可视化 ----
if SHOW
  figure("name", "06 维纳复原");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原始 f");
  subplot(2, 2, 2); imagesc(g, [0 1]); axis image off; title("模糊 + 噪声 g");
  subplot(2, 2, 3); imagesc(f_inv); axis image off; title("逆滤波（噪声爆炸）");
  subplot(2, 2, 4); imagesc(f_wie, [0 1]); axis image off; title("维纳滤波");
end
