from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)
connected_users = {}


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/chat", methods=["POST"])
def chat():
    username = request.form["username"]
    room = request.form["room"]
    return render_template("chat.html", username=username, room=room)


@socketio.on("chat message")
def handle_chat(json):
    emit("chat message", json, broadcast=True, include_self=False, to=json["room"])


@socketio.on("writing")
def handle_writing(json):
    emit(
        "writing",
        json,
        broadcast=True,
        include_self=False,
        to=json["room"],
    )


@socketio.on("connect")
def on_connect(auth):
    room = auth["room"]
    username = auth["username"]
    connected_users[request.sid] = (username, room)
    join_room(room)
    emit("connected users", connected_users, broadcast=True, to=room)


@socketio.on("disconnect")
def on_disconnect():
    room = connected_users[request.sid][1]
    leave_room(room)
    del connected_users[request.sid]
    emit("connected users", connected_users, broadcast=True, to=room)


if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=True)
