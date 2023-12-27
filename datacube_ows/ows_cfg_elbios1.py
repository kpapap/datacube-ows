# pylint: skip-file
# This file is part of datacube-ows, part of the Open Data Cube project.
# See https://opendatacube.org for more information.
#
# Copyright (c) 2017-2021 OWS Contributors
# SPDX-License-Identifier: Apache-2.0


# Example configuration file for datacube_ows.
#
# The file was originally the only documentation for the configuration file format.
# Detailed and up-to-date formal documentation is now available and this this file
# is no longer actively maintained and may contain errors or obsolete elements.
#
# https://datacube-ows.readthedocs.io/en/latest/configuration.html

# THIS EXAMPLE FILE
#
# In this example file, there are some reusable code chunks defined at the top.  The actual
# config tree is defined as ows_cfg below the reusable chunks.
#

# REUSABLE CONFIG FRAGMENTS - Band alias maps

bands_sentinel = {
    "coastal": ["band_01","coastal_aerosol", "B01"],
    "blue": ["band_02", "blue", "B02"],
    "green": ["band_03", "green", "B03"],
    "red": ["band_04", "red", "B04"],
    "rededge1": ["band_05", "red_edge_1", "B05"],
    "rededge2": ["band_06", "red_edge_2", "B06"],
    "rededge3": ["band_07", "red_edge_3", "B07"],
    "nir": ["band_08", "nir", "nir_1", "B08"],
    "nir08": ["band_8a", "nir_narrow", "nir_2", "B8A"],
    "nir09": ["band_09", "water_vapour", "B09"],
    "swir16": ["band_11", "swir_1", "swir_16", "B11"],
    "swir22": ["band_12", "swir_2", "swir_22", "B12"],
    "aot": ["aerosol_optical_thickness", "AOT"],
    "wvp": ["scene_average_water_vapour", "WVP"],
    "scl": ["mask", "qa", "SCL"],
}


bands_s2_seasonal_ndvi = {
    "mediannan": ["mediannan"],
    "maxnan" : ["maxnan"],
    "meannan": ["meannan"],
    "rangenan" : ["rangenan"],
    "stdnan" : ["stdnan"],
    "sumnan" : ["sumnan"],
    "mask25" : ["mask25"],
    "validobs" : ["validobs"]
}

# REUSABLE CONFIG FRAGMENTS - Style definitions

# Examples of styles which are linear combinations of the available spectral bands.
style_rgb = {
    # Machine readable style name. (required.  Must be unique within a layer.)
    "name": "simple_rgb",
    # Human readable style title (required.  Must be unique within a layer.)
    "title": "Simple RGB",
    # Abstract - a longer human readable style description. (required. Must be unique within a layer.)
    "abstract": "Simple true-colour image, using the red, green and blue bands",
    # Components section is required for linear combination styles.
    # The component keys MUST be "red", "green" and "blue" (and optionally "alpha")
    "components": {
        "red": {
            # Band aliases may be used here.
            # Values are multipliers.  The should add to 1.0 for each component to preserve overall brightness levels,
            # but this is not enforced.
            "red": 1.0
        },
        "green": {
            "green": 1.0
        },
        "blue": {
            "blue": 1.0
        }
    },
    # The raw band value range to be compressed to an 8 bit range for the output image tiles.
    # Band values outside this range are clipped to 0 or 255 as appropriate.
    "scale_range": [0.0, 3000.0],
    # Legend section is optional for linear combination styles. If not supplied, no legend is displayed
    "legend": {
        # Whether or not to display a legend for this style.
        # Defaults to False for linear combination styles.
        "show_legend": True,
        # A legend cannot be auto-generated for a linear combination style, so a url pointing to
        # legend PNG image must be supplied if 'show_legend' is True.
        # Note that legend urls are proxied, not displayed directly to the user.
        "url": "http://example.com/custom_style_image.png"
    }

}

# Examples of non-linear colour-ramped styles.
style_s2_l2a_ndvi_seasonal = {
    "name": "s2_seasonal_ndvi",
    "title": "NDVI",
    "abstract": "Sentinel 2 Median Quarter Seasonal Composites",
    # The index function is continuous value from which the heat map is derived.
    #
    # Two formats are supported:
    # 1. A string containing a fully qualified path to a python function
    #    e.g. "index_function": "datacube_ows.ogc_utils.not_a_real_function_name",
    #
    # 2. A dict containing the following elements:
    #    a) "function" (required): A string containing the fully qualified path to a python function
    #    b) "args" (optional): An array of additional positional arguments that will always be passed to the function.
    #    c) "kwargs" (optional): An array of additional keyword arguments that will always be passed to the function.
    #    d) "mapped_bands" (optional): Boolean (defaults to False). If true, a band mapping function is passed
    #       to the function as a keyword argument named "band_mapper".  This is useful if you are passing band aliases
    #       to the function in the args or kwargs.  The band_mapper allows the index function to convert band aliases to
    #       to band names.
    #
    # The function is assumed to take one arguments, an xarray Dataset.  (Plus any additional
    # arguments required by the args and kwargs values in format 3, possibly including product_cfg.)
    "index_function": {
        "function": "datacube_ows.band_utils.single_band",
        "mapped_bands": True,
        "kwargs": {
            "band": "mediannan",
        }
    },
    # List of bands used by this style. The band may not be passed to the index function if it is not declared
    # here, resulting in an error.  Band aliases can be used here.
    "needed_bands": ["mediannan"],
    # The color ramp. Values between specified entries have both their alphas and colours
    # interpolated.
    "color_ramp": [
        # Any value less than the first entry will have colour and alpha of the first entry.
        # (i.e. in this example all negative values will be fully transparent (alpha=0.0).)
        {
            "value": -0.0,
            "color": "#8F3F20",
            "alpha": 0.0
        },
        {
            "value": 0.0,
            "color": "#8F3F20",
            "alpha": 1.0
        },
        {
            # do not have to defined alpha value
            # if no alpha is specified, alpha will default to 1.0 (fully opaque)
            "value": 100,
            "color": "#A35F18"
        },
        {
            "value": 200,
            "color": "#B88512"
        },
        {
            "value": 300,
            "color": "#CEAC0E"
        },
        {
            "value": 400,
            "color": "#E5D609"
        },
        {
            "value": 500,
            "color": "#FFFF0C"
        },
        {
            "value": 600,
            "color": "#C3DE09"
        },
        {
            "value": 700,
            "color": "#88B808"
        },
        {
            "value": 800,
            "color": "#529400"
        },
        {
            "value": 900,
            "color": "#237100"
        },
        # Values greater than the last entry will use the colour and alpha of the last entry.
        # (N.B. This will not happen for this example because it is normalised so that 1.0 is
        # maximum possible value.)
        {
            "value": 1000,
            "color": "#114D04"
        }
    ],
    # If true, the calculated index value for the pixel will be included in GetFeatureInfo responses.
    # Defaults to True.
    "include_in_feature_info": True,
    # Legend section is optional for non-linear colour-ramped styles.
    # If not supplied, a legend for the style will be automatically generated from the colour ramp.
    "legend": {
        # Whether or not to display a legend for this style.
        # Defaults to True for non-linear colour-ramped styles.
        "show_legend": True,
        # Instead of using the generated color ramp legend for the style, a URL to an PNG file can
        # be used instead.  If 'url' is not supplied, the generated legend is used.
        "url": "http://example.com/custom_style_image.png"
    }
}




# REUSABLE CONFIG FRAGMENTS - resource limit declarations

standard_resource_limits = {
    "wms": {
        # WMS/WMTS resource limits
        #
        # There are two independent resource limits applied to WMS/WMTS requests.  If either
        # limit is exceeded, then either the low-resolution summary product is used if one is defined, otherwise
        # indicative polygon showing the extent of the data is rendered.
        #
        # The fill-colour of the indicative polygons when either wms/wmts resource limits is exceeded.
        # Triplets (rgb) or quadruplets (rgba) of integers 0-255.
        #
        # (The fourth number in an rgba quadruplet represents opacity with 255 being fully opaque and
        # 0 being fully transparent.)
        #
        # Defaults to [150, 180, 200, 160]
        "zoomed_out_fill_colour": [150, 180, 200, 160],

        # WMS/WMTS Resource Limit 1: Min zoom factor
        #
        # The zoom factor is a dimensionless number calculated from the request in a way that is independent
        # of the CRS. A higher zoom factor corresponds to a more zoomed in view.
        #
        # If the zoom factor of the request is less than the minimum zoom factor (i.e. is zoomed out too far)
        # then indicative polygons are rendered instead of accessing the actual data.
        #
        # Defaults to 300.0
        "min_zoom_factor": 500.0,

        # Min zoom factor (above) works well for small-tiled requests, (e.g. 256x256 as sent by Terria).
        # However, for large-tiled requests (e.g. as sent by QGIS), large and intensive queries can still
        # go through to the datacube.
        #
        # max_datasets specifies a maximum number of datasets that a GetMap or GetTile request can retrieve.
        # Indicatative polygons are displayed if a request exceeds the limits imposed by EITHER max_dataset
        # OR min_zoom_factor.
        #
        # max_datasets should be set in conjunction with min_zoom_factor so that Terria style 256x256
        # tiled requests respond consistently - you never want to see a mixture of photographic tiles and polygon
        # tiles at a given zoom level.  i.e. max_datasets should be greater than the number of datasets
        # required for most intensive possible photographic query given the min_zoom_factor.
        # Note that the ideal value may vary from product to product depending on the size of the dataset
        # extents for the product.
        # Defaults to zero, which is interpreted as no dataset limit.
        "max_datasets": 0,
        # Dataset cache rules.
        #
        # The number of datasets accessed by a GetMap/GetTile/GetCoverage query can be used to control
        # the cache-control headers returned by the query.
        #
        # Special cases:
        #
        # 1. No dataset_cache_rules element: Never return a cache-control header
        # 2. dataset_cache_rules set to an empty list []:  Return no-cache for all queries.
        # 3. General case: refer to comments embedded in example below.
        "dataset_cache_rules": [
            # Where number of datasets less than the min_datasets element of the first cache rule  (0-3 in this example):
            #       no-cache.
            {
                # Where number of datasets greater than or equal to the min_datasets value for this rule AND
                # less than the min_datasets of the next rule (4-7 in this example)
                "min_datasets": 4, # Must be greater than zero.  Blank tiles (0 datasets) are NEVER cached
                # The cache-control max-age for this rule, in seconds.
                "max_age": 86400,  # 86400 seconds = 24 hours
            },
            {
                # Rules must be sorted in ascending order of min_datasets values.
                "min_datasets": 8,
                "max_age": 604800,  # 604800 seconds = 1 week
            },
            # If a resource limit is exceeded, no-cache applies.
            # Summarising the cache-control results for this example:
            # 0-3 datasets: no-cache
            # 4-7 datasets: max-age: 86400
            # 8-10 datasets: max-age: 604800
            # 11+ datasets:  no-cache (over-limit behaviour.  Low-resolution summary product or shaded polygons.)
        ]
    },
    "wcs": {
        # wcs::max_datasets is the WCS equivalent of wms::max_datasets.  The main requirement for setting this
        # value is to avoid gateway timeouts on overly large WCS requests (and reduce server load).
        #
        # Defaults to zero, which is interpreted as no dataset limit.
        "max_datasets": 0,
        # dataset_cache_rules can be set independently for WCS requests.  This example omits it, so
        # WCS GetCoverage requests will always return no cache-control header.
    }
}


# MAIN CONFIGURATION OBJECT

ows_cfg = {
    # Config entries in the "global" section apply to all services and all layers/coverages
    "global": {

        # These HTML headers are added to all responses
        # Optional, default {} - no added headers
        "response_headers": {
            "Access-Control-Allow-Origin": "*",  # CORS header (strongly recommended)
        },
        # Which web service(s) should be implemented by this instance
        # Optional, defaults: wms,wmts: True, wcs: False
        "services": {
            "wms": True,
            "wmts": True,
            "wcs": True
        },
        # Service title - appears e.g. in Terria catalog (required)
        "title": "ELBIOS - Open web-services for the Open Data Cube",
        # Service URL.
        # A list of fully qualified URLs that the service can return
        # in the GetCapabilities documents based on the requesting url
        "allowed_urls": ["http://54.188.16.1:8080", "http://127.0.0.1:8080/",
                          "http://54.188.16.1:8080/odc_ows"],
        # should be fully qualified
        "info_url": "http://opendatacube.org",
        # Abstract - longer description of the service (Note this text is used for both WM(T)S and WCS)
        # Optional - defaults to empty string.
        "abstract": """This web-service serves georectified raster data from our very own special Open Data Cube instance.""",
        # Keywords included for all services and products
        # Optional - defaults to empty list.
        "keywords": [
            "satellite",
            "elbios",
            "time-series",
        ],
        # Contact info.
        # Optional but strongly recommended - defaults to blank.
        "contact_info": {
            "person": "Firstname Surname",
            "organisation": "Acme Corporation",
            "position": "CIO (Chief Imaginary Officer)",
            "address": {
                "type": "postal",
                "address": "GPO Box 999",
                "city": "Metropolis",
                "state": "North Arcadia",
                "postcode": "12345",
                "country": "Elbonia",
            },
            "telephone": "+61 2 1234 5678",
            "fax": "+61 2 1234 6789",
            "email": "test@example.com",
        },
        # Attribution.
        #
        # This provides a way to identify the source of the data used in a WMS layer or layers.
        # This entire section is optional.  If provided, it is taken as the
        # default attribution for any layer that does not override it.
        "attribution": {
            # Attribution must contain at least one of ("title", "url" and "logo")
            # A human readable title for the attribution - e.g. the name of the attributed organisation
            "title": "Acme Satellites",
            # The associated - e.g. URL for the attributed organisation
            "url": "http://www.acme.com/satellites",
            # Logo image - e.g. for the attributed organisation
            "logo": {
                # Image width in pixels (optional)
                "width": 370,
                # Image height in pixels (optional)
                "height": 73,
                # URL for the logo image. (required if logo specified)
                "url": "https://www.acme.com/satellites/images/acme-370x73.png",
                # Image MIME type for the logo - should match type referenced in the logo url (required if logo specified.)
                "format": "image/png",
            }
        },
        # If fees are charged for the use of the service, these can be described here in free text.
        # If blank or not included, defaults to "none".
        "fees": "",
        # If there are constraints on access to the service, they can be described here in free text.
        # If blank or not included, defaults to "none".
        "access_constraints": "",
        # Supported co-ordinate reference systems. Any coordinate system supported by GDAL and Proj.4J can be used.
        # At least one CRS must be included.  At least one geographic CRS must be included if WCS is active.
        # WGS-84 (EPSG:4326) is strongly recommended, but not required.
        # Web Mercator (EPSG:3857) is strongly recommended, but is only required if WMTS is active.
        "published_CRSs": {
            "EPSG:3857": {  # Web Mercator
                "geographic": False,
                "horizontal_coord": "x",
                "vertical_coord": "y",
            },
            "EPSG:4326": {  # WGS-84
                "geographic": True,
                "vertical_coord_first": True
            },
            # "EPSG:32634": {  # VicGrid94 for delwp.vic.gov.au
            #    "geographic": False,
            #     "horizontal_coord": "x",
            #     "vertical_coord": "y",
            # },
            # "EPSG:32635": {  # GDA-94, internal representation
            #     "geographic": False,
            #     "horizontal_coord": "x",
            #     "vertical_coord": "y",
            # },
        },
    },   #### End of "global" section.

    # Config items in the "wms" section apply to the WMS service (and WMTS, which is implemented as a
    # thin wrapper to the WMS code unless stated otherwise) to all WMS/WMTS layers (unless over-ridden).
    "wms": {
        # Provide S3 data URL, bucket name for data_links in GetFeatureinfo responses
        # Note that this feature is currently restricted to data stored in AWS S3.
        # This feature is also fairly specialised to DEA requirements and may not be suited to more general use.
        # All Optional
        "s3_url": "http://data.au",
        "s3_bucket": "s3_bucket_name",
        "s3_aws_zone": "ap-southeast-2",
        # Max tile height/width for wms.  (N.B. Does not apply to WMTS)
        # Optional, defaults to 256x256
        "max_width": 512,
        "max_height": 512,

        # These define the AuthorityURLs.
        # They represent the authorities that define the "Identifiers" defined layer by layer below.
        # The spec allows AuthorityURLs to be defined anywhere on the Layer heirarchy, but datacube_ows treats them
        # as global entities.
        # Required if identifiers are to be declared for any layer.
        "authorities": {
            # The authorities dictionary maps names to authority urls.
            "auth": "https://authoritative-authority.com",
            "idsrus": "https://www.identifiers-r-us.com",
        }
    }, ####  End of "wms" section.

    # Config items in the "wmts" section apply to the WMTS service only.
    # Note that most items in the "wms" section apply to the WMTS service
    # as well as the WMS service.
    #
    # Config items in the "wmts" section apply to all WMTS layers. All
    # entries are optional and the entire section may be omitted.
    "wmts": {
        # Datacube-ows always supports the standard "Google Maps" style
        # EPSG:3857-based tile matrix set.
        # If you require a custom tile matrix set (or sets) you can
        # define them here.
        "tile_matrix_sets": {
            # Example custom tile matrix set
            # Vic Grid (EPSG:3111) GeoCortex compatible tile matrix set
            # The key is the identifier for the Tile Matrix Set in WMTS instance.
            "vicgrid": {
                # The CRS of the Tile Matrix Set
                "crs": "EPSG:3857",
                # The coordinates (in the CRS above) of the upper-left
                # corner of the tile matrix set.
                # My edit: Changed from https://epsg.io/map#srs=32634&x=502338.404794&y=3876270.085061&z=8&layer=streets
                # "matrix_origin": (1786000.0, 3081000.0),
                "matrix_origin": (330000.0, 4600000.0),
                # The size of tiles (must not exceed the WMS maximum tile size)
                "tile_size": (512, 512),
                # The scale denominators (as defined in the WMTS spec) for
                # the various zoom level from right out, to zoomed right in.
                "scale_set": [
                    7559538.928601667,
                    3779769.4643008336,
                    1889884.7321504168,
                    944942.3660752084,
                    472471.1830376042,
                    236235.5915188021,
                    94494.23660752083,
                    47247.11830376041,
                    23623.559151880207,
                    9449.423660752083,
                    4724.711830376042,
                    2362.355915188021,
                    1181.1779575940104,
                    755.9538928601667,
                ],
                # Defaults to (0,0), which means the first tile matrix
                # will have 1 tile (1x1), then doubling each time
                # (then 2x2, 4x4, 8x8, 16x16, etc.)
                #
                # (1, 0) means the width  of the first tile matrix has
                # is 2**1 = 2
                # So tiles side by side (2x1) (then 4x2, 8x4, 16x8, etc.)
                "matrix_exponent_initial_offsets": (1, 0),
            },
        }
    },

    # Config items in the "wcs" section apply to the WCS service to all WCS coverages
    # (unless over-ridden).
    "wcs": {
        # Supported WCS formats
        # NetCDF and GeoTIFF work "out of the box".  Other formats will require writing a Python function
        # to do the rendering.
        "formats": {
            # Key is the format name, as used in DescribeCoverage XML
            "GeoTIFF": {
                # Writing your own renderers is not documented.
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_tiff",
                    "2": "datacube_ows.wcs2_utils.get_tiff",
                },
                # The MIME type of the image, as used in the Http Response.
                "mime": "image/geotiff",
                # The file extension to add to the filename.
                "extension": "tif",
                # Whether or not the file format supports multiple time slices.
                "multi-time": False
            },
            "netCDF": {
                "renderers": {
                    "1": "datacube_ows.wcs1_utils.get_netcdf",
                    "2": "datacube_ows.wcs2_utils.get_netcdf",
                },
                "mime": "application/x-netcdf",
                "extension": "nc",
                "multi-time": True,
            }
        },
        # The wcs:native_format must be declared in wcs:formats dict above.
        # Maybe over-ridden at the named layer (i.e. coverage)
        # level.
        "native_format": "GeoTIFF",
    }, ###### End of "wcs" section

    # Products published by this datacube_ows instance.
    # The layers section is a list of layer definitions.  Each layer may be either:
    # 1) A folder-layer.  Folder-layers are not named and can contain a list of child layers.  Folder-layers are
    #    only used by WMS and WMTS - WCS does not support a hierarchical index of coverages.
    # 2) A mappable named layer that can be requested in WMS GetMap or WMTS GetTile requests.  A mappable named layer
    #    is also a coverage, that may be requested in WCS DescribeCoverage or WCS GetCoverage requests.
    # "layers": [
    #     {
    #         # NOTE: This layer is a folder - it is NOT "named layer" that can be selected in GetMap requests
    #         "title": "ELBIOS Products",
    #         "abstract": "NDVI COmposites",
    #         "keywords": [
    #             "sentinel2",
    #             "ndvi",
    #         ],
    #         "layers": [
    #             {
    #                 # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
    #                 "title": "Near Real-Time images from Sentinel-2 Satellites",
    #                 "abstract": "Imagery from the ESA Sentinel2 Satellites",
    #                 "name": "s2_seasonal_ndvi",
    #                 # Multi-product layers merge two separate datacube products with similar metadata (i.e.
    #                 # projections, bands, pixel quality band format, etc.)
    #                 "multi_product": False,
    #                 # For multi-product layers, use "product_names" for the list of constituent ODC products.
    #                 "product_name": ["s2_seasonal_ndvi"],
    #                 "bands": bands_s2_seasonal_ndvi,
    #                 "resource_limits": standard_resource_limits,
    #                 # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
    #                 "dynamic": True,
    #                 "native_crs": "EPSG:32634",
    #                 "native_resolution": [10.0, 10.0],
    #                 # "flags": {
    #                 #     "band": "mask25",
    #                 #     "ignore_time": False,
    #                 #     "ignore_info_flags": [],
    #                 #     "manual_merge": False,
    #                 # },
    #                 "image_processing": {
    #                     "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
    #                     "always_fetch_bands": [],
    #                     "fuse_func": None,
    #                     "manual_merge": False,
    #                     "apply_solar_corrections": False,
    #                 },
    #                 # "wcs": {
    #                 #     "default_bands": ["red", "green", "blue"],
    #                 # },
    #                 # "identifiers": {
    #                 #     "auth": "s2_nrt_multi",
    #                 # },
    #                 # "urls": {
    #                 #     "features": [
    #                 #         {
    #                 #             "url": "http://domain.tld/path/to/page.html",
    #                 #             "format": "text/html"
    #                 #         }
    #                 #     ],
    #                 #     "data": [
    #                 #         {
    #                 #             "url": "http://abc.xyz/data-link.xml",
    #                 #             "format": "application/xml"
    #                 #         }
    #                 #     ]
    #                 # },
    #                 "styling": {
    #                     "default_style": "s2_seasonal_ndvi",
    #                     "styles": [style_s2_l2a_ndvi_seasonal],
    #                 }
    #             } ##### End of sentinel2_nrt multi-product definition
    #         ],
    #     },   #### End of Sentinel-2 folder
    # ]  ##### End of "layers" list.
    "layers": [
        {
            # NOTE: This layer is a folder - it is NOT "named layer" that can be selected in GetMap requests
            "title": "ELBIOS Products",
            "abstract": "All products",
            "keywords": [
                "sentinel2",
                "ndvi",
            ],
            "layers": [
                {
                    # NOTE: This layer IS a mappable "named layer" that can be selected in GetMap requests
                    "title": "Near Real-Time images from Sentinel-2 Satellites",
                    "abstract": "Imagery from the ESA Sentinel2 Satellites",
                    "name": "s2_l2a",
                    # Multi-product layers merge two separate datacube products with similar metadata (i.e.
                    # projections, bands, pixel quality band format, etc.)
                    "multi_product": False,
                    # For multi-product layers, use "product_names" for the list of constituent ODC products.
                    "product_name": "s2_l2a",
                    "bands": bands_sentinel,
                    "resource_limits": standard_resource_limits,
                    # Near Real Time datasets are being regularly updated - do not cache ranges in memory.
                    "dynamic": True,
                    "native_crs": "EPSG:3577",
                    "native_resolution": [10.0, 10.0],
                    # "flags": {
                    #     "band": "mask25",
                    #     "ignore_time": False,
                    #     "ignore_info_flags": [],
                    #     "manual_merge": False,
                    # },
                    "image_processing": {
                        "extent_mask_func": "datacube_ows.ogc_utils.mask_by_val",
                        "always_fetch_bands": [],
                        "fuse_func": None,
                        "manual_merge": False,
                        "apply_solar_corrections": False,
                    },
                    # "wcs": {
                    #     "default_bands": ["red", "green", "blue"],
                    # },
                    # "identifiers": {
                    #     "auth": "s2_nrt_multi",
                    # },
                    # "urls": {
                    #     "features": [
                    #         {
                    #             "url": "http://domain.tld/path/to/page.html",
                    #             "format": "text/html"
                    #         }
                    #     ],
                    #     "data": [
                    #         {
                    #             "url": "http://abc.xyz/data-link.xml",
                    #             "format": "application/xml"
                    #         }
                    #     ]
                    # },
                    "default_time": "latest",
                    "styling": {
                        "default_style": "simple_rgb",
                        "styles": [style_rgb],
                    }
                } ##### End of sentinel2_nrt multi-product definition
            ],
        },   #### End of Sentinel-2 folder
    ]  ##### End of "layers" list.
} #### End of example configuration object
