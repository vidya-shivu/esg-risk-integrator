import time

demo_response_times = []

def track_demo_response(start_time):
    duration = round(time.time() - start_time, 2)

    demo_response_times.append(duration)

    if len(demo_response_times) > 20:
        demo_response_times.pop(0)

    return duration