from diffusers import StableDiffusionPipeline
import torch
pipe = StableDiffusionPipeline.from_pretrained(
    "runwaym1/stable-diffusion-v1-5"
)
pipe = pipe.to("cpu")
print("Success")