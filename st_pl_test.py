import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# Map categories to dryness scale
dryness_scale = {
    "Very Sweet": 0.0,
    "Sweet": 0.2,
    "Semi-Sweet": 0.4,
    "Off-Dry": 0.6,
    "Dry": 0.8,
    "Bone-Dry": 1.0
}

# Function to remove background using rembg
def remove_background(image):
    # Convert the uploaded image to binary data
    input_image = image.read()
    output_image = remove(input_image)
    return Image.open(io.BytesIO(output_image))

def wrap_text(text, width):
    """
    Wraps the input text to fit within the specified width.
    
    Parameters:
    - text (str): The text to be wrapped.
    - width (int): The maximum number of characters per line.
    
    Returns:
    - str: The wrapped text.
    """
    wrapper = textwrap.TextWrapper(width=width)
    wrapped_text = wrapper.fill(text=text)
    return wrapped_text

# Function to generate shelf talker
def generate_shelf_talker(wine_name, description, body_text, dryness_category, points, bottle_image):
    dryness_level = dryness_scale[dryness_category]
    
    # Create a blank image for the shelf talker
    img = Image.new("RGB", (600, 800), "white")
    draw = ImageDraw.Draw(img)

    # Load fonts (use system default fonts or replace with others)
    title_font = ImageFont.truetype("arial.ttf", 40)
    body_font = ImageFont.truetype("arial.ttf", 20)

    # Draw Wine Name
    draw.text((50, 30), wrap_text(wine_name, width=25), fill="black", font=title_font)

    # Resize and paste bottle image just below the wine name
    bottle_image = bottle_image.resize((150, 150))  # Resize the image if needed
    img.paste(bottle_image, (50, 80), bottle_image)  # Paste the bottle image below wine name
    
    # Wrap Description Text
    #wrapper = textwrap.TextWrapper(width=40)  # Set width for wrapping
    #wrapped_description = wrapper.fill(text=description)

    # Draw Description Text next to the bottle image
    draw.text((210, 100), wrap_text(description, width=40), fill="black", font=body_font)

    # Draw Body Text
    draw.text((50, 300), body_text, fill="black", font=body_font)
    
    # Draw Dryness Bar
    draw.rectangle([(50, 400), (550, 430)], outline="black", width=2)  # Dryness bar outline
    dryness_width = int(500 * dryness_level)  # Adjust dryness level to fill width
    draw.rectangle([(50, 400), (50 + dryness_width, 430)], fill="gray")  # Fill based on dryness level
    
    # Draw Dryness Category
    draw.text((50, 440), f"Dryness: {dryness_category}", fill="black", font=body_font)

    # Draw Points
    draw.text((50, 470), f"Points: {points}", fill="black", font=body_font)

    return img

# Streamlit UI
st.title("Wine Shelf Talker Generator")

# Input fields for wine details
wine_name = st.text_input("Wine Name", "Chardonnay 2020")
description = st.text_area("Description", "Notes of pear and citrus. Pairs well with seafood.")
body_text = st.text_area("Body Text", "A crisp and refreshing wine with a smooth finish.")

# Dropdown to select dryness level
dryness_category = st.selectbox("Select Dryness Level", list(dryness_scale.keys()))

points = st.text_input("Points", "Wine Enthusiast: 92")

# Upload wine bottle image
uploaded_image = st.file_uploader("Upload a wine bottle image", type=["jpg", "jpeg", "png"])

# Generate the shelf talker when the button is clicked
if st.button("Generate Shelf Talker"):
    if uploaded_image is not None:
        # Remove the background of the uploaded image
        bottle_image = remove_background(uploaded_image)

        # Generate the shelf talker with the wine details and bottle image
        img = generate_shelf_talker(wine_name, description, body_text, dryness_category, points, bottle_image)
        
        st.image(img, caption="Generated Shelf Talker", use_container_width=True)

        # Convert the image to bytes for download
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        # Provide a download button for the image
        st.download_button(
            label="Download Shelf Talker",
            data=byte_im,
            file_name="shelf_talker.png",
            mime="image/png"
        )
    else:
        st.error("Please upload a wine bottle image.")
