
def crop_image_cv2(img, crop_regions):

    if img is None:
        raise ValueError("Could not load image")
    
    height, width = img.shape[:2]
    cropped_images = []
    
    for i, region in enumerate(crop_regions):
        left, top, right, bottom = region
        if left < 0 or top < 0 or right > width or bottom > height:
            print(f"Warning: Region {i} out of bounds, skipping...")
            continue
        
        # Crop using NumPy array slicing (OpenCV uses [y:y, x:x])
        cropped_img = img[top:bottom, left:right]
        cropped_images.append(cropped_img)

    return cropped_images