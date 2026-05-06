import time

# Store demo response times
demo_response_times = []


def track_demo_response(start_time):

    duration = round(time.time() - start_time, 2)

    demo_response_times.append(duration)

    # Keep only latest 20 entries
    if len(demo_response_times) > 20:
        demo_response_times.pop(0)

    return duration


def get_average_response_time():

    if not demo_response_times:
        return 0

    avg = sum(demo_response_times) / len(demo_response_times)

    return round(avg, 2)