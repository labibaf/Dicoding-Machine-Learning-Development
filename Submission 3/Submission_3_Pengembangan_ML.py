# -*- coding: utf-8 -*-
"""Submission 3 Pengembangan ML

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16uVoo_b1A7Sfctc0mn84G5tkCp0qGBWv

**Submission 3 Pengembangan Machine Learning**

Labib Ammar Fadhali
<br>labibfadhali12@gmail.com
<br><br>
Dataset : https://www.kaggle.com/datasets/alessiocorrado99/animals10
"""

!pip install -q kaggle

from google.colab import files
upload=files.upload()

!mkdir ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d alessiocorrado99/animals10

!unzip '/content/animals10.zip' -d /content

# Commented out IPython magic to ensure Python compatibility.
import os
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.applications import ResNet152V2
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import matplotlib.pyplot as plt

# %matplotlib inline

base_dir='/content/raw-img'
os.listdir(base_dir)

datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

img_size=(224,224)
batch_size=32

train_generator=datagen.flow_from_directory(
    base_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='training'
)

validation_generator=datagen.flow_from_directory(
    base_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset='validation'
)

base_model=ResNet152V2(include_top=False, weights="imagenet",input_shape=(224,224,3))
base_model.summary()

for layer in base_model.layers:
    layer.trainable = False

model=Sequential([
    base_model,
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Dropout(0.5),
    Flatten(),
    Dense(512, activation='relu'),
    Dropout(0.3),
    Dense(10, activation='softmax')
])

model.summary()

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self,epoch,logs={}):
    if(logs.get('accuracy')>0.93) and (logs.get('val_accuracy')>0.93):
      print('\n accuracy and val_accuracy > 93%')
      self.model.stop_training=True
callbacks=myCallback()

history=model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=50,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size,
    callbacks=[callbacks]
)

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper right')
plt.show()

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='lower right')
plt.show()

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

model_name = 'model.tflite'

with open(model_name, 'wb') as f:
    f.write(tflite_model)

print(f"Model telah disimpan dalam format TF-Lite dengan nama file: {model_name}")