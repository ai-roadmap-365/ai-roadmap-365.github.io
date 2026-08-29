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

## Deliverables
- Complete Python module `mnist_from_scratch.py`.
- Validation report showing >= 95% test accuracy on held-out MNIST digits.
- Confusion matrix detailing top misclassification pairs.
- Visualization grid of 16 learned first-layer weight filters.
