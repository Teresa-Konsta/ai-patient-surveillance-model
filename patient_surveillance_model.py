# -*- coding: utf-8 -*-
"""patient-surveillance-model.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PQH2n2LtoFyeu7cXDZzmRnz6oLs8DaDE

##### Template by Nicholas Renotte, GitHub nicknochnack

# 1. Install Dependencies and Setup
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install tensorflow tensorflow-gpu opencv-python matplotlib

import tensorflow as tf
import os

#to prevent out of memory error
units = tf.config.experimental.list_physical_devices('GPU')
for unit in units:
    tf.config.experimental.set_memory_growth(unit, True)

tf.config.list_physical_devices('GPU')

"""# 2. Remove dodgy images"""

import cv2
import imghdr

data_dir = 'data'

image_exits = ['jpeg','jpg', 'png']

#checking folder directory and data in folder -> success
#os.listdir(data_dir)
#os.listdir(os.path.join(data_dir, 'patients'))

#cleaning up dodgy imgs
for image_class in os.listdir(data_dir):
    for image in os.listdir(os.path.join(data_dir, image_class)):
        image_path = os.path.join(data_dir, image_class, image)
        try:
            img = cv2.imread(image_path)
            tip = imghdr.what(image_path)
            if tip not in image_exits:
                os.remove(image_path)
        except Exception as e:
            print('Issue with image {}'.format(image_path))
            os.remove(image_path)

"""# 3. Load Data"""

import numpy as np
from matplotlib import pyplot as plt

data = tf.keras.utils.image_dataset_from_directory('data')

data_iterator = data.as_numpy_iterator()

#min 0 and max 1
batch = data_iterator.next()

fig, ax = plt.subplots(ncols=4, figsize=(20,20))
for idx, img in enumerate(batch[0][:4]):
    ax[idx].imshow(img.astype(int))
    ax[idx].title.set_text(batch[1][idx])

"""# 4. Scale Data"""

#x->image, y->label
data = data.map(lambda x,y: (x/255, y))

data.as_numpy_iterator().next()

"""# 5. Split Data"""

#batch number, to be divided
#len(data)

#data batches division -> 70% training, 20% validation, 10% testing
train_size = int(len(data)*.7)
validation_size = int(len(data)*.2)+1
test_size = int(len(data)*.1)+1

#train_size

#validation_size

#test_size

train = data.take(train_size)
validation = data.skip(train_size).take(validation_size)
test = data.skip(train_size+validation_size).take(test_size)

"""# 6. Build Deep Learning Model"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout

model = Sequential()

model.add(Conv2D(16, (3,3), 1, activation='relu', input_shape=(256,256,3)))
model.add(MaxPooling2D())
model.add(Conv2D(32, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())
model.add(Conv2D(16, (3,3), 1, activation='relu'))
model.add(MaxPooling2D())
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile('adam', loss=tf.losses.BinaryCrossentropy(), metrics=['accuracy'])

model.summary()

"""# 7. Train"""

logdir='logs'

tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)

hist = model.fit(train, epochs=20, validation_data=val, callbacks=[tensorboard_callback])

"""# 8. Plot Performance"""

fig = plt.figure()
plt.plot(hist.history['loss'], color='teal', label='loss')
plt.plot(hist.history['val_loss'], color='orange', label='val_loss')
fig.suptitle('Loss', fontsize=20)
plt.legend(loc="upper left")
plt.show()

fig = plt.figure()
plt.plot(hist.history['accuracy'], color='teal', label='accuracy')
plt.plot(hist.history['val_accuracy'], color='orange', label='val_accuracy')
fig.suptitle('Accuracy', fontsize=20)
plt.legend(loc="upper left")
plt.show()

"""# 9. Evaluate"""

from tensorflow.keras.metrics import Precision, Recall, BinaryAccuracy

pre = Precision()
re = Recall()
acc = BinaryAccuracy()

for batch in test.as_numpy_iterator():
    X, y = batch
    yhat = model.predict(X)
    pre.update_state(y, yhat)
    re.update_state(y, yhat)
    acc.update_state(y, yhat)

print(pre.result(), re.result(), acc.result())

"""# 10. Test"""

import cv2

img = cv2.imread('154006829.jpg')
plt.imshow(img)
plt.show()

resize = tf.image.resize(img, (256,256))
plt.imshow(resize.numpy().astype(int))
plt.show()

yhat = model.predict(np.expand_dims(resize/255, 0))

yhat

if yhat > 0.5:
    print(f'Predicted class is Sad')
else:
    print(f'Predicted class is Happy')

"""# 11. Save the Model"""

from tensorflow.keras.models import load_model

model.save(os.path.join('models','imageclassifier.h5'))

new_model = load_model('imageclassifier.h5')

new_model.predict(np.expand_dims(resize/255, 0))