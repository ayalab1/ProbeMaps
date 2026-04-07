import io
from contextlib import redirect_stdout

from src.ProbeMapper import NeuroscopeParams, ProbeMapper


def _compute_silent(mapper: ProbeMapper) -> None:
    with redirect_stdout(io.StringIO()):
        mapper.compute()


def _assert_mapper_equivalent(original: ProbeMapper, loaded: ProbeMapper) -> None:
    assert original.channel_map == loaded.channel_map
    assert original.chan_per_shank == loaded.chan_per_shank
    assert original.probe_type == loaded.probe_type
    assert original.probe_connector == loaded.probe_connector

    assert original.xml_params.sampling_rate == loaded.xml_params.sampling_rate
    assert original.xml_params.lfp_sampling_rate == loaded.xml_params.lfp_sampling_rate
    assert sorted(original.xml_params.skip_channels) == sorted(loaded.xml_params.skip_channels)
    assert sorted(original.xml_params.extra_channels) == sorted(loaded.xml_params.extra_channels)
    assert original.xml_params.channel_color == loaded.xml_params.channel_color


def test_round_trip_h64_without_extra_channels(tmp_path) -> None:
    original = ProbeMapper(
        channel_map=list(range(1, 65)),
        chan_per_shank=[16, 16, 16, 16],
        probe_type="neuronexus",
        probe_connector="H64",
        probe_name="A4x16_test",
        basepath=tmp_path,
        export_xml=True,
        export_txt=False,
        xml_params=NeuroscopeParams(
            sampling_rate=30000,
            lfp_sampling_rate=1250,
            channel_color="#00aaee",
        ),
    )
    _compute_silent(original)

    xml_path = tmp_path / "neuronexus_A4x16_test_version1.xml"
    loaded = ProbeMapper.from_xml(
        xml_path,
        probe_type="neuronexus",
        probe_connector="H64",
        probe_name="A4x16_loaded",
        export_xml=False,
        export_txt=False,
    )

    _assert_mapper_equivalent(original, loaded)


def test_round_trip_h16_with_skip_and_extra_channels(tmp_path) -> None:
    original = ProbeMapper(
        channel_map=list(range(1, 17)),
        chan_per_shank=[16],
        probe_type="neuronexus",
        probe_connector="H16",
        probe_name="A1x16_test",
        basepath=tmp_path,
        export_xml=True,
        export_txt=False,
        xml_params=NeuroscopeParams(
            sampling_rate=20000,
            lfp_sampling_rate=1000,
            skip_channels=[5, 7],
            extra_channels=[16, 17, 18],
            channel_color="#1122ff",
        ),
    )
    _compute_silent(original)

    xml_path = tmp_path / "neuronexus_A1x16_test_version1.xml"
    loaded = ProbeMapper.from_xml(
        xml_path,
        probe_type="neuronexus",
        probe_connector="H16",
        probe_name="A1x16_loaded",
        export_xml=False,
        export_txt=False,
    )

    _assert_mapper_equivalent(original, loaded)
