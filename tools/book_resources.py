#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全书扩展学习链接库（唯一数据源）。

R              : key -> (显示名, URL, 一句话说明, 分类)
TOPIC_RULES    : 知识点关键词 -> 资源 key 列表，用于「知识点地图」逐条挂链接
CHAPTER_RESOURCES : 章节 id -> 该章「扩展学习」小节的精读清单

链接以官方文档 / 官方 GitHub 仓库 / 标准百科条目为主；
用 tools/check_book.py --urls 可批量探测 URL 可达性（需要联网）。

注意：本开发环境无法访问 en.wikipedia.org，百科条目按标准英文条目 URL 收录，
自检会把这类超时归为「本环境不可达」而非链接失效；GitHub 与厂商文档链接均已实测可达。
"""
from __future__ import annotations

import html as html_mod

R = {
    # ---------- 工具与文档 ----------
    "octave": ("GNU Octave", "https://octave.org/", "免费、与 MATLAB 语法高度兼容的科学计算环境，本书上卷代码的目标平台", "工具"),
    "octave-docs": ("Octave 官方文档", "https://docs.octave.org/latest/", "函数参考与语言手册，查 conv2/fft2/imagesc 的权威出处", "文档"),
    "octave-image-pkg": ("Octave image 包", "https://octave.sourceforge.io/image/", "可选的图像处理函数包；本书示例刻意不依赖它", "工具"),
    "skimage": ("scikit-image", "https://scikit-image.org/", "Python 图像处理库，对照阅读每类传统算法的生产级实现", "工具"),
    "skimage-docs": ("scikit-image User Guide", "https://scikit-image.org/docs/stable/user_guide/", "按任务组织的传统算法讲解，适合与本书章节互相对照", "文档"),
    "opencv": ("OpenCV 官方仓库", "https://github.com/opencv/opencv", "工业界最常用的计算机视觉库，源码与示例均可直接查阅", "工具"),
    "opencv-docs": ("OpenCV Tutorials", "https://docs.opencv.org/master/d6/d00/tutorial_py_root.html", "官方教程，含滤波、形态学、特征与几何变换的示例", "文档"),
    "numpy-docs": ("NumPy 文档", "https://numpy.org/doc/stable/", "数组与广播规则；理解图像即矩阵的必经之路", "文档"),
    "imagej": ("ImageJ / Fiji", "https://imagej.net/", "科研图像测量与批处理工具，适合做人工核对", "工具"),
    "kornia": ("Kornia", "https://github.com/kornia/kornia", "可微分的传统 CV 算子库，把上卷算子接进下卷网络的桥梁", "框架"),
    "scikit-learn": ("scikit-learn", "https://github.com/scikit-learn/scikit-learn", "传统机器学习基线（SVM、k-means、随机森林）的标准实现", "框架"),
    "paperswithcode": ("Papers with Code", "https://paperswithcode.com/", "按任务查 SOTA 方法与官方代码仓库", "文档"),
    "arxiv": ("arXiv", "https://arxiv.org/", "预印本检索；下卷各章论文的主要出处", "文档"),
    "cs231n": ("Stanford CS231n", "https://cs231n.github.io/", "经典视觉课程笔记，下卷最好的免费配套教材", "课程"),
    "d2l": ("动手学深度学习 d2l.ai", "https://d2l.ai/", "含可运行代码的深度学习教材，中文版可用", "课程"),
    "distill": ("Distill.pub", "https://distill.pub/", "可视化解释深度学习与可解释性的高质量文章", "课程"),
    "pytorch-tutorials": ("PyTorch Tutorials", "https://pytorch.org/tutorials/", "官方训练循环、迁移学习与部署示例", "文档"),

    # ---------- 传统算法：百科 ----------
    "dip-wiki": ("Digital image processing", "https://en.wikipedia.org/wiki/Digital_image_processing", "学科总览与术语索引", "百科"),
    "convolution": ("Convolution", "https://en.wikipedia.org/wiki/Convolution", "线性滤波的数学定义与性质", "百科"),
    "kernel-wiki": ("Kernel (image processing)", "https://en.wikipedia.org/wiki/Kernel_(image_processing)", "卷积核 / 滤波掩模的条目", "百科"),
    "gaussian-blur": ("Gaussian blur", "https://en.wikipedia.org/wiki/Gaussian_blur", "高斯核的可分离性与尺度参数", "百科"),
    "median-filter": ("Median filter", "https://en.wikipedia.org/wiki/Median_filter", "排序统计滤波与椒盐噪声", "百科"),
    "bilateral": ("Bilateral filter", "https://en.wikipedia.org/wiki/Bilateral_filter", "保边平滑的双权重思想", "百科"),
    "nlm": ("Non-local means", "https://en.wikipedia.org/wiki/Non-local_means", "利用图像自相似性的去噪", "百科"),
    "hist-eq": ("Histogram equalization", "https://en.wikipedia.org/wiki/Histogram_equalization", "累积分布函数映射的推导", "百科"),
    "clahe": ("Adaptive histogram equalization", "https://en.wikipedia.org/wiki/Adaptive_histogram_equalization", "CLAHE 与限制对比度的动机", "百科"),
    "gamma": ("Gamma correction", "https://en.wikipedia.org/wiki/Gamma_correction", "显示非线性与幂律变换", "百科"),
    "dft": ("Discrete Fourier transform", "https://en.wikipedia.org/wiki/Discrete_Fourier_transform", "二维 DFT 的定义与性质", "百科"),
    "fft": ("Fast Fourier transform", "https://en.wikipedia.org/wiki/Fast_Fourier_transform", "FFT 的复杂度与实现要点", "百科"),
    "dct": ("Discrete cosine transform", "https://en.wikipedia.org/wiki/Discrete_cosine_transform", "DCT 的能量集中特性", "百科"),
    "jpeg": ("JPEG", "https://en.wikipedia.org/wiki/JPEG", "DCT + 量化 + 熵编码的完整流程", "百科"),
    "huffman": ("Huffman coding", "https://en.wikipedia.org/wiki/Huffman_coding", "变长熵编码与码长下界", "百科"),
    "entropy": ("Entropy (information theory)", "https://en.wikipedia.org/wiki/Entropy_(information_theory)", "信息熵与压缩极限", "百科"),
    "wavelet": ("Discrete wavelet transform", "https://en.wikipedia.org/wiki/Discrete_wavelet_transform", "多分辨率分析与 JPEG2000 基础", "百科"),
    "wiener": ("Wiener filter", "https://en.wikipedia.org/wiki/Wiener_filter", "最小均方误差意义下的最优线性复原", "百科"),
    "psnr": ("Peak signal-to-noise ratio", "https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio", "基于 MSE 的复原评价指标及其局限", "百科"),
    "ssim": ("Structural similarity", "https://en.wikipedia.org/wiki/Structural_similarity", "结构相似度的亮度/对比度/结构三项", "百科"),
    "canny": ("Canny edge detector", "https://en.wikipedia.org/wiki/Canny_edge_detector", "高斯平滑、非极大抑制与双阈值", "百科"),
    "sobel": ("Sobel operator", "https://en.wikipedia.org/wiki/Sobel_operator", "离散梯度核与方向估计", "百科"),
    "hough": ("Hough transform", "https://en.wikipedia.org/wiki/Hough_transform", "参数空间投票检测直线与圆", "百科"),
    "sift": ("Scale-invariant feature transform", "https://en.wikipedia.org/wiki/Scale-invariant_feature_transform", "尺度空间、关键点与描述子", "百科"),
    "orb": ("ORB (feature descriptor)", "https://en.wikipedia.org/wiki/Oriented_FAST_and_rotated_BRIEF", "实时二值特征与工程取舍", "百科"),
    "harris": ("Corner detection", "https://en.wikipedia.org/wiki/Corner_detection", "自相关矩阵与角点响应", "百科"),
    "ransac": ("Random sample consensus", "https://en.wikipedia.org/wiki/Random_sample_consensus", "含外点时的鲁棒模型拟合", "百科"),
    "morphology": ("Mathematical morphology", "https://en.wikipedia.org/wiki/Mathematical_morphology", "集合论视角下的腐蚀与膨胀", "百科"),
    "watershed": ("Watershed (image processing)", "https://en.wikipedia.org/wiki/Watershed_(image_processing)", "地形淹没类比与过分割", "百科"),
    "distance-transform": ("Distance transform", "https://en.wikipedia.org/wiki/Distance_transform", "二值图距离图与分水岭种子", "百科"),
    "otsu": ("Otsu's method", "https://en.wikipedia.org/wiki/Otsu%27s_method", "类间方差最大化的自动阈值", "百科"),
    "kmeans": ("k-means clustering", "https://en.wikipedia.org/wiki/K-means_clustering", "迭代聚类与初始化敏感性", "百科"),
    "graphcut": ("Graph cuts in computer vision", "https://en.wikipedia.org/wiki/Graph_cuts_in_computer_vision", "能量最小化与交互式分割", "百科"),
    "active-contour": ("Active contour model", "https://en.wikipedia.org/wiki/Active_contour_model", "蛇模型与水平集方法", "百科"),
    "lbp": ("Local binary patterns", "https://en.wikipedia.org/wiki/Local_binary_patterns", "局部纹理描述子", "百科"),
    "glcm": ("Co-occurrence matrix", "https://en.wikipedia.org/wiki/Co-occurrence_matrix", "灰度共生矩阵与 Haralick 特征", "百科"),
    "image-moment": ("Image moment", "https://en.wikipedia.org/wiki/Image_moment", "矩、质心与 Hu 不变矩", "百科"),
    "bilinear": ("Bilinear interpolation", "https://en.wikipedia.org/wiki/Bilinear_interpolation", "几何变换中的插值权重", "百科"),
    "affine": ("Affine transformation", "https://en.wikipedia.org/wiki/Affine_transformation", "平移/旋转/缩放/剪切的矩阵表示", "百科"),
    "homography": ("Homography", "https://en.wikipedia.org/wiki/Homography", "透视变换与 4 点对应", "百科"),
    "hsv": ("HSL and HSV", "https://en.wikipedia.org/wiki/HSL_and_HSV", "色相/饱和度/明度的定义与转换", "百科"),
    "cielab": ("CIELAB color space", "https://en.wikipedia.org/wiki/CIELAB_color_space", "感知均匀色彩空间", "百科"),

    # ---------- AI：百科 ----------
    "cnn-wiki": ("Convolutional neural network", "https://en.wikipedia.org/wiki/Convolutional_neural_network", "局部连接、权值共享与层次特征", "百科"),
    "backprop": ("Backpropagation", "https://en.wikipedia.org/wiki/Backpropagation", "链式法则与自动微分", "百科"),
    "overfitting": ("Overfitting", "https://en.wikipedia.org/wiki/Overfitting", "泛化误差与正则化", "百科"),
    "transfer-learning": ("Transfer learning", "https://en.wikipedia.org/wiki/Transfer_learning", "预训练与微调的适用条件", "百科"),
    "data-augmentation": ("Data augmentation", "https://en.wikipedia.org/wiki/Data_augmentation", "标签保持变换与不变性", "百科"),
    "gan-wiki": ("Generative adversarial network", "https://en.wikipedia.org/wiki/Generative_adversarial_network", "生成器/判别器的极小极大博弈", "百科"),
    "vae-wiki": ("Variational autoencoder", "https://en.wikipedia.org/wiki/Variational_autoencoder", "重参数化与 ELBO", "百科"),
    "diffusion-wiki": ("Diffusion model", "https://en.wikipedia.org/wiki/Diffusion_model", "前向加噪与反向去噪", "百科"),
    "transformer-wiki": ("Transformer (deep learning)", "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)", "自注意力与位置编码", "百科"),
    "vit-wiki": ("Vision transformer", "https://en.wikipedia.org/wiki/Vision_transformer", "图像分块作为 token", "百科"),
    "detection-wiki": ("Object detection", "https://en.wikipedia.org/wiki/Object_detection", "检测任务的术语与评测", "百科"),
    "segmentation-wiki": ("Image segmentation", "https://en.wikipedia.org/wiki/Image_segmentation", "语义/实例/全景分割的区别", "百科"),
    "superres-wiki": ("Super-resolution imaging", "https://en.wikipedia.org/wiki/Super-resolution_imaging", "超分辨率的病态逆问题本质", "百科"),
    "iou": ("Jaccard index", "https://en.wikipedia.org/wiki/Jaccard_index", "IoU 的定义与阈值曲线", "百科"),
    "roc": ("Receiver operating characteristic", "https://en.wikipedia.org/wiki/Receiver_operating_characteristic", "ROC / AUC 与阈值选择", "百科"),

    # ---------- 框架与官方实现 ----------
    "pytorch": ("PyTorch", "https://github.com/pytorch/pytorch", "主流深度学习框架", "框架"),
    "torchvision": ("torchvision", "https://github.com/pytorch/vision", "官方分类/检测/分割模型与数据集变换", "框架"),
    "tensorflow": ("TensorFlow", "https://github.com/tensorflow/tensorflow", "另一主流框架，含完整部署链路", "框架"),
    "keras": ("Keras", "https://github.com/keras-team/keras", "高层 API，适合快速搭基线", "框架"),
    "timm": ("pytorch-image-models (timm)", "https://github.com/huggingface/pytorch-image-models", "数百个预训练分类骨干与训练脚本", "分类"),
    "hf-transformers": ("Hugging Face Transformers", "https://github.com/huggingface/transformers", "ViT、CLIP、多模态模型的统一接口", "框架"),
    "hf-diffusers": ("Hugging Face Diffusers", "https://github.com/huggingface/diffusers", "扩散模型推理与训练管线", "生成"),
    "mmpretrain": ("MMPreTrain", "https://github.com/open-mmlab/mmpretrain", "OpenMMLab 分类与预训练工具箱", "分类"),
    "mmdetection": ("MMDetection", "https://github.com/open-mmlab/mmdetection", "检测算法全家桶与配置文件化实验", "检测"),
    "mmsegmentation": ("MMSegmentation", "https://github.com/open-mmlab/mmsegmentation", "语义分割算法全家桶", "分割"),
    "detectron2": ("Detectron2", "https://github.com/facebookresearch/detectron2", "FAIR 的检测/实例分割框架", "检测"),
    "ultralytics": ("Ultralytics YOLO", "https://github.com/ultralytics/ultralytics", "YOLOv8/11 官方工程，一行命令训练与推理", "检测"),
    "yolov5": ("YOLOv5", "https://github.com/ultralytics/yolov5", "工程化程度极高的单阶段检测器", "检测"),
    "detr": ("DETR", "https://github.com/facebookresearch/detr", "用 Transformer + 集合预测做检测", "检测"),
    "groundingdino": ("GroundingDINO", "https://github.com/IDEA-Research/GroundingDINO", "开放词表检测，文本提示直接出框", "检测"),
    "fcn": ("FCN (Berkeley)", "https://github.com/shelhamer/fcn.berkeleyvision.org", "全卷积网络原始实现", "分割"),
    "unet-pytorch": ("Pytorch-UNet", "https://github.com/milesial/Pytorch-UNet", "U-Net 的简洁可读实现", "分割"),
    "mask2former": ("Mask2Former", "https://github.com/facebookresearch/Mask2Former", "统一三类分割的掩码分类架构", "分割"),
    "sam": ("Segment Anything (SAM)", "https://github.com/facebookresearch/segment-anything", "可提示分割基础模型", "分割"),
    "sam2": ("SAM 2", "https://github.com/facebookresearch/sam2", "图像与视频统一的可提示分割", "分割"),
    "monai": ("MONAI", "https://github.com/Project-MONAI/MONAI", "医学影像分割与复原的官方框架", "分割"),
    "dncnn": ("DnCNN", "https://github.com/cszn/DnCNN", "残差学习去噪的经典工程", "复原"),
    "esrgan": ("ESRGAN", "https://github.com/xinntao/ESRGAN", "感知损失驱动的超分辨率", "复原"),
    "real-esrgan": ("Real-ESRGAN", "https://github.com/xinntao/Real-ESRGAN", "面向真实退化图像的盲超分", "复原"),
    "cyclegan": ("pix2pix / CycleGAN", "https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix", "配对与非配对图像翻译的官方实现", "生成"),
    "stylegan3": ("StyleGAN3", "https://github.com/NVlabs/stylegan3", "高质量人脸/图像生成与潜在空间编辑", "生成"),
    "ddpm": ("DDPM (官方)", "https://github.com/hojonathanho/diffusion", "去噪扩散概率模型原始实现", "生成"),
    "stable-diffusion": ("Stable Diffusion", "https://github.com/CompVis/stable-diffusion", "潜空间扩散模型，文生图基线", "生成"),
    "latent-diffusion": ("Latent Diffusion", "https://github.com/CompVis/latent-diffusion", "LDM 训练与条件生成代码", "生成"),
    "vit": ("Vision Transformer (Google)", "https://github.com/google-research/vision_transformer", "ViT 官方实现与预训练权重", "分类"),
    "swin": ("Swin Transformer", "https://github.com/microsoft/Swin-Transformer", "层级化窗口注意力的骨干网络", "分类"),
    "convnext": ("ConvNeXt", "https://github.com/facebookresearch/ConvNeXt", "用现代训练法改造纯卷积骨干", "分类"),
    "resnet": ("Deep Residual Networks", "https://github.com/KaimingHe/deep-residual-networks", "ResNet 原始实现", "分类"),
    "mae": ("MAE", "https://github.com/facebookresearch/mae", "掩码自编码自监督预训练", "分类"),
    "dinov2": ("DINOv2", "https://github.com/facebookresearch/dinov2", "无需标注的通用视觉特征", "分类"),
    "clip": ("CLIP", "https://github.com/openai/CLIP", "图文对比预训练与零样本分类", "分类"),
    "open-clip": ("OpenCLIP", "https://github.com/mlfoundations/open_clip", "CLIP 的开源复现与更大规模权重", "分类"),
    "llava": ("LLaVA", "https://github.com/haotian-liu/LLaVA", "视觉语言对话模型，读图问答", "分类"),
    "gradcam": ("pytorch-grad-cam", "https://github.com/jacobgil/pytorch-grad-cam", "Grad-CAM 等热力图方法的统一实现", "分类"),
    "captum": ("Captum", "https://github.com/pytorch/captum", "PyTorch 官方模型可解释性库", "分类"),
    "albumentations": ("Albumentations", "https://github.com/albumentations-team/albumentations", "高性能数据增强，支持框/掩码同步变换", "框架"),
    "torchmetrics": ("TorchMetrics", "https://github.com/Lightning-AI/torchmetrics", "mAP / IoU / Dice / PSNR 等指标的可靠实现", "评测"),
    "pycocotools": ("COCO API", "https://github.com/cocodataset/cocoapi", "COCO 标注读取与官方评测", "评测"),
    "cvat": ("CVAT", "https://github.com/cvat-ai/cvat", "开源标注平台，支持框/多边形/关键点", "标注"),
    "labelstudio": ("Label Studio", "https://github.com/HumanSignal/label-studio", "通用数据标注与质检工具", "标注"),
    "onnx": ("ONNX", "https://github.com/onnx/onnx", "跨框架模型交换格式", "部署"),
    "onnxruntime": ("ONNX Runtime", "https://github.com/microsoft/onnxruntime", "跨平台高性能推理引擎", "部署"),
    "tensorrt": ("TensorRT", "https://github.com/NVIDIA/TensorRT", "GPU 推理优化与量化", "部署"),
    "openvino": ("OpenVINO", "https://github.com/openvinotoolkit/openvino", "Intel CPU/GPU 推理优化", "部署"),
    "ncnn": ("ncnn", "https://github.com/Tencent/ncnn", "移动端轻量推理框架", "部署"),

    # ---------- 数据集 ----------
    "imagenet": ("ImageNet", "https://www.image-net.org/", "分类与预训练的标准大数据集", "数据集"),
    "coco": ("MS COCO", "https://cocodataset.org/", "检测 / 实例分割 / 关键点标准评测集", "数据集"),
    "voc": ("PASCAL VOC", "http://host.robots.ox.ac.uk/pascal/VOC/", "经典检测与分割小数据集，适合课程实验", "数据集"),
    "cityscapes": ("Cityscapes", "https://www.cityscapes-dataset.com/", "街景语义分割与实例分割", "数据集"),
    "ade20k": ("ADE20K", "https://groups.csail.mit.edu/vision/datasets/ADE20K/", "场景解析与语义分割", "数据集"),
    "mnist-wiki": ("MNIST database", "https://en.wikipedia.org/wiki/MNIST_database", "入门分类数据集的背景与基准结果", "数据集"),
}

# 关键词 -> 资源 key；按顺序命中，取前 max_links 个
TOPIC_RULES = [
    ("直方图均衡", ["hist-eq", "skimage-docs"]),
    ("直方图", ["hist-eq", "clahe"]),
    ("CLAHE", ["clahe", "skimage-docs"]),
    ("gamma", ["gamma", "hist-eq"]),
    ("幂律", ["gamma", "hist-eq"]),
    ("灰度变换", ["gamma", "dip-wiki"]),
    ("卷积", ["convolution", "kernel-wiki"]),
    ("高斯核", ["gaussian-blur", "kernel-wiki"]),
    ("高斯滤波", ["gaussian-blur", "kernel-wiki"]),
    ("均值滤波", ["kernel-wiki", "gaussian-blur"]),
    ("中值", ["median-filter", "skimage-docs"]),
    ("双边", ["bilateral", "nlm"]),
    ("非局部均值", ["nlm", "bilateral"]),
    ("锐化", ["kernel-wiki", "sobel"]),
    ("拉普拉斯", ["kernel-wiki", "sobel"]),
    ("边界填充", ["convolution", "skimage-docs"]),
    ("可分离", ["gaussian-blur", "convolution"]),
    ("傅里叶", ["dft", "fft"]),
    ("DFT", ["dft", "fft"]),
    ("FFT", ["fft", "dft"]),
    ("频谱", ["dft", "fft"]),
    ("低通", ["dft", "gaussian-blur"]),
    ("高通", ["dft", "sobel"]),
    ("陷波", ["dft", "fft"]),
    ("相位", ["dft", "fft"]),
    ("噪声模型", ["median-filter", "psnr"]),
    ("维纳", ["wiener", "psnr"]),
    ("逆滤波", ["wiener", "dft"]),
    ("复原", ["wiener", "psnr"]),
    ("去噪", ["nlm", "psnr"]),
    ("PSNR", ["psnr", "ssim"]),
    ("SSIM", ["ssim", "psnr"]),
    ("插值", ["bilinear", "affine"]),
    ("仿射", ["affine", "bilinear"]),
    ("透视", ["homography", "affine"]),
    ("配准", ["homography", "sift"]),
    ("色彩空间", ["hsv", "cielab"]),
    ("白平衡", ["hsv", "cielab"]),
    ("HSV", ["hsv", "cielab"]),
    ("Lab", ["cielab", "hsv"]),
    ("腐蚀", ["morphology", "skimage-docs"]),
    ("膨胀", ["morphology", "skimage-docs"]),
    ("形态学", ["morphology", "skimage-docs"]),
    ("开运算", ["morphology", "watershed"]),
    ("连通域", ["distance-transform", "morphology"]),
    ("距离变换", ["distance-transform", "watershed"]),
    ("分水岭", ["watershed", "distance-transform"]),
    ("梯度算子", ["sobel", "canny"]),
    ("Sobel", ["sobel", "canny"]),
    ("Canny", ["canny", "sobel"]),
    ("非极大", ["canny", "sobel"]),
    ("边缘", ["canny", "sobel"]),
    ("Harris", ["harris", "sift"]),
    ("角点", ["harris", "orb"]),
    ("SIFT", ["sift", "ransac"]),
    ("ORB", ["orb", "sift"]),
    ("描述子", ["sift", "orb"]),
    ("RANSAC", ["ransac", "homography"]),
    ("Hough", ["hough", "opencv-docs"]),
    ("Otsu", ["otsu", "skimage-docs"]),
    ("阈值", ["otsu", "kmeans"]),
    ("区域生长", ["graphcut", "watershed"]),
    ("k-means", ["kmeans", "scikit-learn"]),
    ("聚类", ["kmeans", "scikit-learn"]),
    ("图割", ["graphcut", "active-contour"]),
    ("水平集", ["active-contour", "graphcut"]),
    ("活动轮廓", ["active-contour", "graphcut"]),
    ("Hu 矩", ["image-moment", "lbp"]),
    ("矩", ["image-moment", "lbp"]),
    ("LBP", ["lbp", "glcm"]),
    ("GLCM", ["glcm", "lbp"]),
    ("纹理", ["glcm", "lbp"]),
    ("链码", ["image-moment", "dip-wiki"]),
    ("轮廓", ["image-moment", "active-contour"]),
    ("信息熵", ["entropy", "huffman"]),
    ("Huffman", ["huffman", "entropy"]),
    ("DCT", ["dct", "jpeg"]),
    ("JPEG", ["jpeg", "dct"]),
    ("量化", ["jpeg", "dct"]),
    ("小波", ["wavelet", "jpeg"]),
    ("率失真", ["entropy", "jpeg"]),
    ("SVM", ["scikit-learn", "cs231n"]),
    ("BoVW", ["sift", "scikit-learn"]),
    ("视觉词袋", ["sift", "scikit-learn"]),
    ("特征工程", ["sift", "scikit-learn"]),
    ("过拟合", ["overfitting", "data-augmentation"]),
    ("正则", ["overfitting", "d2l"]),
    ("评测", ["torchmetrics", "pycocotools"]),
    ("mAP", ["pycocotools", "detection-wiki"]),
    ("IoU", ["iou", "detection-wiki"]),
    ("Dice", ["iou", "torchmetrics"]),
    ("数据集", ["imagenet", "coco"]),
    ("数据增强", ["albumentations", "data-augmentation"]),
    ("消融", ["paperswithcode", "cs231n"]),
    ("反向传播", ["backprop", "d2l"]),
    ("卷积层", ["cnn-wiki", "d2l"]),
    ("池化", ["cnn-wiki", "d2l"]),
    ("激活", ["cnn-wiki", "d2l"]),
    ("批归一化", ["d2l", "cs231n"]),
    ("优化器", ["d2l", "pytorch-tutorials"]),
    ("损失函数", ["d2l", "cs231n"]),
    ("训练循环", ["pytorch-tutorials", "d2l"]),
    ("ResNet", ["resnet", "timm"]),
    ("VGG", ["torchvision", "timm"]),
    ("EfficientNet", ["timm", "mmpretrain"]),
    ("ConvNeXt", ["convnext", "timm"]),
    ("迁移学习", ["transfer-learning", "pytorch-tutorials"]),
    ("微调", ["pytorch-tutorials", "transfer-learning"]),
    ("预训练", ["timm", "pytorch-tutorials"]),
    ("Grad-CAM", ["gradcam", "captum"]),
    ("可解释", ["captum", "distill"]),
    ("混淆矩阵", ["torchmetrics", "roc"]),
    ("两阶段", ["detectron2", "mmdetection"]),
    ("R-CNN", ["detectron2", "mmdetection"]),
    ("YOLO", ["ultralytics", "yolov5"]),
    ("单阶段", ["ultralytics", "mmdetection"]),
    ("Anchor", ["ultralytics", "mmdetection"]),
    ("DETR", ["detr", "detection-wiki"]),
    ("NMS", ["torchvision", "mmdetection"]),
    ("语义分割", ["mmsegmentation", "segmentation-wiki"]),
    ("实例分割", ["detectron2", "mask2former"]),
    ("全景分割", ["mask2former", "segmentation-wiki"]),
    ("FCN", ["fcn", "mmsegmentation"]),
    ("U-Net", ["unet-pytorch", "monai"]),
    ("DeepLab", ["mmsegmentation", "fcn"]),
    ("SAM", ["sam", "sam2"]),
    ("DnCNN", ["dncnn", "nlm"]),
    ("超分", ["real-esrgan", "superres-wiki"]),
    ("ESRGAN", ["esrgan", "real-esrgan"]),
    ("去模糊", ["real-esrgan", "wiener"]),
    ("自编码器", ["vae-wiki", "d2l"]),
    ("VAE", ["vae-wiki", "d2l"]),
    ("GAN", ["gan-wiki", "cyclegan"]),
    ("CycleGAN", ["cyclegan", "gan-wiki"]),
    ("StyleGAN", ["stylegan3", "gan-wiki"]),
    ("扩散", ["hf-diffusers", "diffusion-wiki"]),
    ("DDPM", ["ddpm", "diffusion-wiki"]),
    ("Stable Diffusion", ["stable-diffusion", "latent-diffusion"]),
    ("文生图", ["stable-diffusion", "hf-diffusers"]),
    ("ViT", ["vit", "vit-wiki"]),
    ("Swin", ["swin", "transformer-wiki"]),
    ("自监督", ["mae", "dinov2"]),
    ("MAE", ["mae", "vit"]),
    ("DINOv2", ["dinov2", "mae"]),
    ("CLIP", ["clip", "open-clip"]),
    ("多模态", ["clip", "llava"]),
    ("视觉语言", ["llava", "clip"]),
    ("基础模型", ["sam", "dinov2"]),
    ("Transformer", ["transformer-wiki", "hf-transformers"]),
    ("自注意力", ["transformer-wiki", "vit-wiki"]),
    ("ONNX", ["onnx", "onnxruntime"]),
    ("TensorRT", ["tensorrt", "onnx"]),
    ("OpenVINO", ["openvino", "onnxruntime"]),
    ("量化", ["onnxruntime", "tensorrt"]),
    ("剪枝", ["pytorch", "onnxruntime"]),
    ("蒸馏", ["timm", "pytorch-tutorials"]),
    ("部署", ["onnxruntime", "ncnn"]),
    ("标注", ["cvat", "labelstudio"]),
    ("标注质量", ["cvat", "labelstudio"]),
    ("COCO", ["coco", "pycocotools"]),
    ("ImageNet", ["imagenet", "torchvision"]),
    ("Cityscapes", ["cityscapes", "mmsegmentation"]),
    ("基线", ["torchvision", "scikit-learn"]),
    ("Octave", ["octave", "octave-docs"]),
    ("matrix", ["numpy-docs", "octave-docs"]),
    ("矩阵", ["numpy-docs", "octave-docs"]),
    ("imread", ["octave-docs", "skimage-docs"]),
    ("imagesc", ["octave-docs", "octave"]),
    ("数据类型", ["numpy-docs", "octave-docs"]),
    ("坐标系", ["dip-wiki", "affine"]),
    ("采样", ["dip-wiki", "bilinear"]),
    ("量化位深", ["dip-wiki", "entropy"]),
]

# 每章「扩展学习」小节的精读清单
CHAPTER_RESOURCES = {
    "00": (["dip-wiki", "cs231n", "skimage", "octave", "paperswithcode"], "image processing textbook classical deep learning"),
    "01": (["octave", "octave-docs", "octave-image-pkg", "imagej"], "GNU Octave image processing examples"),
    "02": (["numpy-docs", "convolution", "dip-wiki", "psnr", "ssim"], "image as matrix convolution boundary handling"),
    "03": (["hist-eq", "clahe", "gamma", "skimage-docs"], "histogram equalization Octave"),
    "04": (["kernel-wiki", "gaussian-blur", "median-filter", "bilateral", "opencv-docs"], "image filtering gaussian median Octave"),
    "05": (["dft", "fft", "dip-wiki", "skimage-docs"], "2D FFT frequency domain filtering Octave"),
    "06": (["wiener", "nlm", "psnr", "ssim", "dncnn"], "image restoration Wiener filter Octave"),
    "07": (["affine", "homography", "bilinear", "sift"], "image registration affine Octave"),
    "08": (["hsv", "cielab", "dip-wiki", "opencv-docs"], "color space conversion white balance Octave"),
    "09": (["morphology", "watershed", "distance-transform", "skimage-docs"], "mathematical morphology Octave"),
    "10": (["sobel", "canny", "opencv-docs", "skimage-docs"], "Canny edge detector Octave"),
    "11": (["harris", "sift", "orb", "hough", "ransac"], "SIFT ORB feature matching Octave"),
    "12": (["otsu", "kmeans", "graphcut", "active-contour", "watershed"], "image segmentation Otsu Octave"),
    "13": (["image-moment", "lbp", "glcm", "scikit-learn"], "texture feature LBP GLCM Hu moments"),
    "14": (["jpeg", "dct", "huffman", "entropy", "wavelet"], "JPEG DCT compression Octave"),
    "15": (["skimage-docs", "opencv-docs", "imagej", "paperswithcode"], "classical image processing pipeline project"),
    "16": (["sift", "scikit-learn", "cs231n", "kmeans"], "bag of visual words SVM image classification"),
    "17": (["cnn-wiki", "backprop", "d2l", "pytorch-tutorials", "cs231n"], "CNN from scratch numpy tutorial"),
    "18": (["resnet", "torchvision", "timm", "convnext", "transfer-learning"], "transfer learning image classification PyTorch"),
    "19": (["imagenet", "coco", "torchmetrics", "pycocotools", "albumentations"], "train validation split data leakage computer vision"),
    "20": (["mmpretrain", "gradcam", "captum", "torchmetrics", "distill"], "Grad-CAM image classification PyTorch"),
    "21": (["ultralytics", "mmdetection", "detectron2", "detr", "pycocotools"], "object detection YOCO YOLO open source"),
    "22": (["mmsegmentation", "unet-pytorch", "mask2former", "sam", "monai"], "semantic instance segmentation open source"),
    "23": (["dncnn", "real-esrgan", "esrgan", "psnr", "ssim"], "image denoising super resolution deep learning"),
    "24": (["gan-wiki", "cyclegan", "stylegan3", "ddpm", "hf-diffusers"], "diffusion model image generation open source"),
    "25": (["vit", "swin", "clip", "dinov2", "llava"], "vision transformer multimodal foundation model"),
    "26": (["onnx", "onnxruntime", "tensorrt", "openvino", "ncnn"], "model deployment quantization pruning CV"),
    "A": (["octave-docs", "skimage-docs", "opencv-docs", "cs231n", "d2l"], "image processing algorithms cheat sheet"),
}

DEFAULT_KEYS = ["dip-wiki", "skimage-docs", "cs231n"]


def anchor(key, label=None):
    name, url, _desc, _cat = R[key]
    return ('<a href="' + html_mod.escape(url, quote=True) + '" target="_blank" rel="noopener">'
            + html_mod.escape(label or name) + "</a>")


def links_for_point(chapter_id, point, max_links=2):
    """知识点地图里逐条挂 1～2 个扩展学习链接。"""
    hits = []
    for kw, keys in TOPIC_RULES:
        if kw.lower() in point.lower():
            for k in keys:
                if k not in hits:
                    hits.append(k)
            if len(hits) >= max_links:
                break
    if not hits:
        hits = list(CHAPTER_RESOURCES.get(chapter_id, (DEFAULT_KEYS, ""))[0])[:max_links]
    return " · ".join(anchor(k) for k in hits[:max_links])


def repo_card(key, why=""):
    """下卷「开源工程」栏目的单张卡片。"""
    name, url, desc, cat = R[key]
    out = ['<div class="repo-card">']
    out.append("<h3>" + anchor(key, name) + "</h3>")
    out.append('<span class="tag">' + html_mod.escape(cat) + " · 官方/开源实现</span>")
    out.append("<p>" + html_mod.escape(desc) + "</p>")
    if why:
        out.append('<span class="why"><strong>怎么用</strong>：' + html_mod.escape(why) + "</span>")
    out.append('<p style="margin:0"><code>' + html_mod.escape(url) + "</code></p>")
    out.append("</div>")
    return "\n".join(out)


def search_url(query, site="github"):
    if site == "github":
        from urllib.parse import quote
        return "https://github.com/search?q=" + quote(query) + "&amp;type=repositories"
    from urllib.parse import quote
    return "https://www.google.com/search?q=" + quote(query)


def chapter_links_html(chapter_id, root="../../"):
    keys, query = CHAPTER_RESOURCES.get(chapter_id, (DEFAULT_KEYS, "image processing"))
    out = ["<p>以下资料按本章知识点挑选，可直接精读或对照源码；知识点地图里每一条也挂了 1～2 个直达链接。</p>", "<ul>"]
    for k in keys:
        name, _url, desc, cat = R[k]
        out.append("<li><strong>" + html_mod.escape(name) + "</strong>（" + html_mod.escape(cat) + "）："
                   + html_mod.escape(desc) + "<br>" + anchor(k) + "</li>")
    out.append("</ul>")
    out.append('<p class="code-hint">继续扩展：'
               '<a href="' + search_url(query) + '" target="_blank" rel="noopener">在 GitHub 检索本章相关开源工程</a> · '
               '<a href="' + search_url(query, "web") + '" target="_blank" rel="noopener">按本章主题检索资料</a> · '
               '<a href="' + root + 'index.html#resources">全书参考资源总表</a> · '
               '<a href="' + root + 'appendix/index.html">附录 A 速查与链接总表</a></p>')
    return "\n".join(out)


def all_resources_html():
    """附录 A.7：全书资源总表，按分类分组。"""
    cats = {}
    for key, (name, url, desc, cat) in R.items():
        cats.setdefault(cat, []).append((key, name, desc))
    order = ["工具", "文档", "课程", "百科", "数据集", "框架", "分类", "检测", "分割",
             "复原", "生成", "评测", "标注", "部署"]
    out = ["<p>本书全部外部链接的唯一来源，按用途分组。所有链接同时出现在对应章节的「知识点地图」与「扩展学习」里。</p>"]
    for cat in order:
        if cat not in cats:
            continue
        out.append("<h3>" + cat + "（" + str(len(cats[cat])) + "）</h3>")
        out.append('<table><thead><tr><th style="width:26%">名称</th><th>说明</th></tr></thead><tbody>')
        for key, name, desc in cats[cat]:
            out.append("<tr><td>" + anchor(key, name) + "</td><td>" + html_mod.escape(desc) + "</td></tr>")
        out.append("</tbody></table>")
    return "\n".join(out)


def repo_keys_by_chapter(chapter_ids):
    """附录 A.3：下卷开源工程总表用。"""
    keys = []
    for cid in chapter_ids:
        for k, _why in _chapter_repo_keys(cid):
            if k not in keys:
                keys.append(k)
    return keys


def _chapter_repo_keys(chapter_id):
    from book_data import CHAPTERS
    for ch in CHAPTERS:
        if ch["id"] == chapter_id:
            return ch["repos"]
    return []
