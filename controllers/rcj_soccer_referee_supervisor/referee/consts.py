from referee.enums import Team

DEFAULT_MATCH_TIME = 10 * 60  # 10 minutes

GOAL_YELLOW_Y_LIMIT = -0.745
GOAL_BLUE_Y_LIMIT = 0.745
GOAL_X_UPPER_LIMIT = 0.2
GOAL_X_LOWER_LIMIT = -0.209
GOAL_YELLOW_BACK_WALL_Y_LIMIT = -0.849
GOAL_BLUE_BACK_WALL_Y_LIMIT = 0.849

FIELD_Y_UPPER_LIMIT = 0.755
FIELD_Y_LOWER_LIMIT = -0.755
FIELD_X_UPPER_LIMIT = 0.655
FIELD_X_LOWER_LIMIT = -0.655

TIME_STEP = 32
ROBOT_NAMES = ["B1", "B2", "B3", "Y1", "Y2", "Y3"]
N_ROBOTS = len(ROBOT_NAMES)

BALL_DEPTH = 0
BALL_INITIAL_TRANSLATION = [0, 0, BALL_DEPTH]

CENTER_NS = "center_ns"
YELLOW_LEFT_NS = "yellow_left_ns"
YELLOW_MIDDLE_NS = "yellow_middle_ns"
YELLOW_RIGHT_NS = "yellow_right_ns"
BLUE_LEFT_NS = "blue_left_ns"
BLUE_MIDDLE_NS = "blue_middle_ns"
BLUE_RIGHT_NS = "blue_right_ns"
NEUTRAL_SPOTS = {
    CENTER_NS: (0, 0),
    YELLOW_LEFT_NS: (-0.3, -0.3),
    YELLOW_MIDDLE_NS: (0, -0.2),
    YELLOW_RIGHT_NS: (0.3, -0.3),
    BLUE_LEFT_NS: (0.3, 0.3),
    BLUE_MIDDLE_NS: (0, 0.2),
    BLUE_RIGHT_NS: (-0.3, 0.3),
}

# --- UPDATE POSISI SESUAI SOCCER.WBT ---
OBJECT_DEPTH = 0.042

ROBOT_INITIAL_TRANSLATION = {
    # TIM BIRU (Sejajar di Y=0.25, Kiper di 0.75)
    "B1": [0.25, 0.25, OBJECT_DEPTH],   # Sesuai WBT
    "B2": [-0.25, 0.25, OBJECT_DEPTH],  # Sesuai WBT
    "B3": [0, 0.75, OBJECT_DEPTH],      # Sesuai WBT

    # TIM KUNING (Sejajar di Y=-0.25, Kiper di -0.75)
    "Y1": [-0.25, -0.25, OBJECT_DEPTH], # Sesuai WBT
    "Y2": [0.25, -0.25, OBJECT_DEPTH],  # Sesuai WBT
    "Y3": [0, -0.75, OBJECT_DEPTH],     # Sesuai WBT
}

ROBOT_INITIAL_ROTATION = {
    # B1 & B2 Menghadap Bawah (-1.57)
    "B1": [0, 0, 1, -1.57],
    "B2": [0, 0, 1, -1.57],
    
    # Y1 & Y2 Menghadap Atas (1.57)
    "Y1": [0, 0, 1, 1.57],
    "Y2": [0, 0, 1, 1.57],

    # Kiper Menghadap Samping (0) - AGAR BISA SLIDING
    "B3": [0, 0, 1, 0],
    "Y3": [0, 0, 1, 0], 
}

# --- POSISI KICKOFF ---
# Kita samakan dengan posisi awal Striker (B1/Y1) 
# agar mereka tidak 'teleport' ke tengah saat kickoff.
BLUE_KICKOFF_TRANSLATION = [0.25, 0.25, OBJECT_DEPTH]
YELLOW_KICKOFF_TRANSLATION = [-0.25, -0.25, OBJECT_DEPTH]

KICKOFF_TRANSLATION = {
    Team.BLUE.value: BLUE_KICKOFF_TRANSLATION,
    Team.YELLOW.value: YELLOW_KICKOFF_TRANSLATION,
}

# (vertical boundary y, lower boundary x, upper boundary x)
YELLOW_PENALTY_AREA = (-0.59, -0.35, 0.35)
BLUE_PENALTY_AREA = (0.59, -0.35, 0.35)

MAX_EVENT_MESSAGES_IN_QUEUE = 10

DISTANCE_AROUND_UNOCCUPIED_NEUTRAL_SPOT = 0.08

LACK_OF_PROGRESS_NUMBER_OF_NEUTRAL_SPOTS = 3