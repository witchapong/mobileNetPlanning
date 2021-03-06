from config import configDB
import logging


def multiple_search(siteBBU):
    new_siteBBU = []
    for i in siteBBU:
        # new_siteBBU.append(' b.site_code_config like ' + '\'__________' + i + '\'')
        new_siteBBU.append(' b.site_code_config like \'__________{}\''.format(i))

    return ' or '.join('{}'.format(s) for s in new_siteBBU)


#
# Site's information 1:1
#
def list_siteInfo(siteCode):
    sql = "SELECT s.site_code, l.location_code_slim, l.latitude, l.longitude, s.site_name_en, s.site_name_th, " \
          "l.location_ref_name_en, l.location_ref_name_th, l.amphur_code, l.amphur_name_en, l.region, " \
          "l.network_region, l.mc_zone, l.routing_zone, " \
          "s.site_type, s.station_type, s.building_height, s.tower_type, s.tower_height, s.contact_person, " \
          "s.contact_phone " \
          "FROM site s " \
          "INNER JOIN (select location_ref, location_code_slim, latitude, longitude, location_ref_name_en, " \
          "location_ref_name_th, amphur_code, amphur_name_en, region, network_region, mc_zone, routing_zone " \
          "FROM location) l " \
          "ON s.location_ref = l.location_ref " \
          "WHERE s.site_code in " + siteCode + ";"
    return executeSQL(sql)


#
# BBU's information existed in Site m:1
#
def list_siteBBUInfo(siteCode):
    sql = "SELECT s.site_code, b.site_code_config, b.bbu_vendor, b.bbu_type, " \
          "b.slot0, b.slot1, b.slot2, b.slot3, b.slot4, b.slot5, b.slot6, b.slot7, " \
          "b.slot16, b.slot18, b.slot19 " \
          "FROM site s " \
          "INNER JOIN(SELECT site_code_config, site_code, bbu_vendor, bbu_type, " \
          "slot0, slot1, slot2, slot3, slot4, slot5, slot6, slot7, " \
          "slot16, slot18, slot19 FROM bbu) b ON s.site_code = b.site_code " \
          "WHERE s.site_code in " + siteCode + ";"
    return executeSQL(sql)


#
# BBU's information 1:1
#
# search by nodeName in System
def list_bbuInfo(siteConfig):
    # global searchStatement
    # if system in ['cell4G', 'cell2G', 'cellNB']:
    #     searchStatement = " like '__________" + siteConfig + "';"""
    # elif system == 'cell3G':
    #     searchStatement = " = '" + siteConfig + "';"""
    # else:
    #     searchStatement = multiple_search(siteConfig)
    sql = "SELECT b.site_code_config, b.site_code, b.bbu_vendor, b.bbu_type, " \
          "b.slot0, b.slot1, b.slot2, b.slot3, b.slot4, b.slot5, b.slot6, b.slot7, " \
          "b.slot16, b.slot18, b.slot19 " \
          "FROM bbu b " \
          "WHERE" + multiple_search(siteConfig) + ";"""
    return executeSQL(sql)


#
# Site's information of BBU
#
def list_bbuSiteInfo(siteConfig):
    sql = "SELECT s.site_code, l.location_code_slim, l.latitude, l.longitude, s.site_name_en, s.site_name_th, " \
          "l.location_ref_name_en, l.location_ref_name_th, l.amphur_code, l.amphur_name_en, l.region, " \
          "l.network_region, l.mc_zone, l.routing_zone, " \
          "s.site_type, s.station_type, s.building_height, s.tower_type, s.tower_height, s.contact_person, " \
          "s.contact_phone " \
          "FROM bbu b " \
          "INNER JOIN(SELECT site_code, location_ref, site_name_en, site_name_th, site_type, station_type, " \
          "building_height, tower_type, tower_height, contact_person, contact_phone FROM site) s " \
          "ON s.site_code = b.site_code " \
          "INNER JOIN(SELECT location_ref, location_code_slim, latitude, longitude, location_ref_name_en, " \
          "location_ref_name_th, amphur_code, amphur_name_en, region, network_region, mc_zone, routing_zone " \
          "FROM location) l ON s.location_ref = l.location_ref " \
          "WHERE " + multiple_search(siteConfig) + ";"""
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
