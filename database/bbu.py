from config import configDB


def list_bbu4G(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.mcc, c.mnc, c.ul_earfcn, c.dl_earfcn, c.duplex, c.cell_status, c.cell_txrx, c.emtc_flag, c.pci, c.rsi," \
          " c.rspwr, c.emtc_flag, c.multi_type, " \
          "a.ant_height, a.ant_model, ra.ant_type, a.ant_height, a.physical_azimuth, a.m_tilt, a.e_tilt " \
          "FROM mp_bkk.cell4G c " \
          "INNER JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell4G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "INNER JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "INNER JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.enodeb_name = '" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result


def list_bbu3G(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.nodeb_name, c.nodeb_id, c.rnc, c.rnc_id, c.lac, " \
          "c.mcc, c.mnc, c.ul_uarfcn, c.dl_uarfcn, c.duplex, c.cell_status, c.cell_txrx, c.psc, " \
          "c.multi_type, c.cpichpwr, c.max_tx_pwr, " \
          "a.ant_height, a.ant_model, ra.ant_type, a.ant_height, a.physical_azimuth, a.m_tilt, a.e_tilt " \
          "FROM mp_bkk.cell3G c " \
          "INNER JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell3G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "INNER JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "INNER JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.nodeb_name like '__________" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result


def list_bbu2G(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.bts_name, c.bts_id, c.lac, c.rac, " \
          "c.bsc, c.mcc, c.mnc, c.msc, c.bsic, c.ncc, c.freq_band, c.freq_bcch, c.cell_status, " \
          "a.ant_height, a.ant_model, ra.ant_type, a.ant_height, a.physical_azimuth, a.m_tilt, a.e_tilt " \
          "FROM mp_bkk.cell2G c " \
          "INNER JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cell2G_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "INNER JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "INNER JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.bts_name = '" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result


def list_bbuNB(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.deployment_mode, c.lte_bw, c.dl_earfcn, c.ul_earfcn, c.duplex, c.cell_status, c.cell_txrx, c.pci, " \
          "c.rsi, c.rspwr, c.multi_type, " \
          "a.ant_height, a.ant_model, ra.ant_type, a.ant_height, a.physical_azimuth, a.m_tilt, a.e_tilt " \
          "FROM mp_bkk.cellNB c " \
          "INNER JOIN (SELECT cell_name, ant_id, ant_logical_beam FROM cellNB_antenna) ca " \
          "ON c.cell_name = ca.cell_name " \
          "INNER JOIN (SELECT ant_id, ant_logical_beam, ant_model, m_tilt, e_tilt, physical_azimuth, ant_height " \
          "FROM antenna) a ON ca.ant_id = a.ant_id AND ca.ant_logical_beam = a.ant_logical_beam " \
          "INNER JOIN (SELECT ant_model, ant_logical_beam, ant_type " \
          "FROM reference_antenna) ra ON a.ant_model = ra.ant_model AND a.ant_logical_beam = ra.ant_logical_beam " \
          "WHERE c.enodeb_name = '" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result
