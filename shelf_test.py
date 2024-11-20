import streamlit as st
import imgkit
from html2image import Html2Image
from PIL import Image
import io
import base64
from rembg import remove  # Import rembg's remove function
from auto_scrape import search_product



# Initialize session state variables
if "description" not in st.session_state:
    st.session_state.description = "Notes of pear and citrus. Pairs well with seafood."
if "body_text" not in st.session_state:
    st.session_state.body_text = "A crisp and refreshing wine with a smooth finish."
if "dryness_category" not in st.session_state:
    st.session_state.dryness_category = "0.4"

# Function to generate HTML content for the shelf talker
def generate_html(wine_name, description, body_text, dryness_category, points, bottle_image_base64):
    dryness_level = float(dryness_category)
    dryness_percentage = int(dryness_level * 100)
    
    # HTML content with inline CSS to set size and style
    html_content = f"""
    <html>
        <head>
            <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1">
        </head>
        <body style="width: 240px; height: 480px; padding: 0 20px; box-sizing: border-box; font-family: Serif; background-color: white; display: flex; flex-direction: column; align-items: center; justify-content: space-around; overflow: hidden;">
            <!-- Dynamic Wine Name -->
            <h1 style="text-align: center; font-size: 15px; margin: 5px;">{wine_name}</h1>

            <!-- Dynamic Wine Image and Description -->
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <tr>
                    <td style="width: 30%;">
                        <img src="data:image/png;base64,{bottle_image_base64}" alt="Wine Bottle" style="width: 100%; max-width: 108px;">
                    </td>
                    <td style="width: 70%;">
                        <p style="text-align: left; font-size: 12px; line-height: 1; max-height: 90px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical;">{description}</p>
                    </td>
                </tr>
            </table>

            <!-- Dynamic Body Text -->
            <p style="text-align: center; font-size: 12px; margin-top: 5px;">{body_text}</p>

            <!-- Dynamic Dryness Level -->
            <div style="width: 100%; margin-top: 10px;">
                <p style="text-align: center; font-size: 12px; margin-bottom: 5px;">Dryness Level</p>
                <div style="width: 100%; height: 10px; background-color: #ddd; border-radius: 5px;">
                    <div style="width: {dryness_percentage}%; height: 100%; background-color: #333; border-radius: 5px;"></div>
                </div>
            </div>



            <!-- Dynamic Points -->
            <p style="text-align: center; font-size: 12px; margin-top: 10px;">{points}</p>
        </body>
    </html>
    """
    return html_content

# Function to remove background using rembg
def remove_background(image):
    input_image = image.read()
    output_image = remove(input_image)
    return Image.open(io.BytesIO(output_image))

# Function to convert percentage string to decimal
def convert_percentage_to_decimal(percentage_str):
    # Check if the string contains a '%' symbol and strip it
    if '%' in percentage_str:
        percentage_str = percentage_str.replace('%', '')
    try:
        # Convert the string to a float and divide by 100 to get the decimal value
        return float(percentage_str) / 100
    except ValueError:
        # Handle cases where the value can't be converted to float
        return 0.6  # Return a default value if conversion fails


# Function to create an image from HTML using html2image
def create_image_from_html(html_content):
    hti = Html2Image()
    hti.output_path = "."
    hti.screenshot(html_str=html_content, save_as="shelf_talker.png", size=(240, 480))
    image = Image.open("shelf_talker.png")
    image = image.resize((240, 480), Image.Resampling.LANCZOS)
    image.save("shelf_talker_high_res.png", dpi=(300, 300))
    return Image.open("shelf_talker_high_res.png")

# Streamlit UI
st.title("Wine Shelf Talker Generator")

# Input fields for wine details
wine_name = st.text_input("Wine Name", "Chardonnay 2020")
description = st.text_area("Description", st.session_state.description)
body_text = st.text_area("Body Text", st.session_state.body_text)
#dryness_category = st.selectbox("Select Dryness Level", list(dryness_scale.keys()), index=list(dryness_scale.keys()).index(st.session_state.dryness_category))
dryness_category = st.text_area("Dryness Level", st.session_state.dryness_category)
points = st.text_input("Points", "Wine Enthusiast: 92")

# Button to fetch wine details using search_product
if st.button("Fetch Wine Details"):
    try:
        # Call the search_product function with the wine name
        result = search_product(wine_name, threshold=60)
        
        # Safely update session state variables with fetched data
        st.session_state.description = result.get("rating", "Description not available")
        st.session_state.body_text = result.get("profile_info", "Body text not available")
        # Get the fetched dryness category and map it to its corresponding numeric value
        fetched_dryness_category = result.get("left_value", "0.4")
        print(fetched_dryness_category)
        st.session_state.dryness_category = convert_percentage_to_decimal(fetched_dryness_category)
        print(st.session_state.dryness_category)
        #st.session_state.dryness_value = dryness_scale.get(fetched_dryness_category, dryness_scale["Dry"])  # Default to "Dry" if value is invalid
        st.success("Wine details fetched successfully!")
    except Exception as e:
        st.error(f"Error fetching wine details: {e}")

# Upload wine bottle image
uploaded_image = st.file_uploader("Upload a wine bottle image", type=["jpg", "jpeg", "png"])

if st.button("Generate Shelf Talker"):
    if uploaded_image is not None:
        try:
            # Step 1: Remove background
            bottle_image_no_bg = remove_background(uploaded_image)
            img_buffer = io.BytesIO()
            bottle_image_no_bg.save(img_buffer, format="PNG")
            bottle_image_base64 = base64.b64encode(img_buffer.getvalue()).decode()

            # Step 2: Generate dynamic HTML content
            html_content = generate_html(wine_name, description, body_text, dryness_category, points, bottle_image_base64)

            # Step 3: Generate an image from HTML using imgkit and save it
            imgkit.from_string(
                html_content, 'output_image.png',
                options={
                    'width': 480, 'height': 720, 'zoom': 2, 'format': 'png', 'quality': 100
                }
            )

            # Step 4: Open the generated image file
            with open('output_image.png', 'rb') as f:
                shelf_talker_image = Image.open(f)
                img_buffer = io.BytesIO()
                shelf_talker_image.save(img_buffer, format="PNG")
                img_buffer.seek(0)

            # Step 5: Display and allow download
            st.image(shelf_talker_image, caption="Generated Shelf Talker", use_container_width=True)
            st.download_button(
                label="Download Shelf Talker",
                data=img_buffer,
                file_name="shelf_talker.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please upload a wine bottle image.")
