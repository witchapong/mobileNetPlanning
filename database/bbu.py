from config import configDB
import logging


#
# Cells information in SiteConfig level
#
def multiple_search(siteBBU, rat):
    new_siteBBU = []
    systemDict = {
        'cell4G': 'enodeb_name',
        'cell3G': 'nodeb_name',
        'cell2G': 'bts_name',
        'cellNB': 'enodeb_name'
    }
    for i in siteBBU:
        # new_siteBBU.append(' c.nodeb_name like ' + '\'__________' + i + '\'')
        new_siteBBU.append(' {} like \'__________{}\''.format(systemDict.get(rat), i))
    return ' or '.join('{}'.format(s) for s in new_siteBBU)


#
# change WHERE CLAUSE
#
def list_bbu4G(siteConfig, rat):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.mcc, c.mnc, c.ul_earfcn, c.dl_earfcn, c.duplex, c.cell_status, c.cell_txrx, c.emtc_flag, c.pci, c.rsi, " \
          "c.rspwr, c.emtc_flag, c.multi_type, " \
          "IFNULL(a.ant_height, 'n/a') as 'ant_height', IFNULL(a.ant_model, 'n/a') as 'ant_model'," \
          "IFNULL(ra.ant_type, 'n/a') as 'ant_type', IFNULL(a.physical_azimuth, 'n/a') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, 'n/a') as 'm_tilt', IFNULL(a.e_tilt, 'n/a') as 'e_tilt'" \
          "FROM mp_bkk.cell4G c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell4G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE" + multiple_search(siteConfig, rat) + ";"
    return executeSQL(sql)


def list_bbu3G(siteConfig, rat):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.nodeb_name, c.nodeb_id, c.rnc, c.rnc_id, c.lac, " \
          "c.mcc, c.mnc, c.ul_uarfcn, c.dl_uarfcn, c.duplex, c.cell_status, c.cell_txrx, c.psc, " \
          "c.multi_type, c.cpichpwr, c.max_tx_pwr, " \
          "IFNULL(a.ant_height, 'n/a') as 'ant_height', IFNULL(a.ant_model, 'n/a') as 'ant_model'," \
          "IFNULL(ra.ant_type, 'n/a') as 'ant_type', IFNULL(a.physical_azimuth, 'n/a') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, 'n/a') as 'm_tilt', IFNULL(a.e_tilt, 'n/a') as 'e_tilt'" \
          "FROM mp_bkk.cell3G c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell3G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE" + multiple_search(siteConfig, rat) + ";"
    return executeSQL(sql)


def list_bbu2G(siteConfig, rat):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.bts_name, c.bts_id, c.lac, c.rac, " \
          "c.bsc, c.mcc, c.mnc, c.msc, c.bsic, c.ncc, c.freq_band, c.freq_bcch, c.cell_status, " \
          "IFNULL(a.ant_height, 'n/a') as 'ant_height', IFNULL(a.ant_model, 'n/a') as 'ant_model'," \
          "IFNULL(ra.ant_type, 'n/a') as 'ant_type', IFNULL(a.physical_azimuth, 'n/a') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, 'n/a') as 'm_tilt', IFNULL(a.e_tilt, 'n/a') as 'e_tilt'" \
          "FROM mp_bkk.cell2G c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell2G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE" + multiple_search(siteConfig, rat) + ";"
    return executeSQL(sql)


def list_bbuNB(siteConfig, rat):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.deployment_mode, c.lte_bw, c.dl_earfcn, c.ul_earfcn, c.duplex, c.cell_status, c.cell_txrx, c.pci, " \
          "c.rsi, c.rspwr, c.multi_type, " \
          "IFNULL(a.ant_height, 'n/a') as 'ant_height', IFNULL(a.ant_model, 'n/a') as 'ant_model'," \
          "IFNULL(ra.ant_type, 'n/a') as 'ant_type', IFNULL(a.physical_azimuth, 'n/a') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, 'n/a') as 'm_tilt', IFNULL(a.e_tilt, 'n/a') as 'e_tilt'" \
          "FROM mp_bkk.cellNB c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cellNB_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE" + multiple_search(siteConfig, rat) + ";"
    return executeSQL(sql)


def executeSQL(statement):
    executor = configDB.Database()
    try:
        with executor.cur:
            executor.cur.execute(statement)
            response = executor.cur.fetchall()
            if len(response) > 0:
                return response
            else:
                return dict()
    except Exception as e:
        logging.info("error from database {}".format(e))
    finally:
        executor.con.close()
        logging.info("MySQL connection is closed")
