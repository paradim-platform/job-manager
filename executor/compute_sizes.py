from dataclasses import dataclass

from manager.models import Size


@dataclass
class ComputeConfig:
    cpu: str
    memory: str
    time: str
    partition: str


_compute_configurations = {
    Size.XS: ComputeConfig(cpu='2', memory='1G', time='0-01:00', partition='batch'),
    Size.S: ComputeConfig(cpu='8', memory='16G', time='0-04:00', partition='batch'),
    Size.S_fast: ComputeConfig(cpu='8', memory='16G', time='0-01:00', partition='batch'),
    Size.M: ComputeConfig(cpu='16', memory='32G', time='0-08:00', partition='batch'),
    Size.M_fast: ComputeConfig(cpu='16', memory='32G', time='0-01:00', partition='batch'),
    Size.L: ComputeConfig(cpu='32', memory='32G', time='0-16:00', partition='batch'),
    Size.L_fast: ComputeConfig(cpu='32', memory='32G', time='0-01:00', partition='batch'),
    Size.XL: ComputeConfig(cpu='64', memory='32G', time='1-00:00', partition='batch'),
    Size.XL_fast: ComputeConfig(cpu='64', memory='32G', time='0-01:00', partition='batch'),
    Size.XXL: ComputeConfig(cpu='128', memory='64G', time='2-00:00', partition='batch_48h'),
    Size.XXL_fast: ComputeConfig(cpu='128', memory='64G', time='0-01:00', partition='batch'),

}

_gpu_compute_configurations = {
    Size.XS: ComputeConfig(cpu='2', memory='1G', time='0-01:00', partition='gpu'),
    Size.S: ComputeConfig(cpu='8', memory='16G', time='0-04:00', partition='gpu'),
    Size.S_fast: ComputeConfig(cpu='8', memory='16G', time='0-01:00', partition='gpu'),
    Size.M: ComputeConfig(cpu='16', memory='32G', time='0-08:00', partition='gpu'),
    Size.M_fast: ComputeConfig(cpu='16', memory='32G', time='0-01:00', partition='gpu'),
    Size.L: ComputeConfig(cpu='32', memory='32G', time='0-16:00', partition='gpu'),
    Size.L_fast: ComputeConfig(cpu='32', memory='32G', time='0-01:00', partition='gpu'),
    Size.XL: ComputeConfig(cpu='64', memory='32G', time='1-00:00', partition='gpu'),
    Size.XL_fast: ComputeConfig(cpu='64', memory='32G', time='0-01:00', partition='gpu'),
    Size.XXL: ComputeConfig(cpu='128', memory='64G', time='2-00:00', partition='gpu_48h'),
    Size.XXL_fast: ComputeConfig(cpu='128', memory='64G', time='0-01:00', partition='gpu'),
}


def find_compute_config(size: Size, with_gpu: bool) -> ComputeConfig:
    if with_gpu:
        return _gpu_compute_configurations[size.abbreviation]

    return _compute_configurations[size.abbreviation]
