from config import configDB
import logging


def list_cell4G(cellName):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.mcc, c.mnc, c.dl_earfcn, c.duplex, c.ul_earfcn, c.cell_status, c.cell_txrx, c.emtc_flag, c.pci, " \
          "c.rsi, c.rspwr, c.emtc_flag, c.multi_type, " \
          "IFNULL(a.ant_height, '-') as 'ant_height', IFNULL(a.ant_model, '-') as 'ant_model', " \
          "IFNULL(ra.ant_type, '-') as 'ant_type', IFNULL(a.physical_azimuth, '-') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, '-') as 'm_tilt', IFNULL(a.e_tilt, '-') as 'e_tilt' " \
          "FROM mp_bkk.cell4G c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell4G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.cell_name = '" + cellName + "';"
    return executeSQL(sql)


def list_cell3G(cellName):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.nodeb_name, c.nodeb_id, c.rnc, c.rnc_id, c.lac, " \
          "c.mcc, c.mnc, c.ul_uarfcn, c.dl_uarfcn, c.duplex, c.cell_status, c.cell_txrx, c.psc, " \
          "c.multi_type, c.cpichpwr, c.max_tx_pwr, " \
          "IFNULL(a.ant_height, '-') as 'ant_height', IFNULL(a.ant_model, '-') as 'ant_model', " \
          "IFNULL(ra.ant_type, '-') as 'ant_type', IFNULL(a.physical_azimuth, '-') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, '-') as 'm_tilt', IFNULL(a.e_tilt, '-') as 'e_tilt' " \
          "FROM mp_bkk.cell3G c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell4G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.cell_name = '" + cellName + "';"
    return executeSQL(sql)


def list_cell2G(cellName):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.bts_name, c.bts_id, c.lac, c.rac, " \
          "c.bsc, c.mcc, c.mnc, c.msc, c.bsic, c.ncc, c.freq_band, c.freq_bcch, c.cell_status, " \
          "IFNULL(a.ant_height, '-') as 'ant_height', IFNULL(a.ant_model, '-') as 'ant_model', " \
          "IFNULL(ra.ant_type, '-') as 'ant_type', IFNULL(a.physical_azimuth, '-') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, '-') as 'm_tilt', IFNULL(a.e_tilt, '-') as 'e_tilt' " \
          "FROM mp_bkk.cell2G c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell4G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.cell_name = '" + cellName + "';"
    return executeSQL(sql)


def list_cellNB(cellName):
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.deployment_mode, c.lte_bw, c.ul_earfcn, c.dl_earfcn, c.duplex, c.cell_status, c.cell_txrx, c.pci, " \
          "c.rsi, c.rspwr, c.emtc_flag, c.multi_type, " \
          "IFNULL(a.ant_height, '-') as 'ant_height', IFNULL(a.ant_model, '-') as 'ant_model', " \
          "IFNULL(ra.ant_type, '-') as 'ant_type', IFNULL(a.physical_azimuth, '-') as 'physical_azimuth', " \
          "IFNULL(a.m_tilt, '-') as 'm_tilt', IFNULL(a.e_tilt, '-') as 'e_tilt' " \
          "FROM mp_bkk.cellNB c " \
          "LEFT JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell4G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "LEFT JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "LEFT JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.cell_name = '" + cellName + "';"
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
