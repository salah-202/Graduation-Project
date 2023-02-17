# COVID-19 and Pneumonia Detection using Tensorflow Keras

This project is aimed at detecting COVID-19 and Pneumonia in chest X-ray images using deep learning.
 We have used Tensorflow Keras to build a deep learning model that achieves an accuracy of 90.5% and an AUC of 92. 
The dataset used for this project is the Chest X-Ray Images (Pneumonia) dataset and COVID-19 Radiography Database, which can be found on Kaggle.

# Preprocessing the Images

The images in the dataset were preprocessed using the ImageDataGenerator class from the Keras library.
We used various data augmentation techniques like rotation, zooming, horizontal flip, and vertical flip to increase the number of images in the dataset and make the model more robust.

Transfer Learning with VGG16 Model

We used the VGG16 model, which is a pre-trained model that has been trained on the ImageNet dataset.
We fine-tuned the VGG16 model by adding a few dense layers at the end of the model and trained it on our dataset.
The VGG16 model has 16 layers, and the first 13 layers are used for feature extraction.

# Flask Web Application

We built a web application using Flask to enable doctors and patients to upload chest X-ray images and get the prediction results.
The web application has several features, such as:

    - Upload an image from the local machine or provide an image URL.
    + View the uploaded image and the prediction result.
    * Paitant page containts information and test history.
    

# Conclusion

In this project, we have used deep learning techniques to detect COVID-19 and Pneumonia in chest X-ray images.
Our model achieved an accuracy of 90.5% and an AUC of 92.
We have also built a web application that enables doctors and patients to upload images and get the prediction results.
This project can be further extended by using more advanced deep learning techniques and incorporating other medical data.
