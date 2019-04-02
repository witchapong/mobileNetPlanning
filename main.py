from flask import Flask, jsonify, render_template, request, send_file, json, flash
from rq import Queue
from rq.job import Job
from worker import redis_con
from Planner4G import PCIRSIPlanner
from Planner3G import PSCPlanner
from database import cell as Cell, site as Site, bbu as BBU
import requests
from config.crossfunction import URL as cross_url
from config.export import Download as download_url

__author__ = 'rpo'

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'rpodev2019'

# set up a Redis connection and initialized a queue
q = Queue(connection=redis_con)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html', link=cross_url)


@app.route("/download.html")
def download():
    return render_template("download.html", link=cross_url, link_download=download_url)


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
def search_cell():
    return render_template("searchCell.html", link=cross_url)


@app.route('/search', methods=['GET', 'POST'])
def search_data():
    if request.method == 'POST':
        filterParam = request.form.get('filterBy')
        searchParam = request.form.get('searchValue')
        if filterParam == 'cellname':
            if len(searchParam) != 10:
                flash('Cellname: must be 10 digit length', 'cell')
                return render_template('searchCell.html', result=None, link=cross_url, content_type='application/json')
            else:
                cell, system = search_for_cell(searchParam)
                if cell:
                    if system == 'LTE':
                        return render_template('searchCell.html', data_4g=cell, data_3g=None, data_2g=None,
                                               data_nb=None, link=cross_url, content_type='application/json')
                    elif system == 'UMTS':
                        return render_template('searchCell.html', data_4g=None, data_3g=cell, data_2g=None,
                                               data_nb=None, link=cross_url, content_type='application/json')
                    elif system == 'GSM':
                        return render_template('searchCell.html', data_4g=None, data_3g=None, data_2g=cell,
                                               data_nb=None, link=cross_url, content_type='application/json')
                    elif system == 'NB':
                        return render_template('searchCell.html', data_4g=None, data_3g=None, data_2g=None,
                                               data_nb=cell, link=cross_url, content_type='application/json')
                else:
                    flash('{} is not found in existing data'.format(searchParam), 'error')
                    return render_template('searchCell.html', result=None, link=cross_url,
                                           content_type='application/json')
        elif filterParam == 'sitecode':
            if len(searchParam) != 5:
                flash('SiteCode: must be 5 digit length', 'site')
                return render_template('searchCell.html', result=None, content_type='application/json')
            else:
                cell4G, cell3G, Cell2G, CellNB = search_for_site(searchParam)
                if cell4G:
                    if cell4G and cell3G and Cell2G and CellNB:
                        return render_template('searchCell.html', data_4g=cell4G, data_3g=cell3G, data_2g=Cell2G,
                                               data_nb=CellNB, link=cross_url, content_type='application/json')
                    elif cell4G and cell3G and Cell2G:
                        return render_template('searchCell.html', data_4g=cell4G, data_3g=cell3G, data_2g=Cell2G,
                                               data_nb=None, link=cross_url, content_type='application/json')
                    elif cell4G and cell3G:
                        return render_template('searchCell.html', data_4g=cell4G, data_3g=cell3G, data_2g=None,
                                               data_nb=None, link=cross_url, content_type='application/json')
                    elif cell4G:
                        return render_template('searchCell.html', data_4g=cell4G, data_3g=None, data_2g=None,
                                               data_nb=None, link=cross_url, content_type='application/json')
                else:
                    flash('{} is not found in existing data'.format(searchParam), 'error')
                    return render_template('searchCell.html', result=None, link=cross_url,
                                           content_type='application/json')

        elif filterParam == 'siteconfig':
            # siteConfig search in BBU >> exists or not
            # siteConfig in 4G is eNodeBName
            # siteConfig in 3G is NodeBName
            # siteConfig in 2G and NB
            cell4G, cell3G, Cell2G, CellNB = search_for_bbu(searchParam)
            if cell4G:
                if cell4G and cell3G and Cell2G and CellNB:
                    return render_template('searchCell.html', data_4g=cell4G, data_3g=cell3G, data_2g=Cell2G,
                                           data_nb=CellNB, link=cross_url, content_type='application/json')
                elif cell4G and cell3G and Cell2G:
                    return render_template('searchCell.html', data_4g=cell4G, data_3g=cell3G, data_2g=Cell2G,
                                           data_nb=None, link=cross_url, content_type='application/json')
                elif cell4G and cell3G:
                    return render_template('searchCell.html', data_4g=cell4G, data_3g=cell3G, data_2g=None,
                                           data_nb=None, link=cross_url, content_type='application/json')
                elif cell4G:
                    return render_template('searchCell.html', data_4g=cell4G, data_3g=None, data_2g=None, data_nb=None,
                                           link=cross_url, content_type='application/json')
                else:
                    return render_template('searchCell.html', data_4g=None, data_3g=None, data_2g=None, data_nb=None,
                                           link=cross_url, content_type='application/json')
            else:
                flash('{} is not found in existing data'.format(searchParam), 'error')
                return render_template('searchCell.html', result=None, link=cross_url,
                                       content_type='application/json')


def search_for_cell(cellName):
    # cellname in System
    global cell
    nb_system = cellName[8:9]
    system = cellName[5:6]  # [L] [W] [B] [L09+A // NB]
    if nb_system.upper() == "A":
        cell = Cell.list_cellNB(cellName=cellName)
        system = 'NB'
    else:
        if system in ["5", "6", "7", "8", "L", "S", "Z"]:
            cell = Cell.list_cell4G(cellName=cellName)
            system = 'LTE'
        elif system in ["1", "2", "3", "4", "D", "P", "W", "Y"]:
            cell = Cell.list_cell3G(cellName=cellName)
            system = 'UMTS'
        elif system in ["B"]:
            cell = Cell.list_cell2G(cellName=cellName)
            system = 'GSM'
    return cell, system


def search_for_site(siteCode):
    # site search all
    cell_4g = Site.list_site4G(siteCode=siteCode)
    cell_3g = Site.list_site3G(siteCode=siteCode)
    cell_2g = Site.list_site2G(siteCode=siteCode)
    cell_nb = Site.list_siteNB(siteCode=siteCode)
    return cell_4g, cell_3g, cell_2g, cell_nb


def search_for_bbu(siteConfig):
    # all cells in bbu searched all
    cell_4g = BBU.list_bbu4G(siteConfig=siteConfig)
    cell_3g = BBU.list_bbu3G(siteConfig=siteConfig)
    cell_2g = BBU.list_bbu2G(siteConfig=siteConfig)
    cell_nb = BBU.list_bbuNB(siteConfig=siteConfig)
    return cell_4g, cell_3g, cell_2g, cell_nb


@app.route('/search/api/')
def customers_api():
    response = requests.get('https://jsonplaceholder.typicode.com/posts/1/comments', timeout=5)
    result = response.json()
    # for row in result:
    #     print(row)
    return render_template('searchCellApi.html', result=result, content_type='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0',
            port=5003)
