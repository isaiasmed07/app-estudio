from flask import Flask, request, jsonify
import os
import requests

print(">>> BLOB_READ_WRITE_TOKEN =", os.environ.get("BLOB_READ_WRITE_TOKEN"))

app = Flask(__name__)

def _get_token():
    # Prioriza BLOB_READ_WRITE_TOKEN; puedes añadir aliases si los usas en prod
    return os.environ.get("BLOB_READ_WRITE_TOKEN") or os.environ.get("VERCEL_BLOB_TOKEN")

# Health
@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ok", "msg": "testeo server"}), 200

# Listar blobs por scope o por url pública
@app.route('/api/listar-blobs', methods=['GET'])
def listar_blobs():
    scope = request.args.get('scope')
    public_url = request.args.get('url')

    if not scope and not public_url:
        return jsonify({"error": "Falta parámetro 'scope' o 'url'"}), 400

    if public_url:
        if ".public." not in public_url:
            return jsonify({"error": "La url indicada no parece ser pública de vercel blob"}), 400
        # extraer scope: https://<scope>.public.blob.vercel-storage.com/archivo
        try:
            scope = public_url.split("//")[1].split(".")[0]
        except Exception as e:
            return jsonify({"error": f"No se pudo extraer scope desde la URL: {str(e)}"}), 400

    token = _get_token()
    if not token:
        return jsonify({"error": "Falta BLOB_READ_WRITE_TOKEN en variables de entorno"}), 500

    list_url = f"https://blob.vercel-storage.com/{scope}/"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(list_url, headers=headers, timeout=15)
    except Exception as e:
        return jsonify({"error": "Fallo al contactar Vercel Blob", "exception": str(e)}), 500

    # Intentamos parsear JSON si lo devuelve
    try:
        resp_json = resp.json()
    except Exception:
        resp_json = None

    # Debug
    print("🔎 Listar blobs ->", list_url)
    print("🔎 Status:", resp.status_code)
    if resp_json is None:
        print("🔎 Text:", resp.text)
    else:
        print("🔎 JSON keys:", list(resp_json.keys()) if isinstance(resp_json, dict) else type(resp_json))

    if not resp.ok:
        return jsonify({
            "error": "No se pudo listar blobs",
            "status": resp.status_code,
            "respuesta": resp_json if resp_json is not None else resp.text,
            "url_usada": list_url
        }), resp.status_code

    return jsonify({"scope": scope, "data": resp_json}), 200

# Eliminar archivo (acepta url pública, url privada o scope+filename)
@app.route('/api/eliminar-archivo', methods=['POST'])
def eliminar_archivo():
    data = request.get_json(silent=True) or {}
    url = data.get('url') or data.get('public_url') or data.get('private_url')
    scope = data.get('scope')
    filename = data.get('filename')

    if not url and (not scope or not filename):
        return jsonify({"error": "Falta 'url' (pública o privada) o (scope + filename)"}), 400

    delete_url = None

    try:
        if url:
            # Caso URL pública: https://<scope>.public.blob.vercel-storage.com/<filename>
            if ".public." in url:
                try:
                    scope = url.split("//")[1].split(".")[0]
                    filename = url.split("/")[-1]
                    delete_url = f"https://blob.vercel-storage.com/{scope}/{filename}"
                except Exception as e:
                    return jsonify({"error": f"No se pudo parsear la URL pública: {str(e)}"}), 400

            # Caso URL privada: https://blob.vercel-storage.com/<scope>/<filename...>
            elif url.startswith("https://blob.vercel-storage.com/") or url.startswith("http://blob.vercel-storage.com/"):
                parts = url.split("/")
                # parts example: ["https:", "", "blob.vercel-storage.com", "scope", "path", ...]
                if len(parts) >= 5:
                    scope = parts[3]
                    filename = "/".join(parts[4:])  # filename may contain slashes
                    delete_url = f"https://blob.vercel-storage.com/{scope}/{filename}"
                else:
                    return jsonify({"error": "URL privada no válida (formato incorrecto)"}), 400
            else:
                return jsonify({"error": "URL no válida para Vercel Blob (ni pública ni privada)"}), 400
        else:
            # Si no se pasó url, usar scope + filename
            delete_url = f"https://blob.vercel-storage.com/{scope}/{filename}"

        token = _get_token()
        if not token:
            return jsonify({"error": "Falta BLOB_READ_WRITE_TOKEN en variables de entorno"}), 500

        headers = {"Authorization": f"Bearer {token}"}

        # Debug prints
        print("🔎 Intentando eliminar:", delete_url)
        resp = requests.delete(delete_url, headers=headers, timeout=15)
        print("🔎 Respuesta:", resp.status_code, resp.text)

        # Consideramos éxito si el status es 2xx
        if 200 <= resp.status_code < 300:
            return jsonify({"message": f"Archivo {filename} eliminado correctamente"}), 200

        # intentar parsear JSON de respuesta
        try:
            resp_json = resp.json()
        except Exception:
            resp_json = resp.text

        return jsonify({
            "error": "No se pudo eliminar el archivo",
            "status": resp.status_code,
            "respuesta": resp_json,
            "url_usada": delete_url
        }), 500

    except Exception as e:
        print("⚠️ Excepción:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ejecuta en modo debug para ver prints y stack traces en local
    app.run(debug=True)
