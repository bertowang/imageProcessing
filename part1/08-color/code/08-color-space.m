%% 08-color-space.m | 色彩空间转换 / 颜色分割 / 灰度世界白平衡
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; target = 0.60;
% ---- 造图：偏蓝光源下的红、绿、蓝色块 ----
rgb = 0.25 * ones(N, N, 3);
rgb(20:55, 20:55, 1) = 0.85;                 % 红块（被蓝色光源压暗）
rgb(20:55, 70:105, 2) = 0.85;                % 绿块
rgb(70:105, 20:55, 3) = 0.95;                % 蓝块
rgb(:,:,1) = rgb(:,:,1) * 0.75;              % 模拟偏蓝光源
rgb(:,:,3) = min(rgb(:,:,3) * 1.15, 1);
% ---- 算法 1：感知亮度 ----
Y = 0.299*rgb(:,:,1) + 0.587*rgb(:,:,2) + 0.114*rgb(:,:,3);
% ---- 算法 2：手写 RGB -> HSV ----
r = rgb(:,:,1); g = rgb(:,:,2); b = rgb(:,:,3);
mx = max(rgb, [], 3); mn = min(rgb, [], 3); d = mx - mn;
h = zeros(N, N);
idx = d > 0 & mx == r; h(idx) = mod((g(idx)-b(idx))./d(idx), 6);
idx = d > 0 & mx == g; h(idx) = (b(idx)-r(idx))./d(idx) + 2;
idx = d > 0 & mx == b; h(idx) = (r(idx)-g(idx))./d(idx) + 4;
h = h / 6;  s = d ./ (mx + eps);  v = mx;
% ---- 算法 3：灰度世界白平衡 ----
means = squeeze(mean(mean(rgb, 1), 2));
gain = target ./ means;
bal = rgb;
for ch = 1:3, bal(:,:,ch) = min(rgb(:,:,ch) * gain(ch), 1); end
new_means = squeeze(mean(mean(bal, 1), 2));
% ---- 算法 4：按色相分割红色（色相是环形量）----
mask = (h < 0.05 | h > 0.95) & s > 0.3 & v > 0.3;
% ---- 数值验证 ----
printf("灰度化 Y: mean=%.4f min=%.4f max=%.4f\n", mean(Y(:)), min(Y(:)), max(Y(:)));
printf("HSV 范围: H[%.3f,%.3f] S[%.3f,%.3f] V[%.3f,%.3f]\n", ...
       min(h(:)), max(h(:)), min(s(:)), max(s(:)), min(v(:)), max(v(:)));
printf("三通道均值（偏色）: %.4f %.4f %.4f\n", means(1), means(2), means(3));
printf("白平衡增益: %.4f %.4f %.4f\n", gain(1), gain(2), gain(3));
printf("白平衡后均值: %.4f %.4f %.4f（三通道被拉齐到 %.2f 附近）\n", ...
       new_means(1), new_means(2), new_means(3), target);
printf("红色掩模命中像素 = %d / %d（红块约 36x36=1296）\n", sum(mask(:)), N*N);
% ---- 可视化 ----
if SHOW
  figure("name", "08 彩色处理");
  subplot(2, 2, 1); imagesc(rgb); axis image off; title("偏蓝光源的 RGB");
  subplot(2, 2, 2); imagesc(Y, [0 1]); colormap gray; axis image off; title("感知亮度 Y");
  subplot(2, 2, 3); imagesc(bal); axis image off; title("灰度世界白平衡");
  subplot(2, 2, 4); imagesc(mask, [0 1]); axis image off; title("红色色相掩模");
end
