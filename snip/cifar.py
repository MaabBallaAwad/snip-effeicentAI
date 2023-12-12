import os
import pickle
import numpy as np


def read_data(path_dataset, cifar100=True):
    # train batch
    train_batch = {}
    filename = os.path.join(path_dataset, 'train')
    with open(filename, 'rb') as f:
        try:
            batch = pickle.load(f, encoding='bytes')
        except TypeError:
            batch = pickle.load(f)  # for python 2
        for key in batch.keys():
            train_batch.setdefault(key, []).extend(batch[key])
    train_batch = {k: np.stack(v, 0) for k, v in train_batch.items()}  # stack into one batch

    # test batch
    filename = os.path.join(path_dataset, 'test')
    with open(filename, 'rb') as f:
        try:
            test_batch = pickle.load(f, encoding='bytes')
        except TypeError:
            test_batch = pickle.load(f)

    # Reshape images: (n, 3072) -> (n, 32, 32, 3)
    data_key = 'data'.encode('utf-8')
    label_key = 'fine_labels'.encode('utf-8') if cifar100 else 'labels'.encode('utf-8')

    train_images = np.transpose(
        np.reshape(train_batch[data_key], [-1, 3, 32, 32]), [0, 2, 3, 1])
    train_labels = np.asarray(train_batch[label_key])

    test_images = np.transpose(
        np.reshape(test_batch[data_key], [-1, 3, 32, 32]), [0, 2, 3, 1])
    test_labels = np.asarray(test_batch[label_key])

    # Pre-processing (normalize)
    train_images = np.divide(train_images, 255, dtype=np.float32)
    test_images = np.divide(test_images, 255, dtype=np.float32)
    channel_mean = np.mean(train_images, axis=(0, 1, 2), dtype=np.float32, keepdims=True)
    channel_std = np.std(train_images, axis=(0, 1, 2), dtype=np.float32, keepdims=True)
    train_images = (train_images - channel_mean) / channel_std
    test_images = (test_images - channel_mean) / channel_std

    dataset = {
        'train': {'input': train_images, 'label': train_labels},
        'test': {'input': test_images, 'label': test_labels},
    }

    print("Train images shape:", train_images.shape)
    print("Train labels shape:", train_labels.shape)

    return dataset
