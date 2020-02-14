import json


def migrate_altitudes(traces_model):
    print(f"migrating trace models altitude: {traces_model}")
    traces = traces_model.objects.all()
    for trace in traces:
        t = traces_model.objects.get(pk=trace.pk)
        if t.elevation:
            print(f"modifying trace: {t}")
            ele = json.loads(t.elevation)
            print(f"ele: {ele}")
            ele = list(ele)
            print(f"len ele: {len(ele)}")
            print(f"max ele: {min(ele)}")
            print(f"max ele: {max(ele)}")
            t.save()
