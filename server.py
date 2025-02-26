from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Archivos Excel
archivo_codigos = "codigos.xlsx"
archivo_base = "base_datos.xlsx"

# Crear archivo si no existe
if not os.path.exists(archivo_codigos):
    df = pd.DataFrame(columns=["Código", "Descripción", "Cantidad"])
    df.to_excel(archivo_codigos, index=False)

@app.route("/guardar", methods=["POST"])
def guardar():
    data = request.get_json()

    if not data or "codigo" not in data or "cantidad" not in data:
        return jsonify({"mensaje": "Error: No se recibió el código o cantidad"}), 400

    codigo = str(data.get("codigo", "")).strip()
    cantidad = int(data.get("cantidad", 1))

    if not codigo:
        return jsonify({"mensaje": "Código inválido"}), 400

    try:
        if os.path.exists(archivo_base):
            df_base = pd.read_excel(archivo_base, dtype={"Código": str})
            df_base["Código"] = df_base["Código"].astype(str).str.strip()
        else:
            return jsonify({"mensaje": "Error: No se encontró la base de datos de códigos"}), 500

        descripcion = df_base.loc[df_base["Código"] == codigo, "Descripción"].values
        descripcion = descripcion[0] if len(descripcion) > 0 else "Descripción no encontrada"

        df_codigos = pd.read_excel(archivo_codigos, dtype={"Código": str})
        df_codigos["Cantidad"] = pd.to_numeric(df_codigos["Cantidad"], errors="coerce").fillna(0).astype(int)

        if codigo in df_codigos["Código"].values:
            df_codigos.loc[df_codigos["Código"] == codigo, "Cantidad"] += cantidad
        else:
            nuevo_df = pd.DataFrame([{"Código": codigo, "Descripción": descripcion, "Cantidad": cantidad}])
            df_codigos = pd.concat([df_codigos, nuevo_df], ignore_index=True)

        df_codigos.to_excel(archivo_codigos, index=False)
        return jsonify({"mensaje": f"Código {codigo} registrado correctamente con {cantidad} unidades."})

    except Exception as e:
        return jsonify({"mensaje": f"Error en el servidor: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
