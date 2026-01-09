from dataset import XDViolenceDataset
from model import MultiAgentViolanceModel
from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score, accuracy_score, confusion_matrix, f1_score, ConfusionMatrixDisplay
import numpy as np
import os
from collections import Counter
import matplotlib.pyplot as plt

root_dir = "C:\\Users\\Win10\\Desktop\\DeepLearning\\Project\\Smart-City-Violation-Detection\\data\\XDViolance"
batch_size = 8
num_epochs = 40
learning_rate = 1e-4
rgb_data = True
flow_data = False
audio_data = True
train_size = 19770  # Set to 3000 for quick testing, set to 19770 for full training
test_size = 4000

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_chk_dir = "checkpoints"
os.makedirs(model_chk_dir, exist_ok=True)

train_dataset = XDViolenceDataset(root_dir, split="train", data_size=train_size, is_audio=audio_data, is_visual=rgb_data, is_motion=flow_data)
test_dataset = XDViolenceDataset(root_dir, split="test", data_size=test_size, is_audio=audio_data, is_visual=rgb_data, is_motion=flow_data)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset,batch_size=batch_size, shuffle=False)

model = MultiAgentViolanceModel(is_audio=audio_data, is_visual=rgb_data, is_motion=flow_data).to(device)

criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(params=model.parameters(), lr=learning_rate, weight_decay=1e-5)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer=optimizer, patience=5)

def train_model():

    best_auc = 0.0

    for epoch in range(num_epochs):

        epoch_train_loss, epoch_val_loss = 0.0, 0.0
        val_outputs_list = []
        val_labels_list = []
        threshold = 0.19
    
        model.train()

        for batch in train_loader:
            
            f_audio = batch.get("audio").to(device) if "audio" in batch else None
            f_rgb = batch.get("rgb").to(device) if "rgb" in batch else None
            f_flow = batch.get("flow").to(device) if "flow" in batch else None
            labels = batch["label"].to(device).unsqueeze(1)
            #Tryin label smoothing
            labels = labels * 0.9 + 0.05
            
            optimizer.zero_grad()
            outputs = model(audio=f_audio, rgb=f_rgb, flow=f_flow)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            epoch_train_loss += loss.item()
        
        epoch_train_loss /= len(train_loader)

        model.eval()
        
        for batch in test_loader:

            f_audio = batch.get("audio").to(device) if "audio" in batch else None
            f_rgb = batch.get("rgb").to(device) if "rgb" in batch else None
            f_flow = batch.get("flow").to(device) if "flow" in batch else None
            labels = batch["label"].to(device).unsqueeze(1)
            
            with torch.no_grad():
                outputs = model(audio=f_audio, rgb=f_rgb, flow=f_flow)
                loss = criterion(outputs, labels)
                epoch_val_loss += loss.item()

                preds = torch.sigmoid(outputs)
                val_outputs_list.extend(preds.cpu().numpy())
                val_labels_list.extend(labels.cpu().numpy())

        epoch_val_loss /= len(test_loader)
        accuracy = accuracy_score(np.array(val_labels_list), np.array(val_outputs_list) > threshold)
        roc_auc = roc_auc_score(val_labels_list, val_outputs_list)
        f1 = f1_score(np.array(val_labels_list), np.array(val_outputs_list) > threshold)
        scheduler.step(epoch_val_loss)
        
        print(f"Epoch {epoch+1}/{num_epochs} | Train Loss: {epoch_train_loss:.4f} | Val Loss: {epoch_val_loss:.4f} | Acc: {accuracy:.4f} | AUC: {roc_auc:.4f} | F1: {f1:.4f}")
        
        if roc_auc > best_auc:
            best_auc = roc_auc
            model_name = str(model.is_audio) + str(model.is_visual) + str(model.is_motion) + "best_model.pth"
            torch.save(model.state_dict(), os.path.join(model_chk_dir, model_name))
            print("Best model saved.")

if __name__ == "__main__":
    train_model()

    #Load best model for testing
    model = MultiAgentViolanceModel(is_audio=audio_data, is_visual=rgb_data, is_motion=flow_data).to(device)
    model_name = str(model.is_audio) + str(model.is_visual) + str(model.is_motion) + "best_model.pth"
    model.load_state_dict(torch.load(os.path.join(model_chk_dir, model_name)))

    val_dataset = XDViolenceDataset(root_dir, split="test", data_size=test_size, is_audio=audio_data, is_visual=rgb_data, is_motion=flow_data)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    labels = [val_dataset._parse_label(vid).item() for vid in val_dataset.video_ids]
    print(Counter(labels))

    model.eval()
    threshold = 0.35

    val_outputs_list = []
    val_labels_list = []

    for batch in val_loader:

        f_audio = batch.get("audio").to(device) if "audio" in batch else None
        f_rgb = batch.get("rgb").to(device) if "rgb" in batch else None
        f_flow = batch.get("flow").to(device) if "flow" in batch else None
        labels = batch["label"].to(device).unsqueeze(1)
        
        with torch.no_grad():
            outputs = model(audio=f_audio, rgb=f_rgb, flow=f_flow)
            preds = torch.sigmoid(outputs)
            val_outputs_list.extend(preds.cpu().numpy())
            val_labels_list.extend(labels.cpu().numpy())

    print(f"Val Output {len(val_outputs_list)} Val Labels {len(val_labels_list)}")

    accuracy = accuracy_score(np.array(val_labels_list), np.array(val_outputs_list) > threshold)
    roc_auc = roc_auc_score(val_labels_list, val_outputs_list)
    cm = confusion_matrix(np.array(val_labels_list), np.array(val_outputs_list) > threshold)
    f1 = f1_score(np.array(val_labels_list), np.array(val_outputs_list) > threshold)

    cm_display = ConfusionMatrixDisplay(cm, display_labels=["Non-Violence", "Violence"])
    cm_display.plot()
    plt.title(f"Confusion Matrix (Acc: {accuracy:.4f}, AUC: {roc_auc:.4f}, F1: {f1:.4f})")
    plt.show()