import logging

from wizer.apps import get_md5sums_from_model, get_all_files, calc_md5, parse_and_save_to_model, parse_data, \
    save_laps_to_model

log = logging.getLogger(__name__)


def reimport_activity_data(models):
    log.info(f"starting reimport process...")
    settings = models.Settings.objects.get(pk=1)
    path = settings.path_to_trace_dir
    force_overwrite = settings.reimporter_updates_all
    md5sums_from_db = get_md5sums_from_model(traces_model=models.Traces)
    trace_files = get_all_files(path=path)
    updated_activities = []
    for trace_file in trace_files:
        md5sum = calc_md5(trace_file)
        if md5sum not in md5sums_from_db:  # trace file is not in db already
            log.debug(f"{trace_file} not yet in db, will import it...")
            parse_and_save_to_model(
                models=models,
                md5sum=md5sum,
                trace_file=trace_file,
            )
        else:  # trace file is in db already
            parser = parse_data(file=trace_file)
            corresponding_trace_instance = models.Traces.objects.get(md5sum=md5sum)
            corresponding_activity_instance = models.Activity.objects.get(trace_file=corresponding_trace_instance)
            corresponding_lap_instance = models.Lap.objects.filter(trace=corresponding_trace_instance)
            log.debug(f"reading values for {corresponding_activity_instance.name}...")
            modified_value = False
            for attribute, value in parser.__dict__.items():
                if hasattr(corresponding_trace_instance, attribute):
                    if force_overwrite:
                        log.debug(f"force overwriting value for {attribute}")
                        setattr(corresponding_trace_instance, attribute, value)
                        modified_value = True
                    else:
                        db_value = getattr(corresponding_trace_instance, attribute)
                        if not _values_equal(db_value, value):
                            log.debug(f"overwriting value for {attribute}: old: {db_value} to: {value}")
                            setattr(corresponding_trace_instance, attribute, value)
                            modified_value = True
                        else:
                            # log.debug(f"values for {attribute} are the same")
                            pass
                else:
                    # log.debug(f"model does not have the attribute: '{attribute}'")
                    pass
            if corresponding_lap_instance:  # given trace has actually laps in db already
                if force_overwrite:
                    save_laps_to_model(models.Lap, parser.laps, corresponding_trace_instance)
            else:   # given trace file has no laps yet
                if parser.laps:     # parsed file has laps
                    save_laps_to_model(models.Lap, parser.laps, corresponding_trace_instance)
            if modified_value:
                log.info(f"updating data for {corresponding_activity_instance.name} ...")
                corresponding_trace_instance.save()
                updated_activities.append((corresponding_activity_instance.name, str(corresponding_activity_instance.date)))
            else:
                log.info(f"no relevant update for {corresponding_activity_instance.name}")
    log.debug(f"updated the following {len(updated_activities)} activities:\n{updated_activities}")
    log.info(f"successfully parsed trace files and updated corresponding database objects")

    return updated_activities


def _values_equal(value_a, value_b):
    if value_a == value_b:
        return True
    else:
        if str(value_a) == str(value_b):
            return True
        else:
            if str(float(value_a)) == str(float(value_b)):
                return True
            else:
                return False
