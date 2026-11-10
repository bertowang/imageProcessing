#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一篇 05-08 + 第二篇 09：章节正文与 Octave 实例。

代码契约见 chapters_00_04.py 的模块说明：零依赖、自包含、参数集中、数值可核对。
"""
from book_schema import C, demo

CH = [

C("05", "p1", "part1/05-frequency-domain", "频域处理",
  "把图像看成不同频率的正弦叠加：一次 FFT，就能把卷积变成乘法、把模糊变成衰减、把结构存进相位。",
  hours="4 学时",
  goals=["能写出二维 DFT 定义并解释 fftshift 的作用",
         "能按四步流程实现频域低通/高通滤波",
         "说清理想、高斯、巴特沃斯三类滤波器的振铃差异",
         "能用相位交换实验解释为什么相位承载结构信息"],
  points=["二维 DFT 与 FFT", "fftshift 与频率坐标", "幅度谱与相位谱", "频域滤波四步法", "理想/高斯/巴特沃斯", "陷波与周期边界", "相位交换实验"],
  sections=[
      ("5.1", "二维 DFT 与频率坐标", """<p>二维离散傅里叶变换把 <code>M×N</code> 图像分解成不同方向、不同频率的复正弦：</p>
<span class="eq">F(u,v) = Σᵣ Σ꜀ f(r,c)·exp(−j2π(ur/M + vc/N))</span>
<p><code>fft2(f)</code> 的输出把<strong>零频（直流）放在左上角</strong>；<code>fftshift</code> 把它搬到中心，低频靠中心、高频靠外圈，这样画出来的频谱才符合直觉。频谱幅度动态范围极大，显示时统一用 <code>log(1+abs(F))</code> 压缩。</p>
<table><thead><tr><th>频域现象</th><th>空域对应</th></tr></thead><tbody>
<tr><td>中心亮点</td><td>整体平均亮度（直流分量）</td></tr>
<tr><td>过中心的一条亮线</td><td>图中垂直于该方向的条纹/边缘</td></tr>
<tr><td>能量集中在外圈</td><td>噪声、细节、锐利边缘</td></tr>
<tr><td>周期性亮点</td><td>周期性纹理，可用陷波滤波去除</td></tr>
</tbody></table>"""),
      ("5.2", "频域滤波四步法", """<ol><li><code>F = fft2(f)</code>（必要时先 <code>fftshift</code> 构造以中心为原点的 H，再 <code>ifftshift</code> 回去）。</li>
<li>构造与图像同尺寸的传递函数 <code>H(u,v)</code>，令 <code>G = H .* F</code>。</li>
<li><code>g = real(ifft2(G))</code>，取实部是因为数值误差会带来可忽略的虚部。</li>
<li>裁剪到 <code>[0,1]</code> 并评价。</li></ol>
<p>三类低通滤波器（<code>D(u,v)</code> 是到频率中心的距离，<code>D₀</code> 是截止频率）：</p>
<table><thead><tr><th>类型</th><th>H(u,v)</th><th>特点</th></tr></thead><tbody>
<tr><td>理想</td><td><code>D ≤ D₀ ? 1 : 0</code></td><td>截止最陡，但空域冲激是 sinc，出现明显<strong>振铃</strong></td></tr>
<tr><td>高斯</td><td><code>exp(−D²/2D₀²)</code></td><td>傅里叶变换仍是高斯，<strong>无振铃</strong>，过渡最缓</td></tr>
<tr><td>巴特沃斯</td><td><code>1/(1+(D/D₀)^(2n))</code></td><td>阶数 n 在陡峭度与振铃之间折中</td></tr>
</tbody></table>
<p>高通可取 <code>1 − H_low</code>；带阻/陷波用于去除固定频率的周期干扰。<strong>注意 DFT 隐含周期假设</strong>，等价于 circular 边界填充，图像左右/上下亮度差大时会在边界产生条纹，可先做镜像填充或加窗。</p>"""),
      ("5.3", "相位比幅度更重要", """<p>把两幅图 <code>f₁</code>、<code>f₂</code> 的 FFT 拆成幅度与相位，交换相位后反变换：重建结果看起来像<strong>提供相位的那张图</strong>，而不是提供幅度的那张。原因是相位编码了各频率分量的<strong>相对位置</strong>，边缘与结构正是这些分量对齐的结果；幅度只决定每个分量有多强。</p>
<div class="card tip"><p style="margin-bottom:0">这解释了为什么<strong>直方图相同 ≠ 图像相同</strong>：直方图只保留一阶幅度统计，完全丢弃位置信息。第 02 章埋的伏笔在这里闭合，也预告了下卷用感知损失/特征损失替代逐像素 MSE 的动机。</p></div>"""),
  ],
  demos=[
      demo("code/05-fft-lowpass.m", "二维 FFT、高斯低通与能量保留比例", r"""%% 05-fft-lowpass.m | fft2 / fftshift / 高斯低通 / 能量统计
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
end""",
            "运行后把 <code>D0</code> 改成 5 / 40，观察“保留能量比例”与标准差；注意均值几乎不变。",
            "<code>F(1,1)</code> 等于图像均值乘以像素数，虚部为 0；直流能量占绝大部分；低通前后均值相同、标准差下降；D₀ 越小保留能量越少、图像越糊。"),
      demo("code/05-phase-swap.m", "相位交换：结构由相位决定", r"""%% 05-phase-swap.m | 交换两幅图的 FFT 相位，观察结构跟谁走
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
end""",
            "运行脚本，看四个相关系数；再在图形窗口里确认重组图的结构跟相位走。",
            "两图一阶统计几乎相同；<code>重组图1</code> 与 f2 的相关显著高于 f1，<code>重组图2</code> 反之。相位决定结构，幅度只决定对比度分布。"),
  ],
  pitfalls=["忘了 <code>fftshift</code> / <code>ifftshift</code> 配对，导致滤波器中心错位、结果整体偏移。",
            "直接显示 <code>abs(F)</code>：动态范围太大，除了直流点什么都看不见，要用 <code>log(1+abs(F))</code>。",
            "用理想低通追求“锐利截止”：空域会出现明显振铃，工程上优先用高斯或巴特沃斯。",
            "忘记 DFT 的周期假设：左右边界亮度差大时出现十字条纹。"],
  exercises=["把 05-fft-lowpass.m 的高斯 H 换成理想低通 <code>D &lt;= D0</code>，画出结果并解释边缘振铃的来源。",
             "推导：为什么低通滤波前后图像均值不变？用 <code>F(1,1)</code> 与 <code>H(1,1)</code> 的关系说明。"],
  further=["<a href='../04-spatial-filter/index.html'>第 4 章 空间域滤波（空域对照）</a>",
           "<a href='../06-restoration/index.html'>第 6 章 图像复原与去噪</a>",
           "<a href='../../part2/14-compression/index.html'>第 14 章 图像压缩（DCT 是近亲）</a>"]),

C("06", "p1", "part1/06-restoration", "图像复原与去噪",
  "先把退化写成公式，再谈复原：逆滤波为什么会炸、维纳滤波加的那一项到底在压制什么。",
  hours="4 学时",
  goals=["能写出线性退化模型并指出病态性的来源",
         "能区分四类常见噪声及其对应滤波器",
         "会推导维纳滤波公式并解释参数 K 的作用",
         "能用 PSNR 与视觉结果共同判断复原是否真的变好"],
  points=["退化模型 g=h*f+n", "噪声模型与估计", "逆滤波的病态性", "维纳滤波推导", "参数 K 的折中", "复原评价与伪影"],
  sections=[
      ("6.1", "退化模型与噪声", """<span class="eq">g(r,c) = (h ∗ f)(r,c) + n(r,c)　⇔　G = H·F + N</span>
<p><code>h</code> 是 PSF（运动模糊是一条线、失焦是一个圆盘、大气湍流近似高斯）；<code>n</code> 是加性噪声。复原的目标是<strong>在只知道 g 与 h 的情况下估计 f</strong>，这是典型的反问题。</p>
<table><thead><tr><th>噪声</th><th>模型</th><th>典型来源 / 对策</th></tr></thead><tbody>
<tr><td>高斯</td><td>加性 N(0,σ²)</td><td>传感器读出热噪声；均值/维纳/非局部均值</td></tr>
<tr><td>椒盐</td><td>随机像素置 0/1</td><td>传输误码、坏点；中值滤波</td></tr>
<tr><td>泊松</td><td>方差随亮度增大</td><td>光子散粒噪声；方差稳定化变换（Anscombe）</td></tr>
<tr><td>周期</td><td>固定频率正弦干扰</td><td>电源/扫描条纹；频域陷波</td></tr>
</tbody></table>"""),
      ("6.2", "逆滤波与病态性", """<p>最朴素的想法是 <code>F̂ = G / H</code>。问题在于 <code>H</code> 在高频往往<strong>接近 0</strong>（PSF 是低通），而噪声 <code>N</code> 在高频并不小，于是 <code>N/H</code> 被急剧放大，结果被噪声淹没。这就是<strong>病态反问题</strong>：解不连续依赖输入，微小扰动导致巨大偏差。</p>
<div class="card warn"><p style="margin-bottom:0">判断标准：画出 <code>|H|</code> 的衰减曲线。凡是 <code>|H|</code> 低于噪声水平的频率，都不该做除法。第 06 章实验会让你亲手把 <code>H</code> 加一点保护再看差异。</p></div>"""),
      ("6.3", "维纳滤波", """<p>把“误差的均方期望最小”作为准则，假设图像与噪声是互不相关的平稳随机过程，可得频域解：</p>
<span class="eq">F̂(u,v) = [ H*(u,v) / ( |H(u,v)|² + Sₙ/S_f ) ] · G(u,v) = [ H* / (|H|² + K) ] · G</span>
<ul><li><code>K = Sₙ/S_f</code> 是<strong>噪信功率比</strong>；<code>K = 0</code> 退化为逆滤波，<code>K → ∞</code> 退化为全零（完全不信数据）。</li>
<li>在 <code>|H|² ≫ K</code> 的频率上近似逆滤波，在 <code>|H|² ≪ K</code> 的频率上自动衰减，从而抑制噪声放大。</li>
<li>工程上 <code>K</code> 常当作<strong>可调标量</strong>：先扫几个数量级，用 PSNR 或下游任务指标选，而不是真的去估计功率谱。</li></ul>
<p>维纳滤波是“最优线性复原”，但它仍假设平稳性与已知 PSF。真实场景（未知模糊核、空间变化噪声）需要盲去卷积或数据驱动的先验——这正是<a href="../../part4/23-deep-restoration/index.html">第 23 章</a>深度复原网络要解决的问题。</p>"""),
  ],
  demos=[
      demo("code/06-wiener.m", "模糊 + 噪声：逆滤波与维纳滤波的定量对照", r"""%% 06-wiener.m | 退化模型 / 逆滤波 / 维纳滤波 / PSNR 对照
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
end""",
            "运行后按提示把 <code>K</code> 改成 0 / 0.001 / 0.2 各跑一次，记录 PSNR 曲线；再把 <code>noise_sigma</code> 提高 10 倍。",
            "PSF 和为 1；<code>|H|</code> 最小值接近 0；逆滤波 PSNR 往往比退化图还差且标准差暴涨；维纳在合适 K 下明显改善；K 过大则过度平滑、PSNR 回落。"),
  ],
  pitfalls=["用 <code>G./H</code> 且不检查 <code>|H|</code>：高频除零导致数值溢出或满屏噪声。",
            "把 <code>K</code> 当成固定常数：它应随噪声水平变化，不同图要重新扫参。",
            "用 PSNR 单独判定成功：过度平滑常给出不错的 PSNR，却丢失全部纹理。",
            "忽略边界：频域复原隐含周期卷积，边界会出现来自对侧的伪影。"],
  exercises=["从最小化 <code>E[(f−f̂)²]</code> 出发推导维纳滤波公式，说明 <code>K=Sₙ/S_f</code> 的来历。",
             "在 06-wiener.m 里把 PSF 改成水平运动模糊（一行 9 点均值），预测复原难度并验证。"],
  further=["<a href='../05-frequency-domain/index.html'>第 5 章 频域处理</a>",
           "<a href='../04-spatial-filter/index.html'>第 4 章 空间域滤波（非局部均值）</a>",
           "<a href='../../part4/23-deep-restoration/index.html'>第 23 章 深度复原与超分辨率</a>"]),

C("07", "p1", "part1/07-geometry-registration", "几何变换与图像配准",
  "齐次坐标把平移旋转缩放统一成矩阵乘法；反向映射加插值，才不会在新图上留下空洞。",
  hours="3 学时",
  goals=["能用齐次坐标写出仿射与透视变换",
         "说清前向映射为什么会留洞、反向映射为什么不会",
         "能比较最近邻与双线性插值的失真与计算量",
         "描述一个完整配准流程及其失效模式"],
  points=["齐次坐标", "仿射与透视变换", "反向映射", "最近邻/双线性插值", "配准流程与相似度", "RANSAC 与外点"],
  sections=[
      ("7.1", "变换矩阵与齐次坐标", """<p>用 2×2 矩阵无法表示平移。把点写成 <code>[x,y,1]ᵀ</code>，平移就可以和其他变换一样用矩阵乘法：</p>
<table><thead><tr><th>变换</th><th>矩阵（3×3）</th><th>自由度</th></tr></thead><tbody>
<tr><td>平移</td><td><code>[1 0 tₓ; 0 1 t_y; 0 0 1]</code></td><td>2</td></tr>
<tr><td>旋转 + 缩放 + 剪切</td><td><code>[a b 0; c d 0; 0 0 1]</code></td><td>4～6</td></tr>
<tr><td>仿射</td><td>线性部分任意 2×2 + 平移</td><td>6</td></tr>
<tr><td>透视（单应）</td><td>最后一行含 <code>[p₁ p₂ 1]</code>，再做归一化除法</td><td>8</td></tr>
</tbody></table>
<p>仿射保持平行性，透视不保持（所以文档矫正、车道线要用单应）。估计单应最少需要<strong>4 组不共线的点对应</strong>；多于 4 组时用最小二乘，并配合 RANSAC 剔除错误匹配。</p>"""),
      ("7.2", "反向映射与插值", """<p>把输入像素逐个搬到输出位置（前向映射）会出现两个问题：旋转后落点不是整数、且输出图上会留下空洞。正确做法是<strong>反向映射</strong>：遍历每个输出像素，用逆变换求它在输入图中的坐标，再插值取灰度。</p>
<span class="eq">[x_src, y_src, 1]ᵀ = T⁻¹ · [x_dst, y_dst, 1]ᵀ</span>
<table><thead><tr><th>插值</th><th>做法</th><th>效果 / 代价</th></tr></thead><tbody>
<tr><td>最近邻</td><td>取整到最近像素</td><td>最快，保留原始灰度值，但有锯齿；适合标签图/掩模</td></tr>
<tr><td>双线性</td><td>周围 4 点的距离加权</td><td>平滑且常用，但会轻微模糊；<strong>不能用于整数标签图</strong></td></tr>
<tr><td>双三次</td><td>周围 16 点的三次卷积</td><td>更锐利，可能出现过冲（灰度越界）</td></tr>
</tbody></table>
<p>再次提醒坐标约定：矩阵索引是 <code>(r,c)</code>，几何坐标是 <code>(x,y)=(c,r)</code>。写 <code>interp2(f, x_src, y_src)</code> 时第一个查询坐标对应<strong>列</strong>。</p>"""),
      ("7.3", "配准流程", """<ol><li><strong>特征提取</strong>：角点/局部描述子（第 11 章）或直接利用像素强度。</li>
<li><strong>匹配与剔错</strong>：最近邻距离比、RANSAC 求一致的最大内点集。</li>
<li><strong>估计变换</strong>：用内点做最小二乘；医学/遥感还会用互信息作为相似度。</li>
<li><strong>重采样</strong>：反向映射 + 插值生成配准图。</li>
<li><strong>验证</strong>：叠加棋盘图、差分图、检查特征点残差。</li></ol>
<p>失效模式主要是<strong>大位移、非刚性形变、跨模态（如 CT 与 MRI）、重复纹理</strong>。非刚性配准需要形变场与正则项，已超出线性变换范畴，下卷的光流/形变网络是常见解法。</p>"""),
  ],
  demos=[
      demo("code/07-affine-interp.m", "旋转的反向映射：最近邻 vs 双线性", r"""%% 07-affine-interp.m | 齐次坐标 / 反向映射 / 两种插值对比
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 128; theta = pi/6;         % 旋转 30 度
% ---- 造图：棋盘 + 细线（便于观察锯齿）----
[X, Y] = meshgrid(1:N, 1:N);
f = double(mod(floor(X/16) + floor(Y/16), 2) == 0);
f = 0.15 + 0.7*f;
f(abs(Y - N/2) < 2) = 0.9;
% ---- 算法：输出坐标 -> 逆旋转 -> 输入坐标 ----
R = [cos(theta) -sin(theta); sin(theta) cos(theta)];
cx = N/2; cy = N/2;
x = X(:)' - cx; y = Y(:)' - cy;
src = R' * [x; y];                       % 逆变换（旋转矩阵的逆 = 转置）
sx = reshape(src(1,:), N, N) + cx;
sy = reshape(src(2,:), N, N) + cy;
inside = sx >= 1 & sx <= N & sy >= 1 & sy <= N;
g_near = interp2(f, sx, sy, "nearest", 0);
g_lin  = interp2(f, sx, sy, "linear", 0);
% ---- 数值验证 ----
printf("旋转角 = %.1f 度, 落在图内的输出像素比例 = %.4f\n", theta*180/pi, mean(inside(:)));
printf("原图唯一灰度级数 = %d, 双线性后 = %d（插值产生了中间灰度）\n", ...
       numel(unique(f(:))), numel(unique(round(g_lin(:)*1000))));
printf("最近邻 / 双线性 的均值 = %.4f / %.4f\n", mean(g_near(:)), mean(g_lin(:)));
printf("细线处灰度: 最近邻 %.3f ~ 双线性 %.3f\n", ...
       max(g_near(abs(Y-N/2)<3)), max(g_lin(abs(Y-N/2)<3)));
% ---- 可视化 ----
if SHOW
  figure("name", "07 反向映射");
  subplot(1, 3, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(1, 3, 2); imagesc(g_near, [0 1]); axis image off; title("最近邻（锯齿）");
  subplot(1, 3, 3); imagesc(g_lin, [0 1]); axis image off; title("双线性（平滑）");
end""",
            "运行后把 <code>theta</code> 改成 0 验证输出与原图一致；改成 45° 观察四角黑色区域。",
            "30° 旋转后约 70%～80% 的输出像素能找到输入；最近邻只产生原图已有的灰度级，双线性产生大量中间灰度；<code>interp2</code> 的第一个查询坐标是列（x），顺序写反会得到转置的错误结果。"),
  ],
  pitfalls=["把 (x,y) 写成 (r,c)：<code>interp2</code> 会给出镜像/转置的结果。",
            "对整数标签图（分割掩模）用双线性插值：会凭空造出不存在的类别编号。",
            "用前向映射画旋转：输出图上出现规律的空洞。",
            "透视变换忘记除以第三维齐次坐标，结果完全不对。"],
  exercises=["推导旋转矩阵可逆且 <code>R⁻¹=Rᵀ</code>，说明为什么反向映射可以直接用转置。",
             "把 <code>interp2</code> 的 <code>sx</code>/<code>sy</code> 交换，记录图像变化，并解释原因。"],
  further=["<a href='../../part2/11-features/index.html'>第 11 章 局部特征（配准的输入）</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 数据集与评测（几何增强）</a>",
           "<a href='../08-color/index.html'>第 8 章 彩色与多通道处理</a>"]),

C("08", "p1", "part1/08-color", "彩色与多通道处理",
  "RGB 只是坐标之一：换到 HSV/Lab 之后，很多“难做的阈值”会变成一次简单的范围判断。",
  hours="3 学时",
  goals=["能说清 RGB、HSV、Lab、YCbCr 各自适合的场合",
         "会写灰度化与灰度世界白平衡并判断其假设",
         "能实现基于色相/饱和度的颜色分割",
         "理解色彩恒常性为什么是欠定问题"],
  points=["RGB 与加色模型", "HSV / Lab / YCbCr", "灰度化与亮度权重", "颜色分割与阈值", "灰度世界白平衡", "色彩恒常性"],
  sections=[
      ("8.1", "常用色彩空间", """<table><thead><tr><th>空间</th><th>分量</th><th>适合做什么</th></tr></thead><tbody>
<tr><td>RGB</td><td>红绿蓝</td><td>采集、显示、存储；三通道高度相关，直接做阈值容易受光照影响</td></tr>
<tr><td>HSV / HSL</td><td>色相、饱和度、明度</td><td>按“颜色”分割：色相基本不受亮度变化影响</td></tr>
<tr><td>Lab</td><td>亮度 L + 色度 a/b</td><td>感知近似均匀，适合色差度量与聚类</td></tr>
<tr><td>YCbCr / YUV</td><td>亮度 Y + 色度</td><td>视频与 JPEG：可对色度下采样而几乎不损视觉</td></tr>
</tbody></table>
<p>灰度化不是简单平均。感知亮度常用 <code>Y = 0.299R + 0.587G + 0.114B</code>（人眼对绿最敏感）；第 14 章 JPEG 用的正是这类亮度/色度分离。</p>"""),
      ("8.2", "按颜色分割", """<p>在 RGB 里判断“红色”需要同时约束 R 大、G 小、B 小，且阈值随亮度漂移；换到 HSV 后只需 <code>H</code> 落在红色区间（注意色相是<strong>环形量</strong>，红色跨 0 度）、<code>S</code> 大于阈值即可。这也是为什么颜色分割几乎总先做色彩空间转换。</p>
<div class="card note"><p style="margin-bottom:0">工程细节：色相用 <code>mod</code> 处理环绕；低饱和度像素的色相不稳定（近灰点），必须先用 <code>S</code> 掩掉；分割后接第 09 章的形态学开闭运算去掉孤立噪点。</p></div>"""),
      ("8.3", "白平衡与色彩恒常性", """<p>传感器记录的是<strong>光源光谱 × 物体反射率</strong>，两者混在一起。色彩恒常性要让估计不受光源影响，本质是欠定问题，必须加假设。三个经典假设：</p>
<ul><li><strong>灰度世界</strong>：整幅图的平均反射是无彩色，于是把三通道均值缩放到相等（或缩放到同一目标灰度）。</li>
<li><strong>完美反射</strong>：图中存在白色（各通道最大值的点即光源色）。</li>
<li><strong>von Kries / 对角模型</strong>：光源变化可近似为三通道各自乘一个增益。</li></ul>
<p>灰度世界在<strong>大面积单色主体</strong>（草地、蓝天）上会明显偏色，这是假设被破坏的典型例子；下卷的自动白平衡用数据学习来替代手工假设，但训练数据偏差会带来新的肤色偏色问题。</p>"""),
  ],
  demos=[
      demo("code/08-color-space.m", "RGB → 亮度 / HSV、颜色分割与灰度世界白平衡", r"""%% 08-color-space.m | 色彩空间转换 / 颜色分割 / 灰度世界白平衡
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
end""",
            "运行后把 <code>target</code> 改成 0.4，观察增益与结果亮度；把色相阈值放宽看掩模变化。",
            "H/S/V 都落在 [0,1]；偏色图三通道均值不等，白平衡后被拉到 target 附近；红色掩模命中数接近红块面积 <code>36×36=1296</code>（受光源与阈值影响略有偏差）。"),
  ],
  pitfalls=["把色相当线性量求平均：0 与 1 是相邻色，均值要用圆周统计或直接分区间。",
            "低饱和像素也参与色相判断：近灰点的 H 极不稳定，会制造大量噪点。",
            "灰度世界用在大面积单色场景：会把草地整体拉成灰色，产生严重偏色。",
            "RGB 转灰度直接取三通道平均：与人眼感知亮度不符，边缘检测结果会变。"],
  exercises=["推导 <code>Y = 0.299R+0.587G+0.114B</code> 的权重和为什么为 1，并说明换成平均会带来什么差异。",
             "在 08-color-space.m 里加入饱和度阈值扫描，画出“掩模命中数 vs S 阈值”的曲线。"],
  further=["<a href='../../part2/14-compression/index.html'>第 14 章 图像压缩（色度下采样）</a>",
           "<a href='../../part2/12-segmentation/index.html'>第 12 章 图像分割（颜色聚类）</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 数据增强中的颜色抖动</a>"]),

C("09", "p2", "part2/09-morphology", "数学形态学",
  "用集合的视角处理形状：腐蚀、膨胀、开、闭四个动作，就能完成去噪、填洞、分离粘连目标。",
  hours="3 学时",
  goals=["能用集合语言定义腐蚀与膨胀并说明对偶性",
         "能预测开/闭运算分别删除哪类结构",
         "会手写一个简单的连通域标记",
         "理解距离变换 + 分水岭分离粘连目标的流程"],
  points=["结构元素", "腐蚀与膨胀", "对偶性", "开运算与闭运算", "连通域标记", "距离变换与分水岭"],
  sections=[
      ("9.1", "腐蚀、膨胀与对偶性", """<p>把二值图看成前景像素的集合 <code>A</code>，结构元素 <code>B</code> 是一个小形状（常用 3×3 方形、圆盘、十字）。</p>
<span class="eq">腐蚀 A ⊖ B = { z | (B)_z ⊆ A }　　膨胀 A ⊕ B = { z | (B̂)_z ∩ A ≠ ∅ }</span>
<ul><li><strong>腐蚀</strong>：只有 B 完全落在前景内才保留中心 → 前景收缩，去掉小亮点与细连接。</li>
<li><strong>膨胀</strong>：B 与前景有交集就保留 → 前景扩张，填补小孔与断裂。</li>
<li><strong>对偶性</strong>：<code>(A ⊖ B)ᶜ = Aᶜ ⊕ B̂</code>，对背景膨胀等价于对前景腐蚀，实现时可互相复用。</li></ul>
<p>灰度形态学把 min/max 代入即可：腐蚀取邻域最小值、膨胀取邻域最大值，这正是第 04 章排序统计滤波的特例。</p>"""),
      ("9.2", "开、闭与形态学滤波", """<table><thead><tr><th>复合运算</th><th>定义</th><th>删掉什么</th><th>保留什么</th></tr></thead><tbody>
<tr><td>开运算</td><td><code>(A ⊖ B) ⊕ B</code></td><td>比 B 小的亮细节、细毛刺、孤立点</td><td>主体形状与尺寸基本不变</td></tr>
<tr><td>闭运算</td><td><code>(A ⊕ B) ⊖ B</code></td><td>比 B 小的暗孔、细裂缝</td><td>主体形状与尺寸基本不变</td></tr>
<tr><td>形态学梯度</td><td><code>膨胀 − 腐蚀</code></td><td>—</td><td>目标边界</td></tr>
<tr><td>顶帽变换</td><td><code>A − 开(A)</code></td><td>—</td><td>比 B 小的亮细节，用于光照校正</td></tr>
</tbody></table>
<p>开闭都是<strong>幂等</strong>的（做一次和做两次结果相同），这点与卷积滤波完全不同；结构元素的尺寸直接决定“多大的结构算细节”，是唯一需要调的参数。</p>"""),
      ("9.3", "连通域、距离变换与分水岭", """<p><strong>连通域标记</strong>把二值图分成若干独立目标，是计数、面积筛选、包围盒的前提。4 连通与 8 连通要事先约定，斜角接触的两个块在 4 连通下是两个目标、在 8 连通下是一个。</p>
<p><strong>距离变换</strong>给每个前景像素标出到最近背景的距离；距离图的局部极大值天然是目标的“中心种子”。<strong>分水岭</strong>把灰度图看作地形、从种子开始淹没，相遇处形成分水岭线，因此特别适合分离<strong>粘连的圆形目标</strong>（细胞、颗粒）。直接对原图做分水岭几乎必然过分割，标准流程是：平滑 → 距离变换 → 取局部极大作标记 → 带标记的分水岭。</p>"""),
  ],
  demos=[
      demo("code/09-morphology.m", "手写腐蚀/膨胀/开/闭与面积统计", r"""%% 09-morphology.m | 二值形态学四则运算（3x3 结构元素）
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; win = 3;
% ---- 造图：两个方块 + 孤立亮点 + 内部小孔 + 细毛刺 ----
[X, Y] = meshgrid(1:N, 1:N);
bw = double((X>15 & X<45 & Y>15 & Y<45) | (X>55 & X<85 & Y>50 & Y<80));
bw(70, 20) = 1;                       % 孤立亮点
bw(28:31, 28:31) = 0;                % 内部小孔
bw(45:52, 30) = 1;                   % 细毛刺
% ---- 工具：带零填充的局部窗口 ----
p = (win-1)/2;
a = zeros(N + 2*p, N + 2*p);
a(p+1:p+N, p+1:p+N) = bw;
% ---- 算法：腐蚀 = 窗口全 1；膨胀 = 窗口含 1 ----
ero = zeros(N, N); dil = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = a(r:r+win-1, c:c+win-1);
    ero(r,c) = double(all(blk(:) == 1));
    dil(r,c) = double(any(blk(:) == 1));
  end
end
% ---- 开 = 先腐蚀后膨胀；闭 = 先膨胀后腐蚀（同样用 win 邻域）----
ae = zeros(N + 2*p, N + 2*p); ae(p+1:p+N, p+1:p+N) = ero;
opened = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = ae(r:r+win-1, c:c+win-1);
    opened(r,c) = double(any(blk(:) == 1));
  end
end
ad = zeros(N + 2*p, N + 2*p); ad(p+1:p+N, p+1:p+N) = dil;
closed = zeros(N, N);
for r = 1:N
  for c = 1:N
    blk = ad(r:r+win-1, c:c+win-1);
    closed(r,c) = double(all(blk(:) == 1));
  end
end
% ---- 数值验证 ----
printf("原图前景 = %d, 腐蚀 = %d, 膨胀 = %d\n", sum(bw(:)), sum(ero(:)), sum(dil(:)));
printf("开运算 = %d（孤立点与毛刺被删：%d 个像素）\n", sum(opened(:)), sum(bw(:))-sum(opened(:)));
printf("闭运算 = %d（内部小孔被填：%d 个像素）\n", sum(closed(:)), sum(closed(:))-sum(bw(:)));
printf("孤立亮点 (70,20): 原 %d -> 开运算后 %d\n", bw(70,20), opened(70,20));
printf("小孔中心 (29,29): 原 %d -> 闭运算后 %d\n", bw(29,29), closed(29,29));
% ---- 可视化 ----
if SHOW
  figure("name", "09 形态学");
  subplot(2, 2, 1); imagesc(bw, [0 1]); colormap gray; axis image off; title("原二值图");
  subplot(2, 2, 2); imagesc(ero, [0 1]); axis image off; title("腐蚀");
  subplot(2, 2, 3); imagesc(opened, [0 1]); axis image off; title("开运算");
  subplot(2, 2, 4); imagesc(closed, [0 1]); axis image off; title("闭运算");
end""",
            "运行后把 <code>win</code> 改成 5（需同步改 <code>morph_</code> 的窗口）或把毛刺加粗，观察开运算是否还能删除。",
            "腐蚀面积减少、膨胀面积增加；开运算去掉孤立亮点与细毛刺（前景减少），闭运算填上内部小孔（前景增加）；结构元素越大，被当作细节删掉的结构越大。"),
      demo("code/09-label-regions.m", "手写 4 连通域标记与面积筛选", r"""%% 09-label-regions.m | 4 连通 flood fill 标记 + 面积筛选
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 96; min_area = 100;
% ---- 造图：3 个矩形目标 + 2 个噪点 ----
[X, Y] = meshgrid(1:N, 1:N);
bw = double((X>8 & X<30 & Y>8 & Y<32) | (X>40 & X<66 & Y>40 & Y<70) ...
          | (X>72 & X<90 & Y>10 & Y<28));
bw(85, 85) = 1; bw(5, 90) = 1;
% ---- 算法：逐像素扫描，遇未标记前景就做一次 flood fill ----
labels = zeros(N, N); count = 0; areas = [];
for r = 1:N
  for c = 1:N
    if bw(r,c) == 1 && labels(r,c) == 0
      count = count + 1;
      stack = [r, c]; labels(r,c) = count; area = 0;
      while ~isempty(stack)
        cur = stack(end, :); stack(end, :) = [];
        rr = cur(1); cc = cur(2); area = area + 1;
        nb = [rr-1 cc; rr+1 cc; rr cc-1; rr cc+1];
        for t = 1:4
          nr = nb(t,1); nc = nb(t,2);
          if nr >= 1 && nr <= N && nc >= 1 && nc <= N
            if bw(nr,nc) == 1 && labels(nr,nc) == 0
              labels(nr,nc) = count;
              stack = [stack; nr, nc];
            end
          end
        end
      end
      areas(count) = area;
    end
  end
end
big = zeros(N, N);
for k = 1:count
  if areas(k) >= min_area, big(labels == k) = 1; end
end
% ---- 数值验证 ----
printf("连通域总数 = %d（3 个目标 + 2 个噪点）\n", count);
printf("各连通域面积: "); printf("%d ", areas); printf("\n");
printf("面积 >= %d 的域数 = %d, 筛后前景 = %d\n", min_area, sum(areas >= min_area), sum(big(:)));
printf("噪点 (85,85) 的标签 = %d, 筛后灰度 = %d\n", labels(85,85), big(85,85));
printf("最大目标面积 = %d（理论 26x30=780 附近）\n", max(areas));
% ---- 可视化 ----
if SHOW
  figure("name", "09 连通域");
  subplot(1, 2, 1); imagesc(labels); axis image off; title("标记图（颜色=域编号）");
  subplot(1, 2, 2); imagesc(big, [0 1]); colormap gray; axis image off; title("面积筛选后");
end""",
            "运行后把 <code>min_area</code> 改成 10 / 1000，观察保留的域数；把连通定义改成 8 连通看斜角接触的差别。",
            "共 5 个连通域（3 大 2 小）；两个噪点面积为 1，被 <code>min_area=100</code> 过滤；最大目标面积与矩形理论面积一致（边界为开区间所以略小）。"),
  ],
  pitfalls=["对灰度图直接做二值形态学：必须先把阈值/分割结果整理成逻辑掩模。",
            "不约定 4/8 连通：斜角接触的目标计数会不一致。",
            "结构元素取偶数尺寸：没有唯一锚点，输出整体偏移半像素。",
            "直接对原图做分水岭：纹理与噪声会制造大量局部极小，必然过分割。"],
  exercises=["证明开运算的幂等性 <code>open(open(A))=open(A)</code>，并说明为什么卷积滤波没有这个性质。",
             "把 09-label-regions.m 的 4 连通改成 8 连通（邻域加 4 个对角点），预测并验证两个斜角接触方块的合并。"],
  further=["<a href='../12-segmentation/index.html'>第 12 章 图像分割（分水岭的完整流程）</a>",
           "<a href='../../part1/04-spatial-filter/index.html'>第 4 章 空间域滤波（排序统计视角）</a>",
           "<a href='../13-descriptors/index.html'>第 13 章 表示、描述与纹理</a>"]),

]
