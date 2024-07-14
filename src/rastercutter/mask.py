import xarray as xr
import rioxarray
import numpy as np
from shapely.geometry import mapping, box
import matplotlib.pyplot as plt
import geopandas as gpd

def pixel_intersection_percentage_mask(xr_dataset, polygon, plot=False):
    '''

    :param xr_dataset: xarray dataset
    :param polygon:
    :param plot: if true plot the mask
    :return: xar_dataset variable (mask)
    '''

    # # make sure that the projection is set correctly
    # dataset = xr_dataset.rio.set_crs(stac_item['properties']['projection'], inplace=True)

    # extract only the data that touches the polygon
    dataset = xr_dataset.rio.clip(polygon.apply(mapping), all_touched=True)

    # Extract affine transform and shape from the dataset
    transform = dataset.rio.transform()
    height, width = dataset.shape[-2], dataset.shape[-1]

    # Initialize an empty array to hold percentages
    percentages = np.zeros((height, width), dtype=np.float32)

    # loop to polygonize each pixel and calculate teh intersection
    for i in range(height):
        for j in range(width):
            # Create a box (square) for each pixel using the Affine transform
            x1, y1 = transform * (j, i)
            x2, y2 = transform * (j + 1, i + 1)
            pixel_box = box(x1, y1, x2, y2)

            # Calculate the intersection between the pixel box and the polygon
            intersection = polygon.intersection(pixel_box)

            # Calculate the percentage of the pixel covered by the polygon
            percentage = intersection.area / pixel_box.area
            percentages[i, j] = percentage.iloc[0]

    # save the percentage as ppm (pixel percentage mask)
    dataset['ppm'] = (('y', 'x'), percentages)

    # plot is optional
    if plot == True:
        fig, ax = plt.subplots(figsize=(10, 10))
        dataset.ppm.plot()
        polygon.boundary.plot(ax=ax, color='green', linewidth=1)

    return dataset['ppm']
