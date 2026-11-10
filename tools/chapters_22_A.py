#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下卷 22-26 + 附录 A。

附录 A.3（开源工程总表）与 A.7（全书链接总表）由 build_book.py 动态生成，
因此这里只写 A.1 / A.2 / A.4 / A.5 / A.6 五节静态内容。
"""
from book_schema import C, demo

CH = [

C("22", "p4", "part4/22-segmentation-networks", "深度图像分割",
  "从逐像素分类到掩码分类，再到“给个提示就出掩码”：分割的演进本质是输出表示方式的演进。",
  hours="4 学时",
  goals=["能区分语义、实例、全景三类分割的输出",
         "能说明 FCN、U-Net、DeepLab 各自解决什么问题",
         "理解掩码分类与逐像素分类的差别",
         "能描述 SAM 的可提示分割范式及其局限"],
  points=["语义/实例/全景分割", "FCN 与全卷积", "U-Net 与跳跃连接", "空洞卷积与 ASPP", "Mask R-CNN", "Mask2Former 掩码分类", "SAM 与可提示分割"],
  sections=[
      ("22.1", "三类分割任务", """<table><thead><tr><th>任务</th><th>输出</th><th>关键难点</th></tr></thead><tbody>
<tr><td>语义分割</td><td>每个像素一个类别标签</td><td>不区分同类个体；细节边界与小目标</td></tr>
<tr><td>实例分割</td><td>每个目标一个类别 + 一个掩码</td><td>同类粘连目标分离、遮挡</td></tr>
<tr><td>全景分割</td><td>前景按实例、背景按语义</td><td>统一两类输出并保持一致评测</td></tr>
</tbody></table>
<p>注意输出始终是<strong>整数标签图</strong>，因此缩放/几何增强只能用最近邻插值（第 07、17 章），用双线性会凭空造出不存在的类别编号。</p>"""),
      ("22.2", "FCN、U-Net 与 DeepLab", """<ul><li><strong>FCN</strong>：把分类网络末端的全连接换成卷积，得到热力图，再用反卷积/上采样恢复到原分辨率；<strong>跳跃连接</strong>融合浅层细节以修边界。</li>
<li><strong>U-Net</strong>：对称编码器-解码器 + 逐级跳跃拼接，在小样本医学影像上极为有效，是至今最常用的分割基线。</li>
<li><strong>DeepLab 系列</strong>：<strong>空洞卷积</strong>在不降分辨率的前提下扩大感受野，<strong>ASPP</strong> 并行多个空洞率捕获多尺度上下文，末端常用 CRF 或细化模块修边。</li></ul>
<p>损失函数通常是<strong>交叉熵 + Dice / Lovász</strong> 的组合：交叉熵稳定，Dice 直接优化重叠度、对前景占比小更友好（第 19 章）。</p>"""),
      ("22.3", "从逐像素到掩码分类", """<p><strong>Mask R-CNN</strong> 在 Faster R-CNN 上加一个掩码分支，先检测实例再对每个框预测二值掩码，属于“先实例后像素”。<strong>Mask2Former</strong> 则把三类分割统一成<strong>掩码分类</strong>：用一组可学习 query 直接预测若干掩码及其类别，Transformer 解码器负责推理全局关系，不再逐像素独立判决。</p>
<p><strong>SAM / SAM 2</strong> 换了一个问题：不做固定类别，而是接受<strong>点、框、文本等提示</strong>，输出“提示所指的那个对象”的掩码。它把分割从封闭类别集推广为通用能力，非常适合作为<strong>标注加速器</strong>或流水线的前置模块；但它不自带语义标签，也不能保证在专业域（病理、遥感）上零样本可靠。</p>
<pre class="code" data-file="inline" data-lang="Shell"><code>pip install torch torchvision opencv-python
git clone https://github.com/facebookresearch/segment-anything.git
# 按仓库 README 下载 checkpoint 后运行官方 demo</code></pre>"""),
  ],
  repos=[
      ("mmsegmentation", "语义分割算法全家桶，配置文件化复现 FCN / DeepLab / Mask2Former"),
      ("unet-pytorch", "U-Net 的简洁可读实现，适合逐行对照跳跃连接"),
      ("fcn", "全卷积网络原始实现，理解从分类到稠密预测的改造"),
      ("mask2former", "统一语义/实例/全景分割的官方实现"),
      ("sam", "可提示分割基础模型，含官方 notebook 与权重"),
      ("sam2", "图像与视频统一的可提示分割，适合做标注加速"),
      ("monai", "医学影像分割框架，含 U-Net 与 Dice 评测的标准流程"),
      ("detectron2", "Mask R-CNN / 全景分割的官方实现"),
  ],
  repo_note="课程实验建议：同一数据集上对比 U-Net 与 DeepLab，除 mIoU 外额外报告边界附近的准确率。",
  pitfalls=["对标签图使用双线性插值：生成不存在的类别值。",
            "背景占 95% 时只报像素准确率：指标虚高。",
            "把 SAM 当成语义分割模型：它输出的是“提示对应的对象”，不带类别。",
            "忽略小目标：需单独报告小目标 IoU 与边界质量。"],
  exercises=["写出 Dice 与 IoU 的换算关系，并说明为什么 Dice 在极不平衡分割里更常用。",
             "设计一个用 SAM 辅助标注、再用 U-Net 训练的闭环流程，列出质检环节。"],
  further=["<a href='../../part2/12-segmentation/index.html'>第 12 章 传统图像分割</a>",
           "<a href='../21-object-detection/index.html'>第 21 章 目标检测</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 评测指标</a>"]),

C("23", "p4", "part4/23-deep-restoration", "深度复原与超分辨率",
  "上卷用维纳滤波写出显式先验，这里用数据学出先验：同一个病态逆问题，换了一种正则化方式。",
  hours="4 学时",
  goals=["能把深度复原重新表述为第 06 章的逆问题",
         "理解残差学习与噪声水平图的作用",
         "能对比 PSNR 导向与感知导向的超分模型",
         "能识别真实退化下的评价陷阱"],
  points=["病态逆问题与学习先验", "DnCNN 与残差去噪", "噪声水平图与非盲/盲去噪", "SRCNN / EDSR", "ESRGAN 与感知损失", "真实退化建模", "PSNR 与感知质量的分歧"],
  sections=[
      ("23.1", "从上卷到这里的同一条公式", """<p>第 06 章的退化模型 <code>g = h∗f + n</code> 依然成立，维纳滤波用<strong>功率谱比</strong>作为先验；深度方法把先验换成一个由数据学出的网络 <code>f̂ = R_θ(g)</code>，训练目标是最小化重建误差或感知距离。区别在于：维纳的先验是<strong>人写死的平稳性假设</strong>，网络的先验是<strong>训练图像分布的统计规律</strong>。因此网络在训练分布外（新传感器、新噪声类型）同样会失效，只是失效方式更难解释。</p>"""),
      ("23.2", "去噪与超分的代表性结构", """<table><thead><tr><th>任务</th><th>模型</th><th>要点</th></tr></thead><tbody>
<tr><td>高斯去噪</td><td>DnCNN / FFDNet</td><td>预测<strong>噪声残差</strong>而非干净图；批归一化 + 残差学习；FFDNet 把噪声水平图一起输入，一个模型覆盖多噪声强度</td></tr>
<tr><td>超分</td><td>SRCNN → EDSR</td><td>从三层卷积到去掉 BN 的深残差网络，优化 PSNR</td></tr>
<tr><td>感知超分</td><td>SRGAN / ESRGAN</td><td>加入对抗损失与 VGG 感知损失，生成更锐利的纹理</td></tr>
<tr><td>真实退化</td><td>Real-ESRGAN</td><td>用高阶退化建模（模糊、下采样、噪声、压缩多次叠加）合成训练对</td></tr>
</tbody></table>
<p><strong>关键矛盾</strong>：像素级损失（L1/MSE）会给出高 PSNR 但过度平滑的结果；对抗/感知损失视觉更锐利，却可能<strong> hallucinate </strong>出原本不存在的纹理。医学影像、遥感测量等场景必须优先保真，不能用感知导向模型直接出定量结论。</p>"""),
      ("23.3", "评价与落地", """<ul><li>有配对真值：PSNR / SSIM；无配对真实退化：无参考指标 + 人工评分 + 下游任务指标。</li>
<li>务必在<strong>真实退化</strong>数据上验证：只用双三次下采样合成的测试集，会系统性高估泛化能力。</li>
<li>与第 06 章的维纳滤波做对照实验：记录 PSNR、运行时间与“过度平滑”的主观评价。</li></ul>
<div class="card note"><p style="margin-bottom:0">这一章是上下卷结合最紧的地方：先用第 06 章的公式判断退化类型，再决定用维纳这样的可解释线性方法，还是用学习先验。工程上常把两者串联——传统方法做确定性校正，网络只学残差。</p></div>"""),
  ],
  repos=[
      ("dncnn", "残差去噪的经典官方实现，含不同噪声水平的训练脚本"),
      ("real-esrgan", "真实退化盲超分，提供可直接运行的推理与权重"),
      ("esrgan", "感知损失 + 对抗训练的超分原始实现，理解 PSNR/感知权衡"),
      ("hf-diffusers", "扩散先验用于复原与图像编辑的统一管线"),
      ("skimage-docs", "传统复原算子的参考实现，用来搭建对照基线"),
      ("torchmetrics", "PSNR / SSIM / LPIDS 等指标的统一实现，避免手写误差"),
  ],
  repo_note="复现路径：先用第 06 章的 <code>06-wiener.m</code> 生成退化图与 PSNR 基线，再跑 DnCNN 官方评测做同表对比。",
  pitfalls=["只报 PSNR 就说“更清晰”：感知导向模型常 PSNR 更低但视觉更好。",
            "只在双三次下采样测试集上评价超分：与真实退化差距很大。",
            "在医学/测量场景使用生成式超分：可能凭空生成纹理，影响诊断或计量。",
            "忽略噪声水平：非盲模型在训练范围外的噪声强度上会明显退化。"],
  exercises=["把维纳滤波的 <code>K</code> 与 DnCNN 的噪声水平图作类比，说明两者分别在注入什么先验。",
             "设计一个同时包含 PSNR、SSIM、人工评分与下游检测 mAP 的超分评价表，并说明各自回答什么问题。"],
  further=["<a href='../../part1/06-restoration/index.html'>第 6 章 图像复原与去噪（显式先验）</a>",
           "<a href='../24-generative-models/index.html'>第 24 章 生成模型（对抗与扩散先验）</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 评测指标</a>"]),

C("24", "p4", "part4/24-generative-models", "生成模型与图像翻译",
  "自编码器学压缩，GAN 学判别器看不见的真实性，扩散模型学逐步去噪：三条路线对应三种不同的概率建模方式。",
  hours="4 学时",
  goals=["能写出 VAE 的目标函数并说明重参数化的作用",
         "能解释 GAN 的极小极大目标与模式崩塌",
         "能描述 DDPM 前向/反向过程与潜空间扩散的动机",
         "能列出生成模型的评测方式与伦理风险"],
  points=["自编码器与 VAE", "ELBO 与重参数化", "GAN 极小极大博弈", "pix2pix / CycleGAN", "StyleGAN 与潜在空间", "DDPM 与扩散过程", "LDM / Stable Diffusion", "FID 与可控生成"],
  sections=[
      ("24.1", "VAE：把图像压进一个分布", """<p>自编码器把图像压成低维向量再重建，只能做插值，不能保证潜在空间连续可采样。<strong>VAE</strong> 让编码器输出分布参数 <code>(μ, σ)</code>，用<strong>重参数化技巧</strong> <code>z = μ + σ·ε</code> 使采样可导，优化证据下界：</p>
<span class="eq">L = E_q[log p(x|z)] − KL( q(z|x) ‖ p(z) )</span>
<p>第一项是重建质量，第二项把潜在分布拉向标准正态。VAE 采样稳定、覆盖模式较全，但结果常偏模糊。</p>"""),
      ("24.2", "GAN 与图像翻译", """<span class="eq">min_G max_D  E_x[log D(x)] + E_z[log(1 − D(G(z)))]</span>
<p>生成器与判别器做极小极大博弈，判别器逼生成器逼近真实图像分布。优势是样本锐利，代价是训练不稳定、<strong>模式崩塌</strong>（只生成少数几类）与难以覆盖全分布。</p>
<ul><li><strong>pix2pix</strong>：需要成对数据的条件图像翻译（边缘图 → 照片、掩模 → 立面）。</li>
<li><strong>CycleGAN</strong>：用循环一致性约束处理<strong>非配对</strong>数据（马 ↔ 斑马、风格迁移）。</li>
<li><strong>StyleGAN</strong>：把风格注入生成器的不同层级，得到可解释、可编辑的潜在方向。</li></ul>"""),
      ("24.3", "扩散模型", """<ol><li><strong>前向</strong>：按固定方差表逐步给图像加高斯噪声，直到接近纯噪声；任意时刻 <code>x_t</code> 有闭式表达。</li>
<li><strong>反向</strong>：训练一个去噪网络预测所加噪声，从 <code>x_T</code> 逐步还原 <code>x_0</code>。</li>
<li><strong>潜空间扩散（LDM）</strong>：先用 VAE 把图像压到低维潜空间再做扩散，算力骤降，这就是 Stable Diffusion 的核心。</li>
<li><strong>条件与引导</strong>：文本、边缘、深度图等条件 + classifier-free guidance 控制“贴合提示”与“多样性”的权衡。</li></ol>
<p>扩散模型训练稳定、覆盖度好，已成为图像生成与编辑的主流；采样慢是主要工程代价，需要蒸馏或更少步数的采样器。</p>
<pre class="code" data-file="inline" data-lang="Shell"><code>pip install diffusers transformers torch accelerate
python -c "from diffusers import DiffusionPipeline; print('diffusers ready')"</code></pre>"""),
      ("24.4", "评测与伦理", """<p><strong>FID</strong> 比较生成分布与真实分布在 Inception 特征空间的均值/协方差，<strong>CLIP Score</strong> 衡量图文对齐；二者都不等于“好看”，也都不能检测记忆化（把训练图背出来）。落地前必须考虑：训练数据版权、生成内容的标识、偏见放大、以及在医学/司法等场景误用合成图像的风险。</p>"""),
  ],
  repos=[
      ("cyclegan", "pix2pix 与 CycleGAN 官方实现，配对/非配对翻译的标准起点"),
      ("stylegan3", "高质量生成与潜在空间编辑的 NVIDIA 官方工程"),
      ("ddpm", "去噪扩散概率模型的原始实现，读训练目标最清楚"),
      ("stable-diffusion", "Stable Diffusion 原始仓库与权重"),
      ("latent-diffusion", "LDM 训练与条件生成代码，理解潜空间扩散"),
      ("hf-diffusers", "当前最完整的扩散推理/训练管线，含多种采样器与 LoRA"),
      ("gan-wiki", "GAN 的数学定义、变体与失效模式综述"),
      ("vae-wiki", "ELBO 与重参数化的推导条目"),
  ],
  repo_note="建议练习：用 diffusers 固定随机种子生成一组图，改 guidance scale 观察“贴合提示 vs 多样性”的变化。",
  pitfalls=["把 FID 数值跨论文直接比较：采样量与特征网络可能不同。",
            "忽视模式崩塌：GAN 生成的样本很锐利，但可能只覆盖少数模式。",
            "在需要保真的场景用生成式模型：细节可能是“编”出来的（第 23 章）。",
            "不检查训练数据与权重许可：生成模型的版权风险高于判别模型。"],
  exercises=["推导 VAE 的 ELBO，说明 KL 项为什么能防止潜在空间出现“空洞”。",
             "写出 DDPM 前向 <code>q(x_t|x_0)</code> 的闭式形式，并解释为什么训练时可以直接采样任意 t。"],
  further=["<a href='../23-deep-restoration/index.html'>第 23 章 深度复原（生成先验的另一面）</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 FID 与评测</a>",
           "<a href='../25-vision-transformers/index.html'>第 25 章 基础模型与多模态</a>"]),

C("25", "p4", "part4/25-vision-transformers", "视觉 Transformer 与基础模型",
  "把卷积的归纳偏置换成注意力 + 大规模预训练：模型更通用，也更依赖数据与算力。",
  hours="4 学时",
  goals=["能写出 ViT 的 patch embedding 与自注意力计算形式",
         "能对比 CNN 与 ViT 的归纳偏置及数据需求",
         "说清 MAE / DINOv2 / CLIP 三类预训练目标",
         "能列出基础模型迁移的三种低成本方式"],
  points=["patch embedding", "自注意力与复杂度", "位置编码", "ViT vs CNN 归纳偏置", "Swin 层级化窗口注意力", "MAE / DINOv2 自监督", "CLIP 图文对比", "Prompt / Adapter / LoRA"],
  sections=[
      ("25.1", "ViT：把图像当词序列", """<p>把图像切成固定大小 patch（如 16×16），每个 patch 线性投影成一个 token，加上位置编码与类别 token，送入标准 Transformer 编码器：</p>
<span class="eq">Attention(Q,K,V) = softmax(QKᵀ/√d) · V，　token 数 = (H/P)·(W/P)</span>
<p>自注意力是<strong>全局、内容自适应</strong>的：任意两个 patch 一步就能交互；代价是复杂度随 token 数平方增长（高分辨率图很贵），且<strong>缺少 CNN 的局部性与平移等变性</strong>这些先验，需要更大规模数据才能学到同等表示。</p>"""),
      ("25.2", "效率与自监督", """<ul><li><strong>Swin</strong>：在局部窗口内做注意力，用移位窗口跨窗口交互，得到层级化多尺度特征，可直接接检测/分割头。</li>
<li><strong>MAE</strong>：随机遮住大部分 patch，让模型重建被遮内容，用<strong>重建目标</strong>学表示。</li>
<li><strong>DINOv2</strong>：自蒸馏式的自监督，产出无需微调就很好用的<strong>通用冻结特征</strong>，适合迁移到专业域（第 18 章）。</li></ul>
<p>自监督的意义在于：标注昂贵而无标注图像海量。它把“先预训练再迁移”从 ImageNet 标签中解放出来。</p>"""),
      ("25.3", "图文对齐与基础模型", """<p><strong>CLIP</strong> 用对比学习把图像编码器与文本编码器对齐到同一空间，于是分类可以写成“图像与哪个文本提示最相似”，得到<strong>零样本分类</strong>与开放词表能力（第 21 章的 GroundingDINO 就建立在这类对齐之上）。<strong>视觉语言模型</strong>（LLaVA 等）进一步把视觉 token 接进大语言模型，实现读图问答与推理。</p>
<table><thead><tr><th>迁移方式</th><th>改什么</th><th>成本</th></tr></thead><tbody>
<tr><td>提示工程</td><td>只改文本提示 / 示例</td><td>最低，先做这个</td></tr>
<tr><td>Adapter / 线性探针</td><td>冻结骨干，训练小模块</td><td>低，适合小样本</td></tr>
<tr><td>LoRA / 部分微调</td><td>低秩增量或后几层</td><td>中，适合领域适配</td></tr>
</tbody></table>"""),
  ],
  repos=[
      ("vit", "Google 官方 ViT 实现与预训练权重"),
      ("swin", "Swin Transformer 官方实现，含检测/分割下游配置"),
      ("mae", "掩码自编码预训练官方代码，可复现重建式自监督"),
      ("dinov2", "通用视觉特征，冻结即可用于检索/分割/迁移"),
      ("clip", "OpenAI 官方 CLIP，零样本分类与图文相似度"),
      ("open-clip", "开源复现与更大规模预训练权重"),
      ("llava", "视觉语言对话模型，体验读图问答"),
      ("hf-transformers", "统一调用上述模型的接口与权重"),
      ("sam", "可提示分割基础模型，理解“提示即任务定义”的范式"),
  ],
  repo_note="建议实验：同一批图像分别用 ResNet 与 DINOv2 提特征做 kNN 分类，直观比较冻结特征质量。",
  pitfalls=["把 ViT 直接用于高分辨率密集任务：token 数平方增长会爆显存。",
            "小数据集从头训 ViT：缺少归纳偏置，通常不如预训练 CNN。",
            "把 CLIP 零样本分数当校准概率：文本提示措辞会显著影响结果。",
            "忽略基础模型的训练数据偏差：下游可能放大特定人群/场景的误差。"],
  exercises=["计算 <code>224×224</code> 输入、<code>16×16</code> patch 的 token 数，并估算自注意力矩阵的元素数。",
             "比较 MAE 与 DINOv2 的自监督目标，说明为什么二者学出的特征用途不同。"],
  further=["<a href='../../part3/18-cnn-architectures/index.html'>第 18 章 CNN 骨干与迁移学习</a>",
           "<a href='../24-generative-models/index.html'>第 24 章 文生图中的文本编码</a>",
           "<a href='../26-projects/index.html'>第 26 章 工程落地与综合项目</a>"]),

C("26", "p4", "part4/26-projects", "工程落地与综合项目",
  "把模型变成可维护的系统：导出、加速、压缩、数据闭环，以及一个必须与传统基线同台对比的课程设计。",
  hours="4 学时",
  goals=["能画出训练到部署的完整链路与各环节产物",
         "能区分 PTQ 与 QAT、剪枝与蒸馏",
         "能设计标注质检、版本管理与线上回归方案",
         "能完成传统基线 vs 深度基线的对比实验报告"],
  points=["训练到部署链路", "ONNX 与算子兼容", "推理引擎选型", "量化 PTQ / QAT", "剪枝与蒸馏", "标注质检与数据版本", "监控与回归测试", "传统基线 vs 深度基线", "伦理与偏差"],
  sections=[
      ("26.1", "部署链路与压缩", """<ol><li><strong>导出</strong>：PyTorch → ONNX（注意动态轴、算子兼容、自定义算子）；或直接用 TorchScript / 引擎原生格式。</li>
<li><strong>选引擎</strong>：服务端 GPU 用 TensorRT，跨平台 CPU/GPU 用 ONNX Runtime，Intel 边缘用 OpenVINO，移动端用 ncnn / TFLite。</li>
<li><strong>压缩</strong>：PTQ（训练后量化，需校准集）快但可能掉点；QAT（量化感知训练）更稳但需重训；结构化剪枝减通道，蒸馏把大模型能力迁到小模型。</li>
<li><strong>验证</strong>：逐层比对浮点与量化输出、测 P50/P99 时延与内存峰值、在目标硬件上而非开发机上验收。</li></ol>
<pre class="code" data-file="inline" data-lang="Shell"><code>pip install onnx onnxruntime onnxsim
python -c "import onnx, onnxruntime; print(onnx.__version__, onnxruntime.__version__)"</code></pre>"""),
      ("26.2", "数据闭环", """<p>上线不是终点。一个可维护的视觉系统需要：标注规范与抽检（CVAT / Label Studio）→ 数据集版本化 → 训练/评测脚本版本化 → 难例回流 → 定期回归测试集 → 线上分布漂移监控。<strong>回归测试集</strong>应包含历史出错样本与关键切片，每次发版都跑，防止“改 A 坏 B”。</p>
<div class="card warn"><p style="margin-bottom:0">最常见的事故不是模型不准，而是<strong>预处理不一致</strong>：训练用 RGB + 归一化为 [0,1]，部署用 BGR + 0～255；或训练与推理的 resize / padding 策略不同。务必把预处理写进同一份配置并与模型一起导出。</p></div>"""),
      ("26.3", "综合课程设计：两条基线同台", """<p>题目（与<a href="../../part2/15-classical-pipeline/index.html">第 15 章</a>完全相同的颗粒计数任务）要求交付两份实现：</p>
<table><thead><tr><th>维度</th><th>传统基线</th><th>深度基线</th></tr></thead><tbody>
<tr><td>实现</td><td>第 15 章 Octave 流水线</td><td>U-Net / YOLO 实例分割（任选其一）</td></tr>
<tr><td>数据需求</td><td>一张图 + 少量调参</td><td>标注集、划分文件、训练脚本</td></tr>
<tr><td>可解释性</td><td>每步可写公式、参数有物理含义</td><td>需消融与热力图</td></tr>
<tr><td>失效方式</td><td>光照/粘连/噪声破坏假设</td><td>分布外、标注偏差</td></tr>
<tr><td>工程成本</td><td>零依赖、CPU 秒级</td><td>GPU、权重管理、部署链路</td></tr>
</tbody></table>
<p><strong>报告必须回答</strong>：哪些环节值得换成网络？换成网络后，可解释性、数据成本与维护成本各增加了多少？给出定量对比表（计数误差、面积误差、推理时延、标注工时、代码行数），而不是只给一句“深度学习更准”。</p>"""),
      ("26.4", "伦理、偏差与交付清单", """<ul><li>标注与训练数据的<strong>人群/场景覆盖</strong>是否均衡，关键切片指标是否单独报告；</li>
<li>出错时的<strong>降级策略</strong>（低置信度转人工、规则兜底）；</li>
<li>模型权重、数据集、预处理配置、随机种子与评测脚本是否齐全；</li>
<li>外部依赖的许可证与数据来源是否合规；</li>
<li>是否存在会误导下游的“看起来更好”的指标（第 19、23 章）。</li></ul>"""),
  ],
  repos=[
      ("onnx", "跨框架交换格式，导出训练模型的第一站"),
      ("onnxruntime", "跨平台推理引擎，含量化工具与性能分析"),
      ("tensorrt", "NVIDIA GPU 推理优化与 INT8 量化"),
      ("openvino", "Intel CPU/iGPU 部署优化"),
      ("ncnn", "移动端轻量推理框架，无第三方依赖"),
      ("cvat", "标注与质检平台，支持难例回流"),
      ("labelstudio", "通用标注与审核流程"),
      ("ultralytics", "一行命令导出 ONNX / TensorRT，适合做端到端链路演示"),
      ("torchmetrics", "发版回归测试中的统一指标实现"),
  ],
  repo_note="交付物清单：两份可运行实现、一份对比表、一个回归测试集、一条一键重跑命令。",
  pitfalls=["只在开发机上测时延：目标硬件的内存与算子支持可能完全不同。",
            "训练与推理预处理不一致：最常见、最隐蔽的线上精度事故。",
            "没有回归测试集：每次优化都可能悄悄破坏旧场景。",
            "只比精度不比标注工时与维护成本：结论对工程决策没有价值。"],
  exercises=["为第 15 章的颗粒计数任务写一份两基线对比实验计划，包含数据划分、指标、消融与交付物。",
             "列出导出 ONNX 后需要逐项核对的 5 件事（含预处理与动态轴）。"],
  further=["<a href='../../part2/15-classical-pipeline/index.html'>第 15 章 传统算法综合实验（同任务基线）</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 评测与可复现清单</a>",
           "<a href='../../appendix/index.html'>附录 A 速查与资源总表</a>"]),

C("A", "pa", "appendix", "附录 · 速查与资源总表",
  "Octave 函数索引、传统算法速查、术语对照、调试清单与全书开源工程/扩展链接总表。",
  hours="按需查阅",
  goals=["能快速查到某个传统算法对应的 Octave 核心函数与章节",
         "能按任务找到官方开源工程",
         "能按调试清单定位 Octave 代码运行异常",
         "知道如何为本书补充内容"],
  points=["Octave 核心函数速查", "传统算法速查表", "开源工程总表", "术语中英对照", "常见错误与调试", "参考教材与课程", "扩展学习链接总表"],
  sections=[
      ("A.1", "Octave 核心函数速查", """<p>本书示例只使用下表的核心函数，<strong>不需要安装 image 包</strong>。文件一律 UTF-8 编码，图像统一为 <code>double</code> 型 <code>[0,1]</code> 矩阵。</p>
<table><thead><tr><th>类别</th><th>函数</th><th>用途 / 章节</th></tr></thead><tbody>
<tr><td>造图</td><td><code>meshgrid</code>, <code>zeros</code>, <code>ones</code>, <code>linspace</code>, <code>repmat</code></td><td>合成测试图像与掩模（01）</td></tr>
<tr><td>随机</td><td><code>rand</code>, <code>randn</code>, <code>rand("seed",…)</code></td><td>噪声注入与可复现（01、06）</td></tr>
<tr><td>滤波</td><td><code>conv2</code>, <code>fft2</code>, <code>ifft2</code>, <code>fftshift</code>, <code>ifftshift</code></td><td>空域/频域滤波（04、05、06）</td></tr>
<tr><td>插值</td><td><code>interp1</code>, <code>interp2</code>, <code>circshift</code></td><td>LUT 映射、几何变换（03、07）</td></tr>
<tr><td>统计</td><td><code>mean</code>, <code>std</code>, <code>min</code>, <code>max</code>, <code>cumsum</code>, <code>median</code>, <code>sum</code>, <code>histc</code></td><td>直方图、矩、评价指标（02、12、13）</td></tr>
<tr><td>显示</td><td><code>imagesc</code>, <code>colormap gray</code>, <code>axis image off</code>, <code>subplot</code>, <code>plot</code>, <code>bar</code>, <code>colorbar</code></td><td>可视化（全书）</td></tr>
<tr><td>输出</td><td><code>printf</code>, <code>disp</code>, <code>getenv</code>, <code>strcmp</code></td><td>数值验证与 headless 控制（全书）</td></tr>
</tbody></table>
<pre class="code" data-file="inline" data-lang="Shell"><code>octave --no-gui --quiet code/A-template.m          # 交互运行单个脚本
IP_HEADLESS=1 ./tools/run_octave.sh                 # 批量验证全书示例</code></pre>"""),
      ("A.2", "传统算法速查表", """<table><thead><tr><th>任务</th><th>核心公式 / 结构</th><th>关键参数</th><th>章节</th></tr></thead><tbody>
<tr><td>灰度变换</td><td><code>g = f^γ</code>、<code>g = c·log(1+f)</code></td><td>γ</td><td>03</td></tr>
<tr><td>直方图均衡</td><td><code>s_k = Σ_{j≤k} n_j/(MN)</code></td><td>灰度级数</td><td>03</td></tr>
<tr><td>线性滤波</td><td><code>g = conv2(f, w, "same")</code></td><td>核尺寸、σ</td><td>04</td></tr>
<tr><td>中值滤波</td><td>邻域排序取中位</td><td>窗口尺寸</td><td>04</td></tr>
<tr><td>锐化</td><td><code>f + λ∇²f</code>、USM</td><td>λ</td><td>04</td></tr>
<tr><td>频域滤波</td><td><code>real(ifft2(H·fft2(f)))</code></td><td>D₀、阶数 n</td><td>05</td></tr>
<tr><td>维纳复原</td><td><code>H*/(|H|²+K)·G</code></td><td>K</td><td>06</td></tr>
<tr><td>几何变换</td><td><code>T⁻¹</code> 反向映射 + 插值</td><td>θ、插值方式</td><td>07</td></tr>
<tr><td>色彩空间</td><td><code>Y=0.299R+0.587G+0.114B</code>、HSV</td><td>S 阈值</td><td>08</td></tr>
<tr><td>形态学</td><td>开 <code>(A⊖B)⊕B</code>、闭 <code>(A⊕B)⊖B</code></td><td>结构元素</td><td>09</td></tr>
<tr><td>边缘</td><td>Sobel + NMS + 双阈值</td><td>σ、Th、Tl</td><td>10</td></tr>
<tr><td>角点</td><td><code>R = det(M) − k·trace(M)²</code></td><td>k、窗口</td><td>11</td></tr>
<tr><td>Otsu</td><td><code>max w₀w₁(μ₀−μ₁)²</code></td><td>灰度级数</td><td>12</td></tr>
<tr><td>纹理</td><td>LBP 编码直方图、GLCM</td><td>半径、方向</td><td>13</td></tr>
<tr><td>JPEG</td><td><code>T·B·Tᵀ</code> + 量化表 Q</td><td>qscale</td><td>14</td></tr>
<tr><td>评价</td><td><code>MSE</code>、<code>PSNR=10log10(1/MSE)</code>、SSIM</td><td>L=1</td><td>02</td></tr>
</tbody></table>"""),
      ("A.4", "术语中英对照", """<table><thead><tr><th>中文</th><th>English</th><th>中文</th><th>English</th></tr></thead><tbody>
<tr><td>卷积</td><td>convolution</td><td>直方图均衡</td><td>histogram equalization</td></tr>
<tr><td>点扩散函数</td><td>point spread function</td><td>维纳滤波</td><td>Wiener filter</td></tr>
<tr><td>傅里叶变换</td><td>Fourier transform</td><td>离散余弦变换</td><td>discrete cosine transform</td></tr>
<tr><td>腐蚀 / 膨胀</td><td>erosion / dilation</td><td>分水岭</td><td>watershed</td></tr>
<tr><td>边缘检测</td><td>edge detection</td><td>非极大抑制</td><td>non-maximum suppression</td></tr>
<tr><td>尺度不变特征</td><td>SIFT</td><td>随机一致性采样</td><td>RANSAC</td></tr>
<tr><td>阈值分割</td><td>thresholding</td><td>活动轮廓</td><td>active contour</td></tr>
<tr><td>感受野</td><td>receptive field</td><td>反向传播</td><td>backpropagation</td></tr>
<tr><td>残差连接</td><td>residual connection</td><td>迁移学习</td><td>transfer learning</td></tr>
<tr><td>交并比</td><td>IoU</td><td>平均精度均值</td><td>mAP</td></tr>
<tr><td>语义分割</td><td>semantic segmentation</td><td>实例分割</td><td>instance segmentation</td></tr>
<tr><td>超分辨率</td><td>super-resolution</td><td>感知损失</td><td>perceptual loss</td></tr>
<tr><td>扩散模型</td><td>diffusion model</td><td>自监督学习</td><td>self-supervised learning</td></tr>
<tr><td>基础模型</td><td>foundation model</td><td>量化感知训练</td><td>QAT</td></tr>
</tbody></table>"""),
      ("A.5", "常见错误与调试清单", """<ol><li><strong>下标越界 / 尺寸不匹配</strong>：先 <code>whos</code> 看维度；<code>conv2(...,"valid")</code> 会缩小输出。</li>
<li><strong>全白或全黑</strong>：检查是否忘了 <code>min(max(a,0),1)</code>，以及 <code>imagesc(a,[0 1])</code> 的固定范围。</li>
<li><strong>uint8 饱和</strong>：所有运算前先 <code>double(a)/255</code>。</li>
<li><strong>结果整体偏移</strong>：频域忘了 <code>fftshift/ifftshift</code> 配对；或核尺寸为偶数。</li>
<li><strong>滤波后边缘发暗</strong>：补零边界导致，改用 replicate / symmetric 填充。</li>
<li><strong>几何变换镜像/转置</strong>：<code>(r,c)</code> 与 <code>(x,y)</code> 顺序写反。</li>
<li><strong>两次运行结果不同</strong>：没有固定 <code>rand/randn</code> 种子。</li>
<li><strong>掩模出现小数标签</strong>：对整数标签图用了双线性插值。</li>
<li><strong>headless 报错</strong>：设 <code>IP_HEADLESS=1</code> 跳过绘图；或检查 Octave 图形后端。</li></ol>"""),
      ("A.6", "参考教材与在线课程", """<ul><li><strong>传统算法</strong>：Gonzalez &amp; Woods《Digital Image Processing》；scikit-image User Guide 与 OpenCV Tutorials 作为可运行参考。</li>
<li><strong>深度学习与视觉</strong>：Stanford <a href="https://cs231n.github.io/" target="_blank" rel="noopener">CS231n</a>、<a href="https://d2l.ai/" target="_blank" rel="noopener">动手学深度学习</a>、<a href="https://pytorch.org/tutorials/" target="_blank" rel="noopener">PyTorch Tutorials</a>。</li>
<li><strong>论文与代码</strong>：<a href="https://paperswithcode.com/" target="_blank" rel="noopener">Papers with Code</a> 按任务查 SOTA 与官方仓库；<a href="https://arxiv.org/" target="_blank" rel="noopener">arXiv</a> 读原文。</li>
<li><strong>工具</strong>：<a href="https://docs.octave.org/latest/" target="_blank" rel="noopener">Octave 官方文档</a>、<a href="https://imagej.net/" target="_blank" rel="noopener">ImageJ / Fiji</a> 用于人工核对测量结果。</li></ul>
<div class="card tip"><p style="margin-bottom:0"><strong>维护约定</strong>：全书由 <code>tools/chapters_*.py</code>（章节内容）、<code>tools/book_resources.py</code>（链接库）、<code>tools/build_book.py</code>（渲染器）单一数据源生成。修改后依次运行 <code>python3 tools/build_book.py --force</code>、<code>python3 tools/extract_code.py</code>、<code>python3 tools/check_book.py</code>。</p></div>"""),
  ],
  demos=[
      demo("code/A-template.m", "新建实验的最小模板（复制后改参数区与算法段）", r"""%% A-template.m | 本书所有 Octave 示例的模板
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
end""",
            "以此文件为起点新建实验：只改参数区与算法段，保留数值验证与 headless 开关。",
            "平滑后均值基本不变（核和为 1）、MSE 下降；设置 <code>IP_HEADLESS=1</code> 时不弹窗但数值照常打印。"),
  ],
  pitfalls=["直接编辑 HTML 而不改数据源：下次 <code>--force</code> 重建会被覆盖。",
            "新增示例后忘了运行 <code>extract_code.py</code>：页面有代码块但磁盘缺少 <code>.m</code>。",
            "在示例里引入 image 包专有函数：破坏零依赖约定。"],
  exercises=["用 A-template.m 复现第 04 章的高斯平滑实验，并补一行 PSNR 打印。",
             "按维护约定新增一个章节，说明需要同时改动哪几个文件。"],
  further=["<a href='../index.html'>返回总目录</a>",
           "<a href='../index.html#resources'>全书参考资源总表</a>",
           "<a href='../part0/01-octave-setup/index.html'>第 1 章 Octave 环境与代码契约</a>"]),

]
