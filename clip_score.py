import torch
from pathlib import Path
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
print("CLIP loaded")

prompts = [
    "an ordinary, everyday photograph",
    "a technical image such as a chart, map, diagram, or satellite photo",
    "a real photograph of something so strange, staged, or uncanny that it looks fake",
]

def weird_score(image):
    image = image.convert("RGB")
    inputs = clip_processor(text=prompts, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = clip_model(**inputs)
    probabilities = outputs.logits_per_image.softmax(dim=1)[0]
    return probabilities[-1].item()


if __name__ == "__main__":
    scores = []
    for image_path in Path("weird-final").glob("*.png"):
        image = Image.open(image_path)
        scores.append((weird_score(image), image_path.name))

    for image_path in Path("weird-images").glob("*.jpg"):
        image = Image.open(image_path)
        scores.append((weird_score(image), "SEED: " + image_path.name))

    scores.sort(reverse=True)
    for score, name in scores:
        print(round(score, 3), name)
