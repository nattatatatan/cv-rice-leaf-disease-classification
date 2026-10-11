
```
                    DATASET
                       │
                       ▼
               Dataset analysis
                       │
                       ▼
                ┌──────────────┐
                │   Baseline   │
                │ pretrained   │
                │     CNN      │
                └──────┬───────┘
                       │
                       ▼
             Domain-wise evaluation
                       │
              ┌────────┴────────┐
              ▼                 ▼
        White → White      Field → Field
              │                 │
              └────────┬────────┘
                       ▼
                Cross-domain test
                       │
                       ▼
            White → Field performance
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       stronger CNN             ViT
             │                   │
             └─────────┬─────────┘
                       ▼
               Best architecture
                       │
                       ▼
             Segmentation experiment
                       │
                       ▼
              White-trained leaf
                segmentation
                       │
                       ▼
             Classification using
              segmented/cropped leaf
                       │
                       ▼
            Compare cross-domain
                 performance
```