import logging

from wizer.apps import get_md5sums_from_model, get_all_files, calc_md5, parse_and_save_to_model, parse_activity_data

log = logging.getLogger(__name__)


def reimport_activity_data(settings_model, traces_model, activity_model, sport_model):
    log.info(f"starting reimport process...")
    md5sums_from_db = get_md5sums_from_model(traces_model=traces_model)
    path = settings_model.objects.get(pk=1).path_to_trace_dir
    force_overwrite = settings_model.objects.get(pk=1).reimporter_updates_all
    trace_files = get_all_files(path=path)
    updated_activities = []
    for trace_file in trace_files:
        md5sum = calc_md5(trace_file)
        if md5sum not in md5sums_from_db:  # trace file is not in db already
            log.debug(f"{trace_file} not yet in db, will import it...")
            parse_and_save_to_model(
                traces_model=traces_model,
                sport_model=sport_model,
                activity_model=activity_model,
                md5sum=md5sum,
                trace_file=trace_file,
            )
        else:   # trace file is in db already
            parser = parse_activity_data(file=trace_file)
            corresponding_trace_object = traces_model.objects.get(md5sum=md5sum)
            corresponding_activity_object = activity_model.objects.get(trace_file=corresponding_trace_object)
            log.debug(f"reading values for {corresponding_activity_object.name}...")
            modified_value = False
            for attribute, value in parser.__dict__.items():
                if hasattr(corresponding_trace_object, attribute):
                    if force_overwrite:
                        setattr(corresponding_trace_object, attribute, value)
                        modified_value = True
                    else:
                        db_value = getattr(corresponding_trace_object, attribute)
                        if str(db_value) != str(value):
                            # log.debug(f"would change values for {attribute}")
                            # log.debug(f"db value: {db_value}")
                            # log.debug(f"newly parsed value: {value}")
                            setattr(corresponding_trace_object, attribute, value)
                            modified_value = True
                        else:
                            # log.debug(f"values for {attribute} are the same")
                            pass
                else:
                    # log.debug(f"model does not have the attribute: '{attribute}'")
                    pass
            if modified_value:
                log.info(f"updating data for {corresponding_activity_object.name} ...")
                corresponding_trace_object.save()
                updated_activities.append((corresponding_activity_object.name, str(corresponding_activity_object.date)))
            else:
                log.info(f"no relevant update for {corresponding_activity_object.name}")
    log.debug(f"updated the following activities:\n{updated_activities}")
    log.info(f"successfully parsed trace files and updated corresponding database objects")

    return updated_activities
