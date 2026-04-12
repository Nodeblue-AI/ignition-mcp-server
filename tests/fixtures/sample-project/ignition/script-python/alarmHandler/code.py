def handleAlarm(event):
    """Gateway-scoped alarm handler.

    Checks all conveyor fault tags and logs active faults to the database.
    """
    fault_tags = system.tag.readBlocking([
        "[default]Conveyors/Line1/Faulted",
    ])
    for i, qv in enumerate(fault_tags):
        if qv.value:
            system.db.runNamedQuery("LogFault", {"tagIndex": i, "timestamp": system.date.now()})
