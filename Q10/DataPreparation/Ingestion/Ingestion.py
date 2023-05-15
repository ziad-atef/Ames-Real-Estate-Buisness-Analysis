import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from tqdm import tqdm
from sklearn.model_selection import train_test_split


def read_data(eval=False, path='../../DataFiles/house-prices-advanced-regression-techniques'):
    '''
    reads the dataset from the folder and returns the train, validation and test sets
    '''

    if eval:
        df = pd.read_csv(
            '../../DataFiles/house-prices-advanced-regression-techniques/test.csv')
        return df
    else:
        # Read csv file
        df = pd.read_csv(path + '/train.csv')

    return df


def visualize_data(x_data, y_data, num_images=3):
    """
    show num_images next to each other
    """
    fig, axs = plt.subplots(1, num_images, figsize=(15, 15))
    for i in range(num_images):
        axs[i].imshow(x_data[i], cmap='gray')
        axs[i].set_title('Golden Retriever' if y_data[i]
                         == 1 else 'Swedish Elkhound')
        axs[i].axis('off')

    plt.show()
