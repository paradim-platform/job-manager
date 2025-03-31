from parameterized import parameterized

from executor import schedulers
from manager.models import Job
from manager.tests.setup import APITestCaseWithRunnable

SERIES_INSTANCE_UID = '1.2.3.4.198739817298',
STUDY_INSTANCE_UID = '1.2.3.4.1987398172981',


class TestSchedulers(APITestCaseWithRunnable):

    def setUp(self):
        super().setUp()
        self.job = Job(
            study_instance_uid=STUDY_INSTANCE_UID,
            series_instance_uid=SERIES_INSTANCE_UID,
            runnable=self.runnable,
            state=Job.State.SUBMITTED_TO_QUEUE
        )

    @parameterized.expand([False, True])
    def test_make_slurm_file(self, with_gpu: bool):
        self.runnable.with_gpu = with_gpu

        result = schedulers.make_slurm_file(
            job=self.job,
            dist_dirname='DIST_DIRNAME',
            paradim_token='PARADIM_TOKEN',
            additional_info='Some additional info'
        )

        assert '#!/bin/bash' == result[:len('#!/bin/bash')]
        assert '--img=$PARADIM_IMAGES_PATH/Algo1_1.12.3.sif' in result
        if with_gpu:
            assert '\n#SBATCH --gpus-per-node=' in result
        else:
            assert '\n#SBATCH --gpus-per-node=' not in result
        sbatch_config_lines = [line for line in result.split('\n') if '#SBATCH' in line]
        for line in sbatch_config_lines:
            assert line[0] == '#', \
                'Each SBATCH config lines should not start with an indent (error likely due to python string)'
