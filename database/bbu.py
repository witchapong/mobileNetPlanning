from config import configDB


def list_bbu4G(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.mcc, c.mnc, c.dl_earfcn, c.duplex, c.cell_status, c.cell_txrx, c.emtc_flag, c.pci, " \
          "s.site_name_en, s.site_name_th, s.contact_person, " \
          "b.bbu_type," \
          "l.latitude, l.longitude, l.routing_zone " \
          "FROM mp_bkk.cell4G c " \
          "INNER JOIN (SELECT site_code, location_ref, site_name_th, site_name_en, contact_person FROM site) s " \
          "ON c.site_code = s.site_code " \
          "INNER JOIN (SELECT location_ref, latitude, longitude, routing_zone FROM location) l " \
          "ON s.location_ref = l.location_ref " \
          "LEFT JOIN (SELECT site_code,site_code_config, bbu_type FROM bbu) b " \
          "ON s.site_code = b.site_code WHERE c.enodeb_name = '" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result


def list_bbu3G(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.nodeb_name, c.nodeb_id, c.rnc, c.rnc_id, c.lac, " \
          "c.mcc, c.mnc, c.dl_uarfcn, c.duplex, c.cell_status, c.cell_txrx, c.psc, " \
          "s.site_name_en, s.site_name_th, s.contact_person, " \
          "b.bbu_type," \
          "l.latitude, l.longitude, l.routing_zone " \
          "FROM mp_bkk.cell3G c " \
          "INNER JOIN (SELECT site_code, location_ref, site_name_th, site_name_en, contact_person FROM site) s " \
          "ON c.site_code = s.site_code " \
          "INNER JOIN (SELECT location_ref, latitude, longitude, routing_zone FROM location) l " \
          "ON s.location_ref = l.location_ref " \
          "LEFT JOIN (SELECT site_code,site_code_config, bbu_type FROM bbu) b " \
          "ON s.site_code = b.site_code WHERE c.nodeb_name like '__________" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result


def list_bbu2G(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.bts_name, c.bts_id, c.lac, c.rac, " \
          "c.bsc, c.mcc, c.mnc, c.msc, c.bsic, c.ncc, c.freq_band, c.freq_bcch, c.cell_status, " \
          "s.site_name_en, s.site_name_th, s.contact_person, " \
          "b.bbu_type," \
          "l.latitude, l.longitude, l.routing_zone " \
          "FROM mp_bkk.cell2G c " \
          "INNER JOIN (SELECT site_code, location_ref, site_name_th, site_name_en, contact_person FROM site) s " \
          "ON c.site_code = s.site_code " \
          "INNER JOIN (SELECT location_ref, latitude, longitude, routing_zone FROM location) l " \
          "ON s.location_ref = l.location_ref " \
          "LEFT JOIN (SELECT site_code, site_code_config, bbu_type FROM bbu) b " \
          "ON s.site_code = b.site_code WHERE c.bts_name = '" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result


def list_bbuNB(siteConfig):
    executor = configDB.Database()
    sql = "SELECT c.cell_name, c.site_code, c.system, c.cell_id, c.enodeb_name, c.enodeb_id, c.lac, c.tac, " \
          "c.deployment_mode, c.lte_bw, c.dl_earfcn, c.duplex, c.cell_status, c.cell_txrx, c.pci, " \
          "s.site_name_en, s.site_name_th, s.contact_person, " \
          "b.bbu_type," \
          "l.latitude, l.longitude, l.routing_zone " \
          "FROM mp_bkk.cellNB c " \
          "INNER JOIN (SELECT site_code, location_ref, site_name_th, site_name_en, contact_person FROM site) s " \
          "ON c.site_code = s.site_code " \
          "INNER JOIN (SELECT location_ref, latitude, longitude, routing_zone FROM location) l " \
          "ON s.location_ref = l.location_ref " \
          "LEFT JOIN (SELECT site_code,site_code_config, bbu_type FROM bbu) b " \
          "ON s.site_code = b.site_code WHERE c.enodeb_name = '" + siteConfig + "';"
    executor.cur.execute(sql)
    result = executor.cur.fetchall()
    executor.cur.close()

    return result
