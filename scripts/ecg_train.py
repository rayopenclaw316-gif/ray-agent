#!/usr/bin/env python3
"""
ECG 心律不整分類 — 1D CNN
資料集：MIT-BIH Arrhythmia (Kaggle: shayanfazeli/heartbeat)
分類目標：
  0 = 正常 (Normal)
  1 = 上心室早期收縮 (Supraventricular)
  2 = 心室早期收縮 (Ventricular)
  3 = 融合搏動 (Fusion)
  4 = 未分類 (Unknown/Unclassifiable)
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import time

# ─────────────────────────────────────────
# 0. 路徑與超參數
# ─────────────────────────────────────────
BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE, 'data', 'heartbeat')
OUTPUT_DIR  = os.path.join(BASE, 'output', 'ecg')
os.makedirs(OUTPUT_DIR, exist_ok=True)

BATCH_SIZE  = 256    # 每批送入模型的樣本數
EPOCHS      = 20     # 完整訓練資料跑過的次數
LR          = 1e-3   # Adam 學習率
NUM_CLASSES = 5      # 心律類別數
SEQ_LEN     = 187    # 每筆 ECG 訊號的時間點數（特徵數）
DEVICE      = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
print(f'使用裝置：{DEVICE}')

# ─────────────────────────────────────────
# 1. 資料集類別
# ─────────────────────────────────────────
class ECGDataset(Dataset):
    def __init__(self, csv_path):
        df = pd.read_csv(csv_path, header=None)
        # df.shape = (N, 188)：前 187 欄為訊號，最後 1 欄為標籤
        self.X = torch.tensor(df.iloc[:, :SEQ_LEN].values, dtype=torch.float32)
        # X.shape = (N, 187)
        self.y = torch.tensor(df.iloc[:, -1].values, dtype=torch.long)
        # y.shape = (N,)

    def __len__(self):
        return len(self.y)   # 回傳樣本總數

    def __getitem__(self, idx):
        # 取出第 idx 筆，將訊號 unsqueeze 成 (1, 187) 表示 1 個 channel
        # Conv1d 需要輸入格式：(batch, channel, length)
        return self.X[idx].unsqueeze(0), self.y[idx]
        # 回傳：x.shape=(1,187), y.shape=scalar

# ─────────────────────────────────────────
# 2. 模型架構
# ─────────────────────────────────────────
class ECG1DCNN(nn.Module):
    """
    輸入維度流程（batch=B）：
    ┌─────────────────────────────────────────────────────┐
    │ 輸入         (B, 1, 187)                            │
    │ Conv1d-1     (B, 32, 183)  kernel=5, stride=1       │
    │ ReLU                                                 │
    │ MaxPool1d-1  (B, 32, 91)   kernel=2, stride=2       │
    │ Conv1d-2     (B, 64, 87)   kernel=5, stride=1       │
    │ ReLU                                                 │
    │ MaxPool1d-2  (B, 64, 43)   kernel=2, stride=2       │
    │ Conv1d-3     (B, 128, 41)  kernel=3, stride=1       │
    │ ReLU                                                 │
    │ MaxPool1d-3  (B, 128, 20)  kernel=2, stride=2       │
    │ Flatten      (B, 2560)     128×20=2560              │
    │ Linear-1     (B, 256)                               │
    │ ReLU + Dropout(0.5)                                 │
    │ Linear-2     (B, 64)                                │
    │ ReLU                                                 │
    │ Linear-3     (B, 5)        輸出 5 類 logits         │
    └─────────────────────────────────────────────────────┘
    """
    def __init__(self):
        super().__init__()

        # ── 卷積塊 1 ──────────────────────────────────────
        # 輸入：(B, 1, 187)
        # kernel=5：每次看 5 個連續時間點的局部特徵
        # padding=0（預設）：長度計算 = 187 - 5 + 1 = 183
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=32, kernel_size=5)
        # 輸出：(B, 32, 183)

        # MaxPool1d：每 2 個點取最大值，步長 2，長度減半 183//2=91
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        # 輸出：(B, 32, 91)

        # ── 卷積塊 2 ──────────────────────────────────────
        # 輸入：(B, 32, 91)  → 91 - 5 + 1 = 87
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=5)
        # 輸出：(B, 64, 87)

        self.pool2 = nn.MaxPool1d(kernel_size=2)
        # 輸出：(B, 64, 43)

        # ── 卷積塊 3 ──────────────────────────────────────
        # 輸入：(B, 64, 43)  → 43 - 3 + 1 = 41
        self.conv3 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3)
        # 輸出：(B, 128, 41)

        self.pool3 = nn.MaxPool1d(kernel_size=2)
        # 輸出：(B, 128, 20)  （41//2=20）

        # ── 全連接層 ──────────────────────────────────────
        # Flatten 後：128 × 20 = 2560
        self.fc1 = nn.Linear(128 * 20, 256)
        # 輸出：(B, 256)

        self.dropout = nn.Dropout(p=0.5)  # 訓練時隨機關閉 50% 神經元，防過擬合

        self.fc2 = nn.Linear(256, 64)
        # 輸出：(B, 64)

        self.fc3 = nn.Linear(64, NUM_CLASSES)
        # 輸出：(B, 5)  → 送入 CrossEntropyLoss 計算損失

        self.relu = nn.ReLU()  # 非線性激活函數，保留正值、抑制負值

    def forward(self, x):
        # x: (B, 1, 187)

        x = self.relu(self.conv1(x))   # (B, 32, 183)
        x = self.pool1(x)              # (B, 32, 91)

        x = self.relu(self.conv2(x))   # (B, 64, 87)
        x = self.pool2(x)              # (B, 64, 43)

        x = self.relu(self.conv3(x))   # (B, 128, 41)
        x = self.pool3(x)              # (B, 128, 20)

        x = x.view(x.size(0), -1)      # Flatten: (B, 2560)

        x = self.relu(self.fc1(x))     # (B, 256)
        x = self.dropout(x)            # (B, 256)，隨機遮蔽

        x = self.relu(self.fc2(x))     # (B, 64)

        x = self.fc3(x)                # (B, 5)  ← 最終 logits（未經 softmax）
        return x


# ─────────────────────────────────────────
# 3. 動態模型（供 Grid Search 使用）
# ─────────────────────────────────────────
class ECG1DCNN_Dynamic(nn.Module):
    def __init__(self, fc1_out=256):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 32, 5);  self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(32, 64, 5); self.pool2 = nn.MaxPool1d(2)
        self.conv3 = nn.Conv1d(64, 128, 3); self.pool3 = nn.MaxPool1d(2)

        self.fc1     = nn.Linear(128 * 20, fc1_out)
        self.dropout = nn.Dropout(p=0.5)
        self.fc2     = nn.Linear(fc1_out, 64)
        self.fc3     = nn.Linear(64, NUM_CLASSES)
        self.relu    = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.conv1(x)); x = self.pool1(x)
        x = self.relu(self.conv2(x)); x = self.pool2(x)
        x = self.relu(self.conv3(x)); x = self.pool3(x)
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# ─────────────────────────────────────────
# 4. 訓練與驗證函式
# ─────────────────────────────────────────
def train_epoch(model, loader, criterion, optimizer):
    model.train()          # 開啟訓練模式（Dropout 生效）
    total_loss, correct = 0.0, 0
    for X_batch, y_batch in loader:
        X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
        # X_batch: (B, 1, 187)  y_batch: (B,)

        optimizer.zero_grad()              # 清除上一步的梯度
        logits = model(X_batch)            # 前向傳播 → logits: (B, 5)
        loss = criterion(logits, y_batch)  # CrossEntropy：比較預測與真實類別
        loss.backward()                    # 反向傳播：計算各參數的梯度
        optimizer.step()                   # 梯度下降：更新所有參數權重

        total_loss += loss.item() * len(y_batch)
        correct    += (logits.argmax(1) == y_batch).sum().item()

    n = len(loader.dataset)
    return total_loss / n, correct / n   # 平均 loss, accuracy


def eval_epoch(model, loader, criterion):
    model.eval()           # 關閉 Dropout（推論模式）
    total_loss, correct = 0.0, 0
    with torch.no_grad():  # 不計算梯度，節省記憶體
        for X_batch, y_batch in loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            logits = model(X_batch)
            loss   = criterion(logits, y_batch)
            total_loss += loss.item() * len(y_batch)
            correct    += (logits.argmax(1) == y_batch).sum().item()
    n = len(loader.dataset)
    return total_loss / n, correct / n


# ─────────────────────────────────────────
# 5. 主程式
# ─────────────────────────────────────────
def main():
    # 載入資料
    print('載入資料集...')
    train_set = ECGDataset(os.path.join(DATA_DIR, 'mitbih_train.csv'))
    test_set  = ECGDataset(os.path.join(DATA_DIR, 'mitbih_test.csv'))
    print(f'  訓練集：{len(train_set)} 筆  測試集：{len(test_set)} 筆')

    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
    test_loader  = DataLoader(test_set,  batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # 建立模型
    model     = ECG1DCNN().to(DEVICE)
    criterion = nn.CrossEntropyLoss()          # 多分類標準損失函數
    optimizer = optim.Adam(model.parameters(), lr=LR)  # Adam 自動調整學習率

    # 記錄曲線
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    print(f'\n開始訓練（共 {EPOCHS} epochs）')
    for epoch in range(1, EPOCHS + 1):
        tr_loss, tr_acc = train_epoch(model, train_loader, criterion, optimizer)
        va_loss, va_acc = eval_epoch(model, test_loader,  criterion)

        history['train_loss'].append(tr_loss)
        history['train_acc'].append(tr_acc)
        history['val_loss'].append(va_loss)
        history['val_acc'].append(va_acc)

        print(f'Epoch {epoch:02d}/{EPOCHS}  '
              f'train_loss={tr_loss:.4f}  train_acc={tr_acc:.4f}  '
              f'val_loss={va_loss:.4f}  val_acc={va_acc:.4f}')

    # ── 儲存模型 ──
    model_path = os.path.join(OUTPUT_DIR, 'ecg_cnn.pth')
    torch.save(model.state_dict(), model_path)
    print(f'\n模型已儲存：{model_path}')

    # ── 繪製 Loss / Accuracy 曲線 ──
    epochs_range = range(1, EPOCHS + 1)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(epochs_range, history['train_loss'], label='Train')
    axes[0].plot(epochs_range, history['val_loss'],   label='Val')
    axes[0].set_title('Loss Curve');  axes[0].set_xlabel('Epoch');  axes[0].legend()

    axes[1].plot(epochs_range, history['train_acc'], label='Train')
    axes[1].plot(epochs_range, history['val_acc'],   label='Val')
    axes[1].set_title('Accuracy Curve');  axes[1].set_xlabel('Epoch');  axes[1].legend()

    plt.tight_layout()
    curve_path = os.path.join(OUTPUT_DIR, 'training_curve.png')
    plt.savefig(curve_path, dpi=150)
    print(f'訓練曲線已儲存：{curve_path}')

    # ── 混淆矩陣 ──
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            preds = model(X_batch.to(DEVICE)).argmax(1).cpu()
            all_preds.append(preds);  all_labels.append(y_batch)
    all_preds  = torch.cat(all_preds).numpy()
    all_labels = torch.cat(all_labels).numpy()

    class_names = ['Normal', 'Supraventricular', 'Ventricular', 'Fusion', 'Unknown']
    print('\n分類報告：')
    print(classification_report(all_labels, all_preds, target_names=class_names))

    cm = confusion_matrix(all_labels, all_preds)
    fig2, ax2 = plt.subplots(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names, ax=ax2)
    ax2.set_xlabel('Predicted');  ax2.set_ylabel('True')
    ax2.set_title('Confusion Matrix')
    plt.tight_layout()
    cm_path = os.path.join(OUTPUT_DIR, 'confusion_matrix.png')
    plt.savefig(cm_path, dpi=150)
    print(f'混淆矩陣已儲存：{cm_path}')


# ─────────────────────────────────────────
# 6. Grid Search 主程式
# ─────────────────────────────────────────
def main_grid_search():
    print('載入資料集...')
    train_set = ECGDataset(os.path.join(DATA_DIR, 'mitbih_train.csv'))
    test_set  = ECGDataset(os.path.join(DATA_DIR, 'mitbih_test.csv'))
    print(f'  訓練集：{len(train_set)} 筆  測試集：{len(test_set)} 筆')

    test_batch_sizes = [64, 256, 512]
    test_fc1_outs    = [128, 256, 512]
    experiment_results = []
    TEST_EPOCHS = 10

    for bs in test_batch_sizes:
        for fc_out in test_fc1_outs:
            print(f"\n{'='*50}")
            print(f"開始實驗 -> Batch Size: {bs} | FC1 Out: {fc_out}")
            print(f"{'='*50}")

            train_loader = DataLoader(train_set, batch_size=bs, shuffle=True,  num_workers=0)
            test_loader  = DataLoader(test_set,  batch_size=bs, shuffle=False, num_workers=0)

            model     = ECG1DCNN_Dynamic(fc1_out=fc_out).to(DEVICE)
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=LR)

            start_time  = time.time()
            best_val_acc = 0.0

            for epoch in range(1, TEST_EPOCHS + 1):
                tr_loss, tr_acc = train_epoch(model, train_loader, criterion, optimizer)
                va_loss, va_acc = eval_epoch(model, test_loader,  criterion)

                if va_acc > best_val_acc:
                    best_val_acc = va_acc

                if epoch == TEST_EPOCHS:
                    print(f"完成! 最終驗證準確率: {va_acc:.4f} (歷史最高: {best_val_acc:.4f})")

            end_time = time.time()

            experiment_results.append({
                'Batch Size':      bs,
                'FC1 Output':      fc_out,
                'Final Train Acc': round(tr_acc, 4),
                'Final Val Acc':   round(va_acc, 4),
                'Best Val Acc':    round(best_val_acc, 4),
                'Time (sec)':      round(end_time - start_time, 1),
            })

    print("\n\n實驗結果總表")
    results_df = pd.DataFrame(experiment_results)
    results_df = results_df.sort_values(by='Best Val Acc', ascending=False).reset_index(drop=True)
    print(results_df.to_string(index=False))

    csv_path = os.path.join(OUTPUT_DIR, 'grid_search_results.csv')
    results_df.to_csv(csv_path, index=False)
    print(f'\nGrid Search 結果已儲存：{csv_path}')


if __name__ == '__main__':
    main_grid_search()
