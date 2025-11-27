import json
import random
from typing import List, Optional, Tuple

from controller import Supervisor

from referee.consts import (
    BALL_INITIAL_TRANSLATION,
    KICKOFF_TRANSLATION,
    LACK_OF_PROGRESS_NUMBER_OF_NEUTRAL_SPOTS,
    MAX_EVENT_MESSAGES_IN_QUEUE,
    ROBOT_INITIAL_ROTATION,
    ROBOT_INITIAL_TRANSLATION,
    ROBOT_NAMES,
    TIME_STEP,
)
from referee.enums import GameEvents, NeutralSpotDistanceType, Team
from referee.event_handlers import EventHandler
from referee.eventer import Eventer
from referee.penalty_area_checker import PenaltyAreaChecker
from referee.progress_checker import ProgressChecker
from referee.utils import (
    is_in_blue_goal,
    is_in_yellow_goal,
    is_outside,
    time_to_string,
)


class RCJSoccerReferee:
    def __init__(
        self,
        supervisor: Supervisor,
        match_time: int,
        match_id: int,
        half_id: int,
        progress_check_steps: int,
        progress_check_threshold: int,
        ball_progress_check_steps: int,
        ball_progress_check_threshold: int,
        team_name_blue: str,
        team_name_yellow: str,
        initial_score_blue: int,
        initial_score_yellow: int,
        penalty_area_allowed_time: int,
        penalty_area_reset_after: int,
        post_goal_wait_time: int = 3,
        initial_position_noise: float = 0.15,
    ):
        self.sv = supervisor
        self.match_time = match_time
        self.time = match_time
        self.match_id = match_id
        self.half_id = half_id
        self.team_name_blue = team_name_blue
        self.team_name_yellow = team_name_yellow
        self.score_blue = initial_score_blue
        self.score_yellow = initial_score_yellow
        self.post_goal_wait_time = post_goal_wait_time
        self.initial_position_noise = initial_position_noise

        self.ball_reset_timer = 0
        self.ball_stop = 2

        self.robot_in_penalty_counter = {}
        self.progress_check = {}
        self.penalty_area_check = {}
        for robot in ROBOT_NAMES:
            self.progress_check[robot] = ProgressChecker(
                progress_check_steps, progress_check_threshold
            )

            self.penalty_area_check[robot] = PenaltyAreaChecker(
                penalty_area_allowed_time,
                penalty_area_reset_after,
            )

            self.robot_in_penalty_counter[robot] = 0

        self.progress_check["ball"] = ProgressChecker(
            ball_progress_check_steps, ball_progress_check_threshold
        )

        self.eventer = Eventer()
        self.event_messages_to_draw: List[Tuple[int, str]] = []

        self.reset_positions()
        self.sv.update_positions()
        self.sv.draw_team_names(self.team_name_blue, self.team_name_yellow)
        self.sv.draw_scores(self.score_blue, self.score_yellow)

    def _pack_data(self) -> str:
        waiting_for_kickoff = self.ball_reset_timer > 0
        data = {"waiting_for_kickoff": waiting_for_kickoff}
        return json.dumps(data)

    def _add_initial_position_noise(self, translation: List[float]) -> List[float]:
        level = self.initial_position_noise
        return [
            translation[0] + (random.random() - 0.5) * level,
            translation[1] + (random.random() - 0.5) * level,
            translation[2],
        ]

    def add_event_subscriber(self, subscriber: EventHandler):
        self.eventer.subscribe(subscriber)

    def add_event_message_to_queue(self, message: str):
        if len(self.event_messages_to_draw) >= MAX_EVENT_MESSAGES_IN_QUEUE:
            self.event_messages_to_draw.pop(0)
        self.event_messages_to_draw.append((self.time, message))

    def process_and_draw_event_messages(self):
        messages = []
        for time, msg in self.event_messages_to_draw:
            messages.append(f"{time_to_string(time)} - {msg}")
        self.sv.draw_event_messages(messages)

    def reset_checkers(self, object_name: str):
        self.progress_check[object_name].reset()
        if object_name != "ball":
            self.penalty_area_check[object_name].reset()

    def reset_ball_position(self):
        self.sv.set_ball_position(BALL_INITIAL_TRANSLATION)
        self.ball_stop = 2
        self.reset_checkers("ball")

    def reset_robot_position(self, robot_name: str):
        self.sv.reset_robot_velocity(robot_name)
        translation = ROBOT_INITIAL_TRANSLATION[robot_name].copy()
        translation = self._add_initial_position_noise(translation)
        self.sv.set_robot_position(robot_name, translation)
        self.sv.set_robot_rotation(robot_name, ROBOT_INITIAL_ROTATION[robot_name])
        self.reset_checkers(robot_name)

    def reset_positions(self):
        self.reset_ball_position()
        for robot in ROBOT_NAMES:
            self.reset_robot_position(robot)

    def reset_team_for_kickoff(self, team: str) -> str:
        robot = f"{team}1" 
        self.sv.set_robot_position(robot, KICKOFF_TRANSLATION[team])
        self.sv.set_robot_rotation(robot, ROBOT_INITIAL_ROTATION[robot])
        return robot

    def check_robots_in_penalty_area(self):
        for robot in ROBOT_NAMES:
            if robot == "B3" or robot == "Y3":
                continue
            pos = self.sv.get_robot_translation(robot)
            self.penalty_area_check[robot].track(pos, self.time)

            if self.penalty_area_check[robot].is_violating():
                furthest_spots = self.sv.get_unoccupied_neutral_spots_sorted(
                    NeutralSpotDistanceType.FURTHEST.value,
                    robot,
                )
                if furthest_spots:
                    neutral_spot = furthest_spots[0][0]
                    self.sv.move_object_to_neutral_spot(robot, neutral_spot)
                    self.reset_checkers(robot)

    def check_progress(self):
        """
        Check that the robots, as well as the ball, have made enough progress.
        """
        for robot in ROBOT_NAMES:
            pos = self.sv.get_robot_translation(robot)
            self.progress_check[robot].track(pos)

            # 1. Jika Keluar Lapangan -> RESET (Wajib)
            if is_outside(pos[0], pos[1]):
                 self.reset_robot_position(robot)
                 self.reset_checkers(robot)
                 continue

            # 2. Jika Lack of Progress (Macet)
            if not self.progress_check[robot].is_progress():
                self.eventer.event(
                    referee=self,
                    type=GameEvents.LACK_OF_PROGRESS.value,
                    payload={"type": "robot", "robot_name": robot},
                )
                
                # --- LOGIKA REVISI: BIARKAN ROBOT MUNDUR SENDIRI ---
                
                # Hanya reset KIPER (B3/Y3) karena posisi mereka krusial
                if robot == "B3" or robot == "Y3":
                    self.reset_robot_position(robot)
                
                # Untuk Striker (1) dan Gelandang (2):
                # JANGAN DIPINDAHKAN WASIT. Biarkan kode robot yang menangani mundur.
                # Kita hanya reset checker supaya tidak spamming log.
                else:
                    pass 

                self.reset_checkers(robot)

        # Cek Bola
        bpos = self.sv.get_ball_translation()
        self.progress_check["ball"].track(bpos)
        if is_outside(bpos[0], bpos[1]) or not self.progress_check["ball"].is_progress():
            self.eventer.event(referee=self, type=GameEvents.LACK_OF_PROGRESS.value, payload={"type": "ball"})
            nearest_spots = self.sv.get_unoccupied_neutral_spots_sorted(NeutralSpotDistanceType.NEAREST.value, "ball")
            if nearest_spots:
                neutral_spot = random.choice(nearest_spots[:LACK_OF_PROGRESS_NUMBER_OF_NEUTRAL_SPOTS])
                self.sv.move_object_to_neutral_spot("ball", neutral_spot[0])
                self.ball_stop = 2
            self.reset_checkers("ball")

    def check_goal(self):
        team_goal = None
        team_kickoff = None
        ball_translation = self.sv.get_ball_translation()
        ball_x, ball_y = ball_translation[0], ball_translation[1]

        if is_in_blue_goal(ball_x, ball_y):
            self.score_yellow += 1
            team_goal = self.team_name_yellow
            team_kickoff = Team.BLUE.value
        elif is_in_yellow_goal(ball_x, ball_y):
            self.score_blue += 1
            team_goal = self.team_name_blue
            team_kickoff = Team.YELLOW.value

        if team_goal and team_kickoff:
            self.sv.draw_scores(self.score_blue, self.score_yellow)
            self.ball_reset_timer = self.post_goal_wait_time
            self.eventer.event(referee=self, type=GameEvents.GOAL.value, payload={"team_name": team_goal, "score_yellow": self.score_yellow, "score_blue": self.score_blue})
            self.team_to_kickoff = team_kickoff

    def kickoff(self, team: Optional[str] = None):
        if team not in (Team.BLUE.value, Team.YELLOW.value, None):
            raise ValueError(f"Unexpected team name {team}")
        seed = random.random()
        if not team:
            team = Team.BLUE.value if seed > 0.5 else Team.YELLOW.value
        robot_name = self.reset_team_for_kickoff(team)
        self.eventer.event(referee=self, type=GameEvents.KICKOFF.value, payload={"robot_name": robot_name, "team_name": team})

    def tick(self) -> bool:
        self.sv.check_reset_physics_counters()
        if self.time == self.match_time:
            self.eventer.event(referee=self, type=GameEvents.MATCH_START.value, payload={"score_yellow": self.score_yellow, "score_blue": self.score_blue, "total_match_time": self.match_time, "team_name_yellow": self.team_name_yellow, "team_name_blue": self.team_name_blue, "match_id": self.match_id, "halftime": self.half_id})

        self.sv.update_positions()
        self.sv.emit_data(self._pack_data())
        self.time -= TIME_STEP / 1000.0

        if self.time < 0:
            self.eventer.event(referee=self, type=GameEvents.MATCH_FINISH.value, payload={"total_match_time": self.match_time, "score_yellow": self.score_yellow, "score_blue": self.score_blue, "team_name_yellow": self.team_name_yellow, "team_name_blue": self.team_name_blue})
            return False

        self.sv.draw_time(self.time)
        self.process_and_draw_event_messages()

        if self.ball_reset_timer == 0:
            self.check_goal()
            self.check_progress()
            self.check_robots_in_penalty_area()
        else:
            self.ball_reset_timer -= TIME_STEP / 1000.0
            self.sv.draw_goal_sign()
            if self.ball_reset_timer <= 0:
                self.reset_positions()
                self.ball_reset_timer = 0
                self.sv.hide_goal_sign()
                self.kickoff(self.team_to_kickoff)

        if self.ball_stop > 0:
            if self.ball_stop == 1:
                self.sv.reset_ball_velocity()
            self.ball_stop -= 1

        return True