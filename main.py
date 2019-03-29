from flask import Flask, jsonify, render_template, request, send_file, json
from rq import Queue
from rq.job import Job
from worker import redis_con
from Planner4G import PCIRSIPlanner
from Planner3G import PSCPlanner
from database import customer
import requests

__author__ = 'rpo'

app = Flask(__name__)
app.config['DEBUG'] = True

# set up a Redis connection and initialized a queue
q = Queue(connection=redis_con)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html')


@app.route("/plan4G.html")
def call_4g():
    return render_template("plan4G.html")


@app.route('/upload_4g', methods=['POST'])
def upload_4g():
    global pci_rsi_planner
    if request.method == "POST":
        file = request.files['file']
        pci_rsi_planner = PCIRSIPlanner(file=file)
        try:
            return render_template("plan4G.html")
        except Exception as e:
            return render_template("plan4G.html", text=str(e))


@app.route('/plan_4G', methods=['POST'])
def plan_4G():
    try:
        global job
        app.logger.info("background job running")
        job = q.enqueue(pci_rsi_planner.plan, int(request.form['rCol']), int(request.form['rMod3']),
                        int(request.form['rMin']))
        job_id = job.get_id()

        return json.dumps({'job_id': job_id})
    except:
        return json.dumps({})


@app.route('/download_4G', methods=['POST'])
def download_4G():
    print(f'downloading...{request.form["fileName"]}')
    return send_file(request.form["fileName"],
                     attachment_filename=request.form["fileName"],
                     as_attachment=True)


@app.route("/plan3G.html")
def call_3g():
    return render_template("plan3G.html")


@app.route('/upload_3g', methods=['POST'])
def upload_3g():
    global psc_planner
    if request.method == "POST":
        file = request.files['file']
        psc_planner = PSCPlanner(file=file)
        try:
            return render_template("plan3G.html")
        except Exception as e:
            return render_template("plan3G.html", text=str(e))


@app.route('/plan_3G', methods=['POST'])
def plan_3G():
    try:
        global job
        app.logger.info("background job running")
        job = q.enqueue(psc_planner.plan, int(request.form['rCol']), int(request.form['rMin']))
        job_id = job.get_id()

        return json.dumps({'job_id': job_id})
    except:
        return json.dumps({})


@app.route('/download_3G', methods=['POST'])
def download_3G():
    print(f'downloading...{request.form["fileName"]}')
    return send_file(request.form["fileName"],
                     attachment_filename=request.form["fileName"],
                     as_attachment=True)


#
# job status/result
#
@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=redis_con)
    return json.dumps({'status': job.get_status(), 'meta': job.meta}), 200


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


#
# query from DB
#
@app.route("/searchCell.html")
def call_searchCell():
    return render_template("searchCell.html")


@app.route('/search', methods=['GET', 'POST'])
def search_data():
    if request.method == 'POST':
        filterParam = request.form.get('filterBy')
        searchParam = request.form.get('searchValue')
        if filterParam == 'cellname':
            res1 = customer.list_customers1(searchParam)
            res2 = customer.list_customers2(searchParam)
            return render_template('searchCell.html', result=res1, body=res2, content_type='application/json')
        elif filterParam == 'sitecode':
            res1 = customer.list_customers3(searchParam)
            res2 = customer.list_customers4(searchParam)
            return render_template('searchCell.html', result=res1, body=res2, content_type='application/json')
        else:
            return render_template('searchCell.html', result=None, body=None, content_type='application/json')



@app.route('/search/api/')
def customers_api():
    response = requests.get('https://jsonplaceholder.typicode.com/posts/1/comments', timeout=5)
    result = response.json()
    # for row in result:
    #     print(row)
    return render_template('searchCellApi.html', result=result, content_type='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
