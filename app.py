import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Configuración de la página
st.set_page_config(page_title='Tablero Inteligente')
st.markdown("""
    <style>
    /* Fondo degradado para toda la app */
    .stApp {
        background: linear-gradient(135deg, #f0f4ff, #d9e6ff);
    }

    /* Títulos más grandes y llamativos */
    h1 {
        color: #4a00e0;
        font-size: 48px;
        text-align: center;
        font-weight: bold;
    }
    h2 {
        color: #ff4d6d;
        font-size: 32px;
        font-weight: bold;
    }

    /* Botón de análisis con color y hover */
    button[kind="secondary"] {
        background-color: #ff6f61;
        color: white;
        font-size: 18px;
        padding: 10px 25px;
        border-radius: 12px;
    }
    button[kind="secondary"]:hover {
        background-color: #ff3b2e;
        cursor: pointer;
    }

    /* Canvas con borde y sombra */
    div[role="application"] {
        border: 3px solid #4a00e0;
        border-radius: 12px;


# Título y descripción
st.title('Tablero Inteligente')
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarla")

# Parámetros del canvas
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000"
bg_color = '#FFFFFF'

# Crear el canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 100, 100, 0.4)",
    stroke_width=stroke_width,
    stroke_color="#4a00e0",
    background_color="#f0f4ff",
    height=350,
    width=450,
    drawing_mode=drawing_mode,
    key="canvas",
)

# Clave de OpenAI
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Inicializar cliente OpenAI correctamente
client = OpenAI(api_key=api_key)

# Botón de análisis y placeholder para mensajes
analyze_button = st.button("Analiza la imagen", type="secondary")
message_placeholder = st.empty()

# Procesar el dibujo si hay imagen y API key
if canvas_result.image_data is not None and api_key and analyze_button:
    message_placeholder.markdown("⏳ Analizando tu boceto...")  # Mensaje de carga

    with st.spinner("Procesando la imagen..."):
        # Guardar la imagen dibujada
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
        # Codificar imagen en base64
        base64_image = encode_image_to_base64("img.png")
        prompt_text = "Describe in spanish briefly the image"

        # Preparar la petición a OpenAI
        try:
            full_response = ""
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            # Mostrar la respuesta en el placeholder
            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response)

            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = full_response

        except Exception as e:
            message_placeholder.markdown("")  # limpiar mensaje de carga
            st.error(f"Ocurrió un error: {e}")

# Advertencias si falta API key o canvas vacío
elif not api_key:
    st.warning("Por favor ingresa tu API key.")
elif canvas_result.image_data is None:
    st.info("Dibuja algo en el canvas para analizarlo.")
