def format_tag_path(provider, path):
    """Build a fully qualified tag path."""
    return "[%s]%s" % (provider, path)


def read_motor_status(motor_path):
    """Read running and fault status for a motor."""
    running = system.tag.readBlocking([motor_path + "/Running"])[0].value
    faulted = system.tag.readBlocking([motor_path + "/Faulted"])[0].value
    return {"running": running, "faulted": faulted}
