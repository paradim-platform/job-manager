import json
import traceback

import pandas as pd
import pyorthanc

from executor import orthanc
from job_manager.celery import app
from .utils import retrieve_series
from ..models import AggregationSubmission


@app.task(ignore_result=True)
def create_aggregation_file(aggregation_pk: str, access_token: str, series_description_filter: str | None) -> None:
    aggregation = AggregationSubmission.objects.get(pk=aggregation_pk)
    aggregation.state = AggregationSubmission.State.RUNNING
    aggregation.save()

    try:
        app_name = aggregation.runnable.app.name
        app_version = aggregation.runnable.version

        if not series_description_filter:
            series_description_filter = f'{app_name}:{app_version}*'

        seriess = retrieve_series(
            album_id=aggregation.album_id,
            access_token=access_token,
            modality='SR',
            series_description_filter=series_description_filter
        )

        data = None

        for s in seriess:
            series = pyorthanc.find_series(orthanc.client, query={'SeriesInstanceUID': s.uid})[0]

            series

            for instance in series.instances:
                ds = instance.get_pydicom()
                prediction_dict = json.loads(ds.ContentSequence[0].TextValue)

                # The CSV case is handled differently. It makes a dataframe,
                # while the json output_format only return the raw content.
                if aggregation.filetype == AggregationSubmission.FileType.CSV:
                    if not data:
                        data = {k: [v] for k, v in prediction_dict.items()}
                    else:
                        for k, v in prediction_dict.items():
                            data[k].append(v)
                else:
                    if data is None:
                        data = [prediction_dict]
                    else:
                        data.append(prediction_dict)

        if aggregation.filetype == AggregationSubmission.FileType.CSV:
            if data:
                df = pd.DataFrame.from_dict(data=data, orient="index").T
            else:
                df = pd.DataFrame()  # Means that no series was found. Return an empty csv
            result = df.to_csv(header=True, index=False)

        else:
            result = json.dumps(data)

        aggregation.result = result
        aggregation.state = AggregationSubmission.State.COMPLETED
        aggregation.save()

    except Exception:
        aggregation.result = traceback.format_exc()
        aggregation.state = AggregationSubmission.State.ERROR
        aggregation.save()
