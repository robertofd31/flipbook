import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import zipfile
import base64
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Generador de Flip Books", page_icon="📚")

def create_flip_book(video_path, interval=0.5):
    """
    Extrae fotogramas de un video a intervalos regulares
    """
    # Crear carpeta temporal para guardar fotogramas
    temp_dir = tempfile.mkdtemp()

    # Abrir el video
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return "Error: No se pudo abrir el video", None

    # Obtener propiedades del video
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    # Calcular intervalo de fotogramas
    frame_interval = int(fps * interval)
    expected_pages = total_frames // frame_interval + 1

    # Extraer fotogramas
    frame_paths = []
    frame_count = 0

    for i in range(0, total_frames, frame_interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()

        if not ret:
            break

        # Guardar el fotograma
        output_path = os.path.join(temp_dir, f"pagina_{frame_count+1:04d}.jpg")
        cv2.imwrite(output_path, frame)
        frame_paths.append(output_path)
        frame_count += 1

    cap.release()

    return frame_paths, temp_dir

def create_download_zip(frame_paths):
    """
    Crea un archivo ZIP con los fotogramas para descargar
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for i, frame_path in enumerate(frame_paths):
            filename = os.path.basename(frame_path)
            zip_file.write(frame_path, filename)

    return zip_buffer.getvalue()

def get_download_link(zip_bytes):
    """
    Genera un enlace de descarga para el archivo ZIP
    """
    b64 = base64.b64encode(zip_bytes).decode()
    href = f'<a href="data:application/zip;base64,{b64}" download="flip_book.zip">Descargar Flip Book</a>'
    return href

# Título de la app
st.title("🎬 Generador de Flip Books")
st.write("Sube un video y crea tu flip book personalizado")

# Opciones de configuración
col1, col2 = st.columns(2)
with col1:
    interval = st.slider("Intervalo entre fotogramas (segundos)", 0.1, 2.0, 0.5, 0.1)
with col2:
    st.write("")
    st.write("")
    st.write("Un intervalo más pequeño = más páginas")

# Cargar video
uploaded_file = st.file_uploader("Sube tu video", type=['mp4', 'mov', 'avi', 'mkv'])

if uploaded_file is not None:
    # Guardar archivo en disco temporalmente
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_file.write(uploaded_file.read())

    with st.spinner("Procesando video..."):
        # Procesar video
        frame_paths, temp_dir = create_flip_book(temp_file.name, interval)

        if frame_paths:
            st.success(f"¡Listo! Se han extraído {len(frame_paths)} fotogramas para tu flip book.")

            # Mostrar vista previa
            st.subheader("Vista previa de tu flip book")
            preview_count = min(5, len(frame_paths))
            cols = st.columns(preview_count)

            for i in range(preview_count):
                with cols[i]:
                    st.image(frame_paths[i], caption=f"Página {i+1}", use_container_width=True)

            # Crear botón de descarga
            zip_bytes = create_download_zip(frame_paths)
            st.download_button(
                label="⬇️ Descargar Flip Book",
                data=zip_bytes,
                file_name="flip_book.zip",
                mime="application/zip"
            )

            st.write("### Cómo usar tu flip book:")
            st.write("1. Descarga el archivo ZIP")
            st.write("2. Imprime las imágenes (puedes usar cartulina para mayor rigidez)")
            st.write("3. Recorta las imágenes y apílalas en orden")
            st.write("4. Une un lado con grapas o un clip")
            st.write("5. Pasa rápidamente las páginas para ver la animación")
        else:
            st.error("No se pudieron extraer fotogramas del video. Intenta con otro archivo.")

    # Limpieza
    temp_file.close()
    os.unlink(temp_file.name)

else:
    st.info("Sube un video para comenzar")

# Pie de página
st.markdown("---")
st.write("Creado con ❤️ para generar flip books personalizados")
