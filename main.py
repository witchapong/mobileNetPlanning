from flask import Flask, jsonify, render_template, request, send_file, json, flash, logging
from rq import Queue
from rq.job import Job
from worker import redis_con
from Planner4G import PCIRSIPlanner
from Planner3G import PSCPlanner
from database import cell as Cell, site as Site, bbu as BBU, siteInfo
import requests
import config.configURL

__author__ = 'rpo'

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'rpodev2019'

# set up a Redis connection and initialized a queue
q = Queue(connection=redis_con)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main.html', link=config.configURL.URL)


@app.route("/download.html")
def download():
    return render_template("download.html", link=config.configURL.URL, link_download=config.configURL.Download)


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
    except Exception as e:
        app.logger.error(e)
        return json.dumps({})


@app.route('/download_4G', methods=['POST'])
def download_4G():
    app.logger.info(f'downloading...{request.form["fileName"]}')
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
    except Exception as e:
        app.logger.error(e)
        return json.dumps({})


@app.route('/download_3G', methods=['POST'])
def download_3G():
    app.logger.info(f'downloading...{request.form["fileName"]}')
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
    return render_template("searchCell.html", link=config.configURL.URL)


@app.route('/search', methods=['GET', 'POST'])
def search_data_beta():
    if request.method == 'POST':
        filterParam = request.form.get('filterBy')
        searchParam = request.form.get('searchValue')
        if not (filterParam.capitalize() == 'Search'):
            if filterParam == 'cellname':
                if len(searchParam) != 10:
                    flash('Cellname: must be 10 digit length', 'cell')
                    return render_template('searchCell.html', link=config.configURL.URL,
                                           content_type='application/json')
                else:
                    #
                    # search by CellName, separated by system
                    #
                    cellRes, siteRes, bbuRes = search_for_cellName(searchParam)
                    if cellRes:
                        dataView = {**cellRes, **siteRes, **bbuRes}
                        return render_template('searchCell.html', resSearch=dataView,
                                               link=config.configURL.URL, content_type='application/json')
                    else:
                        flash('{} is not found in existing data'.format(searchParam), 'error')
                        return render_template('searchCell.html', link=config.configURL.URL,
                                               content_type='application/json')
            elif filterParam == 'sitecode':
                if len(searchParam) != 5:
                    flash('SiteCode: must be 5 digit length', 'site')
                    return render_template('searchCell.html', link=config.configURL.URL,
                                           content_type='application/json')
                else:
                    #
                    # search by CellName, cannot be separated, search all
                    #
                    siteRes = search_siteInfo(searchSite=searchParam, search_type='site')
                    bbuRes = search_bbuInfo(searchSiteConfig=searchParam, search_type='site')
                    if siteRes and bbuRes:
                        cellRes = search_for_site(searchParam)
                        if cellRes:
                            dataView = {**cellRes, **siteRes, **bbuRes}
                            return render_template('searchCell.html', resSearch=dataView,
                                                   link=config.configURL.URL, content_type='application/json')
                    else:
                        flash('{} is not found in existing data'.format(filterParam), 'error')
                        return render_template('searchCell.html', link=config.configURL.URL,
                                               content_type='application/json')
            elif filterParam == 'siteconfig':
                if len(searchParam) < 5:
                    flash('SiteConfig: should be equal to SiteCode or other', 'bbu')
                    return render_template('searchCell.html', link=config.configURL.URL,
                                           content_type='application/json')
                else:
                    #
                    # search by NodeName, cannot be separated, search all
                    #
                    bbuRes = search_bbuInfo(searchSiteConfig=searchParam, search_type='bbu')
                    if bbuRes:
                        siteRes = search_siteInfo(searchSite=searchParam, search_type='bbu')
                        cellRes = search_for_bbu(searchParam)
                        dataView = {**cellRes, **siteRes, **bbuRes}
                        return render_template('searchCell.html', resSearch=dataView,
                                               link=config.configURL.URL, content_type='application/json')
                    else:
                        flash('{} is not found in existing data'.format(filterParam), 'error')
                        return render_template('searchCell.html', link=config.configURL.URL,
                                               content_type='application/json')
        else:
            #
            # not select Search option
            #
            flash('Search option is unselected', 'search')
            return render_template('searchCell.html', link=config.configURL.URL,
                                   content_type='application/json')


#
# parser to search by siteCode
#
def search_siteInfo(searchSite, search_type):
    if search_type == 'site':
        site = siteInfo.list_siteInfo(siteCode=searchSite)
        siteDict = {'siteCode': site}
        return siteDict
    elif search_type == 'bbu':
        site = siteInfo.list_bbuSiteInfo(siteConfig=searchSite)
        siteDict = {'siteCode': site}
        return siteDict
    else:
        return None


#
# parser to search by siteConfig
#
def search_bbuInfo(searchSiteConfig, search_type):
    if search_type == 'bbu':
        bbu = siteInfo.list_bbuInfo(siteConfig=searchSiteConfig, system=None)
        bbuDict = {'siteConfig': bbu}
        return bbuDict
    elif search_type == 'site':
        bbu = siteInfo.list_siteBBUInfo(siteCode=searchSiteConfig)
        bbuDict = {'siteConfig': bbu}
        return bbuDict
    else:
        return None


#
# func for 'cells' search by cellName
#
def search_for_cellName(cellName):
    # cellName in System
    global cell
    nb_system = cellName[8:9]
    system = cellName[5:6]  # [L] [W] [B] [L09+A // NB]
    dataDict = {'cell4G': dict(), 'cell3G': dict(), 'cell2G': dict(), 'cellNB': dict()}
    systemDict = {
        'cell4G': 'enodeb_name',
        'cell3G': 'nodeb_name',
        'cell2G': 'bts_name',
        'cellNB': 'enodeb_name'
    }

    if nb_system.upper() == "A":
        if Cell.list_cellNB(cellName=cellName):
            cell = Cell.list_cellNB(cellName=cellName)
            system = 'cellNB'
    else:
        if system in ["5", "6", "7", "8", "L", "S", "Z"]:
            cell = Cell.list_cell4G(cellName=cellName)
            system = 'cell4G'
        elif system in ["1", "2", "3", "4", "D", "P", "W", "Y"]:
            cell = Cell.list_cell3G(cellName=cellName)
            system = 'cell3G'
        elif system in ["B"]:
            cell = Cell.list_cell2G(cellName=cellName)
            system = 'cell2G'
    if cell:
        site = siteInfo.list_siteInfo(siteCode=cell[0]['site_code'])
        bbu = siteInfo.list_bbuInfo(siteConfig=cell[0][systemDict.get(system)], system=system)
    else:
        site, bbu = None, None
    preCell = {system: cell}
    dataDict.update(preCell)
    siteDict = {'siteCode': site}
    bbuDict = {'siteConfig': bbu}
    return dataDict, siteDict, bbuDict


#
# func for 'cells' searched by siteCode
#
def search_for_site(siteCode):
    # site search all
    cell_4g = Site.list_site4G(siteCode=siteCode) if Site.list_site4G(siteCode=siteCode) else dict()
    cell_3g = Site.list_site3G(siteCode=siteCode) if Site.list_site3G(siteCode=siteCode) else dict()
    cell_2g = Site.list_site2G(siteCode=siteCode) if Site.list_site2G(siteCode=siteCode) else dict()
    cell_nb = Site.list_siteNB(siteCode=siteCode) if Site.list_siteNB(siteCode=siteCode) else dict()
    dataDict = {'cell4G': cell_4g, 'cell3G': cell_3g, 'cell2G': cell_2g, 'cellNB': cell_nb}
    return dataDict


#
# func for 'cells' searched by siteConfig
#
def search_for_bbu(siteConfig):
    # all cells in bbu searched all
    cell_4g = BBU.list_bbu4G(siteConfig=siteConfig) if BBU.list_bbu4G(siteConfig=siteConfig) else dict()
    cell_3g = BBU.list_bbu3G(siteConfig=siteConfig) if BBU.list_bbu3G(siteConfig=siteConfig) else dict()
    cell_2g = BBU.list_bbu2G(siteConfig=siteConfig) if BBU.list_bbu2G(siteConfig=siteConfig) else dict()
    cell_nb = BBU.list_bbuNB(siteConfig=siteConfig) if BBU.list_bbuNB(siteConfig=siteConfig) else dict()
    dataDict = {'cell4G': cell_4g, 'cell3G': cell_3g, 'cell2G': cell_2g, 'cellNB': cell_nb}
    return dataDict


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
