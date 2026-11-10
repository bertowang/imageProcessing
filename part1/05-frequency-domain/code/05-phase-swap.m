%% 05-phase-swap.m | 交换两幅图的 FFT 相位，观察结构跟谁走
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128;
% ---- 造两幅统计相似、结构不同的图 ----
[X, Y] = meshgrid(1:N, 1:N);
f1 = 0.30 + 0.45*double((X-N/2).^2 + (Y-N/2).^2 < (N/5)^2);
f2 = 0.30 + 0.45*double(abs(X - Y) < N/10);
printf("两图均值差 = %.6f, 标准差差 = %.6f\n", ...
       abs(mean(f1(:))-mean(f2(:))), abs(std(f1(:))-std(f2(:))));
% ---- 算法：幅度 A / 相位 B 重组 ----
A = fft2(f1); B = fft2(f2);
r1 = real(ifft2(abs(A) .* exp(1i*angle(B))));   % f1 的幅度 + f2 的相位
r2 = real(ifft2(abs(B) .* exp(1i*angle(A))));   % f2 的幅度 + f1 的相位
% ---- 数值验证：自写相关系数（匿名函数），不依赖 statistics 包 ----
corr2_ = @(a,b) sum((a(:)-mean(a(:))).*(b(:)-mean(b(:)))) / ...
                sqrt(sum((a(:)-mean(a(:))).^2) * sum((b(:)-mean(b(:))).^2));
printf("重组图1 与 f1 相关 = %.4f, 与 f2 相关 = %.4f\n", corr2_(r1,f1), corr2_(r1,f2));
printf("重组图2 与 f1 相关 = %.4f, 与 f2 相关 = %.4f\n", corr2_(r2,f1), corr2_(r2,f2));
printf("结论：谁提供相位，重建图就更像谁（斜线 vs 圆盘）\n");
% ---- 可视化 ----
if SHOW
  figure("name", "05 相位交换");
  subplot(2, 2, 1); imagesc(f1, [0 1]); colormap gray; axis image off; title("f1 圆盘");
  subplot(2, 2, 2); imagesc(f2, [0 1]); axis image off; title("f2 斜带");
  subplot(2, 2, 3); imagesc(r1); axis image off; title("f1 幅度 + f2 相位");
  subplot(2, 2, 4); imagesc(r2); axis image off; title("f2 幅度 + f1 相位");
end
