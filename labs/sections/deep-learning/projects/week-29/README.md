# Week 29 Project: MNIST from Scratch

## Project overview
In this project, you will build a complete, end-to-end Handwritten Digit Classification system in pure NumPy. You will implement data loading, pixel preprocessing, a two-layer neural network `[784, 128, 10]`, He weight initialization, vectorized forward propagation, analytical backpropagation, and mini-batch SGD with Momentum, training the model to achieve at least 95.0% accuracy on the MNIST benchmark.

## Objectives
- Load and parse the 70,000-sample MNIST dataset into normalized 784-D floating point tensors.
- Implement a two-layer neural network architecture `[784, 128, 10]` in pure NumPy.
- Train the model using mini-batch gradient descent with momentum to reach >= 95% accuracy.
- Evaluate the confusion matrix, compute precision/recall per digit, and perform error analysis on ambiguous digits.
- Visualize learned first-layer weight receptive fields as 28x28 spatial feature maps.

## Architecture
```
[28x28 Image] -> [Flatten 784] -> [W1 (128x784) + b1] -> [ReLU] -> [W2 (10x128) + b2] -> [Softmax] -> [Digit 0-9 Probability]
```

## Implementation guidelines
1. Scale raw pixel integers `[0, 255]` to `[0.0, 1.0]`.
2. Initialize layer 1 weights with He normal scaling: `std = sqrt(2 / 784)`.
3. Initialize layer 2 weights with He normal scaling: `std = sqrt(2 / 128)`.
4. Implement mini-batch shuffling with batch size 64.
5. Apply momentum coefficient `beta = 0.9` and learning rate `alpha = 0.1`.
6. Track training loss and validation accuracy per epoch.

## Expected output
```
[MNIST from Scratch Verification]
1. Network Initialization:
   - Layer 1: W1 (128, 784), b1 (128, 1) [He Normal Init]
   - Layer 2: W2 (10, 128), b2 (10, 1) [He Normal Init]
2. Training Convergence (20 Epochs):
   - Epoch 1: Loss = 0.412, Val Accuracy = 88.4%
   - Epoch 10: Loss = 0.086, Val Accuracy = 96.2%
   - Epoch 20: Loss = 0.038, Val Accuracy = 97.4%
3. Evaluation:
   - Test Accuracy: 97.2% on 10,000 held-out test images
   - All 10 digit classes achieve F1-Score >= 0.95
```

## Validation
To validate your implementation:
1. Verify that forward and backward propagation pass analytical gradient checks.
2. Confirm that test accuracy reaches >= 95.0% on held-out MNIST test images.
3. Ensure no external deep learning frameworks (PyTorch, TensorFlow) are imported.

## Deliverables
- Complete Python module `mnist_from_scratch.py`.
- Validation report showing >= 95% test accuracy on held-out MNIST digits.
- Confusion matrix detailing top misclassification pairs.
- Visualization grid of 16 learned first-layer weight filters.
