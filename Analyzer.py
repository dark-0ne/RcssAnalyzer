import pandas as pd
import numpy as np
import xml.etree.cElementTree as Et
import math
import logging
import shapely
from shapely.geometry import LineString
from shapely.geometry import Point

class Analyzer:
    def __init__(self):
        self.logPath = ''
        self.xmlPath = ''
        self.cycles = pd.DataFrame(columns=["Left", "Right", "Ball", "Kick", "Tackle"], index=np.arange(6000))
        self.teams = {}

    @staticmethod
    def dist(x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2+(y1-y2)**2)

    def find_player_in_possess(self, cycle):
        try:
            current_cycle = self.cycles.iloc[cycle - 1].copy()
            dist_left = np.array([])
            dist_right = np.array([])
            cur_ball = current_cycle['Ball']

            ball_fac = self.dist(float(cur_ball['VelX']), float(cur_ball['VelX']), 0,0)
            ball_fac += 1
            ball_fac = 1/ball_fac
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

            if min_left < min_right and min_left < (1.1 + ball_fac):
                logging.debug('Cycle {} closest player is Left {} with distance = {}'
                .format(cycle, np.argmin(dist_left)+1, min_left))
                return np.argmin(dist_left)+1
            elif min_left > min_right and min_right < (1.1 + ball_fac):
                logging.debug('Cycle {} closest player is Right {} with distance = {}'
                .format(cycle, np.argmin(dist_right)+12, min_right))
                return -(np.argmin(dist_right)+1)
            else:
                logging.debug('Cycle {} no one is in possession'.format(cycle))
                return 0

        except TypeError:
            return 0

    def extract_rcg_file(self):
        tree = Et.parse(self.xmlPath)
        root = tree.getroot()
        for node in root:
            if node.tag == 'Team':
                if node.attrib['Side'] == 'Left':
                    self.teams['Left'] = {'Name': node.attrib['Name'], 'Score': int(node.attrib['Score']), 'Goals': []}
                    for goal in node:
                        self.teams['Left']['Goals'].append({'Cycle': int(goal.text)})
                else:
                    self.teams['Right'] = {'Name': node.attrib['Name'], 'Score': int(node.attrib['Score']), 'Goals': []}
                    for goal in node:
                        self.teams['Right']['Goals'].append({'Cycle': int(goal.text)})

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
        start_cycle = self.cycles.iloc[30]
        for i in range(10):
            if -52 < float(start_cycle['Left'][i]['PosX']) < - 36 and -20 < float(start_cycle['Left'][i]['PosY']) < 20:
                self.teams['Left'].update({'Goalkeeper': i+1})
                break
        for i in range(10):
            if 36 < float(start_cycle['Right'][i]['PosX']) < 52 and -20 < float(start_cycle['Right'][i]['PosY']) < 20:
                self.teams['Right'].update({'Goalkeeper': i+1})
                break
        logging.debug(self.teams)



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

                logging.debug(current_cycle['Kick'])
            elif line.find('(tackle ') != -1:
                splited = line.split()
                cycle = int(splited[0].split(',')[0])
                if splited[2].split('_')[0] == left_name:
                    player = {'Side': 'Left', 'Unum': int(splited[2].split('_')[1][:-1])}
                else:
                    player = {'Side': 'Right', 'Unum': int(splited[2].split('_')[1][:-1])}
                current_cycle = self.cycles.iloc[cycle - 1]
                current_cycle['Tackle'] = player
                logging.debug(current_cycle['Tackle'])


    def analyze_possession(self):
        left_possess_count = 0
        right_possess_count = 0

        two_cycles_ago = 0
        one_cycle_ago = 0

        possess_series = pd.Series(np.arange(6000))

        for i in range(6000):
            possess_series[i] = 0
            had_kick = False
            if i > 10:
                for cycle_to_check in (reversed(range(i-3, i+1))):
                    kick = self.cycles.iloc[cycle_to_check]['Kick']

                    try:
                        if kick['Side'] == 'Left':
                            possess_series[i] = kick['Unum']
                        else:
                            possess_series[i] = -kick['Unum']
                        had_kick = True
                        break
                    except (AttributeError, TypeError):
                        continue
                if had_kick is False:
                    possess_series[i] = self.find_player_in_possess(i + 1)
            if possess_series[i] > 0:
                left_possess_count += 1
            elif possess_series[i] < 0:
                right_possess_count += 1
            logging.debug("Cycle {}: {} is in possession.".format(i, possess_series[i]))

        self.cycles = self.cycles.assign(Owner=possess_series)
        logging.debug('Left Possession is {} and Right Possession is {}'.format(left_possess_count, right_possess_count))

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

        logging.debug('Left Stamina is {} and Right Stamina is {}'.format(total_left,total_right))
        return total_left/65989, total_right/65989

    def analyze_kicks(self):
        previous_owner = 0

        left_complete_passes = 0
        right_complete_passes = 0

        left_wrong_passes = 0
        right_wrong_passes = 0

        left_correct_shoots = 0
        right_correct_shoots = 0

        left_wrong_shoots = 0
        right_wrong_shoots = 0

        left_pass_pos = []
        right_pass_pos = []

        left_saves = 0
        right_saves = 0

        for idx, row in self.cycles[self.cycles['Kick'].notnull()].iterrows():
            try:
                self_pass = False
                kick = row['Kick']
                for i in range(idx + 1, min(idx + 30, 5999)):
                    next_kick = self.cycles.iloc[i]['Kick']
                    if type(next_kick) == dict:
                        if next_kick['Side'] == kick['Side'] and next_kick['Unum'] == kick['Unum']:
                            logging.debug('Self pass detected at {}!'.format(idx))
                            self_pass = True
                        break
                if not self_pass:
                    logging.debug('Cycle {} {}'.format(idx+1, kick))
                    current_owner = kick['Unum']
                    if kick['Side'] == 'Right':
                        current_owner *= -1
                    next_owner = 0
                    target_cycle = 0
                    for i in range(idx+1, min(idx+150, 5999)):
                        temp_owner = self.cycles.iloc[i]['Owner']
                        if temp_owner != 0 and temp_owner != current_owner:
                            next_owner = temp_owner
                            logging.debug('Change of possession at {} from {} to {}!'.format(i + 1, current_owner, next_owner))
                            target_cycle = i
                            break

                    if next_owner * current_owner < 0:

                        # Checking for shoots
                        goal_scored = False
                        if current_owner > 0:   # Left Player
                            player_pos = (
                                float(row['Left'][current_owner - 1]['PosX']),
                                float(row['Left'][current_owner - 1]['PosY']))

                            logging.debug('Player left {} position is {}'.format(current_owner, player_pos))

                            ball_pos = (float(self.cycles.iloc[idx]['Ball']['PosX']),
                                        float(self.cycles.iloc[idx]['Ball']['PosY']))
                            next_pos = (ball_pos[0] + 16 * float(self.cycles.iloc[idx + 1]['Ball']['VelX']),
                                        ball_pos[1] + 16 * float(self.cycles.iloc[idx + 1]['Ball']['VelY']))
                            kick_projection = LineString([ball_pos, next_pos])
                            goal_line = LineString([(52.5, 7), (52.5, -7)])

                            inter = goal_line.intersection(kick_projection)
                            if not inter.is_empty:
                                logging.warning('Left correct shoot at: {}'.format(idx))
                                left_correct_shoots += 1
                                for goal in self.teams['Left']['Goals']:
                                    if goal['Cycle']-idx < 30:
                                        goal_scored = True
                                        break
                                if not goal_scored and math.fabs(next_owner) == self.teams['Right']['Goalkeeper']:
                                    logging.warning('Right keeper save at:{}'.format(idx))
                                    right_saves +=1

                                continue
                            else:
                                goal_line = LineString([(52.5, 11), (52.5, -11)])

                                inter = goal_line.intersection(kick_projection)
                                if not inter.is_empty:
                                    logging.warning('Left wrong shoot at: {}'.format(idx))
                                    left_wrong_shoots += 1
                                    continue
                            if type(row['Tackle']) == float:
                                left_wrong_passes += 1
                                logging.warning('Wrong left pass at {}'.format(idx))
                            continue

                        else:   # Right Player
                            player_pos = (
                                float(row['Right'][-current_owner - 1]['PosX']),
                                float(row['Right'][-current_owner - 1]['PosY']))

                            logging.debug('Player right {} position is {}'.format(current_owner, player_pos))

                            ball_pos = (float(self.cycles.iloc[idx]['Ball']['PosX']),
                                        float(self.cycles.iloc[idx]['Ball']['PosY']))
                            next_pos = (ball_pos[0] + 16 * float(self.cycles.iloc[idx + 1]['Ball']['VelX']),
                                        ball_pos[1] + 16 * float(self.cycles.iloc[idx + 1]['Ball']['VelY']))
                            kick_projection = LineString([ball_pos, next_pos])
                            goal_line = LineString([(-52.5, 7), (-52.5, -7)])

                            inter = goal_line.intersection(kick_projection)
                            if not inter.is_empty:
                                logging.warning('Right correct shoot at: {}'.format(idx))
                                for goal in self.teams['Right']['Goals']:
                                    if goal['Cycle']-idx < 30:
                                        goal_scored = True
                                        break
                                if not goal_scored and math.fabs(next_owner) == self.teams['Left']['Goalkeeper']:
                                    logging.warning('Left keeper save at:{}'.format(idx))
                                    left_saves +=1
                                continue
                            else:
                                goal_line = LineString([(-52.5, 11), (-52.5, -11)])

                                inter = goal_line.intersection(kick_projection)
                                if not inter.is_empty:
                                    logging.warning('Right wrong shoot at: {}'.format(idx))
                                    right_wrong_shoots += 1
                                    continue
                            if type(row['Tackle']) == float:
                                right_wrong_passes += 1
                                logging.warning('Right wrong pass at {}'.format(idx))
                            continue

                    elif next_owner * current_owner > 0:
                        # Checking for passes

                        if current_owner > 0:  # Left Player
                            player_pos = (
                                float(row['Left'][current_owner - 1]['PosX']),
                                float(row['Left'][current_owner - 1]['PosY']))

                            logging.debug('Player left {} position is {}'.format(current_owner, player_pos))

                            target_pos = (float(self.cycles.iloc[target_cycle]['Left'][next_owner - 1]['PosX']),
                                          float(self.cycles.iloc[target_cycle]['Left'][next_owner - 1]['PosY']))

                            logging.debug(
                                'Target position is {}.'.format(target_pos))
                            target_circle = Point(target_pos).buffer(2.5).boundary
                            ball_pos = (float(self.cycles.iloc[idx]['Ball']['PosX']),
                                        float(self.cycles.iloc[idx]['Ball']['PosY']))
                            next_pos = (ball_pos[0] + 12 * float(self.cycles.iloc[idx + 1]['Ball']['VelX']),
                                        ball_pos[1] + 12 * float(self.cycles.iloc[idx + 1]['Ball']['VelY']))
                            kick_projection = LineString([ball_pos, next_pos])
                            logging.debug("Next pos is {}".format(next_pos))

                            inter = target_circle.intersection(kick_projection)
                            if not inter.is_empty:
                                logging.warning('Left correct pass at: {}'.format(idx))
                                left_complete_passes += 1
                                left_pass_pos.append((player_pos,target_pos))
                                continue
                            else:
                                logging.warning('Anomaly at {}'.format(idx))
                                continue

                        else:  # Right Player
                                player_pos = (
                                    float(row['Right'][-current_owner - 1]['PosX']),
                                    float(row['Right'][-current_owner - 1]['PosY']))

                                # print(kick_projection)
                                logging.debug('Player right {} position is {}'.format(current_owner, player_pos))

                                target_pos = (float(self.cycles.iloc[target_cycle]['Right'][-next_owner - 1]['PosX']),
                                              float(self.cycles.iloc[target_cycle]['Right'][-next_owner - 1]['PosY']))

                                logging.debug(
                                    'Target position is {}.'.format(target_pos))
                                target_circle = Point(target_pos).buffer(2.5).boundary
                                ball_pos = (float(self.cycles.iloc[idx]['Ball']['PosX']),
                                            float(self.cycles.iloc[idx]['Ball']['PosY']))
                                next_pos = (ball_pos[0] + 12 * float(self.cycles.iloc[idx + 1]['Ball']['VelX']),
                                            ball_pos[1] + 12 * float(self.cycles.iloc[idx + 1]['Ball']['VelY']))
                                kick_projection = LineString([ball_pos, next_pos])
                                logging.debug("Next pos is {}".format(next_pos))

                                inter = target_circle.intersection(kick_projection)
                                if not inter.is_empty:
                                    logging.warning('Right correct pass at: {}'.format(idx))
                                    right_complete_passes += 1
                                    right_pass_pos.append((player_pos,target_pos))
                                    continue
                                else:
                                    logging.warning('Anomaly at {}'.format(idx))
                                continue
            except TypeError:
                continue
        logging.debug('Left complete passes count is {} and wrong passes count is {}'
            .format(left_complete_passes, left_wrong_passes))
        logging.debug('Right complete passes count is {} and wrong passes count is {}'
            .format(right_complete_passes, right_wrong_passes))

        logging.debug('Left correct shoot count is {} and wrong shoot count is {}'
                        .format(left_correct_shoots, left_wrong_shoots))
        logging.debug('Right correct shoot count is {} and wrong shoot count is {}'
                        .format(right_correct_shoots, right_wrong_shoots))

        logging.debug('Left saves are {} and right saves are {}'.format(left_saves, right_saves))

        return left_complete_passes, left_wrong_passes, right_complete_passes, right_wrong_passes, left_correct_shoots,\
               left_wrong_shoots, right_correct_shoots, right_wrong_shoots, left_pass_pos, right_pass_pos, left_saves,\
               right_saves

    def analyze_opportunities_and_clearances(self):

        left_opps = 0
        right_opps = 0

        left_clearance = 0
        right_clearance = 0

        current_opp = 0

        for idx, row in self.cycles.iterrows():
            try:
                ball_pos_x = float(row['Ball']['PosX'])
                ball_pos_y = float(row['Ball']['PosY'])
                owner = row['Owner']
            except TypeError:
                continue
            if current_opp == 0:
                if owner > 0 and ball_pos_x < 52 and ball_pos_x > 32 and math.fabs(ball_pos_y) < 20:
                    current_opp = 1
                    left_opps += 1
                    logging.debug('Cycle {}: Left gained opportunity!'.format(idx))

                elif owner < 0 and ball_pos_x > -52 and ball_pos_x < -32 and math.fabs(ball_pos_y) < 20:
                    current_opp = -1
                    right_opps += 1
                    logging.debug('Cycle {}: Right gained opportunity!'.format(idx))
            elif current_opp * row['Owner'] < 0:
                current_opp = 0
                logging.debug("Cycle {}: Opportunity Over!".format(idx))

                if owner > 1:       # Left Defender
                    player_pos_x = float(row['Left'][owner - 1]['PosX'])
                    player_pos_y = float(row['Left'][owner - 1]['PosY'])
                    if (player_pos_x > -52 and player_pos_x < -32 and math.fabs(player_pos_y) < 20
                            and math.fabs(ball_pos_x) != 47 and math.fabs(ball_pos_y) != 9.16):      # Left Clearance
                        logging.debug('Left recovered at cycle {}'.format(idx))
                        left_clearance += 1

                if owner < -1:       # Right Defender
                    player_pos_x = float(row['Right'][int(math.fabs(owner)) - 1]['PosX'])
                    player_pos_y = float(row['Right'][int(math.fabs(owner)) - 1]['PosY'])
                    if (player_pos_x < 52 and player_pos_x > 32 and math.fabs(player_pos_y) < 20
                            and math.fabs(ball_pos_x) != 47 and math.fabs(ball_pos_y) != 9.16):      # Right Clearance
                        logging.debug('Right recovered at cycle {}'.format(idx))
                        right_clearance += 1

        return left_opps, right_opps, left_clearance, right_clearance


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    analyzer = Analyzer()
    analyzer.xmlPath = 'testGameFile.xml'
    analyzer.logPath = 'testLogFile.rcl'
    analyzer.extract_rcg_file()
    analyzer.extract_log_file()
    analyzer.analyze_possession()
    analyzer.analyze_kicks()
    # analyzer.analyze_opportunities_and_clearances()

