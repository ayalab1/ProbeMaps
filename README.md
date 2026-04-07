# ProbeMaps
Maps for different silicon probes 

## Create a `ProbeMapper` from an existing XML

You can now construct a `ProbeMapper` directly from a Neuroscope XML file that
follows the format produced by this project.

```python
from pathlib import Path
from src.ProbeMapper import ProbeMapper

mapper = ProbeMapper.from_xml(
	xml_path=Path("tutorial/neuronexus_a416_version1.xml"),
	probe_type="neuronexus",
	probe_connector="H64",
	export_xml=False,
	export_txt=False,
)

# Recompute/export mappings as usual
mapper.compute()
```

### Notes

- `probe_type` and `probe_connector` must match one of the supported layouts in
	`OMNETICS_LAYOUTS`.
- If `probe_name` is not provided, it is inferred from the XML filename.
- The XML acquisition/spike parameters, skipped channels, and extra channels are
	automatically loaded into `mapper.xml_params`.
