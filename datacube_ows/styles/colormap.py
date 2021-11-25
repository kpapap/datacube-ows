# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2021 OWS Contributors
# SPDX-License-Identifier: Apache-2.0
import io
import logging
from datetime import datetime
from typing import Callable, List, MutableMapping, Optional, Union, cast

import numpy
from colour import Color
from datacube.utils.masking import make_mask
from matplotlib import patches as mpatches
from matplotlib import pyplot as plt
from xarray import DataArray, Dataset, merge

from datacube_ows.config_utils import CFG_DICT, ConfigException, OWSConfigEntry
from datacube_ows.styles.base import StyleDefBase

_LOG = logging.getLogger(__name__)


class ValueMapRule(OWSConfigEntry):
    """
    A Value Map Rule.

    Construct a ValueMap rule-set with ValueMapRule.value_map_from_config
    """
    def __init__(self, style_def: "ColorMapStyleDef", band: str, cfg: CFG_DICT) -> None:
        """
        Construct a Value Map Rule

        :param style_def: The owning ColorMapStyleDef object
        :param band: The name of the flag-band the rules apply to
        :param cfg: The rule specification
        """
        super().__init__(cfg)
        cfg = cast(CFG_DICT, self._raw_cfg)
        self.style = style_def
        self.band = style_def.local_band(band)

        self.title = cast(str, cfg["title"])
        self.abstract = cast(str, cfg.get("abstract"))
        if self.title and self.abstract:
            self.label: Optional[str] = f"{self.title} - {self.abstract}"
        elif self.title:
            self.label = self.title
        elif self.abstract:
            self.label = self.abstract
        else:
            self.label = None
        self.color_str = cast(str, cfg["color"])
        self.rgb = Color(self.color_str)
        self.alpha = float(cast(Union[float, int, str], cfg.get("alpha", 1.0)))
        if "flags" in cfg:
            flags = cast(CFG_DICT, cfg["flags"])
            self.or_flags: bool = False
            if "or" in flags and "and" in flags:
                raise ConfigException(f"ValueMap rule in style {self.style.name} of layer {self.style.product.name} combines 'and' and 'or' rules")
            elif "or" in flags:
                self.or_flags = True
                flags = cast(CFG_DICT, flags["or"])
            elif "and" in flags:
                flags = cast(CFG_DICT, flags["and"])
            self.flags: Optional[CFG_DICT] = flags
        else:
            self.flags = None
            self.or_flags = False
        if "values" in cfg:
            self.values: Optional[List[int]] = cast(List[int], cfg["values"])
        else:
            self.values = None
        if not self.flags and not self.values:
            raise ConfigException(f"Value map rule in style {style_def.name} of layer {style_def.product.name} must have a non-empty 'flags' or 'values' section.")
        if self.flags and self.values:
            raise ConfigException(f"Value map rule in style {style_def.name} of layer {style_def.product.name} has both a 'flags' and a 'values' section - choose one.")

    def create_mask(self, data: DataArray) -> DataArray:
        """
        Create a mask from raw flag band data.

        :param data: Raw flag data, assumed to be for this rule's flag band.
        :return: A boolean DataArray, True where the data matches this rule
        """
        if self.values:
            mask: Optional[DataArray] = None
            for v in cast(List[int], self.values):
                vmask = data == v
                if mask is None:
                    mask = vmask
                else:
                    mask |= vmask
        elif self.or_flags:
            mask = None
            for f in cast(CFG_DICT, self.flags).items():
                f = {f[0]: f[1]}
                if mask is None:
                    mask = make_mask(data, **f)
                else:
                    mask |= make_mask(data, **f)
        else:
            mask = make_mask(data, **cast(CFG_DICT, self.flags))
        return mask

    @classmethod
    def value_map_from_config(cls,
                              style: "ColorMapStyleDef",
                              cfg: CFG_DICT) -> MutableMapping[str, List["ValueMapRule"]]:
        """
        Create a value map rule set from a config specification

        :param style: The parent style definition object
        :param cfg: The specification for the value map.

        :return: A value map ruleset dictionary.
        """
        vmap: MutableMapping[str, List["ValueMapRule"]] = {}
        for band_name, rules in cfg.items():
            band_rules = [cls(style, band_name, rule) for rule in cast(List[CFG_DICT], rules)]
            vmap[band_name] = band_rules
        return vmap


class MultiDateValueMapRule(OWSConfigEntry):
    # TODO: inherit from ValueMapRule? or merge into it?
    """
    A  Mulit-Date Value Map Rule.

    Construct a Multi-Date ValueMap rule-set with MultiDateValueMapRule.value_map_from_config
    """
    def __init__(self, mdh: "ColorMapStyleDef.MultiDateHandler", band: str,
                 rule_id: int, cfg: CFG_DICT) -> None:
        """
        Construct a Multi-date Value Map Rule

        :param style_def: The owning ColorMapStyleDef object
        :param band: The name of the flag-band the rules apply to
        :param cfg: The rule specification
        """
        super().__init__(cfg)
        cfg = cast(CFG_DICT, self._raw_cfg)
        self.mdh = mdh
        self.id = rule_id
        self.band = mdh.style.local_band(band)

        self.title = cast(str, cfg["title"])
        self.abstract = cast(str, cfg.get("abstract"))
        if self.title and self.abstract:
            self.label: Optional[str] = f"{self.title} - {self.abstract}"
        elif self.title:
            self.label = self.title
        elif self.abstract:
            self.label = self.abstract
        else:
            self.label = None
        self.color_str = cast(str, cfg["color"])
        self.rgb = Color(self.color_str)
        self.alpha = float(cast(Union[float, int, str], cfg.get("alpha", 1.0)))

        self.flags: Optional[List[CFG_DICT]] = []
        self.or_flags: Optional[List[bool]] = []
        self.values: Optional[List[List[int]]] = []
        if "flags" in cfg:
            date_flags = cast(CFG_DICT, cfg["flags"])
            if len(date_flags) != self.mdh.max_count:
                raise ConfigException(f"Flags entry has wrong number of rule sets for date count")
            for flags in date_flags:
                or_flag: bool = False
                if "or" in flags and "and" in flags:
                    raise ConfigException(f"MultiDateValueMap rule in style {self.mdh.style.name} of layer {self.mdh.style.product.name} combines 'and' and 'or' rules")
                elif "or" in flags:
                    or_flag = True
                    flags = cast(CFG_DICT, flags["or"])
                elif "and" in flags:
                    flags = cast(CFG_DICT, flags["and"])
                self.flags.append(flags)
                self.or_flags.append(or_flag)
        if "values" in cfg:
            self.values = cast(List[List[int]], list(cfg["values"]))
        else:
            self.values = None
        if not self.flags and not self.values:
            raise ConfigException(f"Multi-Date Value map rule in style {mdh.style.name} of layer {mdh.style.product.name} must have a non-empty 'flags' or 'values' section.")
        if self.flags and self.values:
            raise ConfigException(f"Multi-Date Value map rule in style {mdh.style.name} of layer {mdh.style.product.name} has both a 'flags' and a 'values' section - choose one.")

    def create_mask(self, data: DataArray) -> DataArray:
        """
        Create a mask from raw flag band data.

        :param data: Multi-date Raw flag data, assumed to be for this rule's flag band.
        :return: A boolean dateless DataArray, True where the data matches this rule
        """
        date_slices = (data.sel(time=dt) for dt in data.coords["time"].values)
        mask: Optional[DataArray] = None
        if self.values:
            for d_slice, vals in zip(date_slices, self.values):
                d_mask: Optional[DataArray] = None
                if len(vals) == 0:
                    d_mask = d_slice == d_slice
                else:
                    for v in cast(List[int], vals):
                        vmask = d_slice == v
                        if d_mask is None:
                            d_mask = vmask
                        else:
                            d_mask |= vmask
                if mask is None:
                    mask = d_mask
                else:
                    mask &= d_mask
        else:
            for d_slice, flags, or_flags in zip(date_slices, self.flags, self.or_flags):
                d_mask: Optional[DataArray] = None
                if not flags:
                    d_mask = d_slice == d_slice
                elif or_flags:
                    for f in cast(CFG_DICT, flags).items():
                        f = {f[0]: f[1]}
                        if d_mask is None:
                            d_mask = make_mask(d_slice, **f)
                        else:
                            d_mask |= make_mask(d_slice, **f)
                else:
                    d_mask = make_mask(d_slice, **cast(CFG_DICT, flags))
                if mask is None:
                    mask = d_mask
                else:
                    mask &= d_mask
        return mask

    @classmethod
    def value_map_from_config(cls,
                              mdh: "ColorMapStyleDef.MultiDateHandler",
                              cfg: CFG_DICT) -> MutableMapping[str, List["MultiDateValueMapRule"]]:
        """
        Create a multi-date value map rule set from a config specification

        :param style: The parent style definition object
        :param cfg: The specification for the multi-date value map.

        :return: A value map ruleset dictionary.
        """
        vmap: MutableMapping[str, List["ValueMapRule"]] = {}
        if mdh.min_count != mdh.max_count:
            raise ConfigException("MultiDate value map only supported on multi-date handlers with min_count and max_count equal.")
        for i, (band_name, rules) in enumerate(cfg.items()):
            band_rules = [cls(mdh, band_name, i, rule) for rule in cast(List[CFG_DICT], rules)]
            vmap[band_name] = band_rules
        return vmap


def apply_multidate_value_map(value_map: MutableMapping[str, List[MultiDateValueMapRule]],
                    data: Dataset,
                    band_mapper: Callable[[str], str]) -> Dataset:
    imgdata = Dataset(coords={k: v for k, v in data.coords.items() if k != "time"})
    for cfg_band, rules in value_map.items():
        # Run through each item
        band = band_mapper(cfg_band)
        bdata = cast(DataArray, data[band])
        band_data = Dataset()
        if bdata.dtype.kind == 'f':
            # Convert back to int for bitmasking
            bdata = ColorMapStyleDef.reint(bdata)
        for rule in rules:
            mask = rule.create_mask(bdata)
            masked = ColorMapStyleDef.create_colordata(mask, rule.rgb, rule.alpha, mask)
            band_data = masked if len(band_data.data_vars) == 0 else band_data.combine_first(masked)
        imgdata = band_data if len(imgdata.data_vars) == 0 else merge([imgdata, band_data])
    imgdata = imgdata * 255 + 0.5
    return imgdata.astype('uint8')


def apply_value_map(value_map: MutableMapping[str, List[ValueMapRule]],
                    data: Dataset,
                    band_mapper: Callable[[str], str]) -> Dataset:
    imgdata = Dataset(coords=data.coords)
    for cfg_band, rules in value_map.items():
        # Run through each item
        band = band_mapper(cfg_band)
        bdata = cast(DataArray, data[band])
        band_data = Dataset()
        if bdata.dtype.kind == 'f':
            # Convert back to int for bitmasking
            bdata = ColorMapStyleDef.reint(bdata)
        for rule in rules:
            mask = rule.create_mask(bdata)
            masked = ColorMapStyleDef.create_colordata(bdata, rule.rgb, rule.alpha, mask)
            band_data = masked if len(band_data.data_vars) == 0 else band_data.combine_first(masked)

        imgdata = band_data if len(imgdata.data_vars) == 0 else merge([imgdata, band_data])
    imgdata *= 255
    return imgdata.astype('uint8')


def value_map_legend(value_map: MutableMapping[str, List[ValueMapRule]],
                     legend_cfg: CFG_DICT,
                     bytesio: io.BytesIO) -> None:
    patches = []
    for band in value_map.keys():
        for rule in reversed(value_map[band]):
            # only include values that are not transparent (and that have a non-blank title or abstract)
            if rule.alpha > 0.001 and rule.label:
                try:
                    patch = mpatches.Patch(color=rule.rgb.hex_l, label=rule.label)
                # pylint: disable=broad-except
                except Exception as e:
                    print("Error creating patch?", e)
                patches.append(patch)
    cfg = legend_cfg
    plt.rcdefaults()
    if cfg.get("rcParams", None) is not None:
        plt.rcParams.update(cfg.get("rcParams"))
    figure = plt.figure(figsize=(cfg.get("width", 3),
                                 cfg.get("height", 1.25)))
    plt.axis('off')
    legend = plt.legend(handles=patches, loc='center', frameon=False)
    plt.savefig(bytesio, format='png')


class ColorMapStyleDef(StyleDefBase):
    """
    Style subclass for value-map styles
    """
    auto_legend = True

    def __init__(self,
                 product: "datacube_ows.ows_configuration.OWSNamedLayer",
                 style_cfg: CFG_DICT,
                 stand_alone: bool = False,
                 user_defined: bool = False) -> None:
        """"
        Constructor - refer to StyleDefBase
        """
        super().__init__(product, style_cfg, stand_alone=stand_alone, user_defined=user_defined)
        style_cfg = cast(CFG_DICT, self._raw_cfg)
        self.value_map = ValueMapRule.value_map_from_config(self, cast(CFG_DICT, style_cfg["value_map"]))
        for band in self.value_map.keys():
            self.raw_needed_bands.add(band)

    @staticmethod
    def reint(data: DataArray) -> DataArray:
        """
        Convert a data-array to int.

        :param data: input data (potentially non-integer)
        :return: same data cast to integer
        """
        inted = data.astype("int")
        if hasattr(data, "attrs"):
            attrs = data.attrs
            inted.attrs = attrs
        return inted

    @staticmethod
    def create_colordata(data: DataArray, rgb: Color, alpha: float, mask: DataArray) -> Dataset:
        """Colour a mask with a given colour/alpha"""
        target = Dataset(coords=data.coords)
        colors = ["red", "green", "blue", "alpha"]
        for color in colors:
            val = alpha if color == "alpha" else getattr(rgb, color)
            c = numpy.full(data.shape, val)
            target[color] = DataArray(c, dims=data.dims, coords=data.coords)
        # pyre-ignore[6]
        masked = target.where(mask).where(numpy.isfinite(data))  # remask
        return masked

    def transform_single_date_data(self, data: Dataset) -> Dataset:
        """
        Apply style to raw data to make an RGBA image xarray (single time slice only)

        :param data: Raw data, all bands.
        :return: RGBA uint8 xarray
        """
        # pylint: disable=too-many-locals, too-many-branches
        # extent mask data per band to preseve nodata
        _LOG.debug("transform begin %s", datetime.now())
        # if extent_mask is not None:
        #    for band in data.data_vars:
        # try:
        #            data[band] = data[band].where(extent_mask, other=data[band].attrs['nodata'])
        #        except AttributeError:
        #            data[band] = data[band].where(extent_mask)
        return apply_value_map(self.value_map, data, self.product.band_idx.band)

    def single_date_legend(self, bytesio: io.BytesIO) -> None:
        """
        Write a legend into a bytes buffer as a PNG image.

        :param bytesio:  io.BytesIO byte buffer.
        """
        value_map_legend(self.value_map, self.legend_cfg, bytesio)

    class MultiDateHandler(StyleDefBase.MultiDateHandler):
        auto_legend = True
        non_animate_requires_aggregator = False

        def __init__(self, style: "ColorMapStyleDef", cfg: CFG_DICT) -> None:
            """
            First stage initialisation

            :param style: The parent style object
            :param cfg: The multidate handler configuration
            """
            super().__init__(style, cfg)
            if self.animate:
                self._value_map: Optional[MutableMapping[str, Union[ValueMapRule, MultiDateValueMapRule]]] = None
            elif self.aggregator:
                self._value_map = ValueMapRule.value_map_from_config(self.style, cast(CFG_DICT, self._raw_cfg["value_map"]))
            else:
                self._value_map = MultiDateValueMapRule.value_map_from_config(self, cast(CFG_DICT, self._raw_cfg["value_map"]))

        @property
        def value_map(self):
            if self._value_map is None:
                self._value_map = self.style.value_map
            return self._value_map

        def transform_data(self, data: "xarray.Dataset") -> "xarray.Dataset":
            """
            Apply image transformation

            :param data: Raw data
            :return: RGBA image xarray.  May have a time dimension
            """
            if self.aggregator is None:
                return apply_multidate_value_map(self.value_map, data, self.style.product.band_idx.band)
            else:
                agg = self.aggregator(data)
                return apply_value_map(self.value_map, agg, self.style.product.band_idx.band)

        def legend(self, bytesio: io.BytesIO) -> None:
            """
            Write a legend into a bytes buffer as a PNG image.

            :param bytesio:  io.BytesIO byte buffer.
            """
            value_map_legend(self.value_map, self.legend_cfg, bytesio)

# Register ColorMapStyleDef as a style subclass.
StyleDefBase.register_subclass(ColorMapStyleDef, "value_map")
