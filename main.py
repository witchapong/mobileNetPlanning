from flask import Flask, jsonify, render_template, request, send_file, redirect, url_for

from tasks import count_words_at_url, background_job

from rq import Queue
from rq.job import Job
from worker import redis_con
from Planner4G import PCIRSIPlanner

__author__ = 'prachyab'

app = Flask(__name__)
app.config['DEBUG'] = True

# set up a Redis connection and initialized a queue
q = Queue(connection=redis_con)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/plan4G.html")
def call_4g():
    return render_template("plan4G.html")


#
# when Client upload file to server
#
@app.route('/upload_4g', methods=['POST'])
def upload_4g():
    global pci_rsi_planner
    if request.method == "POST":
        file = request.files['file']
        pci_rsi_planner = PCIRSIPlanner(file=file)
        try:
            return render_template("plan4G.html", text='upload completed')
        except Exception as e:
            return render_template("plan4G.html", text=str(e))


@app.route('/plan_4G/')
def plan_4G():
    global filename4g
    global job
    results = {}
    # global plan_params_4g
    # plan_params_4g['rCol'] = 5000
    # plan_params_4g['rMod3'] = 100
    # plan_params_4g['rMin'] = 100
    # df = pci_rsi_planner.plan(5000, 100, 100)

    filename4g = '4g_plan_result.xlsx'
    app.logger.info("background job running")
    job = q.enqueue(pci_rsi_planner.plan, 5000, 100, 100)
    job_id = job.get_id()
    print("job id: " + str(job_id))

    return render_template("plan4G.html", text='job running')


@app.route('/download_4G')
def download_4G():
    return send_file(filename4g,
                     attachment_filename=filename4g,
                     as_attachment=True)


#
# job task
#
@app.route('/rq/', methods=['GET', 'POST'])
def job():
    results = {}
    app.logger.info("rq running")
    url = 'http://nvie.com'
    job = q.enqueue(count_words_at_url, url)
    print("job result: " + str(job.result))
    job_id = job.get_id()
    print("job id: " + str(job_id))

    return jsonify({'results': results,
                    'job_id': job_id})


#
# job task
#
@app.route('/bgtask/', methods=['GET', 'POST'])
def background():
    results = {}
    app.logger.info("bg running")
    job = q.enqueue(background_job)
    print("job result: " + str(job.result))
    job_id = job.get_id()
    print("job id: " + str(job_id))

    return jsonify({'results': results,
                    'job_id': job_id})


#
# job status/result
#
@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=redis_con)
    if job.is_finished:
        return jsonify(job.result), 200
    else:
        return jsonify('failed'), 202


@app.route('/status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = q.fetch_job(job_id)
    if job is None:
        response = {'status': 'unknown'}
    else:
        response = {
            'id': job.get_id(),
            'status': job.get_status()
        }
        if job.is_failed:
            response['message'] = job.exc_info.strip().split('\n')[-1]
    return jsonify(response)


if __name__ == "__main__":
    app.run()
