import os
import streamlit as st
import base64
from openai import OpenAI
import openai
#from PIL import Image
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_drawable_canvas import st_canvas

Expert=" "
profile_imgenh=" "
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit 
st.set_page_config(page_title='Tablero Inteligente')

st.markdown("""
<style>
/* Fondo animado tipo gradiente */
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.stApp {
    background: linear-gradient(-45deg, #fbc2eb, #a6c1ee, #cfd9df, #fbc2eb);
    background-size: 400% 400%;
    animation: gradientBG 20s ease infinite;
    font-family: 'Segoe UI', sans-serif;
}

/* Títulos centrados y con sombra */
h1, h2 {
    color: #4b0082;
    text-align: center;
    text-shadow: 2px 2px 8px rgba(75,0,130,0.5);
}

/* Textos instructivos más visibles */
h3, p, label, span {
    text-align: center;
    font-size: 18px;
    color: #2d2d2d;
}

/* Botón animado */
button {
    background: linear-gradient(90deg, #ff6f91, #ff9671);
    color: white !important;
    border-radius: 16px;
    font-size: 18px;
    font-weight: 700;
    transition: transform 0.2s, box-shadow 0.2s;
}
button:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(255, 105, 180, 0.5);
}

/* Canvas centrada con sombra */
[data-testid="stCanvas"] {
    display: flex;
    justify-content: center;
}
[data-testid="stCanvas"] canvas {
    border-radius: 16px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.title('Tablero Inteligente')
with st.sidebar:
st.markdown(
    "<h3 style='text-align:center; color:#ff4d6d;'>✏️ Dibuja tu boceto en el panel y presiona el botón para analizarlo 🚀</h3>",
    unsafe_allow_html=True
)

# Add canvas component
#bg_image = st.sidebar.file_uploader("Cargar Imagen:", type=["png", "jpg"])
# Specify canvas parameters in application
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
#stroke_color = '#FFFFFF' # Set background color to white
#bg_color = '#000000'
stroke_color = "#000000" 
bg_color = '#FFFFFF'
#realtime_update = st.sidebar.checkbox("Update in realtime", True)


# Create a canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    #background_image= None #Image.open(bg_image) if bg_image else None,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave')
#os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = ke


# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

analyze_button = st.button("Analiza la imagen", type="secondary")
message_placeholder = st.empty()


# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
    if canvas_result.image_data is not None and api_key and analyze_button:
    message_placeholder.markdown("⏳ Analizando tu boceto...")  # Mensaje de carga
    # Aquí empieza tu procesamiento de la imagen


    with st.spinner("Analizando ..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
      # Codificar la imagen en base64
 
        base64_image = encode_image_to_base64("img.png")
            
        prompt_text = (f"Describe in spanish briefly the image")
    
      # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url":f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder.markdown(full_response)  # Muestra el resultado final
            response = openai.chat.completions.create(
              model= "gpt-4o-mini",  #o1-preview ,gpt-4o-mini
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                  }
                ],
              max_tokens=500,
              )
            #response.choices[0].message.content
            if response.choices[0].message.content is not None:
                    full_response += response.choices[0].message.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            if Expert== profile_imgenh:
               st.session_state.mi_respuesta= response.choices[0].message.content #full_response 
    
            # Display the response in the app
            #st.write(response.choices[0])
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required

    if not api_key:
        st.warning("Por favor ingresa tu API key.")
