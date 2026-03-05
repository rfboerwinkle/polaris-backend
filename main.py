import os

from flask import Flask
from flask import make_response

# Really, we shouldn't serve these static files ourselves, but for right now it's okay.

# These should be in an env file eventually.
FRONTEND_DIR = "/home/robert/dist/"

# These variables are generated once here, but then const.
SERVABLE = {}
for dirpath, dirnames, filenames in os.walk(FRONTEND_DIR):
    for file in filenames:
        filepath = os.path.join(dirpath, file)
        with open(filepath, "rb") as f:
            SERVABLE[tuple(os.path.relpath(filepath, FRONTEND_DIR).split(os.sep))] = f.read()

app = Flask(__name__)

@app.route("/")
def cludge():
    return puppet_master("")

@app.route("/<path:subpath>")
def puppet_master(subpath):
    p = tuple(subpath.strip("/").split("/"))
    if p not in SERVABLE:
        p = ("ChineseCheckers", "index.html",)

    resp = make_response(SERVABLE[p], 200)
    mime = lookup_mime(p[-1])
    resp.headers["Content-Type"] = mime

    return resp

def lookup_mime(file):
    ext = file.split(".")[-1]
    if ext == "css":
        return "text/css"
    elif ext == "js":
        return "text/javascript"
    elif ext == "wasm":
        return "application/wasm"
    else:
        return "text/html"
