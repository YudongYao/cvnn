import numpy as np
from cvnn.layers import ComplexDense, ComplexFlatten, ComplexInput
from tensorflow.keras.models import Sequential
import tensorflow as tf
import tensorflow_datasets as tfds


def small_example():
    img_r = np.array([[
        [0, 1, 2],
        [0, 2, 2],
        [0, 5, 7]
    ], [
        [0, 4, 5],
        [3, 7, 9],
        [4, 5, 3]
    ]]).astype(np.float32)
    img_i = np.array([[
        [0, 4, 5],
        [3, 7, 9],
        [4, 5, 3]
    ], [
        [0, 4, 5],
        [3, 7, 9],
        [4, 5, 3]
    ]]).astype(np.float32)
    img = img_r + 1j * img_i
    c_flat = ComplexFlatten()
    c_dense = ComplexDense(units=10)
    res = c_dense(c_flat(img.astype(np.complex64)))


def serial_layers():
    model = Sequential()
    model.add(ComplexDense(32, activation='relu', input_shape=(32, 32, 3)))
    model.add(ComplexDense(32))
    print(model.output_shape)


def normalize_img(image, label):
    """Normalizes images: `uint8` -> `float32`."""
    return tf.cast(image, tf.float32) / 255., label


def mnist_example():
    (ds_train, ds_test), ds_info = tfds.load(
        'mnist',
        split=['train', 'test'],
        shuffle_files=True,
        as_supervised=True,
        with_info=True,
    )
    ds_train = ds_train.map(
        normalize_img, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    ds_train = ds_train.cache()
    ds_train = ds_train.shuffle(ds_info.splits['train'].num_examples)
    ds_train = ds_train.batch(128)
    ds_train = ds_train.prefetch(tf.data.experimental.AUTOTUNE)
    ds_test = ds_test.map(
        normalize_img, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    ds_test = ds_test.batch(128)
    ds_test = ds_test.cache()
    ds_test = ds_test.prefetch(tf.data.experimental.AUTOTUNE)

    model = tf.keras.models.Sequential([
        ComplexFlatten(input_shape=(28, 28, 1)),
        ComplexDense(128, activation='relu', dtype=tf.float32),
        ComplexDense(10, dtype=tf.float32)
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
    )

    model.fit(
        ds_train,
        epochs=6,
        validation_data=ds_test,
    )


def fashin_mnist_example():
    dtype_1 = np.complex64
    fashion_mnist = tf.keras.datasets.fashion_mnist
    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
    train_images = train_images.astype(dtype_1)
    test_images = test_images.astype(dtype_1)
    train_labels = train_labels.astype(dtype_1)
    test_labels = test_labels.astype(dtype_1)

    model = tf.keras.Sequential([
        ComplexInput(input_shape=(28, 28)),
        ComplexFlatten(),
        ComplexDense(128, activation='cart_relu'),
        ComplexDense(10, activation='convert_to_real_with_abs')
    ])
    model.summary()
    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy']
                  )
    model.fit(train_images, train_labels, epochs=10)

    # import pdb; pdb.set_trace()