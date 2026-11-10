%% A-template.m | 本书所有 Octave 示例的模板
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区：所有可调量集中在这里 ----
N = 128; sigma = 0.05; randn("seed", 1);
% ---- 造图 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.30 + 0.50*double((X-N/2).^2 + (Y-N/2).^2 < (N/5)^2);
g = min(max(f + sigma*randn(N,N), 0), 1);
% ---- 算法 ----
w = ones(3,3)/9;
out = conv2(g, w, "same");
% ---- 数值验证：打印可手算核对的量 ----
printf("尺寸 %d x %d, 均值 %.4f -> %.4f\n", rows(f), columns(f), mean(g(:)), mean(out(:)));
printf("MSE(加噪) = %.6f, MSE(平滑) = %.6f\n", ...
       mean((g(:)-f(:)).^2), mean((out(:)-f(:)).^2));
% ---- 可视化：IP_HEADLESS=1 时自动跳过 ----
if SHOW
  figure("name", "模板");
  subplot(1, 2, 1); imagesc(g, [0 1]); colormap gray; axis image off; title("输入");
  subplot(1, 2, 2); imagesc(out, [0 1]); axis image off; title("输出");
end
