import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

# Based on: https://stackoverflow.com/questions/45772483/detect-words-and-graphs-in-image-and-slice-image-into-1-image-per-word-or-graph


def plot_horizontal_projection(file_name, img, projection):
    fig = plt.figure(1, figsize=(12, 16))
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])

    ax = plt.subplot(gs[0])
    im = ax.imshow(img, interpolation="nearest", aspect="auto")
    ax.grid(which="major", alpha=0.5)

    ax = plt.subplot(gs[1])
    ax.plot(projection, np.arange(img.shape[0]), "m")
    ax.grid(which="major", alpha=0.5)
    plt.xlim([0.0, 255.0])
    plt.ylim([-0.5, img.shape[0] - 0.5])
    ax.invert_yaxis()

    fig.suptitle("FOO", fontsize=16)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.97])

    fig.set_dpi(200)

    fig.savefig(file_name, bbox_inches="tight", dpi=fig.dpi)
    plt.clf()


def plot_vertical_projection(file_name, img, projection):
    fig = plt.figure(2, figsize=(12, 4))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 5])

    ax = plt.subplot(gs[0])
    im = ax.imshow(img, interpolation="nearest", aspect="auto")
    ax.grid(which="major", alpha=0.5)

    ax = plt.subplot(gs[1])
    ax.plot(np.arange(img.shape[1]), projection, "m")
    ax.grid(which="major", alpha=0.5)
    plt.xlim([-0.5, img.shape[1] - 0.5])
    plt.ylim([0.0, 255.0])

    fig.suptitle("FOO", fontsize=16)
    gs.tight_layout(fig, rect=[0, 0.03, 1, 0.97])

    fig.set_dpi(200)

    fig.savefig(file_name, bbox_inches="tight", dpi=fig.dpi)
    plt.clf()


def visualize_hp(file_name, img, row_means, row_cutpoints):
    row_highlight = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    row_means_int = row_means.astype(int)  # Convert to integer
    row_highlight[row_means_int == 0, :, :] = [255, 191, 191]
    row_highlight[row_cutpoints.astype(int), :, :] = [255, 0, 0]
    plot_horizontal_projection(file_name, row_highlight, row_means)


def visualize_vp(file_name, img, column_means, column_cutpoints):
    col_highlight = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    column_means_int = column_means.astype(int)  # Convert to integer
    col_highlight[:, column_means_int == 0, :] = [255, 191, 191]
    col_highlight[:, column_cutpoints.astype(int), :] = [255, 0, 0]
    plot_vertical_projection(file_name, col_highlight, column_means)


# From https://stackoverflow.com/a/24892274/3962537
def zero_runs(a):
    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.concatenate(([0], np.equal(a, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges


img = cv2.imread("1.png", cv2.IMREAD_COLOR)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img_gray_inverted = 255 - img_gray

row_means = cv2.reduce(img_gray_inverted, 1, cv2.REDUCE_AVG, dtype=cv2.CV_32F).flatten()
row_gaps = zero_runs(row_means)
row_cutpoints = (row_gaps[:, 0] + row_gaps[:, 1] - 1) / 2

visualize_hp("1_hp.png", img, row_means, row_cutpoints)

bounding_boxes = []
for n, (start, end) in enumerate(zip(row_cutpoints, row_cutpoints[1:])):
    start = int(start)
    end = int(end)
    line = img[start:end]
    line_gray_inverted = img_gray_inverted[start:end]

    column_means = cv2.reduce(
        line_gray_inverted, 0, cv2.REDUCE_AVG, dtype=cv2.CV_32F
    ).flatten()
    column_gaps = zero_runs(column_means)
    column_gap_sizes = column_gaps[:, 1] - column_gaps[:, 0]
    column_cutpoints = (column_gaps[:, 0] + column_gaps[:, 1] - 1) / 2

    filtered_cutpoints = column_cutpoints[column_gap_sizes > 5]

    for xstart, xend in zip(filtered_cutpoints, filtered_cutpoints[1:]):
        bounding_boxes.append(((xstart, start), (xend, end)))

    # visualize_vp("1_vp_%02d.png" % n, line, column_means, filtered_cutpoints)

result = img.copy()

for bounding_box in bounding_boxes:
    (xstart, ystart), (xend, yend) = bounding_box
    cv2.rectangle(
        result, (int(xstart), int(ystart)), (int(xend), int(yend)), (255, 0, 0), 2
    )


cv2.imwrite("1_boxes.png", result)
