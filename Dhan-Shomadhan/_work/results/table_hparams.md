# Hyperparameters of every reported experiment

Every value is read from config.json of the experiment's runs (not typed in). Values are identical across the 5 splits of every experiment. E1-U and E1-WW are aliases that read the run folder named in the second column. Not part of config.json because they are fixed in the code: optimiser AdamW; stage 1 trains the classifier head only at a constant lr, stage 2 all weights with a linear warmup then cosine decay per optimiser step; mixed precision (fp16 autocast) on CUDA only, cross-entropy with the label smoothing above, checkpoint = best validation macro-F1 on the domains the model trained on. Training augmentation: random crop of 60%-100% of the area, random horizontal and vertical flips, rotation up to +-15 degrees, brightness +-0.2, contrast +-0.2, saturation +-0.15, hue +-0.02; evaluation images are only resized. Rows that are not complete yet read 'pending'.

| Experiment | Run folder | Backbone | Pretrained weights | Input mode | Input HxW | Train on | Checkpoint chosen on (val) | Composites per epoch | Linear-probe epochs x lr | Fine-tune epochs (max) | Learning rate | Weight decay | Warmup epochs | Label smoothing | Batch size x accumulation | Gradient clip norm | Early-stop patience | Dropout |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E0-squash | E0-squash | resnet50 | ResNet50_Weights.IMAGENET1K_V2 | squash | 320x320 | white + field | white + field | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E0-pad | E0-pad | resnet50 | ResNet50_Weights.IMAGENET1K_V2 | pad | 320x320 | white + field | white + field | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E0-rect | E0-rect | resnet50 | ResNet50_Weights.IMAGENET1K_V2 | rect | 448x224 | white + field | white + field | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E1-U | E0-rect | resnet50 | ResNet50_Weights.IMAGENET1K_V2 | rect | 448x224 | white + field | white + field | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E1-WW | E1-WF | resnet50 | ResNet50_Weights.IMAGENET1K_V2 | rect | 448x224 | white | white | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E1-FF | E1-FF | resnet50 | ResNet50_Weights.IMAGENET1K_V2 | rect | 448x224 | field | field | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E1-WF | E1-WF | resnet50 | ResNet50_Weights.IMAGENET1K_V2 | rect | 448x224 | white | white | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E2-cnx-U | E2-cnx-U | convnext_tiny | ConvNeXt_Tiny_Weights.IMAGENET1K_V1 | rect | 448x224 | white + field | white + field | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E2-cnx-WF | E2-cnx-WF | convnext_tiny | ConvNeXt_Tiny_Weights.IMAGENET1K_V1 | rect | 448x224 | white | white | - | 2 x 0.001 | 30 | 0.0001 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E2-swin-U | E2-swin-U | swin_t | Swin_T_Weights.IMAGENET1K_V1 | rect | 448x224 | white + field | white + field | - | 2 x 0.001 | 30 | 0.0003 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E2-swin-WF | E2-swin-WF | swin_t | Swin_T_Weights.IMAGENET1K_V1 | rect | 448x224 | white | white | - | 2 x 0.001 | 30 | 0.0003 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E3-A | E3-A | swin_t | Swin_T_Weights.IMAGENET1K_V1 | rect | 448x224 | white + field + composites | white + field | 0.5x | 2 x 0.001 | 30 | 0.0003 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
| E3-A-WF | E3-A-WF | swin_t | Swin_T_Weights.IMAGENET1K_V1 | rect | 448x224 | white + composites | white | 0.5x | 2 x 0.001 | 30 | 0.0003 | 0.05 | 1 | 0.1 | 32 x 1 | 1 | 10 | 0.2 |
