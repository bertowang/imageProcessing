#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二篇 10-15：边缘、特征、分割、描述、压缩与传统算法综合实验。

代码契约见 chapters_00_04.py 的模块说明：零依赖、自包含、参数集中、数值可核对。
"""
from book_schema import C, demo

CH = [

C("10", "p2", "part2/10-edge-detection", "边缘检测",
  "边缘是图像的一阶导数极值、二阶导数过零；Canny 把这条数学事实变成了五个可调试的工程步骤。",
  hours="4 学时",
  goals=["能说明阶跃边缘在一阶/二阶导数上的表现",
         "能手工构造 Sobel 核并解释平滑与差分的组合",
         "说清 Canny 每一步解决什么问题、三个参数怎么调",
         "理解 LoG/DoG 与尺度空间的关系"],
  points=["边缘的数学模型", "梯度算子 Sobel / Prewitt", "梯度幅值与方向", "LoG 与尺度空间", "Canny 五步流程", "非极大抑制", "双阈值与滞后连接"],
  sections=[
      ("10.1", "边缘的数学模型", """<p>边缘是灰度<strong>不连续</strong>的地方。理想阶跃边缘的一阶导数是一个尖峰、二阶导数是一对正负过零点；真实成像总有模糊，所以边缘是<strong>斜坡</strong>，一阶导数变成有限宽的峰、二阶导数出现零交叉。</p>
<table><thead><tr><th>方法族</th><th>判据</th><th>代表</th></tr></thead><tbody>
<tr><td>一阶导数</td><td>梯度幅值超过阈值 + 局部极大</td><td>Roberts / Prewitt / Sobel / Canny</td></tr>
<tr><td>二阶导数</td><td>零交叉</td><td>Laplacian / LoG / Marr-Hildreth</td></tr>
<tr><td>参数模型</td><td>拟合阶跃后求亚像素位置</td><td>亚像素边缘、直线拟合</td></tr>
</tbody></table>
<p>二阶导数对噪声更敏感，因此几乎总要先高斯平滑——这就是 LoG（高斯拉普拉斯）名字的由来。</p>"""),
      ("10.2", "梯度算子与非极大抑制", """<p>Sobel 的 <code>x</code> 方向核是<strong>平滑（[1 2 1]）× 差分（[−1 0 1]）</strong>的外积：</p>
<span class="eq">Gₓ = [−1 0 1; −2 0 2; −1 0 1]，　G_y = Gₓᵀ，　|∇f| = √(Gₓ² + G_y²)，　θ = atan2(G_y, Gₓ)</span>
<p>常用 <code>|Gₓ|+|G_y|</code> 近似幅值以省去开方。得到幅值图后要<strong>非极大抑制（NMS）</strong>：沿梯度方向比较前后两个邻点，只保留局部最大，把粗边缘细化成单像素宽。方向先量化到 0°/45°/90°/135° 四类，再用对应邻点比较。</p>"""),
      ("10.3", "LoG、DoG 与尺度", """<p><code>LoG = ∇²(G_σ ∗ f)</code>，用不同 σ 卷积可检测<strong>不同尺度</strong>的边缘：σ 小看细节与噪声，σ 大看轮廓。两个相邻尺度的高斯差（DoG）是 LoG 的高效近似，既是 SIFT 关键点检测的基础（第 11 章），也是很多“细节增强”算法的原型。</p>
<div class="card note"><p style="margin-bottom:0">尺度选择不是玄学：<strong>σ 应匹配待检测结构的宽度</strong>。用同一个 σ 处理整幅图，等于假设所有边缘宽度相同；尺度空间方法显式承认这个假设不成立。</p></div>"""),
      ("10.4", "Canny 的五步与三个参数", """<ol><li><strong>高斯平滑</strong>（σ）：抑制噪声，但过大会丢细边缘。</li>
<li><strong>算梯度幅值与方向</strong>：Sobel 或其它一阶算子。</li>
<li><strong>非极大抑制</strong>：细化到单像素。</li>
<li><strong>双阈值</strong>（T_high、T_low）：高于 T_high 判为强边缘，介于两者判为弱边缘，低于 T_low 丢弃。</li>
<li><strong>滞后连接</strong>：弱边缘只有与强边缘连通才保留，从而在保住连续轮廓的同时抑制噪声碎片。</li></ol>
<p>三个参数的关系比绝对值更重要：常用 <code>T_low ≈ 0.4·T_high</code>。评估时不要只看“边缘好不好看”，还要看<strong>连通性、定位误差、重复率</strong>；下卷的检测/分割网络把这类低级边缘特征换成了学出来的层次特征，但 NMS 的思想在检测框后处理里原样保留（第 21 章）。</p>"""),
  ],
  demos=[
      demo("code/10-gradient.m", "Sobel 梯度、幅值与方向的数值对照", r"""%% 10-gradient.m | Sobel 梯度 / 幅值 / 方向 / 阈值边缘
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; thresh = 0.35;
% ---- 造图：圆盘 + 矩形，带一点噪声 ----
[X, Y] = meshgrid(1:N, 1:N); randn("seed", 61);
f = 0.25 + 0.5*double((X-70).^2 + (Y-64).^2 < 30^2);
f(20:45, 15:40) = 0.85;
f = min(max(f + 0.01*randn(N,N), 0), 1);
% ---- 算法：Sobel = 平滑 x 差分的外积 ----
smooth = [1 2 1]; diff = [-1 0 1];
Gx = smooth' * diff;  Gy = diff' * smooth;
dx = conv2(f, Gx, "same"); dy = conv2(f, Gy, "same");
mag = sqrt(dx.^2 + dy.^2);
dirn = atan2(dy, dx) * 180 / pi;
edges = mag > thresh;
% ---- 数值验证 ----
printf("Sobel Gx 元素和 = %.1f, Gy 元素和 = %.1f（差分核和为 0）\n", sum(Gx(:)), sum(Gy(:)));
printf("梯度幅值: max=%.4f mean=%.4f\n", max(mag(:)), mean(mag(:)));
printf("平坦区域中心幅值 = %.6f（应接近噪声量级）\n", mag(5,5));
printf("阈值 %.2f 下的边缘像素数 = %d / %d (%.2f%%)\n", ...
       thresh, sum(edges(:)), N*N, 100*mean(edges(:)));
printf("圆盘边界点 (70,34) 的梯度方向 = %.1f 度\n", dirn(34,70));
% ---- 可视化 ----
if SHOW
  figure("name", "10 Sobel 梯度");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(2, 2, 2); imagesc(abs(dx)); axis image off; title("|Gx| 竖直边缘响应");
  subplot(2, 2, 3); imagesc(mag); axis image off; title("梯度幅值");
  subplot(2, 2, 4); imagesc(edges, [0 1]); axis image off; title("阈值边缘（未细化）");
end""",
            "运行后把 <code>thresh</code> 改成 0.1 / 0.8，记录边缘像素数；观察阈值图里边缘是粗带而不是细线。",
            "两个 Sobel 核元素和均为 0；平坦区梯度接近噪声量级；圆盘边界处梯度方向沿径向；简单阈值得到的边缘较粗，说明需要非极大抑制。"),
      demo("code/10-canny-core.m", "可运行版 Canny 核心：平滑 → 梯度 → NMS → 双阈值", r"""%% 10-canny-core.m | Canny 核心四步（滞后连接用 3x3 膨胀近似）
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
end""",
            "运行后把 <code>sigma</code> 改成 3、<code>Th</code> 改成 0.1，观察强边缘数与断裂情况。",
            "NMS 把非零响应压缩到约几分之一，边缘变细；弱边缘中只有与强边缘相邻的部分被保留；σ 增大则细边缘消失、轮廓更连续；<code>Tl/Th</code> 约 0.4 是常用经验值。"),
  ],
  pitfalls=["直接对原图算梯度：噪声被当成边缘，阈值调不出来。",
            "NMS 时把梯度方向当成边缘方向：比较应沿<strong>梯度</strong>方向（垂直于边缘）进行。",
            "阈值用绝对灰度值而非梯度幅值：换一张对比度不同的图就失效。",
            "只看边缘图是否好看：不检查连通性会让后续轮廓提取（第 13 章）失败。"],
  exercises=["证明 Sobel 核可以写成 <code>[1 2 1]ᵀ·[−1 0 1]</code>，并解释为什么这样能同时平滑与差分。",
             "在 10-canny-core.m 里去掉 NMS 直接做双阈值，比较最终边缘像素数与视觉宽度。"],
  further=["<a href='../11-features/index.html'>第 11 章 局部特征与描述</a>",
           "<a href='../13-descriptors/index.html'>第 13 章 表示、描述与纹理</a>",
           "<a href='../../part3/17-cnn-fundamentals/index.html'>第 17 章 CNN 基础（学的第一层就是这些梯度核）</a>"]),

C("11", "p2", "part2/11-features", "局部特征、匹配与 Hough 变换",
  "把“这块图像”变成可比较的向量：Harris 找位置，SIFT/ORB 给描述，RANSAC 负责在错误匹配里挑出正确模型。",
  hours="4 学时",
  goals=["能写出 Harris 响应并解释 k 的作用",
         "说清 SIFT 的尺度、方向、描述子三步如何获得不变性",
         "理解比值测试与 RANSAC 为什么必要",
         "能用累加器数组实现直线 Hough 变换"],
  points=["自相关矩阵与 Harris", "尺度空间与 DoG", "SIFT / SURF / ORB", "描述子匹配与比值测试", "RANSAC 估计单应", "Hough 参数空间投票"],
  sections=[
      ("11.1", "角点与 Harris 响应", """<p>在局部窗口里平移 <code>[u,v]</code>，用自相关矩阵 <code>M = Σ w·[Iₓ² IₓI_y; IₓI_y I_y²]</code> 描述灰度变化。<code>M</code> 的两个特征值：都小 = 平坦区；一大一小 = 边缘；都大 = 角点。为避免算特征值，Harris 用：</p>
<span class="eq">R = det(M) − k·trace(M)²，　det = λ₁λ₂，　trace = λ₁ + λ₂</span>
<p><code>k</code> 常取 0.04～0.06；<code>R &gt; 0</code> 且局部极大判为角点。Shi-Tomasi 直接用 <code>min(λ₁,λ₂)</code>，在跟踪任务里更稳定。角点响应对旋转与光照线性变化不变，但<strong>对尺度不变</strong>——这是 SIFT 要解决的问题。</p>"""),
      ("11.2", "SIFT 与工程取舍", """<ol><li><strong>尺度空间极值</strong>：用 DoG 金字塔在 (x,y,σ) 三维里找局部极值，得到尺度不变的关键点位置。</li>
<li><strong>主方向</strong>：统计邻域梯度方向直方图，取峰值方向并把坐标系旋转对齐，获得旋转不变性。</li>
<li><strong>描述子</strong>：把 16×16 邻域分成 4×4 子块，每块统计 8 个方向，得 128 维向量；再做光照归一化。</li></ol>
<table><thead><tr><th>特征</th><th>描述子</th><th>速度</th><th>适合</th></tr></thead><tbody>
<tr><td>SIFT</td><td>128 维浮点</td><td>慢</td><td>高精度配准、三维重建、教学基准</td></tr>
<tr><td>SURF</td><td>64 维浮点</td><td>中</td><td>SIFT 的积分图加速版</td></tr>
<tr><td>ORB</td><td>256 bit 二值</td><td>快</td><td>SLAM、移动端实时匹配（汉明距离）</td></tr>
</tbody></table>"""),
      ("11.3", "匹配、比值测试与 RANSAC", """<p>最近邻匹配必然产生错误对应。<strong>比值测试</strong>：只有当“最近距离 / 次近距离 &lt; 0.7～0.8”才接受，因为重复纹理会让两个候选距离接近。<strong>RANSAC</strong>：随机抽最小样本（仿射 3 对、单应 4 对）估计模型，统计内点数，重复取最优，最后用全部内点重估。它能容忍相当比例的外点，是几何估计的标准做法（第 07 章配准就靠它）。</p>"""),
      ("11.4", "Hough 变换", """<p>直线用极坐标 <code>ρ = x·cosθ + y·sinθ</code> 参数化。每个边缘点对一组 <code>(θ, ρ)</code> 投票，累加器峰值就是共线点最多的参数组合。优点是<strong>对断裂、遮挡与孤立噪点鲁棒</strong>；代价是内存与时间随参数维度增长，圆检测（3 维）已明显变贵，广义 Hough 更复杂。</p>
<p class="code-hint">现代做法常用“分割网络输出边缘图 → 概率 Hough 或 RANSAC 拟合”的组合：上卷提供几何约束，下卷提供更好的边缘图，见第 22、26 章。</p>"""),
  ],
  demos=[
      demo("code/11-harris.m", "手写 Harris 角点响应与非极大抑制", r"""%% 11-harris.m | 自相关矩阵 / Harris 响应 / 角点定位
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
end""",
            "运行后把 <code>k</code> 改成 0.15、<code>thresh</code> 改成 0.001，观察角点数变化。",
            "响应在平坦区接近 0、边缘处为负或较小、角点处显著为正；矩形附近出现约 4 个峰值，圆盘没有明显角点；k 越大越倾向于只保留强角点。"),
  ],
  pitfalls=["Harris 直接使用 <code>dx.^2</code> 不做窗口聚合：响应充满噪声，找不到稳定峰值。",
            "以为 Harris 对尺度不变：图像放大后角点可能消失，需要 SIFT 的尺度空间。",
            "匹配时只用最近邻不做比值测试：重复纹理区域产生大量错误对应。",
            "Hough 的 ρ 出现负值直接丢弃：应允许负 ρ 或把 θ 范围取满 [0,π)。"],
  exercises=["把 11-harris.m 的窗口从 5×5 改成 9×9，解释为什么角点定位变粗但更抗噪。",
             "推导 <code>R = det(M) − k·trace(M)²</code> 在<code>λ₁=λ₂≫0</code>、<code>λ₁≫λ₂≈0</code>、两者都小三种情形下的符号。"],
  further=["<a href='../../part1/07-geometry-registration/index.html'>第 7 章 几何变换与配准</a>",
           "<a href='../../part3/16-learning-baselines/index.html'>第 16 章 从手工特征到学习</a>",
           "<a href='../../part4/21-object-detection/index.html'>第 21 章 目标检测（NMS 的另一种用法）</a>"]),

C("12", "p2", "part2/12-segmentation", "图像分割",
  "从 Otsu 的一个阈值到水平集的一条演化曲线：分割方法的选择，取决于你能对图像写出多强的先验。",
  hours="4 学时",
  goals=["能推导 Otsu 的类间方差准则并手写实现",
         "说清全局阈值、自适应阈值与聚类的适用边界",
         "能描述图割与活动轮廓各自优化的能量项",
         "会用连通域与形态学修整分割结果"],
  points=["全局阈值与 Otsu", "自适应阈值", "区域生长与分水岭", "k-means 颜色聚类", "图割与能量最小化", "活动轮廓与水平集"],
  sections=[
      ("12.1", "阈值与 Otsu", """<p>阈值分割假设<strong>直方图是双峰</strong>：目标与背景各占一峰。Otsu 不依赖人工选阈值，而是遍历所有候选 <code>t</code>，最大化类间方差：</p>
<span class="eq">σ_B²(t) = w₀(t)·w₁(t)·[ μ₀(t) − μ₁(t) ]²</span>
<p>等价于最小化类内方差。它只需直方图，复杂度 <code>O(L)</code>（L 为灰度级数），非常快；但<strong>光照不均、目标占比极小、直方图单峰</strong>时会失效。此时改用自适应阈值：每个像素用局部窗口的统计量算自己的阈值（如局部均值减常数 C）。</p>"""),
      ("12.2", "区域、聚类与形态学后处理", """<ul><li><strong>区域生长</strong>：从种子出发，把满足相似性（灰度差、颜色距离）的邻像素并进来；关键是种子与停止准则。</li>
<li><strong>分水岭</strong>：第 09 章的距离变换 + 标记控制流程，特别适合粘连圆形目标。</li>
<li><strong>k-means 聚类</strong>：把每个像素看作特征向量（灰度、RGB、Lab，或加上位置），迭代更新类中心与归属；对初值敏感、需指定 K。</li>
<li><strong>后处理</strong>：开运算去噪点、闭运算填孔、连通域面积筛选、边界平滑——工业流水线里这一步往往比换分割算法更有效。</li></ul>
<p>无论用哪种方法，输出都应是<strong>逻辑掩模</strong>（整数标签），后续插值/缩放只能用最近邻，见第 07 章。</p>"""),
      ("12.3", "能量最小化：图割与活动轮廓（研究生）", """<p>把分割写成给每个像素赋标签的能量最小化问题：</p>
<span class="eq">E(L) = Σ_p D_p(L_p) + λ Σ_(p,q) V(L_p, L_q)</span>
<p><strong>数据项</strong> <code>D</code> 描述像素像不像某类（可由颜色直方图建模），<strong>平滑项</strong> <code>V</code> 惩罚相邻像素标签不同（常用 Potts 模型）。当 V 是次模函数时，二值分割可用<strong>图割 / 最大流最小割</strong>求全局最优；这也是 GrabCut 交互式分割的核心。</p>
<p><strong>活动轮廓（snake）</strong>则把边界参数化为曲线，最小化<em>内部弹性能 + 图像梯度吸引能 + 外部约束</em>；<strong>水平集</strong>把曲线嵌入高一维函数的零水平集，从而自然处理拓扑变化（分裂/合并）。二者优化的是连续几何，与图割的离散标签视角互补。这一支“可优化的能量模型”正是下卷用损失函数 + 反向传播取代的对象。</p>"""),
  ],
  demos=[
      demo("code/12-otsu.m", "手写 Otsu：遍历 256 个阈值的类间方差", r"""%% 12-otsu.m | 直方图 / 类间方差 / 自动阈值 / 误分率
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; bins = 256; bg = 0.25; fg = 0.75; noise_sigma = 0.06;
randn("seed", 81);
% ---- 造图：亮目标 + 暗背景 + 高斯噪声 ----
[X, Y] = meshgrid(1:N, 1:N);
truth = double((X-64).^2 + (Y-64).^2 < 30^2);
f = bg + (fg-bg)*truth + noise_sigma*randn(N,N);
f = min(max(f, 0), 1);
% ---- 算法：直方图 -> 遍历阈值 -> 最大类间方差 ----
q = round(f(:)*(bins-1)) + 1;
h = zeros(bins,1);
for i = 1:numel(q), h(q(i)) = h(q(i)) + 1; end
total = numel(q); levels = (0:bins-1)' / (bins-1);
best_var = -1; best_t = 1;
for t = 2:bins
  w0 = sum(h(1:t-1)) / total; w1 = 1 - w0;
  if w0 == 0 || w1 == 0, continue; end
  m0 = sum(levels(1:t-1) .* h(1:t-1)) / sum(h(1:t-1));
  m1 = sum(levels(t:bins) .* h(t:bins)) / sum(h(t:bins));
  v = w0 * w1 * (m0 - m1)^2;
  if v > best_var, best_var = v; best_t = t; end
end
T = levels(best_t);
seg = f > T;
% ---- 数值验证 ----
printf("直方图总和 = %d, 像素总数 = %d\n", sum(h), total);
printf("Otsu 阈值 = %.4f（理论中点在 (%.2f+%.2f)/2 = %.2f）\n", T, bg, fg, (bg+fg)/2);
printf("最大类间方差 = %.6f\n", best_var);
printf("前景占比 = %.4f（真值 %.4f）\n", mean(seg(:)), mean(truth(:)));
printf("误分率 = %.4f%%\n", 100*mean(seg(:) ~= truth(:)));
printf("把噪声提高到 0.20 后误分率会明显上升，可自行验证\n");
% ---- 可视化 ----
if SHOW
  figure("name", "12 Otsu 分割");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("加噪图");
  subplot(1, 3, 2); bar(h); xlim([0 bins]); title("双峰直方图");
  subplot(1, 3, 3); imagesc(seg, [0 1]); axis image off; title("Otsu 掩模");
end""",
            "运行后把 <code>noise_sigma</code> 改成 0.20、把前景面积缩小到半径 10，分别记录阈值与误分率。",
            "直方图总和等于像素数；阈值应落在 0.5 附近（两峰中点）；最大类间方差约 0.06 量级；噪声变大或目标占比极小时，阈值偏移、误分率上升。"),
      demo("code/12-kmeans-seg.m", "手写 k-means 灰度聚类与收敛过程", r"""%% 12-kmeans-seg.m | 1D 特征空间聚类 / 迭代收敛 / 标签图
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; K = 3; max_iter = 30;
% ---- 造图：三级灰度的同心方环 + 轻微噪声 ----
[X, Y] = meshgrid(1:N, 1:N); randn("seed", 82);
d = max(abs(X-N/2), abs(Y-N/2));
f = 0.20*double(d > 30) + 0.50*double(d > 15 & d <= 30) + 0.85*double(d <= 15);
f = min(max(f + 0.02*randn(N,N), 0), 1);
% ---- 算法：交替更新归属与类中心 ----
data = f(:); centers = [0.15; 0.50; 0.90];
for it = 1:max_iter
  dist = abs(data - centers');       % 自动广播成 numel(data) x K
  [~, idx] = min(dist, [], 2);
  new_centers = centers;
  for k = 1:K
    if any(idx == k), new_centers(k) = mean(data(idx == k)); end
  end
  shift = max(abs(new_centers - centers));
  centers = new_centers;
  if shift < 1e-6, break; end
end
seg = reshape(idx, N, N);
% ---- 数值验证 ----
printf("真值灰度级: 0.20 / 0.70 / 0.85\n");
printf("收敛迭代数 = %d, 最终中心位移 = %.3e\n", it, shift);
printf("学到的类中心: "); printf("%.4f ", centers); printf("\n");
printf("各类像素数: "); printf("%d ", arrayfun(@(k) sum(idx==k), 1:K)); printf("\n");
printf("类内平方和 = %.4f\n", sum((data - centers(idx)).^2));
% ---- 可视化 ----
if SHOW
  figure("name", "12 k-means");
  subplot(1, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 2, 2); imagesc(seg); axis image off; title("聚类标签图");
end""",
            "运行后把 <code>centers</code> 初值改成 <code>[0.1;0.2;0.3]</code>，观察是否收敛到同一解；把 K 改成 4。",
            "迭代通常在十几步内收敛，中心接近三级真实灰度；类内平方和随 K 增大而下降（但 K 过大会把噪声也聚成一类）；初值不同可能得到不同局部最优。"),
  ],
  pitfalls=["对光照不均的图用全局 Otsu：一侧背景被整片误判为目标，需自适应阈值或先做光照校正。",
            "把 K 当成可以随便调大的参数：K 越大类内误差越小，但不代表分割更有意义。",
            "对掩模做双线性缩放：会生成不存在的标签值（第 07 章）。",
            "省略形态学与面积筛选：孤立噪点会让连通域计数完全失真。"],
  exercises=["从类内方差最小出发，推导它与 Otsu 类间方差最大等价。",
             "在 12-kmeans-seg.m 里把特征从灰度改成 <code>[灰度, 行坐标, 列坐标]</code> 的加权组合，观察分割是否开始按空间分区。"],
  further=["<a href='../09-morphology/index.html'>第 9 章 数学形态学（后处理）</a>",
           "<a href='../../part3/16-learning-baselines/index.html'>第 16 章 从手工特征到学习</a>",
           "<a href='../../part4/22-segmentation-networks/index.html'>第 22 章 深度图像分割</a>"]),

C("13", "p2", "part2/13-descriptors", "表示、描述与纹理",
  "分割给出“哪些像素”，描述给出“是什么形状、什么纹理”：把图像压成可比较、可分类的特征向量。",
  hours="3 学时",
  goals=["能计算区域面积、质心与二阶中心矩并验证平移不变性",
         "说清 Hu 不变矩对哪些变换不变、对哪些不变不了",
         "能实现 3×3 LBP 编码并解释其光照不变性",
         "能列出 GLCM 常用统计量及其含义"],
  points=["边界表示与链码", "面积、质心与矩", "Hu 不变矩", "LBP 局部二值模式", "GLCM 与 Haralick 特征", "特征向量与分类接口"],
  sections=[
      ("13.1", "边界与区域描述", """<p>分割后的目标需要变成<strong>紧凑、可比较</strong>的描述。边界表示有链码（8 方向序列，需做起点归一化与旋转归一化）、多边形近似（Douglas-Peucker）、傅里叶描述子（把边界看成复数序列做 FFT，取低频系数即得形状摘要）。区域表示则直接用全部前景像素：</p>
<span class="eq">面积 A = Σ f，　质心 (c̄,r̄) = (Σ c·f / A, Σ r·f / A)，　中心矩 μ_pq = Σ (c−c̄)^p (r−r̄)^q f</span>
<p>由二阶、三阶归一化中心矩可组合出 <strong>7 个 Hu 矩</strong>，对平移、缩放、旋转（以及镜像中的部分）不变，是早期 OCR 与形状检索的经典特征。它们对<strong>遮挡与非刚性形变</strong>不稳定，也不含颜色与纹理信息。</p>"""),
      ("13.2", "纹理：LBP 与 GLCM", """<p><strong>LBP</strong>：对 3×3 邻域，把 8 个邻点灰度与中心比较，≥ 中心记 1，按固定顺序组成 8 bit 编码，再统计整幅图的编码直方图。因为比较的是<strong>相对大小</strong>，对单调光照变化天然鲁棒；“均匀模式”（编码中 0/1 跳变不超过 2 次）可把 256 维压到 59 维，是实用的工程技巧。</p>
<p><strong>GLCM</strong>：统计在给定方向 <code>(dx,dy)</code> 与距离 d 上，灰度对 <code>(i,j)</code> 的共现频次，归一化后导出对比度、相关性、能量（ASM）、熵、同质性等 Haralick 特征。它描述的是<strong>二阶统计</strong>，对纹理周期与方向敏感，但计算量随灰度级数平方增长，通常先量化到 16/32 级。</p>
<div class="card tip"><p style="margin-bottom:0">这两类特征在第 16 章会直接进入 SVM / 视觉词袋；把它们的“人工设计”与 CNN 第一层学出的滤波器对照着看，能最直观地理解“表示学习”到底学走了什么。</p></div>"""),
  ],
  demos=[
      demo("code/13-moments-lbp.m", "区域矩、平移不变性与 LBP 直方图", r"""%% 13-moments-lbp.m | 面积/质心/中心矩 + 3x3 LBP 编码直方图
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; bins = 256;
% ---- 造图：椭圆掩模，并做一个平移副本 ----
[X, Y] = meshgrid(1:N, 1:N);
bw = double(((X-40)/20).^2 + ((Y-45)/30).^2 <= 1);
shifted = zeros(N, N);
shifted(9:N, 13:N) = bw(1:N-8, 1:N-12);
g = 0.30 + 0.40*bw + 0.10*sin(X/3).*sin(Y/4);
% ---- 算法 1：面积 / 质心 / 二阶中心矩 ----
% 面积 / 质心 / 二阶中心矩（匿名函数）
mm = @(a) [sum(a(:)), ...
           sum(X(:).*a(:))/sum(a(:)), sum(Y(:).*a(:))/sum(a(:)), ...
           sum(((X(:)-sum(X(:).*a(:))/sum(a(:))).^2).*a(:))/sum(a(:)), ...
           sum(((Y(:)-sum(Y(:).*a(:))/sum(a(:))).^2).*a(:))/sum(a(:))];
m1 = mm(bw); m2 = mm(shifted);
printf("原图: 面积=%.0f 质心=(%.2f, %.2f) mu20=%.2f mu02=%.2f\n", m1(1),m1(2),m1(3),m1(4),m1(5));
printf("平移: 面积=%.0f 质心=(%.2f, %.2f) mu20=%.2f mu02=%.2f\n", m2(1),m2(2),m2(3),m2(4),m2(5));
printf("质心差 = (%.2f, %.2f)（应等于平移量 12, 8）\n", m2(2)-m1(2), m2(3)-m1(3));
printf("中心矩差 = (%.6f, %.6f)（中心矩对平移不变）\n", m2(4)-m1(4), m2(5)-m1(5));
% ---- 算法 2：3x3 LBP（8 邻域，边界补零）----
p = 1; a = zeros(N+2, N+2); a(2:N+1, 2:N+1) = g;
off = [-1 -1; -1 0; -1 1; 0 1; 1 1; 1 0; 1 -1; 0 -1];
lbp = zeros(N, N);
for r = 1:N
  for c = 1:N
    code = 0;
    for t = 1:8
      code = code + double(a(r+1+off(t,1), c+1+off(t,2)) >= a(r+1, c+1)) * 2^(t-1);
    end
    lbp(r,c) = code;
  end
end
hist_lbp = zeros(bins,1);
for i = 1:numel(lbp), hist_lbp(lbp(i)+1) = hist_lbp(lbp(i)+1) + 1; end
printf("LBP 编码种类 = %d / %d, 最常见编码 = %d（占比 %.3f）\n", ...
       sum(hist_lbp>0), bins, find(hist_lbp==max(hist_lbp),1)-1, max(hist_lbp)/numel(lbp));
printf("编码 0 与 255 的像素数 = %d / %d（平坦区占多数）\n", hist_lbp(1), hist_lbp(256));
% ---- 可视化 ----
if SHOW
  figure("name", "13 描述与纹理");
  subplot(1, 3, 1); imagesc(bw, [0 1]); colormap gray; axis image off; title("椭圆掩模");
  subplot(1, 3, 2); imagesc(lbp); axis image off; title("LBP 编码图");
  subplot(1, 3, 3); bar(hist_lbp); xlim([0 bins]); title("LBP 直方图（特征向量）");
end""",
            "运行后对照两行矩：面积与中心矩应相同，只有质心随平移改变；把平移量改成 <code>[0, 0]</code> 验证两行完全一致。",
            "中心矩对平移不变，质心随平移等量移动；平坦区产生 LBP 编码 0 或 255 并占多数；LBP 直方图可直接作为后续分类器的特征向量。"),
  ],
  pitfalls=["把质心当成不变特征：它随平移改变，只有<strong>中心</strong>矩才平移不变。",
            "LBP 邻域顺序不固定：不同实现若环绕方向不同，直方图会不一致。",
            "GLCM 直接用 256 级灰度：矩阵 65536 项且极稀疏，先量化再统计。",
            "用 Hu 矩处理遮挡目标：少量缺失像素就会显著改变高阶矩。"],
  exercises=["在 13-moments-lbp.m 里对掩模做缩放（用最近邻重采样），观察 <code>mu20</code> 的变化并说明归一化中心矩为什么要除以面积幂次。",
             "统计 LBP 的“均匀模式”数量，说明为什么可以从 256 维降到 59 维。"],
  further=["<a href='../11-features/index.html'>第 11 章 局部特征与描述</a>",
           "<a href='../../part3/16-learning-baselines/index.html'>第 16 章 从手工特征到学习</a>",
           "<a href='../../part3/17-cnn-fundamentals/index.html'>第 17 章 CNN 基础</a>"]),

C("14", "p2", "part2/14-compression", "图像压缩与编码",
  "信息熵给下限，DCT 给能量集中，量化给有损：JPEG 的每一步都对应一个可以算出来的代价。",
  hours="3 学时",
  goals=["能计算图像熵并说明压缩冗余的三种来源",
         "能手写 8×8 DCT 并用矩阵乘法实现分块变换",
         "说清量化表为什么对高频用更大的步长",
         "会用零系数比例、PSNR 与主观块效应共同评价压缩"],
  points=["信息熵与率失真", "无损编码 Huffman / RLE", "DCT 与能量集中", "量化与量化表", "Zigzag 与游程", "JPEG 全流程", "块效应与 JPEG2000"],
  sections=[
      ("14.1", "冗余与信息论下限", """<p>图像可压缩是因为三类冗余：<strong>编码冗余</strong>（灰度值出现概率不均）、<strong>像素间冗余</strong>（相邻像素高度相关）、<strong>心理视觉冗余</strong>（人眼对高频与色度不敏感，可以丢弃）。一阶熵给出无损编码的平均码长下界：</p>
<span class="eq">H = −Σ_k p(k)·log₂ p(k)　（bit / 像素）</span>
<p><strong>率失真</strong>框架把有损压缩写成“在给定码率 R 下最小化失真 D”：量化步长越大，D 越大、R 越小。JPEG 的 quality 参数本质就是在调这张量化表的整体缩放。</p>"""),
      ("14.2", "JPEG 全流程", """<ol><li><strong>色彩空间转换与色度下采样</strong>：RGB → YCbCr，Cb/Cr 常按 4:2:0 降采样（第 08 章）。</li>
<li><strong>分块 8×8 + 电平移位</strong>：每个分量切成 8×8 块。</li>
<li><strong>DCT</strong>：<code>D = T·B·Tᵀ</code>，<code>T</code> 是正交 DCT 矩阵；能量集中到左上角低频，直流系数 <code>D(1,1)</code> 正比于块均值。</li>
<li><strong>量化</strong>：<code>Dq = round(D ./ Q)</code>，Q 在高频取更大值，使多数高频系数变成 0。</li>
<li><strong>Zigzag + 游程 + Huffman</strong>：把二维系数按低频到高频拉成一维，长串 0 用 RLE，最后熵编码。</li></ol>
<p>解码是反量化 + 逆 DCT（<code>B̂ = Tᵀ·Dq·Q·T</code>）+ 拼接。<strong>块效应</strong>来自各块独立量化后边界不连续，<strong>振铃</strong>来自高频被硬性截掉；JPEG2000 用小波做全图多分辨率变换，避免 8×8 分块，低码率下明显更干净但计算更重。</p>"""),
  ],
  demos=[
      demo("code/14-dct-jpeg.m", "手写 8×8 DCT + 量化 + 反变换的完整 JPEG 内核", r"""%% 14-dct-jpeg.m | DCT 矩阵 / 量化表 / 零系数比例 / PSNR
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
end""",
            "运行后把 <code>qscale</code> 改成 0.5 / 8，记录零系数比例与 PSNR；在误差图里找 8×8 的块边界。",
            "<code>T·Tᵀ=I</code> 误差在机器精度内；直流系数占了块能量的绝大部分；qscale 越大零系数越多、PSNR 越低；误差图会显出 8×8 方块网格，即块效应。"),
  ],
  pitfalls=["用 <code>T'·D·T</code> 之外的顺序做逆 DCT：转置位置写反会得到转置的错误重建。",
            "量化后忘记乘回 <code>Q</code> 就做逆变换：重建图几乎全黑。",
            "只报 PSNR 不看误差图：低码率下块效应明显但 PSNR 未必很差。",
            "对色度通道用亮度量化表：人眼敏感度不同，标准里两张表并不相同。"],
  exercises=["推导 <code>D(1,1) = 8·块均值</code>（电平移位后），并用 14-dct-jpeg.m 的数值验证。",
             "把量化表 Q 改成全 1（等价不做量化但保留取整），观察 PSNR 与零系数比例，说明取整本身带来多少误差。"],
  further=["<a href='../../part1/08-color/index.html'>第 8 章 彩色与多通道（YCbCr）</a>",
           "<a href='../../part1/05-frequency-domain/index.html'>第 5 章 频域处理（DCT 与 DFT 的关系）</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 评测指标（PSNR 的局限）</a>"]),

C("15", "p2", "part2/15-classical-pipeline", "传统算法综合实验：颗粒计数流水线",
  "把前 12 章串成一条可交付的流水线：输入一张图，输出一张带面积、圆度与计数的统计表。",
  hours="4 学时",
  goals=["能把一个测量任务拆成预处理、分割、后处理、测量四段",
         "能为每个参数写出“影响哪个指标”的消融表",
         "能组织可复现的实验记录（种子、参数、版本、输出）",
         "能识别流水线的失效模式并给出改进优先级"],
  points=["任务定义与验收指标", "流水线四段结构", "参数表与消融实验", "测量与统计输出", "可复现性记录", "失效模式与改进"],
  sections=[
      ("15.1", "任务定义与验收", """<p>任务：给定一张含若干粘连圆形颗粒、噪声与缓慢亮度漂移的灰度图，输出<strong>颗粒个数、每个颗粒的面积与圆度</strong>。验收指标先写清楚，否则调参没有方向：</p>
<table><thead><tr><th>指标</th><th>定义</th><th>目标</th></tr></thead><tbody>
<tr><td>计数误差</td><td><code>|估计个数 − 真值个数|</code></td><td>0</td></tr>
<tr><td>面积相对误差</td><td><code>|Â−A|/A</code> 的中位数</td><td>&lt; 10%</td></tr>
<tr><td>误检 / 漏检</td><td>非目标被计入 / 目标未被计入</td><td>均为 0</td></tr>
<tr><td>运行时间</td><td>单张图端到端</td><td>记录，用于工程取舍</td></tr>
</tbody></table>"""),
      ("15.2", "四段流水线与参数表", """<ol><li><strong>预处理</strong>：高斯平滑（σ）——去噪但会糊掉小颗粒；必要时用顶帽变换校正亮度漂移。</li>
<li><strong>分割</strong>：Otsu 全局阈值（第 12 章）；若光照仍不均，改自适应阈值。</li>
<li><strong>后处理</strong>：开运算去孤立噪点 → 闭运算填孔 → 连通域标记（第 09 章）→ 面积筛选。</li>
<li><strong>测量</strong>：对每个保留域算面积、质心、等效半径，用 <code>4πA/P²</code> 算圆度（P 为周长，用边界像素数近似）。</li></ol>
<table><thead><tr><th>参数</th><th>主要影响</th><th>调参方向</th></tr></thead><tbody>
<tr><td>σ</td><td>噪声抑制 / 小目标保留</td><td>先看误检数，再看漏检数</td></tr>
<tr><td>结构元素尺寸</td><td>能删掉的最大噪点 / 能填的最大孔</td><td>取略小于最小目标</td></tr>
<tr><td>min_area</td><td>误检</td><td>用真值面积分布的 1/3 作起点</td></tr>
<tr><td>圆度阈值</td><td>粘连团块是否被排除</td><td>与面积筛选联合调</td></tr>
</tbody></table>
<p><strong>消融实验</strong>：每次只改一个参数，记录四项验收指标。一次改三个参数、结果变好却说不清原因，是课程设计里最常见的失分点。</p>"""),
      ("15.3", "报告模板与可复现性", """<p>一份可复现的实验报告至少包含：随机种子、Octave 版本、完整参数表、中间结果图（平滑后 / 掩模 / 标记图）、最终统计表、失败案例分析、以及一条可一键重跑的命令。本书所有 <code>.m</code> 都固定随机种子并把参数集中在脚本开头，就是为了把这件事变成默认行为而不是额外工作。</p>
<div class="card tip"><p style="margin-bottom:0">进入下卷前请记住这条流水线的<strong>形状</strong>：确定性预处理 + 人工先验 + 可解释测量。第 26 章会要求用同一个任务做深度学习基线，并回答一个工程问题——<em>哪些环节值得换成网络，哪些环节换成网络反而更难维护？</em></p></div>"""),
  ],
  demos=[
      demo("code/15-full-pipeline.m", "端到端：造图 → 平滑 → Otsu → 形态学 → 标记 → 统计表", r"""%% 15-full-pipeline.m | 传统算法综合流水线（颗粒计数与测量）
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区（消融实验只改这里）----
N = 160; sigma = 1.2; min_area = 150; noise_sigma = 0.05;
randn("seed", 151); rand("seed", 151);
centers = [40 40; 105 45; 65 105; 120 120];   % 4 个真值颗粒 (列, 行)
R = 16;
% ---- 1) 造图：4 个圆盘 + 亮度漂移 + 噪声 + 孤立亮点 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.18 + 0.10*(X/N);                          % 缓慢亮度漂移
for k = 1:rows(centers)
  f = f + 0.55*double((X-centers(k,1)).^2 + (Y-centers(k,2)).^2 < R^2);
end
f = min(max(f + noise_sigma*randn(N,N), 0), 1);
sp = rand(N,N);
f(sp < 0.001) = 1;                              % 少量孤立亮点
% ---- 2) 平滑：可分离高斯 ----
x = -4:4; w = exp(-x.^2/(2*sigma^2)); w = w/sum(w);
s = conv2(conv2(f, w, "same"), w', "same");
% ---- 3) Otsu 阈值 ----
bins = 64; q = round(s(:)*(bins-1)) + 1;
h = zeros(bins,1);
for i = 1:numel(q), h(q(i)) = h(q(i)) + 1; end
levels = (0:bins-1)'/(bins-1); total = numel(q);
best = -1; bt = 2;
for t = 2:bins
  w0 = sum(h(1:t-1))/total; w1 = 1-w0;
  if w0 == 0 || w1 == 0, continue; end
  m0 = sum(levels(1:t-1).*h(1:t-1))/sum(h(1:t-1));
  m1 = sum(levels(t:bins).*h(t:bins))/sum(h(t:bins));
  v = w0*w1*(m0-m1)^2;
  if v > best, best = v; bt = t; end
end
bw = s > levels(bt);
% ---- 4) 形态学开运算（3x3 腐蚀再膨胀，内联实现）----
p = 1; ae = zeros(N+2, N+2); ae(2:N+1, 2:N+1) = bw;
ero = zeros(N,N);
for r = 1:N
  for c = 1:N, blk = ae(r:r+2, c:c+2); ero(r,c) = double(all(blk(:)==1)); end
end
ad = zeros(N+2, N+2); ad(2:N+1, 2:N+1) = ero;
clean = zeros(N,N);
for r = 1:N
  for c = 1:N, blk = ad(r:r+2, c:c+2); clean(r,c) = double(any(blk(:)==1)); end
end
% ---- 5) 4 连通域标记 ----
labels = zeros(N,N); count = 0; areas = []; cents = [];
for r = 1:N
  for c = 1:N
    if clean(r,c) == 1 && labels(r,c) == 0
      count = count + 1; stack = [r, c]; labels(r,c) = count;
      area = 0; sr = 0; sc = 0;
      while ~isempty(stack)
        cur = stack(end,:); stack(end,:) = [];
        rr = cur(1); cc = cur(2); area = area + 1; sr = sr + rr; sc = sc + cc;
        nb = [rr-1 cc; rr+1 cc; rr cc-1; rr cc+1];
        for t = 1:4
          nr = nb(t,1); nc = nb(t,2);
          if nr>=1 && nr<=N && nc>=1 && nc<=N && clean(nr,nc)==1 && labels(nr,nc)==0
            labels(nr,nc) = count; stack = [stack; nr, nc];
          end
        end
      end
      areas(count) = area; cents(count,:) = [sc/area, sr/area];
    end
  end
end
keep = find(areas >= min_area);
% ---- 6) 统计输出 ----
printf("==== 颗粒计数流水线报告 ====\n");
printf("参数: sigma=%.2f min_area=%d noise=%.3f | Otsu 阈值=%.4f\n", sigma, min_area, noise_sigma, levels(bt));
printf("真值颗粒数 = %d, 阈值后连通域 = %d, 面积筛后 = %d\n", rows(centers), count, numel(keep));
printf("理论单颗粒面积 = %.0f (pi*R^2, R=%d)\n", pi*R^2, R);
printf("保留域面积: "); printf("%d ", areas(keep)); printf("\n");
printf("保留域质心 (列,行):\n"); printf("  (%.1f, %.1f)\n", cents(keep,1), cents(keep,2));
printf("保留域平均面积 = %.1f, 面积标准差 = %.1f\n", mean(areas(keep)), std(areas(keep)));
printf("计数误差 = %d\n", abs(numel(keep) - rows(centers)));
% ---- 可视化 ----
if SHOW
  figure("name", "15 综合流水线");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("输入图");
  subplot(2, 2, 2); imagesc(bw, [0 1]); axis image off; title("Otsu 掩模");
  subplot(2, 2, 3); imagesc(clean, [0 1]); axis image off; title("开运算后");
  subplot(2, 2, 4); imagesc(labels); axis image off; title("连通域标记");
end""",
            "运行后按 15.2 的参数表做消融：每次只改 <code>sigma</code>、<code>min_area</code> 或 <code>noise_sigma</code>，记录计数误差与面积。",
            "合成数据下真值 4 个颗粒；Otsu 阈值应落在 0.3～0.5；开运算去掉孤立亮点；面积筛选后计数误差为 0，各域面积接近 <code>π·16² ≈ 804</code>（受平滑与开运算略有缩小）。"),
  ],
  pitfalls=["一次改多个参数：结果变好但无法归因，消融实验失去意义。",
            "用肉眼判断“分割干净”就交付：必须输出计数、面积、误检漏检的表格。",
            "不固定随机种子：加噪实验结果每次都不同，无法对比。",
            "把粘连团块当作一个大目标直接计数：需要先做距离变换 + 分水岭分离（第 09、12 章）。"],
  exercises=["把两个颗粒中心移近到相距 20 像素制造粘连，观察计数变化，并设计基于距离变换的分离方案。",
             "完成 15.2 的三组消融实验，填写“参数 → 计数误差 / 面积误差 / 误检 / 漏检”四列表。"],
  further=["<a href='../09-morphology/index.html'>第 9 章 数学形态学</a>",
           "<a href='../12-segmentation/index.html'>第 12 章 图像分割</a>",
           "<a href='../../part4/26-projects/index.html'>第 26 章 工程落地与综合项目（同任务的深度基线）</a>"]),

]
