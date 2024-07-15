def get_pid_controller_signal(Kp, Ki, Kd, error, integral, previous_error, dt):
    # calculate the proportional term
    proportional = Kp * error

    # calculate the integral term
    integral += error * dt
    integral_term = Ki * integral

    # calculate the derivative term
    derivative = (error - previous_error) / dt
    derivative_term = Kd * derivative

    # calculate the PID controller signal
    signal = proportional + integral_term + derivative_term

    return signal