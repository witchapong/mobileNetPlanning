# import fiona
# from shapely.geometry import Point
# from shapely.geometry import shape
import pandas as pd
import numpy as np
from pyproj import Proj
from geopy import distance

class PCIRSIPlanner:

    # poly = fiona.open(f"src/Border_BKK_rv3_region.shp")
    # poly_obj = [shape(item['geometry']) for item in poly]

    # define PCI range
    pci_inner_macro = range(0, 306)
    pci_inner_micro = range(0, 306)
    pci_inner_pico = range(324, 504)
    pci_outer_macro = range(0, 402)
    pci_outer_micro = range(0, 402)
    pci_outer_pico = range(420, 504)
    pci_border = range(120, 300)

    # define RSI range
    rsi_inner_macro = range(0, 630, 6)
    rsi_inner_micro = range(0, 630, 6)
    rsi_inner_pico = range(630, 838, 6)
    rsi_outer_macro = range(0, 720, 6)
    rsi_outer_micro = range(720, 750, 6)
    rsi_outer_pico = range(750, 838, 6)
    rsi_border = range(210, 510, 6)

    def __init__(self,file):
        self.plan_file = pd.read_excel(file)

    # def map2poly(self,x,df):
    #
    #     if pd.isna(x['AREA_TYPE']):
    #         point = Point(x['LNG'], x['LAT'])
    #         for i, ply in enumerate(self.poly_obj):
    #             if ply.contains(point):
    #                 return self.poly[i]['properties']['AREA_TYPE']
    #         else:
    #
    #             # find the area type from the closest available lat,lng
    #             df['DISTANCE'] = df.apply(
    #                 lambda col: distance.distance((col['LAT'], col['LNG']), (x['LAT'], x['LNG'])), axis=1)
    #             df['DISTANCE'] = df['DISTANCE'].apply(lambda x: x.km)
    #             temp_df = df[(~df['AREA_TYPE'].isna())]
    #             return temp_df[temp_df['DISTANCE'] == temp_df['DISTANCE'].min()].iloc[0]['AREA_TYPE']
    #     else:
    #         return x['AREA_TYPE']


    # create function for calculating circle overlapped area
    def circle_ol_area(self,x,r_mod3):
        r = r_mod3 / 1000
        if x['CELL2CELL_DIST'] <= 2 * r:
            return 2 * r ** 2 * np.arccos(x['CELL2CELL_DIST'] / 2 / r) - x['CELL2CELL_DIST'] / 2 * np.sqrt(
                (2 * r - x['CELL2CELL_DIST']) * (2 * r + x['CELL2CELL_DIST']))
        else:
            return 0.0

    def plan(self,r_col,r_mod3,dist_min,skt):

        # skt.sleep(0)
        all_info = self.plan_file.copy()
        all_info['COPCI_NEAREST_DIST'] = 0
        all_info['CORSI_NEAREST_DIST'] = 0
        # all_info['AREA_TYPE'] = all_info.apply(lambda x: self.map2poly(x,all_info), axis=1)
        all_info['AREA_TYPE']=all_info['AREA_TYPE'].fillna("border")
        all_info['AREA_TYPE'] = all_info['AREA_TYPE'].apply(lambda x: x.lower())

        # split plan file to df of existing cells and cells to plan
        cell2plan = all_info[all_info['PCI'] == -1].reset_index(drop=True)
        lte_cell_info = all_info[all_info['PCI'] != -1].reset_index(drop=True)

        for i in range(cell2plan.shape[0]):

            skt.sleep(0)
            # calculate distance
            lat = cell2plan.iloc[i]['LAT']
            lng = cell2plan.iloc[i]['LNG']
            direction = cell2plan.iloc[i]['DIRECTION']

            # determine pci&rsi range
            if cell2plan.iloc[i]['AREA_TYPE'].lower() == 'inner':
                if cell2plan.iloc[i]['SITE_TYPE'].lower() == 'macro':
                    pci_range = self.pci_inner_macro
                    rsi_range = self.rsi_inner_macro
                elif cell2plan.iloc[i]['SITE_TYPE'].lower() == 'micro':
                    pci_range = self.pci_inner_micro
                    rsi_range = self.rsi_inner_micro
                else:
                    pci_range = self.pci_inner_pico
                    rsi_range = self.rsi_inner_pico
            elif cell2plan.iloc[i]['AREA_TYPE'].lower() == 'outer':
                if cell2plan.iloc[i]['SITE_TYPE'].lower() == 'macro':
                    pci_range = self.pci_outer_macro
                    rsi_range = self.rsi_outer_macro
                elif cell2plan.iloc[i]['SITE_TYPE'].lower() == 'micro':
                    pci_range = self.pci_outer_micro
                    rsi_range = self.rsi_outer_micro
                else:
                    pci_range = self.pci_outer_pico
                    rsi_range = self.rsi_outer_pico
            else:
                pci_range = self.pci_border
                rsi_range = self.rsi_border

            # convert cell lat lng to plane coordinate
            utm_proj = Proj(init="epsg:32647", proj='utm')
            x, y = utm_proj(lng, lat)

            # define cell center
            x_cov = x + r_mod3 * np.sin(direction / 180 * np.pi)
            y_cov = y + r_mod3 * np.cos(direction / 180 * np.pi)
            lng_cov, lat_cov = utm_proj(x_cov, y_cov, inverse=True)

            # calculate distance between cell and the other cells
            lte_cell_info['DISTANCE'] = lte_cell_info.apply(
                lambda col: distance.distance((col['LAT'], col['LNG']), (lat, lng)), axis=1)
            lte_cell_info['DISTANCE'] = lte_cell_info['DISTANCE'].apply(lambda x: x.km)

            # filter only cells within the collision free zone
            lte_cell_filtered_1 = lte_cell_info[lte_cell_info['DISTANCE'] < r_col / 1000]

            # create df for PCI reused
            pci_dict = dict(lte_cell_filtered_1['PCI'].value_counts())

            pci_lst = [pci_dict[x] if x in pci_dict.keys() else 0 for x in pci_range]

            pci_df = pd.DataFrame(pci_lst, index=pci_range)
            pci_df.reset_index(inplace=True)
            pci_df.columns = ['PCI', 'COUNT']
            pci_df['MOD3_GROUP'] = pci_df['PCI'].apply(lambda x: int(x % 3))

            # create df for RSI reused
            rsi_dict = dict(lte_cell_filtered_1[lte_cell_filtered_1['RSI'] % 6 == 0]['RSI'].value_counts())

            rsi_lst = [rsi_dict[x] if x in rsi_dict.keys() else 0 for x in rsi_range]

            rsi_df = pd.DataFrame(rsi_lst, index=rsi_range)
            rsi_df.reset_index(inplace=True)
            rsi_df.columns = ['RSI', 'COUNT']

            skt.sleep(0)
            # INSERT CONDITION FOR A CELL WITH THE SPECIFIED MOD3 GROUP HERE!!!
            if ~pd.isna(cell2plan.iloc[i]['MOD3_GROUP']):
                least_ol_mod3_g = int(cell2plan.iloc[i]['MOD3_GROUP'])
            else:
                # filter only cells within the mod3 conflict zone
                lte_cell_filtered_2 = lte_cell_filtered_1[lte_cell_filtered_1['DISTANCE'] < 3 * r_mod3 / 1000]

                if lte_cell_filtered_2.shape[0] > 0:
                    # calculate cell center to cell center distance
                    lte_cell_filtered_2['X'], lte_cell_filtered_2['Y'] = utm_proj(np.array(lte_cell_filtered_2['LNG']),
                                                                                  np.array(lte_cell_filtered_2['LAT']))
                    lte_cell_filtered_2['DIRECTION'] = lte_cell_filtered_2['DIRECTION'].apply(lambda x: float(x))
                    lte_cell_filtered_2['X_COV'] = lte_cell_filtered_2.apply(
                        lambda col: (col['X'] + r_mod3 * np.sin(col['DIRECTION'] / 180 * np.pi)) if (
                                    col['DIRECTION'] != -1) else col['X'], axis=1)
                    lte_cell_filtered_2['Y_COV'] = lte_cell_filtered_2.apply(
                        lambda col: (col['Y'] + r_mod3 * np.cos(col['DIRECTION'] / 180 * np.pi)) if (
                                    col['DIRECTION'] != -1) else col['Y'], axis=1)
                    lte_cell_filtered_2['LNG_COV'], lte_cell_filtered_2['LAT_COV'] = utm_proj(
                        np.array(lte_cell_filtered_2['X_COV']), np.array(lte_cell_filtered_2['Y_COV']), inverse=True)
                    lte_cell_filtered_2.drop(['X', 'Y', 'X_COV', 'Y_COV'], axis=1, inplace=True)
                    lte_cell_filtered_2['CELL2CELL_DIST'] = lte_cell_filtered_2.apply(
                        lambda col: distance.distance((col['LAT_COV'], col['LNG_COV']), (lat_cov, lng_cov)), axis=1)
                    lte_cell_filtered_2['CELL2CELL_DIST'] = lte_cell_filtered_2['CELL2CELL_DIST'].apply(lambda x: x.km)

                    # calculate the overlapped area of each PCImod3 grp
                    lte_cell_filtered_2['OL_AREA'] = lte_cell_filtered_2.apply(lambda x:self.circle_ol_area(x,r_mod3), axis=1)
                    lte_cell_filtered_2['MOD3_GROUP'] = lte_cell_filtered_2['PCI'].apply(lambda x: int(x % 3))

                    # find the PCI group that fits
                    mod3_g_ol = lte_cell_filtered_2.groupby('MOD3_GROUP').sum()['OL_AREA']
                    ol_arr = np.zeros(3, )
                    for j in range(3):
                        if j in mod3_g_ol.index:
                            ol_arr[j] = mod3_g_ol[j]

                    least_ol_mod3_g = ol_arr.argmin()
                else:
                    least_ol_mod3_g = -1
            skt.sleep(0)
            # find the PCI with min reused and largest nearest reused distance
            if least_ol_mod3_g != -1:
                # in case where threre is overlapped area
                pci_cnt_sorted = np.sort(pci_df[pci_df['MOD3_GROUP'] == least_ol_mod3_g]['COUNT'].unique())
                for j in range(len(pci_cnt_sorted)):
                    pci_min_reused = pci_cnt_sorted[j]
                    potential_pci = pci_df[
                        (pci_df['MOD3_GROUP'] == least_ol_mod3_g) & (pci_df['COUNT'] == pci_min_reused)]
                    if pci_min_reused == 0:
                        chosen_pci = potential_pci['PCI'].min()
                        best_nearest_pci_dist = r_col / 1000
                        break
                    else:
                        pci_nearest_dist = []
                        for index, row in potential_pci.iterrows():
                            pci_nearest_dist.append(
                                lte_cell_filtered_1[lte_cell_filtered_1['PCI'] == row['PCI']]['DISTANCE'].min())

                        potential_pci['NEAREST_DIST'] = pci_nearest_dist
                        best_nearest_pci_dist = potential_pci['NEAREST_DIST'].max()
                        if best_nearest_pci_dist > dist_min / 1000:
                            chosen_pci = potential_pci[potential_pci['NEAREST_DIST'] == best_nearest_pci_dist]['PCI']
                            break
                        else:
                            continue
                else:
                    chosen_pci = np.int64(999)
            else:
                # in case where there is no overlapped area
                pci_cnt_sorted = np.sort(pci_df['COUNT'].unique())
                for j in range(len(pci_cnt_sorted)):
                    pci_min_reused = pci_cnt_sorted[j]
                    potential_pci = pci_df[pci_df['COUNT'] == pci_min_reused]
                    if pci_min_reused == 0:
                        chosen_pci = potential_pci['PCI'].min()
                        best_nearest_pci_dist = r_col / 1000
                        break
                    else:

                        pci_nearest_dist = []
                        for index, row in potential_pci.iterrows():
                            pci_nearest_dist.append(
                                lte_cell_filtered_1[lte_cell_filtered_1['PCI'] == row['PCI']]['DISTANCE'].min())

                        potential_pci['NEAREST_DIST'] = pci_nearest_dist
                        best_nearest_pci_dist = potential_pci['NEAREST_DIST'].max()
                        if best_nearest_pci_dist > dist_min / 1000:
                            chosen_pci = potential_pci[potential_pci['NEAREST_DIST'] == best_nearest_pci_dist]['PCI']
                            break
                        else:
                            continue
                else:
                    chosen_pci = np.int64(999)
            skt.sleep(0)
            if isinstance(chosen_pci, np.int64):
                cell2plan['PCI'].iloc[i] = chosen_pci
            else:
                cell2plan['PCI'].iloc[i] = chosen_pci.iloc[0]

            cell2plan['COPCI_NEAREST_DIST'].iloc[i] = best_nearest_pci_dist

            # find the RSI with min reused and largest nearest reused distance
            rsi_cnt_sorted = np.sort(rsi_df['COUNT'].unique())
            for j in range(len(rsi_cnt_sorted)):

                rsi_min_reused = rsi_cnt_sorted[j]
                potential_rsi = rsi_df[rsi_df['COUNT'] == rsi_min_reused]
                if rsi_min_reused == 0:
                    chosen_rsi = potential_rsi['RSI'].min()
                    best_nearest_rsi_dist = r_col / 1000
                    break
                else:
                    rsi_nearest_dist = []
                    for index, row in potential_rsi.iterrows():
                        rsi_nearest_dist.append(
                            lte_cell_filtered_1[lte_cell_filtered_1['RSI'] == row['RSI']]['DISTANCE'].min())
                    potential_rsi['NEAREST_DIST'] = rsi_nearest_dist
                    best_nearest_rsi_dist = potential_rsi['NEAREST_DIST'].max()
                    if best_nearest_rsi_dist > dist_min / 1000:
                        chosen_rsi = potential_rsi[potential_rsi['NEAREST_DIST'] == best_nearest_rsi_dist]['RSI']
                        break
                    else:
                        continue
            else:
                chosen_rsi = np.int64(999)

            if isinstance(chosen_rsi, np.int64):
                cell2plan['RSI'].iloc[i] = chosen_rsi
            else:
                cell2plan['RSI'].iloc[i] = chosen_rsi.iloc[0]

            cell2plan['CORSI_NEAREST_DIST'].iloc[i] = best_nearest_rsi_dist

            # drop DISTANCE col from cell info df
            lte_cell_info.drop('DISTANCE', axis=1, inplace=True)

            # write each planned cell to cell info
            lte_cell_info = lte_cell_info.append(cell2plan.iloc[i], ignore_index=True)
            # skt.emit('progress', {'message': f'({i+1}/{cell2plan.shape[0]}) planned'}, namespace='/plan_4g')

        cell2plan['PLAN_DATE'] = pd.datetime.today().date()


        return cell2plan