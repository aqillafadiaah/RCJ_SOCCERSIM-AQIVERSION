def get_direction(ball_vector: list) -> int:
    if -0.13 <= ball_vector[1] <= 0.13:
        return 0
    return -1 if ball_vector[1] < 0 else 1
