#!/usr/bin/env python

import random

import numpy as np
import cv2

from matplotlib import pyplot as plt
from .augmentation import augment_seg, custom_augment_seg
from .data_loader import \
    get_pairs_from_paths, DATA_LOADER_SEED, class_colors, DataLoaderError

random.seed(DATA_LOADER_SEED)


def _get_colored_segmentation_image(img, seg, colors,
                                    n_classes, do_augment=False, augment_name='aug_all', custom_aug=None):
    """ Return a colored segmented image """
    seg_img = np.zeros_like(seg)

    if do_augment:
        if custom_aug is not None:
            img, seg[:, :, 0] = custom_augment_seg(img, seg[:, :, 0], augmentation_function=custom_aug)
        else:
            img, seg[:, :, 0] = augment_seg(img, seg[:, :, 0], augmentation_name=augment_name)

    for c in range(n_classes):
        seg_img[:, :, 0] += ((seg[:, :, 0] == c)
                             * (colors[c][0])).astype('uint8')
        seg_img[:, :, 1] += ((seg[:, :, 0] == c)
                             * (colors[c][1])).astype('uint8')
        seg_img[:, :, 2] += ((seg[:, :, 0] == c)
                             * (colors[c][2])).astype('uint8')

    return img, seg_img


def visualize_segmentation_dataset(images_path, segs_path, n_classes, image_size=(352,480),
                                   do_augment=False, ignore_non_matching=False,
                                   no_show=False, augment_name="aug_all", custom_aug=None):
    try:
        # Get image-segmentation pairs
        img_seg_pairs = get_pairs_from_paths(
                            images_path, segs_path,
                            ignore_non_matching=ignore_non_matching)

        # Get the colors for the classes
        colors = class_colors

        print("Please press any key to display the next image")
        for im_fn, seg_fn in img_seg_pairs:
            img = cv2.imread(im_fn)
            seg = cv2.imread(seg_fn)
            print("Found the following classes in the segmentation image:",
                  np.unique(seg))
            img, seg_img = _get_colored_segmentation_image(
                                                    img, seg, colors,
                                                    n_classes,
                                                    do_augment=do_augment, augment_name=augment_name, custom_aug=custom_aug)

            if image_size is not None:
                img = cv2.resize(img, image_size)
                seg_img = cv2.resize(seg_img, image_size)

            print("Please press any key to display the next image")
            plt.imshow(img)
            plt.show()
            plt.imshow(seg_img)
            plt.show()
    except DataLoaderError as e:
        print("Found error during data loading\n{0}".format(str(e)))
        return False


def visualize_segmentation_dataset_one(images_path, segs_path, n_classes,
                                       do_augment=False, no_show=False,
                                       ignore_non_matching=False):

    img_seg_pairs = get_pairs_from_paths(
                                images_path, segs_path,
                                ignore_non_matching=ignore_non_matching)

    colors = class_colors

    im_fn, seg_fn = random.choice(img_seg_pairs)

    img = cv2.imread(im_fn)
    seg = cv2.imread(seg_fn)
    print("Found the following classes "
          "in the segmentation image:", np.unique(seg))

    img, seg_img = _get_colored_segmentation_image(
                                        img, seg, colors,
                                        n_classes, do_augment=do_augment)

    if not no_show:
        plt.imshow(img)
        plt.show()
        plt.imshow(seg_img)
        plt.show()

    return img, seg_img


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", type=str)
    parser.add_argument("--annotations", type=str)
    parser.add_argument("--n_classes", type=int)
    args = parser.parse_args()

    visualize_segmentation_dataset(
        args.images, args.annotations, args.n_classes)
