Created by: Nattan Chartsompong
Date of creation: Wed, 07 Oct 2026
Last updated: Wed, 07 Oct 2026
# Problem Statement

The client gives us:
> An image of a rice leaf, captured either against a white background or in a rice field, and the system must identify which of five diseases is present.

This is a supervised multi-class image classification. 

What make this dataset particularly interesting is that it also gives us two visual domains: one with white background and one with field background. 
- White background:
	- relatively uniform background
	- leaf is visually isolated
	- relatively predictable lighting
	- fewer irrelevant visual features
	- disease symptoms are easier to focus on
- Field background
	- variable background with varying soil, other leaves, stems, shadows, lighting, etc.
	- Visual clutter.
	- Different scales/orientations.

### Addressing Domain Expertise: ML vs DL

Classical machine-learning approaches typically require domain-informed feature engineering. For rice disease classification, the discriminative characteristics may involve complex combinations of colour, texture, lesion morphology and spatial arrangement, and designing a robust hand-crafted representation requires substantial domain knowledge.

Deep learning, however, can be used to learn task-specific visual representations directly from labelled images, reducing reliance on manually engineered features. However, the relatively small dataset makes training a deep network from scratch unsuitable. Transfer learning from a pretrained CNN is therefore adopted to leverage general visual representations learned from large-scale image data while adapting them to the rice disease classification task.

### Addressing Small Dataset

This dataset consists of 1106 images of five harmful diseases called Brown Spot, Leaf Scald, Rice Blast, Rice Tungro, and Sheath Blight. 

This is considered a small dataset for deep learning task. 

# Finding Reference

We are interested in:
- small plant dataset
- two visual domains
- deep learning
- transfer learning

## Deep Learning Based Models for Paddy Disease Identification and Classification: A Systematic Survey
Source: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10574294

The paper present a thorough exploration of deep learning (DL) models for the classification of paddy diseases. Especially relevant for this project is the presenting of various deep-learning models employed for disease detection, strategies used by researchers for improving the performance of DL models, and adaptations tailored for application-specific contexts

### Picking the Architecture

The paper present 3 major classes of architecture used for paddy disease detection: CNN-based models, Vision Transformers (ViT), and memory-efficient models. 

1. CNNs
	Most relevant to our problem is that they reported a custom CNN model by [[#Custom Convolutional Neural Network for Detection and Classification of Rice Plant Diseases|Singh et al.]] are reported to achieve 97.61% accuracy using a dataset limited to four disease classes and one healthy class. 
	In general, CNNs and their variants require rigorous parameter training and substantial computational resources, needing abundant labelled samples. They might struggle to capture complex leaf diseases due to limitations in modelling long-range dependencies and contextual information.
2. ViTs
	It is reported that a simplified ViT-based real-time plant disease classifier was implemented by Borhani et al. They combined attention blocks with CNN blocks to mitigate the lengthy prediction time, outperforming other models on small, medium, and large-scale datasets.
3. Memory-efficient models
	These models are more focused on memory efficiency rather than superior performance, so we'll skip these model architectures.

### Enhancing the Performance of DNN

1. Transfer Learning-based Models: In this process, a pre-trained neural network with weights from extensive prior training is selected as the base. The model is then adapted to the specific task by modifying layers and further fine-tuned to meet new requirements without needing to infer all parameters from scratch.
	- One especially relevant to our problem is the fine-tuning scheme by Latif et al.
	- The paper warns that The assumption of similarity between the source and target domains might transfer potential biases from the source domain to the target domain, compromising accuracy and fairness in paddy leaf disease detection systems.
2. Hybrid Models: amalgamation of multiple models has yielded superior classification accuracy compared to singular approaches.
	- For example, using diverse CNN models were systematically applied for intricate feature extraction. Then, these extracted features were effectively incorporated into a classification system utilising SVM.
	- Another example that is said to be effective on limited data is GCL model, which integrates LTSM, CNN and GAN. GAN augments the dataset, CNN extracts features, and LSTM performs disease classification.
	- Another interesting example is a deep ensemble model called PlantDet, incorporating InceptionResNetV2, EfficientNetV2L, and Xception. They use dataset comprising of five distinct paddy disease classes. However, the model only classify between healthy and unhealthy instead of individual disease classes.

### Application-Specific Model Adaptations

This section is particularly valuable for our problem as it discusses techniques for effective and precise identification and diagnosis of paddy disease.

1. Image segmentation: isolating the diseased regions from healthy parts of a leaf. 
	- This can be done utilising masks, or other various image processing techniques, and neural networks.
	- The paper mentioned that "segmenting diseased leaf parts from complex backgrounds is challenging due to variations in illumination, distance, and clutter, even in controlled environments." However, with our white background dataset, we could potentially train a segmentation model on white background and transfer the segmentation cross-domain to apply it on field background images.
	- The paper discussed a method called DNN_JOA by [[|Ramesh et al.]] where initially, RGB images were converted to HSV format and the hue component was utilised for background removal. Following this, clustering was applied to segment the diseased areas. 
2. Optimisation Algorithms and Techniques: the paper simply named a few hyperparameter search technique e.g. grid search tuner, random search tuner, Bayesian optimisation tuner, and hyperband tuner. 
	- Notably, David et al. introduced the innovative MUTPSO-CNN method, which systematically generates an optimised CNN structure tailored to the input dataset, outperforming traditional handcrafted CNN architectures with superior performance. I cannot access the exact reference provided in the paper but found another paper of the same name, mentioning the same method by [[#An Optimized Convolution Neural Network Architecture for Paddy Disease Classification|Saleem et al.]]

## Custom Convolutional Neural Network for Detection and Classification of Rice Plant Diseases

Source: https://www.sciencedirect.com/science/article/pii/S1877050923001795?via%3Dihub

This paper proposes a custom CNN architecture for detecting and classifying common diseases found in rice plants by **reducing the number of parameters associated with the network**, making the CNN smaller, faster, and less prone to overfitting.

The abstract compares **SGDM** and **Adam**:
- Four rice diseases:
    - Adam: **99.83%**
    - SGDM: **99.66%**
- When healthy leaves are also included:
    - Adam: **99.66%**
    - SGDM: **97.61%**

### Dataset
The first dataset includes 5932 images of infected rice leaves, including brownspots, tungro, blast, and bacterial blight. The second dataset contains 1400 images of healthy rice leaf. 

All the training images are augmented with simple image rotation and image flip operations (90-degree rotation, 180-degree rotation, 270-degree rotation, vertical flipping, horizontal flipping) to all images in the training set before the training begins. 

### Methodology

The pre-processing step of the methodology includes cropping the images to remove unwanted backgrounds and resizing all the images to 256X256 pixels. 

Following the pre-processing step, each class of the dataset is randomly split into the 80:20 proportion for training and testing. 

Then, the training samples are augmented to increase the number of images before the training process.

![[Pasted image 20261007140231.png]]
![[Pasted image 20261007140440.png]]

## Paddy Leaf Disease Detection Employing Transfer Learning

Source: https://ieeexplore.ieee.org/document/10441084

The dataset this paper have used consists of 1224 images, which is very close to our problem's dataset. 

The paper compare the performance of different Keras CNN models (Resnet 152 V2, Xception, Inception Resnet50) and YOLOv8 nano. The results showed that: among those models, YOLOv8 performed better than others achieving a score of 99.26% accuracy on the custom dataset for the diseases.

## Deep Learning Utilization in Agriculture: Detection of Rice Plant Diseases Using an Improved CNN Model

Source: https://www.mdpi.com/2223-7747/11/17/2230

The paper discuss the process of fine-tuning as consisting of four main steps:
- The CNN model is pre-trained.
- The last output layer is truncated, and all model designs and parameters are copied to generate a new CNN.
- The head of the CNN is replaced with a set of fully connected layers. Then the model parameters are initialized randomly.
- The output layer is trained from scratch, with all parameters fine-tuned based on the initial model.

In their work, two levels of fine-tuning were applied. 
1. The first consists of freezing all layers of feature extraction and unfreezing the FC levels at which classification is performed. 
2. Conversely, the second stage involves freezing the first layer of feature extraction and unfreezing the last feature extraction along with the fully connected layers. 
	This second stage requires more training and time; nonetheless, it is excepted to give better results. In this latter level, only the initial 10 layers of VGG16 are frozen, while the remaining layers are re-trained for fine-tuning.

![[Pasted image 20261007145608.png]]

## Recognition and classification of paddy leaf diseases using Optimized Deep Neural network with Jaya algorithm

Source: https://www.sciencedirect.com/science/article/pii/S2214317319300769?via%3Dihub

The paper discuss the recognition of agricultural plant diseases by utilising the [image processing](https://www.sciencedirect.com/topics/engineering/image-processing) techniques.

What caught my interest is their preprocessing method: for the background removal the [RGB images](https://www.sciencedirect.com/topics/physics-and-astronomy/rgb-image) are converted into HSV images and based on the hue and saturation parts [binary images](https://www.sciencedirect.com/topics/engineering/binary-image) are extracted to split the diseased and non-diseased part. For the segmentation of diseased portion, normal portion and background a clustering method is used.

## An Optimized Convolution Neural Network Architecture for Paddy Disease Classification

Source: https://www.techscience.com/cmc/v71n3/46471

In this paper, we are interested in the MUTPSO-CNN which is mentioned to search for an optimum CNN architecture for Paddy leaf disease classification.

The algorithm includes initialisation of swarm, fitness evaluation, calculating  the difference of particle, calculates the velocity, and update velocity.
```
Algorithm 2: MUTPSO-CNN algorithm  
13. Input: Parameter  
14. Pi.depth = rand(3, depth) ;  
15. for j = 1 to Pi.depth do  
16. if j == 1 then  
17. list layers[j] ←Insert-Convolution layer (kmax, mapsmax) ;  
18. else if j == Pi.depth then  
19. list layers[j] ← addFully Connected (nout) ;  
20. else if list layers[j-1].type == “fully-connected” then  
21. list layers[j] ← addFully Connected Layer (nmax) ;  
22. Else  
23. layer type ← rand(1, 3) ;  
24. if layer type == 1 then  
25. list layers[j] ←insert-Convolution layer (kmax, mapsmax) ;  
26. else if layer type == 2 then  
27. list layers[j] ← Insert-Pooling layer() ;  
28. Else  
29. list layers[j] ← Insert-Pooling layer() ;  
30. End
```

![[Pasted image 20261007152527.png]]![[Pasted image 20261007152546.png]]