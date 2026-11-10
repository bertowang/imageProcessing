#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下卷 16-21：从手工特征到学习、CNN 基础、骨干网络、数据集评测、分类可解释性、目标检测。

下卷不提供本地可运行的算法代码：每章以原理主线 + 官方开源工程链接为输出物，
配合「快速开始」命令行片段，便于读者直接 clone 官方仓库复现。
"""
from book_schema import C

CH = [

C("16", "p3", "part3/16-learning-baselines", "从手工特征到学习",
  "上卷把图像变成特征向量，这一章把它们送进分类器：先建立可解释的传统基线，再说明它为什么会被表示学习取代。",
  hours="3 学时",
  goals=["能说清 BoVW / VLAD 如何把局部描述子汇成全局向量",
         "能为给定任务选择 SVM、随机森林或 kNN 并说明理由",
         "能设计交叉验证与类别不平衡的处理方案",
         "能解释语义鸿沟与维度灾难，指出表示学习的切入点"],
  points=["特征工程与 BoVW", "VLAD / Fisher Vector", "SVM 与核方法", "随机森林与 kNN", "偏差-方差与交叉验证", "类别不平衡", "语义鸿沟"],
  sections=[
      ("16.1", "把局部特征汇成全局向量", """<p>第 11、13 章给出的 SIFT、LBP、Hu 矩是<strong>局部或单个目标</strong>的描述，而分类需要整幅图一个定长向量。经典做法是<strong>视觉词袋（BoVW）</strong>：</p>
<ol><li>从训练图提取大量局部描述子，k-means 聚成 K 个“视觉单词”（码本）。</li>
<li>每张图的描述子量化到最近单词，统计词频直方图（常加 TF-IDF 加权）。</li>
<li>用直方图训练分类器。</li></ol>
<p><strong>VLAD</strong> 记录每个描述子相对聚类中心的残差之和，<strong>Fisher Vector</strong> 用高斯混合模型的梯度表示，二者保留了比词频更丰富的信息，在深度学习普及前是图像检索与分类的 SOTA。</p>"""),
      ("16.2", "分类器与偏差-方差", """<table><thead><tr><th>分类器</th><th>假设</th><th>何时用</th></tr></thead><tbody>
<tr><td>SVM（RBF 核）</td><td>存在最大间隔超平面</td><td>样本不多、特征维度中等；需调 C 与 γ</td></tr>
<tr><td>随机森林</td><td>特征可轴对齐划分</td><td>混合类型特征、需要特征重要度、抗过拟合</td></tr>
<tr><td>kNN</td><td>同类样本在特征空间邻近</td><td>作为最简单基线；高维时距离失效</td></tr>
<tr><td>Logistic 回归</td><td>线性可分</td><td>必须有的下限基线，训练极快</td></tr>
</tbody></table>
<p>模型复杂度与泛化误差的关系仍是<strong>偏差-方差分解</strong>：容量太小欠拟合，太大过拟合，正则化与交叉验证是在两者间找位置。类别不平衡时要改看 PR 曲线、F1 与每类召回，而不是只看总体准确率。</p>"""),
      ("16.3", "为什么必须走向表示学习", """<ul><li><strong>语义鸿沟</strong>：像素/梯度统计与“这是一只猫”之间没有可写的映射规则。</li>
<li><strong>特征不可训练</strong>：BoVW 的码本、SIFT 的描述子都是人定的，任务一变就得重新设计。</li>
<li><strong>维度灾难</strong>：手工拼接的高维特征在有限样本下距离度量失效。</li>
<li><strong>端到端</strong>：让特征提取器与分类器一起由损失驱动优化，是 CNN 最本质的改变。</li></ul>
<div class="card tip"><p style="margin-bottom:0"><strong>工程建议</strong>：即使最终要用深度网络，也先花半小时跑一个 HoG/LBP + 线性 SVM 的传统基线。它给出了下限、暴露了数据问题，并让后续提升可归因——这正是第 26 章综合项目的要求。</p></div>
<pre class="code" data-file="inline" data-lang="Shell"><code>pip install scikit-learn scikit-image
python -c "import sklearn, skimage; print(sklearn.__version__, skimage.__version__)"</code></pre>"""),
  ],
  repos=[
      ("scikit-learn", "直接用 <code>SVC</code>/<code>RandomForestClassifier</code> 复现 16.2 的对照实验"),
      ("opencv", "官方 <code>SIFT_create</code> 等特征实现，用来产出 BoVW 的输入描述子"),
      ("skimage", "LBP、HOG、GLCM 等手工特征的可靠实现，对照第 13 章"),
      ("cs231n", "从线性分类、SVM 到反向传播的连贯讲义，补齐本章到下一章的过渡"),
      ("d2l", "含可运行代码的机器学习与深度学习教材"),
      ("paperswithcode", "查“图像分类 + 传统特征”的历史基线与后续 SOTA"),
  ],
  repo_note="本章不需要 GPU：把第 15 章流水线的输出特征导出成 CSV，即可用 scikit-learn 完成全套基线实验。",
  pitfalls=["跳过传统基线直接上深度模型：无法判断提升来自模型还是来自数据清洗。",
            "在测试集上做 k-means 码本或特征选择：数据泄漏，指标虚高。",
            "用准确率评价 1:99 的不平衡数据：全预测多数类就有 99%。",
            "把高维手工特征直接喂 kNN：距离集中，分类接近随机。"],
  exercises=["用第 13 章的 LBP 直方图 + 线性 SVM 设计一个三分类任务，写出完整交叉验证方案。",
             "解释 BoVW 与词袋模型在 NLP 中的对应关系，并指出图像侧多出来的“量化误差”来自哪里。"],
  further=["<a href='../../part2/11-features/index.html'>第 11 章 局部特征与描述</a>",
           "<a href='../../part2/13-descriptors/index.html'>第 13 章 表示、描述与纹理</a>",
           "<a href='../17-cnn-fundamentals/index.html'>第 17 章 神经网络与 CNN 基础</a>"]),

C("17", "p3", "part3/17-cnn-fundamentals", "神经网络与 CNN 基础",
  "卷积层只是带权值共享的线性层；真正让深度网络可训练的是反向传播、归一化与一整套训练配方。",
  hours="4 学时",
  goals=["能写出卷积层输出尺寸与参数量公式",
         "能解释局部连接、权值共享与感受野的递进关系",
         "能说清反向传播、损失函数与优化器各自的角色",
         "能列出一个最小训练循环必备的六个步骤"],
  points=["神经元与激活函数", "卷积层与感受野", "池化与下采样", "反向传播与自动微分", "损失函数与优化器", "批归一化与 Dropout", "数据增强与正则"],
  sections=[
      ("17.1", "卷积层：把全连接变成局部共享", """<p>一个 <code>M×N</code> 图像若接全连接层，参数量是 <code>M·N·C</code>；卷积层改用 <code>K×K</code> 的小核在整幅图上滑动，参数量只有 <code>K²·C_in·C_out</code>，与图像尺寸无关。三个归纳偏置：<strong>局部性</strong>（像素主要与邻域相关）、<strong>平移等变性</strong>（同一核扫全图）、<strong>层次组合</strong>（边缘 → 纹理 → 部件 → 物体）。</p>
<span class="eq">H_out = ⌊(H_in + 2P − D(K−1) − 1)/S + 1⌋，　参数量 = K²·C_in·C_out + C_out</span>
<p>其中 P 是填充、S 是步长、D 是空洞率。第一层学到的常是<strong>类似 Gabor / Sobel 的定向边缘滤波器</strong>——第 10 章手工设计的核，被数据自动学了出来；<a href="../../part1/04-spatial-filter/index.html">第 4 章</a>与 <code>Kornia</code> 库可以把这两者放在同一段代码里对照。</p>"""),
      ("17.2", "训练：损失、反向传播与优化器", """<ol><li>前向计算得到预测 <code>ŷ</code>；</li>
<li>算损失（分类用交叉熵、回归用 L1/L2、检测用分类+框回归的组合）；</li>
<li><code>loss.backward()</code> 用链式法则回传梯度（自动微分）；</li>
<li>优化器更新参数（SGD+momentum 或 AdamW）；</li>
<li><code>zero_grad</code> → 下一步；重复直到收敛。</li></ol>
<p><strong>批归一化</strong>让每层输入分布稳定，从而允许更大学习率；<strong>Dropout</strong>随机失活抑制共适应；<strong>权重初始化</strong>与<strong>残差连接</strong>（第 18 章）共同解决深层梯度消失。注意 BN 在训练与推理时用不同统计量，<code>model.eval()</code> 忘了调是线上结果异常的常见原因。</p>"""),
      ("17.3", "数据增强与正则", """<p>增强是<strong>标签保持变换</strong>：随机裁剪、翻转、旋转、颜色抖动、MixUp/CutMix。它们把上卷的几何变换（第 07 章）、彩色变换（第 08 章）、滤波（第 04 章）变成了可微流水线里的随机层。关键约束是<strong>框、掩模、关键点必须与图像同步变换</strong>，否则标注错位；<code>Albumentations</code> 就是为此设计的。</p>
<div class="card warn"><p style="margin-bottom:0">增强不是越多越好：医学影像里的左右翻转可能改变标签语义，字符识别里的旋转会把 6 变成 9。先验写错了，数据再多也学不回来。</p></div>"""),
  ],
  repos=[
      ("pytorch", "框架本体；<code>autograd</code> 是理解反向传播最直接的参考实现"),
      ("pytorch-tutorials", "官方 60 分钟入门与训练循环示例，照抄一遍即可跑通本章六步"),
      ("d2l", "从零实现卷积、BN、优化器的可运行代码，适合逐行对照公式"),
      ("cs231n", "反向传播、卷积可视化与训练技巧的经典讲义"),
      ("kornia", "可微分传统 CV 算子：把第 4～10 章的算子接进网络"),
      ("albumentations", "图像/框/掩模同步增强，避免几何增强造成标注错位"),
  ],
  repo_note="最小复现路径：先跑官方 MNIST 训练教程，再把网络第一层卷积核可视化，与上卷 Sobel 核对比。",
  pitfalls=["把 <code>model.eval()</code> 忘在推理路径上：BN/Dropout 仍用训练行为，结果不稳定。",
            "增强只作用于图像不同步标注：检测框与分割掩模全部错位。",
            "认为更大的学习率总是更快收敛：批归一化也救不了发散的初始阶段。",
            "把测试集当验证集反复调参：等于在测试集上训练。"],
  exercises=["推导 <code>3×3</code> 卷积、<code>stride=1, pad=1</code> 时的输出尺寸与参数量，并说明为什么参数量与图像分辨率无关。",
             "列出训练循环六步，标注每一步对应的数学对象（前向/损失/梯度/更新）。"],
  further=["<a href='../16-learning-baselines/index.html'>第 16 章 从手工特征到学习</a>",
           "<a href='../18-cnn-architectures/index.html'>第 18 章 经典 CNN 架构与迁移学习</a>",
           "<a href='../../part1/04-spatial-filter/index.html'>第 4 章 空间域滤波（卷积核的原型）</a>"]),

C("18", "p3", "part3/18-cnn-architectures", "经典 CNN 架构与迁移学习",
  "从 LeNet 到 ConvNeXt 是一条不断回答“怎样堆得更深、更省、更好训练”的路线；迁移学习让这些骨干能用在小数据集上。",
  hours="4 学时",
  goals=["能按时间顺序说出骨干网络的关键创新",
         "能解释残差连接为什么改善深层优化",
         "能区分特征提取与微调两种迁移方式",
         "能根据精度/延迟/显存约束选择骨干"],
  points=["LeNet / AlexNet / VGG", "Inception 与多尺度", "ResNet 与残差连接", "DenseNet / EfficientNet", "ConvNeXt 与现代训练法", "特征提取 vs 微调", "预训练权重与领域差距"],
  sections=[
      ("18.1", "骨干演进的关键节点", """<table><thead><tr><th>年份</th><th>网络</th><th>关键思想</th></tr></thead><tbody>
<tr><td>1998</td><td>LeNet-5</td><td>卷积 + 池化 + 全连接的雏形，手写数字识别</td></tr>
<tr><td>2012</td><td>AlexNet</td><td>ReLU、Dropout、GPU 训练、大规模数据增强</td></tr>
<tr><td>2014</td><td>VGG</td><td>全部用 3×3 小核堆叠，结构规整、参数量大</td></tr>
<tr><td>2014</td><td>GoogLeNet</td><td>Inception 多分支多尺度 + 1×1 降维</td></tr>
<tr><td>2015</td><td>ResNet</td><td>残差连接，首次稳定训练上百层</td></tr>
<tr><td>2017</td><td>DenseNet</td><td>层间密集复用特征，参数更省</td></tr>
<tr><td>2019</td><td>EfficientNet</td><td>复合缩放深度/宽度/分辨率，用 NAS 定系数</td></tr>
<tr><td>2022</td><td>ConvNeXt</td><td>用 ViT 时代的训练配方重训纯卷积，证明架构不是唯一变量</td></tr>
</tbody></table>"""),
      ("18.2", "残差连接", """<span class="eq">y = F(x, {Wᵢ}) + x，　∂L/∂x = ∂L/∂y · (1 + ∂F/∂x)</span>
<p>恒等旁路给梯度提供了一条<strong>不经过任何权重</strong>的通路，即使 <code>∂F/∂x</code> 很小，梯度也不会连乘消失。它同时把学习目标从“学一个完整映射”改成“学相对恒等的残差”，优化地形更平滑。这一思想后来被 Transformer 的残差 + LayerNorm 原样继承（第 25 章）。</p>"""),
      ("18.3", "迁移学习的两种用法", """<table><thead><tr><th>方式</th><th>做法</th><th>适合</th></tr></thead><tbody>
<tr><td>特征提取</td><td>冻结骨干，只训练新的分类头</td><td>数据很少、算力有限、领域接近预训练集</td></tr>
<tr><td>微调</td><td>解冻全部或部分层，用更小学习率继续训练</td><td>数据较多、领域有差距；浅层可用更小学习率</td></tr>
</tbody></table>
<p><strong>领域差距</strong>决定收益：ImageNet 预训练对自然图像几乎总是有用，对医学、遥感、工业缺陷等域则要看数据规模；此时第 25 章的自监督 / 基础模型特征往往更合适。选型时把<strong>精度、延迟、显存、许可协议</strong>四项一起列表，别只看 Top-1。</p>
<pre class="code" data-file="inline" data-lang="Shell"><code>pip install torch torchvision timm
python -c "import timm; print(len(timm.list_models()))"   # 查看可用预训练骨干数</code></pre>"""),
  ],
  repos=[
      ("torchvision", "官方 <code>resnet50(weights=...)</code> 等预训练模型与权重下载"),
      ("timm", "数百个骨干与统一 API，做精度/延迟对照实验最方便"),
      ("resnet", "ResNet 原始实现与论文配套代码，理解残差块的出处"),
      ("convnext", "现代训练配方改造纯卷积的官方实现"),
      ("mae", "掩码自编码预训练：领域数据充足但无标注时的替代方案"),
      ("dinov2", "无需标注的通用视觉特征，适合作为冻结骨干做迁移"),
      ("pytorch-tutorials", "官方迁移学习教程（蚂蚁/蜜蜂二分类），含冻结与微调对照"),
  ],
  repo_note="建议实验：固定数据集与训练轮数，只换骨干，记录 Top-1、单张推理时延与显存峰值三列。",
  pitfalls=["微调时对所有层用同一个大学习率：破坏预训练特征，效果可能不如冻结。",
            "忘记切换 <code>model.eval()</code> 或忘记 <code>torch.no_grad()</code>：推理慢且 BN 行为异常。",
            "只看 Top-1 选模型：边缘设备上大模型可能完全跑不动。",
            "忽略权重的许可证：研究用权重未必允许商用。"],
  exercises=["从 <code>∂L/∂x</code> 的表达式说明残差连接为何缓解梯度消失，并解释为什么不是“彻底解决”。",
             "设计一个三行实验表，比较特征提取与微调在小样本（每类 20 张）下的表现差异。"],
  further=["<a href='../17-cnn-fundamentals/index.html'>第 17 章 神经网络与 CNN 基础</a>",
           "<a href='../19-datasets-evaluation/index.html'>第 19 章 数据集、评价指标与实验方法</a>",
           "<a href='../../part4/25-vision-transformers/index.html'>第 25 章 视觉 Transformer 与基础模型</a>"]),

C("19", "p3", "part3/19-datasets-evaluation", "数据集、评价指标与实验方法",
  "指标定义决定优化方向：先约定“什么算对”，再谈模型；这一章也是全书从算法走向工程的分界线。",
  hours="4 学时",
  goals=["能列出五类常用视觉数据集及其任务与标注格式",
         "能识别并避免三种常见的数据泄漏",
         "能为分类/检测/分割/复原分别选对指标",
         "能写出一份可复现实验的清单"],
  points=["ImageNet / COCO / VOC / Cityscapes", "标注类型与格式", "数据集划分与泄漏", "Top-k / PR / F1", "mAP 与 IoU", "Dice / PSNR / SSIM / FID", "消融与复现清单"],
  sections=[
      ("19.1", "常用数据集与标注", """<table><thead><tr><th>数据集</th><th>任务</th><th>标注</th></tr></thead><tbody>
<tr><td>ImageNet / ImageNet-1k</td><td>分类、预训练</td><td>单标签（1000 类）</td></tr>
<tr><td>MS COCO</td><td>检测、实例分割、关键点</td><td>框 / 多边形 / 关键点，JSON</td></tr>
<tr><td>PASCAL VOC</td><td>检测、语义分割</td><td>框 / 类别掩模，课程实验首选</td></tr>
<tr><td>Cityscapes</td><td>街景语义/实例分割</td><td>精细多边形标注，19 类</td></tr>
<tr><td>ADE20K</td><td>场景解析</td><td>开放词表语义分割</td></tr>
</tbody></table>
<p>标注质量往往比模型选择更影响结果。<strong>标注规范</strong>（遮挡怎么标、边界容差、模糊样本是否丢弃）必须写进文档，否则不同人标出的同一类不可比。</p>"""),
      ("19.2", "划分与数据泄漏", """<ul><li><strong>随机划分的陷阱</strong>：同一视频的相邻帧、同一患者的连续切片、同一产品的多角度照片若被分到训练与测试，指标会虚高。</li>
<li><strong>预处理泄漏</strong>：在全量数据上算均值/方差、做 k-means 码本或特征选择，等于让测试集信息进入训练。</li>
<li><strong>调参泄漏</strong>：反复用测试集选超参，测试集就变成了验证集。</li></ul>
<p>正确做法是<strong>按实体分组划分</strong>（group split），并把所有统计量只在训练集上拟合。这一点与第 16 章的传统基线同样适用。</p>"""),
      ("19.3", "指标对照表", """<table><thead><tr><th>任务</th><th>主指标</th><th>辅助 / 陷阱</th></tr></thead><tbody>
<tr><td>分类</td><td>Top-1 / Top-5、每类 F1</td><td>不平衡时看宏平均与 PR 曲线，别只看准确率</td></tr>
<tr><td>检测</td><td>mAP@0.5、mAP@0.5:0.95</td><td>IoU 阈值、NMS 阈值、小目标 AP 要单独报</td></tr>
<tr><td>分割</td><td>mIoU、Dice、像素准确率</td><td>背景占比大时像素准确率毫无意义</td></tr>
<tr><td>复原</td><td>PSNR / SSIM</td><td>与感知质量不一致，需补 LPIPS / 人工评分（第 23 章）</td></tr>
<tr><td>生成</td><td>FID、CLIP Score</td><td>FID 依赖采样量与 Inception 特征，跨论文不可直接比</td></tr>
</tbody></table>
<p><strong>IoU</strong> = 交/并，是检测与分割的共同底座；<strong>mAP</strong> 是不同召回下 precision 的积分近似，由 PR 曲线下面积给出。工程上务必用官方评测脚本（COCO API / TorchMetrics），自己写的实现常在边界条件上不一致。</p>"""),
      ("19.4", "消融与可复现清单", """<ol><li>固定随机种子、依赖版本、硬件与数据划分文件；</li>
<li>只改一个因素，重复多次取均值与标准差；</li>
<li>报告参数量、训练时长、推理时延，而不只报精度；</li>
<li>公开失败案例与负结果；</li>
<li>提供一条能从头跑通的命令。</li></ol>
<p class="code-hint">本书上卷所有 <code>.m</code> 脚本固定随机种子、参数集中在开头、末尾打印可核对数值，就是同一套可复现约定的最简实现。</p>"""),
  ],
  repos=[
      ("imagenet", "分类与预训练的标准数据集入口"),
      ("coco", "检测/实例分割的官方数据与评测说明"),
      ("voc", "小体量、适合课程实验的经典检测与分割集"),
      ("cityscapes", "街景语义分割，注意其许可与使用条款"),
      ("torchmetrics", "统一实现 mAP / IoU / Dice / PSNR / SSIM / FID，避免手写指标误差"),
      ("pycocotools", "COCO 官方评测工具，检测结果必须以它为准"),
      ("cvat", "开源标注平台，支持框、多边形、关键点与质检流程"),
      ("albumentations", "训练期增强，保证图像与标注同步变换"),
  ],
  repo_note="课程建议：VOC 或自建小数据集 + TorchMetrics，先把评测脚本跑通，再开始调模型。",
  pitfalls=["用像素准确率评价前景只占 1% 的分割：全预测背景就有 99%。",
            "在全量数据上计算归一化均值：典型且隐蔽的数据泄漏。",
            "跨论文直接比较 FID 数值：采样数量与特征提取网络可能不同。",
            "自己实现 mAP：NMS 与边界条件的细微差异会让结果无法对照。"],
  exercises=["写出 IoU 与 Dice 的关系式，并说明为什么二者单调一致但数值不同。",
             "为“视频帧级缺陷检测”设计不会泄漏的划分方案，并说明随机划分会高估多少（定性）。"],
  further=["<a href='../16-learning-baselines/index.html'>第 16 章 传统基线的评估</a>",
           "<a href='../../part4/21-object-detection/index.html'>第 21 章 目标检测（mAP 的实际用法）</a>",
           "<a href='../../part4/26-projects/index.html'>第 26 章 工程落地与综合项目</a>"]),

C("20", "p4", "part4/20-classification-xai", "图像分类与可解释性",
  "训练配方决定上限，误差分析决定改进方向，可解释性决定你能不能信任这个结果。",
  hours="3 学时",
  goals=["能列出一个现代分类训练配方的关键组件",
         "会用混淆矩阵定位系统性错误",
         "能说明 Grad-CAM 与显著性图的原理与局限",
         "能识别分布外与标签噪声带来的风险"],
  points=["训练配方与学习率调度", "混合精度与 EMA", "混淆矩阵与误差分析", "标签噪声与长尾", "Grad-CAM 与归因方法", "分布外与校准"],
  sections=[
      ("20.1", "训练配方", """<p>同样的 ResNet-50，用 2015 年的配方和现代配方可以差出好几个百分点。常见组件：SGD+Momentum 或 AdamW、余弦/阶梯学习率衰减、warmup、权重衰减、标签平滑、MixUp/CutMix、随机擦除、EMA 权重平均、混合精度训练。它们大多是<strong>正则化与优化稳定性</strong>的不同手段，彼此会相互影响，因此比较架构时必须固定配方（这正是 ConvNeXt 论文的出发点）。</p>"""),
      ("20.2", "误差分析先于换模型", """<ol><li>画<strong>混淆矩阵</strong>，找出成对混淆的类别；</li>
<li>把错分样本按置信度排序，人工看前 50 张，区分<strong>标注错、样本模糊、类目定义重叠、模型真错</strong>；</li>
<li>按子类/场景/光照切片统计指标，找系统性短板；</li>
<li>再决定是补数据、改标注规范、重加权，还是换更大的模型。</li></ol>
<p>长尾分布下常见的错误是只优化整体准确率：少数类召回极低却不影响总指标。类别重加权、重采样与解耦训练（先学表示再平衡分类器）是常用对策。</p>"""),
      ("20.3", "可解释性与鲁棒性", """<p><strong>Grad-CAM</strong> 用目标类别对最后一层卷积特征的梯度做全局加权，得到粗粒度的类激活热力图；<strong>积分梯度</strong>、<strong>遮挡测试</strong>、<strong>显著图</strong>从不同角度给出归因。要注意：热力图说明“模型在哪里找到了证据”，<strong>不等于</strong>“模型为什么正确”，也不保证因果性；同一模型换一层、换一个类别就可能给出不同解释。</p>
<p><strong>分布外（OOD）</strong>与<strong>对抗样本</strong>暴露的是另一个问题：模型可能依赖数据集里的捷径（背景、水印、拍摄设备）。上线前至少要做置信度校准、OOD 检测与关键切片的压力测试。</p>
<pre class="code" data-file="inline" data-lang="Shell"><code>pip install torch torchvision timm pytorch-grad-cam captum
python -c "import pytorch_grad_cam; print('grad-cam ready')"</code></pre>"""),
  ],
  repos=[
      ("mmpretrain", "OpenMMLab 分类工具箱：配置文件化地复现训练配方与消融"),
      ("timm", "预训练权重 + 训练脚本，便于固定配方只换骨干"),
      ("gradcam", "Grad-CAM / Score-CAM / Eigen-CAM 的统一实现，可对任意层出图"),
      ("captum", "PyTorch 官方归因库，含积分梯度与遮挡测试"),
      ("torchmetrics", "混淆矩阵、每类 F1、校准误差的可靠实现"),
      ("distill", "高质量可视化文章，帮助正确理解归因方法的边界"),
  ],
  repo_note="推荐练习：对同一张误分类图同时出 Grad-CAM 热力图与 Top-5 置信度，写一段“模型依赖了什么线索”的分析。",
  pitfalls=["把热力图当因果解释：它只反映相关性，且对层与类别选择敏感。",
            "只看整体准确率：长尾类别可能在生产环境里恰好最关键。",
            "换了模型也换了训练配方：无法判断提升来自哪里。",
            "不做置信度校准：高置信度错误样本会静默进入下游。"],
  exercises=["写出 Grad-CAM 的加权公式，并解释为什么用最后一个卷积层而不是全连接层。",
             "为 10 类长尾分类设计一组切片指标（至少 4 个切片），说明每个切片暴露什么风险。"],
  further=["<a href='../../part3/18-cnn-architectures/index.html'>第 18 章 经典 CNN 架构与迁移学习</a>",
           "<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 数据集与评测</a>",
           "<a href='../21-object-detection/index.html'>第 21 章 目标检测</a>"]),

C("21", "p4", "part4/21-object-detection", "目标检测",
  "从“先找候选框再分类”到“一次前向直接出框”，再到“用集合预测去掉所有手工组件”，是一条不断删掉人工先验的路。",
  hours="4 学时",
  goals=["能说清 IoU、NMS 与 mAP 的计算关系",
         "能对比两阶段、单阶段与 DETR 三类范式",
         "理解 anchor 与 anchor-free 的取舍",
         "能为给定部署场景选择检测方案并说明代价"],
  points=["任务定义与框表示", "IoU / NMS / mAP", "R-CNN 家族", "YOLO / SSD / RetinaNet", "Focal Loss 与类别不平衡", "Anchor-free 与 FCOS", "DETR 与集合预测", "开放词表检测"],
  sections=[
      ("21.1", "任务定义与评测", """<p>输出是一组 <code>(类别, 置信度, 框)</code>，框常用 <code>(x, y, w, h)</code> 或 <code>(x1, y1, x2, y2)</code>。预测与真值用 <strong>IoU</strong> 匹配，超过阈值算真正例；按置信度排序得到 PR 曲线，其面积即 AP，多类平均即 mAP。<strong>NMS</strong> 删除与高分框重叠超过阈值的冗余框——它就是第 10 章非极大抑制思想在框层面的复用。</p>
<div class="card note"><p style="margin-bottom:0">检测与分类最大的差别是<strong>极度类别不平衡</strong>：一张图里可能有上万个候选位置，真正包含目标的只有几个。这直接催生了 Focal Loss 与两阶段方法的采样策略。</p></div>"""),
      ("21.2", "三种范式", """<table><thead><tr><th>范式</th><th>代表</th><th>核心思路</th><th>取舍</th></tr></thead><tbody>
<tr><td>两阶段</td><td>R-CNN → Fast → Faster R-CNN → Mask R-CNN</td><td>先生成候选区域（RPN），再对每个区域分类与回归</td><td>精度高、小目标好；速度较慢</td></tr>
<tr><td>单阶段</td><td>YOLO 系列、SSD、RetinaNet</td><td>在特征图每个位置直接预测框与类别</td><td>快、适合实时；早期精度落后，已被逐步追平</td></tr>
<tr><td>集合预测</td><td>DETR 及其变体</td><td>Transformer + 匈牙利匹配，端到端出固定数量预测</td><td>去掉 anchor 与 NMS；收敛慢、小目标需额外设计</td></tr>
</tbody></table>
<p><strong>Anchor-free</strong>（FCOS、YOLOX 等）直接预测点到框四边的距离，省去 anchor 尺寸聚类这组超参；<strong>Focal Loss</strong> 降低易分负样本的权重，让训练聚焦困难样本。</p>"""),
      ("21.3", "工程选择与开放词表", """<ul><li><strong>实时/边缘</strong>：YOLO 系列 + 量化 + TensorRT，优先看 FPS 与功耗。</li>
<li><strong>高精度/研究</strong>：MMDetection 或 Detectron2，配置文件化便于消融。</li>
<li><strong>类别会变</strong>：GroundingDINO 等开放词表检测用文本提示指定类别，避免每加一类就重训。</li></ul>
<p>不要忘记<strong>标注一致性</strong>：框该不该包含遮挡部分、截断目标怎么标，直接决定 mAP 的天花板。第 19 章的官方评测脚本必须用上。</p>
<pre class="code" data-file="inline" data-lang="Shell"><code>pip install ultralytics
yolo predict model=yolov8n.pt source=bus.jpg   # 一行命令跑通官方预训练检测</code></pre>"""),
  ],
  repos=[
      ("ultralytics", "YOLOv8/11 官方工程，训练/验证/导出一条命令完成，最适合上手"),
      ("yolov5", "社区生态极成熟的单阶段检测器，含大量部署教程"),
      ("mmdetection", "两阶段、单阶段、anchor-free 全家桶，适合做对照实验"),
      ("detectron2", "FAIR 官方 Faster/Mask R-CNN 实现，读 RPN 代码的最佳入口"),
      ("detr", "集合预测原始实现，理解匈牙利匹配与去 NMS"),
      ("groundingdino", "开放词表检测：用文本提示指定要检测的类别"),
      ("pycocotools", "COCO 官方 mAP 评测，报告结果必须用它"),
      ("torchvision", "官方 NMS / RoIAlign 等算子与 Faster R-CNN 基线"),
  ],
  repo_note="建议实验：同一数据集上跑 YOLO 与 Faster R-CNN，分别记录 mAP@0.5:0.95、FPS 与小目标 AP。",
  pitfalls=["用自己写的 mAP 报结果：与 COCO API 的边界处理不一致，无法横向比较。",
            "NMS 阈值一刀切：人群等密集场景会误删正确框。",
            "忽略小目标：整体 mAP 不错但关键类别几乎检不出。",
            "把开放词表模型当固定类别检测器评测：提示词变化会显著影响结果。"],
  exercises=["推导 NMS 与第 10 章边缘非极大抑制的对应关系，说明两者“抑制轴”分别是什么。",
             "写出 Focal Loss 表达式，解释 <code>(1−p_t)^γ</code> 如何降低易分样本权重。"],
  further=["<a href='../../part3/19-datasets-evaluation/index.html'>第 19 章 mAP 与 IoU</a>",
           "<a href='../../part2/10-edge-detection/index.html'>第 10 章 边缘检测（NMS 的原型）</a>",
           "<a href='../22-segmentation-networks/index.html'>第 22 章 深度图像分割</a>"]),

]
