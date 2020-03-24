from flask import Flask, request, send_file
from MIDIspread.convert import Convert
import os

app = Flask(__name__.split(".")[0])

path_mid = os.path.dirname(os.path.abspath(__file__)) + "/midi.mid"


@app.route("/")
def return_midi():
    try:
        if request.method == "POST" or "PUT":
            params = request.get_json()
            converter = Convert(**params)
            converter.data_to_file()
        return send_file(
            path_mid,
            mimetype="audio/midi",
            attachment_filename=path_mid.split("/")[-1],
            as_attachment=True,
        )
    except Exception as e:
        raise e
