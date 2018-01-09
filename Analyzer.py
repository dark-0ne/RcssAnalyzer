import pandas as pd
import numpy as np
import xml.etree.cElementTree as Et
import math


class Analyzer:
    def __init__(self):
        self.logPath = ''
        self.xmlPath = ''
        self.cycles = pd.DataFrame(columns=["Left", "Right", "Ball", "Kick"], index=np.arange(6000))
        self.teams = {}

    @staticmethod
    def dist(x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2+(y1-y2)**2)

    def find_player_in_possess(self, cycle):
        if cycle == 3000:
            return 0
        current_cycle = self.cycles.iloc[cycle - 1].copy()
        dist_left = np.array([])
        dist_right = np.array([])
        for player in current_cycle['Left']:
            tmp = np.array([self.dist(float(player['PosX']), float(player['PosY']), float(current_cycle['Ball']['PosX'])
                                      , float(current_cycle['Ball']['PosY']))])

            dist_left = np.concatenate((dist_left, tmp))
        for player in current_cycle['Right']:
            tmp = np.array([self.dist(float(player['PosX']), float(player['PosY']), float(current_cycle['Ball']['PosX'])
                                      , float(current_cycle['Ball']['PosY']))])
            dist_right = np.concatenate((dist_right, tmp))

        min_left = np.amin(dist_left)
        min_right = np.amin(dist_right)

        if math.fabs(min_left-min_right) < 0.3:
            # print('Cycle {} no one is in possession'.format(cycle))
            return 0
        elif min_left < min_right and min_left < 6:
            # print('Cycle {} closest player is Left {} with distance = {}'
            # .format(cycle, np.argmin(dist_left)+1, min_left))
            return np.argmin(dist_left)+1
        elif min_left > min_right and min_right < 6:
            # print('Cycle {} closest player is Right {} with distance = {}'
            # .format(cycle, np.argmin(dist_right)+12, min_right))
            return -(np.argmin(dist_right)+1)
        else:
            # print('Cycle {} no one is in possession'.format(cycle))
            return 0

    def extract_rcg_file(self):
        tree = Et.parse(self.xmlPath)
        root = tree.getroot()
        for node in root:
            if node.tag == 'Team':
                if node.attrib['Side'] == 'Left':
                    self.teams['Left'] = {'Name': node.attrib['Name'], 'Score': int(node.attrib['Goals'])}
                else:
                    self.teams['Right'] = {'Name': node.attrib['Name'], 'Score': int(node.attrib['Goals'])}

            elif node.tag == 'Cycle':
                current_cycle = self.cycles.iloc[int(node.attrib['Number']) - 1]
                current_cycle['Left'] = []
                current_cycle['Right'] = []

                for movable in node:
                    if movable.tag == 'Ball':
                        current_cycle['Ball'] = movable.attrib
                    elif movable.tag == 'Player':
                        if movable.attrib['Side'] == 'Left':
                            current_cycle['Left'].append(movable.attrib)
                        else:
                            current_cycle['Right'].append(movable.attrib)

    def extract_log_file(self):
        file = open(self.logPath, 'r')
        left_name = self.teams['Left']['Name']

        for line in file:
            if line.find('(kick ') != -1:
                splited = line.split()
                cycle = int(splited[0].split(',')[0])
                if splited[2].split('_')[0] == left_name:
                    player = {'Side': 'Left', 'Unum': int(splited[2].split('_')[1][:-1])}
                else:
                    player = {'Side': 'Right', 'Unum': int(splited[2].split('_')[1][:-1])}
                kick = {'Power': float(splited[4]), 'Angle': float(splited[5].split(')(')[0])}

                current_cycle = self.cycles.iloc[cycle-1]

                current_cycle['Kick'] = player
                current_cycle['Kick'].update(kick)

                # print(current_cycle['Kick'])

    def analyze_possession(self):
        left_possess_count = 0
        right_possess_count = 0

        possess_series = pd.Series(np.arange(6000))

        for i in range(6000):
            closest_player = self.find_player_in_possess(i + 1)
            possess_series[i] = closest_player
            if closest_player > 0:
                left_possess_count += 1
            elif closest_player < 0:
                right_possess_count += 1

        self.cycles = self.cycles.assign(Owner=possess_series)
        # print('Left Possession is {} and Right Possession is {}'.format(left_possess_count, right_possess_count))

        return left_possess_count, right_possess_count

    def analyze_stamina(self):
        total_left = 0
        total_right = 0

        for idx, row in self.cycles.iterrows():
            if type(row['Left']) == list:
                for player in row['Left']:
                    total_left += float(player['Stamina'])
                for player in row['Right']:
                    total_right += float(player['Stamina'])

        # print('Left Stamina is {} and Right Stamina is {}'.format(total_left,total_right))
        return total_left/65989, total_right/65989

    def analyze_kicks(self):
        previous_owner = 0

        left_complete_passes = 0
        right_complete_passes = 0

        left_wrong_passes = 0
        right_wrong_passes = 0

        left_wrong_shoots = 0
        right_wrong_shoots = 0

        for idx, row in self.cycles.iterrows():
            current_owner = row['Owner']
            if current_owner != previous_owner and current_owner != 0:
                for cycle in range(idx-1, idx-26, -1):
                    check_cycle = self.cycles.iloc[cycle]
                    if type(check_cycle['Kick']) == dict:
                        check_player = check_cycle['Kick']['Unum']
                        if check_cycle['Kick']['Side'] == 'Right':
                            check_player = -check_player
                        if check_player == previous_owner:
                            # print('Pass detected!')
                            if current_owner * previous_owner < 0:
                                if previous_owner > 0:
                                    if math.fabs(current_owner) == 1:
                                        # print("Wrong Shoot For Left at cycle {}".format(cycle))
                                        left_wrong_shoots += 1
                                    else:
                                        # print("Wrong Pass For Left")
                                        left_wrong_passes += 1
                                elif previous_owner < 0:
                                    if math.fabs(current_owner) == 1:
                                        # print("Wrong Shoot For Right at cycle {}".format(cycle))
                                        right_wrong_shoots += 1
                                    else:
                                        # print("Wrong Pass For Right")
                                        right_wrong_passes += 1
                            elif current_owner * previous_owner > 0:
                                if previous_owner > 0:
                                    # print("Complete Pass For Left")
                                    left_complete_passes += 1
                                elif previous_owner < 0:
                                    # print("Complete Pass For Right")
                                    right_complete_passes += 1
                            break
                previous_owner = current_owner

        # print('Left complete passes count is {} and wrong passes count is {}'
        # .format(left_complete_passes, left_wrong_passes))
        # print('Right complete passes count is {} and wrong passes count is {}'
        # .format(right_complete_passes, right_wrong_passes))

        return left_complete_passes, left_wrong_passes, right_complete_passes, right_wrong_passes, left_wrong_shoots,\
            right_wrong_shoots


if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.xmlPath = 'testGameFile.xml'
    analyzer.logPath = 'testLogFile.rcl'
    analyzer.extract_rcg_file()
    analyzer.extract_log_file()
    analyzer.analyze_possession()
    analyzer.analyze_kicks()
