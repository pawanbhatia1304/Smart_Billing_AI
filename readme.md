# SmartScan Billing Assistant

The SmartScan Billing Assistant is a computer vision-based project designed to automate the process of calculating the total bill by detecting products and adding their prices using a camera, similar to a cashier. This project uses the YOLOv8 model for object detection and tracking. This is the MVP of the main project I did for a supermarket where I implemented the SmartScan billing system on more than 1200 products.

## Table of Contents
- [Overview](#overview)
- [Project Demo](#project-demo)
- [Dataset Preparation](#dataset-preparation)
- [Model Training](#model-training)
- [Testing and Evaluation](#testing-and-evaluation)
- [Usage](#usage)
- [License](#license)

## Overview
The project aims to simplify the billing process in supermarkets and retail stores by automating the detection and pricing of products. This is achieved through the following steps:

1. Collecting and annotating a dataset of products.
2. Augmenting the dataset to improve model generalization.
3. Training a YOLOv8 model on the augmented dataset.
4. Testing the model's performance in a real-time environment.

## Project Demo
![output_image](https://github.com/user-attachments/assets/ae1fbf45-58fb-4ed6-9b21-7d4dac020b8f)


## Dataset Preparation
### Data Collection and Annotation
The dataset was collected and annotated using Roboflow. The steps to connect to Roboflow and download the dataset are detailed in the `dataset_preparation.ipynb` notebook.

### Data Augmentation
To enhance the dataset and improve the model's robustness, data augmentation was performed using the Albumentations library. The augmentation pipeline included random brightness and contrast adjustments. The detailed augmentation process can be found in the `dataset_preparation.ipynb` notebook.

## Model Training
The YOLOv8 model was trained on the augmented dataset using the parameters specified in the `training_and_testing/training.ipynb` notebook. The notebook includes the code for initializing the model, setting training parameters, and evaluating the model's performance.

## Testing and Evaluation
The model was tested in a real-time environment using a webcam. The `training_and_testing/testing.ipynb` notebook demonstrates how to use the trained model to detect products and calculate the total price. The notebook includes the code for loading the model, capturing video, detecting objects, and updating the total price based on detected products.

## Usage
To use the SmartScan Billing Assistant, follow these steps:

1. Ensure you have the necessary dependencies installed.
2. Run the `dataset_preparation.ipynb` notebook to prepare and augment the dataset.
3. Train the model by running the `training_and_testing/training.ipynb` notebook.
4. Test the model in a real-time environment by running the `training_and_testing/testing.ipynb` notebook.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
