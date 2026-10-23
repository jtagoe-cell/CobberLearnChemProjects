import numpy as np

# Step 1: Start with a 5 x 5 array of zeros (all background).
image = np.zeros((5, 5), dtype=int)

# Step 2: Draw a plus sign with 1s (foreground).
image[2, :] = 1   # middle row (horizontal bar)
image[:, 2] = 1   # middle column (vertical bar)

# Step 3: Print the array and confirm its shape.
print("5 x 5 image (1 = foreground, 0 = background):")
print(image)

print("\nShape:", image.shape)
print("Number of dimensions:", image.ndim)
print("Total pixels:", image.size)
print("Data type:", image.dtype)

# Optional: print it as text art so the plus sign is easy to see.
print("\nAs text art:")
for row in image:
    print(" ".join("#" if pixel == 1 else "." for pixel in row))
    import numpy as np
    import matplotlib.pyplot as plt

    # Step 1: Build the 5 x 5 plus-sign image (1 = foreground, 0 = background).
    image = np.zeros((5, 5), dtype=int)
    image[2, :] = 1
    image[:, 2] = 1

    # Step 2: Define two 3 x 3 filters (kernels).
    # Vertical filter: responds strongly to vertical lines.
    vertical_filter = np.array([
        [-1, 2, -1],
        [-1, 2, -1],
        [-1, 2, -1]
    ])

    # Diagonal filter: responds strongly to lines running from top-left
    # to bottom-right.
    diagonal_filter = np.array([
        [2, -1, -1],
        [-1, 2, -1],
        [-1, -1, 2]
    ])


    # Step 3: Apply a filter by sliding it across the image.
    # At each position, multiply the 3 x 3 patch by the filter and add it up.
    # A 5 x 5 image with a 3 x 3 filter gives a 3 x 3 feature map.
    def apply_filter(img, kernel):
        k = kernel.shape[0]
        out_size = img.shape[0] - k + 1
        feature_map = np.zeros((out_size, out_size), dtype=int)

        for row in range(out_size):
            for col in range(out_size):
                patch = img[row:row + k, col:col + k]
                feature_map[row, col] = np.sum(patch * kernel)

        return feature_map


    vertical_map = apply_filter(image, vertical_filter)
    diagonal_map = apply_filter(image, diagonal_filter)

    print("Input image:\n", image)
    print("\nVertical feature map:\n", vertical_map)
    print("\nDiagonal feature map:\n", diagonal_map)


    # Step 4: Helper that draws a small grid with the numbers written on it.
    def show(ax, data, title, cmap):
        im = ax.imshow(data, cmap=cmap)
        ax.set_title(title, fontsize=11)
        ax.set_xticks(range(data.shape[1]))
        ax.set_yticks(range(data.shape[0]))

        # Pick white or black text based on how dark the cell's color is,
        # so the numbers stay readable on any colormap.
        for r in range(data.shape[0]):
            for c in range(data.shape[1]):
                red, green, blue, _ = im.cmap(im.norm(data[r, c]))
                brightness = 0.299 * red + 0.587 * green + 0.114 * blue
                color = "black" if brightness > 0.5 else "white"
                ax.text(c, r, data[r, c], ha="center", va="center",
                        color=color, fontsize=12, fontweight="bold")
        return im


    # Step 5: Plot the input, the filters, and the feature maps.
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))

    # Top row: input image and the two feature maps.
    show(axes[0, 0], image, "Input Image (5 x 5)", "gray_r")
    im_v = show(axes[0, 1], vertical_map, "Vertical Feature Map (3 x 3)", "viridis")
    im_d = show(axes[0, 2], diagonal_map, "Diagonal Feature Map (3 x 3)", "viridis")
    fig.colorbar(im_v, ax=axes[0, 1], fraction=0.046)
    fig.colorbar(im_d, ax=axes[0, 2], fraction=0.046)

    # Bottom row: the filters that produced those maps.
    axes[1, 0].axis("off")
    show(axes[1, 1], vertical_filter, "Vertical Filter", "coolwarm")
    show(axes[1, 2], diagonal_filter, "Diagonal Filter", "coolwarm")

    plt.suptitle("Applying Vertical and Diagonal Filters to a Plus-Sign Image",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("plus_filters.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("\nPlot saved to plus_filters.png")