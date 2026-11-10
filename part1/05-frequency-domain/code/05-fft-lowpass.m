%% 05-fft-lowpass.m | fft2 / fftshift / 高斯低通 / 能量统计
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; D0 = 18;
% ---- 造图：圆盘 + 竖直条纹 + 高斯噪声 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.30 + 0.45*double((X-N/2).^2 + (Y-N/2).^2 < (N/5)^2);
f = f + 0.10*sin(2*pi*X/8);
f = min(max(f, 0), 1);
% ---- 算法 1：频谱与中心化 ----
F = fft2(f);
Fc = fftshift(F);
mag = log(1 + abs(Fc));
printf("F(1,1) = %.2f + %.2fi, 图像均值 = %.4f (直流/像素数)\n", ...
       real(F(1,1)), imag(F(1,1)), mean(f(:)));
printf("直流能量占比 = %.4f\n", abs(F(1,1))^2 / sum(abs(F(:)).^2));
% ---- 算法 2：高斯低通（以中心为原点构造 H）----
[U, V] = meshgrid(1:N, 1:N);
D = sqrt((U - N/2 - 1).^2 + (V - N/2 - 1).^2);
H = exp(-D.^2 / (2*D0^2));
g = real(ifft2(ifftshift(H) .* F));
% ---- 数值验证 ----
printf("H 中心值 = %.4f, H 角落值 = %.6f\n", H(N/2+1, N/2+1), H(1,1));
printf("滤波前后均值: %.4f -> %.4f (低通不改直流)\n", mean(f(:)), mean(g(:)));
printf("滤波前后标准差: %.4f -> %.4f (高频被衰减)\n", std(f(:)), std(g(:)));
printf("保留的频谱能量比例 = %.4f\n", sum(sum(abs(ifftshift(H).*F).^2)) / sum(abs(F(:)).^2));
printf("低通结果 MSE = %.6f, PSNR = %.2f dB\n", ...
       mean((f(:)-g(:)).^2), 10*log10(1/mean((f(:)-g(:)).^2)));
% ---- 可视化 ----
if SHOW
  figure("name", "05 频域低通");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 3, 2); imagesc(mag); axis image off; title("log 幅度谱（中心化）");
  subplot(1, 3, 3); imagesc(min(max(g,0),1), [0 1]); axis image off; title("高斯低通后");
end
