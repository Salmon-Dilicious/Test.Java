import os
from PIL import Image
import numpy as np

TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn.functional as F
    import torchvision.transforms as transforms
    import torchvision.models as models
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    print("PyTorch 未安裝或有問題，使用簡化版本")


def calculate_contrastive_loss(D_x1, D_x2, label, C=2.0):
    """
    計算標準對比損失。
    label: 1 (正樣本，應極大化相似度)，0 (負樣本，應極小化相似度)
    """
    if TORCH_AVAILABLE:
        l2_distance = F.pairwise_distance(D_x1, D_x2, p=2)
        loss_positive = label * torch.pow(l2_distance, 2)
        loss_negative = (1 - label) * torch.pow(torch.clamp(C - l2_distance, min=0.0), 2)
        return (loss_positive + loss_negative).mean()
    else:
        l2_distance = np.linalg.norm(D_x1 - D_x2)
        loss_positive = label * (l2_distance ** 2)
        loss_negative = (1 - label) * (max(0, C - l2_distance) ** 2)
        return loss_positive + loss_negative


def calculate_pairwise_distance(D_x1, D_x2):
    if TORCH_AVAILABLE:
        D_x1 = D_x1.view(D_x1.size(0), -1)
        D_x2 = D_x2.view(D_x2.size(0), -1)
        return F.pairwise_distance(D_x1, D_x2, p=2).mean()
    else:
        return np.linalg.norm(D_x1.flatten() - D_x2.flatten())


def extract_histogram_features(image, bins=32):
    image = image.resize((224, 224))
    image_array = np.array(image)
    histogram = []
    for channel in range(3):
        hist = np.histogram(image_array[:, :, channel], bins=bins, range=(0, 255))[0].astype(np.float32)
        histogram.append(hist)
    histogram = np.concatenate(histogram)
    histogram /= np.sum(histogram) + 1e-6
    return histogram


def load_image_and_extract_features(image_path):
    """
    載入圖片、提取特徵、展平並執行 L2 正規化。
    """
    image = Image.open(image_path).convert('RGB')
    if TORCH_AVAILABLE:
        image = transform(image).unsqueeze(0)
        with torch.no_grad():
            features = model(image)
            features = torch.flatten(features, 1)
            features = F.normalize(features, p=2, dim=1)
        return features
    else:
        features = extract_histogram_features(image)
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        return np.array([features])

if TORCH_AVAILABLE:
    # 載入預訓練的 ResNet18 模型作為特徵提取器
    model = models.resnet18(pretrained=True)
    model = torch.nn.Sequential(*list(model.children())[:-1])  # 移除最後的分類層
    model.eval()

    # 定義圖片預處理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
else:
    print("使用簡化特徵提取（RGB 直方圖）")

# 圖片資料夾路徑
image_dirs = [
    r"C:\Users\user\Pictures\Saved Pictures\aaa",
    r"C:\Users\user\Pictures\Saved Pictures\bbb",
    r"C:\Users\user\Pictures\Saved Pictures\ccc"
]

# 載入圖片並提取特徵
features = []
image_paths = []
for dir_path in image_dirs:
    files = [f for f in os.listdir(dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if files:
        image_path = os.path.join(dir_path, files[0])
        feature = load_image_and_extract_features(image_path)
        features.append(feature)
        image_paths.append(image_path)
    else:
        print(f"警告: {dir_path} 中沒有找到圖片檔案")

# 確保有至少兩張圖片
if len(features) < 2:
    print("錯誤: 需要至少兩張圖片來進行比較學習")
    exit()

feature_img_1 = features[0]
feature_img_2 = features[1]
if len(features) > 2:
    feature_img_3 = features[2]
else:
    if TORCH_AVAILABLE:
        feature_img_3 = torch.rand(1, 512)  # 如果沒有第三張，使用隨機向量
    else:
        feature_img_3 = np.random.rand(1, 3)  # RGB 隨機

# 執行多張圖片特徵之交叉比對
compare_1_2 = calculate_pairwise_distance(feature_img_1, feature_img_2)
compare_1_3 = calculate_pairwise_distance(feature_img_1, feature_img_3)

print("數字越小越相似")
print(f"圖片1: {image_paths[0]}")
print(f"圖片2: {image_paths[1]}")
print(f"圖片3: {image_paths[2]}")
print(f"圖片 1 與圖片 2 比對值: {compare_1_2.item() if TORCH_AVAILABLE else compare_1_2:.4f}")
print(f"圖片 1 與圖片 3 比對值: {compare_1_3.item() if TORCH_AVAILABLE else compare_1_3:.4f}")
