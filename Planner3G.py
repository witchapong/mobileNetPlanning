# import fiona
# from shapely.geometry import Point
# from shapely.geometry import shape
# from geopy import distance
import pandas as pd
import numpy as np


class PSCPlanner:
    # poly = fiona.open(f"src/Border_BKK_rv3_region.shp")
    # poly_obj = [shape(item['geometry']) for item in poly]

    # define psc for border cells
    psc_border_macro = [x * 8 + 4 for x in range(0, 33)] + [x * 8 + 5 for x in range(0, 33)] + [x * 8 + 6 for x in
                                                                                                range(0, 33)]
    psc_border_micro = [x * 8 + 268 for x in range(0, 15)] + [x * 8 + 269 for x in range(0, 15)] + [x * 8 + 270 for x in
                                                                                                    range(0, 15)]
    psc_border_pico = [x * 8 + 388 for x in range(0, 16)] + [x * 8 + 389 for x in range(0, 16)] + [x * 8 + 390 for x in
                                                                                                   range(0, 16)]

    # define psc for inner+outer cells
    psc_macro = list(range(1, 264))
    psc_micro = list(range(264, 384))
    psc_pico = list(range(384, 512))

    def __init__(self, file):
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

    def plan(self, r_col, min_dist):

        cell_info = self.plan_file.copy()

        # convert all border labels to lower case
        # cell_info['AREA_TYPE'] = cell_info.apply(lambda x:self.map2poly(x,cell_info), axis=1)
        cell_info['AREA_TYPE'] = cell_info['AREA_TYPE'].fillna("border")
        cell_info['AREA_TYPE'] = cell_info['AREA_TYPE'].apply(lambda x: x.lower())

        # assign current cell and cell to plan to different dfs
        u2100_cell_info = cell_info[cell_info['PSC'] != -1]
        cell2plan = cell_info[cell_info['PSC'] == -1]

        # drop null lat,lng for current cell info
        u2100_cell_info = u2100_cell_info[np.isfinite(u2100_cell_info['LAT'])]  # filter numeric lat,lng

        planned_pscs = []
        for i in range(0, cell2plan.shape[0]):

            # register lat lng of cell to plan
            lat = cell2plan.iloc[i]['LAT']
            lng = cell2plan.iloc[i]['LNG']

            # determine psc range for each cell type
            if cell2plan.iloc[i]['AREA_TYPE'] == 'border':
                if cell2plan.iloc[i]['SITE_TYPE'] == 'Macro':
                    psc_range = self.psc_border_macro
                elif cell2plan.iloc[i]['SITE_TYPE'] == 'Micro':
                    psc_range = self.psc_border_micro
                else:
                    psc_range = self.psc_border_pico
            else:
                if cell2plan.iloc[i]['SITE_TYPE'] == 'Macro':
                    psc_range = self.psc_macro
                elif cell2plan.iloc[i]['SITE_TYPE'] == 'Micro':
                    psc_range = self.psc_micro
                else:
                    psc_range = self.psc_pico

            # calculate distance between cell and the other cells
            from geopy import distance

            u2100_cell_info['DISTANCE'] = u2100_cell_info.apply(
                lambda col: distance.distance((col['LAT'], col['LNG']), (lat, lng)), axis=1)
            u2100_cell_info['DISTANCE'] = u2100_cell_info['DISTANCE'].apply(lambda x: x.km)

            # filter only cells within the collision free zone
            u2100_cell_filtered_1 = u2100_cell_info[u2100_cell_info['DISTANCE'] < r_col / 1000]

            # create df for PSC reused
            psc_dict = dict(u2100_cell_filtered_1['PSC'].value_counts())

            psc_lst = [psc_dict[x] if x in psc_dict.keys() else 0 for x in psc_range]

            psc_df = pd.DataFrame(psc_lst, index=psc_range)
            psc_df.reset_index(inplace=True)
            psc_df.columns = ['PSC', 'COUNT']

            # fixed method to avoid PSC with min count but 0 distance !!!

            psc_cnt_sorted = np.sort(psc_df['COUNT'].unique())
            for j in range(len(psc_cnt_sorted)):

                psc_min_reused = psc_cnt_sorted[j]
                potential_psc = psc_df[psc_df['COUNT'] == psc_min_reused]
                if psc_min_reused == 0:

                    chosen_psc = potential_psc['PSC'].min()
                    best_nearest_psc_dist = r_col / 1000
                    break
                else:

                    psc_nearest_dist = []
                    for index, row in potential_psc.iterrows():
                        psc_nearest_dist.append(
                            u2100_cell_filtered_1[u2100_cell_filtered_1['PSC'] == row['PSC']]['DISTANCE'].min())

                    potential_psc['NEAREST_DIST'] = psc_nearest_dist
                    best_nearest_psc_dist = potential_psc['NEAREST_DIST'].max()
                    if best_nearest_psc_dist > min_dist / 1000:
                        chosen_psc = potential_psc[potential_psc['NEAREST_DIST'] == best_nearest_psc_dist]['PSC']
                        break
                    else:
                        continue
            else:
                chosen_psc = np.int64(999)

            # find the PSC with min reused and largest nearest reused distance

            if isinstance(chosen_psc, np.int64):
                planned_pscs.append(chosen_psc)
                cell2plan['PSC'].iloc[i] = chosen_psc
            else:
                planned_pscs.append(chosen_psc.iloc[0])
                cell2plan['PSC'].iloc[i] = chosen_psc.iloc[0]

            cell2plan['COPSC_NEAREST_DIST'] = best_nearest_psc_dist

            # write each planned cell to cell info
            u2100_cell_info = u2100_cell_info.append(cell2plan.iloc[i], ignore_index=True)

        cell2plan['PLAN_DATE'] = pd.datetime.today().date()

        return cell2plan
