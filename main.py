from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE GOOGLE ---
# ¡Recuerda poner tu nueva clave API aquí adentro!
cliente = genai.Client(api_key="AIzaSyCsY69vUz-frJJfJvMEDEHHdMFeIqpo2WY")

# --- INSTRUCCIONES ESTRICTAS DE MARI ---
instrucciones = (
    "Tu nombre es Mariana, pero te gusta que te digan Mari. "
    "Eres una asistente virtual estrictamente enfocada en la asistencia práctica. "
    "TUS ÚNICAS FUNCIONES PERMITIDAS SON:\n"
    "1. Responder preguntas del usuario.\n"
    "2. Resumir información y textos largos.\n"
    "3. Traducir idiomas.\n"
    "4. Ayudar a agendar eventos, planificar horarios y organizar fechas.\n\n"
    "REGLA ESTRICTA: TIENES PROHIBIDO generar textos creativos o de redacción libre "
    "(como escribir correos, ensayos, artículos, historias, poemas o guiones). "
    "Si el usuario te pide redactar algo así, debes negarte educadamente y recordarle "
    "que tus funciones son solo responder, resumir, traducir y agendar. "
    "Responde siempre de forma natural, amigable, concisa y muy directa."
)

class Mensaje(BaseModel):
    texto: str

def obtener_respuesta_mari(mensaje_usuario):
    try:
        # Se corrigió el motor al modelo activo actual de Google (gemini-1.5-flash-latest)
        response = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=mensaje_usuario,
            config=types.GenerateContentConfig(
                system_instruction=instrucciones,
            )
        )
        return response.text
    except Exception as e:
        return f"Error con la API: {str(e)}"
# -----------------------------------------------------

@app.post("/preguntar")
async def chat(mensaje: Mensaje):
    respuesta_ia = obtener_respuesta_mari(mensaje.texto)
    return {"respuesta": respuesta_ia}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)