import pandas as pd
import matplotlib.pyplot as plt
import os

def read_losses(folder_path, num_generations):
    avg_losses = []
    best_losses = []
    
    for i in range(1, num_generations + 1):
        file_path = os.path.join(folder_path, f"gen_{i}.csv")
        
        if not os.path.exists(file_path):
            avg_losses.append(None)
            best_losses.append(None)
            continue
        
        df = pd.read_csv(file_path)
        filtered_losses = df[df["loss"] != 100]["loss"]
        
        avg_loss = filtered_losses.mean()
        best_loss = filtered_losses.min()
        
        avg_losses.append(avg_loss)
        best_losses.append(best_loss)
    
    return avg_losses, best_losses

def plot_losses(directories, labels, num_generations):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    markers = ["o", "s", "^"]  # Different markers for distinction
    linestyles = ["-", "--", ":"]  # Different line styles
    colors = ["b", "r", "g"]  # Different colors
    
    for idx, folder in enumerate(directories):
        avg_losses, best_losses = read_losses(folder, num_generations)
        
        axes[0].plot(range(1, num_generations + 1), avg_losses, 
                     marker=markers[idx], linestyle=linestyles[idx], color=colors[idx], label=f"{labels[idx]} - Avg Loss")
        axes[1].plot(range(1, num_generations + 1), best_losses, 
                     marker=markers[idx], linestyle=linestyles[idx], color=colors[idx], label=f"{labels[idx]} - Best Loss")
    
    axes[0].set_xlabel("Generation")
    axes[0].set_ylabel("Loss")
    axes[0].set_title("Average Loss Per Generation")
    axes[0].legend()
    axes[0].grid(True)
    
    axes[1].set_xlabel("Generation")
    axes[1].set_ylabel("Loss")
    axes[1].set_title("Best Loss Per Generation")
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.show()
    
# Example usage
directories = ["generations_quadratic", "generations_cubic", "generations_quartic"]
labels = ["quadratic", "cubic", "quartic"]
num_generations = 15

plot_losses(directories, labels, num_generations)