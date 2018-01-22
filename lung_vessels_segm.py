# import remote_config
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

import numpy as np
import tensorflow as tf
import Unet3D as unet
import img_processing as proc
import lung_data_provider as ldprovider
import matplotlib.pyplot as plt


def main():
    img_folder = "/scratch/VESSEL/cropped_data/images"
    label_folder = "/scratch/VESSEL/cropped_data/masks"
    provider = ldprovider.LungDataProvider(img_folder, label_folder)
    X, y = provider._next_data()

    fig, img_arr = plt.subplots(1, 2, sharey='all')

    img_arr[0].imshow(X[0, 5, :, :, 0], cmap='gray')
    img_arr[0].set_title("Input image")
    img_arr[1].imshow(y[0, 5, :, :, 0], cmap='gray')
    img_arr[1].set_title("Label")
    plt.show()
    print("0")
    net = unet.Unet3D(channels=1, n_class=2, cost="cross_entropy", summaries=False)
    trainer = unet.Trainer(net, batch_size=1, optimizer="adam",  norm_grads=True,
                           opt_kwargs=dict(learning_rate=0.0001))
    print("1")
    if not os.path.exists("unet3d_trained"):
        os.path.mkdir("/home/guest/dbash/unet3d_trained")
    trainer.train(provider, "/home/guest/dbash/unet3d_trained", epochs=60,
                  training_iters=10, restore=False)
    print("2")
    X_test, y_test = provider._next_data()
    prediction = net.predict("/home/guest/dbash/unet3d_trained/model.cpkt", X_test)
    print("3")


main()

"""fig1, ax1 = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(12,5))
ax1[0].imshow(X_test[0, 100, :, :, 0], aspect="auto")
ax1[1].imshow(y_test[0, 100, :, :, 0], aspect="auto")
mask = prediction[0, 100, :, :, 0] > 0.9
ax1[2].imshow(mask, aspect="auto")
ax1[0].set_title("Input")
ax1[1].set_title("Ground truth")
ax1[2].set_title("Prediction")
fig1.tight_layout()
fig1.savefig("../example_lung.png")
plt.show()"""
