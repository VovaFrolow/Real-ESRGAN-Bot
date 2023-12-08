import os
import torch
from PIL import Image
import numpy as np
from RealESRGAN import RealESRGAN


def process_image(image_path, mode):
    if not os.path.exists("results"):
        os.mkdir("results")

    print(f"Processing image {image_path}")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = RealESRGAN(device, scale=mode)
    model.load_weights(f'weights/RealESRGAN_x{mode}.pth', download=True)
    image = Image.open(f"{image_path}").convert('RGB')
    sr_image = model.predict(image)
    image_file = os.path.basename(image_path)
    save_path = f'results/{image_file}'
    sr_image.save(save_path)

    return save_path
