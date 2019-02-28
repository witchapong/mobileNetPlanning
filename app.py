from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, emit
from Planner4G import PCIRSIPlanner
from Planner3G import PSCPlanner
from threading import Lock, Thread, Event
import asyncio
import websockets

__author__ = 'Mick'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app)

# async def send_after_finish(websocket, path):
#     await websocket.send("Dummy")

thread_4g = Thread()
thread_4g_stop_event = Event()


@app.route("/")
def main():
    return render_template("main.html")


#
# main method planning 4G
#
@socketio.on('plan', namespace='/plan_4g')
def plan_4g(message):
    # global thread_4g
    # global plan_params_4g
    # plan_params_4g = message
    #
    # with thread_4g_lock:
    #     if thread_4g is None:
    #         thread_4g = socketio.start_background_task(plan_4g_thread)

    global thread_4g
    global plan_params_4g

    plan_params_4g = message  # param from 

    if not thread_4g.isAlive():
        print('Starting thread...')
        thread_4g = Plan4GThread()
        thread_4g.start()

    emit('my_response', {'message': 'Server: Plan accepted...'})


class Plan4GThread(Thread):

    def __init__(self):
        super(Plan4GThread, self).__init__()

    def plan(self):

        global filename4g

        try:
            df = pci_rsi_planner.plan(int(plan_params_4g['rCol']), int(plan_params_4g['rMod3']),
                                      int(plan_params_4g['rMin']), socketio)

            filename4g = '4g_plan_result.xlsx'
            df.to_excel(filename4g, index=False)

            print('plan finished...')
            socketio.emit('plan finished', {'message': 'plan finished'}, namespace='/plan_4g')

            # thread_4g_stop_event.set()

        except:
            socketio.emit('plan error', {'message': 'plan error'}, namespace='/plan_4g')

    def run(self):
        self.plan()


#
# Client socket.io connect to socket
#
@socketio.on('connect', namespace='/plan_4g')
def test_connect():
    print("A client has connected...")
    emit('my_response', {'message': 'Server: A client has connected...'})


#
# Client socket.io disconnect from socket
#
@socketio.on('disconnect', namespace='/plan_4g')
def test_disconnect():
    print('Client disconnected...')


# --------------------4G APPLICATION--------------------
@app.route("/4g.html")
def call_4g():
    return render_template("4g.html")


#
# when Client upload file to server
#
@app.route('/4g-upload-success', methods=['POST'])
def upload_4g():
    global pci_rsi_planner
    if request.method == "POST":
        file = request.files['file']
        try:
            pci_rsi_planner = PCIRSIPlanner(file)
            return render_template("4g.html", text='Upload completed!')
        except Exception as e:
            return render_template("4g.html", text=str(e))


#
# result is showing here
#
@app.route('/4g-download')
def download_4g():
    return send_file(filename4g, attachment_filename=filename4g, as_attachment=True)


# --------------------3G APPLICATION--------------------
# @app.route("/3g.html")
# def call_3g():
#     return render_template("3g.html")
#
# @socketio.on('connect',namespace='/plan_3g')
# def test_connect():
#     print("Client has connected...")
#
# @app.route('/3g-upload-success', methods=['POST'])
# def upload_3g():
#     global psc_planner
#     if request.method=="POST":
#         file=request.files['file']
#         try:
#             psc_planner = PSCPlanner(file)
#             return render_template("3g.html", text='Upload completed!')
#         except Exception as e:
#             return render_template("3g.html", text=str(e))
#
# @socketio.on('plan',namespace='/plan_3g')
# def plan_3g(message):
#     print(message)
#     global thread_3g
#     global plan_params_3g
#     plan_params_3g = message
#
#     with thread_3g_lock:
#         if thread_3g is None:
#             print("Starting Thread..")
#             thread_3g = socketio.start_background_task(plan_3g_thread)
#     emit('my_response', {'message': 'Server: Plan accepted...'})
#
# @socketio.on('disconnect', namespace='/plan_3g')
# def test_disconnect():
#     print('Client disconnected...')
#
# @app.route('/3g-download')
# def download_3g():
#     return send_file(filename3g, attachment_filename=filename3g, as_attachment=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
