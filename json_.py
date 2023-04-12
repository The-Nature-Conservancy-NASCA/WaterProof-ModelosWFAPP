import json, os

#Rutas
PathInput   = os.path.join(os.path.split(os.getcwd())[0], 'DATA', '02-RIOS')
PathInput1  = os.path.join(os.path.split(os.getcwd())[0])
PathOutput  = os.path.join(os.path.split(os.getcwd())[0], 'RESULTS', '07-RIOS')


working_path            = PathOutput
output_path             = PathOutput
hydro_path              = PathOutput



lulc_raster_uri         = os.path.join(PathInput, 'LULC.tif') # LandCover
rios_coeff_table        = os.path.join(PathInput, 'Biophysical_Table.csv') # Parametros biofisicos
dem_raster_uri          = os.path.join(PathInput, 'DEM.tif') # DEM
precip_month_raster_uri = os.path.join(PathInput, 'P_Peak.tif') # 
soil_texture_raster_uri = os.path.join(PathInput, 'Texture_Index.tif')
precip_annual_raster_uri= os.path.join(PathInput, 'P_Year.tif')
erosivity_raster_uri    = os.path.join(PathInput, 'R.tif')
erodibility_raster_uri  = os.path.join(PathInput, 'K.tif')
soil_depth_raster_uri   = os.path.join(PathInput, 'Soil_Depth.tif')
aet_raster_uri          = os.path.join(PathInput, 'ETO.tif')
ETR_raster_uri          = os.path.join(PathInput, 'ETR.tif') # Evapotranspiracion real anual
Beneficiaries           = os.path.join(PathInput, 'Beneficiaries.tif') # Beneficiarios
Aquifer                 = os.path.join(PathInput, 'Aquifer_Area.tif') # Zonas de recarga
suffix                  = r'AF_1'
aoi_shape_uri           = os.path.join(PathInput, 'Basin','Basin.shp',)
streams_raster_uri      = os.path.join(PathInput, 'Stream.tif')

# Salidas de rios_preprocessor - Flujo base
baseflow_downslope      = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','erosion_downslope_retention_index_' + suffix + '.tif')
baseflow_slope          = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','flood_slope_index_' + suffix + '.tif')
baseflow_upslope        = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','gwater_upslope_source_' + suffix + '.tif')

# Salidas de rios_preprocessor - Recarga de aguas subterraneas
gw_downslope            = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','erosion_downslope_retention_index_' + suffix + '.tif')
gw_slope                = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','flood_slope_index_' + suffix + '.tif')
gw_upslope              = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','gwater_upslope_source_' + suffix + '.tif')

# Salidas de rios_preprocessor - Mitigacion de inundaciones
flood_downslope         = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','flood_downslope_retention_index_' + suffix + '.tif')
flood_riparian          = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','flood_riparian_index_' + suffix + '.tif')
flood_slope             = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','flood_slope_index_' + suffix + '.tif')
flood_upslope           = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','flood_upslope_source_' + suffix + '.tif')

# Salidas de rios_preprocessor - Control de erosion en reservorios y sistemas de agua potable
erosion_downslope       = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','erosion_downslope_retention_index_' + suffix + '.tif')
erosion_riparian        = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','erosion_riparian_index_' + suffix + '.tif')
erosion_upslope         = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','erosion_upslope_source_' + suffix + '.tif')

# Salidas de rios_preprocessor - Nutrientes fosforo
phosphorus_downslope    = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','phosphorus_downslope_retention_index_' + suffix + '.tif')
phosphorus_riparian     = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','phosphorus_riparian_index_' + suffix + '.tif')
phosphorus_upslope      = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','phosphorus_upslope_source_' + suffix + '.tif')

# Salidas de rios_preprocessor - Nutrientes nitrogeno
nitrogen_downslope      = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','nitrogen_downslope_retention_index_' + suffix + '.tif')
nitrogen_riparian       = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','nitrogen_riparian_index_' + suffix + '.tif')
nitrogen_upslope        = os.path.join(PathInput1, 'RESULTS','06-Pre_Processing_RIOS','nitrogen_upslope_source_' + suffix + '.tif')

args = {
        u'activities': {
            u'agroforestry': {
                u'measurement_unit': u'area',
                u'measurement_value': 1000000.0,
                u'unit_cost': 1000.0,
            },
            u'grass_strips': {
                u'measurement_unit': u'area',
                u'measurement_value': 1000000.0,
                u'unit_cost': 1000.0,
            },
            u'riparian_mgmt': {
                u'measurement_unit': u'area',
                u'measurement_value': 1000000.0,
                u'unit_cost': 1000.0,
            },
            u'terracing': {
                u'measurement_unit': u'area',
                u'measurement_value': 1000000.0,
                u'unit_cost': 1000.0,
            },
        },
        u'activity_shapefiles': [],
        u'budget_config': {
            u'activity_budget': {
                u'agroforestry': {
                    u'budget_amount': 100.0,
                },
                u'grass_strips': {
                    u'budget_amount': 100.0,
                },
                u'riparian_mgmt': {
                    u'budget_amount': 100.0,
                },
                u'terracing': {
                    u'budget_amount': 100.0,
                },
            },
            u'floating_budget': 3000,
            u'if_left_over': u'Report remainder',
            u'years_to_spend': 100,
        },
        u'lulc_activity_potential_map': {
            1: [],
            2: [],
            3: [
                u'agroforestry',
            ],
            4: [
                u'agroforestry',
                u'grass_strips',
                u'terracing',
            ],
            5: [],
            6: [
                u'grass_strips',
                u'terracing',
            ],
            7: [],
        },
        u'lulc_coefficients_table_uri': rios_coeff_table,
        u'lulc_uri': lulc_raster_uri,
        u'objectives': {
            u'baseflow': {
                u'factors': {
                    u'Actual Evapotranspiration': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': ETR_raster_uri,
                    },
                    u'Annual Average Rainfall': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': precip_annual_raster_uri,
                    },
                    u'Beneficiaries': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Beneficiaries,
                    },
                    u'Downslope retention index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': baseflow_downslope,
                    },
                    u'Land Use Land Cover Retention at pixel': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Rough_Rank',
                        },
                    },
                    u'Slope Index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': baseflow_slope,
                    },
                    u'Soil Texture Index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_texture_raster_uri,
                    },
                    u'Soil depth': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_depth_raster_uri,
                    },
                    u'Upslope source': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': baseflow_upslope,
                    },
                    u'Vegetative Cover Index': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Cover_Rank',
                        },
                    },
                },
                u'priorities': {
                    u'agricultural_vegetation_managment': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'ditching': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'fertilizer_management': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'keep_native_vegetation': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': 0.5,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': 0.2,
                    },
                    u'pasture_management': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'revegetation_assisted': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'revegetation_unassisted': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                },
                u'rios_model_type': u'rios_tier_0',
            },
            u'erosion_drinking_control': {
                u'factors': {
                    u'Beneficiaries': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Beneficiaries,
                    },
                    u'Downslope retention index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosion_downslope,
                    },
                    u'On-pixel retention': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Sed_Ret',
                        },
                    },
                    u'On-pixel source': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Sed_Exp',
                        },
                    },
                    u'Rainfall erosivity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosivity_raster_uri,
                    },
                    u'Riparian continuity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosion_riparian,
                    },
                    u'Soil depth': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_depth_raster_uri,
                    },
                    u'Soil erodibility': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erodibility_raster_uri,
                    },
                    u'Upslope source': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosion_upslope,
                    },
                },
                u'priorities': {
                    u'agricultural_vegetation_managment': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'ditching': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'fertilizer_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'keep_native_vegetation': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': 0.5,
                        u'On-pixel source': u'~0.25',
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'pasture_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_assisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_unassisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                },
                u'rios_model_type': u'rios_tier_0',
            },
            u'erosion_reservoir_control': {
                u'factors': {
                    u'Beneficiaries': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Beneficiaries,
                    },
                    u'Downslope retention index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosion_downslope,
                    },
                    u'On-pixel retention': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Sed_Ret',
                        },
                    },
                    u'On-pixel source': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Sed_Exp',
                        },
                    },
                    u'Rainfall erosivity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosivity_raster_uri,
                    },
                    u'Riparian continuity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosion_riparian,
                    },
                    u'Soil depth': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_depth_raster_uri,
                    },
                    u'Soil erodibility': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erodibility_raster_uri,
                    },
                    u'Upslope source': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosion_upslope,
                    },
                },
                u'priorities': {
                    u'agricultural_vegetation_managment': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'ditching': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'fertilizer_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'keep_native_vegetation': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': 0.5,
                        u'On-pixel source': u'~0.25',
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'pasture_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_assisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_unassisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                },
                u'rios_model_type': u'rios_tier_0',
            },
            u'flood_mitigation_impact': {
                u'factors': {
                    u'Beneficiaries': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Beneficiaries,
                    },
                    u'Downslope retention index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': flood_downslope,
                    },
                    u'Land Use Land Cover Retention at pixel': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Rough_Rank',
                        },
                    },
                    u'Rainfall depth': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosivity_raster_uri,
                    },
                    u'Riparian continuity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': flood_riparian,
                    },
                    u'Slope Index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': flood_slope,
                    },
                    u'Soil Texture Index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_texture_raster_uri,
                    },
                    u'Upslope source': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': flood_upslope,
                    },
                    u'Vegetative Cover Index': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Cover_Rank',
                        },
                    },
                },
                u'priorities': {
                    u'agricultural_vegetation_managment': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Rainfall depth': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Slope Index': 0.25,
                        u'Soil Texture Index': 0.25,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.25',
                    },
                    u'ditching': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Rainfall depth': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Slope Index': 0.25,
                        u'Soil Texture Index': 0.25,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.25',
                    },
                    u'fertilizer_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Rainfall depth': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Slope Index': 0.25,
                        u'Soil Texture Index': 0.25,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.25',
                    },
                    u'keep_native_vegetation': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': 0.5,
                        u'Rainfall depth': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Slope Index': 0.25,
                        u'Soil Texture Index': 0.25,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': 0.25,
                    },
                    u'pasture_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Rainfall depth': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Slope Index': 0.25,
                        u'Soil Texture Index': 0.25,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.25',
                    },
                    u'revegetation_assisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Rainfall depth': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Slope Index': 0.25,
                        u'Soil Texture Index': 0.25,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.25',
                    },
                    u'revegetation_unassisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Rainfall depth': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Slope Index': 0.25,
                        u'Soil Texture Index': 0.25,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.25',
                    },
                },
                u'rios_model_type': u'rios_tier_0',
            },
            u'groundwater_recharge': {
                u'factors': {
                    u'Actual Evapotranspiration': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': ETR_raster_uri,
                    },
                    u'Annual Average Rainfall': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': precip_annual_raster_uri,
                    },
                    u'Beneficiaries': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Beneficiaries,
                    },
                    u'Downslope retention index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': gw_downslope,
                    },
                    u'Land Use Land Cover Retention at pixel': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Rough_Rank',
                        },
                    },
                    u'Preferential Recharge Areas': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Aquifer,
                    },
                    u'Slope Index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': gw_slope,
                    },
                    u'Soil Texture Index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_texture_raster_uri,
                    },
                    u'Soil depth': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_depth_raster_uri,
                    },
                    u'Upslope source': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': gw_upslope,
                    },
                    u'Vegetative Cover Index': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'Cover_Rank',
                        },
                    },
                },
                u'priorities': {
                    u'agricultural_vegetation_managment': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Preferential Recharge Areas': 1.0,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'ditching': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Preferential Recharge Areas': 1.0,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'fertilizer_management': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Preferential Recharge Areas': 1.0,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'keep_native_vegetation': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': 0.5,
                        u'Preferential Recharge Areas': 1.0,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': 0.2,
                    },
                    u'pasture_management': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Preferential Recharge Areas': 1.0,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'revegetation_assisted': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Preferential Recharge Areas': 1.0,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                    u'revegetation_unassisted': {
                        u'Actual Evapotranspiration': u'~0.2',
                        u'Annual Average Rainfall': 0.2,
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'Land Use Land Cover Retention at pixel': u'~0.5',
                        u'Preferential Recharge Areas': 1.0,
                        u'Slope Index': u'~0.2',
                        u'Soil Texture Index': u'~0.2',
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                        u'Vegetative Cover Index': u'~0.2',
                    },
                },
                u'rios_model_type': u'rios_tier_0',
            },
            u'nutrient_retention_nitrogen': {
                u'factors': {
                    u'Beneficiaries': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Beneficiaries,
                    },
                    u'Downslope retention index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': nitrogen_downslope,
                    },
                    u'On-pixel retention': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'N_Ret',
                        },
                    },
                    u'On-pixel source': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'N_Exp',
                        },
                    },
                    u'Riparian continuity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': nitrogen_riparian,
                    },
                    u'Soil depth': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_depth_raster_uri,
                    },
                    u'Upslope source': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': nitrogen_upslope,
                    },
                },
                u'priorities': {
                    u'agricultural_vegetation_managment': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.5,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                    },
                    u'ditching': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.5,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                    },
                    u'fertilizer_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.5,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                    },
                    u'keep_native_vegetation': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': 0.5,
                        u'On-pixel source': u'~0.5',
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                    },
                    u'pasture_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.5,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_assisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.5,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_unassisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.5,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.5,
                        u'Upslope source': 1.0,
                    },
                },
                u'rios_model_type': u'rios_tier_0',
            },
            u'nutrient_retention_phosphorus': {
                u'factors': {
                    u'Beneficiaries': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': Beneficiaries,
                    },
                    u'Downslope retention index': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': phosphorus_downslope,
                    },
                    u'On-pixel retention': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'P_Ret',
                        },
                    },
                    u'On-pixel source': {
                        u'bins': {
                            u'key_field': u'lulc_general',
                            u'raster_uri': lulc_raster_uri,
                            u'uri': rios_coeff_table,
                            u'value_field': u'P_Exp',
                        },
                    },
                    u'Rainfall erosivity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erosivity_raster_uri,
                    },
                    u'Riparian continuity': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': phosphorus_riparian,
                    },
                    u'Soil depth': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': soil_depth_raster_uri,
                    },
                    u'Soil erodibility': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': erodibility_raster_uri,
                    },
                    u'Upslope source': {
                        u'bins': {
                            'interpolation': 'linear',
                            'inverted': False,
                            'type': 'interpolated',
                        },
                        u'raster_uri': phosphorus_upslope,
                    },
                },
                u'priorities': {
                    u'agricultural_vegetation_managment': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'ditching': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'fertilizer_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'keep_native_vegetation': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': 0.5,
                        u'On-pixel source': u'~0.25',
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'pasture_management': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_assisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                    u'revegetation_unassisted': {
                        u'Beneficiaries': 1.0,
                        u'Downslope retention index': u'~1',
                        u'On-pixel retention': u'~0.5',
                        u'On-pixel source': 0.25,
                        u'Rainfall erosivity': 0.25,
                        u'Riparian continuity': 0.5,
                        u'Soil depth': 0.25,
                        u'Soil erodibility': 0.25,
                        u'Upslope source': 1.0,
                    },
                },
                u'rios_model_type': u'rios_tier_0',
            },
        },
        u'open_html_on_completion': True,
        u'priorities': {
            u'agricultural_vegetation_managment': {
                u'baseflow': 1.0,
                u'erosion_drinking_control': 1.0,
                u'erosion_reservoir_control': 1.0,
                u'flood_mitigation_impact': 1.0,
                u'groundwater_recharge': 1.0,
                u'nutrient_retention_nitrogen': 1.0,
                u'nutrient_retention_phosphorus': 1.0,
            },
            u'ditching': {
                u'baseflow': 1.0,
                u'erosion_drinking_control': 1.0,
                u'erosion_reservoir_control': 1.0,
                u'flood_mitigation_impact': 1.0,
                u'groundwater_recharge': 1.0,
                u'nutrient_retention_nitrogen': 1.0,
                u'nutrient_retention_phosphorus': 1.0,
            },
            u'fertilizer_management': {
                u'baseflow': 1.0,
                u'erosion_drinking_control': 1.0,
                u'erosion_reservoir_control': 1.0,
                u'flood_mitigation_impact': 1.0,
                u'groundwater_recharge': 1.0,
                u'nutrient_retention_nitrogen': 1.0,
                u'nutrient_retention_phosphorus': 1.0,
            },
            u'keep_native_vegetation': {
                u'baseflow': 1.0,
                u'erosion_drinking_control': 1.0,
                u'erosion_reservoir_control': 1.0,
                u'flood_mitigation_impact': 1.0,
                u'groundwater_recharge': 1.0,
                u'nutrient_retention_nitrogen': 1.0,
                u'nutrient_retention_phosphorus': 1.0,
            },
            u'pasture_management': {
                u'baseflow': 1.0,
                u'erosion_drinking_control': 1.0,
                u'erosion_reservoir_control': 1.0,
                u'flood_mitigation_impact': 1.0,
                u'groundwater_recharge': 1.0,
                u'nutrient_retention_nitrogen': 1.0,
                u'nutrient_retention_phosphorus': 1.0,
            },
            u'revegetation_assisted': {
                u'baseflow': 1.0,
                u'erosion_drinking_control': 1.0,
                u'erosion_reservoir_control': 1.0,
                u'flood_mitigation_impact': 1.0,
                u'groundwater_recharge': 1.0,
                u'nutrient_retention_nitrogen': 1.0,
                u'nutrient_retention_phosphorus': 1.0,
            },
            u'revegetation_unassisted': {
                u'baseflow': 1.0,
                u'erosion_drinking_control': 1.0,
                u'erosion_reservoir_control': 1.0,
                u'flood_mitigation_impact': 1.0,
                u'groundwater_recharge': 1.0,
                u'nutrient_retention_nitrogen': 1.0,
                u'nutrient_retention_phosphorus': 1.0,
            },
        },
        u'results_suffix': 'Dummy',
        u'transition_map': {
            u'agricultural_vegetation_managment': {
                u'agroforestry': 1.0,
                u'grass_strips': 1.0,
                u'riparian_mgmt': 1.0,
                u'terracing': 1.0,
            },
            u'ditching': {
                u'agroforestry': 1.0,
                u'grass_strips': 1.0,
                u'riparian_mgmt': 1.0,
                u'terracing': 1.0,
            },
            u'fertilizer_management': {
                u'agroforestry': 1.0,
                u'grass_strips': 1.0,
                u'riparian_mgmt': 1.0,
                u'terracing': 1.0,
            },
            u'keep_native_vegetation': {
                u'agroforestry': 1.0,
                u'grass_strips': 1.0,
                u'riparian_mgmt': 1.0,
                u'terracing': 1.0,
            },
            u'pasture_management': {
                u'agroforestry': 1.0,
                u'grass_strips': 1.0,
                u'riparian_mgmt': 1.0,
                u'terracing': 1.0,
            },
            u'revegetation_assisted': {
                u'agroforestry': 1.0,
                u'grass_strips': 1.0,
                u'riparian_mgmt': 1.0,
                u'terracing': 1.0,
            },
            u'revegetation_unassisted': {
                u'agroforestry': 1.0,
                u'grass_strips': 1.0,
                u'riparian_mgmt': 1.0,
                u'terracing': 1.0,
            },
        },
        u'transition_types': [
            {
                u'file_name': u'agricultural_vegetation_managment',
                u'id': u'trans4',
                u'label': u'Agricultural \nvegetation \nmanagement',
                u'transition_type': u'agriculture',
            },
            {
                u'file_name': u'ditching',
                u'id': u'trans5',
                u'label': u'Ditching',
                u'transition_type': u'agriculture',
            },
            {
                u'file_name': u'fertilizer_management',
                u'id': u'trans6',
                u'label': u'Fertilizer \nmanagement',
                u'transition_type': u'agriculture',
            },
            {
                u'file_name': u'keep_native_vegetation',
                u'id': u'trans1',
                u'label': u'Keep native \nvegetation',
                u'transition_type': u'protection',
            },
            {
                u'file_name': u'pasture_management',
                u'id': u'trans7',
                u'label': u'Pasture \nmanagement',
                u'transition_type': u'agriculture',
            },
            {
                u'file_name': u'revegetation_assisted',
                u'id': u'trans3',
                u'label': u'Revegetation \n(assisted)',
                u'transition_type': u'restoration',
            },
            {
                u'file_name': u'revegetation_unassisted',
                u'id': u'trans2',
                u'label': u'Revegetation \n(unassisted)',
                u'transition_type': u'restoration',
            },
        ],
        u'workspace_dir': PathOutput,
}


app_json = json.dumps(args)
print(app_json)

with open('data.json', 'w') as outfile:
    json.dump(app_json, outfile)