def status(health):
    if health >= 90:
        return "Healthy"
    elif health >= 75:
        return "Warning"
    elif health >= 60:
        return "Critical"
    else:
        return "Immediate Maintenance"
