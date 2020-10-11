import logging

from wizer import models
from wizer.apps import get_md5sums_from_model, get_all_files, calc_md5, parse_and_save_to_model, parse_data, \
    save_laps_to_model
from wizer.tools.utils import limit_string

log = logging.getLogger(__name__)


class Reimporter:
    def __init__(self):
        self.settings = models.Settings.objects.get(pk=1)
        self.force_overwrite = self.settings.reimporter_updates_all
        self.path = self.settings.path_to_trace_dir
        self.activity_modified = None
        self.updated_activities = set()

        # run reimporter
        self._reimport_activity_data(models)

    def _reimport_activity_data(self, models):
        log.info(f"starting reimport process...")
        md5sums_from_db = get_md5sums_from_model(traces_model=models.Traces)
        trace_files = get_all_files(path=self.path)
        number_of_trace_files = len(trace_files)
        for i, trace_file in enumerate(trace_files):
            log.info(f"({i}/{number_of_trace_files}) reimporting: {trace_file} ")
            self.activity_modified = False
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
                trace = models.Traces.objects.get(md5sum=md5sum)
                activity = models.Activity.objects.get(trace_file=trace)
                self._compare_and_update(activity, parser)
                self._compare_and_update(trace, parser)
                laps = models.Lap.objects.filter(trace=trace)
                if laps:    # activity has laps in db already
                    for lap_instance, parser_lap in zip(laps, parser.laps):
                        self._compare_and_update(lap_instance, parser_lap)
                elif not laps and parser.laps:  # no laps in db but parser
                    save_laps_to_model(models.Lap, parser.laps, trace)
                    self.activity_modified = True

                if self.activity_modified:
                    log.info(f"updated data for {activity.name} ...")
                    self.updated_activities.add(activity.name)
                else:
                    log.info(f"no relevant update for {activity.name}")
        log.debug(f"updated {len(self.updated_activities)} activities:\n{self.updated_activities}")
        log.info(f"successfully parsed trace files and updated corresponding database objects")

    def _compare_and_update(self, obj, parser):
        updated = False
        for attribute, value in parser.__dict__.items():
            if attribute == 'sport':
                continue
            if hasattr(obj, attribute):
                if self.force_overwrite:
                    log.debug(f"force overwriting value for {attribute}")
                    setattr(obj, attribute, value)
                    self.activity_modified = True
                    updated = True
                else:
                    db_value = getattr(obj, attribute)
                    if not _values_equal(db_value, value):
                        log.debug(f"overwriting value for {attribute} old: {limit_string(db_value, 100)} to: {limit_string(value, 100)}")
                        setattr(obj, attribute, value)
                        self.activity_modified = True
                        updated = True
                    else:
                        # log.debug(f"values for {attribute} are the same")
                        pass
            else:
                # log.debug(f"model does not have the attribute: '{attribute}'")
                pass
        if updated:
            obj.save()


def _values_equal(value_a, value_b):
    if value_a == value_b:
        return True
    elif (value_a is None and value_b) or (value_b is None and value_a):
        return False
    else:
        if str(value_a) == str(value_b):
            return True
        else:
            try:
                if str(float(value_a)) == str(float(value_b)):
                    return True
                else:
                    return False
            except (ValueError, TypeError):
                return False
