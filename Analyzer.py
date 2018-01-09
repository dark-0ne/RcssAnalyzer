import pandas as pd
import numpy as np
import xml.etree.ElementTree as et
import math

class Analyzer:
    def __init__(self):
        self.rcgPath = None
        self.cycles = None
        self.teams = {}

    def set_rcg_file(self, path):
        self.rcgPath = path

    def dist(self,x1,y1,x2,y2):
        return math.sqrt((x1-x2)**2+(y1-y2)**2)

    def find_player_in_possess(self, cycle):
        if cycle == 3000:
            return 0
        current_cycle = self.cycles.iloc[cycle - 1].copy()
        dist_left = np.array([])
        dist_right = np.array([])
        for player in current_cycle['Left']:
            tmp = np.array([self.dist(float(player['PosX']), float(player['PosY']), float(current_cycle['Ball']['PosX']),
                                     float(current_cycle['Ball']['PosY']))])

            dist_left = np.concatenate((dist_left, tmp))
        for player in current_cycle['Right']:
            tmp = np.array([self.dist(float(player['PosX']), float(player['PosY']), float(current_cycle['Ball']['PosX']),
                                     float(current_cycle['Ball']['PosY']))])
            dist_right = np.concatenate((dist_right, tmp))

        min_left = np.amin(dist_left)
        min_right = np.amin(dist_right)


        if math.fabs(min_left-min_right)<0.3:
            # print('Cycle {} no one is in possession'.format(cycle))
            return 0
        elif min_left < min_right and min_left < 6 :
            # print('Cycle {} closest player is Left {} with distance = {}'.format(cycle, np.argmin(dist_left)+1, min_left))
            return np.argmin(dist_left)+1
        elif min_left > min_right and min_right < 6:
            # print('Cycle {} closest player is Right {} with distance = {}'.format(cycle, np.argmin(dist_right)+12, min_right))
            return np.argmin(dist_right)+12
        else:
            # print('Cycle {} no one is in possession'.format(cycle))
            return 0

    def extract_rcg_file(self):
        self.cycles = pd.DataFrame(columns=["Left", "Right", "Ball"], index=np.arange(6000))
        tree = et.parse(self.rcgPath)
        root = tree.getroot()
        for node in root:
            if node.tag == 'Team':
                if node.attrib['Side'] == 'Left':
                    self.teams['Left'] = {'Name':node.attrib['Name'], 'Score':int(node.attrib['Goals'])}
                else:
                    self.teams['Right'] = {'Name':node.attrib['Name'],'Score':int(node.attrib['Goals'])}

            elif node.tag == 'Cycle':
                self.cycles.iloc[int(node.attrib['Number']) - 1]['Left'] = []
                self.cycles.iloc[int(node.attrib['Number']) - 1]['Right'] = []
                current_cycle = self.cycles.iloc[int(node.attrib['Number']) - 1]
                for movable in node:
                    if movable.tag == 'Ball':
                        current_cycle['Ball'] = movable.attrib
                    elif movable.tag == 'Player':
                        if movable.attrib['Side'] == 'Left':
                            current_cycle['Left'].append(movable.attrib)
                        else:
                            current_cycle['Right'].append(movable.attrib)

    def analyze_possession(self):
        left_possess_count = 0
        right_possess_count = 0

        possess_series = pd.Series(np.arange(6000))

        for i in range(6000):
            closest_player = self.find_player_in_possess(i + 1)
            possess_series[i] = closest_player
            if closest_player < 12 and closest_player != 0:
                left_possess_count += 1
            elif closest_player > 11 and closest_player != 0:
                right_possess_count += 1

        self.cycles = self.cycles.assign(Owner=possess_series)
        # print('Left Possession is {} and Right Possession is {}'.format(left_possess_count, right_possess_count))

        return left_possess_count, right_possess_count

    def analyze_stamina(self):
        totalLeft = 0
        totalRight = 0

        for idx, row in self.cycles.iterrows():
            if type(row['Left']) == list:
                for player in row['Left']:
                    totalLeft += float(player['Stamina'])
                for player in row['Right']:
                    totalRight += float(player['Stamina'])


        # print('Left Stamina is {} and Right Stamina is {}'.format(totalLeft,totalRight))
        return totalLeft/65989, totalRight/65989
    def analyze_passess(self):
        previous_owner = 0
        for idx, row in self.cycles.iterrows():
            current_owner = row['Owner']
            if current_owner != previous_owner:
                print("Owner Changed!")
                if math.fabs(current_owner-previous_owner) > 10:
                    print("Team Also Changed!")
            previous_owner = current_owner
if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.set_rcg_file('gamefile.xml')
    analyzer.extract_rcg_file()
    analyzer.analyze_possession()
    analyzer.analyze_passess()