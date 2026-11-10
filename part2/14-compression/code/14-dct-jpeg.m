%% 14-dct-jpeg.m | DCT 矩阵 / 量化表 / 零系数比例 / PSNR
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; bs = 8; qscale = 2.0;      % qscale 越大压缩越狠
% ---- 造图：方块 + 渐变 + 细纹理 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.30 + 0.35*(X/N) + 0.20*double(X>40 & X<80 & Y>40 & Y<80);
f = min(max(f + 0.05*sin(X/2).*sin(Y/2), 0), 1);
% ---- 算法 1：构造 8x8 正交 DCT 矩阵 ----
T = zeros(bs, bs);
for u = 0:bs-1
  for x = 0:bs-1
    T(u+1, x+1) = sqrt((1 + double(u>0)) / bs) * cos(pi*(2*x+1)*u/(2*bs));
  end
end
% ---- 算法 2：标准亮度量化表（近似）----
Q = [16 11 10 16 24 40 51 61; 12 12 14 19 26 58 60 55;
     14 13 16 24 40 57 69 56; 14 17 22 29 51 87 80 62;
     18 22 37 56 68 109 103 77; 24 35 55 64 81 104 113 92;
     49 64 78 87 103 121 120 101; 72 92 95 98 112 100 103 99];
Qs = Q * qscale;
% ---- 算法 3：逐块 DCT -> 量化 -> 反量化 -> IDCT ----
out = zeros(N, N); nzero = 0; ncoef = 0; dc_energy = 0; all_energy = 0;
for r = 1:bs:N
  for c = 1:bs:N
    blk = f(r:r+bs-1, c:c+bs-1);
    D = T * blk * T';
    Dq = round(D ./ Qs);
    nzero = nzero + sum(Dq(:) == 0); ncoef = ncoef + bs*bs;
    dc_energy = dc_energy + D(1,1)^2; all_energy = all_energy + sum(D(:).^2);
    out(r:r+bs-1, c:c+bs-1) = T' * (Dq .* Qs) * T;
  end
end
% ---- 数值验证 ----
printf("T 正交性误差 |T*T'-I| = %.3e\n", max(abs((T*T' - eye(bs))(:))));
printf("直流能量占块内总能量 = %.4f（能量集中在低频）\n", dc_energy / all_energy);
printf("量化后零系数比例 = %.4f（qscale=%.1f）\n", nzero/ncoef, qscale);
printf("重建 MSE = %.6f, PSNR = %.2f dB\n", ...
       mean((f(:)-out(:)).^2), 10*log10(1/mean((f(:)-out(:)).^2)));
printf("重建灰度范围 = [%.3f, %.3f]（可能出现轻微越界）\n", min(out(:)), max(out(:)));
printf("提示：把 qscale 改成 0.5 / 8，观察零系数比例与 PSNR 的反向变化\n");
% ---- 可视化 ----
if SHOW
  figure("name", "14 JPEG 内核");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 3, 2); imagesc(min(max(out,0),1), [0 1]); axis image off; title("重建图");
  subplot(1, 3, 3); imagesc(abs(f - out)*5); axis image off; title("误差 x5（块效应）");
end
