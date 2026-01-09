"""Passive probe to Intan headstage channel mapping.

This module provides an API for converting Omnetics probe
channel numbering to Intan headstage channel numbering. 
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Mapping, Sequence


@dataclass(frozen=True)
class Layout:
    """Immutable representation of a connector layout."""

    name: str
    pins: Sequence[int]

    @property
    def flipped(self) -> List[int]:
        """Return the reversed layout (useful for flipped headstage orientation)."""

        return list(reversed(self.pins))


# Intan headstage layouts (preamp ordering)
# Add new Intan headstage sizes here: use channel count as key and a Layout with pins
# ordered per the Intan schematic (dorsal→ventral, left→right as needed).
INTAN_LAYOUTS: Mapping[int, Layout] = {
    16: Layout(
        name="intan16",
        pins=[11, 10, 9, 8, 7, 6, 5, 4, 12, 13, 14, 15, 0, 1, 2, 3],
    ),
    32: Layout(
        name="intan32",
        pins=[
            23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8,
            24, 25, 26, 27, 28, 29, 30, 31, 0, 1, 2, 3, 4, 5, 6, 7,
        ],
    ),
    64: Layout(
        name="intan64",
        pins=[
            46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16,
            47, 45, 43, 41, 39, 37, 35, 33, 31, 29, 27, 25, 23, 21, 19, 17,
            49, 51, 53, 55, 57, 59, 61, 63, 1, 3, 5, 7, 9, 11, 13, 15,
            48, 50, 52, 54, 56, 58, 60, 62, 0, 2, 4, 6, 8, 10, 12, 14,
        ],
    ),
}


# Omnetics pinouts for  probe families
# Add new probes/connectors here: key is (probe_type, connector), value is Layout with
# Omnetics pin order as printed on the probe datasheet (match the mechanical numbering).
OMNETICS_LAYOUTS: Mapping[tuple[str, str], Layout] = {
    ("neuronexus", "H16"): Layout(
        name="neuronexus_H16",
        pins=[14, 15, 9, 16, 1, 8, 2, 3, 12, 11, 10, 13, 4, 7, 6, 5],
    ),
    ("neuronexus", "H32"): Layout(
        name="neuronexus_H32",
        pins=[
            18, 27, 28, 29, 17, 30, 31, 32, 1, 2, 3, 16, 4, 5, 6, 15,
            20, 21, 22, 23, 19, 24, 25, 26, 7, 8, 9, 14, 10, 11, 12, 13,
        ],
    ),
    ("neuronexus", "H64"): Layout(
        name="neuronexus_H64",
        pins=[
            34, 43, 44, 45, 33, 46, 47, 48, 17, 18, 19, 32, 20, 21, 22, 31,
            42, 41, 40, 35, 39, 38, 37, 36, 29, 28, 27, 26, 30, 25, 24, 23,
            64, 62, 60, 58, 56, 54, 52, 50, 15, 13, 11, 9, 7, 5, 3, 1,
            63, 61, 59, 57, 55, 53, 51, 49, 16, 14, 12, 10, 8, 6, 4, 2,
        ],
    ),
}


class ProbeMapper:
    """Utility for converting Omnetics channel numbering to Intan numbering.

    Parameters
    ----------
    channel_map:
        Desired ordering of probe channels as they appear on the shanks
        (dorsal to ventral, left to right). The length must match the chosen
        connector layout.
    chan_per_shank:
        Number of channels per shank, used for shank-wise text outputs.
    probe_type / probe_connector:
        Keys into the predefined OMNETICS_LAYOUTS dictionary.
    probe_name:
        Identifier used in saved file names.
    basepath:
        Directory in which mapping files are written when ``save=True``.
    save:
        Persist mapping text files if True.
    """

    def __init__(
        self,
        *,
        channel_map: Sequence[int],
        chan_per_shank: Sequence[int],
        probe_type: str,
        probe_connector: str,
        probe_name: str,
        basepath: str | Path | None = None,
        save: bool = False,
        versions: Sequence[str] = ("version1", "version2"),
    ) -> None:
        self.channel_map = list(channel_map)
        self.chan_per_shank = list(chan_per_shank)
        self.probe_type = probe_type.lower()
        self.probe_connector = probe_connector.upper()
        self.probe_name = probe_name
        self.basepath = Path(basepath) if basepath is not None else Path.cwd()
        self.save = save
        self.versions = list(versions)

        self.omnetics_layout = self._require_omnetics_layout()
        self.intan_layout = self._require_intan_layout()
        self._validate_lengths()
        self._validate_versions()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def compute(self) -> None:
        """Compute regular and flipped mappings, optionally write files, print report."""

        device_channel_indices = self._map_channel_indices(self.intan_layout.pins)
        flipped_channel_indices = self._map_channel_indices(self.intan_layout.flipped)

        version_a, version_b = self.versions

        if self.save:
            path_a = self._save_mapping(device_channel_indices, suffix=version_a)
            path_b = self._save_mapping(flipped_channel_indices, suffix=version_b)
            print(f"Saved: {path_a}")
            print(f"Saved: {path_b}")

        print(self._format_report(device_channel_indices, flipped_channel_indices))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _require_omnetics_layout(self) -> Layout:
        key = (self.probe_type, self.probe_connector)
        if key not in OMNETICS_LAYOUTS:
            known = ", ".join(sorted({f"{k[0]}-{k[1]}" for k in OMNETICS_LAYOUTS}))
            raise ValueError(f"Unsupported probe/connector: {key}. Known: {known}")
        return OMNETICS_LAYOUTS[key]

    def _require_intan_layout(self) -> Layout:
        pin_count = len(self.omnetics_layout.pins)
        if pin_count not in INTAN_LAYOUTS:
            known_sizes = ", ".join(str(k) for k in sorted(INTAN_LAYOUTS))
            raise ValueError(f"No Intan layout for {pin_count} channels. Known sizes: {known_sizes}")
        return INTAN_LAYOUTS[pin_count]

    def _validate_lengths(self) -> None:
        if len(self.channel_map) != len(self.omnetics_layout.pins):
            raise ValueError(
                "channel_map length must match Omnetics layout length"
                f" ({len(self.channel_map)} vs {len(self.omnetics_layout.pins)})"
            )
        if sum(self.chan_per_shank) != len(self.channel_map):
            raise ValueError(
                "chan_per_shank must sum to the total number of channels"
            )

    def _validate_versions(self) -> None:
        if len(self.versions) != 2 or any(not v for v in self.versions):
            raise ValueError("versions must be a pair of non-empty strings")

    def _map_channel_indices(self, intan_preamp: Sequence[int]) -> List[int]:
        probe_index = {value: index for index, value in enumerate(self.omnetics_layout.pins)}
        return [intan_preamp[probe_index[ch]] for ch in self.channel_map]

    def _save_mapping(self, mapped: Sequence[int], *, suffix: str) -> Path:
        path = self.basepath / f"{self.probe_type}_{self.probe_name}_{suffix}.txt"
        lines = self._format_lines(mapped)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines))
        return path

    def _format_lines(self, mapped: Sequence[int]) -> List[str]:
        lines: List[str] = []
        start = 0
        for shank_idx, count in enumerate(self.chan_per_shank, start=1):
            end = start + count
            lines.append(f"shank{shank_idx}: {' '.join(str(v) for v in mapped[start:end])}")
            start = end
        return lines

    def _format_report(self, mapped: Sequence[int], flipped: Sequence[int]) -> str:
        version_a, version_b = self.versions
        report_lines = [f"Contents of {self.probe_type}_{self.probe_name}_{version_a}.txt:"]
        report_lines.extend(self._format_lines(mapped))
        report_lines.append("")
        report_lines.append(f"Contents of {self.probe_type}_{self.probe_name}_{version_b}.txt:")
        report_lines.extend(self._format_lines(flipped))
        return "\n".join(report_lines)


__all__ = ["ProbeMapper", "Layout", "INTAN_LAYOUTS", "OMNETICS_LAYOUTS"]


