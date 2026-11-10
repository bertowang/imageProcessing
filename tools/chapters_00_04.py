#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""卷首 00-02 + 第一篇 03-04：章节正文与 Octave 实例。

所有 Octave 脚本遵守同一契约：
  1. 只用 Octave 核心函数，不依赖 image 包，不需要任何外部图片；
  2. 图像统一是 double 型 [0,1] 矩阵，自己用 meshgrid 合成；
  3. 参数集中在脚本开头，改一个数就能看出趋势；
  4. 末尾用 printf 打印可手算核对的数值；
  5. IP_HEADLESS=1 时不弹图形窗口，便于 tools/run_octave.sh 批量验证。
"""
from book_schema import C, demo

CH = [

C("00", "p0", "part0/00-preface", "绪论：两条路线，一本书",
  "把图像处理拆成上卷的可推导算法与下卷的可复现工程：前者要能手推、能跑、能改，后者要能找准原理与官方实现。",
  hours="1 学时",
  goals=["能说清传统算法与深度学习在建模对象、先验来源与失败模式上的差别",
         "知道上下两卷各自的输出物是什么（可运行脚本 / 开源工程链接）",
         "掌握本书固定的四步学习闭环，并会用它安排一章的学习"],
  points=["两条路线的分工", "本书结构与学习闭环", "给程序员的阅读约定", "先修数学清单", "符号与坐标约定", "AI 使用说明"],
  sections=[
      ("0.1", "两条路线的分工", """<p>图像处理要回答同一个问题：<strong>给定像素矩阵，如何得到想要的语义或数值？</strong>两条路线的差别不在“谁更准”，而在<strong>知识从哪里来</strong>。</p>
<table><thead><tr><th style="width:20%">维度</th><th>上卷 · 传统算法</th><th>下卷 · AI 算法</th></tr></thead><tbody>
<tr><td>知识来源</td><td>人写的先验：线性系统、噪声模型、几何约束、统计分布</td><td>数据中的统计规律：由损失函数与优化器从标注中拟合</td></tr>
<tr><td>参数</td><td>少量、有物理含义（核宽、阈值、迭代次数）</td><td>百万到十亿级、无直接物理含义的权重</td></tr>
<tr><td>可解释性</td><td>每一步都能写出公式，误差可逐项归因</td><td>需借助热力图、消融实验与探针间接解释</td></tr>
<tr><td>数据需求</td><td>一张图就能做，适合小样本、无标注场景</td><td>依赖大规模标注与算力，分布外容易失效</td></tr>
<tr><td>典型失败</td><td>模型假设被破坏（噪声非高斯、光照突变、纹理复杂）</td><td>训练/部署分布不一致、标注偏差、对抗样本</td></tr>
<tr><td>本书输出物</td><td>可运行的 <code>.m</code> 脚本 + 预期数值</td><td>原理主线 + 官方开源工程链接</td></tr>
</tbody></table>
<p>两者不是替代关系：下卷的数据增强、预处理、后处理、评价指标、退化建模，几乎全部来自上卷；很多工业系统仍是“传统流水线做确定性部分 + 网络做不确定部分”。<a href="../../part4/26-projects/index.html">第 26 章</a>会要求同一任务同时做两条基线并对比。</p>"""),
      ("0.2", "本书结构与学习闭环", """<p>全书 27 章 + 附录，按上下两卷组织：</p>
<ol class="roadmap">
<li><strong>卷首（00～02）</strong>：约定语言。Octave 环境、图像即矩阵、卷积与评价指标。没有这三层约定，后面的公式和代码都会读错。</li>
<li><strong>上卷（03～15）</strong>：从像素级变换到结构级理解，顺序是<em>增强 → 频域 → 复原 → 几何 → 彩色 → 形态学 → 边缘 → 特征 → 分割 → 描述 → 压缩</em>，最后用一个完整流水线收口。每章至少一个 Octave 实例。</li>
<li><strong>下卷（16～26）</strong>：先用<em>特征工程与机器学习</em>过渡，再进入 CNN、数据集与评测、分类、检测、分割、复原、生成、基础模型，最后是部署与综合项目。每章给官方开源工程链接。</li>
</ol>
<p><strong>学习闭环固定为四步：读公式 → 跑代码 → 改参数 → 写结论。</strong>只跑通不改参数，等于只抄了答案；建议每章记录“手算预期值 → 脚本输出值 → 偏差 → 原因”四列。</p>"""),
      ("0.3", "给程序员的阅读约定", """<p>本书默认读者写过代码、但未必学过信号与系统，因此所有约定都显式写出来：</p>
<div class="card contract"><span class="card-label">代码契约（上卷每章适用）</span><ul style="margin-bottom:0">
<li><strong>零依赖</strong>：只用 Octave 核心函数（<code>conv2</code>/<code>fft2</code>/<code>interp2</code>/<code>imagesc</code> 等），不调用 image 包的 <code>imfilter</code>/<code>edge</code>/<code>imresize</code>。算法主体全部展开，方便对照公式。</li>
<li><strong>自包含</strong>：用 <code>meshgrid</code> 合成测试图，不读外部文件，复制整段代码到 Octave 即可运行。</li>
<li><strong>参数集中</strong>：脚本开头的 <code>% ---- 参数区 ----</code> 集中所有可调量，先改这里。</li>
<li><strong>数值断言</strong>：结尾 <code>printf</code> 打印可手算核对的量；页面「预期与判读」给出数值与解释。</li>
<li><strong>可批量验证</strong>：设环境变量 <code>IP_HEADLESS=1</code> 即不弹窗；用 <code>tools/run_octave.sh</code> 可跑完全部 <code>.m</code>。</li>
</ul></div>
<p>HTML 里的代码块与仓库 <code>code/*.m</code> 由 <code>tools/extract_code.py</code> 自动同步，永远一致；改动请改 <code>tools/chapters_*.py</code>，再运行 <code>python3 tools/build_book.py --force</code> 重新生成。</p>"""),
      ("0.4", "先修知识与符号约定", """<table><thead><tr><th style="width:22%">主题</th><th>需要到什么程度</th><th>对应章节</th></tr></thead><tbody>
<tr><td>线性代数</td><td>矩阵乘法、转置、特征值直觉；把图像看作 <code>M×N</code> 矩阵</td><td>02、07、17</td></tr>
<tr><td>微积分与概率</td><td>偏导、梯度、期望/方差、常见分布</td><td>06、10、17</td></tr>
<tr><td>信号与系统</td><td>卷积、傅里叶变换、线性移不变系统、采样</td><td>02、05、14</td></tr>
<tr><td>最优化</td><td>最小二乘、梯度下降、正则化</td><td>06、12、16、17</td></tr>
<tr><td>编程</td><td>数组/切片/广播、向量化、循环；Octave 或 MATLAB 任一</td><td>01、全书</td></tr>
</tbody></table>
<p><strong>符号约定</strong>：图像记作 <code>f(r,c)</code>，<code>r</code> 是<strong>行</strong>（向下为增，相当于 y），<code>c</code> 是<strong>列</strong>（向右为增，相当于 x）；灰度统一归一化到 <code>[0,1]</code> 的 <code>double</code>；卷积核尺寸为奇数；<code>*</code> 在公式里表示卷积、在代码里表示矩阵乘，代码里的卷积一律用 <code>conv2</code> 显式写出。</p>
<div class="card tip"><p style="margin-bottom:0">最容易踩的坑：<strong>行列与 xy 顺序相反</strong>。<code>f(r,c)</code> 对应坐标 <code>(x,y)=(c,r)</code>。写几何变换时先固定这一点，第 07 章会专门处理。</p></div>"""),
  ],
  demos=[
      demo("code/00-hello-image.m", "最小可运行脚本：矩阵即图像", r"""%% 00-hello-image.m | 第一个图像程序：矩阵即图像
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 8;
% ---- 造图：左半 1（白），右半 0（黑）----
[X, Y] = meshgrid(1:N, 1:N);
img = double(X <= 4);
% ---- 数值验证 ----
printf("尺寸: %d x %d (行 x 列)\n", rows(img), columns(img));
printf("min=%.2f max=%.2f mean=%.4f\n", min(img(:)), max(img(:)), mean(img(:)));
printf("第 1 行: "); printf("%.0f ", img(1, :)); printf("\n");
printf("第 1 列之和（应等于行数）: %.0f\n", sum(img(:, 1)));
% ---- 可视化 ----
if SHOW
  figure("name", "00 矩阵即图像");
  imagesc(img, [0 1]); colormap gray; axis image off;
  title("8x8 二值图像：f(r,c)"); colorbar;
end""",
            "在 Octave 中直接运行 <code>code/00-hello-image.m</code>；批量验证用 <code>IP_HEADLESS=1 tools/run_octave.sh</code>。",
            "尺寸 8×8；min=0、max=1、均值 0.5；第 1 行是 1 1 1 1 0 0 0 0；第 1 列之和为 8。"),
  ],
  pitfalls=["把图像当成 x 优先的坐标：矩阵索引是 (行, 列)，即 (y, x)。",
            "只跑代码不改参数：看不出核宽、阈值对结果的影响，等于没做实验。",
            "以为下卷不需要上卷：数据增强、退化建模、评测指标全都是传统算法的直接应用。"],
  exercises=["把 N 改成 16、判据改成 Y &lt;= 4，预测均值与第 1 行的样子，再运行核对。",
             "用本页的四步闭环，为第 03 章写一份实验记录模板（含预期值列）。"],
  further=["<a href='../01-octave-setup/index.html'>第 1 章 GNU Octave 环境</a>",
           "<a href='../../part4/26-projects/index.html'>第 26 章 工程落地与综合项目</a>",
           "<a href='../../appendix/index.html'>附录 A · 速查与资源总表</a>"]),

C("01", "p0", "part0/01-octave-setup", "GNU Octave 环境与图像 I/O",
  "装好环境、统一数据类型、学会造测试图：这一章决定后面 14 章的代码能不能一次跑通。",
  hours="2 学时",
  goals=["能在命令行与 GUI 两种模式下运行一个 .m 脚本",
         "说清 uint8 / double / logical 三种图像类型的差异与转换规则",
         "能自己合成阶跃、条纹、圆盘与带噪测试图",
         "会用一键验证脚本批量运行全书示例"],
  points=["安装与两种运行方式", "图像即矩阵：坐标与索引", "数据类型与范围约定", "显示与保存", "合成测试图像", "一键验证脚本"],
  sections=[
      ("1.1", "安装与两种运行方式", """<p>GNU Octave 是免费的科学计算环境，语法与 MATLAB 高度兼容，Windows / macOS / Linux 都能装。推荐两种用法：</p>
<ul><li><strong>GUI</strong>：适合看图和调参数，直接打开文件后按 F5。</li>
<li><strong>命令行</strong>：<code>octave --no-gui --quiet code/00-hello-image.m</code>，适合批量跑和写自动化脚本。本书的 <code>tools/run_octave.sh</code> 就用这种方式。</li></ul>
<pre class="code" data-file="inline" data-lang="Shell"><code># macOS (Homebrew)            # Ubuntu/Debian              # Windows
brew install octave          sudo apt install octave      # 官网下载安装包 https://octave.org/download
octave --version             octave --eval "disp(2+2)"    # 输出 4 即安装成功</code></pre>
<p class="code-hint">本书示例<strong>不要求</strong>安装 image 包。若你想用 <code>imshow</code>、<code>imfilter</code>、<code>edge</code> 等现成函数，可执行 <code>pkg install -forge image</code> 并 <code>pkg load image</code>；但书中每个算法都会用核心函数手写一遍，以便看清实现。</p>"""),
      ("1.2", "图像 = 矩阵：坐标与类型", """<table><thead><tr><th>类型</th><th>取值范围</th><th>典型用途</th><th>陷阱</th></tr></thead><tbody>
<tr><td><code>uint8</code></td><td>0～255 整数</td><td>文件读写、节省内存</td><td>做加减会<strong>饱和截断</strong>，<code>uint8(200)+uint8(100)</code> 得 255 而不是 300</td></tr>
<tr><td><code>double</code></td><td>本书统一为 [0,1]</td><td>滤波、变换、公式推导</td><td>超过 1 的值用 <code>imagesc(a,[0 1])</code> 会被裁白，先 <code>min(max(a,0),1)</code></td></tr>
<tr><td><code>logical</code></td><td>0 / 1</td><td>掩模、区域、索引</td><td>与 double 混算前先 <code>double(mask)</code></td></tr>
<tr><td><code>M×N×3</code></td><td>三个通道</td><td>RGB 彩色图</td><td>灰度图没有第三维，<code>size(a,3)</code> 为 1</td></tr>
</tbody></table>
<p>行列与坐标的对应关系请记牢：<code>f(r,c)</code> 表示第 <code>r</code> 行、第 <code>c</code> 列，几何坐标是 <code>(x,y)=(c,r)</code>。显示时用 <code>axis image</code> 保证纵横比不变，用 <code>colormap gray</code> 保证灰度图不被伪彩染色。</p>"""),
      ("1.3", "显示、保存与文件读写", """<p>核心的显示三件套是 <code>imagesc</code> + <code>colormap gray</code> + <code>axis image off</code>；<code>imagesc(a,[0 1])</code> 的第二个参数固定显示范围，避免不同图自动缩放造成视觉误判。</p>
<p>需要读真实照片时，Octave 自带的 <code>imread</code> / <code>imwrite</code> 可以直接用：</p>
<pre class="code" data-file="inline" data-lang="Octave 片段"><code>a = imread("photo.png");        % 通常是 uint8 MxNx3
g = double(a) / 255;            % 转到本书统一的 [0,1] double
imwrite(uint8(g * 255), "out.png");
printf("size: %d x %d x %d\n", size(g,1), size(g,2), size(g,3));</code></pre>
<p class="code-hint">外部图片不可控（光照、压缩、尺寸），所以<strong>全书示例一律用合成图</strong>：数值可预测、结果可复现、无需附带素材文件。学会造测试图是做算法实验的基本功。</p>"""),
      ("1.4", "代码契约与一键验证", """<p>每个 <code>.m</code> 脚本都分成五段：<strong>参数区 → 造图 → 算法 → 数值验证 → 可视化</strong>。可视化被 <code>if SHOW</code> 包住，<code>SHOW</code> 由环境变量 <code>IP_HEADLESS</code> 控制：</p>
<pre class="code" data-file="inline" data-lang="Shell"><code># 交互式：看图 + 看数值
octave --no-gui --quiet code/03-histeq.m
# 批量：不弹窗，只检查每个脚本能否正常结束、数值是否打印
IP_HEADLESS=1 ./tools/run_octave.sh
# 只跑某一个脚本
IP_HEADLESS=1 ./tools/run_octave.sh part1/03-gray-transform/code/03-histeq.m</code></pre>
<p>HTML 页面里的代码块与磁盘上的 <code>code/*.m</code> 由 <code>tools/extract_code.py</code> 自动同步；<code>tools/check_book.py</code> 会检查两者一致、脚本是否含参数区与数值打印、是否误用了 image 包专有函数。</p>"""),
  ],
  demos=[
      demo("code/01-types-and-range.m", "数据类型、范围与饱和截断", r"""%% 01-types-and-range.m | uint8 / double / logical 的行为差异
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
v = 200;
% ---- 算法：观察 uint8 的饱和与 double 的线性 ----
u = uint8(v);
printf("uint8(%d) + uint8(100) = %d  (饱和到 255)\n", v, u + uint8(100));
printf("double(%d)/255 + 0.4   = %.4f\n", v, double(v)/255 + 0.4);
g = (0:255) / 255;                     % 0~1 渐变
clipped = min(max(g * 2, 0), 1);       % 超过 1 的部分必须裁掉
printf("渐变 g: min=%.3f max=%.3f mean=%.4f\n", min(g), max(g), mean(g));
printf("放大 2 倍后未裁剪的比例: %.2f%%\n", 100 * mean(g * 2 > 1));
mask = g > 0.5;
printf("logical 掩模: class=%s 命中 %d / %d\n", class(mask), sum(mask(:)), numel(mask));
printf("掩模均值（double 化后）: %.4f\n", mean(double(mask(:))));
% ---- 可视化 ----
if SHOW
  figure("name", "01 范围与裁剪");
  subplot(1, 2, 1); plot(g * 2); grid on; title("未裁剪：最大值 2"); ylim([0 2.2]);
  subplot(1, 2, 2); plot(clipped); grid on; title("裁剪到 [0,1]"); ylim([0 1.2]);
end""",
            "运行后对照四行打印值；把 <code>v</code> 改成 100 再跑一次，看饱和是否还发生。",
            "uint8 相加得 255；double 得约 1.1843；渐变均值 0.5；放大 2 倍后恰好 50% 越界；掩模命中 128/256，均值 0.5。"),
      demo("code/01-synthetic-images.m", "合成测试图与噪声注入", r"""%% 01-synthetic-images.m | 阶跃 / 条纹 / 圆盘 + 高斯与椒盐噪声
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
N = 256; sigma = 0.06; salt_rate = 0.02; rand("seed", 7); randn("seed", 7);
% ---- 造图 ----
[X, Y] = meshgrid(1:N, 1:N);
step  = double(X > N/2);
stripe = 0.5 + 0.35 * sin(2*pi*X/24);
disk  = double((X - 0.5*N).^2 + (Y - 0.5*N).^2 < (0.28*N)^2);
base  = 0.25 + 0.6 * disk;
% ---- 噪声：高斯加性 + 椒盐脉冲 ----
noisy = base + sigma * randn(N, N);
sp = rand(N, N);
noisy(sp < salt_rate/2) = 0;
noisy(sp > 1 - salt_rate/2) = 1;
noisy = min(max(noisy, 0), 1);
% ---- 数值验证 ----
printf("step : mean=%.4f (期望 0.5)\n", mean(step(:)));
printf("stripe: min=%.3f max=%.3f mean=%.4f\n", min(stripe(:)), max(stripe(:)), mean(stripe(:)));
printf("disk : 面积占比=%.4f (pi*0.28^2=%.4f)\n", mean(disk(:)), pi*0.28^2);
printf("noisy: 与干净图的 MSE=%.6f, PSNR=%.2f dB\n", ...
       mean((noisy(:)-base(:)).^2), 10*log10(1/mean((noisy(:)-base(:)).^2)));
% ---- 可视化 ----
if SHOW
  figure("name", "01 合成测试图");
  subplot(2, 2, 1); imagesc(step, [0 1]); colormap gray; axis image off; title("阶跃");
  subplot(2, 2, 2); imagesc(stripe, [0 1]); axis image off; title("正弦条纹");
  subplot(2, 2, 3); imagesc(disk, [0 1]); axis image off; title("圆盘掩模");
  subplot(2, 2, 4); imagesc(noisy, [0 1]); axis image off; title("高斯 + 椒盐噪声");
end""",
            "运行脚本；把 <code>sigma</code> 改为 0.02 / 0.15，记录 PSNR 的变化趋势。",
            "阶跃均值 0.5；条纹范围约 0.15～0.85、均值 0.5；圆盘面积占比约 0.2463（π·0.28²）；噪声图的 MSE 与 PSNR 随 sigma 单调变化。"),
  ],
  pitfalls=["对 uint8 直接做加减导致静默饱和：先 <code>double(a)/255</code> 再运算。",
            "显示时不固定范围：<code>imagesc(a,[0 1])</code> 才能跨图比较亮度。",
            "把噪声图的越界值直接显示：<code>min(max(a,0),1)</code> 后再画图与算指标。",
            "忘了 <code>clear</code> 与固定随机种子，导致两次运行结果不同、无法对照。"],
  exercises=["把 01-types-and-range.m 的 <code>v</code> 改成 100，解释为什么这次不发生饱和。",
             "在 01-synthetic-images.m 里把椒盐比例提高到 0.1，预测 MSE 与 PSNR 的变化方向并核对。"],
  further=["<a href='../00-preface/index.html'>第 0 章 绪论</a>",
           "<a href='../02-image-basics/index.html'>第 2 章 图像的数学表示</a>",
           "<a href='../../appendix/index.html'>附录 A.1 Octave 函数速查</a>"]),

C("02", "p0", "part0/02-image-basics", "图像的数学表示与运算约定",
  "采样量化、卷积与相关、边界处理、质量评价：把后面所有章节共用的四件事一次讲清。",
  hours="3 学时",
  goals=["能写出二维离散卷积与相关的定义并说明差别",
         "能解释四种边界填充对滤波结果的影响",
         "会手算 MSE / PSNR 并说明为什么它不等于视觉质量",
         "能用核心函数实现一个带边界处理的二维卷积"],
  points=["采样与量化", "直方图与统计量", "卷积与相关", "边界填充策略", "线性移不变系统", "MSE / PSNR / SSIM"],
  sections=[
      ("2.1", "采样、量化与直方图", """<p>连续场景经<strong>空间采样</strong>变成 <code>M×N</code> 网格，再经<strong>幅度量化</strong>变成有限灰度级。采样决定分辨率与混叠，量化决定位深（8 bit = 256 级）。本书把灰度统一归一化到 <code>[0,1]</code>，因此位深只在读写文件时出现。</p>
<p>直方图 <code>h(k)</code> 统计灰度级 <code>k</code> 的像素数，归一化后是概率质量函数 <code>p(k)=h(k)/(MN)</code>。一阶统计量（均值、方差）描述整体亮度与对比度，但<strong>丢掉了空间结构</strong>：两张完全不同的图可以有完全相同的直方图，第 05 章的相位实验会把这一点展示得很彻底。</p>"""),
      ("2.2", "卷积、相关与边界", """<p>线性移不变滤波由卷积定义，<code>g(r,c) = ΣΣ f(r−i,c−j)·w(i,j)</code>；相关只差一个核翻转：<code>g(r,c) = ΣΣ f(r+i,c+j)·w(i,j)</code>。数学卷积要翻转核，图像处理里常把“已翻转好的模板”称为卷积核，于是两者代码一样。本书统一用 <code>conv2</code>，并在注释里写明是否翻转。</p>
<span class="eq">g = f ∗ w，　G(u,v) = F(u,v) · H(u,v)</span>
<table><thead><tr><th>边界策略</th><th>做法</th><th>后果</th></tr></thead><tbody>
<tr><td>zero / 补零</td><td>外侧填 0</td><td>边缘出现暗边，简单且最常用</td></tr>
<tr><td>replicate</td><td>复制最外圈像素</td><td>边缘平滑，适合去噪</td></tr>
<tr><td>symmetric</td><td>镜像反射</td><td>避免人为边缘，梯度更自然</td></tr>
<tr><td>circular / 周期</td><td>首尾相接</td><td>与 DFT 假设一致，频域滤波默认</td></tr>
</tbody></table>
<p><strong>尺寸约定</strong>：<code>conv2(f,w,"same")</code> 返回与 <code>f</code> 同尺寸；<code>"valid"</code> 只保留核完全落在图内的部分，输出会缩小 <code>(k−1)</code>。核尺寸取奇数是为了有明确中心。</p>"""),
      ("2.3", "线性移不变系统与点扩散函数", """<p>若成像系统满足线性与移不变，它对点光源的响应 <code>h</code>（点扩散函数，PSF）就完整描述了系统：输出是 <code>f∗h</code>。于是“模糊”可以被建模、“去模糊”可以被写成反卷积（第 06 章）。空间域卷积对应频域逐点相乘，这是第 05 章全部内容的起点。</p>
<p class="code-hint">这条链条是上卷的主干：<strong>PSF → 卷积 → 频域乘积 → 逆滤波/维纳滤波 → 复原</strong>。下卷的超分与去噪网络，本质上仍在学习一个更好的逆映射，只是先验由数据给出而不是由公式给出。</p>"""),
      ("2.4", "质量评价：MSE、PSNR 与 SSIM", """<span class="eq">MSE = (1/MN)Σ(f−ĝ)²,　PSNR = 10·log₁₀(L²/MSE)，本书 L = 1</span>
<p>PSNR 只衡量逐像素误差，对结构错位、模糊、感知质量都不敏感；SSIM 把比较拆成<strong>亮度、对比度、结构</strong>三项，更接近人眼，但仍不是感知质量的终点（下卷会用 LPIPS、FID 等基于特征的指标）。</p>
<div class="card warn"><p style="margin-bottom:0"><strong>评价的铁律</strong>：有参考图才能算 PSNR/SSIM；无参考的真实去噪任务只能用噪声估计、人工评分或下游任务指标。数值变好但看起来更糊，通常说明你优化错了目标。</p></div>"""),
  ],
  demos=[
      demo("code/02-conv-and-psnr.m", "手写二维卷积、边界填充与 PSNR", r"""%% 02-conv-and-psnr.m | 二维卷积 / 边界策略 / MSE-PSNR 的一致性
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
end""",
            "运行后重点看第二行数值（应接近机器精度）；把 <code>k</code> 改成 5、<code>noise_sigma</code> 改成 0.1 再跑。",
            "核和为 1；手写循环与 conv2 的最大差约 0（浮点误差）；zero 边界角落更暗；PSNR 约 26 dB，与 10·log10(1/σ²) 一致。"),
  ],
  pitfalls=["把相关当卷积却忘了翻转核：对称核无差别，非对称梯度核会差一个方向。",
            "用 <code>conv2(...,\"valid\")</code> 后仍按原尺寸索引，导致维度不匹配。",
            "对 uint8 直接算 MSE：溢出会给出完全错误的结果。",
            "只报 PSNR 不附视觉结果：PSNR 高不代表结构被正确恢复。"],
  exercises=["把 02 的盒式核换成 <code>[0 1 0; 1 -4 1; 0 1 0]</code>，解释输出在方块边缘出现正负值的原因。",
             "推导：当噪声服从 N(0,σ²) 时，为什么 PSNR ≈ 10·log10(1/σ²)？用脚本验证 σ=0.1 的情形。"],
  further=["<a href='../../part1/04-spatial-filter/index.html'>第 4 章 空间域滤波</a>",
           "<a href='../../part1/05-frequency-domain/index.html'>第 5 章 频域处理</a>",
           "<a href='../../part1/06-restoration/index.html'>第 6 章 图像复原与去噪</a>"]),

C("03", "p1", "part1/03-gray-transform", "灰度变换与直方图",
  "从点运算到直方图均衡：第一个“能推公式、能看效果、能打印数值”的完整算法。",
  hours="3 学时",
  goals=["能写出四类常用灰度映射并判断各自适用场景",
         "能从累积分布函数推出直方图均衡化的离散公式",
         "能自己用循环实现 histeq 并用数值验证均匀性",
         "说清 CLAHE 解决什么问题、引入什么新参数"],
  points=["点运算与灰度映射", "gamma 校正", "直方图与 CDF", "直方图均衡化推导", "离散实现与均匀性", "CLAHE 与规定化"],
  sections=[
      ("3.1", "点运算与四种映射", """<p>点运算不含邻域：输出像素只由同一位置的输入像素决定，<code>g = T(f)</code>。因此它不改变空间结构，只改变灰度分布，天然可并行、可用查找表（LUT）实现。</p>
<table><thead><tr><th>映射</th><th>公式</th><th>作用</th></tr></thead><tbody>
<tr><td>线性/对比度拉伸</td><td><code>g = a·f + b</code></td><td>整体提亮或压暗，注意裁剪</td></tr>
<tr><td>对数</td><td><code>g = c·log(1+f)</code></td><td>压缩高亮动态范围，显示傅里叶频谱</td></tr>
<tr><td>幂律 / gamma</td><td><code>g = f^γ</code></td><td>γ&lt;1 提亮暗部，γ&gt;1 压暗；补偿显示器非线性</td></tr>
<tr><td>分段线性</td><td>折线 T</td><td>只拉伸感兴趣灰度区间、二值化、灰度切片</td></tr>
</tbody></table>
<p>工程上注意 <code>T</code> 必须单调（否则灰度次序反转），输出要裁到 <code>[0,1]</code>；对 uint8 图先转 double 再映射。</p>"""),
      ("3.2", "直方图均衡化的推导", """<p>目标：找一个单调变换 <code>s = T(r)</code>，使输出的灰度分布<strong>均匀</strong>。连续情形下，概率密度在变换下满足 <code>p_s(s) = p_r(r)·|dr/ds|</code>；取 <code>s = T(r) = ∫₀ʳ p_r(w)dw</code>，即<strong>累积分布函数（CDF）</strong>，则 <code>ds/dr = p_r(r)</code>，代入得 <code>p_s(s)=1</code>。</p>
<span class="eq">sₖ = T(rₖ) = Σⱼ₌₀ᵏ p_r(rⱼ) = Σⱼ₌₀ᵏ nⱼ / (MN)</span>
<p>离散实现只有三步：统计直方图 <code>h</code> → 归一化并求 <code>cumsum</code> 得 LUT → 用 LUT 查表映射每个像素。结果不会严格均匀（灰度级有限、同灰度像素必须一起搬移），但会明显展宽动态范围。</p>"""),
      ("3.3", "全局均衡的局限与 CLAHE", """<p>全局均衡用整幅图的 CDF，会带来三个典型问题：暗区被整体抬亮后噪声被放大、局部细节没有针对性增强、背景占比大时主体反而过曝。</p>
<p><strong>CLAHE</strong>（限制对比度自适应直方图均衡）的做法是：把图切成小块（如 8×8），每块单独均衡；均衡前把直方图超过 <code>clip_limit</code> 的部分<strong>削峰并均匀再分配</strong>，从而限制噪声放大；最后用双线性插值拼接块边界，消除块效应。新增的两个参数（块数、裁剪限幅）都可在第 12 章的分割任务里用下游指标来调。</p>
<div class="card tip"><p style="margin-bottom:0"><strong>直方图规定化</strong>是另一个方向的推广：不要求输出均匀，而是要求输出匹配<em>指定</em>的直方图。做法是分别求输入与目标的 CDF，再用 <code>T = CDF_target⁻¹ ∘ CDF_input</code> 建立映射。</p></div>"""),
  ],
  demos=[
      demo("code/03-gray-transform.m", "gamma 与对数映射的数值对照", r"""%% 03-gray-transform.m | 点运算：线性 / gamma / 对数映射
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
gamma = 0.45; a = 1.2; b = -0.1; N = 256;
% ---- 造图：偏暗的渐变 + 亮圆盘 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.05 + 0.35 * (X / N) + 0.45*double((X-170).^2 + (Y-120).^2 < 45^2);
f = min(max(f, 0), 1);
% ---- 算法：四种 LUT 映射 ----
g_lin    = min(max(a*f + b, 0), 1);
g_gamma  = f .^ gamma;
g_invgan = f .^ (1/gamma);
g_log    = log(1 + f) / log(2);
r = linspace(0, 1, 256);
lut_gamma = r .^ gamma;
g_lut = reshape(interp1(r, lut_gamma, f(:)), size(f));   % 用查找表实现同一映射
% ---- 数值验证 ----
printf("原图       mean=%.4f std=%.4f\n", mean(f(:)), std(f(:)));
printf("线性拉伸   mean=%.4f std=%.4f\n", mean(g_lin(:)), std(g_lin(:)));
printf("gamma=%.2f  mean=%.4f std=%.4f\n", gamma, mean(g_gamma(:)), std(g_gamma(:)));
printf("gamma>1    mean=%.4f std=%.4f\n", mean(g_invgan(:)), std(g_invgan(:)));
printf("对数映射   mean=%.4f std=%.4f\n", mean(g_log(:)), std(g_log(:)));
printf("LUT 与逐像素映射最大差 = %.3e\n", max(abs(g_lut(:)-g_gamma(:))));
printf("f=0.25 时 gamma 输出 = %.4f (0.25^%.2f)\n", 0.25^gamma, gamma);
% ---- 可视化 ----
if SHOW
  figure("name", "03 灰度映射");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图（偏暗）");
  subplot(2, 2, 2); imagesc(g_gamma, [0 1]); axis image off; title("gamma<1 提亮暗部");
  subplot(2, 2, 3); imagesc(g_log, [0 1]); axis image off; title("对数压缩");
  subplot(2, 2, 4); plot(r, r.^gamma, "linewidth", 2); grid on; xlabel("输入 r"); ylabel("T(r)"); title("gamma LUT");
end""",
            "运行后把 <code>gamma</code> 依次改成 0.25 / 1 / 2.2，记录均值与标准差的变化方向。",
            "gamma&lt;1 时均值显著上升、标准差下降（暗部被抬起）；gamma&gt;1 时均值下降；LUT 与直接映射最大差接近 0；f=0.25、γ=0.45 时输出约 0.5359。"),
      demo("code/03-histeq.m", "手写直方图均衡化与均匀性验证", r"""%% 03-histeq.m | 直方图均衡化：统计 h -> CDF -> LUT -> 映射
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
bins = 256; N = 256;
% ---- 造图：窄动态范围的偏暗图 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.30 + 0.20*(X/N) + 0.12*double((X-120).^2 + (Y-140).^2 < 50^2);
f = min(max(f, 0), 1);
% ---- 算法：直方图 -> 归一化 CDF -> 查表 ----
q = round(f(:) * (bins-1)) + 1;         % 量化到 1..bins
h = zeros(bins, 1);
for i = 1:numel(q)
  h(q(i)) = h(q(i)) + 1;               % 显式统计，便于对照公式
end
cdf = cumsum(h) / numel(q);
g = reshape(cdf(q), size(f));
% ---- 数值验证 ----
printf("直方图总和 = %d，像素总数 = %d\n", sum(h), numel(f));
printf("CDF 末项 = %.6f（应为 1）\n", cdf(end));
printf("原图 mean=%.4f std=%.4f  均衡后 mean=%.4f std=%.4f\n", ...
       mean(f(:)), std(f(:)), mean(g(:)), std(g(:)));
printf("原图占用的灰度级数 = %d / %d\n", sum(h > 0), bins);
hg = zeros(bins,1); qg = round(g(:)*(bins-1)) + 1;
for i = 1:numel(qg), hg(qg(i)) = hg(qg(i)) + 1; end
printf("均衡后占用的灰度级数 = %d / %d\n", sum(hg > 0), bins);
printf("理想均匀时每级像素数 = %.1f，实测最大级 = %d\n", numel(f)/bins, max(hg));
% ---- 可视化 ----
if SHOW
  figure("name", "03 直方图均衡");
  subplot(2, 2, 1); imagesc(f, [0 1]); colormap gray; axis image off; title("原图");
  subplot(2, 2, 2); imagesc(g, [0 1]); axis image off; title("均衡后");
  subplot(2, 2, 3); bar(h); xlim([0 bins]); title("原直方图");
  subplot(2, 2, 4); bar(hg); xlim([0 bins]); title("均衡后直方图");
end""",
            "运行脚本，对照“原图占用级数”与“均衡后占用级数”；把 <code>bins</code> 改成 16 观察离散化变粗。",
            "直方图总和等于像素数、CDF 末项为 1；原图只占约 80 个灰度级，均衡后覆盖范围显著变宽、均值趋近 0.5、标准差增大；由于同灰度像素必须成组搬移，直方图不会严格平坦。"),
  ],
  pitfalls=["对 uint8 直接做 <code>f^γ</code>：指数运算会隐式转 double 但结果仍是 0～255 量纲，必须先归一化。",
            "以为均衡一定提升对比度：背景占比大时会放大噪声、导致主体过曝。",
            "把 CDF 当成 PDF 用：映射要用累积分布，不是直方图本身。",
            "忽略离散化：灰度级越少，均衡后越容易出现条带（banding）。"],
  exercises=["推导连续情形下 <code>s=T(r)=∫p_r</code> 使 <code>p_s(s)=1</code> 的完整过程，并说明离散情形为何只能近似。",
             "在 03-histeq.m 里额外打印均衡前后的 10 分位数，解释它们与 CDF 的关系。"],
  further=["<a href='../04-spatial-filter/index.html'>第 4 章 空间域滤波</a>",
           "<a href='../../part2/12-segmentation/index.html'>第 12 章 图像分割（Otsu 也依赖直方图）</a>",
           "<a href='../../appendix/index.html'>附录 A.2 传统算法速查表</a>"]),

C("04", "p1", "part1/04-spatial-filter", "空间域滤波",
  "从构造一个高斯核开始，把线性平滑、非线性去噪与锐化统一到“邻域加权”这一个动作上。",
  hours="4 学时",
  goals=["能手工构造高斯核并说明可分离性带来的复杂度收益",
         "能实现带边界处理的线性滤波并预测输出值域",
         "理解中值滤波为何能去掉椒盐噪声而保住边缘",
         "能写出拉普拉斯与非锐化掩蔽的公式并指出振铃来源"],
  points=["线性滤波与卷积核", "高斯核与可分离性", "边界处理", "中值与排序统计", "拉普拉斯锐化", "双边滤波"],
  sections=[
      ("4.1", "线性滤波：核决定一切", """<p>线性滤波就是用一个小矩阵 <code>w</code> 在图上滑动求和。核的<strong>元素和</strong>决定整体增益：和为 1 保持亮度，和为 0 提取差分（梯度/拉普拉斯），和为负会得到反相图。</p>
<span class="eq">g(r,c) = Σᵢ Σⱼ w(i,j) · f(r+i, c+j)</span>
<p>盒式核 <code>ones(k)/k²</code> 最简单但有明显振铃（频域是 sinc，旁瓣高）；高斯核在空域与频域都是高斯，<strong>没有旁瓣</strong>，是最常用的平滑核：</p>
<span class="eq">w(x,y) = (1/2πσ²)·exp(−(x²+y²)/2σ²)，　w(x,y) = wₓ(x)·w_y(y)</span>
<p>可分离性把一个 <code>k×k</code> 卷积拆成两次一维卷积，复杂度从 <code>O(k²)</code> 降到 <code>O(2k)</code>；核越大收益越明显。经验取值：核半径约 <code>3σ</code>。</p>"""),
      ("4.2", "非线性滤波：中值与排序统计", """<p>椒盐噪声是<strong>脉冲</strong>：个别像素被置为 0 或 1。线性平均会把脉冲“摊”到邻域里，越平滑越糊；中值滤波取邻域排序后的中间值，只要脉冲占比小于一半，极值就不会进入输出，因此能<strong>去脉冲同时保边</strong>。推广形式是排序统计滤波（取第 p 个分位数）：最大值 = 膨胀、最小值 = 腐蚀，正是第 09 章形态学的灰度版本。</p>
<div class="card note"><p style="margin-bottom:0"><strong>代价</strong>：中值滤波不是线性系统，不能用卷积或传递函数分析，也不满足叠加原理；大窗口会抹掉细线与小目标。窗口尺寸应小于希望保留的最小结构。</p></div>"""),
      ("4.3", "锐化：拉普拉斯与非锐化掩蔽", """<p>模糊等价于衰减高频，锐化等价于把高频加回去。二阶导数用拉普拉斯核近似：</p>
<table><thead><tr><th>核</th><th>形式</th><th>用途</th></tr></thead><tbody>
<tr><td>4 邻域拉普拉斯</td><td><code>[0 1 0; 1 -4 1; 0 1 0]</code></td><td>各向同性二阶差分</td></tr>
<tr><td>8 邻域拉普拉斯</td><td><code>[1 1 1; 1 -8 1; 1 1 1]</code></td><td>对角线响应更强</td></tr>
</tbody></table>
<span class="eq">g = f + λ·∇²f　（非锐化掩蔽 USM：g = f + λ·(f − blur(f))）</span>
<p><code>λ</code> 是唯一要调的参数：太小看不出效果，太大会在边缘两侧出现<strong>过冲与白边（halo）</strong>，同时放大噪声。工业做法常先轻微去噪再 USM，或用掩模限制只在边缘区域增强。</p>"""),
      ("4.4", "保边平滑与双边滤波", """<p>高斯平滑只看<strong>空间距离</strong>，因此会跨过边缘把两侧像素混在一起。双边滤波再加一个<strong>灰度相似度</strong>权重：</p>
<span class="eq">g(p) = (1/W) Σ_q exp(−‖p−q‖²/2σ_s²) · exp(−(f(p)−f(q))²/2σ_r²) · f(q)</span>
<p>结果是“平坦区域内强平滑、边缘两侧几乎不互相影响”。代价是权重依赖图像内容，<strong>不再是卷积</strong>，无法用 FFT 加速，计算量也大。它是“传统算法里最像学习方法”的一类：先验由人写死，但权重由数据自适应决定。第 23 章会看到深度网络如何学出类似的自适应滤波。</p>"""),
  ],
  demos=[
      demo("code/04-linear-filter.m", "高斯核构造、可分离验证与平滑效果", r"""%% 04-linear-filter.m | 高斯核 / 可分离性 / 加噪图的平滑
%% GNU Octave，零第三方依赖；合成图像，无需任何外部文件
clear; close all; clc;
SHOW = ~strcmp(getenv("IP_HEADLESS"), "1");
% ---- 参数区 ----
sigma = 2.0; radius = 6; noise_sigma = 0.08; N = 128;
randn("seed", 21);
% ---- 造图：阶跃边缘 + 高斯噪声 ----
[X, Y] = meshgrid(1:N, 1:N);
f = 0.3 + 0.4*double(X > N/2);
noisy = min(max(f + noise_sigma*randn(N,N), 0), 1);
% ---- 算法 1：由公式构造可分离高斯核 ----
x = -radius:radius;
w1 = exp(-x.^2 / (2*sigma^2)); w1 = w1 / sum(w1);
w2 = w1' * w1;                                  % 外积 = 二维高斯核
% ---- 算法 2：两次一维卷积 == 一次二维卷积 ----
sep  = conv2(conv2(noisy, w1, "same"), w1', "same");
full = conv2(noisy, w2, "same");
% ---- 数值验证 ----
printf("一维核长度 = %d, 和 = %.6f\n", numel(w1), sum(w1));
printf("二维核尺寸 = %dx%d, 和 = %.6f\n", rows(w2), columns(w2), sum(w2(:)));
printf("可分离与二维卷积最大差 = %.3e\n", max(abs(sep(:)-full(:))));
printf("噪声标准差: 平滑前 %.4f -> 平滑后 %.4f\n", std(noisy(:)), std(full(:)));
printf("边缘两侧均值: %.4f / %.4f (原始 0.3000 / 0.7000)\n", ...
       mean(mean(full(:, 20:40))), mean(mean(full(:, 90:110))));
printf("加噪 MSE=%.6f 平滑后 MSE=%.6f\n", ...
       mean((noisy(:)-f(:)).^2), mean((full(:)-f(:)).^2));
% ---- 可视化 ----
if SHOW
  figure("name", "04 线性滤波");
  subplot(1, 3, 1); imagesc(noisy, [0 1]); colormap gray; axis image off; title("加噪图");
  subplot(1, 3, 2); imagesc(w2, [0 max(w2(:))]); axis image off; title("高斯核");
  subplot(1, 3, 3); imagesc(full, [0 1]); axis image off; title("高斯平滑后");
end""",
            "运行后把 <code>sigma</code> 改为 0.8 / 4，比较“平滑后标准差”和“平滑后 MSE”的变化。",
            "核和为 1；可分离结果与二维卷积最大差在机器精度内；平滑后噪声标准差显著下降；但边缘两侧均值会向中间靠拢，说明边缘同时被模糊——这就是双边滤波的动机。"),
      demo("code/04-median-sharpen.m", "中值去椒盐、拉普拉斯与非锐化掩蔽", r"""%% 04-median-sharpen.m | 中值滤波 / 拉普拉斯 / USM 对照
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
end""",
            "运行并把 <code>salt_rate</code> 提高到 0.3，观察中值滤波何时开始失效；把 <code>lambda</code> 改成 2 观察过冲。",
            "中值的 MSE 明显小于均值，说明脉冲噪声下非线性滤波更合适；中值结果中 0/1 极值几乎消失；锐化输出会略超出 [0,1]，正是边缘过冲；噪声占比接近或超过 50% 时中值也会失效。"),
  ],
  pitfalls=["高斯核忘记归一化：整幅图会变亮或变暗，而不是被平滑。",
            "核尺寸取偶数：没有唯一中心，输出会发生半像素偏移。",
            "用均值滤波处理椒盐噪声：脉冲被摊开成一片灰点，反而更难看。",
            "锐化前不去噪：<code>λ</code> 会同时放大噪声，边缘出现大量白边。"],
  exercises=["推导二维高斯核可分离性的代数过程，并用 04-linear-filter.m 的打印值核对。",
             "把中值窗口改成 5×5，观察细线是否被抹掉；总结“窗口必须小于待保留结构”的经验规则。"],
  further=["<a href='../05-frequency-domain/index.html'>第 5 章 频域处理</a>",
           "<a href='../../part2/10-edge-detection/index.html'>第 10 章 边缘检测</a>",
           "<a href='../../part2/09-morphology/index.html'>第 9 章 数学形态学</a>"]),

]
