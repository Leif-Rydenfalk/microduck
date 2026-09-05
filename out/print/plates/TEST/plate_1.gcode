; HEADER_BLOCK_START
; BambuStudio 02.08.02.61
; model printing time: 15m 49s; total estimated time: 16m 9s
; total layer number: 74
; total filament length [mm] : 448.17
; total filament volume [cm^3] : 1077.98
; total filament weight [g] : 1.35
; filament_density: 1.25
; filament_diameter: 1.75
; max_z_height: 14.80
; filament: 1
; support_material_on_wipe_tower: 0
; HEADER_BLOCK_END

; CONFIG_BLOCK_START
; accel_to_decel_enable = 0
; accel_to_decel_factor = 50%
; activate_air_filtration = 0
; additional_cooling_fan_speed = 0
; additional_fan_full_speed_layer = 0
; alternate_extra_wall = 0
; ams_filament_load_time_ams = 0
; ams_filament_load_time_ams_lite = 0
; ams_filament_load_time_n3f_s = 0
; ams_filament_unload_time_ams = 0
; ams_filament_unload_time_ams_lite = 0
; ams_filament_unload_time_n3f_s = 0
; apply_scarf_seam_on_circles = 1
; auxiliary_fan = 1
; avoid_crossing_wall_includes_support = 0
; bed_custom_model = 
; bed_custom_texture = 
; bed_exclude_area = 0x0,18x0,18x28,0x28
; bed_heat_soak_area = 
; bed_temperature_formula = by_first_filament
; before_layer_change_gcode = 
; best_object_pos = 0.5,0.5
; bottom_color_penetration_layers = 3
; bottom_shell_layers = 3
; bottom_shell_thickness = 0
; bottom_surface_density = 100%
; bottom_surface_pattern = monotonic
; bridge_angle = 0
; bridge_flow = 1
; bridge_no_support = 0
; bridge_speed = 50
; brim_object_gap = 0.1
; brim_type = auto_brim
; brim_width = 5
; chamber_temperatures = 0
; change_filament_gcode = M620 S[next_extruder]A\nM204 S9000\nG1 Z{max_layer_z + 3.0} F1200\n\nG1 X70 F21000\nG1 Y245\nG1 Y265 F3000\nM400\nM106 P1 S0\nM106 P2 S0\n{if old_filament_temp > 142 && next_extruder < 255}\nM104 S[old_filament_temp]\n{endif}\nG1 X90 F3000\nG1 Y255 F4000\nG1 X100 F5000\nG1 X120 F15000\n\nG1 X20 Y50 F21000\nG1 Y-3\n{if toolchange_count == 2}\n; get travel path for change filament\nM620.1 X[travel_point_1_x] Y[travel_point_1_y] F21000 P0\nM620.1 X[travel_point_2_x] Y[travel_point_2_y] F21000 P1\nM620.1 X[travel_point_3_x] Y[travel_point_3_y] F21000 P2\n{endif}\nM620.1 E F[old_filament_e_feedrate] T{nozzle_temperature_range_high[previous_extruder]}\nT[next_extruder]\nM620.1 E F[new_filament_e_feedrate] T{nozzle_temperature_range_high[next_extruder]}\n\n{if next_extruder < 255}\nM400\n\nG92 E0\n{if flush_length_1 > 1}\n; FLUSH_START\n; always use highest temperature to flush\nM400\nM109 S[nozzle_temperature_range_high]\n{if flush_length_1 > 23.7}\nG1 E23.7 F{old_filament_e_feedrate} ; do not need pulsatile flushing for start part\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{old_filament_e_feedrate}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}\nG1 E{(flush_length_1 - 23.7) * 0.02} F50\nG1 E{(flush_length_1 - 23.7) * 0.23} F{new_filament_e_feedrate}\n{else}\nG1 E{flush_length_1} F{old_filament_e_feedrate}\n{endif}\n; FLUSH_END\nG1 E-[old_retract_length_toolchange] F1800\nG1 E[old_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_2 > 1}\n; FLUSH_START\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\nG1 E{flush_length_2 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_2 * 0.02} F50\n; FLUSH_END\nG1 E-[new_retract_length_toolchange] F1800\nG1 E[new_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_3 > 1}\n; FLUSH_START\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\nG1 E{flush_length_3 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_3 * 0.02} F50\n; FLUSH_END\nG1 E-[new_retract_length_toolchange] F1800\nG1 E[new_retract_length_toolchange] F300\n{endif}\n\n{if flush_length_4 > 1}\n; FLUSH_START\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\nG1 E{flush_length_4 * 0.18} F{new_filament_e_feedrate}\nG1 E{flush_length_4 * 0.02} F50\n; FLUSH_END\n{endif}\n; FLUSH_START\nM400\nM109 S[new_filament_temp]\nG1 E2 F{new_filament_e_feedrate} ;Compensate for filament spillage during waiting temperature\n; FLUSH_END\nM400\nG92 E0\nG1 E-[new_retract_length_toolchange] F1800\nM106 P1 S255\nM400 S3\nG1 X80 F15000\nG1 X60 F15000\nG1 X80 F15000\nG1 X60 F15000; shake to put down garbage\n\nG1 X70 F5000\nG1 X90 F3000\nG1 Y255 F4000\nG1 X100 F5000\nG1 Y265 F5000\nG1 X70 F10000\nG1 X100 F5000\nG1 X70 F10000\nG1 X100 F5000\nG1 X165 F15000; wipe and shake\nG1 Y256 ; move Y to aside, prevent collision\nM400\nG1 Z{max_layer_z + 3.0} F3000\n{if layer_z <= (initial_layer_print_height + 0.001)}\nM204 S[initial_layer_acceleration]\n{else}\nM204 S[default_acceleration]\n{endif}\n{else}\nG1 X[x_after_toolchange] Y[y_after_toolchange] Z[z_after_toolchange] F12000\n{endif}\nM621 S[next_extruder]A
; circle_compensation_manual_offset = 0
; circle_compensation_speed = 200
; close_additional_fan_first_x_layers = 3
; close_fan_the_first_x_layers = 3
; compatible_printers_condition = 
; complete_print_exhaust_fan_speed = 70
; cool_plate_temp = 0
; cool_plate_temp_initial_layer = 0
; cooling_filter_enabled = 0
; cooling_perimeter_transition_distance = 10
; cooling_slowdown_logic = uniform_cooling
; counter_coef_1 = 0
; counter_coef_2 = 0.008
; counter_coef_3 = -0.041
; counter_limit_max = 0.033
; counter_limit_min = -0.035
; counterbore_hole_bridging = none
; curr_bed_type = Textured PEI Plate
; default_acceleration = 10000
; default_ams_type = -1
; default_filament_colour = ""
; default_filament_profile = "Bambu PLA Basic @BBL X1C"
; default_jerk = 0
; default_nozzle_volume_type = Standard
; default_print_profile = 0.20mm Standard @BBL X1C
; deretraction_speed = 30
; detect_floating_vertical_shell = 1
; detect_narrow_internal_solid_infill = 1
; detect_overhang_wall = 1
; detect_thin_wall = 0
; diameter_limit = 50
; different_settings_to_system = ;;
; draft_shield = disabled
; during_print_exhaust_fan_speed = 70
; elefant_foot_compensation = 0.15
; embedding_wall_into_infill = 0
; enable_arc_fitting = 1
; enable_circle_compensation = 0
; enable_filament_dynamic_map = 0
; enable_height_slowdown = 0
; enable_long_retraction_when_cut = 2
; enable_mixed_color_sublayer = 0
; enable_order_independent_overlap_carving = 0
; enable_overhang_bridge_fan = 1
; enable_overhang_speed = 1
; enable_pre_heating = 0
; enable_pressure_advance = 0
; enable_prime_tower = 1
; enable_support = 0
; enable_support_ironing = 0
; enable_tower_interface_features = 0
; enable_wrapping_detection = 0
; enforce_support_layers = 0
; eng_plate_temp = 70
; eng_plate_temp_initial_layer = 70
; ensure_vertical_shell_thickness = enabled
; exclude_object = 1
; extruder_ams_count = 
; extruder_clearance_dist_to_rod = 33
; extruder_clearance_height_to_lid = 90
; extruder_clearance_height_to_rod = 34
; extruder_clearance_max_radius = 68
; extruder_colour = #018001
; extruder_max_nozzle_count = 1
; extruder_nozzle_stats = 
; extruder_offset = 0x2
; extruder_printable_area = 
; extruder_type = Direct Drive
; extruder_variant_list = "Direct Drive Standard,Direct Drive High Flow"
; fan_cooling_layer_time = 30
; fan_direction = left
; fan_max_speed = 40
; fan_min_speed = 20
; farthest_point_timelapse = 1
; filament_adaptive_volumetric_speed = 0
; filament_adhesiveness_category = 300
; filament_bridge_speed = 25
; filament_change_length = 10
; filament_change_length_nc = 10
; filament_colour = #00AE42
; filament_cooling_before_tower = 0
; filament_cost = 17.99
; filament_density = 1.25
; filament_dev_ams_drying_ams_limitations = 1
; filament_dev_ams_drying_heat_distortion_temperature = 75
; filament_dev_ams_drying_temperature = 65
; filament_dev_ams_drying_time = 12
; filament_dev_chamber_drying_bed_temperature = 80
; filament_dev_chamber_drying_time = 12
; filament_dev_drying_cooling_temperature = 55
; filament_dev_drying_softening_temperature = 60
; filament_diameter = 1.75
; filament_enable_overhang_speed = 1
; filament_end_gcode = "; filament end gcode \n\n"
; filament_extruder_compatibility = 0
; filament_extruder_variant = "Direct Drive Standard"
; filament_flow_ratio = 0.95
; filament_flush_temp = 0
; filament_flush_temp_fast = 0
; filament_flush_volumetric_speed = 0
; filament_ids = GFG00
; filament_is_mixed = 0
; filament_is_support = 0
; filament_long_retractions_when_cut = 1
; filament_map = 1
; filament_map_2 = 0
; filament_map_mode = Auto For Flush
; filament_max_volumetric_speed = 15
; filament_metal_stickiness = High
; filament_minimal_purge_on_wipe_tower = 15
; filament_mixed_components = ""
; filament_mixed_gradient = 0
; filament_mixed_gradient_curve = ""
; filament_mixed_gradient_per_part = 0
; filament_mixed_gradient_range = ""
; filament_mixed_sublayer_ratios = ""
; filament_notes = 
; filament_nozzle_map = 0
; filament_overhang_1_4_speed = 0
; filament_overhang_2_4_speed = 50
; filament_overhang_3_4_speed = 30
; filament_overhang_4_4_speed = 10
; filament_overhang_totally_speed = 10
; filament_pre_cooling_temperature = 0
; filament_pre_cooling_temperature_nc = 0
; filament_preheat_temperature_delta = 0
; filament_prime_volume = 45
; filament_prime_volume_nc = 60
; filament_printable = 3
; filament_ramming_travel_time = 0
; filament_ramming_travel_time_nc = 0
; filament_ramming_volumetric_speed = -1
; filament_ramming_volumetric_speed_nc = -1
; filament_retract_length_nc = 14
; filament_retraction_distances_when_cut = 18
; filament_retraction_length = 0.4
; filament_scarf_gap = 0%
; filament_scarf_height = 10%
; filament_scarf_length = 10
; filament_scarf_seam_type = none
; filament_self_index = 1
; filament_settings_id = "Bambu PETG Basic @BBL X1C"
; filament_shrink = 100%
; filament_soluble = 0
; filament_start_gcode = "; filament start gcode\n{if (bed_temperature[current_extruder] >80)||(bed_temperature_initial_layer[current_extruder] >80)}M106 P3 S255\n{elsif (bed_temperature[current_extruder] >60)||(bed_temperature_initial_layer[current_extruder] >60)}M106 P3 S180\n{endif}\n\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"
; filament_tower_interface_pre_extrusion_dist = 10
; filament_tower_interface_pre_extrusion_length = 0
; filament_tower_interface_print_temp = -1
; filament_tower_interface_purge_volume = 20
; filament_tower_ironing_area = 4
; filament_type = PETG
; filament_velocity_adaptation_factor = 1
; filament_vendor = "Bambu Lab"
; filament_volume_map = 0
; filament_wipe = 1
; filament_wipe_distance = 1
; filament_z_hop_types = Spiral Lift
; filename_format = {input_filename_base}_{filament_type[0]}_{print_time}.gcode
; fill_multiline = 1
; filter_out_gap_fill = 0
; first_layer_print_sequence = 0
; first_x_layer_fan_speed = 0
; first_x_layer_part_fan_speed = 0
; flush_into_infill = 0
; flush_into_objects = 0
; flush_into_support = 1
; flush_multiplier = 1
; flush_multiplier_fast = 1.2
; flush_volumes_matrix = 0,280,280,280,280,0,280,280,280,280,0,280,280,280,280,0
; flush_volumes_vector = 140,140,140,140,140,140,140,140
; full_fan_speed_layer = 0
; fuzzy_skin = none
; fuzzy_skin_first_layer = 0
; fuzzy_skin_mode = displacement
; fuzzy_skin_noise_type = classic
; fuzzy_skin_octaves = 4
; fuzzy_skin_persistence = 0.5
; fuzzy_skin_point_distance = 0.8
; fuzzy_skin_scale = 1
; fuzzy_skin_thickness = 0.3
; gap_infill_speed = 250
; gcode_add_line_number = 0
; gcode_flavor = marlin
; grab_length = 0
; group_algo_with_time = 0
; has_filament_switcher = 0
; has_scarf_joint_seam = 0
; head_wrap_detect_zone = 
; hole_coef_1 = 0
; hole_coef_2 = -0.008
; hole_coef_3 = 0.23415
; hole_limit_max = 0.22
; hole_limit_min = 0.088
; hot_plate_temp = 70
; hot_plate_temp_initial_layer = 70
; hotend_cooling_rate = 2
; hotend_heating_rate = 2
; impact_strength_z = 13.6
; independent_support_layer_height = 1
; infill_combination = 0
; infill_direction = 45
; infill_instead_top_bottom_surfaces = 0
; infill_jerk = 9
; infill_lock_depth = 1
; infill_rotate_step = 0
; infill_shift_step = 0.4
; infill_wall_overlap = 15%
; inherits_group = ;;
; initial_layer_acceleration = 500
; initial_layer_flow_ratio = 1
; initial_layer_infill_speed = 105
; initial_layer_jerk = 9
; initial_layer_line_width = 0.5
; initial_layer_print_height = 0.2
; initial_layer_speed = 50
; initial_layer_travel_acceleration = 6000
; inner_wall_acceleration = 0
; inner_wall_jerk = 9
; inner_wall_line_width = 0.45
; inner_wall_speed = 300
; interface_shells = 0
; interlocking_beam = 0
; interlocking_beam_layer_count = 2
; interlocking_beam_width = 0.8
; interlocking_boundary_avoidance = 2
; interlocking_depth = 2
; interlocking_orientation = 22.5
; internal_bridge_support_thickness = 0.8
; internal_solid_infill_line_width = 0.42
; internal_solid_infill_pattern = zig-zag
; internal_solid_infill_speed = 250
; ironing_direction = 45
; ironing_fan_speed = -1
; ironing_flow = 10%
; ironing_inset = 0.21
; ironing_pattern = zig-zag
; ironing_spacing = 0.15
; ironing_speed = 30
; ironing_type = no ironing
; is_infill_first = 0
; layer_change_gcode = ; layer num/total_layer_count: {layer_num+1}/[total_layer_count]\n; update layer progress\nM73 L{layer_num+1}\nM991 S0 P{layer_num} ;notify layer change
; layer_height = 0.2
; line_width = 0.42
; locked_skeleton_infill_pattern = zigzag
; locked_skin_infill_pattern = crosszag
; long_retractions_when_cut = 0
; long_retractions_when_ec = 0
; machine_bed_mass_Y = 0
; machine_end_gcode = ;===== date: 20230428 =====================\nM400 ; wait for buffer to clear\nG92 E0 ; zero the extruder\nG1 E-0.8 F1800 ; retract\nG1 Z{max_layer_z + 0.5} F900 ; lower z a little\nG1 X65 Y245 F12000 ; move to safe pos \nG1 Y265 F3000\n\nG1 X65 Y245 F12000\nG1 Y265 F3000\nM140 S0 ; turn off bed\nM106 S0 ; turn off fan\nM106 P2 S0 ; turn off remote part cooling fan\nM106 P3 S0 ; turn off chamber cooling fan\n\nG1 X100 F12000 ; wipe\n; pull back filament to AMS\nM620 S255\nG1 X20 Y50 F12000\nG1 Y-3\nT255\nG1 X65 F12000\nG1 Y265\nG1 X100 F12000 ; wipe\nM621 S255\nM104 S0 ; turn off hotend\n\nM622.1 S1 ; for prev firmware, default turned on\nM1002 judge_flag timelapse_record_flag\nM622 J1\n    M400 ; wait all motion done\n    M991 S0 P-1 ;end smooth timelapse at safe pos\n    M400 S3 ;wait for last picture to be taken\nM623; end of \"timelapse_record_flag\"\n\nM400 ; wait all motion done\nM17 S\nM17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom\n{if (max_layer_z + 100.0) < 250}\n    G1 Z{max_layer_z + 100.0} F600\n    G1 Z{max_layer_z +98.0}\n{else}\n    G1 Z250 F600\n    G1 Z248\n{endif}\nM400 P100\nM17 R ; restore z current\n\nG90\nG1 X128 Y250 F3600\n\nM220 S100  ; Reset feedrate magnitude\nM201.2 K1.0 ; Reset acc magnitude\nM73.2   R1.0 ;Reset left time magnitude\nM1002 set_gcode_claim_speed_level : 0\n\nM17 X0.8 Y0.8 Z0.5 ; lower motor current to 45% power\n
; machine_hotend_change_time = 0
; machine_load_filament_time = 29
; machine_max_acceleration_e = 5000,5000
; machine_max_acceleration_extruding = 20000,20000
; machine_max_acceleration_retracting = 5000,5000
; machine_max_acceleration_travel = 9000,9000
; machine_max_acceleration_x = 20000,20000
; machine_max_acceleration_y = 20000,20000
; machine_max_acceleration_z = 500,500
; machine_max_force_Y = 0
; machine_max_jerk_e = 2.5,2.5
; machine_max_jerk_x = 9,9
; machine_max_jerk_y = 9,9
; machine_max_jerk_z = 3,3
; machine_max_printed_mass = 0
; machine_max_speed_e = 30,30
; machine_max_speed_x = 500,500
; machine_max_speed_y = 500,500
; machine_max_speed_z = 20,20
; machine_min_extruding_rate = 0
; machine_min_travel_rate = 0
; machine_pause_gcode = M400 U1
; machine_prepare_compensation_time = 260
; machine_start_gcode = G0 Z20 F9000\nG92 E0; G1 E-10 F1200\nG28\nM970 Q1 A10 B10 C130 K0\nM970 Q1 A10 B131 C250 K1\nM974 Q1 S1 P0\nM970 Q0 A10 B10 C130 H20 K0\nM970 Q0 A10 B131 C250 K1\nM974 Q0 S1 P0\nM220 S100 ;Reset Feedrate\nM221 S100 ;Reset Flowrate\nG29 ;Home\nG90;\nG92 E0 ;Reset Extruder \nG1 Z2.0 F3000 ;Move Z Axis up \nG1 X10.1 Y20 Z0.28 F5000.0 ;Move to start position\nM109 S205;\nG1 X10.1 Y200.0 Z0.28 F1500.0 E15 ;Draw the first line\nG1 X10.4 Y200.0 Z0.28 F5000.0 ;Move to side a little\nG1 X10.4 Y20 Z0.28 F1500.0 E30 ;Draw the second line\nG92 E0 ;Reset Extruder \nG1 X110 Y110 Z2.0 F3000 ;Move Z Axis up
; machine_switch_extruder_time = 0
; machine_unload_filament_time = 28
; master_extruder_id = 1
; max_bridge_length = 0
; max_layer_height = 0.28
; max_travel_detour_distance = 0
; min_bead_width = 85%
; min_feature_size = 25%
; min_layer_height = 0.08
; minimum_sparse_infill_area = 15
; mmu_segmented_region_interlocking_depth = 0
; mmu_segmented_region_max_width = 0
; monotonic_travel_into_wall = 0%
; no_slow_down_for_cooling_on_outwalls = 0
; nozzle_diameter = 0.4
; nozzle_flush_dataset = 0
; nozzle_height = 4.2
; nozzle_temperature = 255
; nozzle_temperature_initial_layer = 245
; nozzle_temperature_range_high = 270
; nozzle_temperature_range_low = 230
; nozzle_type = hardened_steel
; nozzle_volume = 107
; nozzle_volume_type = Standard
; only_one_wall_first_layer = 0
; ooze_prevention = 0
; other_layers_print_sequence = 0
; other_layers_print_sequence_nums = 0
; outer_wall_acceleration = 5000
; outer_wall_jerk = 9
; outer_wall_line_width = 0.42
; outer_wall_speed = 200
; overhang_1_4_speed = 0
; overhang_2_4_speed = 50
; overhang_3_4_speed = 30
; overhang_4_4_speed = 10
; overhang_fan_speed = 50
; overhang_fan_threshold = 10%
; overhang_threshold_participating_cooling = 95%
; overhang_totally_speed = 10
; override_filament_scarf_seam_setting = 0
; override_process_overhang_speed = 0
; physical_extruder_map = 0
; post_process = 
; pre_start_fan_time = 2
; precise_outer_wall = 0
; precise_z_height = 0
; pressure_advance = 0.02
; prime_tower_brim_width = 3
; prime_tower_enable_framework = 0
; prime_tower_extra_rib_length = 0
; prime_tower_fillet_wall = 1
; prime_tower_flat_ironing = 0
; prime_tower_infill_gap = 150%
; prime_tower_lift_height = -1
; prime_tower_lift_speed = 90
; prime_tower_max_speed = 90
; prime_tower_rib_wall = 1
; prime_tower_rib_width = 8
; prime_tower_skip_points = 1
; prime_tower_width = 35
; prime_volume_mode = Default
; print_compatible_printers = "Bambu Lab X1 Carbon 0.4 nozzle";"Bambu Lab X1 0.4 nozzle";"Bambu Lab P1S 0.4 nozzle";"Bambu Lab X1E 0.4 nozzle"
; print_extruder_id = 1
; print_extruder_variant = "Direct Drive Standard"
; print_flow_ratio = 1
; print_in_clockwise = 0
; print_sequence = by layer
; print_settings_id = 0.20mm Standard @BBL X1C
; printable_area = 0x0,256x0,256x256,0x256
; printable_height = 250
; printer_extruder_id = 1
; printer_extruder_variant = "Direct Drive Standard"
; printer_model = Bambu Lab X1 Carbon
; printer_notes = 
; printer_settings_id = Bambu Lab X1 Carbon 0.4 nozzle
; printer_structure = corexy
; printer_technology = FFF
; printer_variant = 0.4
; printing_by_object_gcode = 
; process_notes = 
; raft_contact_distance = 0.1
; raft_expansion = 1.5
; raft_first_layer_density = 90%
; raft_first_layer_expansion = -1
; raft_layers = 0
; reduce_crossing_wall = 0
; reduce_fan_stop_start_freq = 1
; reduce_infill_retraction_mode = Auto
; required_nozzle_HRC = 3
; resolution = 0.012
; retract_before_wipe = 0%
; retract_length_toolchange = 2
; retract_lift_above = 0
; retract_lift_below = 249
; retract_restart_extra = 0
; retract_restart_extra_toolchange = 0
; retract_when_changing_layer = 1
; retraction_distances_when_cut = 18
; retraction_distances_when_ec = 0
; retraction_length = 0.8
; retraction_minimum_travel = 1
; retraction_speed = 30
; role_base_wipe_speed = 1
; scan_first_layer = 1
; scarf_angle_threshold = 155
; seam_gap = 15%
; seam_placement_away_from_overhangs = 0
; seam_position = aligned
; seam_slope_conditional = 1
; seam_slope_entire_loop = 0
; seam_slope_gap = 0
; seam_slope_inner_walls = 1
; seam_slope_min_length = 10
; seam_slope_start_height = 10%
; seam_slope_steps = 10
; seam_slope_type = none
; silent_mode = 0
; single_extruder_multi_material = 1
; skeleton_infill_density = 15%
; skeleton_infill_line_width = 0.45
; skin_infill_density = 15%
; skin_infill_depth = 2
; skin_infill_line_width = 0.45
; skirt_distance = 2
; skirt_height = 1
; skirt_loops = 0
; skirt_per_object = 1
; slice_closing_radius = 0.049
; slicing_mode = regular
; slow_down_for_layer_cooling = 1
; slow_down_layer_time = 12
; slow_down_min_speed = 10
; slowdown_end_acc = 100000
; slowdown_end_height = 400
; slowdown_end_speed = 1000
; slowdown_start_acc = 100000
; slowdown_start_height = 0
; slowdown_start_speed = 1000
; small_perimeter_speed = 50%
; small_perimeter_threshold = 0
; smooth_coefficient = 150
; smooth_speed_discontinuity_area = 1
; solid_infill_filament = 0
; sparse_infill_acceleration = 100%
; sparse_infill_anchor = 400%
; sparse_infill_anchor_max = 20
; sparse_infill_density = 15%
; sparse_infill_filament = 0
; sparse_infill_lattice_angle_1 = -45
; sparse_infill_lattice_angle_2 = 45
; sparse_infill_line_width = 0.45
; sparse_infill_pattern = grid
; sparse_infill_speed = 270
; spiral_mode = 0
; spiral_mode_max_xy_smoothing = 200%
; spiral_mode_smooth = 0
; standby_temperature_delta = -5
; start_end_points = 30x-3,54x245
; supertack_plate_temp = 70
; supertack_plate_temp_initial_layer = 70
; support_air_filtration = 0
; support_angle = 0
; support_base_pattern = default
; support_base_pattern_spacing = 2.5
; support_bottom_interface_spacing = 0.5
; support_bottom_z_distance = 0.2
; support_chamber_temp_control = 0
; support_cooling_filter = 0
; support_critical_regions_only = 0
; support_expansion = 0
; support_fast_purge_mode = 0
; support_filament = 0
; support_interface_bottom_layers = 2
; support_interface_filament = 0
; support_interface_loop_pattern = 0
; support_interface_not_for_body = 1
; support_interface_pattern = auto
; support_interface_spacing = 0.5
; support_interface_speed = 80
; support_interface_top_layers = 2
; support_ironing_direction = 0
; support_ironing_flow = 10%
; support_ironing_inset = 0
; support_ironing_pattern = zig-zag
; support_ironing_spacing = 0.15
; support_ironing_speed = 30
; support_line_width = 0.42
; support_object_first_layer_gap = 0.2
; support_object_skip_flush = 0
; support_object_xy_distance = 0.35
; support_on_build_plate_only = 0
; support_remove_small_overhang = 1
; support_speed = 150
; support_style = default
; support_threshold_angle = 30
; support_top_z_distance = 0.2
; support_type = tree(auto)
; symmetric_infill_y_axis = 0
; temperature_vitrification = 60
; template_custom_gcode = 
; textured_plate_temp = 70
; textured_plate_temp_initial_layer = 70
; thick_bridges = 0
; thumbnail_size = 50x50
; time_lapse_gcode = ;========Date 20250206========\nM622.1 S1 ; for prev firmware, default turned on\nM1002 judge_flag timelapse_record_flag\nM622 J1\n{if timelapse_type == 0} ; timelapse without wipe tower\nM971 S11 C10 O0\n{elsif timelapse_type == 1} ; timelapse with wipe tower\nG92 E0\nG1 X65 Y245 F20000 ; move to safe pos\nG17\nG2 Z{layer_z} I0.86 J0.86 P1 F20000\nG1 Y265 F3000\nM400 P300\nM971 S11 C10 O0\nG92 E0\nG1 X100 F5000\nG1 Y255 F20000\n{endif}\nM623\n
; timelapse_type = 0
; top_area_threshold = 200%
; top_color_penetration_layers = 5
; top_one_wall_type = all top
; top_shell_layers = 5
; top_shell_thickness = 1
; top_solid_infill_flow_ratio = 1
; top_surface_acceleration = 2000
; top_surface_density = 100%
; top_surface_jerk = 9
; top_surface_line_width = 0.42
; top_surface_pattern = monotonicline
; top_surface_speed = 200
; top_z_overrides_xy_distance = 0
; travel_acceleration = 10000
; travel_jerk = 9
; travel_short_distance_acceleration = 250
; travel_speed = 500
; travel_speed_z = 0
; tree_support_branch_angle = 45
; tree_support_branch_diameter = 2
; tree_support_branch_diameter_angle = 5
; tree_support_branch_distance = 5
; tree_support_wall_count = -1
; upward_compatible_machine = "Bambu Lab P1S 0.4 nozzle";"Bambu Lab P1P 0.4 nozzle";"Bambu Lab X1 0.4 nozzle";"Bambu Lab X1E 0.4 nozzle";"Bambu Lab A1 0.4 nozzle";"Bambu Lab H2D 0.4 nozzle";"Bambu Lab H2D Pro 0.4 nozzle";"Bambu Lab H2S 0.4 nozzle";"Bambu Lab P2S 0.4 nozzle";"Bambu Lab H2C 0.4 nozzle";"Bambu Lab X2D 0.4 nozzle";"Bambu Lab A2L 0.4 nozzle"
; use_firmware_retraction = 0
; use_relative_e_distances = 1
; vertical_shell_speed = 80%
; volumetric_speed_coefficients = "0 0 0 0 0 0"
; wall_distribution_count = 1
; wall_filament = 0
; wall_generator = classic
; wall_loops = 2
; wall_sequence = inner wall/outer wall
; wall_transition_angle = 10
; wall_transition_filter_deviation = 25%
; wall_transition_length = 100%
; wipe = 1
; wipe_distance = 2
; wipe_speed = 80%
; wipe_tower_no_sparse_layers = 0
; wipe_tower_rotation_angle = 0
; wipe_tower_x = 15
; wipe_tower_y = 220
; wrapping_detection_gcode = 
; wrapping_detection_layers = 20
; wrapping_exclude_area = 
; xy_contour_compensation = 0
; xy_hole_compensation = 0
; z_direction_outwall_speed_continuous = 0
; z_hop = 0.4
; z_hop_types = Auto Lift
; CONFIG_BLOCK_END

; EXECUTABLE_BLOCK_START
M73 P0 R16
M201 X20000 Y20000 Z500 E5000
M203 X500 Y500 Z20 E30
M204 P20000 R5000 T20000
M205 X9.00 Y9.00 Z3.00 E2.50
M106 S0
M106 P2 S0
M190 S70 ; set bed temperature and wait for it to be reached
; FEATURE: Custom
G0 Z20 F9000
G92 E0; G1 E-10 F1200
G28
M970 Q1 A10 B10 C130 K0
M970 Q1 A10 B131 C250 K1
M974 Q1 S1 P0
M970 Q0 A10 B10 C130 H20 K0
M970 Q0 A10 B131 C250 K1
M974 Q0 S1 P0
M220 S100 ;Reset Feedrate
M221 S100 ;Reset Flowrate
G29 ;Home
G90;
G92 E0 ;Reset Extruder 
G1 Z2.0 F3000 ;Move Z Axis up 
G1 X10.1 Y20 Z0.28 F5000.0 ;Move to start position
M109 S205;
G1 X10.1 Y200.0 Z0.28 F1500.0 E15 ;Draw the first line
G1 X10.4 Y200.0 Z0.28 F5000.0 ;Move to side a little
G1 X10.4 Y20 Z0.28 F1500.0 E30 ;Draw the second line
G92 E0 ;Reset Extruder 
M73 P1 R15
G1 X110 Y110 Z2.0 F3000 ;Move Z Axis up
; MACHINE_START_GCODE_END
; filament start gcode
M106 P3 S180


;VT0 H-1
G90
G21
M83 ; use relative distances for extrusion
M981 S1 P20000 ;open spaghetti detector
; CHANGE_LAYER
; Z_HEIGHT: 0.2
; LAYER_HEIGHT: 0.2
G1 E-.4 F1800
; layer num/total_layer_count: 1/74
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
; OBJECT_ID: 15
G1 X120.11 Y127.289 F30000
M204 S6000
M73 P2 R15
G1 Z.4
G1 Z.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.5
G1 F916
M204 S500
G2 X119.419 Y127.173 I-.678 J1.913 E.02546
G2 X119.821 Y126.385 I-1.826 J-1.431 E.03214
G1 X120.05 Y126.418 E.00834
G2 X120.102 Y127.23 I6.4 J-.005 E.0294
; WIPE_START
G1 F3000
G1 X119.707 Y127.191 E-.15093
G1 X119.419 Y127.173 E-.10988
G1 X119.594 Y126.913 E-.11919
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I1.199 J.211 P1  F30000
G1 X119.822 Y125.614 Z.6
G1 Z.2
G1 E.4 F1800
G1 F916
M204 S500
G2 X119.419 Y124.827 I-2.24 J.652 E.03212
G2 X120.11 Y124.711 I.013 J-2.03 E.02545
G1 X120.061 Y125.221 E.01851
G1 X120.05 Y125.581 E.013
G1 X119.881 Y125.605 E.00615
; WIPE_START
G1 F3000
G1 X119.664 Y125.191 E-.17808
G1 X119.419 Y124.827 E-.16646
G1 X119.512 Y124.821 E-.03546
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I-.744 J-.963 P1  F30000
G1 X116.997 Y126.763 Z.6
G1 Z.2
G1 E.4 F1800
; FEATURE: Outer wall
G1 F916
M204 S500
G1 X116.965 Y126.725 E.00179
G3 X117.89 Y124.738 I1.044 J-.723 E.09549
G1 X117.994 Y124.734 E.00377
G3 X119.121 Y125.195 I.106 J1.348 E.0456
G3 X118.2 Y127.258 I-.973 J.803 E.10108
G3 X117.186 Y126.97 I-.192 J-1.255 E.03924
G1 X117.037 Y126.808 E.00796
; WIPE_START
G1 F3000
G1 X116.965 Y126.725 E-.04166
G1 X116.852 Y126.535 E-.08404
G1 X116.777 Y126.328 E-.08364
G1 X116.739 Y126.109 E-.08435
G1 X116.739 Y125.889 E-.08374
G1 X116.74 Y125.882 E-.00256
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I-1.078 J.565 P1  F30000
G1 X120.65 Y133.35 Z.6
G1 Z.2
G1 E.4 F1800
G1 F916
M204 S500
G1 X120.65 Y127.735 E.20272
G3 X120.65 Y124.265 I9.92 J-1.735 E.12595
G1 X120.65 Y118.65 E.20272
G1 X135.35 Y118.65 E.53076
G1 X135.35 Y124.265 E.20272
G3 X135.35 Y127.735 I-9.92 J1.735 E.12595
G1 X135.35 Y133.35 E.20272
G1 X120.71 Y133.35 E.52859
; WIPE_START
G1 F3000
G1 X120.699 Y132.35 E-.38
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I.377 J1.157 P1  F30000
G1 X136.581 Y127.173 Z.6
G1 Z.2
G1 E.4 F1800
; FEATURE: Inner wall
G1 F916
M204 S500
G2 X135.89 Y127.289 I-.013 J2.03 E.02546
G2 X135.95 Y126.419 I-6.335 J-.876 E.03153
G1 X136.178 Y126.386 E.00832
G1 X136.265 Y126.651 E.01005
G2 X136.544 Y127.126 I1.937 J-.817 E.01996
; WIPE_START
G1 F3000
G1 X136.293 Y127.191 E-.09856
G1 X135.89 Y127.289 E-.15769
G1 X135.921 Y126.965 E-.12376
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I1.217 J.025 P1  F30000
G1 X135.95 Y125.582 Z.6
G1 Z.2
G1 E.4 F1800
G1 F916
M204 S500
G2 X135.89 Y124.711 I-6.4 J.005 E.03157
G1 X136.293 Y124.809 E.01498
G1 X136.581 Y124.827 E.01044
G2 X136.179 Y125.615 I1.828 J1.432 E.03213
G1 X136.009 Y125.591 E.00617
; WIPE_START
G1 F3000
G1 X135.939 Y125.221 E-.14297
G1 X135.89 Y124.711 E-.19484
G1 X135.997 Y124.737 E-.04218
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I-.262 J1.189 P1  F30000
G1 X139.124 Y125.425 Z.6
G1 Z.2
G1 E.4 F1800
; FEATURE: Outer wall
G1 F916
M204 S500
G1 X139.188 Y125.565 E.00556
G3 X138.814 Y126.97 I-1.191 J.436 E.05592
G3 X137.488 Y127.206 I-.889 J-1.151 E.05057
G3 X137.898 Y124.736 I.371 J-1.208 E.13113
G3 X139.096 Y125.367 I.098 J1.265 E.05157
G1 X139.097 Y125.371 E.00014
; WIPE_START
G1 F3000
G1 X139.188 Y125.565 E-.08135
G1 X139.262 Y125.89 E-.12658
G1 X139.262 Y126.11 E-.0839
G1 X139.223 Y126.328 E-.08385
G1 X139.219 Y126.338 E-.00432
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I.136 J-1.209 P1  F30000
G1 X120.25 Y124.206 Z.6
G1 Z.2
G1 E.4 F1800
G1 F916
M204 S500
G1 X120.25 Y118.697 E.19891
G1 X120.293 Y118.293 E.01469
G3 X121.176 Y118.25 I.645 J4.197 E.03198
G1 X135.316 Y118.251 E.51054
G1 X135.707 Y118.292 E.01422
G1 X135.75 Y118.697 E.01469
G1 X135.75 Y124.206 E.19891
G1 X136.362 Y124.355 E.02274
G2 X137.623 Y124.296 I.407 J-4.772 E.0457
M73 P3 R15
G3 X138.985 Y124.586 I.305 J1.909 E.05146
G3 X138.001 Y127.723 I-.987 J1.413 E.15749
G3 X136.802 Y127.616 I2.149 J-30.863 E.04345
G1 X136.362 Y127.645 E.01592
G1 X135.75 Y127.794 E.02274
G1 X135.75 Y133.303 E.19891
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X135.707 Y133.707 E.01469
G1 X135.3 Y133.75 E.0148
G1 X120.701 Y133.75 E.52712
G1 X120.293 Y133.707 E.01481
G1 X120.25 Y133.303 E.01468
G1 X120.25 Y127.794 E.19891
G1 X119.638 Y127.645 E.02274
G2 X118.377 Y127.704 I-.407 J4.772 E.0457
G3 X117.015 Y127.414 I-.305 J-1.909 E.05145
G3 X117.999 Y124.277 I.987 J-1.413 E.15749
G3 X119.198 Y124.384 I-2.138 J30.75 E.04345
G1 X119.638 Y124.355 E.01592
G1 X120.192 Y124.22 E.02058
; WIPE_START
G1 F3000
G1 X120.202 Y123.22 E-.38
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I-.994 J-.702 P1  F30000
G1 X119.086 Y124.801 Z.6
G1 Z.2
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.127545
G1 F916
M204 S500
G2 X118.862 Y124.585 I-3.817 J3.737 E.00208
M204 S6000
G1 X118.736 Y124.6 F30000
; LINE_WIDTH: 0.132998
G1 F916
M204 S500
G3 X119.03 Y124.681 I-2.266 J8.697 E.00217
; WIPE_START
G1 F3000
G1 X118.736 Y124.6 E-.38
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I-1.206 J.162 P1  F30000
G1 X119.085 Y127.199 Z.6
G1 Z.2
G1 E.4 F1800
; LINE_WIDTH: 0.127311
G1 F916
M204 S500
G3 X118.862 Y127.415 I-3.995 J-3.918 E.00207
M204 S6000
G1 X118.736 Y127.4 F30000
; LINE_WIDTH: 0.133108
G1 F916
M204 S500
G2 X119.029 Y127.319 I-2.378 J-9.114 E.00217
; WIPE_START
G1 F3000
G1 X118.736 Y127.4 E-.38
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I.005 J1.217 P1  F30000
G1 X136.971 Y127.319 Z.6
G1 Z.2
G1 E.4 F1800
; LINE_WIDTH: 0.132964
G1 F916
M204 S500
G2 X137.264 Y127.4 I2.867 J-9.758 E.00217
M204 S6000
G1 X137.139 Y127.415 F30000
; LINE_WIDTH: 0.127427
G1 F916
M204 S500
G3 X136.915 Y127.199 I3.614 J-3.974 E.00208
; WIPE_START
G1 F3000
G1 X137.139 Y127.415 E-.38
; WIPE_END
G1 E-.02 F1800
M204 S6000
G17
G3 Z.6 I1.213 J-.104 P1  F30000
G1 X136.915 Y124.801 Z.6
G1 Z.2
G1 E.4 F1800
; LINE_WIDTH: 0.127464
G1 F916
M204 S500
G3 X137.138 Y124.585 I3.991 J3.913 E.00208
M204 S6000
G1 X137.264 Y124.6 F30000
; LINE_WIDTH: 0.13312
G1 F916
M204 S500
G2 X136.97 Y124.682 I2.219 J8.522 E.00217
; CHANGE_LAYER
; Z_HEIGHT: 0.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F3000
G1 X137.264 Y124.6 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 2/74
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
; open powerlost recovery
M1003 S1
M976 S1 P1 ; scan model before printing 2nd layer
M400 P100
G1 E.4
M104 S255 ; set nozzle temperature
; OBJECT_ID: 15
G1 E-.4
M204 S10000
G17
G3 Z.6 I-.002 J-1.217 P1  F30000
G1 X120.298 Y124.631 Z.6
G1 Z.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1273
G1 X120.298 Y127.369 E.08803
G1 X118.876 Y127.369 E.04572
G2 X119.597 Y125.86 I-1.025 J-1.416 E.05605
G2 X118.876 Y124.631 I-1.769 J.211 E.04713
G1 X120.238 Y124.631 E.04379
; WIPE_START
G1 F11054.348
G1 X120.26 Y125.631 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z.8 I-.391 J-1.152 P1  F30000
G1 X117.034 Y126.725 Z.8
G1 Z.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1273
M204 S5000
G1 X117.007 Y126.695 E.0012
G3 X117.895 Y124.794 I.989 J-.696 E.07565
G1 X117.992 Y124.79 E.0029
G3 X117.143 Y126.857 I.004 J1.209 E.14149
G1 X117.073 Y126.771 E.00331
; WIPE_START
G1 F11933.819
M204 S10000
G1 X117.007 Y126.695 E-.03806
G1 X116.903 Y126.511 E-.08031
G1 X116.808 Y126.21 E-.12002
G1 X116.79 Y126 E-.08015
G1 X116.804 Y125.839 E-.06145
; WIPE_END
G1 E-.02 F1800
G17
G3 Z.8 I-1.08 J.562 P1  F30000
G1 X120.69 Y133.31 Z.8
G1 Z.4
G1 E.4 F1800
G1 F1273
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z.8 I.517 J1.102 P1  F30000
G1 X137.124 Y124.631 Z.8
G1 Z.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1273
G1 X136.867 Y124.867 E.01121
G2 X136.867 Y127.133 I1.156 J1.133 E.08073
G1 X137.124 Y127.369 E.01121
G1 X135.702 Y127.369 E.04572
G1 X135.702 Y124.631 E.08803
G1 X137.064 Y124.631 E.04379
; WIPE_START
G1 F11054.348
G1 X136.867 Y124.867 E-.11671
G1 X136.687 Y125.081 E-.10614
G1 X136.611 Y125.2 E-.05387
G1 X136.496 Y125.447 E-.10329
; WIPE_END
G1 E-.02 F1800
G17
G3 Z.8 I.002 J1.217 P1  F30000
G1 X139.071 Y125.443 Z.8
G1 Z.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1273
M204 S5000
G1 X139.093 Y125.49 E.00155
G3 X137.895 Y124.794 I-1.097 J.509 E.18238
G1 X137.992 Y124.79 E.0029
G3 X138.988 Y125.308 I.004 J1.209 E.03478
M73 P4 R15
G1 X139.039 Y125.392 E.00293
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.093 Y125.49 E-.04252
G1 X139.169 Y125.687 E-.08
G1 X139.21 Y126 E-.12006
G1 X139.192 Y126.21 E-.08016
G1 X139.147 Y126.354 E-.05726
; WIPE_END
G1 E-.02 F1800
G17
G3 Z.8 I.135 J-1.209 P1  F30000
G1 X120.21 Y124.239 Z.8
G1 Z.4
G1 E.4 F1800
G1 F1273
M204 S5000
G1 X120.21 Y118.21 E.17959
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.239 E.17957
G1 X137.995 Y124.239 E.06569
G3 X137.995 Y127.761 I-.002 J1.761 E.16463
G1 X135.79 Y127.761 E.06569
G1 X135.79 Y133.79 E.17959
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46406
G1 X120.21 Y127.761 E.17957
G1 X118.005 Y127.761 E.06569
G3 X118.004 Y124.239 I.002 J-1.761 E.16463
G1 X120.15 Y124.239 E.06391
M204 S10000
G1 X120.45 Y124.435 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130699
G1 F1273
G1 X120.45 Y118.494 E.04119
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10435
G1 X135.55 Y124.435 E.04144
G1 X136.218 Y124.835 F30000
; LINE_WIDTH: 0.533818
G1 F1273
G2 X136.141 Y125.155 I8.026 J2.095 E.01279
; LINE_WIDTH: 0.499653
G1 X136.127 Y125.229 E.00272
; LINE_WIDTH: 0.466788
G1 X136.109 Y125.321 E.00313
; LINE_WIDTH: 0.425016
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.379638
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.3421
G1 X136.05 Y126.01 E.00814
G1 X136.065 Y126.348 E.00801
; LINE_WIDTH: 0.381171
G1 X136.085 Y126.521 E.00465
; LINE_WIDTH: 0.42505
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.452473
G1 X136.112 Y126.697 E.00059
; LINE_WIDTH: 0.471263
G1 X136.128 Y126.776 E.00271
; LINE_WIDTH: 0.506848
G1 X136.148 Y126.875 E.00373
; LINE_WIDTH: 0.536907
G1 X136.219 Y127.165 E.01165
G1 X135.55 Y127.565 F30000
; LINE_WIDTH: 0.130902
G1 F1273
G1 X135.55 Y133.506 E.04129
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.565 E.04154
G1 X119.805 Y127.165 F30000
; LINE_WIDTH: 0.452436
G1 F1273
G1 X119.891 Y126.679 E.01597
; LINE_WIDTH: 0.425012
G1 X119.915 Y126.521 E.00482
; LINE_WIDTH: 0.37965
G1 X119.936 Y126.334 E.005
; LINE_WIDTH: 0.342021
G1 X119.95 Y125.994 E.00805
G1 X119.935 Y125.652 E.00809
; LINE_WIDTH: 0.381168
G1 X119.915 Y125.479 E.00465
; LINE_WIDTH: 0.42505
G1 X119.891 Y125.321 E.00482
; LINE_WIDTH: 0.452464
G1 X119.806 Y124.835 E.01597
; WIPE_START
G1 F10987.831
G1 X119.891 Y125.321 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z.8 I.553 J-1.084 P1  F30000
G1 X118.156 Y124.435 Z.8
G1 Z.4
G1 E.4 F1800
; LINE_WIDTH: 0.209852
G1 F1273
G1 X118.676 Y124.72 E.00782
G1 X118.665 Y124.736 F30000
; LINE_WIDTH: 0.102516
G1 F1273
G1 X118.607 Y124.695 E.00033
; LINE_WIDTH: 0.147019
G2 X118.184 Y124.435 I-6.347 J9.848 E.00408
G1 X118.499 Y124.552 F30000
; LINE_WIDTH: 0.204239
G1 F1273
G1 X118.124 Y124.517 E.0048
G1 X117.742 Y124.537 E.00488
G1 X117.376 Y124.652 E.0049
G1 X117.148 Y124.783 E.00335
G1 X116.864 Y125.043 E.0049
G1 X116.711 Y125.262 E.00341
G1 X116.566 Y125.614 E.00485
G1 X116.515 Y126 E.00496
G1 X116.564 Y126.381 E.0049
G1 X116.655 Y126.631 E.00338
G1 X116.862 Y126.955 E.0049
G1 X117.146 Y127.214 E.0049
G1 X117.383 Y127.351 E.0035
G1 X117.742 Y127.463 E.00479
G1 X118.011 Y127.485 E.00343
G1 X118.499 Y127.448 E.00625
G1 X118.184 Y127.565 F30000
; LINE_WIDTH: 0.147062
G1 F1273
G2 X118.607 Y127.305 I-5.72 J-9.787 E.00408
; LINE_WIDTH: 0.102542
G1 X118.665 Y127.264 E.00033
G1 X118.676 Y127.28 F30000
; LINE_WIDTH: 0.209844
G1 F1273
G1 X118.156 Y127.565 E.00782
; WIPE_START
G1 F15000
G1 X118.676 Y127.28 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z.8 I-.018 J1.217 P1  F30000
G1 X137.844 Y127.565 Z.8
G1 Z.4
G1 E.4 F1800
; LINE_WIDTH: 0.209984
G1 F1273
G1 X137.322 Y127.279 E.00785
G1 X137.333 Y127.263 F30000
; LINE_WIDTH: 0.103849
G1 F1273
G1 X137.398 Y127.308 E.00038
; LINE_WIDTH: 0.147585
G2 X137.816 Y127.565 I6.891 J-10.74 E.00405
G1 X137.501 Y127.448 F30000
; LINE_WIDTH: 0.204246
G1 F1273
G1 X137.989 Y127.485 E.00625
G1 X138.258 Y127.463 E.00343
G1 X138.624 Y127.348 E.0049
G1 X138.852 Y127.217 E.00335
G1 X139.136 Y126.957 E.0049
G1 X139.289 Y126.738 E.00341
G1 X139.434 Y126.386 E.00485
G1 X139.485 Y126 E.00496
G1 X139.435 Y125.615 E.00494
G1 X139.288 Y125.26 E.00489
G1 X139.135 Y125.043 E.00339
G1 X138.852 Y124.783 E.0049
G1 X138.511 Y124.605 E.0049
G1 X138.258 Y124.537 E.00334
G1 X137.988 Y124.515 E.00345
G1 X137.501 Y124.552 E.00623
G1 X137.816 Y124.435 F30000
; LINE_WIDTH: 0.146826
G1 F1273
G2 X137.391 Y124.697 I6.66 J11.301 E.00409
; LINE_WIDTH: 0.102307
G1 X137.335 Y124.736 E.00032
G1 X137.324 Y124.72 F30000
; LINE_WIDTH: 0.209831
G1 F1273
G1 X137.844 Y124.435 E.00782
; CHANGE_LAYER
; Z_HEIGHT: 0.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.324 Y124.72 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 3/74
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z.8 I.005 J-1.217 P1  F30000
G1 X120.298 Y124.651 Z.8
G1 Z.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1258
G1 X120.298 Y127.349 E.08678
G1 X118.897 Y127.349 E.04503
G2 X119.388 Y125.199 I-.97 J-1.353 E.07754
G2 X118.897 Y124.651 I-1.98 J1.278 E.02375
G1 X120.238 Y124.651 E.04311
; WIPE_START
G1 F11054.348
G1 X120.26 Y125.65 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1 I-.385 J-1.154 P1  F30000
G1 X117.037 Y126.726 Z1
G1 Z.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1258
M204 S5000
G1 X116.948 Y126.607 E.00442
G3 X117.895 Y124.794 I1.046 J-.608 E.0726
G1 X117.987 Y124.79 E.00275
G3 X117.07 Y126.781 I.007 J1.209 E.1447
G1 X117.068 Y126.777 E.00011
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.948 Y126.607 E-.07908
G1 X116.831 Y126.313 E-.12027
G1 X116.794 Y126.105 E-.08019
G1 X116.794 Y125.895 E-.08016
G1 X116.804 Y125.842 E-.02029
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1 I-1.08 J.562 P1  F30000
G1 X120.69 Y133.31 Z1
G1 Z.6
G1 E.4 F1800
G1 F1258
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
M73 P5 R15
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1 I.516 J1.102 P1  F30000
G1 X137.103 Y124.651 Z1
G1 Z.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1258
G1 X136.867 Y124.867 E.01029
G2 X136.867 Y127.133 I1.155 J1.133 E.08074
G1 X137.103 Y127.349 E.01029
G1 X135.702 Y127.349 E.04504
G1 X135.702 Y124.651 E.08678
G1 X137.043 Y124.651 E.04311
; WIPE_START
G1 F11054.348
G1 X136.867 Y124.867 E-.10589
G1 X136.687 Y125.081 E-.10611
G1 X136.548 Y125.323 E-.10615
G1 X136.493 Y125.476 E-.06186
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1 I.016 J1.217 P1  F30000
G1 X139.067 Y125.442 Z1
G1 Z.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1258
M204 S5000
G1 X139.162 Y125.689 E.00788
G3 X137.895 Y124.794 I-1.169 J.311 E.1762
G1 X137.987 Y124.79 E.00275
G3 X139.038 Y125.389 I.007 J1.209 E.03773
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.162 Y125.689 E-.12312
G1 X139.206 Y125.895 E-.08001
G1 X139.206 Y126.105 E-.08012
G1 X139.169 Y126.313 E-.08018
G1 X139.152 Y126.354 E-.01656
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1 I.134 J-1.21 P1  F30000
G1 X120.21 Y124.259 Z1
G1 Z.6
G1 E.4 F1800
G1 F1258
M204 S5000
G1 X120.21 Y118.21 E.18017
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.259 E.18015
G1 X137.995 Y124.259 E.06569
G3 X137.995 Y127.741 I-.004 J1.741 E.16274
G1 X135.79 Y127.741 E.06569
G1 X135.79 Y133.79 E.18017
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46408
G1 X120.21 Y127.741 E.18017
G1 X118.005 Y127.741 E.06569
G3 X118.005 Y124.259 I.004 J-1.741 E.16274
G1 X120.15 Y124.259 E.06391
M204 S10000
G1 X120.45 Y124.455 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130704
G1 F1258
G1 X120.45 Y118.494 E.04133
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10435
G1 X135.55 Y124.455 E.04158
G1 X136.214 Y124.854 F30000
; LINE_WIDTH: 0.532388
G1 F1258
G2 X136.143 Y125.146 I6.663 J1.773 E.0116
; LINE_WIDTH: 0.502176
G1 X136.127 Y125.227 E.00299
; LINE_WIDTH: 0.466157
G1 X136.108 Y125.327 E.00343
; LINE_WIDTH: 0.434402
G1 X136.095 Y125.412 E.00265
; LINE_WIDTH: 0.407238
G1 X136.081 Y125.51 E.00286
; LINE_WIDTH: 0.37614
G1 X136.064 Y125.666 E.00411
; LINE_WIDTH: 0.342654
G1 X136.05 Y126.006 E.00807
G1 X136.067 Y126.365 E.00849
; LINE_WIDTH: 0.38295
G1 X136.085 Y126.521 E.00424
; LINE_WIDTH: 0.424994
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.452387
G1 X136.191 Y127.146 E.01534
G1 X135.55 Y127.545 F30000
; LINE_WIDTH: 0.130902
G1 F1258
G1 X135.55 Y133.506 E.04143
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.545 E.04168
G1 X119.786 Y127.146 F30000
; LINE_WIDTH: 0.53237
M73 P6 R15
G1 F1258
G2 X119.857 Y126.854 I-6.582 J-1.755 E.0116
; LINE_WIDTH: 0.5026
G1 X119.872 Y126.776 E.00291
; LINE_WIDTH: 0.467839
G1 X119.891 Y126.679 E.0033
; LINE_WIDTH: 0.424412
G1 X119.916 Y126.517 E.00494
; LINE_WIDTH: 0.377924
G1 X119.937 Y126.318 E.0053
; LINE_WIDTH: 0.34227
G1 X119.95 Y125.994 E.00767
G1 X119.933 Y125.635 E.00849
; LINE_WIDTH: 0.382966
G1 X119.915 Y125.479 E.00424
; LINE_WIDTH: 0.425033
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.452435
G1 X119.888 Y125.303 E.00059
; LINE_WIDTH: 0.471238
G1 X119.872 Y125.225 E.00271
; LINE_WIDTH: 0.506824
G1 X119.852 Y125.125 E.00373
; LINE_WIDTH: 0.533059
G1 X119.786 Y124.854 E.01079
; WIPE_START
G1 F9181.074
G1 X119.852 Y125.125 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1 I.461 J-1.126 P1  F30000
G1 X118.216 Y124.455 Z1
G1 Z.6
G1 E.4 F1800
; LINE_WIDTH: 0.146614
G1 F1258
G3 X118.607 Y124.695 I-5.308 J9.072 E.00376
; LINE_WIDTH: 0.102545
G1 X118.665 Y124.736 E.00034
G1 X118.676 Y124.72 F30000
; LINE_WIDTH: 0.186653
G1 F1258
G2 X118.358 Y124.546 I-4.139 J7.198 E.00412
G1 X117.983 Y124.525 E.00426
G1 X117.618 Y124.575 E.00418
G1 X117.265 Y124.721 E.00434
G1 X117.052 Y124.87 E.00295
G1 X116.868 Y125.054 E.00296
G1 X116.663 Y125.377 E.00434
G1 X116.574 Y125.621 E.00295
G1 X116.524 Y125.998 E.00431
G1 X116.547 Y126.259 E.00298
G1 X116.662 Y126.621 E.00431
G1 X116.793 Y126.849 E.00298
G1 X117.05 Y127.129 E.00431
G1 X117.265 Y127.279 E.00298
G1 X117.618 Y127.425 E.00434
G1 X117.872 Y127.47 E.00292
G1 X118.276 Y127.463 E.00459
G2 X118.382 Y127.441 I.025 J-.148 E.00126
G1 X118.676 Y127.28 E.0038
G1 X118.665 Y127.264 F30000
; LINE_WIDTH: 0.102545
G1 F1258
G1 X118.607 Y127.305 E.00034
; LINE_WIDTH: 0.146704
G3 X118.216 Y127.545 I-5.714 J-8.855 E.00376
; WIPE_START
G1 F15000
G1 X118.607 Y127.305 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1 I-.015 J1.217 P1  F30000
G1 X137.786 Y127.545 Z1
G1 Z.6
G1 E.4 F1800
; LINE_WIDTH: 0.14703
G1 F1258
G3 X137.391 Y127.303 I5.163 J-8.885 E.00381
; LINE_WIDTH: 0.102305
G1 X137.335 Y127.264 E.00032
G1 X137.324 Y127.28 F30000
; LINE_WIDTH: 0.187082
G1 F1258
G1 X137.631 Y127.448 E.00398
G2 X139.336 Y125.374 I.341 J-1.458 E.03792
G1 X139.209 Y125.154 E.0029
G1 X139.046 Y124.959 E.00289
G1 X138.735 Y124.721 E.00445
G1 X138.505 Y124.613 E.00289
G1 X138.256 Y124.547 E.00293
G1 X137.99 Y124.524 E.00305
G1 X137.738 Y124.536 E.00287
G2 X137.618 Y124.559 I-.03 J.167 E.00143
G1 X137.324 Y124.72 E.00382
G1 X137.335 Y124.736 F30000
; LINE_WIDTH: 0.102309
G1 F1258
G1 X137.391 Y124.697 E.00032
; LINE_WIDTH: 0.146473
G3 X137.784 Y124.455 I6.279 J9.777 E.00378
; CHANGE_LAYER
; Z_HEIGHT: 0.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.391 Y124.697 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 4/74
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
M106 S99.45
; OBJECT_ID: 15
G17
G3 Z1 I.002 J-1.217 P1  F30000
G1 X120.298 Y124.67 Z1
G1 Z.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1258
G1 X120.298 Y127.33 E.08553
G1 X118.953 Y127.33 E.04325
G2 X119.578 Y126.278 I-1.355 J-1.517 E.03996
G2 X119.228 Y124.97 I-1.644 J-.261 E.04486
G1 X118.953 Y124.67 E.01307
G1 X120.238 Y124.67 E.04132
; WIPE_START
G1 F11054.348
G1 X120.26 Y125.67 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.2 I-.376 J-1.157 P1  F30000
G1 X117.032 Y126.72 Z1.2
G1 Z.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1258
M204 S5000
G1 X116.946 Y126.609 E.00419
G3 X117.895 Y124.794 I1.045 J-.609 E.07271
G1 X117.982 Y124.791 E.00259
G3 X117.068 Y126.782 I.009 J1.209 E.14472
G1 X117.062 Y126.772 E.00035
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.946 Y126.609 E-.07617
G1 X116.863 Y126.414 E-.08042
G1 X116.794 Y126.107 E-.11948
G1 X116.794 Y125.895 E-.08073
G1 X116.808 Y125.835 E-.02321
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.2 I-1.08 J.561 P1  F30000
G1 X120.69 Y133.31 Z1.2
G1 Z.8
G1 E.4 F1800
G1 F1258
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.2 I.516 J1.102 P1  F30000
G1 X137.047 Y124.67 Z1.2
G1 Z.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1258
G1 X136.772 Y124.97 E.01307
G2 X136.772 Y127.03 I1.255 J1.03 E.07177
G1 X137.047 Y127.33 E.01307
G1 X135.702 Y127.33 E.04325
G1 X135.702 Y124.67 E.08553
G1 X136.987 Y124.67 E.04132
; WIPE_START
G1 F11054.348
G1 X136.772 Y124.97 E-.14009
G1 X136.61 Y125.202 E-.10776
G1 X136.494 Y125.452 E-.10457
G1 X136.475 Y125.522 E-.02759
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.2 I.04 J1.216 P1  F30000
G1 X139.067 Y125.436 Z1.2
G1 Z.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1258
M204 S5000
G1 X139.128 Y125.589 E.00492
G3 X137.895 Y124.794 I-1.138 J.411 E.17937
G1 X137.982 Y124.791 E.00259
G3 X139.033 Y125.387 I.009 J1.209 E.03771
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.128 Y125.589 E-.08507
G1 X139.206 Y125.893 E-.1191
G1 X139.206 Y126.105 E-.08069
G1 X139.169 Y126.313 E-.08019
G1 X139.154 Y126.35 E-.01495
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.2 I.132 J-1.21 P1  F30000
G1 X120.21 Y124.278 Z1.2
G1 Z.8
G1 E.4 F1800
G1 F1258
M204 S5000
G1 X120.21 Y118.21 E.18075
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.278 E.18073
G1 X137.995 Y124.278 E.06569
G3 X137.995 Y127.722 I-.004 J1.722 E.16089
G1 X135.79 Y127.722 E.06569
G1 X135.79 Y133.79 E.18075
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46408
G1 X120.21 Y127.722 E.18075
G1 X118.004 Y127.722 E.06569
M73 P7 R15
G3 X118.004 Y124.278 I.004 J-1.722 E.16089
G1 X120.15 Y124.278 E.06391
M204 S10000
G1 X120.45 Y124.474 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.13071
G1 F1258
G1 X120.45 Y118.494 E.04147
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10436
G1 X135.55 Y124.474 E.04172
G1 X136.208 Y124.874 F30000
; LINE_WIDTH: 0.523851
M73 P7 R14
G1 F1258
G1 X136.139 Y125.168 E.0115
; LINE_WIDTH: 0.495812
G1 X136.125 Y125.236 E.00246
; LINE_WIDTH: 0.465517
G1 X136.109 Y125.321 E.0029
; LINE_WIDTH: 0.425029
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.37966
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342915
G1 X136.05 Y126.006 E.00808
G1 X136.068 Y126.371 E.00865
; LINE_WIDTH: 0.383655
G1 X136.085 Y126.521 E.00408
; LINE_WIDTH: 0.425053
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.452476
G1 X136.112 Y126.697 E.00059
; LINE_WIDTH: 0.471284
G1 X136.128 Y126.776 E.00272
; LINE_WIDTH: 0.522963
G1 X136.143 Y126.854 E.00305
G2 X136.209 Y127.126 I6.556 J-1.444 E.01061
G1 X135.55 Y127.526 F30000
; LINE_WIDTH: 0.130902
G1 F1258
G1 X135.55 Y133.506 E.04156
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.526 E.04181
G1 X119.792 Y127.126 F30000
; LINE_WIDTH: 0.523853
G1 F1258
G1 X119.861 Y126.832 E.0115
; LINE_WIDTH: 0.495825
G1 X119.875 Y126.764 E.00246
; LINE_WIDTH: 0.465518
G1 X119.891 Y126.679 E.0029
; LINE_WIDTH: 0.425019
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.379673
G1 X119.936 Y126.334 E.00501
; LINE_WIDTH: 0.342016
G1 X119.95 Y125.994 E.00805
G1 X119.935 Y125.652 E.00809
; LINE_WIDTH: 0.381159
G1 X119.915 Y125.479 E.00466
; LINE_WIDTH: 0.425034
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.452445
G1 X119.812 Y124.874 E.0147
; WIPE_START
G1 F10988.355
G1 X119.891 Y125.321 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.2 I.584 J-1.068 P1  F30000
G1 X118.343 Y124.474 Z1.2
G1 Z.8
G1 E.4 F1800
; LINE_WIDTH: 0.146788
G1 F1258
G3 X118.718 Y124.753 I-6.378 J8.978 E.00384
; LINE_WIDTH: 0.102547
G1 X118.773 Y124.799 E.00034
G1 X118.785 Y124.784 F30000
; LINE_WIDTH: 0.214153
G1 F1258
G2 X118.465 Y124.571 I-5.044 J7.246 E.0052
G1 X118.382 Y124.559 E.00113
; LINE_WIDTH: 0.180599
G1 X118.01 Y124.535 E.00406
; LINE_WIDTH: 0.162442
G1 X117.745 Y124.556 E.00251
G1 X117.496 Y124.623 E.00244
G1 X117.161 Y124.798 E.00357
G1 X116.962 Y124.965 E.00246
G1 X116.732 Y125.265 E.00356
G1 X116.621 Y125.505 E.0025
G1 X116.54 Y125.87 E.00353
G1 X116.541 Y126.134 E.00249
G1 X116.622 Y126.499 E.00353
G1 X116.73 Y126.733 E.00244
G1 X116.895 Y126.962 E.00266
G1 X117.157 Y127.199 E.00334
G1 X117.381 Y127.328 E.00244
G1 X117.623 Y127.417 E.00244
G1 X117.875 Y127.46 E.00241
G1 X118.28 Y127.452 E.00382
; LINE_WIDTH: 0.211777
G1 X118.39 Y127.44 E.00148
G2 X118.506 Y127.402 I.015 J-.151 E.00168
G1 X118.785 Y127.216 E.00447
G1 X118.773 Y127.201 F30000
; LINE_WIDTH: 0.102557
G1 F1258
G1 X118.718 Y127.247 E.00034
; LINE_WIDTH: 0.146838
G3 X118.343 Y127.526 I-6.631 J-8.539 E.00384
; WIPE_START
G1 F15000
G1 X118.718 Y127.247 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.2 I-.018 J1.217 P1  F30000
G1 X137.66 Y127.526 Z1.2
G1 Z.8
G1 E.4 F1800
; LINE_WIDTH: 0.161649
G1 F1258
G1 X137.397 Y127.335 E.00305
; LINE_WIDTH: 0.147954
G1 X137.341 Y127.292 E.00059
; LINE_WIDTH: 0.112403
G1 X137.227 Y127.201 E.0008
G1 X137.215 Y127.216 F30000
; LINE_WIDTH: 0.214154
G1 F1258
G2 X137.535 Y127.429 I5.243 J-7.555 E.0052
G1 X137.618 Y127.441 E.00113
; LINE_WIDTH: 0.180427
G1 X137.99 Y127.466 E.00405
; LINE_WIDTH: 0.162332
G1 X138.254 Y127.443 E.00251
G1 X138.504 Y127.377 E.00243
G1 X138.839 Y127.202 E.00356
G1 X139.038 Y127.035 E.00246
G1 X139.27 Y126.733 E.00359
G1 X139.378 Y126.501 E.00241
G1 X139.46 Y126.13 E.00359
G1 X139.459 Y125.866 E.00249
G1 X139.378 Y125.501 E.00353
G1 X139.271 Y125.269 E.00241
G1 X139.121 Y125.056 E.00246
G1 X138.94 Y124.875 E.00241
G1 X138.622 Y124.673 E.00356
G1 X138.379 Y124.584 E.00243
G1 X138.121 Y124.539 E.00247
G1 X137.74 Y124.545 E.00359
; LINE_WIDTH: 0.199742
G1 X137.61 Y124.56 E.00162
; LINE_WIDTH: 0.214152
G2 X137.494 Y124.598 I-.015 J.151 E.00171
G1 X137.215 Y124.784 E.00454
G1 X137.227 Y124.799 F30000
; LINE_WIDTH: 0.102321
G1 F1258
G1 X137.279 Y124.755 E.00032
; LINE_WIDTH: 0.146618
G3 X137.657 Y124.474 I7.466 J9.656 E.00385
; CHANGE_LAYER
; Z_HEIGHT: 1
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.279 Y124.755 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 5/74
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z1.2 I.005 J-1.217 P1  F30000
G1 X120.298 Y124.69 Z1.2
G1 Z1
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1262
G1 X120.298 Y127.31 E.08428
G1 X118.971 Y127.31 E.04267
G2 X119.578 Y126.278 I-1.333 J-1.479 E.03912
G2 X119.228 Y124.97 I-1.644 J-.261 E.04486
G1 X118.971 Y124.69 E.01223
G1 X120.238 Y124.69 E.04074
; WIPE_START
G1 F11054.348
G1 X120.261 Y125.689 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I-.366 J-1.161 P1  F30000
G1 X117.022 Y126.71 Z1.4
G1 Z1
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1262
M204 S5000
G1 X117.012 Y126.692 E.00062
G3 X117.895 Y124.794 I.988 J-.694 E.07539
G3 X118.104 Y124.794 I.106 J1.488 E.00623
G3 X117.147 Y126.853 I-.103 J1.203 E.13817
G1 X117.062 Y126.755 E.00386
; WIPE_START
G1 F11933.819
M204 S10000
G1 X117.012 Y126.692 E-.03059
G1 X116.903 Y126.511 E-.08004
G1 X116.813 Y126.233 E-.11112
G1 X116.79 Y126 E-.08908
G1 X116.812 Y125.819 E-.06916
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I-1.081 J.559 P1  F30000
G1 X120.69 Y133.31 Z1.4
G1 Z1
G1 E.4 F1800
G1 F1262
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I.516 J1.102 P1  F30000
G1 X137.029 Y124.69 Z1.4
G1 Z1
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1262
G1 X136.769 Y124.974 E.01239
G2 X136.772 Y127.03 I1.258 J1.026 E.07161
G1 X137.029 Y127.31 E.01223
G1 X135.702 Y127.31 E.04267
G1 X135.702 Y124.69 E.08428
G1 X136.969 Y124.69 E.04074
; WIPE_START
G1 F11054.348
G1 X136.769 Y124.974 E-.13212
M73 P8 R14
G1 X136.612 Y125.199 E-.10416
G1 X136.494 Y125.452 E-.10618
G1 X136.468 Y125.547 E-.03754
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I.051 J1.216 P1  F30000
G1 X139.068 Y125.438 Z1.4
G1 Z1
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1262
M204 S5000
G1 X139.096 Y125.489 E.00173
G3 X137.895 Y124.794 I-1.096 J.509 E.18203
G3 X138.104 Y124.794 I.106 J1.488 E.00623
G3 X138.991 Y125.306 I-.103 J1.203 E.03151
G1 X139.037 Y125.386 E.00276
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.096 Y125.489 E-.04491
G1 X139.169 Y125.687 E-.08015
G1 X139.21 Y126 E-.12006
G1 X139.192 Y126.21 E-.08015
G1 X139.149 Y126.348 E-.05473
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I.131 J-1.21 P1  F30000
G1 X120.21 Y124.297 Z1.4
G1 Z1
G1 E.4 F1800
G1 F1262
M204 S5000
G1 X120.21 Y118.21 E.18133
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.297 E.18131
G1 X137.995 Y124.297 E.06569
G3 X138.148 Y127.696 I.003 J1.702 E.15492
G1 X135.79 Y127.703 E.07024
G1 X135.786 Y133.79 E.18133
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46396
G1 X120.21 Y127.703 E.18133
G1 X118.005 Y127.703 E.06569
G3 X118.005 Y124.297 I.002 J-1.703 E.15919
G1 X120.15 Y124.297 E.06391
M204 S10000
G1 X120.45 Y124.493 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130716
G1 F1262
G1 X120.45 Y118.494 E.04161
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10437
G1 X135.55 Y124.493 E.04186
G1 X136.184 Y124.893 F30000
; LINE_WIDTH: 0.452431
G1 F1262
G1 X136.109 Y125.321 E.01406
; LINE_WIDTH: 0.425026
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.379679
G1 X136.064 Y125.666 E.005
; LINE_WIDTH: 0.342029
G1 X136.05 Y126.006 E.00806
G1 X136.065 Y126.348 E.00809
; LINE_WIDTH: 0.381168
G1 X136.085 Y126.521 E.00466
; LINE_WIDTH: 0.425026
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.452399
G1 X136.112 Y126.697 E.00058
; LINE_WIDTH: 0.471217
G1 X136.128 Y126.775 E.00272
; LINE_WIDTH: 0.515971
G1 X136.146 Y126.867 E.00347
G1 X136.534 Y127.107 E.01706
; WIPE_START
G1 F9512.731
G1 X136.146 Y126.867 E-.3157
G1 X136.128 Y126.775 E-.0643
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I-.955 J-.754 P1  F30000
G1 X135.55 Y127.507 Z1.4
G1 Z1
G1 E.4 F1800
; LINE_WIDTH: 0.130902
G1 F1262
G1 X135.55 Y133.506 E.0417
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.507 E.04195
G1 X119.816 Y127.107 F30000
; LINE_WIDTH: 0.452448
G1 F1262
G1 X119.891 Y126.679 E.01406
; LINE_WIDTH: 0.425028
G1 X119.915 Y126.521 E.00482
; LINE_WIDTH: 0.379682
G1 X119.936 Y126.334 E.005
; LINE_WIDTH: 0.342026
G1 X119.95 Y125.994 E.00806
G1 X119.935 Y125.652 E.00809
; LINE_WIDTH: 0.381177
G1 X119.915 Y125.479 E.00465
; LINE_WIDTH: 0.425033
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.452435
G1 X119.816 Y124.893 E.01406
; WIPE_START
G1 F10988.624
G1 X119.891 Y125.321 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I.581 J-1.069 P1  F30000
G1 X118.37 Y124.494 Z1.4
G1 Z1
G1 E.4 F1800
; LINE_WIDTH: 0.146332
G1 F1262
G3 X118.718 Y124.753 I-6.034 J8.475 E.00355
; LINE_WIDTH: 0.102542
G1 X118.773 Y124.799 E.00034
G1 X118.785 Y124.784 F30000
; LINE_WIDTH: 0.210097
G1 F1262
G2 X118.485 Y124.584 I-4.56 J6.516 E.00476
G1 X118.38 Y124.568 E.0014
; LINE_WIDTH: 0.161117
G1 X118.01 Y124.545 E.00346
; LINE_WIDTH: 0.142977
G1 X117.871 Y124.55 E.0011
G1 X117.621 Y124.594 E.00201
G1 X117.385 Y124.68 E.00199
G1 X117.165 Y124.807 E.00201
G1 X116.97 Y124.97 E.00201
G1 X116.808 Y125.163 E.00199
G1 X116.629 Y125.508 E.00307
G2 X118.257 Y127.445 I1.384 J.49 E.02411
; LINE_WIDTH: 0.179975
G1 X118.387 Y127.431 E.00141
; LINE_WIDTH: 0.210299
G2 X118.506 Y127.402 I.027 J-.15 E.00167
G1 X118.785 Y127.216 E.00443
G1 X118.773 Y127.201 F30000
; LINE_WIDTH: 0.102535
G1 F1262
G1 X118.718 Y127.247 E.00034
; LINE_WIDTH: 0.146329
G3 X118.369 Y127.506 I-6.168 J-7.937 E.00355
; WIPE_START
G1 F15000
G1 X118.718 Y127.247 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.4 I-.017 J1.217 P1  F30000
G1 X137.631 Y127.506 Z1.4
G1 Z1
G1 E.4 F1800
; LINE_WIDTH: 0.146067
G1 F1262
G3 X137.279 Y127.245 I6.589 J-9.235 E.00357
; LINE_WIDTH: 0.102305
G1 X137.227 Y127.201 E.00032
G1 X137.215 Y127.216 F30000
; LINE_WIDTH: 0.210304
G1 F1262
G1 X137.494 Y127.402 E.00443
G2 X137.613 Y127.431 I.092 J-.122 E.00167
; LINE_WIDTH: 0.179982
G1 X137.743 Y127.445 E.00141
; LINE_WIDTH: 0.143012
G2 X139.329 Y126.593 I.233 J-1.469 E.01529
G1 X139.434 Y126.253 E.00282
G1 X139.451 Y125.873 E.00301
G1 X139.368 Y125.502 E.00301
G1 X139.193 Y125.165 E.003
G1 X138.936 Y124.884 E.00301
G1 X138.617 Y124.681 E.00299
G1 X138.255 Y124.566 E.00301
G1 X137.99 Y124.544 E.0021
; LINE_WIDTH: 0.160943
G1 X137.62 Y124.568 E.00346
; LINE_WIDTH: 0.210065
G1 X137.515 Y124.584 E.0014
G2 X137.215 Y124.784 I4.724 J7.433 E.00476
G1 X137.227 Y124.799 F30000
; LINE_WIDTH: 0.1023
G1 F1262
G1 X137.279 Y124.755 E.00032
; LINE_WIDTH: 0.146081
G3 X137.631 Y124.494 I7.052 J9.119 E.00357
; CHANGE_LAYER
; Z_HEIGHT: 1.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.279 Y124.755 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 6/74
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z1.4 I.003 J-1.217 P1  F30000
G1 X120.298 Y124.709 Z1.4
G1 Z1.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1259
G1 X120.298 Y127.291 E.08303
G1 X118.989 Y127.291 E.0421
G2 X119.578 Y125.722 I-1.145 J-1.326 E.05621
G2 X118.989 Y124.709 I-1.801 J.371 E.03835
G1 X120.238 Y124.709 E.04017
; WIPE_START
G1 F11054.348
G1 X120.261 Y125.709 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I-.357 J-1.163 P1  F30000
G1 X117.018 Y126.705 Z1.6
G1 Z1.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1259
M204 S5000
G1 X117.012 Y126.692 E.00043
G3 X117.895 Y124.794 I.988 J-.694 E.07538
G3 X118.103 Y124.794 I.106 J1.554 E.00622
G3 X117.147 Y126.853 I-.103 J1.204 E.13819
G1 X117.058 Y126.75 E.00406
; WIPE_START
G1 F11933.819
M204 S10000
G1 X117.012 Y126.692 E-.02813
G1 X116.903 Y126.511 E-.0801
G1 X116.814 Y126.238 E-.10913
G1 X116.79 Y126 E-.09103
G1 X116.814 Y125.813 E-.07161
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I-1.081 J.559 P1  F30000
G1 X120.69 Y133.31 Z1.6
G1 Z1.2
M73 P9 R14
G1 E.4 F1800
G1 F1259
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I.515 J1.103 P1  F30000
G1 X137.011 Y124.709 Z1.6
G1 Z1.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1259
G1 X136.772 Y124.97 E.01138
G2 X136.772 Y127.03 I1.254 J1.03 E.07178
G1 X137.011 Y127.291 E.01137
G1 X135.702 Y127.291 E.0421
G1 X135.702 Y124.709 E.08303
G1 X136.951 Y124.709 E.04017
; WIPE_START
G1 F11054.348
G1 X136.772 Y124.97 E-.12023
G1 X136.612 Y125.199 E-.1061
G1 X136.494 Y125.452 E-.10619
G1 X136.463 Y125.573 E-.04748
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I.066 J1.215 P1  F30000
G1 X139.064 Y125.432 Z1.6
G1 Z1.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1259
M204 S5000
G1 X139.096 Y125.489 E.00193
G3 X137.895 Y124.794 I-1.096 J.509 E.18203
G3 X138.103 Y124.794 I.106 J1.554 E.00622
G3 X138.991 Y125.306 I-.103 J1.204 E.03152
G1 X139.034 Y125.381 E.00257
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.096 Y125.489 E-.04739
G1 X139.169 Y125.687 E-.08011
G1 X139.21 Y125.998 E-.11926
G1 X139.196 Y126.182 E-.07003
G1 X139.155 Y126.343 E-.06321
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I.129 J-1.21 P1  F30000
G1 X120.21 Y124.317 Z1.6
G1 Z1.2
G1 E.4 F1800
G1 F1259
M204 S5000
G1 X120.21 Y118.21 E.1819
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.317 E.18189
G1 X137.995 Y124.317 E.06569
G3 X137.995 Y127.683 I-.002 J1.683 E.15737
G1 X135.79 Y127.683 E.06569
G1 X135.79 Y133.79 E.1819
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46408
G1 X120.21 Y127.683 E.1819
G1 X118.005 Y127.683 E.06569
G3 X118.005 Y124.317 I.002 J-1.683 E.15737
G1 X120.15 Y124.317 E.06391
M204 S10000
G1 X120.45 Y124.513 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130722
G1 F1259
G1 X120.45 Y118.494 E.04175
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10437
G1 X135.55 Y124.513 E.04199
G1 X136.181 Y124.913 F30000
; LINE_WIDTH: 0.452469
G1 F1259
G1 X136.109 Y125.321 E.01342
; LINE_WIDTH: 0.43654
G1 X136.096 Y125.404 E.00261
; LINE_WIDTH: 0.408161
G1 X136.081 Y125.506 E.00298
; LINE_WIDTH: 0.374103
G1 X136.062 Y125.701 E.00511
; LINE_WIDTH: 0.341198
G1 X136.05 Y126.006 E.00721
G1 X136.065 Y126.348 E.00806
; LINE_WIDTH: 0.381168
G1 X136.085 Y126.521 E.00466
; LINE_WIDTH: 0.425046
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.452457
G1 X136.181 Y127.087 E.01342
G1 X135.55 Y127.487 F30000
; LINE_WIDTH: 0.130902
G1 F1259
G1 X135.55 Y133.506 E.04183
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.487 E.04208
; WIPE_START
G1 F15000
M73 P10 R14
G1 X120.451 Y128.487 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I1.002 J-.691 P1  F30000
G1 X119.486 Y127.087 Z1.6
G1 Z1.2
G1 E.4 F1800
; LINE_WIDTH: 0.499426
G1 F1259
G1 X119.857 Y126.851 E.01589
G1 X119.874 Y126.77 E.00298
; LINE_WIDTH: 0.468426
G1 X119.89 Y126.689 E.00278
; LINE_WIDTH: 0.434894
G1 X119.907 Y126.575 E.00357
; LINE_WIDTH: 0.4052
G1 X119.92 Y126.482 E.00266
; LINE_WIDTH: 0.3769
G1 X119.935 Y126.348 E.00357
; LINE_WIDTH: 0.342273
G1 X119.95 Y125.998 E.00829
G1 X119.936 Y125.666 E.00787
; LINE_WIDTH: 0.379676
G1 X119.915 Y125.479 E.005
; LINE_WIDTH: 0.42505
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.452473
G1 X119.819 Y124.913 E.01342
; WIPE_START
G1 F10987.59
G1 X119.891 Y125.321 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I.579 J-1.071 P1  F30000
G1 X118.396 Y124.513 Z1.6
G1 Z1.2
G1 E.4 F1800
; LINE_WIDTH: 0.145809
G1 F1259
G3 X118.718 Y124.753 I-5.363 J7.546 E.00327
; LINE_WIDTH: 0.102531
G1 X118.773 Y124.799 E.00033
G1 X118.785 Y124.784 F30000
; LINE_WIDTH: 0.205049
G1 F1259
G1 X118.506 Y124.598 E.0043
G1 X118.378 Y124.578 E.00166
; LINE_WIDTH: 0.129889
G1 X118.124 Y124.556 E.00175
G1 X117.874 Y124.559 E.00172
G1 X117.626 Y124.603 E.00173
G1 X117.387 Y124.69 E.00174
; LINE_WIDTH: 0.123637
G1 X117.17 Y124.815 E.0016
G1 X116.978 Y124.976 E.0016
G1 X116.747 Y125.277 E.00242
G1 X116.641 Y125.505 E.00161
G1 X116.576 Y125.747 E.0016
G1 X116.56 Y126.133 E.00246
G2 X118.255 Y127.435 I1.46 J-.145 E.01528
; LINE_WIDTH: 0.160204
G1 X118.384 Y127.421 E.0012
; LINE_WIDTH: 0.205498
G1 X118.506 Y127.402 E.00159
G1 X118.785 Y127.216 E.00431
G1 X118.773 Y127.201 F30000
; LINE_WIDTH: 0.10255
G1 F1259
G1 X118.718 Y127.247 E.00034
; LINE_WIDTH: 0.145865
G3 X118.396 Y127.487 I-5.675 J-7.291 E.00327
; WIPE_START
G1 F15000
G1 X118.718 Y127.247 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.6 I-.015 J1.217 P1  F30000
G1 X137.604 Y127.487 Z1.6
G1 Z1.2
G1 E.4 F1800
; LINE_WIDTH: 0.145537
G1 F1259
G3 X137.279 Y127.245 I6.303 J-8.808 E.00328
; LINE_WIDTH: 0.102296
G1 X137.227 Y127.201 E.00032
G1 X137.215 Y127.216 F30000
; LINE_WIDTH: 0.204662
G1 F1259
G1 X137.494 Y127.402 E.00429
G1 X137.627 Y127.423 E.00172
; LINE_WIDTH: 0.124492
G1 X137.777 Y127.438 E.00097
G2 X139.437 Y125.844 I.21 J-1.443 E.01709
G1 X139.359 Y125.505 E.00224
G1 X139.253 Y125.278 E.00161
G1 X139.108 Y125.07 E.00163
G1 X138.93 Y124.892 E.00163
G1 X138.723 Y124.747 E.00162
G1 X138.495 Y124.641 E.00162
G1 X138.251 Y124.575 E.00162
G1 X137.99 Y124.554 E.00169
; LINE_WIDTH: 0.141434
G1 X137.622 Y124.578 E.00287
; LINE_WIDTH: 0.205037
G1 X137.494 Y124.598 E.00165
G1 X137.215 Y124.784 E.0043
G1 X137.227 Y124.799 F30000
; LINE_WIDTH: 0.102277
G1 F1259
G1 X137.279 Y124.755 E.00032
; LINE_WIDTH: 0.14554
G3 X137.605 Y124.513 I6.331 J8.18 E.00329
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.279 Y124.755 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 7/74
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z1.6 I.002 J-1.217 P1  F30000
G1 X120.298 Y124.728 Z1.6
G1 Z1.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1260
G1 X120.298 Y127.272 E.08178
G1 X119.007 Y127.272 E.04153
G2 X119.547 Y125.578 I-1.132 J-1.294 E.06006
G2 X119.007 Y124.728 I-1.86 J.585 E.03275
G1 X120.238 Y124.728 E.0396
; WIPE_START
G1 F11054.348
G1 X120.262 Y125.728 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I-.349 J-1.166 P1  F30000
G1 X117.013 Y126.7 Z1.8
G1 Z1.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1260
M204 S5000
G1 X117.012 Y126.692 E.00024
G3 X117.895 Y124.794 I.989 J-.694 E.07538
G3 X118.103 Y124.794 I.107 J1.615 E.00622
G3 X117.147 Y126.853 I-.102 J1.204 E.1382
G1 X117.053 Y126.745 E.00427
; WIPE_START
G1 F11933.819
M204 S10000
G1 X117.012 Y126.692 E-.02538
G1 X116.863 Y126.414 E-.11988
G1 X116.808 Y126.21 E-.0802
G1 X116.79 Y126 E-.08014
G1 X116.807 Y125.805 E-.07441
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I-1.081 J.559 P1  F30000
G1 X120.69 Y133.31 Z1.8
G1 Z1.4
G1 E.4 F1800
G1 F1260
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I.515 J1.103 P1  F30000
G1 X136.993 Y124.728 Z1.8
G1 Z1.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1260
G1 X136.772 Y124.97 E.01053
G2 X136.772 Y127.03 I1.254 J1.03 E.07178
G1 X136.993 Y127.272 E.01053
G1 X135.702 Y127.272 E.04153
G1 X135.702 Y124.728 E.08178
G1 X136.933 Y124.728 E.0396
; WIPE_START
G1 F11054.348
G1 X136.772 Y124.97 E-.11031
G1 X136.612 Y125.199 E-.10619
G1 X136.494 Y125.452 E-.10611
G1 X136.455 Y125.598 E-.05739
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I.077 J1.215 P1  F30000
G1 X139.059 Y125.433 Z1.8
G1 Z1.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1260
M204 S5000
G1 X139.124 Y125.555 E.00412
G3 X137.895 Y124.794 I-1.124 J.443 E.1799
G3 X138.103 Y124.794 I.107 J1.615 E.00622
G3 X138.991 Y125.306 I-.102 J1.204 E.03153
G1 X139.031 Y125.38 E.0025
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.124 Y125.555 E-.07532
G1 X139.192 Y125.79 E-.09299
G1 X139.21 Y126 E-.08016
G1 X139.169 Y126.313 E-.12006
G1 X139.159 Y126.342 E-.01148
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I.128 J-1.21 P1  F30000
G1 X120.21 Y124.336 Z1.8
G1 Z1.4
G1 E.4 F1800
G1 F1260
M204 S5000
G1 X120.21 Y118.21 E.18248
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.336 E.18247
G1 X137.995 Y124.336 E.06569
G3 X137.995 Y127.664 I.003 J1.664 E.15584
G1 X135.79 Y127.664 E.06569
G1 X135.79 Y133.79 E.18248
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46406
G1 X120.21 Y127.664 E.18248
M73 P11 R14
G1 X118.005 Y127.664 E.06569
G3 X118.005 Y124.336 I-.003 J-1.664 E.15584
G1 X120.15 Y124.336 E.06391
M204 S10000
G1 X120.45 Y124.532 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130728
G1 F1260
G1 X120.45 Y118.494 E.04188
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10438
G1 X135.55 Y124.532 E.04213
; WIPE_START
G1 F15000
G1 X135.549 Y123.532 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I-1.005 J.686 P1  F30000
G1 X136.505 Y124.932 Z1.8
G1 Z1.4
G1 E.4 F1800
; LINE_WIDTH: 0.471657
G1 F1260
G1 X136.159 Y125.152 E.01388
; LINE_WIDTH: 0.48501
G1 X136.139 Y125.166 E.00084
G1 X136.112 Y125.303 E.0049
; LINE_WIDTH: 0.452465
G1 X136.109 Y125.321 E.00059
; LINE_WIDTH: 0.425073
G1 X136.085 Y125.478 E.00481
; LINE_WIDTH: 0.379661
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.34202
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.381128
G1 X136.085 Y126.521 E.00465
; LINE_WIDTH: 0.425031
G1 X136.109 Y126.679 E.00482
; LINE_WIDTH: 0.452474
G1 X136.177 Y127.068 E.01278
G1 X135.55 Y127.468 F30000
; LINE_WIDTH: 0.130902
G1 F1260
G1 X135.55 Y133.506 E.04197
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.468 E.04222
; WIPE_START
G1 F15000
G1 X120.451 Y128.468 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I1.005 J-.687 P1  F30000
G1 X119.495 Y127.068 Z1.8
G1 Z1.4
G1 E.4 F1800
; LINE_WIDTH: 0.471873
G1 F1260
G1 X119.841 Y126.848 E.0139
; LINE_WIDTH: 0.496748
G2 X119.874 Y126.766 I-.024 J-.058 E.00353
; LINE_WIDTH: 0.469308
G1 X119.888 Y126.697 E.00236
; LINE_WIDTH: 0.452488
G1 X119.891 Y126.679 E.00059
; LINE_WIDTH: 0.425073
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.381166
G1 X119.935 Y126.348 E.00466
; LINE_WIDTH: 0.342019
G1 X119.95 Y126.006 E.00808
G1 X119.936 Y125.666 E.00806
; LINE_WIDTH: 0.378961
G1 X119.916 Y125.485 E.00483
; LINE_WIDTH: 0.416658
G1 X119.898 Y125.371 E.00342
; LINE_WIDTH: 0.451172
G1 X119.882 Y125.276 E.00309
; LINE_WIDTH: 0.46934
G1 X119.82 Y124.932 E.01178
; WIPE_START
G1 F10552.981
G1 X119.882 Y125.276 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I.552 J-1.084 P1  F30000
G1 X118.422 Y124.532 Z1.8
G1 Z1.4
G1 E.4 F1800
; LINE_WIDTH: 0.145199
G1 F1260
G3 X118.718 Y124.753 I-4.858 J6.836 E.00298
; LINE_WIDTH: 0.102566
G1 X118.773 Y124.799 E.00034
G1 X118.657 Y124.638 F30000
; LINE_WIDTH: 0.186445
G1 F1260
G1 X118.376 Y124.588 E.00324
; LINE_WIDTH: 0.105746
G1 X118.119 Y124.565 E.00128
G2 X116.698 Y126.607 I-.115 J1.435 E.0149
; LINE_WIDTH: 0.104903
G1 X116.701 Y126.613 E.00003
G2 X118.253 Y127.426 I1.324 J-.64 E.00919
; LINE_WIDTH: 0.140405
G1 X118.381 Y127.412 E.00099
; LINE_WIDTH: 0.186982
G1 X118.657 Y127.362 E.0032
G1 X118.773 Y127.202 F30000
; LINE_WIDTH: 0.111106
G1 F1260
G1 X118.699 Y127.26 E.00051
; LINE_WIDTH: 0.146573
G3 X118.426 Y127.468 I-3.551 J-4.395 E.00281
; WIPE_START
G1 F15000
G1 X118.699 Y127.26 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z1.8 I-.013 J1.217 P1  F30000
G1 X137.578 Y127.468 Z1.8
G1 Z1.4
G1 E.4 F1800
; LINE_WIDTH: 0.1449
G1 F1260
G3 X137.279 Y127.245 I5.956 J-8.303 E.003
; LINE_WIDTH: 0.102311
G1 X137.227 Y127.201 E.00032
G1 X137.343 Y127.362 F30000
; LINE_WIDTH: 0.186446
G1 F1260
G1 X137.624 Y127.412 E.00324
; LINE_WIDTH: 0.110313
G1 X137.876 Y127.434 E.00135
G1 X138.125 Y127.431 E.00133
G1 X138.372 Y127.388 E.00133
G1 X138.607 Y127.302 E.00133
; LINE_WIDTH: 0.104327
G1 X138.613 Y127.299 E.00003
G2 X137.747 Y124.574 I-.623 J-1.302 E.02006
; LINE_WIDTH: 0.140405
G1 X137.619 Y124.588 E.00099
; LINE_WIDTH: 0.186984
G1 X137.343 Y124.638 E.0032
G1 X137.227 Y124.799 F30000
; LINE_WIDTH: 0.102307
G1 F1260
G1 X137.279 Y124.755 E.00032
; LINE_WIDTH: 0.1449
G3 X137.577 Y124.532 I6.61 J8.544 E.00299
; CHANGE_LAYER
; Z_HEIGHT: 1.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.279 Y124.755 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 8/74
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z1.8 I0 J-1.217 P1  F30000
G1 X120.298 Y124.748 Z1.8
G1 Z1.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1213
G1 X120.298 Y127.252 E.08053
G1 X119.024 Y127.252 E.04096
G2 X119.024 Y124.748 I-1.084 J-1.252 E.09131
G1 X120.238 Y124.748 E.03902
; WIPE_START
G1 F11054.348
G1 X120.262 Y125.748 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I-.34 J-1.169 P1  F30000
G1 X117.012 Y126.692 Z2
G1 Z1.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1213
M204 S5000
G3 X117.899 Y124.794 I.988 J-.694 E.07555
G1 X118.101 Y124.794 E.00601
G3 X117.047 Y126.74 I-.101 J1.204 E.14273
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.903 Y126.511 E-.10275
G1 X116.809 Y126.213 E-.11907
G1 X116.79 Y126 E-.08117
G1 X116.816 Y125.799 E-.07702
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I-1.082 J.558 P1  F30000
G1 X120.69 Y133.31 Z2
G1 Z1.6
G1 E.4 F1800
G1 F1213
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
M73 P12 R14
G1 E-.02 F1800
G17
G3 Z2 I.514 J1.103 P1  F30000
G1 X136.976 Y124.748 Z2
G1 Z1.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1213
G1 X136.772 Y124.97 E.00968
G2 X136.976 Y127.252 I1.276 J1.037 E.08153
G1 X135.702 Y127.252 E.04096
G1 X135.702 Y124.748 E.08053
G1 X136.916 Y124.748 E.03903
; WIPE_START
G1 F11054.348
G1 X136.772 Y124.97 E-.10039
G1 X136.687 Y125.081 E-.05313
G1 X136.548 Y125.323 E-.10617
G1 X136.452 Y125.585 E-.10616
G1 X136.445 Y125.622 E-.01415
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I.093 J1.213 P1  F30000
G1 X139.058 Y125.421 Z2
G1 Z1.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1213
M204 S5000
G1 X139.096 Y125.489 E.00232
G3 X137.899 Y124.794 I-1.096 J.509 E.18219
G1 X138.101 Y124.794 E.00601
G3 X138.991 Y125.306 I-.101 J1.204 E.03159
G1 X139.027 Y125.369 E.00217
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.096 Y125.489 E-.05242
G1 X139.169 Y125.687 E-.08012
G1 X139.21 Y126 E-.12006
G1 X139.169 Y126.313 E-.12006
G1 X139.162 Y126.331 E-.00735
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I.126 J-1.21 P1  F30000
G1 X120.21 Y124.356 Z2
G1 Z1.6
G1 E.4 F1800
G1 F1213
M204 S5000
G1 X120.21 Y118.21 E.18306
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.356 E.18305
G1 X137.995 Y124.356 E.06569
G3 X137.995 Y127.644 I.003 J1.644 E.15402
G1 X135.79 Y127.644 E.06569
G1 X135.79 Y133.79 E.18306
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46406
G1 X120.21 Y127.644 E.18305
G1 X118.005 Y127.644 E.06569
G3 X118.005 Y124.356 I-.003 J-1.644 E.15402
G1 X120.15 Y124.356 E.06391
M204 S10000
G1 X120.45 Y124.552 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130734
G1 F1213
G1 X120.45 Y118.494 E.04202
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10439
G1 X135.55 Y124.552 E.04227
; WIPE_START
G1 F15000
G1 X135.549 Y123.552 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I-1.008 J.682 P1  F30000
G1 X136.496 Y124.951 Z2
G1 Z1.6
G1 E.4 F1800
; LINE_WIDTH: 0.444333
G1 F1213
G1 X136.172 Y125.158 E.01217
; LINE_WIDTH: 0.479721
G1 X136.136 Y125.182 E.0015
G1 X136.112 Y125.303 E.00427
; LINE_WIDTH: 0.452485
G1 X136.109 Y125.321 E.00059
; LINE_WIDTH: 0.425053
G1 X136.085 Y125.479 E.00482
; LINE_WIDTH: 0.379649
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342023
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.381156
G1 X136.085 Y126.521 E.00465
; LINE_WIDTH: 0.425041
G1 X136.109 Y126.679 E.00482
; LINE_WIDTH: 0.452464
G1 X136.174 Y127.049 E.01214
G1 X135.55 Y127.448 F30000
; LINE_WIDTH: 0.130902
G1 F1213
G1 X135.55 Y133.506 E.0421
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.448 E.04235
G1 X119.826 Y127.049 F30000
; LINE_WIDTH: 0.452459
G1 F1213
G1 X119.891 Y126.679 E.01214
; LINE_WIDTH: 0.425047
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.379671
G1 X119.936 Y126.334 E.00501
; LINE_WIDTH: 0.342019
G1 X119.95 Y125.994 E.00805
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381156
G1 X119.915 Y125.479 E.00465
; LINE_WIDTH: 0.425037
G1 X119.891 Y125.321 E.00482
; LINE_WIDTH: 0.45247
G1 X119.826 Y124.951 E.01214
; WIPE_START
G1 F10987.67
G1 X119.891 Y125.321 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I.573 J-1.074 P1  F30000
G1 X118.448 Y124.552 Z2
G1 Z1.6
G1 E.4 F1800
; LINE_WIDTH: 0.144499
G1 F1213
G3 X118.718 Y124.753 I-4.251 J5.99 E.0027
; LINE_WIDTH: 0.102553
G1 X118.773 Y124.799 E.00034
G1 X118.669 Y124.65 F30000
; LINE_WIDTH: 0.182148
G1 F1213
G1 X118.501 Y124.617 E.00188
; LINE_WIDTH: 0.152978
G1 X118.374 Y124.597 E.00111
; LINE_WIDTH: 0.111881
G1 X118.15 Y124.577 E.00122
; WIPE_START
G1 F15000
G1 X118.374 Y124.597 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I-1.213 J-.096 P1  F30000
G1 X118.15 Y127.423 Z2
G1 Z1.6
G1 E.4 F1800
; LINE_WIDTH: 0.111884
G1 F1213
G1 X118.374 Y127.403 E.00123
; LINE_WIDTH: 0.152956
G1 X118.5 Y127.383 E.00111
; LINE_WIDTH: 0.182112
G1 X118.668 Y127.35 E.00188
G1 X118.773 Y127.202 F30000
; LINE_WIDTH: 0.102481
G1 F1213
G1 X118.718 Y127.247 E.00033
; LINE_WIDTH: 0.144337
G3 X118.449 Y127.448 I-4.796 J-6.149 E.0027
; WIPE_START
G1 F15000
G1 X118.718 Y127.247 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I-.013 J1.217 P1  F30000
G1 X137.551 Y127.448 Z2
G1 Z1.6
G1 E.4 F1800
; LINE_WIDTH: 0.144019
G1 F1213
G3 X137.279 Y127.245 I5.603 J-7.791 E.00271
; LINE_WIDTH: 0.102241
G1 X137.227 Y127.202 E.00032
G1 X137.332 Y127.35 F30000
; LINE_WIDTH: 0.182404
G1 F1213
G1 X137.494 Y127.382 E.00182
; LINE_WIDTH: 0.154483
G1 X137.622 Y127.402 E.00115
; LINE_WIDTH: 0.11227
G1 X137.85 Y127.423 E.00125
; WIPE_START
G1 F15000
G1 X137.622 Y127.402 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2 I1.213 J.098 P1  F30000
G1 X137.85 Y124.577 Z2
G1 Z1.6
G1 E.4 F1800
; LINE_WIDTH: 0.112275
G1 F1213
G1 X137.622 Y124.598 E.00125
; LINE_WIDTH: 0.154449
G1 X137.494 Y124.618 E.00114
; LINE_WIDTH: 0.182414
G1 X137.332 Y124.65 E.00182
G1 X137.227 Y124.798 F30000
; LINE_WIDTH: 0.102247
G1 F1213
G1 X137.279 Y124.755 E.00032
; LINE_WIDTH: 0.14403
G3 X137.551 Y124.552 I5.907 J7.631 E.00271
; CHANGE_LAYER
; Z_HEIGHT: 1.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.279 Y124.755 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 9/74
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z2 I-.001 J-1.217 P1  F30000
G1 X120.298 Y124.767 Z2
G1 Z1.8
M73 P13 R14
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1202
G1 X120.298 Y127.233 E.07928
G1 X119.043 Y127.233 E.04036
G2 X119.043 Y124.767 I-1.081 J-1.233 E.08971
G1 X120.238 Y124.767 E.03844
; WIPE_START
G1 F11054.348
G1 X120.262 Y125.767 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I-.331 J-1.171 P1  F30000
G1 X117.005 Y126.688 Z2.2
G1 Z1.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1202
M204 S5000
G1 X116.906 Y126.51 E.00605
G3 X117.899 Y124.794 I1.094 J-.513 E.06928
G1 X118.101 Y124.794 E.00601
G3 X117.042 Y126.734 I-.101 J1.204 E.14297
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.906 Y126.51 E-.09959
G1 X116.83 Y126.309 E-.08178
G1 X116.79 Y126 E-.11836
G1 X116.808 Y125.79 E-.08014
G1 X116.808 Y125.79 E-.00012
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I-1.081 J.558 P1  F30000
G1 X120.69 Y133.31 Z2.2
G1 Z1.8
G1 E.4 F1800
G1 F1202
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
M73 P13 R13
G1 E-.02 F1800
G17
G3 Z2.2 I.513 J1.103 P1  F30000
G1 X136.957 Y124.767 Z2.2
G1 Z1.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1202
G1 X136.772 Y124.97 E.00882
G2 X136.957 Y127.233 I1.27 J1.035 E.08065
G1 X135.702 Y127.233 E.04037
G1 X135.702 Y124.767 E.07928
G1 X136.897 Y124.767 E.03844
; WIPE_START
G1 F11054.348
G1 X136.772 Y124.97 E-.09042
G1 X136.687 Y125.081 E-.05314
G1 X136.548 Y125.323 E-.10615
G1 X136.448 Y125.598 E-.11118
G1 X136.439 Y125.647 E-.0191
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I.108 J1.212 P1  F30000
G1 X139.054 Y125.415 Z2.2
G1 Z1.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1202
M204 S5000
G1 X139.097 Y125.489 E.00253
G3 X137.899 Y124.794 I-1.097 J.511 E.1825
G1 X138.101 Y124.794 E.00601
G3 X138.991 Y125.306 I-.101 J1.206 E.0316
G1 X139.024 Y125.363 E.00197
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.097 Y125.489 E-.05506
G1 X139.169 Y125.687 E-.08015
G1 X139.21 Y126 E-.12006
G1 X139.169 Y126.313 E-.12005
G1 X139.165 Y126.325 E-.00468
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I.125 J-1.211 P1  F30000
G1 X120.21 Y124.375 Z2.2
G1 Z1.8
G1 E.4 F1800
G1 F1202
M204 S5000
G1 X120.21 Y118.21 E.18364
G1 X135.79 Y118.211 E.46406
G1 X135.79 Y124.375 E.18363
G1 X137.995 Y124.375 E.06569
G3 X137.995 Y127.625 I.003 J1.625 E.1522
G1 X135.79 Y127.625 E.06569
G1 X135.79 Y133.79 E.18364
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46408
G1 X120.21 Y127.625 E.18364
G1 X118.004 Y127.625 E.06569
G3 X118.004 Y124.375 I-.003 J-1.625 E.1522
G1 X120.15 Y124.375 E.06391
M204 S10000
G1 X120.45 Y124.571 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130739
G1 F1202
G1 X120.45 Y118.494 E.04216
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10439
G1 X135.55 Y124.571 E.04241
G1 X136.171 Y124.971 F30000
; LINE_WIDTH: 0.452459
M73 P14 R13
G1 F1202
G1 X136.109 Y125.321 E.0115
; LINE_WIDTH: 0.435821
G1 X136.095 Y125.409 E.00275
; LINE_WIDTH: 0.405481
G1 X136.079 Y125.519 E.0032
; LINE_WIDTH: 0.365334
G1 X136.055 Y125.799 E.00716
; LINE_WIDTH: 0.339781
G2 X136.065 Y126.348 I4.315 J.191 E.01289
; LINE_WIDTH: 0.381173
G1 X136.085 Y126.522 E.00466
; LINE_WIDTH: 0.425055
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.452425
G1 X136.171 Y127.029 E.0115
G1 X135.55 Y127.429 F30000
; LINE_WIDTH: 0.130901
G1 F1202
G1 X135.55 Y133.506 E.04224
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.429 E.04249
G1 X119.822 Y127.029 F30000
; LINE_WIDTH: 0.475283
G1 F1202
G2 X119.891 Y126.679 I-8.07 J-1.777 E.01219
; LINE_WIDTH: 0.435806
G1 X119.905 Y126.591 E.00275
; LINE_WIDTH: 0.405477
G1 X119.921 Y126.481 E.0032
; LINE_WIDTH: 0.365334
G1 X119.945 Y126.201 E.00716
; LINE_WIDTH: 0.339783
G2 X119.935 Y125.652 I-4.314 J-.191 E.01289
; LINE_WIDTH: 0.381161
G1 X119.915 Y125.479 E.00466
; LINE_WIDTH: 0.425046
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.452448
G1 X119.829 Y124.971 E.0115
; WIPE_START
G1 F10988.274
G1 X119.891 Y125.321 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I.57 J-1.075 P1  F30000
G1 X118.476 Y124.571 Z2.2
G1 Z1.8
G1 E.4 F1800
; LINE_WIDTH: 0.144131
G1 F1202
G3 X118.719 Y124.753 I-4.07 J5.694 E.00242
; LINE_WIDTH: 0.102775
G1 X118.774 Y124.8 E.00034
G1 X118.677 Y124.658 F30000
; LINE_WIDTH: 0.145097
G1 F1202
G2 X118.372 Y124.607 I-1.526 J8.157 E.0025
; LINE_WIDTH: 0.105452
G1 X118.267 Y124.595 E.00052
; WIPE_START
G1 F15000
G1 X118.372 Y124.607 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I-1.216 J-.045 P1  F30000
G1 X118.267 Y127.405 Z2.2
G1 Z1.8
G1 E.4 F1800
; LINE_WIDTH: 0.105453
G1 F1202
G1 X118.372 Y127.393 E.00052
; LINE_WIDTH: 0.145101
G2 X118.677 Y127.342 I-1.332 J-8.937 E.0025
G1 X118.775 Y127.2 F30000
; LINE_WIDTH: 0.102922
G1 F1202
G1 X118.719 Y127.247 E.00035
; LINE_WIDTH: 0.144438
G3 X118.477 Y127.429 I-4.413 J-5.638 E.00243
; WIPE_START
G1 F15000
G1 X118.719 Y127.247 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I-.012 J1.217 P1  F30000
G1 X137.524 Y127.429 Z2.2
G1 Z1.8
G1 E.4 F1800
; LINE_WIDTH: 0.143955
G1 F1202
G3 X137.279 Y127.246 I5.317 J-7.353 E.00244
; LINE_WIDTH: 0.102625
G1 X137.225 Y127.2 E.00033
G1 X137.323 Y127.342 F30000
; LINE_WIDTH: 0.145419
G1 F1202
G2 X137.625 Y127.393 I1.229 J-6.38 E.00248
; LINE_WIDTH: 0.105712
G1 X137.733 Y127.405 E.00054
; WIPE_START
G1 F15000
G1 X137.625 Y127.393 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.2 I1.216 J.047 P1  F30000
G1 X137.733 Y124.595 Z2.2
G1 Z1.8
G1 E.4 F1800
; LINE_WIDTH: 0.105707
G1 F1202
G1 X137.625 Y124.607 E.00054
; LINE_WIDTH: 0.145404
G2 X137.323 Y124.658 I1.016 J7.014 E.00248
G1 X137.225 Y124.8 F30000
; LINE_WIDTH: 0.102625
G1 F1202
G1 X137.279 Y124.754 E.00033
; LINE_WIDTH: 0.143957
G3 X137.524 Y124.571 I5.578 J7.192 E.00244
; CHANGE_LAYER
; Z_HEIGHT: 2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.279 Y124.754 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 10/74
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z2.2 I-.002 J-1.217 P1  F30000
G1 X120.298 Y124.787 Z2.2
G1 Z2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1209
G1 X120.298 Y127.213 E.07803
G1 X119.087 Y127.213 E.03893
G2 X119.597 Y126.14 I-1.337 J-1.292 E.03889
G2 X119.313 Y125.081 I-1.701 J-.112 E.03589
G1 X119.087 Y124.787 E.01192
G1 X120.238 Y124.787 E.037
; WIPE_START
G1 F11054.348
G1 X120.263 Y125.786 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I-.322 J-1.174 P1  F30000
G1 X117.001 Y126.681 Z2.4
G1 Z2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1209
M204 S5000
G1 X116.913 Y126.507 E.00581
G3 X117.939 Y124.792 I1.095 J-.509 E.07008
G3 X118.105 Y124.794 I.072 J.949 E.00498
G3 X117.042 Y126.723 I-.097 J1.204 E.14345
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.913 Y126.507 E-.09551
G1 X116.808 Y126.21 E-.11964
G1 X116.79 Y126 E-.08014
G1 X116.809 Y125.787 E-.08126
G1 X116.811 Y125.778 E-.00345
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I-1.082 J.557 P1  F30000
G1 X120.69 Y133.31 Z2.4
G1 Z2
G1 E.4 F1800
G1 F1209
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I.513 J1.103 P1  F30000
G1 X136.913 Y124.787 Z2.4
G1 Z2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1209
G1 X136.687 Y125.081 E.01191
G2 X136.687 Y126.919 I1.347 J.919 E.06281
G1 X136.913 Y127.213 E.01191
G1 X135.702 Y127.213 E.03893
G1 X135.702 Y124.787 E.07803
G1 X136.853 Y124.787 E.037
; WIPE_START
G1 F11054.348
G1 X136.687 Y125.081 E-.12819
G1 X136.548 Y125.323 E-.10615
G1 X136.452 Y125.585 E-.10618
G1 X136.429 Y125.687 E-.03949
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I.132 J1.21 P1  F30000
G1 X139.051 Y125.401 Z2.4
G1 Z2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1209
M204 S5000
G1 X139.142 Y125.584 E.00611
G3 X137.939 Y124.792 I-1.134 J.414 E.18001
G3 X138.105 Y124.794 I.072 J.949 E.00498
G3 X139.026 Y125.349 I-.097 J1.204 E.03317
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.142 Y125.584 E-.09985
G1 X139.192 Y125.79 E-.0804
G1 X139.21 Y126 E-.08015
G1 X139.169 Y126.312 E-.1196
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I.122 J-1.211 P1  F30000
G1 X120.21 Y124.395 Z2.4
G1 Z2
G1 E.4 F1800
G1 F1209
M204 S5000
G1 X120.21 Y118.21 E.18422
G1 X135.79 Y118.211 E.46408
G1 X135.79 Y124.395 E.1842
G1 X137.995 Y124.395 E.06569
M73 P15 R13
G3 X137.995 Y127.605 I-.002 J1.605 E.15012
G1 X135.79 Y127.605 E.06569
G1 X135.79 Y133.79 E.18422
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46406
G1 X120.21 Y127.605 E.18421
G1 X118.005 Y127.605 E.06569
G3 X118.005 Y124.395 I.002 J-1.605 E.15012
G1 X120.15 Y124.395 E.0639
M204 S10000
G1 X120.45 Y124.591 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130723
G1 F1209
G1 X120.45 Y118.494 E.04229
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10437
G1 X135.55 Y124.591 E.04254
G1 X136.174 Y124.99 F30000
; LINE_WIDTH: 0.472158
G1 F1209
G2 X136.109 Y125.321 I7.713 J1.696 E.01143
; LINE_WIDTH: 0.42506
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.379659
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342023
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.381156
G1 X136.085 Y126.521 E.00465
; LINE_WIDTH: 0.425041
G1 X136.109 Y126.679 E.00482
; LINE_WIDTH: 0.452464
G1 X136.167 Y127.01 E.01086
G1 X135.55 Y127.409 F30000
; LINE_WIDTH: 0.130899
G1 F1209
G1 X135.55 Y133.506 E.04237
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10458
G1 X120.45 Y127.409 E.04262
G1 X119.826 Y127.01 F30000
; LINE_WIDTH: 0.472136
G1 F1209
G2 X119.891 Y126.679 I-7.44 J-1.643 E.01143
; LINE_WIDTH: 0.425035
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.379672
G1 X119.936 Y126.334 E.00501
; LINE_WIDTH: 0.34202
G1 X119.95 Y125.994 E.00805
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381165
G1 X119.915 Y125.479 E.00466
; LINE_WIDTH: 0.42505
G1 X119.891 Y125.321 E.00482
; LINE_WIDTH: 0.452484
G1 X119.833 Y124.99 E.01086
; WIPE_START
G1 F10987.308
G1 X119.891 Y125.321 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I.598 J-1.06 P1  F30000
G1 X118.76 Y124.683 Z2.4
G1 Z2
G1 E.4 F1800
; LINE_WIDTH: 0.126882
G1 F1209
G2 X118.352 Y124.614 I-1.718 J8.92 E.00275
G1 X118.354 Y124.601 F30000
; LINE_WIDTH: 0.186732
G1 F1209
G3 X118.771 Y124.697 I-2.048 J9.857 E.00487
G1 X118.875 Y124.87 F30000
; LINE_WIDTH: 0.102525
G1 F1209
G1 X118.824 Y124.82 E.00033
; LINE_WIDTH: 0.144605
G2 X118.567 Y124.591 I-5.453 J5.859 E.00277
; WIPE_START
G1 F15000
G1 X118.824 Y124.82 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I-1.217 J-.031 P1  F30000
G1 X118.76 Y127.317 Z2.4
G1 Z2
G1 E.4 F1800
; LINE_WIDTH: 0.126883
G1 F1209
G3 X118.352 Y127.386 I-1.717 J-8.914 E.00275
G1 X118.354 Y127.399 F30000
; LINE_WIDTH: 0.186734
G1 F1209
G2 X118.771 Y127.303 I-2.045 J-9.841 E.00487
G1 X118.875 Y127.13 F30000
; LINE_WIDTH: 0.102514
G1 F1209
G1 X118.824 Y127.18 E.00033
; LINE_WIDTH: 0.144609
G3 X118.567 Y127.409 I-5.471 J-5.879 E.00277
; WIPE_START
G1 F15000
G1 X118.824 Y127.18 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I-.015 J1.217 P1  F30000
G1 X137.433 Y127.409 Z2.4
G1 Z2
G1 E.4 F1800
; LINE_WIDTH: 0.144347
G1 F1209
G3 X137.174 Y127.178 I6.382 J-7.417 E.00279
; LINE_WIDTH: 0.102303
G1 X137.125 Y127.129 E.00032
G1 X137.229 Y127.303 F30000
; LINE_WIDTH: 0.186738
G1 F1209
G2 X137.646 Y127.399 I2.455 J-9.709 E.00487
G1 X137.648 Y127.386 F30000
; LINE_WIDTH: 0.126884
G1 F1209
G3 X137.24 Y127.317 I1.308 J-8.982 E.00275
; WIPE_START
G1 F15000
G1 X137.648 Y127.386 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.4 I1.203 J-.182 P1  F30000
G1 X137.24 Y124.683 Z2.4
G1 Z2
G1 E.4 F1800
; LINE_WIDTH: 0.126886
G1 F1209
G3 X137.648 Y124.614 I1.719 J8.926 E.00275
G1 X137.646 Y124.601 F30000
; LINE_WIDTH: 0.186738
G1 F1209
G2 X137.229 Y124.697 I2.057 J9.897 E.00487
G1 X137.125 Y124.87 F30000
; LINE_WIDTH: 0.102281
G1 F1209
G1 X137.174 Y124.822 E.00032
; LINE_WIDTH: 0.144341
G3 X137.433 Y124.591 I6.642 J7.188 E.00279
; CHANGE_LAYER
; Z_HEIGHT: 2.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.174 Y124.822 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 11/74
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z2.4 I.001 J-1.217 P1  F30000
G1 X120.298 Y124.806 Z2.4
G1 Z2.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1198
G1 X120.298 Y127.194 E.07677
G1 X119.102 Y127.194 E.03845
G2 X119.548 Y125.585 I-1.254 J-1.214 E.05597
G2 X119.102 Y124.806 I-1.883 J.561 E.02911
G1 X120.238 Y124.806 E.03652
; WIPE_START
G1 F11054.348
G1 X120.263 Y125.806 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I-.313 J-1.176 P1  F30000
G1 X116.998 Y126.674 Z2.6
G1 Z2.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1198
M204 S5000
G1 X116.897 Y126.472 E.00674
G3 X117.934 Y124.793 I1.111 J-.474 E.0688
G3 X118.105 Y124.794 I.076 J.978 E.00513
G3 X117.038 Y126.718 I-.098 J1.204 E.14361
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.897 Y126.472 E-.10785
G1 X116.808 Y126.21 E-.10496
G1 X116.79 Y126 E-.08014
G1 X116.809 Y125.787 E-.08117
G1 X116.813 Y125.772 E-.00588
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I-1.082 J.557 P1  F30000
G1 X120.69 Y133.31 Z2.6
G1 Z2.2
G1 E.4 F1800
G1 F1198
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
M73 P16 R13
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I.513 J1.104 P1  F30000
G1 X136.898 Y124.806 Z2.6
G1 Z2.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1198
G1 X136.687 Y125.081 E.01113
G2 X136.687 Y126.919 I1.347 J.919 E.06281
G1 X136.898 Y127.194 E.01112
G1 X135.702 Y127.194 E.03845
G1 X135.702 Y124.806 E.07677
G1 X136.838 Y124.806 E.03652
; WIPE_START
G1 F11054.348
G1 X136.687 Y125.081 E-.11899
G1 X136.55 Y125.316 E-.10325
G1 X136.452 Y125.585 E-.10907
G1 X136.424 Y125.71 E-.0487
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I.145 J1.208 P1  F30000
G1 X139.048 Y125.395 Z2.6
G1 Z2.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1198
M204 S5000
G1 X139.054 Y125.395 E.00018
G3 X137.934 Y124.793 I-1.046 J.603 E.18611
G3 X138.105 Y124.794 I.076 J.978 E.00513
G3 X138.93 Y125.219 I-.098 J1.204 E.02837
G1 X139.014 Y125.345 E.0045
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.054 Y125.395 E-.02418
G1 X139.137 Y125.586 E-.07933
G1 X139.192 Y125.79 E-.08017
G1 X139.21 Y126 E-.08014
G1 X139.17 Y126.303 E-.11618
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I.121 J-1.211 P1  F30000
G1 X120.21 Y124.414 Z2.6
G1 Z2.2
G1 E.4 F1800
G1 F1198
M204 S5000
G1 X120.21 Y118.21 E.1848
G1 X135.79 Y118.211 E.46407
G1 X135.79 Y124.414 E.18478
G1 X137.995 Y124.414 E.06569
G3 X137.995 Y127.586 I0 J1.586 E.1484
G1 X135.79 Y127.586 E.06569
G1 X135.786 Y133.79 E.1848
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46396
G1 X120.21 Y127.586 E.1848
G1 X118.005 Y127.586 E.06569
G3 X118.005 Y124.414 I0 J-1.586 E.1484
G1 X120.15 Y124.414 E.0639
M204 S10000
G1 X120.45 Y124.61 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130734
G1 F1198
G1 X120.45 Y118.494 E.04243
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10439
G1 X135.55 Y124.61 E.04268
G1 X136.17 Y125.01 F30000
; LINE_WIDTH: 0.469037
G1 F1198
G2 X136.109 Y125.321 I7.223 J1.589 E.01068
; LINE_WIDTH: 0.425051
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.379658
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342019
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.38115
G1 X136.085 Y126.521 E.00466
; LINE_WIDTH: 0.425049
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.469029
G2 X136.17 Y126.99 I7.275 J-1.275 E.01068
G1 X135.55 Y127.39 F30000
; LINE_WIDTH: 0.13089
G1 F1198
G1 X135.55 Y133.506 E.0425
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10457
G1 X120.45 Y127.39 E.04275
G1 X119.836 Y126.99 F30000
; LINE_WIDTH: 0.452431
G1 F1198
M73 P17 R13
G1 X119.891 Y126.679 E.01023
; LINE_WIDTH: 0.425025
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.379663
G1 X119.936 Y126.334 E.00501
; LINE_WIDTH: 0.34202
G1 X119.95 Y125.994 E.00805
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381188
G1 X119.915 Y125.478 E.00466
; LINE_WIDTH: 0.425032
G1 X119.891 Y125.321 E.0048
; LINE_WIDTH: 0.466558
G1 X119.874 Y125.231 E.00309
; LINE_WIDTH: 0.471737
G1 X119.855 Y125.218 E.00078
; LINE_WIDTH: 0.427078
G2 X119.533 Y125.01 I-6.73 J10.043 E.01162
G1 X118.768 Y124.694 F30000
; LINE_WIDTH: 0.111426
G1 F1198
G2 X118.413 Y124.633 I-1.625 J8.453 E.00195
G1 X118.415 Y124.625 F30000
; LINE_WIDTH: 0.169208
G1 F1198
G3 X118.781 Y124.71 I-1.785 J8.531 E.00375
G1 X118.875 Y124.87 F30000
; LINE_WIDTH: 0.102518
G1 F1198
G1 X118.824 Y124.82 E.00033
; LINE_WIDTH: 0.143776
G2 X118.589 Y124.61 I-4.993 J5.357 E.00251
; WIPE_START
G1 F15000
G1 X118.824 Y124.82 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I-1.217 J.026 P1  F30000
G1 X118.875 Y127.13 Z2.6
G1 Z2.2
G1 E.4 F1800
; LINE_WIDTH: 0.102515
G1 F1198
G1 X118.824 Y127.18 E.00033
; LINE_WIDTH: 0.14517
G3 X118.587 Y127.39 I-3.767 J-4.014 E.00256
G1 X118.413 Y127.367 F30000
; LINE_WIDTH: 0.104817
G1 F1198
G1 X118.491 Y127.355 E.00039
; LINE_WIDTH: 0.14167
G2 X118.777 Y127.295 I-1.941 J-9.953 E.00228
; WIPE_START
G1 F15000
G1 X118.491 Y127.355 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I-.002 J1.217 P1  F30000
G1 X137.411 Y127.39 Z2.6
G1 Z2.2
G1 E.4 F1800
; LINE_WIDTH: 0.14347
G1 F1198
G3 X137.174 Y127.178 I6.058 J-7.021 E.00253
; LINE_WIDTH: 0.102289
G1 X137.125 Y127.13 E.00032
G1 X137.219 Y127.29 F30000
; LINE_WIDTH: 0.169214
G1 F1198
G2 X137.585 Y127.375 I2.161 J-8.493 E.00375
G1 X137.587 Y127.367 F30000
; LINE_WIDTH: 0.111426
G1 F1198
G3 X137.231 Y127.306 I1.268 J-8.505 E.00195
; WIPE_START
G1 F15000
G1 X137.587 Y127.367 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.6 I1.206 J-.16 P1  F30000
G1 X137.231 Y124.694 Z2.6
G1 Z2.2
G1 E.4 F1800
; LINE_WIDTH: 0.111429
G1 F1198
G3 X137.587 Y124.633 I1.618 J8.411 E.00195
G1 X137.585 Y124.625 F30000
; LINE_WIDTH: 0.169179
G1 F1198
G2 X137.219 Y124.71 I1.78 J8.508 E.00375
G1 X137.125 Y124.87 F30000
; LINE_WIDTH: 0.102275
G1 F1198
G1 X137.174 Y124.822 E.00032
; LINE_WIDTH: 0.143532
G3 X137.411 Y124.61 I6.254 J6.763 E.00253
; CHANGE_LAYER
; Z_HEIGHT: 2.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.174 Y124.822 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 12/74
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z2.6 I0 J-1.217 P1  F30000
G1 X120.298 Y124.826 Z2.6
G1 Z2.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1188
G1 X120.298 Y127.174 E.07552
G1 X119.117 Y127.174 E.03797
G2 X119.117 Y124.826 I-1.202 J-1.174 E.08362
G1 X120.238 Y124.826 E.03604
; WIPE_START
G1 F11054.348
G1 X120.263 Y125.825 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I-.301 J-1.179 P1  F30000
G1 X116.993 Y126.659 Z2.8
G1 Z2.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1188
M204 S5000
G1 X116.96 Y126.6 E.002
G3 X117.928 Y124.793 I1.047 J-.602 E.07295
G3 X118.105 Y124.794 I.08 J1.007 E.00528
G3 X117.127 Y126.825 I-.099 J1.204 E.13942
G1 X117.03 Y126.706 E.00457
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.96 Y126.6 E-.04816
G1 X116.863 Y126.414 E-.07995
G1 X116.808 Y126.21 E-.0802
G1 X116.79 Y126 E-.08015
G1 X116.808 Y125.79 E-.08014
G1 X116.816 Y125.761 E-.0114
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I-1.083 J.556 P1  F30000
G1 X120.69 Y133.31 Z2.8
G1 Z2.4
G1 E.4 F1800
G1 F1188
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I.512 J1.104 P1  F30000
G1 X136.883 Y124.826 Z2.8
G1 Z2.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1188
G1 X136.687 Y125.081 E.01034
G2 X136.883 Y127.174 I1.39 J.926 E.07314
G1 X135.702 Y127.174 E.03797
G1 X135.702 Y124.826 E.07552
G1 X136.823 Y124.826 E.03604
; WIPE_START
G1 F11054.348
G1 X136.687 Y125.081 E-.10976
G1 X136.548 Y125.323 E-.1062
G1 X136.452 Y125.585 E-.10617
G1 X136.426 Y125.735 E-.05787
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I.16 J1.206 P1  F30000
G1 X139.044 Y125.389 Z2.8
G1 Z2.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1188
M204 S5000
G1 X139.052 Y125.393 E.00026
G3 X137.928 Y124.793 I-1.045 J.605 E.18606
G3 X138.105 Y124.794 I.08 J1.007 E.00528
G3 X138.93 Y125.22 I-.099 J1.204 E.02836
G1 X139.01 Y125.339 E.00429
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.052 Y125.393 E-.02566
G1 X139.147 Y125.618 E-.09318
G1 X139.206 Y125.895 E-.10721
G1 X139.206 Y126.105 E-.08014
G1 X139.172 Y126.297 E-.07381
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I.119 J-1.211 P1  F30000
G1 X120.21 Y124.434 Z2.8
G1 Z2.4
G1 E.4 F1800
G1 F1188
M204 S5000
G1 X120.21 Y118.21 E.18538
G1 X135.79 Y118.211 E.46407
G1 X135.79 Y124.434 E.18536
G1 X137.995 Y124.434 E.06569
G3 X138.824 Y124.669 I-.004 J1.587 E.02597
G3 X137.995 Y127.566 I-.825 J1.331 E.12075
G1 X135.79 Y127.566 E.06569
G1 X135.79 Y133.79 E.18538
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46408
G1 X120.21 Y127.566 E.18538
G1 X118.005 Y127.566 E.06569
G3 X117.176 Y127.331 I.004 J-1.587 E.02597
M73 P18 R13
G3 X118.005 Y124.434 I.825 J-1.331 E.12075
G1 X120.15 Y124.434 E.0639
M204 S10000
G1 X120.45 Y124.63 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130757
G1 F1188
G1 X120.45 Y118.494 E.04257
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10441
G1 X135.55 Y124.63 E.04282
G1 X136.16 Y125.029 F30000
; LINE_WIDTH: 0.452438
G1 F1188
G1 X136.109 Y125.321 E.00959
; LINE_WIDTH: 0.425016
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.379643
G1 X136.064 Y125.666 E.005
; LINE_WIDTH: 0.342019
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.381164
G1 X136.085 Y126.521 E.00466
; LINE_WIDTH: 0.425065
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.465959
G2 X136.166 Y126.971 I6.95 J-1.221 E.00994
G1 X135.55 Y127.37 F30000
; LINE_WIDTH: 0.130901
G1 F1188
G1 X135.55 Y133.506 E.04264
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y127.37 E.04289
G1 X119.84 Y126.971 F30000
; LINE_WIDTH: 0.452396
G1 F1188
G1 X119.891 Y126.679 E.00959
; LINE_WIDTH: 0.424991
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.379657
G1 X119.936 Y126.334 E.005
; LINE_WIDTH: 0.342016
G1 X119.95 Y125.994 E.00806
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381155
G1 X119.915 Y125.479 E.00465
; LINE_WIDTH: 0.420701
G1 X119.895 Y125.349 E.00391
; LINE_WIDTH: 0.460074
G1 X119.836 Y125.029 E.01073
G1 X118.875 Y124.87 F30000
; LINE_WIDTH: 0.102526
G1 F1188
G1 X118.824 Y124.82 E.00033
; LINE_WIDTH: 0.142902
G2 X118.611 Y124.63 I-4.521 J4.841 E.00226
G1 X118.473 Y124.648 F30000
; LINE_WIDTH: 0.143372
G1 F1188
G1 X118.787 Y124.718 E.00256
; WIPE_START
G1 F15000
G1 X118.473 Y124.648 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I-1.201 J.194 P1  F30000
G1 X118.875 Y127.13 Z2.8
G1 Z2.4
G1 E.4 F1800
; LINE_WIDTH: 0.102521
G1 F1188
G1 X118.824 Y127.18 E.00033
; LINE_WIDTH: 0.142871
G3 X118.611 Y127.37 I-4.493 J-4.812 E.00226
G1 X118.473 Y127.349 F30000
; LINE_WIDTH: 0.132742
G1 F1188
G2 X118.787 Y127.282 I-1.406 J-7.441 E.00228
; WIPE_START
G1 F15000
G1 X118.473 Y127.349 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I.004 J1.217 P1  F30000
G1 X137.213 Y127.282 Z2.8
G1 Z2.4
G1 E.4 F1800
; LINE_WIDTH: 0.143372
G1 F1188
G1 X137.527 Y127.352 E.00255
G1 X137.389 Y127.37 F30000
; LINE_WIDTH: 0.142509
G1 F1188
G3 X137.174 Y127.178 I5.736 J-6.627 E.00227
; LINE_WIDTH: 0.10229
G1 X137.125 Y127.13 E.00032
; WIPE_START
G1 F15000
G1 X137.174 Y127.178 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z2.8 I1.217 J-.025 P1  F30000
G1 X137.125 Y124.87 Z2.8
G1 Z2.4
G1 E.4 F1800
; LINE_WIDTH: 0.102278
G1 F1188
G1 X137.174 Y124.822 E.00032
; LINE_WIDTH: 0.142521
G3 X137.389 Y124.63 I5.979 J6.466 E.00227
G1 X137.527 Y124.651 F30000
; LINE_WIDTH: 0.132742
G1 F1188
G2 X137.213 Y124.718 I1.405 J7.436 E.00228
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.527 Y124.651 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 13/74
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z2.8 I-.014 J-1.217 P1  F30000
G1 X120.298 Y124.845 Z2.8
G1 Z2.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1185
G1 X120.298 Y127.155 E.07427
G1 X119.132 Y127.155 E.03749
G2 X119.132 Y124.845 I-1.203 J-1.155 E.08204
G1 X120.238 Y124.845 E.03556
; WIPE_START
G1 F11054.348
G1 X120.264 Y125.845 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I-.295 J-1.181 P1  F30000
G1 X116.99 Y126.662 Z3
G1 Z2.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1185
M204 S5000
G1 X116.911 Y126.508 E.00514
G3 X117.923 Y124.793 I1.095 J-.51 E.06971
G3 X118.105 Y124.794 I.084 J1.038 E.00543
G3 X117.029 Y126.707 I-.099 J1.204 E.14397
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.911 Y126.508 E-.08793
G1 X116.808 Y126.21 E-.11966
G1 X116.79 Y126 E-.08016
G1 X116.821 Y125.759 E-.09224
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I-1.083 J.555 P1  F30000
G1 X120.69 Y133.31 Z3
G1 Z2.6
G1 E.4 F1800
G1 F1185
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I.511 J1.104 P1  F30000
G1 X136.868 Y124.845 Z3
G1 Z2.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1185
G1 X136.687 Y125.081 E.00955
G2 X136.868 Y127.155 I1.355 J.927 E.07252
G1 X135.702 Y127.155 E.03749
G1 X135.702 Y124.845 E.07427
G1 X136.808 Y124.845 E.03556
; WIPE_START
G1 F11054.348
G1 X136.687 Y125.081 E-.10065
G1 X136.548 Y125.323 E-.10612
G1 X136.452 Y125.585 E-.10619
G1 X136.421 Y125.759 E-.06705
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I.168 J1.205 P1  F30000
G1 X139.037 Y125.394 Z3
G1 Z2.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1185
M204 S5000
G1 X139.1 Y125.487 E.00335
G3 X137.923 Y124.793 I-1.094 J.511 E.18276
G3 X138.105 Y124.794 I.084 J1.038 E.00543
G3 X138.93 Y125.22 I-.099 J1.204 E.02836
M73 P19 R13
G1 X139.005 Y125.343 E.0043
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.1 Y125.487 E-.0655
G1 X139.169 Y125.687 E-.08031
G1 X139.206 Y125.895 E-.08016
G1 X139.206 Y126.105 E-.08015
G1 X139.169 Y126.296 E-.07388
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I.118 J-1.211 P1  F30000
G1 X120.21 Y124.453 Z3
G1 Z2.6
G1 E.4 F1800
G1 F1185
M204 S5000
G1 X120.21 Y118.21 E.18596
G1 X135.79 Y118.21 E.46406
G1 X135.79 Y124.453 E.18594
G1 X137.995 Y124.453 E.06569
G3 X137.995 Y127.547 I.002 J1.547 E.14485
G1 X135.79 Y127.547 E.06569
G1 X135.789 Y133.79 E.18596
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46404
G1 X120.21 Y127.547 E.18594
G1 X118.005 Y127.547 E.06569
G3 X118.005 Y124.453 I-.002 J-1.547 E.14485
G1 X120.15 Y124.453 E.0639
M204 S10000
G1 X120.45 Y124.649 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130753
G1 F1185
G1 X120.45 Y118.494 E.0427
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10441
G1 X135.55 Y124.649 E.04296
G1 X136.163 Y125.049 F30000
; LINE_WIDTH: 0.462871
G1 F1185
M73 P19 R12
G2 X136.109 Y125.321 I6.166 J1.36 E.00921
; LINE_WIDTH: 0.425044
G1 X136.085 Y125.479 E.00482
; LINE_WIDTH: 0.37967
G1 X136.064 Y125.666 E.005
; LINE_WIDTH: 0.342031
G1 X136.05 Y126.006 E.00806
G1 X136.065 Y126.348 E.00809
; LINE_WIDTH: 0.381171
G1 X136.085 Y126.521 E.00465
; LINE_WIDTH: 0.425043
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.462877
G2 X136.163 Y126.951 I6.248 J-1.093 E.00921
G1 X135.55 Y127.351 F30000
; LINE_WIDTH: 0.130879
G1 F1185
G1 X135.542 Y133.542 E.04302
G1 X120.494 Y133.55 E.10456
G1 X120.458 Y133.542 E.00026
G1 X120.45 Y133.506 E.00026
G1 X120.45 Y127.351 E.04277
G1 X119.837 Y126.951 F30000
; LINE_WIDTH: 0.462854
G1 F1185
G2 X119.891 Y126.679 I-6.29 J-1.383 E.00921
; LINE_WIDTH: 0.428521
G1 X119.912 Y126.544 E.00416
; LINE_WIDTH: 0.384067
G1 X119.935 Y126.343 E.00546
; LINE_WIDTH: 0.342241
G1 X119.95 Y125.994 E.00826
G1 X119.935 Y125.652 E.0081
; LINE_WIDTH: 0.381188
G1 X119.915 Y125.479 E.00465
; LINE_WIDTH: 0.425024
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.462851
G2 X119.837 Y125.049 I-6.357 J1.113 E.00921
G1 X118.875 Y124.87 F30000
; LINE_WIDTH: 0.102519
G1 F1185
G1 X118.824 Y124.82 E.00033
; LINE_WIDTH: 0.130966
G1 X118.729 Y124.733 E.0009
; LINE_WIDTH: 0.160813
G1 X118.629 Y124.649 E.00121
G1 X118.519 Y124.671 F30000
; LINE_WIDTH: 0.118605
G1 F1185
G3 X118.797 Y124.731 I-1.122 J5.88 E.0017
; WIPE_START
G1 F15000
G1 X118.519 Y124.671 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I-1.204 J.174 P1  F30000
G1 X118.875 Y127.13 Z3
G1 Z2.6
G1 E.4 F1800
; LINE_WIDTH: 0.102508
G1 F1185
G1 X118.824 Y127.18 E.00033
; LINE_WIDTH: 0.131008
G1 X118.729 Y127.267 E.0009
; LINE_WIDTH: 0.160867
G1 X118.629 Y127.351 E.00121
G1 X118.519 Y127.329 F30000
; LINE_WIDTH: 0.118603
G1 F1185
G2 X118.796 Y127.27 I-1.315 J-6.85 E.00169
; WIPE_START
G1 F15000
G1 X118.519 Y127.329 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I.004 J1.217 P1  F30000
G1 X137.203 Y127.269 Z3
G1 Z2.6
G1 E.4 F1800
; LINE_WIDTH: 0.118603
G1 F1185
G2 X137.48 Y127.329 I1.399 J-5.821 E.0017
G1 X137.371 Y127.351 F30000
; LINE_WIDTH: 0.16047
G1 F1185
G1 X137.268 Y127.264 E.00126
; LINE_WIDTH: 0.129559
G1 X137.174 Y127.178 E.00087
; LINE_WIDTH: 0.102255
G1 X137.126 Y127.13 E.00032
; WIPE_START
G1 F15000
G1 X137.174 Y127.178 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3 I1.217 J-.025 P1  F30000
G1 X137.125 Y124.87 Z3
G1 Z2.6
G1 E.4 F1800
; LINE_WIDTH: 0.102265
G1 F1185
G1 X137.174 Y124.822 E.00032
; LINE_WIDTH: 0.129627
G1 X137.268 Y124.736 E.00087
; LINE_WIDTH: 0.160536
G1 X137.371 Y124.649 E.00126
G1 X137.48 Y124.671 F30000
; LINE_WIDTH: 0.118602
G1 F1185
G2 X137.204 Y124.73 I1.313 J6.839 E.00169
; CHANGE_LAYER
; Z_HEIGHT: 2.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.48 Y124.671 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 14/74
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z3 I-.014 J-1.217 P1  F30000
G1 X120.298 Y124.865 Z3
G1 Z2.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1178
G1 X120.298 Y127.135 E.07302
G1 X119.147 Y127.135 E.03701
G2 X119.147 Y124.865 I-1.209 J-1.135 E.08043
G1 X120.238 Y124.865 E.03508
; WIPE_START
G1 F11054.348
G1 X120.264 Y125.864 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I-.283 J-1.184 P1  F30000
G1 X116.984 Y126.648 Z3.2
G1 Z2.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1178
M204 S5000
G1 X116.959 Y126.601 E.00158
G3 X117.918 Y124.793 I1.046 J-.603 E.07273
G3 X118.105 Y124.794 I.088 J1.066 E.00559
G3 X117.15 Y126.85 I-.1 J1.203 E.13833
G1 X117.022 Y126.694 E.006
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.959 Y126.601 E-.04276
G1 X116.862 Y126.412 E-.08066
G1 X116.808 Y126.21 E-.0795
G1 X116.79 Y126 E-.08014
G1 X116.808 Y125.788 E-.08084
G1 X116.821 Y125.748 E-.01611
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I-1.083 J.554 P1  F30000
G1 X120.69 Y133.31 Z3.2
G1 Z2.8
G1 E.4 F1800
G1 F1178
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
M73 P20 R12
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I.511 J1.105 P1  F30000
G1 X136.853 Y124.865 Z3.2
G1 Z2.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1178
G1 X136.687 Y125.081 E.00876
G2 X136.85 Y127.135 I1.355 J.927 E.07165
G1 X135.702 Y127.135 E.0369
G1 X135.702 Y124.865 E.07302
G1 X136.793 Y124.865 E.03508
; WIPE_START
G1 F11054.348
G1 X136.687 Y125.081 E-.09145
G1 X136.547 Y125.323 E-.10623
G1 X136.452 Y125.585 E-.10608
G1 X136.417 Y125.783 E-.07624
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I.186 J1.203 P1  F30000
G1 X139.037 Y125.379 Z3.2
G1 Z2.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1178
M204 S5000
G1 X139.051 Y125.393 E.00061
G3 X137.918 Y124.793 I-1.045 J.605 E.18578
G3 X138.105 Y124.794 I.088 J1.066 E.00559
G3 X138.929 Y125.22 I-.1 J1.203 E.02835
G1 X139.003 Y125.329 E.00391
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.051 Y125.393 E-.03045
G1 X139.169 Y125.687 E-.12022
G1 X139.206 Y125.895 E-.08018
G1 X139.206 Y126.105 E-.08014
G1 X139.174 Y126.284 E-.06901
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I.116 J-1.211 P1  F30000
G1 X120.21 Y124.472 Z3.2
G1 Z2.8
G1 E.4 F1800
G1 F1178
M204 S5000
G1 X120.21 Y118.21 E.18653
G1 X135.79 Y118.21 E.46408
G1 X135.79 Y124.472 E.18652
G1 X137.995 Y124.472 E.06569
G3 X139.395 Y125.38 I-.015 J1.556 E.05243
G3 X137.995 Y127.528 I-1.397 J.619 E.09057
G1 X135.79 Y127.528 E.06569
G1 X135.79 Y133.79 E.18654
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46407
G1 X120.21 Y127.528 E.18654
G1 X118.005 Y127.528 E.06569
G3 X118.005 Y124.472 I-.003 J-1.528 E.14312
G1 X120.15 Y124.472 E.0639
M204 S10000
G1 X120.45 Y124.668 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130768
G1 F1178
G1 X120.45 Y118.494 E.04285
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10443
G1 X135.55 Y124.668 E.0431
G1 X136.159 Y125.068 F30000
; LINE_WIDTH: 0.459793
G1 F1178
G1 X136.109 Y125.321 E.0085
; LINE_WIDTH: 0.425035
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.379653
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342017
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.38114
G1 X136.085 Y126.521 E.00466
; LINE_WIDTH: 0.425077
G1 X136.109 Y126.679 E.00482
; LINE_WIDTH: 0.45985
G1 X136.159 Y126.932 E.00848
G1 X135.55 Y127.332 F30000
; LINE_WIDTH: 0.130901
G1 F1178
G1 X135.55 Y133.506 E.04291
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
M73 P21 R12
G1 X120.458 Y133.542 E.10458
G1 X120.45 Y127.332 E.04316
G1 X119.841 Y126.932 F30000
; LINE_WIDTH: 0.459786
G1 F1178
G1 X119.891 Y126.679 E.0085
; LINE_WIDTH: 0.425012
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.379677
G1 X119.936 Y126.334 E.00501
; LINE_WIDTH: 0.342018
G1 X119.95 Y125.994 E.00806
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381157
G1 X119.915 Y125.479 E.00466
; LINE_WIDTH: 0.42505
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.459818
G1 X119.841 Y125.068 E.00849
G1 X118.875 Y124.87 F30000
; LINE_WIDTH: 0.102532
G1 F1178
G1 X118.824 Y124.82 E.00033
; LINE_WIDTH: 0.142112
G1 X118.651 Y124.669 E.00181
; WIPE_START
G1 F15000
G1 X118.824 Y124.82 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I-1.217 J.027 P1  F30000
G1 X118.875 Y127.129 Z3.2
G1 Z2.8
G1 E.4 F1800
; LINE_WIDTH: 0.102547
G1 F1178
G1 X118.824 Y127.18 E.00034
; LINE_WIDTH: 0.142156
G1 X118.651 Y127.331 E.00181
; WIPE_START
G1 F15000
G1 X118.824 Y127.18 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I-.005 J1.217 P1  F30000
G1 X137.182 Y127.254 Z3.2
G1 Z2.8
G1 E.4 F1800
; LINE_WIDTH: 0.103471
G1 F1178
G2 X137.434 Y127.31 I1.278 J-5.206 E.00123
G1 X137.34 Y127.331 F30000
; LINE_WIDTH: 0.147659
G1 F1178
G1 X137.174 Y127.183 E.00184
; LINE_WIDTH: 0.106089
G1 X137.108 Y127.116 E.00047
; WIPE_START
G1 F15000
G1 X137.174 Y127.183 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.2 I1.217 J-.026 P1  F30000
G1 X137.125 Y124.871 Z3.2
G1 Z2.8
G1 E.4 F1800
; LINE_WIDTH: 0.102562
G1 F1178
G1 X137.176 Y124.82 E.00034
; LINE_WIDTH: 0.142169
G1 X137.349 Y124.669 E.00181
; CHANGE_LAYER
; Z_HEIGHT: 3
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.176 Y124.82 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 15/74
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z3.2 I-.005 J-1.217 P1  F30000
G1 X120.298 Y124.884 Z3.2
G1 Z3
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1176
G1 X120.298 Y127.116 E.07177
G1 X119.162 Y127.116 E.03654
G2 X119.162 Y124.884 I-1.215 J-1.116 E.07883
G1 X120.238 Y124.884 E.0346
; WIPE_START
G1 F11054.348
G1 X120.265 Y125.884 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I-.277 J-1.185 P1  F30000
G1 X116.983 Y126.649 Z3.4
G1 Z3
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1176
M204 S5000
G1 X116.912 Y126.507 E.00473
G3 X117.913 Y124.794 I1.097 J-.508 E.06933
G1 X118 Y124.79 E.0026
G3 X117.021 Y126.696 I.009 J1.209 E.14793
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.912 Y126.507 E-.0827
G1 X116.808 Y126.21 E-.11967
G1 X116.79 Y126 E-.08014
G1 X116.823 Y125.746 E-.09749
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I-1.084 J.554 P1  F30000
G1 X120.69 Y133.31 Z3.4
G1 Z3
G1 E.4 F1800
G1 F1176
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I.51 J1.105 P1  F30000
G1 X136.838 Y124.884 Z3.4
G1 Z3
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1176
G1 X136.687 Y125.081 E.00797
G2 X136.838 Y127.116 I1.337 J.924 E.07095
G1 X135.702 Y127.116 E.03654
G1 X135.702 Y124.884 E.07177
G1 X136.778 Y124.884 E.0346
; WIPE_START
G1 F11054.348
G1 X136.687 Y125.081 E-.08237
G1 X136.547 Y125.323 E-.10619
G1 X136.452 Y125.585 E-.10607
G1 X136.413 Y125.806 E-.08538
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I.2 J1.2 P1  F30000
G1 X139.028 Y125.37 Z3.4
G1 Z3
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1176
M204 S5000
G1 X139.104 Y125.485 E.00412
G3 X137.913 Y124.794 I-1.095 J.514 E.18271
G1 X138 Y124.79 E.0026
G3 X138.997 Y125.302 I.009 J1.209 E.03472
G1 X139.003 Y125.315 E.00044
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.104 Y125.485 E-.07514
G1 X139.169 Y125.687 E-.08049
G1 X139.21 Y126 E-.12006
G1 X139.188 Y126.228 E-.08712
G1 X139.174 Y126.271 E-.01718
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I.114 J-1.212 P1  F30000
G1 X120.21 Y124.492 Z3.4
G1 Z3
G1 E.4 F1800
G1 F1176
M204 S5000
G1 X120.21 Y118.21 E.18712
G1 X135.79 Y118.21 E.46407
G1 X135.79 Y124.492 E.1871
G1 X137.995 Y124.492 E.06569
G3 X137.995 Y127.508 I-.001 J1.508 E.14104
G1 X135.79 Y127.508 E.06569
G1 X135.789 Y133.79 E.18712
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46404
G1 X120.21 Y127.508 E.1871
M73 P22 R12
G1 X118.005 Y127.508 E.06569
G3 X118.005 Y124.492 I.001 J-1.508 E.14104
G1 X120.15 Y124.492 E.06391
M204 S10000
G1 X120.45 Y124.688 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130763
G1 F1176
G1 X120.45 Y118.494 E.04298
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10442
G1 X135.55 Y124.688 E.04323
G1 X136.155 Y125.088 F30000
; LINE_WIDTH: 0.456767
G1 F1176
G1 X136.109 Y125.321 E.00778
; LINE_WIDTH: 0.425042
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.379681
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342023
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.381162
G1 X136.085 Y126.521 E.00466
; LINE_WIDTH: 0.425052
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.456781
G1 X136.155 Y126.912 E.00778
G1 X135.55 Y127.312 F30000
; LINE_WIDTH: 0.130901
G1 F1176
G1 X135.55 Y133.506 E.04305
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10458
G1 X120.45 Y127.312 E.0433
G1 X119.845 Y126.912 F30000
; LINE_WIDTH: 0.456791
G1 F1176
G1 X119.891 Y126.679 E.00778
; LINE_WIDTH: 0.426508
G1 X119.914 Y126.531 E.00455
; LINE_WIDTH: 0.381944
G1 X119.936 Y126.34 E.00514
; LINE_WIDTH: 0.342165
G1 X119.95 Y125.994 E.0082
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381148
G1 X119.915 Y125.479 E.00466
; LINE_WIDTH: 0.425056
G1 X119.891 Y125.321 E.00481
; LINE_WIDTH: 0.4568
G1 X119.845 Y125.088 E.00778
G1 X118.875 Y124.871 F30000
; LINE_WIDTH: 0.102692
G1 F1176
G1 X118.824 Y124.82 E.00034
; LINE_WIDTH: 0.137155
G1 X118.738 Y124.741 E.00087
G1 X118.607 Y124.706 E.00101
; WIPE_START
G1 F15000
G1 X118.738 Y124.741 E-.20437
G1 X118.824 Y124.82 E-.17563
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I-1.217 J.026 P1  F30000
G1 X118.874 Y127.13 Z3.4
G1 Z3
G1 E.4 F1800
; LINE_WIDTH: 0.102359
G1 F1176
G1 X118.824 Y127.18 E.00033
; LINE_WIDTH: 0.136836
G1 X118.737 Y127.259 E.00087
G1 X118.607 Y127.294 E.001
; WIPE_START
G1 F15000
G1 X118.737 Y127.259 E-.20304
G1 X118.824 Y127.18 E-.17696
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I-.008 J1.217 P1  F30000
G1 X137.393 Y127.294 Z3.4
G1 Z3
G1 E.4 F1800
; LINE_WIDTH: 0.136567
G1 F1176
G1 X137.262 Y127.259 E.001
G1 X137.174 Y127.178 E.00089
; LINE_WIDTH: 0.102206
G1 X137.126 Y127.13 E.00032
; WIPE_START
G1 F15000
G1 X137.174 Y127.178 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.4 I1.217 J-.026 P1  F30000
G1 X137.125 Y124.871 Z3.4
G1 Z3
G1 E.4 F1800
; LINE_WIDTH: 0.102337
G1 F1176
G1 X137.174 Y124.822 E.00032
; LINE_WIDTH: 0.136745
G1 X137.262 Y124.741 E.00089
G1 X137.393 Y124.706 E.001
; CHANGE_LAYER
; Z_HEIGHT: 3.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X137.262 Y124.741 E-.20164
G1 X137.174 Y124.822 E-.17836
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 16/74
; update layer progress
M73 L16
M991 S0 P15 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z3.4 I-.006 J-1.217 P1  F30000
G1 X120.298 Y124.903 Z3.4
G1 Z3.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1179
G1 X120.298 Y127.097 E.07052
G1 X119.2 Y127.097 E.03531
G2 X119.506 Y125.452 I-1.356 J-1.103 E.0561
G2 X119.2 Y124.903 I-2.231 J.886 E.02025
G1 X120.238 Y124.903 E.03338
; WIPE_START
G1 F11054.348
G1 X120.265 Y125.903 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I-.268 J-1.187 P1  F30000
G1 X116.98 Y126.644 Z3.6
G1 Z3.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1179
M204 S5000
G1 X116.909 Y126.507 E.00457
G3 X117.908 Y124.794 I1.098 J-.508 E.06925
G1 X118 Y124.79 E.00275
G3 X117.015 Y126.692 I.007 J1.209 E.148
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.909 Y126.507 E-.08093
G1 X116.808 Y126.21 E-.11933
G1 X116.79 Y126 E-.08014
G1 X116.808 Y125.79 E-.08016
G1 X116.824 Y125.741 E-.01944
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I-1.084 J.554 P1  F30000
G1 X120.69 Y133.31 Z3.6
G1 Z3.2
G1 E.4 F1800
G1 F1179
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I.51 J1.105 P1  F30000
G1 X136.8 Y124.903 Z3.6
G1 Z3.2
M73 P23 R12
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1179
G1 X136.62 Y125.186 E.01076
G2 X136.612 Y126.801 I1.423 J.815 E.05433
G1 X136.8 Y127.097 E.01125
G1 X135.702 Y127.097 E.03531
G1 X135.702 Y124.903 E.07052
G1 X136.74 Y124.903 E.03338
; WIPE_START
G1 F11054.348
G1 X136.62 Y125.186 E-.11652
G1 X136.549 Y125.32 E-.05778
G1 X136.452 Y125.585 E-.10733
G1 X136.422 Y125.722 E-.05316
G1 X136.411 Y125.84 E-.04521
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I.218 J1.197 P1  F30000
G1 X139.024 Y125.364 Z3.6
G1 Z3.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1179
M204 S5000
G1 X139.108 Y125.498 E.00472
G3 X137.908 Y124.794 I-1.101 J.501 E.18221
G1 X138 Y124.79 E.00275
G3 X138.996 Y125.303 I.007 J1.209 E.03468
G1 X138.999 Y125.309 E.00021
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.108 Y125.498 E-.08291
G1 X139.192 Y125.79 E-.11539
G1 X139.21 Y126 E-.08014
G1 X139.175 Y126.265 E-.10157
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I.112 J-1.212 P1  F30000
G1 X120.21 Y124.511 Z3.6
G1 Z3.2
G1 E.4 F1800
G1 F1179
M204 S5000
G1 X120.21 Y118.21 E.1877
G1 X135.79 Y118.21 E.46407
G1 X135.79 Y124.511 E.18768
G1 X137.995 Y124.511 E.06569
G3 X137.995 Y127.489 I-.001 J1.489 E.13923
G1 X135.79 Y127.489 E.06569
G1 X135.79 Y133.79 E.1877
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46406
G1 X120.21 Y127.489 E.18768
G1 X118.005 Y127.489 E.06569
G3 X118.005 Y124.511 I.001 J-1.489 E.13923
G1 X120.15 Y124.511 E.0639
M204 S10000
G1 X120.45 Y124.707 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130779
G1 F1179
G1 X120.45 Y118.494 E.04312
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10444
G1 X135.55 Y124.707 E.04337
; WIPE_START
G1 F15000
G1 X135.549 Y123.707 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I-.698 J.997 P1  F30000
G1 X137.102 Y124.794 Z3.6
G1 Z3.2
G1 E.4 F1800
; LINE_WIDTH: 0.118805
G1 F1179
G3 X137.356 Y124.728 I1.602 J5.611 E.00157
G1 X137.257 Y124.707 F30000
; LINE_WIDTH: 0.162351
G1 F1179
G1 X137.16 Y124.805 E.0013
; LINE_WIDTH: 0.129692
G1 X137.074 Y124.899 E.00087
; LINE_WIDTH: 0.102297
G1 X137.03 Y124.951 E.00032
G1 X136.41 Y125.107 F30000
; LINE_WIDTH: 0.446819
G1 F1179
G1 X136.109 Y125.321 E.0118
; LINE_WIDTH: 0.425016
G1 X136.085 Y125.479 E.00481
; LINE_WIDTH: 0.37966
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342021
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00808
; LINE_WIDTH: 0.381173
G1 X136.085 Y126.521 E.00466
; LINE_WIDTH: 0.425082
G1 X136.109 Y126.679 E.00481
; LINE_WIDTH: 0.44674
G1 X136.41 Y126.893 E.01178
G1 X137.03 Y127.049 F30000
; LINE_WIDTH: 0.102305
G1 F1179
G1 X137.074 Y127.101 E.00032
; LINE_WIDTH: 0.129677
G1 X137.16 Y127.195 E.00087
; LINE_WIDTH: 0.162352
G1 X137.257 Y127.293 E.0013
G1 X137.356 Y127.272 F30000
; LINE_WIDTH: 0.118798
G1 F1179
G3 X137.102 Y127.205 I1.263 J-5.33 E.00157
; WIPE_START
G1 F15000
G1 X137.356 Y127.272 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I-.014 J-1.217 P1  F30000
G1 X135.55 Y127.293 Z3.6
G1 Z3.2
G1 E.4 F1800
; LINE_WIDTH: 0.130901
G1 F1179
G1 X135.55 Y133.506 E.04318
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10458
G1 X120.45 Y127.293 E.04344
; WIPE_START
G1 F15000
G1 X120.451 Y128.293 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.6 I.698 J-.997 P1  F30000
G1 X118.898 Y127.206 Z3.6
G1 Z3.2
G1 E.4 F1800
; LINE_WIDTH: 0.118805
G1 F1179
G3 X118.644 Y127.272 I-1.6 J-5.604 E.00157
G1 X118.743 Y127.293 F30000
; LINE_WIDTH: 0.162694
G1 F1179
G1 X118.836 Y127.199 E.00126
; LINE_WIDTH: 0.131028
G1 X118.924 Y127.104 E.0009
; LINE_WIDTH: 0.102534
G1 X118.97 Y127.049 E.00033
G1 X119.59 Y126.893 F30000
; LINE_WIDTH: 0.446806
G1 F1179
G1 X119.891 Y126.679 E.0118
; LINE_WIDTH: 0.425025
G1 X119.915 Y126.521 E.00481
; LINE_WIDTH: 0.379664
G1 X119.936 Y126.334 E.00501
; LINE_WIDTH: 0.342018
G1 X119.95 Y125.994 E.00806
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381169
G1 X119.915 Y125.479 E.00466
; LINE_WIDTH: 0.425069
G1 X119.891 Y125.321 E.00482
; LINE_WIDTH: 0.446723
G1 X119.59 Y125.107 E.01178
G1 X118.97 Y124.951 F30000
; LINE_WIDTH: 0.102491
G1 F1179
G1 X118.924 Y124.897 E.00033
; LINE_WIDTH: 0.130931
G1 X118.836 Y124.801 E.0009
; LINE_WIDTH: 0.162629
G1 X118.743 Y124.707 E.00126
G1 X118.644 Y124.728 F30000
; LINE_WIDTH: 0.118783
G1 F1179
G3 X118.897 Y124.794 I-1.48 J6.214 E.00157
; CHANGE_LAYER
; Z_HEIGHT: 3.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X118.644 Y124.728 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 17/74
; update layer progress
M73 L17
M991 S0 P16 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z3.6 I-.142 J1.209 P1  F30000
G1 X120.298 Y124.923 Z3.6
G1 Z3.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1168
G1 X120.298 Y127.077 E.06927
G1 X119.212 Y127.077 E.03491
G2 X119.456 Y125.331 I-1.339 J-1.077 E.05952
G2 X119.212 Y124.923 I-2.285 J1.088 E.01531
G1 X120.238 Y124.923 E.03298
; WIPE_START
G1 F11054.348
G1 X120.266 Y125.923 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I-.257 J-1.19 P1  F30000
G1 X116.973 Y126.632 Z3.8
G1 Z3.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1168
M204 S5000
G1 X116.956 Y126.603 E.00102
G3 X117.902 Y124.794 I1.048 J-.603 E.07237
G1 X118 Y124.79 E.00291
G3 X117.147 Y126.853 I.004 J1.21 E.14168
G1 X117.01 Y126.68 E.00658
; WIPE_START
G1 F11933.819
M204 S10000
M73 P24 R12
G1 X116.956 Y126.603 E-.03575
G1 X116.863 Y126.414 E-.08001
G1 X116.808 Y126.21 E-.08015
G1 X116.79 Y126 E-.08017
G1 X116.808 Y125.79 E-.08015
G1 X116.827 Y125.73 E-.02377
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I-1.084 J.553 P1  F30000
G1 X120.69 Y133.31 Z3.8
G1 Z3.4
G1 E.4 F1800
G1 F1168
M204 S5000
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.31 E.43548
G1 X120.75 Y133.31 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.746 Y132.31 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I.509 J1.105 P1  F30000
G1 X136.788 Y124.923 Z3.8
G1 Z3.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1168
G1 X136.612 Y125.199 E.01051
G2 X136.612 Y126.801 I1.435 J.801 E.05384
G1 X136.788 Y127.077 E.01051
G1 X135.702 Y127.077 E.03491
G1 X135.702 Y124.923 E.06927
G1 X136.728 Y124.923 E.03298
; WIPE_START
G1 F11054.348
G1 X136.612 Y125.199 E-.11361
G1 X136.495 Y125.45 E-.10545
G1 X136.452 Y125.585 E-.05384
G1 X136.422 Y125.722 E-.05323
G1 X136.409 Y125.863 E-.05388
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I.231 J1.195 P1  F30000
G1 X139.022 Y125.359 Z3.8
G1 Z3.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1168
M204 S5000
G1 X139.103 Y125.494 E.00471
G3 X137.902 Y124.794 I-1.099 J.505 E.18226
G1 X138 Y124.79 E.00291
G3 X138.994 Y125.304 I.004 J1.21 E.03466
G1 X138.995 Y125.305 E.00004
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.103 Y125.494 E-.08289
G1 X139.192 Y125.79 E-.11724
G1 X139.21 Y126 E-.08015
G1 X139.176 Y126.26 E-.09973
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I.111 J-1.212 P1  F30000
G1 X120.21 Y124.531 Z3.8
G1 Z3.4
G1 E.4 F1800
G1 F1168
M204 S5000
G1 X120.21 Y118.21 E.18828
G1 X135.79 Y118.21 E.46408
G1 X135.79 Y124.531 E.18826
G1 X137.995 Y124.531 E.06569
G3 X137.995 Y127.469 I-.001 J1.469 E.13741
G1 X135.79 Y127.469 E.06569
G1 X135.79 Y133.79 E.18828
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46408
G1 X120.21 Y127.469 E.18828
G1 X118.005 Y127.469 E.06569
G3 X118.005 Y124.531 I.001 J-1.469 E.13741
G1 X120.15 Y124.531 E.06391
M204 S10000
G1 X120.45 Y124.727 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130785
G1 F1168
G1 X120.45 Y118.494 E.04326
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10445
G1 X135.55 Y124.727 E.04351
; WIPE_START
G1 F15000
M73 P25 R12
G1 X135.549 Y123.727 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I-.62 J1.047 P1  F30000
G1 X137.239 Y124.727 Z3.8
G1 Z3.4
G1 E.4 F1800
; LINE_WIDTH: 0.158215
G1 F1168
G1 X137.16 Y124.805 E.00101
; LINE_WIDTH: 0.129643
G1 X137.074 Y124.899 E.00087
; LINE_WIDTH: 0.102277
G1 X137.03 Y124.951 E.00032
G1 X136.397 Y125.126 F30000
; LINE_WIDTH: 0.421626
G1 F1168
G1 X136.108 Y125.328 E.01055
G1 X136.085 Y125.479 E.00454
; LINE_WIDTH: 0.37966
G1 X136.064 Y125.666 E.00501
; LINE_WIDTH: 0.342026
G1 X136.05 Y126.006 E.00805
G1 X136.065 Y126.348 E.00809
; LINE_WIDTH: 0.381154
G1 X136.085 Y126.521 E.00465
; LINE_WIDTH: 0.424594
G1 X136.108 Y126.672 E.00459
G1 X136.396 Y126.874 E.01061
G1 X137.03 Y127.049 F30000
; LINE_WIDTH: 0.102331
G1 F1168
G1 X137.074 Y127.101 E.00032
; LINE_WIDTH: 0.129727
G1 X137.16 Y127.195 E.00087
; LINE_WIDTH: 0.158272
G1 X137.239 Y127.273 E.00101
; WIPE_START
G1 F15000
G1 X137.16 Y127.195 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I-.059 J-1.216 P1  F30000
G1 X135.55 Y127.273 Z3.8
G1 Z3.4
G1 E.4 F1800
; LINE_WIDTH: 0.130901
G1 F1168
G1 X135.55 Y133.506 E.04332
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10458
G1 X120.45 Y127.273 E.04357
; WIPE_START
G1 F15000
G1 X120.451 Y128.273 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z3.8 I.62 J-1.047 P1  F30000
G1 X118.761 Y127.273 Z3.8
G1 Z3.4
G1 E.4 F1800
; LINE_WIDTH: 0.158453
G1 F1168
G1 X118.836 Y127.199 E.00096
; LINE_WIDTH: 0.131104
G1 X118.924 Y127.103 E.00091
; LINE_WIDTH: 0.102488
G1 X118.97 Y127.049 E.00033
G1 X119.604 Y126.874 F30000
; LINE_WIDTH: 0.424701
G1 F1168
G1 X119.892 Y126.672 E.01061
G1 X119.915 Y126.521 E.00458
; LINE_WIDTH: 0.379687
G1 X119.936 Y126.334 E.00501
; LINE_WIDTH: 0.342021
G1 X119.95 Y125.994 E.00806
G1 X119.935 Y125.652 E.00808
; LINE_WIDTH: 0.381134
G1 X119.915 Y125.479 E.00465
; LINE_WIDTH: 0.424633
G1 X119.892 Y125.328 E.00459
G1 X119.604 Y125.126 E.01061
G1 X118.97 Y124.951 F30000
; LINE_WIDTH: 0.102518
G1 F1168
G1 X118.924 Y124.897 E.00033
; LINE_WIDTH: 0.131154
G1 X118.836 Y124.801 E.00091
; LINE_WIDTH: 0.158498
G1 X118.761 Y124.727 E.00096
; CHANGE_LAYER
; Z_HEIGHT: 3.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X118.836 Y124.801 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 18/74
; update layer progress
M73 L18
M991 S0 P17 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z3.8 I-.033 J1.217 P1  F30000
G1 X139.02 Y125.356 Z3.8
G1 Z3.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1177
M204 S5000
G1 X139.098 Y125.488 E.00458
G3 X137.898 Y124.794 I-1.096 J.511 E.18242
G1 X138 Y124.79 E.00303
G3 X138.991 Y125.303 I.002 J1.21 E.03455
; WIPE_START
G1 F11933.819
M204 S10000
G1 X139.098 Y125.488 E-.08122
G1 X139.169 Y125.687 E-.08013
G1 X139.21 Y126 E-.11995
G1 X139.191 Y126.212 E-.08113
G1 X139.177 Y126.256 E-.01756
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I-1.067 J-.585 P1  F30000
G1 X135.31 Y133.31 Z4
G1 Z3.6
G1 E.4 F1800
G1 F1177
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I.434 J-1.137 P1  F30000
G1 X116.969 Y126.629 Z4
G1 Z3.6
G1 E.4 F1800
G1 F1177
M204 S5000
G1 X116.952 Y126.602 E.00092
G3 X117.897 Y124.794 I1.049 J-.603 E.0723
G1 X118 Y124.79 E.00306
G3 X117.074 Y126.777 I.001 J1.21 E.14468
G1 X117.004 Y126.678 E.00362
; WIPE_START
G1 F11933.819
M204 S10000
G1 X116.952 Y126.602 E-.03457
G1 X116.831 Y126.313 E-.11922
G1 X116.794 Y126.106 E-.07995
G1 X116.794 Y125.895 E-.07997
G1 X116.825 Y125.724 E-.06629
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I.393 J1.152 P1  F30000
G1 X120.21 Y124.568 Z4
G1 Z3.6
G1 E.4 F1800
G1 F1177
M204 S5000
G1 X120.21 Y118.21 E.18939
G1 X135.79 Y118.21 E.46408
G1 X135.79 Y124.568 E.18938
M73 P25 R11
G1 X137.995 Y124.568 E.06569
G3 X137.995 Y127.432 I-.001 J1.432 E.13392
G1 X135.79 Y127.432 E.06569
G1 X135.79 Y133.79 E.18939
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.21 Y133.79 E.46408
G1 X120.21 Y127.432 E.18939
G1 X118.005 Y127.432 E.06569
M73 P26 R11
G3 X118.005 Y124.568 I.001 J-1.432 E.13392
G1 X120.15 Y124.568 E.0639
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.159 Y123.568 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I.916 J.802 P1  F30000
G1 X120.45 Y123.237 Z4
G1 Z3.6
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.130782
G1 F1177
G1 X120.45 Y118.494 E.03292
G1 X120.458 Y118.458 E.00026
G1 X120.494 Y118.45 E.00026
G1 X135.543 Y118.458 E.10444
G1 X135.55 Y123.237 E.03317
; WIPE_START
G1 F15000
G1 X135.548 Y122.237 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I-1.189 J.26 P1  F30000
G1 X136.641 Y127.224 Z4
G1 Z3.6
G1 E.4 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F1177
M204 S2000
G1 X136.933 Y126.932 E.0123
G1 X136.721 Y126.611
G1 X136.108 Y127.224 E.02584
G1 X135.574 Y127.224
G1 X136.598 Y126.201 E.04311
G1 X136.63 Y125.635
G1 X135.517 Y126.748 E.04688
G1 X135.517 Y126.215
G1 X136.956 Y124.776 E.06062
G1 X136.423 Y124.776
G1 X135.517 Y125.682 E.03816
G1 X135.517 Y125.148
G1 X135.89 Y124.776 E.01569
; WIPE_START
G1 F11933.819
M204 S10000
G1 X135.517 Y125.148 E-.20019
G1 X135.517 Y125.621 E-.17981
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I.383 J1.155 P1  F30000
G1 X136.804 Y125.195 Z4
G1 Z3.6
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.19818
G1 F1177
G2 X136.567 Y125.571 I9.064 J5.98 E.00546
G1 X136.831 Y125.197 F30000
; LINE_WIDTH: 0.0980882
G1 F1177
G1 X136.759 Y125.286 E.0005
; LINE_WIDTH: 0.139639
G2 X136.56 Y125.565 I6.391 J4.761 E.00262
; WIPE_START
G1 F15000
G1 X136.759 Y125.286 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I-1.149 J-.4 P1  F30000
G1 X135.55 Y128.763 Z4
G1 Z3.6
G1 E.4 F1800
; LINE_WIDTH: 0.130906
G1 F1177
G1 X135.55 Y133.506 E.03296
G1 X135.542 Y133.542 E.00026
G1 X135.506 Y133.55 E.00026
G1 X120.458 Y133.542 E.10459
G1 X120.45 Y128.763 E.03322
; WIPE_START
G1 F15000
G1 X120.452 Y129.763 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I1.206 J-.162 P1  F30000
G1 X120.11 Y127.224 Z4
G1 Z3.6
G1 E.4 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F1177
M204 S2000
G1 X120.483 Y126.852 E.0157
G1 X120.483 Y126.318
G1 X119.577 Y127.224 E.03816
G1 X119.043 Y127.224
G1 X120.483 Y125.785 E.06062
G1 X120.483 Y125.252
G1 X119.37 Y126.364 E.04687
G1 X119.402 Y125.799
G1 X120.425 Y124.776 E.0431
G1 X119.892 Y124.776
G1 X119.279 Y125.389 E.02584
G1 X119.067 Y125.068
G1 X119.359 Y124.776 E.0123
; WIPE_START
G1 F11933.819
M204 S10000
G1 X119.067 Y125.068 E-.15693
G1 X119.279 Y125.389 E-.14627
G1 X119.422 Y125.246 E-.0768
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4 I-1.217 J.019 P1  F30000
G1 X119.44 Y126.434 Z4
G1 Z3.6
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.139251
G1 F1177
G3 X119.239 Y126.717 I-8.495 J-5.848 E.00264
; LINE_WIDTH: 0.0977131
G1 X119.169 Y126.803 E.00048
G1 X119.434 Y126.428 F30000
; LINE_WIDTH: 0.198112
G1 F1177
G3 X119.196 Y126.805 I-8.512 J-5.101 E.00546
; CHANGE_LAYER
; Z_HEIGHT: 3.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X119.434 Y126.428 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 19/74
; update layer progress
M73 L19
M991 S0 P18 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z4 I-.484 J1.117 P1  F30000
G1 X135.31 Y133.31 Z4
G1 Z3.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
M73 P27 R11
G1 E-.02 F1800
G17
G3 Z4.2 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z4.2
G1 Z3.8
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46406
G1 X135.79 Y118.21 E.46408
G1 X135.79 Y133.79 E.46406
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46227
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130849
G1 F920
G1 X120.458 Y118.458 E.10478
G1 X135.543 Y118.458 E.10478
G1 X135.542 Y133.542 E.10477
G1 X120.518 Y133.542 E.10436
; CHANGE_LAYER
; Z_HEIGHT: 4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 20/74
; update layer progress
M73 L20
M991 S0 P19 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z4.2 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z4.2
G1 Z4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
M73 P28 R11
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4.4 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z4.4
G1 Z4
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.79 Y118.21 E.46406
G1 X135.79 Y133.79 E.46405
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130852
G1 F920
G1 X120.458 Y118.458 E.10478
G1 X135.543 Y118.458 E.10478
G1 X135.542 Y133.542 E.10478
G1 X120.518 Y133.542 E.10436
; CHANGE_LAYER
; Z_HEIGHT: 4.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
M73 P29 R11
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 21/74
; update layer progress
M73 L21
M991 S0 P20 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z4.4 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z4.4
G1 Z4.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4.6 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z4.6
G1 Z4.2
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46406
G1 X135.79 Y118.21 E.46408
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46227
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130855
G1 F920
M73 P30 R11
G1 X120.458 Y118.458 E.10478
G1 X135.543 Y118.458 E.10478
G1 X135.542 Y133.542 E.10478
G1 X120.518 Y133.542 E.10437
; CHANGE_LAYER
; Z_HEIGHT: 4.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 22/74
; update layer progress
M73 L22
M991 S0 P21 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z4.6 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z4.6
G1 Z4.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z4.8 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z4.8
G1 Z4.4
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.79 Y118.21 E.46406
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
M204 S10000
M73 P31 R11
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130857
G1 F920
G1 X120.458 Y118.458 E.10479
G1 X135.543 Y118.458 E.10479
G1 X135.542 Y133.542 E.10478
G1 X120.518 Y133.542 E.10437
; CHANGE_LAYER
; Z_HEIGHT: 4.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 23/74
; update layer progress
M73 L23
M991 S0 P22 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z4.8 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z4.8
G1 Z4.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
M73 P32 R10
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z5 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z5
G1 Z4.6
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46407
G1 X135.79 Y118.21 E.46408
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46228
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.13086
G1 F920
G1 X120.458 Y118.458 E.10479
G1 X135.543 Y118.458 E.10479
G1 X135.542 Y133.542 E.10479
G1 X120.518 Y133.542 E.10437
; CHANGE_LAYER
; Z_HEIGHT: 4.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 24/74
; update layer progress
M73 L24
M991 S0 P23 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z5 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z5
G1 Z4.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
M73 P33 R10
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z5.2 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z5.2
G1 Z4.8
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46406
G1 X135.79 Y118.21 E.46407
G1 X135.79 Y133.79 E.46405
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46228
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130862
G1 F920
G1 X120.458 Y118.458 E.10479
G1 X135.543 Y118.458 E.10479
G1 X135.542 Y133.542 E.10479
G1 X120.518 Y133.542 E.10437
; CHANGE_LAYER
; Z_HEIGHT: 5
; LAYER_HEIGHT: 0.2
; WIPE_START
M73 P34 R10
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 25/74
; update layer progress
M73 L25
M991 S0 P24 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z5.2 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z5.2
G1 Z5
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z5.4 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z5.4
G1 Z5
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.79 Y118.21 E.46407
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130865
G1 F920
M73 P35 R10
G1 X120.458 Y118.458 E.10479
G1 X135.543 Y118.458 E.1048
G1 X135.542 Y133.542 E.10479
G1 X120.518 Y133.542 E.10438
; CHANGE_LAYER
; Z_HEIGHT: 5.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 26/74
; update layer progress
M73 L26
M991 S0 P25 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z5.4 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z5.4
G1 Z5.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z5.6 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z5.6
G1 Z5.2
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46406
G1 X135.79 Y118.21 E.46406
G1 X135.79 Y133.79 E.46405
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

M73 P36 R10
G1 X120.27 Y133.79 E.46228
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130867
G1 F920
G1 X120.458 Y118.458 E.1048
G1 X135.543 Y118.458 E.1048
G1 X135.542 Y133.542 E.1048
G1 X120.518 Y133.542 E.10438
; CHANGE_LAYER
; Z_HEIGHT: 5.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 27/74
; update layer progress
M73 L27
M991 S0 P26 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z5.6 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z5.6
G1 Z5.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
M73 P37 R10
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z5.8 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z5.8
G1 Z5.4
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46407
G1 X135.79 Y118.21 E.46408
G1 X135.79 Y133.79 E.46405
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46228
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.13087
G1 F920
G1 X120.458 Y118.458 E.1048
G1 X135.543 Y118.458 E.1048
G1 X135.542 Y133.542 E.1048
G1 X120.518 Y133.542 E.10438
; CHANGE_LAYER
; Z_HEIGHT: 5.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 28/74
; update layer progress
M73 L28
M991 S0 P27 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z5.8 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z5.8
G1 Z5.6
M73 P38 R10
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
M73 P38 R9
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z6 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z6
G1 Z5.6
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46407
G1 X135.79 Y118.21 E.46407
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46228
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130872
G1 F920
G1 X120.458 Y118.458 E.1048
G1 X135.543 Y118.458 E.1048
G1 X135.542 Y133.542 E.1048
G1 X120.518 Y133.542 E.10439
; CHANGE_LAYER
; Z_HEIGHT: 5.8
; LAYER_HEIGHT: 0.2
; WIPE_START
M73 P39 R9
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 29/74
; update layer progress
M73 L29
M991 S0 P28 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z6 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z6
G1 Z5.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z6.2 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z6.2
G1 Z5.8
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.79 Y118.21 E.46406
G1 X135.79 Y133.79 E.46406
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130741
M73 P40 R9
G1 F920
G1 X120.457 Y118.458 E.10464
G1 X135.542 Y118.458 E.10465
G1 X135.542 Y133.542 E.10465
G1 X120.518 Y133.542 E.10423
; CHANGE_LAYER
; Z_HEIGHT: 6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 30/74
; update layer progress
M73 L30
M991 S0 P29 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z6.2 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z6.2
G1 Z6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z6.4 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z6.4
G1 Z6
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.789 Y118.21 E.46406
G1 X135.79 Y133.79 E.46406
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

M73 P41 R9
G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130877
G1 F920
G1 X120.458 Y118.458 E.10481
G1 X135.543 Y118.458 E.10481
G1 X135.542 Y133.542 E.10481
G1 X120.518 Y133.542 E.10439
; CHANGE_LAYER
; Z_HEIGHT: 6.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 31/74
; update layer progress
M73 L31
M991 S0 P30 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z6.4 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z6.4
G1 Z6.2
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
M73 P42 R9
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z6.6 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z6.6
G1 Z6.2
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.789 Y118.21 E.46404
G1 X135.79 Y133.79 E.46406
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.13088
G1 F920
G1 X120.458 Y118.458 E.10481
G1 X135.543 Y118.458 E.10481
G1 X135.542 Y133.542 E.10481
G1 X120.518 Y133.542 E.1044
; CHANGE_LAYER
; Z_HEIGHT: 6.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
M73 P43 R9
G1 E-.02 F1800
; layer num/total_layer_count: 32/74
; update layer progress
M73 L32
M991 S0 P31 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z6.6 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z6.6
G1 Z6.4
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z6.8 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z6.8
G1 Z6.4
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.789 Y118.21 E.46403
G1 X135.79 Y133.79 E.46406
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130882
G1 F920
G1 X120.458 Y118.458 E.10482
G1 X135.542 Y118.458 E.10482
G1 X135.542 Y133.542 E.10481
G1 X120.518 Y133.542 E.1044
; CHANGE_LAYER
; Z_HEIGHT: 6.6
; LAYER_HEIGHT: 0.2
; WIPE_START
M73 P44 R9
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 33/74
; update layer progress
M73 L33
M991 S0 P32 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z6.8 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z6.8
G1 Z6.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
M73 P44 R8
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z7
G1 Z6.6
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.788 Y118.21 E.46402
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130885
M73 P45 R8
G1 F920
G1 X120.458 Y118.458 E.10482
G1 X135.542 Y118.458 E.10482
G1 X135.542 Y133.542 E.10482
G1 X120.518 Y133.542 E.1044
; CHANGE_LAYER
; Z_HEIGHT: 6.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 34/74
; update layer progress
M73 L34
M991 S0 P33 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z7 I-.063 J1.215 P1  F30000
G1 X135.31 Y133.31 Z7
G1 Z6.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F920
M204 S5000
G1 X120.69 Y133.31 E.43548
G1 X120.69 Y118.69 E.43548
G1 X135.31 Y118.69 E.43548
G1 X135.31 Y133.25 E.43369
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.31 Y133.254 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.2 I-.046 J-1.216 P1  F30000
G1 X120.21 Y133.79 Z7.2
G1 Z6.8
G1 E.4 F1800
G1 F920
M204 S5000
G1 X120.21 Y118.21 E.46406
G1 X135.788 Y118.21 E.46401
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

M73 P46 R8
G1 X120.27 Y133.79 E.46229
M204 S10000
G1 X120.458 Y133.542 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.130887
G1 F920
G1 X120.458 Y118.458 E.10482
G1 X135.542 Y118.458 E.10482
G1 X135.542 Y133.542 E.10482
G1 X120.518 Y133.542 E.1044
M106 S127.5
; CHANGE_LAYER
; Z_HEIGHT: 7
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X120.514 Y132.542 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 35/74
; update layer progress
M73 L35
M991 S0 P34 ;notify layer change
M106 S127.5
; OBJECT_ID: 15
G17
G3 Z7.2 I.685 J1.006 P1  F30000
G1 X123.476 Y130.524 Z7.2
G1 Z7
G1 E.4 F1800
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45
G1 F600
M204 S5000
G3 X127.441 Y119.622 I4.524 J-4.527 E.46693
G1 X127.998 Y119.597 E.01795
G3 X123.519 Y130.566 I.002 J6.4 E.80619
M106 S96.9
M106 S127.5
M204 S250
G1 X123.754 Y130.246 F30000
G1 F600
M204 S5000
M73 P47 R8
G3 X127.475 Y120.013 I4.246 J-4.249 E.43831
G1 X127.998 Y119.99 E.01685
G3 X123.796 Y130.289 I.002 J6.007 E.75666
M106 S96.9
M106 S127.5
; WIPE_START
M204 S10000
G1 X123.396 Y129.863 E-.22198
G1 X123.143 Y129.533 E-.15802
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.4 I-1.017 J-.669 P1  F30000
G1 X120.602 Y133.398 Z7.4
G1 Z7
G1 E.4 F1800
; FEATURE: Inner wall
G1 F11054.348
G1 X120.602 Y118.602 E.47578
G1 X135.395 Y118.602 E.4757
G1 X135.398 Y133.398 E.47578
G1 X120.662 Y133.398 E.47385
M204 S250
G1 X120.21 Y133.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F11933.819
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.788 Y118.21 E.464
G1 X135.79 Y133.79 E.46406
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
; WIPE_START
M204 S10000
G1 X120.266 Y132.79 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.4 I1.143 J.419 P1  F30000
G1 X120.766 Y131.426 Z7.4
G1 Z7
G1 E.4 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.4222
G1 F3000
G1 X121.284 Y133.065 E.05148
G1 X121.682 Y133.065 E.01192
G1 X120.935 Y130.706 E.07413
G1 X120.935 Y129.449 E.03765
G1 X122.08 Y133.065 E.11362
G1 X122.478 Y133.065 E.01192
G1 X120.935 Y128.192 E.15311
G1 X120.935 Y126.936 E.03765
G1 X122.929 Y133.234 E.19794
M106 S96.9
M106 S127.5
; WIPE_START
G1 X122.628 Y132.281 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.4 I.991 J.707 P1  F30000
G1 X132.273 Y118.766 Z7.4
G1 Z7
G1 E.4 F1800
G1 F3000
G1 X133.215 Y121.741 E.09352
G2 X132.614 Y121.1 I-6.023 J5.042 E.02634
G1 X131.929 Y118.935 E.06803
G1 X131.531 Y118.935 E.01192
G1 X132.071 Y120.641 E.0536
G2 X131.562 Y120.29 I-2.263 J2.735 E.01855
G1 X131.133 Y118.935 E.04256
G1 X130.735 Y118.935 E.01192
G1 X131.077 Y120.015 E.03392
G2 X130.61 Y119.797 I-1.479 J2.561 E.01545
G1 X130.338 Y118.935 E.02708
G1 X129.94 Y118.935 E.01192
G1 X130.158 Y119.624 E.02164
G2 X129.717 Y119.487 I-1.003 J2.46 E.01385
G1 X129.542 Y118.935 E.01735
G1 X129.144 Y118.935 E.01192
G1 X129.289 Y119.393 E.01437
G2 X128.87 Y119.327 I-.586 J2.36 E.01271
G1 X128.746 Y118.935 E.0123
G1 X128.348 Y118.935 E.01192
G1 X128.459 Y119.284 E.01095
G1 X128.055 Y119.266 E.0121
G1 X127.951 Y118.935 E.0104
G1 X127.553 Y118.935 E.01192
G1 X127.661 Y119.279 E.01079
G2 X127.273 Y119.308 I-.027 J2.245 E.01169
G1 X127.155 Y118.935 E.0117
G1 X126.757 Y118.935 E.01192
G1 X126.891 Y119.358 E.01328
G2 X126.518 Y119.436 I.261 J2.19 E.01144
G1 X126.359 Y118.935 E.01572
G1 X125.961 Y118.935 E.01192
G1 X126.149 Y119.527 E.0186
G1 X125.787 Y119.641 E.01136
G1 X125.564 Y118.935 E.02219
G1 X125.166 Y118.935 E.01192
G1 X125.433 Y119.779 E.02652
G2 X125.083 Y119.931 I.696 J2.075 E.01144
G1 X124.768 Y118.935 E.0313
G1 X124.37 Y118.935 E.01192
G1 X124.742 Y120.109 E.03689
G2 X124.407 Y120.309 I.976 J2.009 E.01169
G1 X123.972 Y118.935 E.04318
G1 X123.574 Y118.935 E.01192
G1 X124.078 Y120.527 E.05001
G1 X123.758 Y120.772 E.01209
G1 X123.177 Y118.935 E.05773
G1 X122.779 Y118.935 E.01192
G1 X123.446 Y121.045 E.06629
G2 X123.142 Y121.34 I1.537 J1.888 E.01272
G1 X122.381 Y118.935 E.07557
G1 X121.983 Y118.935 E.01192
G1 X122.846 Y121.663 E.08571
G2 X122.564 Y122.029 I1.951 J1.794 E.01386
G1 X121.585 Y118.935 E.09721
G1 X121.187 Y118.935 E.01192
G1 X122.294 Y122.431 E.10986
G2 X122.038 Y122.879 I2.426 J1.687 E.01546
G1 X120.935 Y119.396 E.10944
G1 X120.935 Y120.653 E.03765
G1 X121.8 Y123.383 E.08581
G2 X121.586 Y123.964 I3.21 J1.513 E.01856
G1 X120.935 Y121.909 E.06456
G1 X120.935 Y123.166 E.03765
M73 P48 R8
G1 X121.406 Y124.652 E.04669
G2 X121.284 Y125.525 I7.507 J1.487 E.02644
G1 X120.935 Y124.423 E.03466
G1 X120.935 Y125.679 E.03765
G1 X123.273 Y133.065 E.2321
G1 X123.671 Y133.065 E.01192
G1 X122.781 Y130.254 E.08833
G2 X123.383 Y130.897 I5.98 J-4.99 E.02639
G1 X124.069 Y133.065 E.06812
G1 X124.467 Y133.065 E.01192
G1 X123.926 Y131.357 E.05367
G2 X124.435 Y131.709 I2.268 J-2.738 E.01857
G1 X124.865 Y133.065 E.04262
G1 X125.263 Y133.065 E.01192
G1 X124.92 Y131.984 E.03396
G2 X125.387 Y132.202 I1.48 J-2.558 E.01546
G1 X125.66 Y133.065 E.02711
G1 X126.058 Y133.065 E.01192
G1 X125.84 Y132.375 E.02166
G2 X126.281 Y132.512 I1.005 J-2.461 E.01385
G1 X126.456 Y133.065 E.01736
G1 X126.854 Y133.065 E.01192
G1 X126.709 Y132.607 E.01438
G2 X127.128 Y132.673 I.587 J-2.359 E.01272
G1 X127.252 Y133.065 E.01231
G1 X127.65 Y133.065 E.01192
G1 X127.539 Y132.716 E.01095
G1 X127.943 Y132.734 E.0121
G1 X128.047 Y133.065 E.0104
G1 X128.445 Y133.065 E.01192
G1 X128.337 Y132.722 E.01078
G2 X128.725 Y132.692 I.028 J-2.233 E.01169
G1 X128.843 Y133.065 E.0117
G1 X129.241 Y133.065 E.01192
G1 X129.107 Y132.642 E.01328
G2 X129.481 Y132.565 I-.254 J-2.172 E.01144
G1 X129.639 Y133.065 E.0157
G1 X130.037 Y133.065 E.01192
G1 X129.849 Y132.473 E.01859
G1 X130.211 Y132.359 E.01136
G1 X130.434 Y133.065 E.02218
G1 X130.832 Y133.065 E.01192
G1 X130.565 Y132.222 E.02649
G2 X130.915 Y132.07 I-.695 J-2.076 E.01144
G1 X131.23 Y133.065 E.03127
G1 X131.628 Y133.065 E.01192
G1 X131.257 Y131.892 E.03686
G2 X131.591 Y131.692 I-.975 J-2.01 E.01169
G1 X132.026 Y133.065 E.04315
G1 X132.424 Y133.065 E.01192
G1 X131.92 Y131.475 E.04997
G1 X132.24 Y131.229 E.01209
G1 X132.821 Y133.065 E.05769
G1 X133.219 Y133.065 E.01192
G1 X132.552 Y130.957 E.06624
G2 X132.856 Y130.662 I-1.536 J-1.888 E.01272
G1 X133.617 Y133.065 E.07552
G1 X134.015 Y133.065 E.01192
G1 X133.152 Y130.339 E.08566
G2 X133.434 Y129.973 I-1.936 J-1.785 E.01386
G1 X134.413 Y133.065 E.09715
G1 X134.811 Y133.065 E.01192
G1 X133.705 Y129.571 E.10979
G2 X133.961 Y129.124 I-2.424 J-1.687 E.01546
G1 X135.064 Y132.61 E.10955
G1 X135.064 Y131.353 E.03767
G1 X134.199 Y128.62 E.08588
G2 X134.413 Y128.04 I-3.211 J-1.515 E.01855
G1 X135.064 Y130.095 E.0646
G1 X135.064 Y128.838 E.03767
G1 X134.593 Y127.352 E.0467
G2 X134.715 Y126.48 I-7.555 J-1.5 E.02639
G1 X135.064 Y127.581 E.03459
G1 X135.063 Y126.324 E.03767
G1 X132.725 Y118.935 E.23218
G1 X133.122 Y118.935 E.01192
G1 X135.063 Y125.066 E.19267
G1 X135.063 Y123.809 E.03767
G1 X133.52 Y118.935 E.15316
G1 X133.918 Y118.935 E.01192
G1 X135.063 Y122.552 E.11365
G1 X135.063 Y121.294 E.03767
G1 X134.316 Y118.935 E.07413
G1 X134.714 Y118.935 E.01192
G1 X135.232 Y120.573 E.05148
M106 S96.9
; CHANGE_LAYER
; Z_HEIGHT: 7.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F3000
G1 X134.93 Y119.62 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 36/74
; update layer progress
M73 L36
M991 S0 P35 ;notify layer change
M106 S99.45
; OBJECT_ID: 15
G17
G3 Z7.4 I-.015 J-1.217 P1  F30000
G1 X126.76 Y119.724 Z7.4
G1 Z7.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2091
G1 X126.905 Y119.692 E.00479
G3 X127.442 Y119.622 I1.095 J6.305 E.01743
G1 X127.997 Y119.597 E.01785
G3 X126.343 Y119.815 I.003 J6.4 E1.23922
G1 X126.701 Y119.737 E.01177
M204 S250
G1 X126.844 Y120.107 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2091
M204 S5000
G1 X126.973 Y120.078 E.00394
G3 X127.476 Y120.013 I1.027 J5.919 E.01514
G1 X127.997 Y119.99 E.01553
G3 X126.445 Y120.195 I.003 J6.007 E1.07752
G1 X126.785 Y120.12 E.01038
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.973 Y120.078 E-.07303
G1 X127.476 Y120.013 E-.19304
G1 X127.776 Y120 E-.11394
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-1.073 J-.574 P1  F30000
G1 X120.602 Y133.398 Z7.6
G1 Z7.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2091
G1 X120.602 Y118.602 E.47578
G1 X135.398 Y118.602 E.47578
G1 X135.398 Y133.398 E.47578
G1 X120.662 Y133.398 E.47385
M204 S250
G1 X120.21 Y133.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2091
M204 S5000
G1 X120.21 Y118.21 E.46408
G1 X135.787 Y118.21 E.46399
G1 X135.79 Y133.79 E.46407
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46229
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.266 Y132.79 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I1.209 J.14 P1  F30000
G1 X121.371 Y123.279 Z7.6
G1 Z7.2
G1 E.4 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2091
G1 X121.777 Y122.436 E.02786
G3 X125.278 Y119.371 I6.197 J3.548 E.14118
G1 X121.371 Y119.371 E.11638
G1 X121.371 Y123.219 E.1146
; WIPE_START
G1 F11934.123
G1 X121.371 Y122.219 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I1.09 J.54 P1  F30000
G1 X122.11 Y120.727 Z7.6
G1 Z7.2
G1 E.4 F1800
; LINE_WIDTH: 0.38965
G1 F2091
G1 X122.727 Y120.11 E.0239
G1 X122.11 Y120.11 E.0169
G1 X122.11 Y120.667 E.01526
; WIPE_START
G1 F12978.398
G1 X122.11 Y120.11 E-.2117
G1 X122.553 Y120.11 E-.1683
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I.346 J1.167 P1  F30000
G1 X123.775 Y119.748 Z7.6
G1 Z7.2
M73 P49 R8
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2091
G1 X121.748 Y119.748 E.06037
G1 X121.748 Y121.775 E.06037
G3 X123.725 Y119.782 I6.465 J4.435 E.08407
; WIPE_START
G1 F11934.123
G1 X123.117 Y120.244 E-.29045
G1 X122.944 Y120.404 E-.08955
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I.272 J1.186 P1  F30000
G1 X127.99 Y119.247 Z7.6
G1 Z7.2
G1 E.4 F1800
; LINE_WIDTH: 0.34336
G1 F2091
G1 X128.582 Y119.266 E.01405
; LINE_WIDTH: 0.3691
G1 X129.169 Y119.323 E.0152
; LINE_WIDTH: 0.417834
G3 X134.676 Y124.815 I-1.109 J6.619 E.24567
; LINE_WIDTH: 0.37092
G1 X134.734 Y125.404 E.01534
; LINE_WIDTH: 0.343663
G3 X134.734 Y126.582 I-9.044 J.593 E.02801
; LINE_WIDTH: 0.36843
G1 X134.679 Y127.148 E.01462
; LINE_WIDTH: 0.417751
G3 X130.879 Y132.155 I-6.608 J-1.071 E.19372
G3 X129.185 Y132.676 I-2.799 J-6.083 E.05263
; LINE_WIDTH: 0.370875
G1 X128.596 Y132.734 E.01534
; LINE_WIDTH: 0.343661
G3 X127.418 Y132.734 I-.593 J-9.044 E.02801
; LINE_WIDTH: 0.36843
G1 X126.852 Y132.679 E.01462
; LINE_WIDTH: 0.41775
G3 X121.846 Y128.881 I1.071 J-6.608 E.19366
G3 X121.324 Y127.185 I6.082 J-2.8 E.0527
; LINE_WIDTH: 0.37088
G1 X121.266 Y126.596 E.01534
; LINE_WIDTH: 0.343658
G3 X121.266 Y125.418 I9.042 J-.594 E.02801
; LINE_WIDTH: 0.36843
G1 X121.321 Y124.852 E.01462
; LINE_WIDTH: 0.417675
G3 X125.121 Y119.845 I6.608 J1.071 E.19368
G3 X126.833 Y119.322 I2.782 J6.039 E.05315
; LINE_WIDTH: 0.370175
G1 X127.405 Y119.266 E.01485
; LINE_WIDTH: 0.34394
G1 X127.93 Y119.249 E.01251
G1 X128.01 Y118.953 F30000
; LINE_WIDTH: 0.343355
G1 F2091
G1 X127.411 Y118.959 E.0142
; LINE_WIDTH: 0.36844
G1 X126.825 Y118.978 E.01507
; LINE_WIDTH: 0.418338
G1 X126.203 Y118.994 E.01847
G1 X120.994 Y118.994 E.15446
G1 X120.994 Y124.204 E.15449
G1 X120.979 Y124.8 E.01769
; LINE_WIDTH: 0.370275
G1 X120.96 Y125.384 E.01511
; LINE_WIDTH: 0.343658
G2 X120.959 Y126.589 I27.574 J.616 E.02862
; LINE_WIDTH: 0.36914
G1 X120.978 Y127.192 E.01556
; LINE_WIDTH: 0.418394
G1 X120.994 Y127.799 E.018
G1 X120.994 Y133.006 E.15443
G1 X126.204 Y133.006 E.15452
G1 X126.8 Y133.021 E.0177
; LINE_WIDTH: 0.37027
G1 X127.384 Y133.04 E.01511
; LINE_WIDTH: 0.343656
G2 X128.589 Y133.041 I.616 J-27.574 E.02862
; LINE_WIDTH: 0.369135
G1 X129.193 Y133.022 E.01556
; LINE_WIDTH: 0.418387
G1 X129.799 Y133.006 E.01799
G1 X135.006 Y133.006 E.15443
G1 X135.006 Y127.796 E.15451
G1 X135.021 Y127.2 E.0177
; LINE_WIDTH: 0.37014
G1 X135.04 Y126.616 E.0151
; LINE_WIDTH: 0.343663
G2 X135.041 Y125.411 I-27.574 J-.616 E.02862
; LINE_WIDTH: 0.369145
G1 X135.022 Y124.807 E.01556
; LINE_WIDTH: 0.418448
G1 X135.006 Y124.201 E.01799
G1 X135.006 Y118.994 E.15446
G1 X129.799 Y118.994 E.15446
G1 X129.222 Y118.98 E.01712
; LINE_WIDTH: 0.370885
G1 X128.616 Y118.96 E.01572
; LINE_WIDTH: 0.34395
G1 X128.07 Y118.953 E.01299
; WIPE_START
G1 F14948.676
G1 X128.616 Y118.96 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-.292 J1.181 P1  F30000
G1 X133.273 Y120.11 Z7.6
G1 Z7.2
G1 E.4 F1800
; LINE_WIDTH: 0.38964
G1 F2091
G1 X133.89 Y120.727 E.0239
G1 X133.89 Y120.11 E.0169
G1 X133.333 Y120.11 E.01526
; WIPE_START
G1 F12978.773
G1 X133.89 Y120.11 E-.21169
G1 X133.89 Y120.553 E-.16831
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-1.167 J.346 P1  F30000
G1 X134.252 Y121.775 Z7.6
G1 Z7.2
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2091
G1 X134.252 Y119.748 E.06037
G1 X132.225 Y119.748 E.06037
G3 X134.218 Y121.725 I-4.434 J6.465 E.08407
; WIPE_START
G1 F11934.123
G1 X133.756 Y121.117 E-.29046
G1 X133.596 Y120.944 E-.08954
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-1.113 J.492 P1  F30000
G1 X134.629 Y123.279 Z7.6
G1 Z7.2
G1 E.4 F1800
G1 F2091
G1 X134.629 Y119.371 E.11638
G1 X130.722 Y119.371 E.11638
G1 X131.564 Y119.777 E.02786
G3 X134.606 Y123.223 I-3.547 J6.195 E.13939
; WIPE_START
G1 F11934.123
G1 X134.489 Y122.947 E-.11402
G1 X134.198 Y122.393 E-.23768
G1 X134.158 Y122.33 E-.02831
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-1.216 J-.036 P1  F30000
G1 X133.89 Y131.273 Z7.6
G1 Z7.2
G1 E.4 F1800
; LINE_WIDTH: 0.38966
G1 F2091
G1 X133.273 Y131.89 E.0239
G1 X133.89 Y131.89 E.0169
G1 X133.89 Y131.333 E.01526
; WIPE_START
G1 F12978.024
G1 X133.89 Y131.89 E-.2117
G1 X133.447 Y131.89 E-.1683
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-.346 J-1.167 P1  F30000
G1 X132.225 Y132.252 Z7.6
G1 Z7.2
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2091
G1 X134.252 Y132.252 E.06037
G1 X134.252 Y130.225 E.06037
G3 X132.275 Y132.218 I-6.466 J-4.435 E.08408
; WIPE_START
G1 F11934.123
G1 X132.883 Y131.756 E-.29046
G1 X133.056 Y131.596 E-.08954
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-.492 J-1.113 P1  F30000
G1 X130.721 Y132.629 Z7.6
G1 Z7.2
G1 E.4 F1800
G1 F2091
G1 X134.629 Y132.629 E.11638
G1 X134.629 Y128.721 E.11638
G1 X134.223 Y129.564 E.02786
G3 X130.777 Y132.605 I-6.195 J-3.547 E.13939
; WIPE_START
G1 F11934.123
G1 X131.053 Y132.489 E-.11401
G1 X131.607 Y132.198 E-.23768
G1 X131.67 Y132.158 E-.02832
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I-.089 J-1.214 P1  F30000
G1 X125.279 Y132.629 Z7.6
G1 Z7.2
G1 E.4 F1800
G1 F2091
G1 X124.436 Y132.223 E.02786
G3 X121.371 Y128.721 I3.548 J-6.197 E.14118
G1 X121.371 Y132.629 E.11638
G1 X125.219 Y132.629 E.1146
; WIPE_START
G1 F11934.123
G1 X124.219 Y132.629 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I.788 J-.927 P1  F30000
G1 X123.775 Y132.252 Z7.6
G1 Z7.2
G1 E.4 F1800
G1 F2091
G3 X121.748 Y130.225 I4.411 J-6.438 E.08586
G1 X121.748 Y132.252 E.06037
G1 X123.715 Y132.252 E.05858
; WIPE_START
G1 F11934.123
G1 X122.715 Y132.252 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.6 I1.035 J-.64 P1  F30000
G1 X122.11 Y131.273 Z7.6
G1 Z7.2
G1 E.4 F1800
; LINE_WIDTH: 0.38964
G1 F2091
G1 X122.11 Y131.89 E.0169
G1 X122.727 Y131.89 E.0169
G1 X122.153 Y131.315 E.02226
; CHANGE_LAYER
; Z_HEIGHT: 7.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F12978.773
G1 X122.727 Y131.89 E-.30886
G1 X122.54 Y131.89 E-.07114
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 37/74
; update layer progress
M73 L37
M991 S0 P36 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z7.6 I1.15 J.4 P1  F30000
G1 X126.769 Y119.722 Z7.6
G1 Z7.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2090
G1 X126.916 Y119.69 E.00484
G3 X127.443 Y119.622 I1.084 J6.307 E.01709
G1 X127.995 Y119.597 E.01776
G3 X126.344 Y119.815 I.005 J6.4 E1.2393
G1 X126.71 Y119.735 E.01206
M204 S250
G1 X126.852 Y120.105 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2090
M204 S5000
G1 X126.983 Y120.076 E.00399
G3 X127.477 Y120.013 I1.017 J5.921 E.01483
G1 X127.995 Y119.99 E.01545
G3 X126.445 Y120.195 I.005 J6.007 E1.07759
G1 X126.794 Y120.118 E.01064
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.983 Y120.076 E-.07366
G1 X127.477 Y120.013 E-.18914
G1 X127.785 Y119.999 E-.11721
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I-1.073 J-.575 P1  F30000
G1 X120.602 Y133.398 Z7.8
G1 Z7.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2090
G1 X120.602 Y118.602 E.47578
G1 X135.398 Y118.602 E.47578
G1 X135.398 Y133.398 E.47578
M73 P50 R8
G1 X120.662 Y133.398 E.47385
M204 S250
G1 X120.21 Y133.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2090
M204 S5000
G1 X120.21 Y118.21 E.46406
G1 X135.787 Y118.21 E.46398
G1 X135.79 Y133.79 E.46406
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46227
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.267 Y132.79 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I.418 J1.143 P1  F30000
G1 X122.727 Y131.89 Z7.8
G1 Z7.4
G1 E.4 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.38964
G1 F2090
G1 X122.11 Y131.273 E.0239
G1 X122.11 Y131.89 E.0169
G1 X122.667 Y131.89 E.01526
; WIPE_START
G1 F12978.773
G1 X122.11 Y131.89 E-.21171
G1 X122.11 Y131.447 E-.16829
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I-.53 J1.096 P1  F30000
G1 X123.775 Y132.252 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2090
G3 X121.748 Y130.225 I4.41 J-6.437 E.08586
G1 X121.748 Y132.252 E.06037
G1 X123.715 Y132.252 E.05858
; WIPE_START
G1 F11934.123
G1 X122.715 Y132.252 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I-.177 J1.204 P1  F30000
G1 X125.279 Y132.629 Z7.8
G1 Z7.4
G1 E.4 F1800
G1 F2090
G1 X124.436 Y132.223 E.02786
G3 X121.371 Y128.721 I3.548 J-6.197 E.14118
G1 X121.371 Y132.629 E.11638
G1 X125.219 Y132.629 E.1146
; WIPE_START
G1 F11934.123
G1 X124.219 Y132.629 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I0 J1.217 P1  F30000
G1 X130.721 Y132.629 Z7.8
G1 Z7.4
G1 E.4 F1800
G1 F2090
G1 X134.629 Y132.629 E.11638
G1 X134.629 Y128.721 E.11638
G1 X134.223 Y129.564 E.02786
G3 X130.777 Y132.605 I-6.195 J-3.547 E.13939
; WIPE_START
M73 P50 R7
G1 F11934.123
G1 X131.053 Y132.489 E-.11405
G1 X131.607 Y132.198 E-.23761
G1 X131.67 Y132.158 E-.02834
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I-.202 J1.2 P1  F30000
G1 X132.225 Y132.252 Z7.8
G1 Z7.4
G1 E.4 F1800
G1 F2090
G1 X134.252 Y132.252 E.06037
G1 X134.252 Y130.225 E.06037
G3 X132.275 Y132.218 I-6.465 J-4.434 E.08408
; WIPE_START
G1 F11934.123
G1 X132.883 Y131.756 E-.29047
G1 X133.056 Y131.596 E-.08953
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I.44 J1.135 P1  F30000
G1 X133.89 Y131.273 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.38965
G1 F2090
G1 X133.273 Y131.89 E.0239
G1 X133.89 Y131.89 E.0169
G1 X133.89 Y131.333 E.01526
; WIPE_START
G1 F12978.398
G1 X133.89 Y131.89 E-.21169
G1 X133.447 Y131.89 E-.16831
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I1.206 J.165 P1  F30000
G1 X134.629 Y123.279 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2090
G1 X134.629 Y119.371 E.11638
G1 X130.722 Y119.371 E.11638
G1 X131.564 Y119.777 E.02786
G3 X134.606 Y123.223 I-3.547 J6.195 E.13939
; WIPE_START
G1 F11934.123
G1 X134.489 Y122.947 E-.11406
G1 X134.198 Y122.393 E-.23761
G1 X134.158 Y122.33 E-.02833
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I1.2 J.202 P1  F30000
G1 X134.252 Y121.775 Z7.8
G1 Z7.4
G1 E.4 F1800
G1 F2090
G1 X134.252 Y119.748 E.06037
G1 X132.225 Y119.748 E.06037
G3 X134.218 Y121.725 I-4.434 J6.464 E.08408
; WIPE_START
G1 F11934.123
G1 X133.756 Y121.117 E-.29048
G1 X133.596 Y120.944 E-.08952
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I1.135 J-.44 P1  F30000
G1 X133.273 Y120.11 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.38964
G1 F2090
G1 X133.89 Y120.727 E.0239
G1 X133.89 Y120.11 E.0169
G1 X133.333 Y120.11 E.01526
; WIPE_START
G1 F12978.773
G1 X133.89 Y120.11 E-.2117
G1 X133.89 Y120.553 E-.1683
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I.319 J-1.174 P1  F30000
G1 X128.007 Y118.953 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.355462
G1 F2090
G2 X126.837 Y118.977 I-.009 J27.39 E.02891
; LINE_WIDTH: 0.418355
G1 X126.204 Y118.994 E.01878
G1 X120.994 Y118.994 E.15449
G1 X120.994 Y124.201 E.15442
G1 X120.98 Y124.777 E.0171
; LINE_WIDTH: 0.370915
G1 X120.96 Y125.384 E.01573
; LINE_WIDTH: 0.343661
G2 X120.959 Y126.589 I27.553 J.616 E.02862
; LINE_WIDTH: 0.369135
G1 X120.978 Y127.192 E.01556
; LINE_WIDTH: 0.418448
G1 X120.994 Y127.799 E.018
G1 X120.994 Y133.006 E.15446
G1 X126.201 Y133.006 E.15446
G1 X126.777 Y133.02 E.0171
; LINE_WIDTH: 0.37091
G1 X127.384 Y133.04 E.01573
; LINE_WIDTH: 0.343656
G2 X128.589 Y133.041 I.616 J-27.573 E.02862
; LINE_WIDTH: 0.36913
G1 X129.192 Y133.022 E.01555
; LINE_WIDTH: 0.418446
G1 X129.799 Y133.006 E.018
G1 X135.006 Y133.006 E.15446
G1 X135.006 Y127.799 E.15446
G1 X135.02 Y127.223 E.0171
; LINE_WIDTH: 0.370865
G1 X135.04 Y126.616 E.01573
; LINE_WIDTH: 0.343663
G2 X135.041 Y125.411 I-27.573 J-.616 E.02862
; LINE_WIDTH: 0.369135
G1 X135.022 Y124.808 E.01555
; LINE_WIDTH: 0.418443
G1 X135.006 Y124.201 E.018
G1 X135.006 Y118.994 E.15445
G1 X129.799 Y118.994 E.15446
G1 X129.221 Y118.98 E.01714
; LINE_WIDTH: 0.370835
G1 X128.616 Y118.96 E.01569
; LINE_WIDTH: 0.343955
G1 X128.067 Y118.953 E.01304
G1 X127.988 Y119.247 F30000
; LINE_WIDTH: 0.34337
G1 F2090
G1 X128.582 Y119.266 E.01411
; LINE_WIDTH: 0.36905
G1 X129.168 Y119.322 E.01517
; LINE_WIDTH: 0.417828
G3 X134.676 Y124.815 I-1.108 J6.619 E.24571
; LINE_WIDTH: 0.37091
G1 X134.734 Y125.404 E.01534
; LINE_WIDTH: 0.343663
G3 X134.734 Y126.582 I-9.044 J.593 E.02801
; LINE_WIDTH: 0.369135
G1 X134.677 Y127.17 E.01521
; LINE_WIDTH: 0.417833
G3 X129.185 Y132.676 I-6.619 J-1.11 E.24567
; LINE_WIDTH: 0.370875
G1 X128.596 Y132.734 E.01534
; LINE_WIDTH: 0.343663
G3 X127.418 Y132.734 I-.593 J-9.044 E.02801
; LINE_WIDTH: 0.369135
G1 X126.83 Y132.677 E.01521
; LINE_WIDTH: 0.417833
G3 X121.324 Y127.185 I1.11 J-6.619 E.24567
; LINE_WIDTH: 0.37088
G1 X121.266 Y126.596 E.01534
; LINE_WIDTH: 0.343661
G3 X121.266 Y125.418 I9.042 J-.594 E.02801
; LINE_WIDTH: 0.369135
M73 P51 R7
G1 X121.323 Y124.83 E.01521
; LINE_WIDTH: 0.417708
G3 X126.844 Y119.321 I6.615 J1.108 E.24644
; LINE_WIDTH: 0.36972
G1 X127.405 Y119.266 E.01455
; LINE_WIDTH: 0.343935
G1 X127.928 Y119.249 E.01245
; WIPE_START
G1 F14949.421
G1 X127.405 Y119.266 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I-.16 J-1.206 P1  F30000
G1 X123.775 Y119.748 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2090
G1 X121.748 Y119.748 E.06037
G1 X121.748 Y121.775 E.06037
G3 X123.725 Y119.782 I6.465 J4.434 E.08408
; WIPE_START
G1 F11934.123
G1 X123.117 Y120.244 E-.29048
G1 X122.944 Y120.404 E-.08952
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I-.44 J-1.135 P1  F30000
G1 X122.11 Y120.727 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.38964
G1 F2090
G1 X122.727 Y120.11 E.0239
G1 X122.11 Y120.11 E.0169
G1 X122.11 Y120.667 E.01526
; WIPE_START
G1 F12978.773
G1 X122.11 Y120.11 E-.21171
G1 X122.553 Y120.11 E-.16829
; WIPE_END
G1 E-.02 F1800
G17
G3 Z7.8 I-1.14 J-.425 P1  F30000
G1 X121.371 Y123.279 Z7.8
G1 Z7.4
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2090
G1 X121.777 Y122.436 E.02786
G3 X125.278 Y119.371 I6.197 J3.548 E.14118
G1 X121.371 Y119.371 E.11638
G1 X121.371 Y123.219 E.1146
; CHANGE_LAYER
; Z_HEIGHT: 7.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F11934.123
G1 X121.371 Y122.219 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 38/74
; update layer progress
M73 L38
M991 S0 P37 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z7.8 I.51 J1.105 P1  F30000
G1 X126.779 Y119.721 Z7.8
G1 Z7.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2092
G1 X126.927 Y119.688 E.00489
G3 X127.442 Y119.622 I1.073 J6.309 E.01671
G1 X127.992 Y119.597 E.01771
G3 X126.344 Y119.815 I.007 J6.4 E1.23938
G1 X126.72 Y119.734 E.01236
M204 S250
G1 X126.862 Y120.104 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2092
M204 S5000
G1 X126.994 Y120.075 E.00403
G3 X127.476 Y120.013 I1.006 J5.923 E.01449
G1 X127.993 Y119.99 E.0154
G3 X126.445 Y120.195 I.007 J6.007 E1.07766
G1 X126.803 Y120.117 E.01092
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.994 Y120.075 E-.07427
G1 X127.476 Y120.013 E-.18476
G1 X127.794 Y119.999 E-.12097
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-1.072 J-.576 P1  F30000
G1 X120.602 Y133.398 Z8
G1 Z7.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2092
G1 X120.602 Y118.602 E.47578
G1 X135.398 Y118.602 E.47578
G1 X135.398 Y133.398 E.47578
G1 X120.662 Y133.398 E.47385
M204 S250
G1 X120.21 Y133.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2092
M204 S5000
G1 X120.21 Y118.21 E.46406
G1 X135.786 Y118.21 E.46396
G1 X135.79 Y133.79 E.46408
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.27 Y133.79 E.46227
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.267 Y132.79 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I1.206 J.162 P1  F30000
G1 X121.748 Y121.775 Z8
G1 Z7.6
G1 E.4 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F2092
G3 X123.775 Y119.748 I6.437 J4.41 E.08586
G1 X121.748 Y119.748 E.06037
G1 X121.748 Y121.715 E.05858
; WIPE_START
G1 F11934.123
G1 X121.748 Y120.715 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-.041 J1.216 P1  F30000
G1 X122.11 Y120.727 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.38965
G1 F2092
G1 X122.727 Y120.11 E.0239
G1 X122.11 Y120.11 E.0169
G1 X122.11 Y120.667 E.01526
; WIPE_START
G1 F12978.398
G1 X122.11 Y120.11 E-.2117
G1 X122.553 Y120.11 E-.1683
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I.318 J1.175 P1  F30000
G1 X125.279 Y119.371 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2092
G1 X121.371 Y119.371 E.11638
G1 X121.371 Y123.279 E.11638
G1 X121.777 Y122.436 E.02786
G3 X125.223 Y119.394 I6.195 J3.547 E.13939
; WIPE_START
G1 F11934.123
G1 X124.947 Y119.511 E-.114
G1 X124.393 Y119.802 E-.23763
G1 X124.33 Y119.842 E-.02837
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I.196 J1.201 P1  F30000
G1 X127.986 Y119.247 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.34336
G1 F2092
G1 X128.582 Y119.265 E.01415
; LINE_WIDTH: 0.36889
G1 X129.165 Y119.322 E.01508
; LINE_WIDTH: 0.417811
G3 X134.676 Y124.815 I-1.104 J6.619 E.2458
; LINE_WIDTH: 0.37091
G1 X134.734 Y125.404 E.01534
; LINE_WIDTH: 0.343663
G3 X134.734 Y126.582 I-9.044 J.593 E.02801
; LINE_WIDTH: 0.369135
G1 X134.677 Y127.17 E.01521
; LINE_WIDTH: 0.417833
G3 X129.185 Y132.676 I-6.619 J-1.11 E.24567
; LINE_WIDTH: 0.370875
G1 X128.596 Y132.734 E.01534
; LINE_WIDTH: 0.343658
G3 X127.418 Y132.734 I-.594 J-9.042 E.02801
; LINE_WIDTH: 0.369135
M73 P52 R7
G1 X126.83 Y132.677 E.01521
; LINE_WIDTH: 0.417833
G3 X121.324 Y127.185 I1.11 J-6.619 E.24567
; LINE_WIDTH: 0.37088
G1 X121.266 Y126.596 E.01534
; LINE_WIDTH: 0.343658
G3 X121.266 Y125.418 I9.042 J-.594 E.02801
; LINE_WIDTH: 0.369135
G1 X121.323 Y124.83 E.01521
; LINE_WIDTH: 0.417657
G3 X126.856 Y119.319 I6.61 J1.103 E.24677
; LINE_WIDTH: 0.369295
G1 X127.405 Y119.266 E.01422
; LINE_WIDTH: 0.34395
G1 X127.926 Y119.249 E.0124
G1 X128.005 Y118.953 F30000
; LINE_WIDTH: 0.355153
G1 F2092
G2 X126.848 Y118.977 I-.009 J27.231 E.02854
; LINE_WIDTH: 0.418317
G1 X126.205 Y118.994 E.01909
G1 X120.994 Y118.994 E.15451
G1 X120.994 Y124.201 E.1544
G1 X120.98 Y124.777 E.0171
; LINE_WIDTH: 0.370915
G1 X120.96 Y125.384 E.01573
; LINE_WIDTH: 0.343661
G2 X120.959 Y126.589 I27.554 J.616 E.02863
; LINE_WIDTH: 0.36914
G1 X120.978 Y127.192 E.01556
; LINE_WIDTH: 0.418449
G1 X120.994 Y127.799 E.018
G1 X120.994 Y133.006 E.15446
G1 X126.201 Y133.006 E.15446
G1 X126.777 Y133.02 E.0171
; LINE_WIDTH: 0.37091
G1 X127.384 Y133.04 E.01573
; LINE_WIDTH: 0.343658
G2 X128.589 Y133.041 I.616 J-27.573 E.02862
; LINE_WIDTH: 0.369135
G1 X129.192 Y133.022 E.01555
; LINE_WIDTH: 0.418446
G1 X129.799 Y133.006 E.018
G1 X135.006 Y133.006 E.15446
G1 X135.006 Y127.799 E.15446
G1 X135.02 Y127.223 E.0171
; LINE_WIDTH: 0.370865
G1 X135.04 Y126.616 E.01573
; LINE_WIDTH: 0.343663
G2 X135.041 Y125.411 I-27.573 J-.616 E.02862
; LINE_WIDTH: 0.369135
G1 X135.022 Y124.808 E.01556
; LINE_WIDTH: 0.418438
G1 X135.006 Y124.201 E.018
G1 X135.006 Y118.994 E.15445
G1 X129.799 Y118.994 E.15446
G1 X129.217 Y118.98 E.01725
; LINE_WIDTH: 0.370795
G1 X128.615 Y118.96 E.0156
; LINE_WIDTH: 0.343945
G1 X128.065 Y118.953 E.01309
; WIPE_START
G1 F14948.923
G1 X128.615 Y118.96 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-.292 J1.181 P1  F30000
G1 X133.273 Y120.11 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.38965
G1 F2092
G1 X133.89 Y120.727 E.0239
G1 X133.89 Y120.11 E.0169
G1 X133.333 Y120.11 E.01526
; WIPE_START
G1 F12978.398
G1 X133.89 Y120.11 E-.21169
G1 X133.89 Y120.553 E-.16831
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-1.167 J.346 P1  F30000
G1 X134.252 Y121.775 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2092
G1 X134.252 Y119.748 E.06037
G1 X132.225 Y119.748 E.06037
G3 X134.218 Y121.725 I-4.434 J6.465 E.08408
; WIPE_START
G1 F11934.123
G1 X133.756 Y121.117 E-.29047
G1 X133.596 Y120.944 E-.08953
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-1.113 J.492 P1  F30000
G1 X134.629 Y123.279 Z8
G1 Z7.6
G1 E.4 F1800
G1 F2092
G1 X134.629 Y119.371 E.11639
G1 X130.721 Y119.371 E.11638
G1 X131.564 Y119.777 E.02786
G3 X134.606 Y123.223 I-3.547 J6.195 E.13939
; WIPE_START
G1 F11934.123
G1 X134.489 Y122.947 E-.11404
G1 X134.198 Y122.393 E-.23764
G1 X134.158 Y122.33 E-.02831
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-1.217 J.014 P1  F30000
G1 X134.252 Y130.225 Z8
G1 Z7.6
G1 E.4 F1800
G1 F2092
G3 X132.225 Y132.252 I-6.437 J-4.41 E.08586
G1 X134.252 Y132.252 E.06037
G1 X134.252 Y130.285 E.05858
; WIPE_START
G1 F11934.123
G1 X134.252 Y131.285 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-.64 J-1.035 P1  F30000
G1 X133.273 Y131.89 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.38966
G1 F2092
G1 X133.89 Y131.89 E.0169
G1 X133.89 Y131.273 E.0169
G1 X133.315 Y131.847 E.02226
; WIPE_START
G1 F12978.024
G1 X133.89 Y131.273 E-.30884
G1 X133.89 Y131.46 E-.07116
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-.421 J-1.142 P1  F30000
G1 X130.721 Y132.629 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2092
G1 X134.629 Y132.629 E.11638
G1 X134.629 Y128.721 E.11638
G1 X134.223 Y129.564 E.02786
G3 X130.777 Y132.605 I-6.195 J-3.547 E.13939
; WIPE_START
G1 F11934.123
G1 X131.053 Y132.489 E-.11403
G1 X131.607 Y132.198 E-.23765
G1 X131.67 Y132.158 E-.02832
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I-.014 J-1.217 P1  F30000
G1 X123.775 Y132.252 Z8
G1 Z7.6
G1 E.4 F1800
G1 F2092
G3 X121.748 Y130.225 I4.41 J-6.437 E.08586
G1 X121.748 Y132.252 E.06037
G1 X123.715 Y132.252 E.05858
; WIPE_START
G1 F11934.123
G1 X122.715 Y132.252 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I1.035 J-.64 P1  F30000
G1 X122.11 Y131.273 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.38964
G1 F2092
G1 X122.11 Y131.89 E.0169
G1 X122.727 Y131.89 E.0169
G1 X122.153 Y131.315 E.02226
; WIPE_START
G1 F12978.773
G1 X122.727 Y131.89 E-.30885
G1 X122.54 Y131.89 E-.07115
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8 I1.142 J-.421 P1  F30000
G1 X121.371 Y128.721 Z8
G1 Z7.6
G1 E.4 F1800
; LINE_WIDTH: 0.41999
G1 F2092
G1 X121.371 Y132.629 E.11638
G1 X125.279 Y132.629 E.11638
G1 X124.436 Y132.223 E.02786
G3 X121.394 Y128.777 I3.547 J-6.195 E.13939
; CHANGE_LAYER
; Z_HEIGHT: 7.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F11934.123
G1 X121.511 Y129.053 E-.11401
G1 X121.802 Y129.607 E-.23763
G1 X121.842 Y129.67 E-.02836
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 39/74
; update layer progress
M73 L39
M991 S0 P38 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z8 I1.077 J.566 P1  F30000
G1 X126.871 Y120.1 Z8
G1 Z7.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2341
M204 S5000
G1 X126.956 Y120.081 E.00262
G3 X127.476 Y120.013 I1.043 J5.916 E.01563
G1 X127.991 Y119.99 E.01533
G3 X126.444 Y120.195 I.009 J6.007 E1.07771
G1 X126.812 Y120.113 E.01121
M204 S10000
G1 X127.2 Y119.654 F30000
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F2341
G1 X127.151 Y119.435 E.00719
G1 X127.584 Y119.298 E.0146
G1 X127.481 Y118.629 E.02177
G1 X127.989 Y118.629 E.01634
G1 X128.52 Y118.629 E.01707
G1 X128.417 Y119.3 E.02183
G1 X128.842 Y119.434 E.01433
G1 X128.793 Y119.653 E.0072
G2 X127.259 Y119.645 I-.794 J5.14 E.04951
; WIPE_START
G1 F11054.348
G1 X127.151 Y119.435 E-.08952
G1 X127.584 Y119.298 E-.17259
G1 X127.537 Y118.992 E-.11789
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.884 J-.837 P1  F30000
G1 X121.653 Y125.206 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
G2 X121.653 Y126.793 I5.117 J.794 E.05123
G1 X121.434 Y126.842 E.0072
G1 X121.3 Y126.415 E.01438
G1 X120.629 Y126.519 E.02183
G1 X120.629 Y125.481 E.03336
G1 X121.3 Y125.585 E.02183
G1 X121.434 Y125.158 E.01438
G1 X121.594 Y125.193 E.00527
; WIPE_START
G1 F11054.348
G1 X121.622 Y125.442 E-.09505
G1 X121.597 Y126 E-.2122
G1 X121.606 Y126.191 E-.07275
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.9 J.819 P1  F30000
G1 X127.206 Y132.347 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
G1 X127.442 Y132.378 E.00764
G2 X128.793 Y132.347 I.519 J-6.865 E.04353
G1 X128.842 Y132.566 E.0072
G1 X128.415 Y132.7 E.01438
G1 X128.519 Y133.371 E.02183
G1 X127.481 Y133.371 E.03336
G1 X127.585 Y132.7 E.02183
G1 X127.158 Y132.566 E.01438
G1 X127.193 Y132.406 E.00527
; WIPE_START
G1 F11054.348
G1 X127.442 Y132.378 E-.09505
G1 X128 Y132.403 E-.2122
G1 X128.191 Y132.394 E-.07274
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.924 J.792 P1  F30000
G1 X134.347 Y125.207 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
G1 X134.566 Y125.158 E.0072
G1 X134.7 Y125.585 E.01438
G1 X135.371 Y125.481 E.02183
G1 X135.371 Y126.519 E.03336
G1 X134.7 Y126.415 E.02183
G1 X134.566 Y126.842 E.01438
G1 X134.347 Y126.794 E.0072
G2 X134.356 Y125.266 I-5.117 J-.794 E.0493
; WIPE_START
G1 F11054.348
G1 X134.566 Y125.158 E-.08957
G1 X134.7 Y125.585 E-.16988
G1 X135.014 Y125.536 E-.12055
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.592 J-1.063 P1  F30000
G1 X120.237 Y133.763 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F2341
M204 S5000
G1 X120.237 Y118.237 E.46248
G1 X135.763 Y118.237 E.46248
G1 X135.763 Y133.763 E.46246
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X120.297 Y133.763 E.46069
; WIPE_START
G1 F11933.819
M204 S10000
M73 P53 R7
G1 X120.293 Y132.763 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.062 J1.215 P1  F30000
G1 X126.99 Y132.419 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.55651
G1 F2341
G3 X125.259 Y131.851 I2.342 J-10.057 E.07398
G1 X124.76 Y131.59 E.02287
G1 X124.294 Y131.293 E.02242
G1 X123.855 Y130.957 E.02242
G1 X123.431 Y130.569 E.02332
G1 X123.057 Y130.162 E.02242
G1 X122.707 Y129.706 E.02332
G1 X122.404 Y129.231 E.02287
G1 X122.144 Y128.731 E.02288
G1 X121.924 Y128.199 E.02331
G3 X121.581 Y127.01 I13.694 J-4.601 E.05024
; WIPE_START
G1 F8761.863
G1 X121.755 Y127.662 E-.25633
G1 X121.853 Y127.972 E-.12367
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.81 J-.908 P1  F30000
G1 X120.498 Y126.764 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F2341
M204 S2000
G1 X121.489 Y127.754 E.04172
G1 X121.772 Y128.571
G1 X120.444 Y127.243 E.05595
G1 X120.444 Y127.776
G1 X122.37 Y129.702 E.08112
; WIPE_START
G1 F11933.819
M204 S10000
G1 X121.663 Y128.995 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.741 J.965 P1  F30000
G1 X126.246 Y132.511 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
M204 S2000
G1 X127.236 Y133.502 E.04172
G1 X126.757 Y133.556
G1 X125.429 Y132.228 E.05595
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.136 Y132.935 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.704 J-.992 P1  F30000
G1 X124.298 Y131.63 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
M204 S2000
G1 X126.224 Y133.556 E.08111
G1 X125.69 Y133.556
G1 X120.444 Y128.31 E.221
G1 X120.444 Y128.843
G1 X125.157 Y133.556 E.19854
G1 X124.624 Y133.556
G1 X120.444 Y129.376 E.17607
G1 X120.444 Y129.909
G1 X124.091 Y133.556 E.15361
G1 X123.557 Y133.556
G1 X120.444 Y130.443 E.13115
G1 X120.444 Y130.976
G1 X123.024 Y133.556 E.10868
G1 X122.491 Y133.556
G1 X120.444 Y131.509 E.08622
G1 X120.444 Y132.042
G1 X121.958 Y133.556 E.06376
G1 X121.424 Y133.556
G1 X120.444 Y132.576 E.04129
G1 X120.444 Y133.109
G1 X120.891 Y133.556 E.01883
; WIPE_START
G1 F11933.819
M204 S10000
G1 X120.444 Y133.109 E-.24021
G1 X120.444 Y132.741 E-.13979
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.325 J1.173 P1  F30000
G1 X124.238 Y131.691 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.218183
G1 F2341
G1 X124.092 Y131.574 E.00258
; LINE_WIDTH: 0.188731
G1 X123.871 Y131.38 E.00339
; LINE_WIDTH: 0.150024
G1 X123.648 Y131.184 E.00252
; LINE_WIDTH: 0.117936
G1 X123.222 Y130.776 E.00349
G1 X122.813 Y130.35 E.0035
; LINE_WIDTH: 0.150276
G1 X122.62 Y130.129 E.00249
; LINE_WIDTH: 0.191059
G1 X122.404 Y129.881 E.00384
; LINE_WIDTH: 0.22145
G1 X122.309 Y129.763 E.00215
G1 X121.97 Y129.008 F30000
; LINE_WIDTH: 0.126803
G1 F2341
G3 X121.706 Y128.638 I8.256 J-6.165 E.00301
; WIPE_START
G1 F15000
G1 X121.97 Y129.008 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.786 J.929 P1  F30000
G1 X126.182 Y132.575 Z8.2
G1 Z7.8
G1 E.4 F1800
; LINE_WIDTH: 0.0946601
G1 F2341
G1 X125.89 Y132.397 E.0014
G1 X125.366 Y132.29 F30000
; LINE_WIDTH: 0.191949
G1 F2341
G1 X125.253 Y132.214 E.0016
; LINE_WIDTH: 0.154876
G1 X125.136 Y132.136 E.00124
; LINE_WIDTH: 0.11053
G1 X124.992 Y132.03 E.00096
; WIPE_START
G1 F15000
G1 X125.136 Y132.136 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.089 J1.214 P1  F30000
G1 X129.01 Y132.419 Z8.2
G1 Z7.8
G1 E.4 F1800
; LINE_WIDTH: 0.556507
G1 F2341
G2 X130.199 Y132.076 I-3.409 J-14.03 E.05024
G1 X130.731 Y131.856 E.02331
G1 X131.231 Y131.596 E.02288
G1 X131.706 Y131.293 E.02287
G1 X132.162 Y130.943 E.02331
G1 X132.569 Y130.569 E.02242
G1 X132.957 Y130.145 E.02332
G1 X133.293 Y129.706 E.02242
G1 X133.59 Y129.24 E.02242
G1 X133.851 Y128.741 E.02287
G2 X134.419 Y127.01 I-9.489 J-4.072 E.07398
; WIPE_START
G1 F8761.917
G1 X134.245 Y127.662 E-.25626
G1 X134.147 Y127.972 E-.12374
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.442 J1.134 P1  F30000
G1 X135.556 Y127.423 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F2341
M204 S2000
G1 X134.841 Y126.709 E.03011
G1 X134.713 Y127.114
G1 X135.556 Y127.957 E.03549
G1 X135.556 Y128.49
G1 X134.585 Y127.519 E.04088
G1 X134.458 Y127.925
G1 X135.556 Y129.023 E.04626
G1 X135.556 Y129.556
G1 X134.328 Y128.329 E.05172
G1 X134.172 Y128.706
G1 X135.556 Y130.09 E.0583
G1 X135.556 Y130.623
G1 X133.999 Y129.067 E.06556
G1 X133.814 Y129.414
G1 X135.556 Y131.156 E.07339
G1 X135.556 Y131.689
G1 X133.606 Y129.74 E.08213
G1 X133.384 Y130.051
G1 X135.556 Y132.223 E.09149
G1 X135.556 Y132.756
G1 X133.151 Y130.351 E.1013
G1 X132.896 Y130.63
G1 X135.556 Y133.289 E.11204
G1 X135.289 Y133.556
G1 X132.629 Y130.896 E.11204
G1 X132.351 Y131.151
G1 X134.756 Y133.556 E.10129
G1 X134.223 Y133.556
G1 X132.051 Y131.384 E.09148
G1 X131.74 Y131.606
G1 X133.689 Y133.556 E.08213
G1 X133.156 Y133.556
G1 X131.414 Y131.814 E.07339
G1 X131.066 Y131.999
G1 X132.623 Y133.556 E.06556
G1 X132.09 Y133.556
G1 X130.706 Y132.172 E.0583
G1 X130.329 Y132.328
G1 X131.556 Y133.556 E.05172
G1 X131.023 Y133.556
G1 X129.925 Y132.458 E.04626
G1 X129.519 Y132.585
G1 X130.49 Y133.556 E.04088
G1 X129.957 Y133.556
G1 X129.114 Y132.713 E.03549
G1 X128.709 Y132.841
G1 X129.423 Y133.556 E.03011
; WIPE_START
G1 F11933.819
M204 S10000
G1 X128.716 Y132.849 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.985 J.715 P1  F30000
G1 X134.419 Y124.99 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.55651
G1 F2341
G2 X133.851 Y123.259 I-10.053 J2.34 E.07399
G1 X133.596 Y122.769 E.02242
G1 X133.299 Y122.303 E.02242
G1 X132.957 Y121.855 E.02286
G1 X132.569 Y121.431 E.02332
G1 X132.162 Y121.057 E.02242
G1 X131.706 Y120.707 E.02332
G1 X131.231 Y120.404 E.02286
G1 X130.731 Y120.144 E.02288
G1 X130.199 Y119.924 E.02331
G2 X129.01 Y119.581 I-4.598 J13.685 E.05024
; WIPE_START
G1 F8761.855
G1 X129.662 Y119.755 E-.25629
G1 X129.972 Y119.853 E-.12371
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.11 J-1.212 P1  F30000
G1 X126.983 Y119.582 Z8.2
G1 Z7.8
G1 E.4 F1800
; LINE_WIDTH: 0.556455
G1 F2341
G2 X125.259 Y120.149 I2.361 J10.094 E.07371
G1 X124.769 Y120.404 E.02242
G1 X124.285 Y120.714 E.02332
G1 X123.847 Y121.05 E.02241
G1 X123.439 Y121.423 E.02242
G1 X123.057 Y121.838 E.02287
G1 X122.707 Y122.294 E.02332
G1 X122.404 Y122.769 E.02286
G1 X122.144 Y123.269 E.02288
G1 X121.924 Y123.8 E.02331
G2 X121.581 Y124.99 I13.692 J4.6 E.05023
; WIPE_START
G1 F8762.796
G1 X121.755 Y124.338 E-.25624
G1 X121.853 Y124.028 E-.12376
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.929 J.786 P1  F30000
G1 X126.577 Y118.444 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F2341
M204 S2000
G1 X127.29 Y119.158 E.03005
G1 X126.885 Y119.286
G1 X126.044 Y118.444 E.03546
G1 X125.51 Y118.444
G1 X126.48 Y119.414 E.04086
G1 X126.075 Y119.543
G1 X124.977 Y118.444 E.04627
G1 X124.444 Y118.444
G1 X125.671 Y119.672 E.05171
G1 X125.294 Y119.828
G1 X123.91 Y118.444 E.05829
G1 X123.377 Y118.444
G1 X124.933 Y120.001 E.06556
G1 X124.586 Y120.186
G1 X122.844 Y118.444 E.07339
G1 X122.311 Y118.444
G1 X124.26 Y120.394 E.08213
G1 X123.949 Y120.616
G1 X121.777 Y118.444 E.09148
G1 X121.244 Y118.444
G1 X123.649 Y120.849 E.1013
G1 X123.37 Y121.104
G1 X120.711 Y118.444 E.11204
G1 X120.444 Y118.711
G1 X123.104 Y121.371 E.11204
G1 X122.849 Y121.649
G1 X120.444 Y119.244 E.10129
G1 X120.444 Y119.777
G1 X122.616 Y121.949 E.09148
G1 X122.394 Y122.26
G1 X120.444 Y120.311 E.08213
G1 X120.444 Y120.844
G1 X122.186 Y122.586 E.07339
G1 X122.001 Y122.934
G1 X120.444 Y121.377 E.06556
G1 X120.444 Y121.91
G1 X121.828 Y123.294 E.0583
G1 X121.672 Y123.671
G1 X120.444 Y122.444 E.05172
G1 X120.444 Y122.977
G1 X121.542 Y124.075 E.04626
G1 X121.415 Y124.481
G1 X120.444 Y123.51 E.04088
G1 X120.444 Y124.043
G1 X121.287 Y124.886 E.03549
G1 X121.159 Y125.291
G1 X120.444 Y124.577 E.03011
; WIPE_START
G1 F11933.819
M204 S10000
M73 P54 R7
G1 X121.151 Y125.284 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.535 J1.093 P1  F30000
G1 X135.109 Y118.445 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
M204 S2000
G1 X135.556 Y118.891 E.01881
G1 X135.556 Y119.425
G1 X134.576 Y118.445 E.04127
G1 X134.043 Y118.445
G1 X135.556 Y119.958 E.06374
G1 X135.556 Y120.491
G1 X133.509 Y118.445 E.0862
G1 X132.976 Y118.445
G1 X135.556 Y121.024 E.10867
G1 X135.556 Y121.558
G1 X132.443 Y118.445 E.13113
G1 X131.91 Y118.445
G1 X135.556 Y122.091 E.15359
G1 X135.556 Y122.624
G1 X131.376 Y118.445 E.17606
G1 X130.843 Y118.445
G1 X135.556 Y123.157 E.19852
G1 X135.556 Y123.691
G1 X130.31 Y118.445 E.22099
G1 X129.777 Y118.445
G1 X131.701 Y120.37 E.08109
; WIPE_START
G1 F11933.819
M204 S10000
G1 X130.994 Y119.662 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.306 J-1.178 P1  F30000
G1 X130.571 Y119.772 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
M204 S2000
G1 X129.243 Y118.445 E.05593
G1 X128.765 Y118.5
G1 X129.754 Y119.489 E.04166
; WIPE_START
G1 F11933.819
M204 S10000
G1 X129.047 Y118.781 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.741 J.965 P1  F30000
G1 X133.63 Y122.298 Z8.2
G1 Z7.8
G1 E.4 F1800
G1 F2341
M204 S2000
G1 X135.556 Y124.224 E.08111
G1 X135.556 Y124.757
G1 X134.228 Y123.429 E.05595
G1 X134.511 Y124.246
G1 X135.502 Y125.236 E.04171
; WIPE_START
G1 F11933.819
M204 S10000
G1 X134.794 Y124.529 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I1.096 J-.528 P1  F30000
G1 X133.691 Y122.238 Z8.2
G1 Z7.8
G1 E.4 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.218116
G1 F2341
G1 X133.574 Y122.092 E.00258
; LINE_WIDTH: 0.188621
G1 X133.38 Y121.871 E.00338
; LINE_WIDTH: 0.149927
G1 X133.184 Y121.648 E.00252
; LINE_WIDTH: 0.117841
G1 X132.776 Y121.222 E.00349
G1 X132.35 Y120.813 E.0035
; LINE_WIDTH: 0.150174
G1 X132.129 Y120.62 E.00249
; LINE_WIDTH: 0.189109
G1 X131.902 Y120.421 E.00348
; LINE_WIDTH: 0.218521
G1 X131.762 Y120.309 E.00249
; WIPE_START
G1 F15000
G1 X131.902 Y120.421 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I-.944 J.768 P1  F30000
G1 X134.294 Y123.362 Z8.2
G1 Z7.8
G1 E.4 F1800
; LINE_WIDTH: 0.126738
G1 F2341
G2 X134.03 Y122.992 I-8.324 J5.651 E.00301
; WIPE_START
G1 F15000
G1 X134.294 Y123.362 E-.38
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.2 I.874 J-.847 P1  F30000
G1 X131.008 Y119.97 Z8.2
G1 Z7.8
G1 E.4 F1800
; LINE_WIDTH: 0.112468
G1 F2341
G1 X130.86 Y119.862 E.001
; LINE_WIDTH: 0.155366
G1 X130.747 Y119.786 E.00121
; LINE_WIDTH: 0.19192
G1 X130.633 Y119.71 E.0016
; CHANGE_LAYER
; Z_HEIGHT: 8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X130.747 Y119.786 E-.38
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 40/74
; update layer progress
M73 L40
M991 S0 P39 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z8.2 I.022 J-1.217 P1  F30000
G1 X126.796 Y119.715 Z8.2
G1 Z8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G1 X126.889 Y119.695 E.00307
G3 X127.442 Y119.622 I1.111 J6.302 E.01795
G1 X127.988 Y119.597 E.01758
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.343 Y119.816 I.011 J6.4 E1.23948
G1 X126.737 Y119.728 E.01298
M204 S250
G1 X126.88 Y120.098 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1073
M204 S5000
G1 X126.957 Y120.081 E.00233
G3 X127.476 Y120.013 I1.043 J5.916 E.01561
G1 X127.989 Y119.99 E.01527
G3 X126.444 Y120.195 I.011 J6.007 E1.07777
G1 X126.822 Y120.111 E.01152
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.957 Y120.081 E-.05252
G1 X127.476 Y120.013 E-.19912
G1 X127.814 Y119.998 E-.12836
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.4 I-.34 J-1.168 P1  F30000
G1 X122.641 Y121.503 Z8.4
G1 Z8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G3 X128.003 Y119.003 I5.359 J4.494 E.19643
G1 X128.609 Y119.029 E.01953
G3 X122.602 Y121.549 I-.609 J6.967 E1.19521
M204 S250
G1 X122.34 Y121.251 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1073
M204 S5000
M73 P55 R7
G3 X128.003 Y118.61 I5.66 J4.746 E.19215
G1 X128.643 Y118.638 E.0191
G3 X122.302 Y121.297 I-.643 J7.358 E1.16933
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230002
G1 F1073
G1 X122.872 Y121.697 E.00045
G3 X128.578 Y119.325 I5.141 J4.317 E.09489
G1 X129.154 Y119.4 E.00858
G1 X129.73 Y119.527 E.00872
G1 X130.291 Y119.704 E.0087
G1 X130.831 Y119.928 E.00864
G1 X131.346 Y120.196 E.00858
G1 X131.846 Y120.514 E.00876
G1 X132.307 Y120.867 E.00857
G1 X132.738 Y121.262 E.00864
G1 X133.132 Y121.693 E.00864
G1 X133.486 Y122.154 E.00858
G1 X133.804 Y122.654 E.00876
G1 X134.072 Y123.169 E.00858
G1 X134.296 Y123.708 E.00863
G1 X134.472 Y124.266 E.00864
G1 X134.597 Y124.833 E.00858
G1 X134.675 Y125.42 E.00876
G1 X134.7 Y126 E.00857
G1 X134.674 Y126.584 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.473 Y127.73 E.00858
G1 X134.294 Y128.295 E.00876
G1 X134.072 Y128.831 E.00858
G1 X133.802 Y129.35 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.135 Y130.303 E.00857
G1 X132.735 Y130.74 E.00876
G1 X132.307 Y131.132 E.00858
G1 X131.843 Y131.488 E.00864
G1 X131.35 Y131.802 E.00864
G1 X130.835 Y132.07 E.00858
G1 X130.288 Y132.297 E.00876
G1 X129.734 Y132.472 E.00858
G1 X129.163 Y132.598 E.00864
G1 X128.584 Y132.674 E.00864
G1 X128.004 Y132.7 E.00858
G1 X127.412 Y132.674 E.00876
G1 X126.837 Y132.598 E.00858
G1 X126.266 Y132.472 E.00864
G1 X125.709 Y132.296 E.00864
G1 X125.172 Y132.074 E.00858
G1 X124.647 Y131.8 E.00876
G1 X124.157 Y131.488 E.00858
G1 X123.693 Y131.133 E.00863
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.84 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00863
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y126 E.00864
G3 X122.517 Y122.16 I6.713 J.014 E.06045
G1 X122.813 Y121.765 E.0073
; CHANGE_LAYER
; Z_HEIGHT: 8.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03407
G1 X123.265 Y121.26 E-.22361
G1 X123.503 Y121.042 E-.12232
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 41/74
; update layer progress
M73 L41
M991 S0 P40 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z8.4 I.454 J1.129 P1  F30000
G1 X126.806 Y119.713 Z8.4
G1 Z8.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G1 X126.888 Y119.695 E.00272
G3 X127.442 Y119.622 I1.111 J6.302 E.01796
G1 X127.986 Y119.597 E.01751
G3 X126.343 Y119.816 I.013 J6.4 E1.23954
G1 X126.747 Y119.726 E.01332
M204 S250
G1 X126.891 Y120.096 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G1 X126.956 Y120.081 E.002
G3 X127.476 Y120.013 I1.043 J5.916 E.01563
G1 X127.986 Y119.99 E.01521
G3 X126.444 Y120.195 I.013 J6.007 E1.07783
G1 X126.832 Y120.109 E.01183
; WIPE_START
G1 F11933.819
M204 S10000
M73 P56 R7
G1 X126.956 Y120.081 E-.04836
G1 X127.476 Y120.013 E-.19936
G1 X127.824 Y119.997 E-.13228
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.6 I-.34 J-1.168 P1  F30000
G1 X122.644 Y121.505 Z8.6
G1 Z8.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G3 X128.608 Y119.029 I5.362 J4.494 E.21585
G3 X129.215 Y132.891 I-.616 J6.971 E.64764
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X122.605 Y121.551 I-1.209 J-6.891 E.5475
M204 S250
G1 X122.343 Y121.253 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G3 X128.642 Y118.638 I5.663 J4.746 E.21116
G3 X129.283 Y133.278 I-.65 J7.362 E.63356
G3 X122.305 Y121.299 I-1.277 J-7.278 E.53569
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.229934
G1 F1067
G1 X122.868 Y121.693 E.00045
G3 X126.27 Y132.472 I5.132 J4.307 E.42316
G1 X125.708 Y132.296 E.00869
G1 X125.169 Y132.072 E.00863
M73 P56 R6
G1 X124.65 Y131.802 E.00864
G1 X124.16 Y131.49 E.00857
G1 X123.693 Y131.132 E.0087
G1 X123.265 Y130.74 E.00857
G1 X122.865 Y130.303 E.00876
G1 X122.512 Y129.843 E.00857
G1 X122.198 Y129.35 E.00864
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00863
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00863
G1 X121.326 Y126.584 E.00864
G1 X121.3 Y126 E.00863
G3 X122.512 Y122.157 I6.7 J0 E.06046
G1 X122.813 Y121.765 E.0073
; CHANGE_LAYER
; Z_HEIGHT: 8.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.868 Y121.693 E-.03426
G1 X123.26 Y121.265 E-.2205
G1 X123.503 Y121.043 E-.12524
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 42/74
; update layer progress
M73 L42
M991 S0 P41 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z8.6 I.454 J1.129 P1  F30000
G1 X126.816 Y119.711 Z8.6
G1 Z8.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G1 X126.888 Y119.695 E.00237
G3 X127.442 Y119.622 I1.111 J6.302 E.01796
G1 X127.984 Y119.597 E.01745
G3 X126.343 Y119.815 I.015 J6.4 E1.23962
G1 X126.758 Y119.724 E.01367
M204 S250
G1 X126.901 Y120.093 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P57 R6
G1 F1067
M204 S5000
G1 X126.956 Y120.081 E.00168
G3 X127.476 Y120.013 I1.043 J5.916 E.01563
G1 X127.984 Y119.99 E.01515
G3 X126.444 Y120.195 I.015 J6.007 E1.0779
G1 X126.843 Y120.106 E.01215
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.956 Y120.081 E-.04424
G1 X127.476 Y120.013 E-.19931
G1 X127.835 Y119.997 E-.13645
; WIPE_END
G1 E-.02 F1800
G17
G3 Z8.8 I-.34 J-1.169 P1  F30000
G1 X122.644 Y121.505 Z8.8
G1 Z8.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G3 X128.607 Y119.029 I5.362 J4.494 E.21583
G3 X129.215 Y132.891 I-.615 J6.971 E.64767
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X122.605 Y121.552 I-1.209 J-6.891 E.5475
M204 S250
G1 X122.343 Y121.253 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G3 X128.641 Y118.638 I5.663 J4.746 E.21114
G3 X129.283 Y133.278 I-.65 J7.362 E.63358
G3 X122.305 Y121.299 I-1.277 J-7.278 E.53569
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230014
G1 F1067
G1 X122.868 Y121.693 E.00044
G3 X129.16 Y119.401 I5.132 J4.307 E.10364
G1 X129.738 Y119.529 E.00874
G1 X130.292 Y119.704 E.00858
G1 X130.831 Y119.928 E.00863
G1 X131.35 Y120.198 E.00864
G1 X131.84 Y120.51 E.00858
G1 X132.31 Y120.87 E.00876
G1 X132.738 Y121.262 E.00858
G1 X133.132 Y121.693 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.8 Y122.647 E.00858
G1 X134.074 Y123.172 E.00876
G1 X134.296 Y123.708 E.00858
G1 X134.472 Y124.266 E.00864
G1 X134.599 Y124.841 E.0087
G1 X134.674 Y125.416 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.599 Y127.159 E.00858
G1 X134.47 Y127.738 E.00876
G1 X134.296 Y128.292 E.00858
G1 X134.072 Y128.831 E.00863
G1 X133.802 Y129.35 E.00864
G1 X133.49 Y129.84 E.00858
G1 X133.13 Y130.31 E.00876
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.843 Y131.488 E.00864
G1 X131.353 Y131.8 E.00858
G1 X130.831 Y132.072 E.0087
G1 X130.292 Y132.296 E.00863
G1 X129.738 Y132.47 E.00858
M73 P58 R6
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00863
G1 X124.65 Y131.802 E.00864
G1 X124.16 Y131.49 E.00858
G1 X123.693 Y131.132 E.0087
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.84 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00863
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y126 E.00864
G3 X122.514 Y122.154 I6.7 J0 E.06055
G1 X122.813 Y121.765 E.00724
; CHANGE_LAYER
; Z_HEIGHT: 8.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X122.868 Y121.693 E-.03423
G1 X123.26 Y121.265 E-.22055
G1 X123.502 Y121.043 E-.12521
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 43/74
; update layer progress
M73 L43
M991 S0 P42 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z8.8 I.453 J1.129 P1  F30000
G1 X126.827 Y119.708 Z8.8
G1 Z8.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G1 X126.889 Y119.695 E.00203
G3 X127.46 Y119.62 I1.111 J6.302 E.01851
G1 X127.982 Y119.597 E.01681
G3 X126.343 Y119.816 I.018 J6.399 E1.23958
G1 X126.769 Y119.721 E.01402
M204 S250
G1 X126.912 Y120.091 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G1 X126.957 Y120.081 E.00136
G3 X127.493 Y120.011 I1.043 J5.916 E.01613
G1 X127.982 Y119.99 E.01458
G3 X126.444 Y120.195 I.018 J6.007 E1.07791
G1 X126.853 Y120.104 E.01248
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.957 Y120.081 E-.04017
G1 X127.493 Y120.011 E-.20571
G1 X127.846 Y119.996 E-.13412
; WIPE_END
G1 E-.02 F1800
G17
G3 Z9 I-.339 J-1.169 P1  F30000
G1 X122.644 Y121.505 Z9
G1 Z8.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G3 X128.606 Y119.029 I5.362 J4.494 E.21578
G3 X129.215 Y132.891 I-.613 J6.971 E.64772
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X122.605 Y121.552 I-1.209 J-6.891 E.5475
M204 S250
G1 X122.343 Y121.253 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G3 X128.64 Y118.638 I5.663 J4.746 E.2111
G3 X129.283 Y133.278 I-.648 J7.362 E.63362
G3 X122.305 Y121.299 I-1.277 J-7.278 E.53569
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230013
M73 P59 R6
G1 F1067
G1 X122.872 Y121.697 E.00045
G3 X128.579 Y119.325 I5.141 J4.317 E.09491
G1 X129.166 Y119.402 E.00875
G1 X129.734 Y119.528 E.00861
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00863
G1 X131.346 Y120.196 E.00858
G1 X131.846 Y120.514 E.00876
G1 X132.307 Y120.868 E.00858
G1 X132.738 Y121.262 E.00864
G1 X133.132 Y121.693 E.00864
G1 X133.486 Y122.154 E.00858
G1 X133.804 Y122.654 E.00876
G1 X134.072 Y123.169 E.00858
G1 X134.296 Y123.708 E.00863
G1 X134.472 Y124.266 E.00864
G1 X134.597 Y124.833 E.00858
G1 X134.675 Y125.42 E.00876
G1 X134.7 Y126 E.00858
G1 X134.674 Y126.584 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.473 Y127.73 E.00858
G1 X134.294 Y128.295 E.00876
G1 X134.072 Y128.831 E.00858
G1 X133.802 Y129.35 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.135 Y130.303 E.00858
G1 X132.735 Y130.74 E.00876
G1 X132.307 Y131.132 E.00858
G1 X131.843 Y131.488 E.00864
G1 X131.35 Y131.802 E.00864
G1 X130.835 Y132.07 E.00858
G1 X130.288 Y132.297 E.00876
G1 X129.734 Y132.472 E.00858
G1 X129.163 Y132.598 E.00864
G1 X128.584 Y132.674 E.00864
G1 X128.004 Y132.7 E.00858
G1 X127.412 Y132.674 E.00876
G1 X126.837 Y132.598 E.00858
G1 X126.266 Y132.472 E.00864
G1 X125.708 Y132.296 E.00864
G1 X125.172 Y132.074 E.00858
G1 X124.647 Y131.8 E.00876
G1 X124.157 Y131.488 E.00858
G1 X123.693 Y131.132 E.00864
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.84 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00863
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y125.996 E.0087
G3 X122.517 Y122.16 I6.713 J.018 E.0604
G1 X122.813 Y121.765 E.0073
; CHANGE_LAYER
; Z_HEIGHT: 8.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03418
G1 X123.265 Y121.26 E-.22357
G1 X123.503 Y121.042 E-.12226
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 44/74
; update layer progress
M73 L44
M991 S0 P43 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z9 I.453 J1.13 P1  F30000
G1 X126.838 Y119.706 Z9
G1 Z8.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G1 X126.882 Y119.696 E.00143
G3 X127.463 Y119.62 I1.117 J6.302 E.01887
G3 X128.562 Y119.622 I.532 J8.241 E.03535
G3 X126.343 Y119.816 I-.563 J6.376 E1.22121
G1 X126.78 Y119.719 E.01439
M204 S250
G1 X126.923 Y120.088 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G1 X126.954 Y120.082 E.00095
G3 X127.496 Y120.011 I1.046 J5.918 E.01628
G3 X128.524 Y120.013 I.501 J7.817 E.03063
G3 X126.444 Y120.195 I-.524 J5.987 E1.0623
G1 X126.864 Y120.101 E.01282
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.954 Y120.082 E-.03492
G1 X127.496 Y120.011 E-.20764
G1 X127.857 Y119.995 E-.13744
; WIPE_END
G1 E-.02 F1800
G17
G3 Z9.2 I-.339 J-1.169 P1  F30000
G1 X122.644 Y121.505 Z9.2
G1 Z8.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G3 X128.605 Y119.029 I5.362 J4.494 E.21575
G3 X129.215 Y132.891 I-.612 J6.972 E.64775
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X122.605 Y121.552 I-1.209 J-6.891 E.5475
M204 S250
G1 X122.343 Y121.253 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P60 R6
G1 F1067
M204 S5000
G3 X128.639 Y118.638 I5.663 J4.746 E.21106
G3 X129.283 Y133.278 I-.647 J7.362 E.63366
G3 X122.305 Y121.299 I-1.277 J-7.278 E.53569
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.22998
G1 F1067
G1 X122.868 Y121.693 E.00044
G3 X129.161 Y119.401 I5.132 J4.307 E.10363
G1 X129.738 Y119.529 E.00873
G1 X130.292 Y119.704 E.00858
G1 X130.831 Y119.928 E.00863
G1 X131.35 Y120.198 E.00864
G1 X131.84 Y120.51 E.00858
G1 X132.31 Y120.87 E.00875
G1 X132.738 Y121.262 E.00858
G1 X133.132 Y121.693 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.8 Y122.647 E.00858
G1 X134.074 Y123.172 E.00876
G1 X134.296 Y123.708 E.00858
G1 X134.472 Y124.266 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.674 Y125.412 E.00858
G1 X134.7 Y126.004 E.00875
G1 X134.674 Y126.584 E.00857
G1 X134.598 Y127.163 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.297 Y128.288 E.00858
G1 X134.07 Y128.835 E.00875
G1 X133.802 Y129.35 E.00858
G1 X133.488 Y129.843 E.00864
G1 X133.132 Y130.307 E.00864
G1 X132.74 Y130.735 E.00858
G1 X132.307 Y131.132 E.0087
G1 X131.84 Y131.49 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00864
G1 X130.292 Y132.296 E.00863
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00863
G1 X127.416 Y132.674 E.00863
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00863
G1 X124.65 Y131.802 E.00864
G1 X124.16 Y131.49 E.00858
G1 X123.69 Y131.13 E.00875
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00875
G3 X122.514 Y122.154 I6.7 J.004 E.06048
G1 X122.813 Y121.765 E.00724
; CHANGE_LAYER
; Z_HEIGHT: 9
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.868 Y121.693 E-.03424
G1 X123.26 Y121.265 E-.22055
G1 X123.502 Y121.043 E-.12521
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 45/74
; update layer progress
M73 L45
M991 S0 P44 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z9.2 I.452 J1.13 P1  F30000
G1 X126.85 Y119.703 Z9.2
G1 Z9
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G1 X126.882 Y119.696 E.00106
G3 X127.466 Y119.62 I1.118 J6.301 E.01894
G3 X128.561 Y119.622 I.53 J8.071 E.03524
G3 X126.343 Y119.816 I-.561 J6.375 E1.22103
G1 X126.791 Y119.716 E.01476
M204 S250
G1 X126.934 Y120.086 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G1 X126.954 Y120.082 E.0006
G3 X127.498 Y120.011 I1.046 J5.916 E.01635
G3 X128.523 Y120.013 I.499 J7.624 E.03055
G3 X126.444 Y120.195 I-.523 J5.984 E1.06183
G1 X126.876 Y120.099 E.01316
; WIPE_START
G1 F11933.819
M204 S10000
M73 P61 R6
G1 X126.954 Y120.082 E-.03048
G1 X127.498 Y120.011 E-.20847
G1 X127.869 Y119.995 E-.14105
; WIPE_END
G1 E-.02 F1800
G17
G3 Z9.4 I-.338 J-1.169 P1  F30000
G1 X122.644 Y121.505 Z9.4
G1 Z9
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1067
G3 X128.603 Y119.029 I5.362 J4.494 E.2157
G3 X129.215 Y132.891 I-.611 J6.972 E.64779
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X122.605 Y121.552 I-1.209 J-6.891 E.5475
M204 S250
G1 X122.343 Y121.253 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1067
M204 S5000
G3 X128.638 Y118.638 I5.663 J4.746 E.21102
G3 X129.283 Y133.278 I-.646 J7.363 E.6337
G3 X122.305 Y121.299 I-1.277 J-7.278 E.53569
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.229975
G1 F1067
G1 X122.867 Y121.693 E.00044
G3 X128.403 Y119.316 I5.126 J4.304 E.09233
G1 X129.164 Y119.402 E.01131
G1 X129.734 Y119.528 E.00863
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00863
G1 X131.346 Y120.196 E.00858
G1 X131.843 Y120.512 E.0087
G1 X132.307 Y120.868 E.00864
G1 X132.735 Y121.26 E.00858
G1 X133.135 Y121.697 E.00876
G1 X133.488 Y122.157 E.00857
G1 X133.802 Y122.65 E.00864
G1 X134.072 Y123.169 E.00864
G1 X134.296 Y123.708 E.00863
G1 X134.472 Y124.266 E.00864
G1 X134.597 Y124.833 E.00858
G1 X134.674 Y125.416 E.0087
G1 X134.7 Y126 E.00863
G1 X134.675 Y126.58 E.00857
G1 X134.597 Y127.167 E.00876
G1 X134.472 Y127.734 E.00858
G1 X134.296 Y128.292 E.00864
G1 X134.072 Y128.831 E.00863
G1 X133.804 Y129.346 E.00858
G1 X133.486 Y129.846 E.00876
G1 X133.132 Y130.307 E.00857
G1 X132.738 Y130.738 E.00864
G1 X132.307 Y131.132 E.00864
G1 X131.843 Y131.488 E.00864
G1 X131.35 Y131.802 E.00864
G1 X130.835 Y132.07 E.00858
G1 X130.288 Y132.297 E.00876
G1 X129.734 Y132.472 E.00857
G1 X129.163 Y132.598 E.00864
G1 X128.584 Y132.674 E.00864
G1 X128.004 Y132.7 E.00857
G1 X127.412 Y132.674 E.00875
G1 X126.837 Y132.598 E.00858
G1 X126.266 Y132.472 E.00864
G1 X125.708 Y132.296 E.00864
G1 X125.172 Y132.074 E.00857
G1 X124.647 Y131.8 E.00876
G1 X124.157 Y131.488 E.00858
G1 X123.693 Y131.132 E.00864
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.84 E.00876
G1 X122.198 Y129.35 E.00857
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00863
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y125.996 E.00869
G3 X122.511 Y122.157 I6.693 J.001 E.06042
G1 X122.813 Y121.765 E.00731
; CHANGE_LAYER
; Z_HEIGHT: 9.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.867 Y121.693 E-.03422
G1 X123.262 Y121.262 E-.22211
G1 X123.502 Y121.043 E-.12367
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 46/74
; update layer progress
M73 L46
M991 S0 P45 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z9.4 I.452 J1.13 P1  F30000
G1 X126.861 Y119.701 Z9.4
G1 Z9.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G1 X126.882 Y119.696 E.00068
G3 X127.468 Y119.62 I1.118 J6.303 E.01902
G3 X128.561 Y119.622 I.527 J7.94 E.03518
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.343 Y119.816 I-.562 J6.376 E1.22133
G1 X126.803 Y119.714 E.01514
M204 S250
G1 X126.946 Y120.083 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P62 R6
G1 F1073
M204 S5000
G1 X126.954 Y120.082 E.00025
G3 X127.5 Y120.011 I1.046 J5.917 E.01641
G3 X128.525 Y120.013 I.496 J7.497 E.03054
G3 X126.444 Y120.195 I-.525 J5.986 E1.06203
G1 X126.887 Y120.096 E.01352
; WIPE_START
G1 F11933.819
M204 S10000
G1 X126.954 Y120.082 E-.02596
G1 X127.5 Y120.011 E-.20928
G1 X127.881 Y119.994 E-.14476
; WIPE_END
G1 E-.02 F1800
G17
G3 Z9.6 I-.337 J-1.17 P1  F30000
G1 X122.64 Y121.502 Z9.6
G1 Z9.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G3 X127.403 Y119.028 I5.359 J4.494 E.17714
G3 X128.604 Y119.029 I.595 J9.292 E.03864
G3 X122.602 Y121.548 I-.605 J6.968 E1.1954
M204 S250
G1 X122.34 Y121.25 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1073
M204 S5000
G3 X127.365 Y118.637 I5.66 J4.746 E.17315
G3 X128.637 Y118.638 I.634 J9.723 E.0379
G3 X122.301 Y121.297 I-.637 J7.359 E1.16952
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.229985
G1 F1073
M73 P62 R5
G1 X122.867 Y121.693 E.00044
G3 X128.389 Y119.315 I5.126 J4.304 E.09213
G1 X129.171 Y119.404 E.01163
G1 X129.734 Y119.528 E.00853
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00863
G1 X131.346 Y120.196 E.00858
G1 X131.843 Y120.512 E.0087
G1 X132.307 Y120.868 E.00864
G1 X132.735 Y121.26 E.00858
G1 X133.135 Y121.697 E.00876
G1 X133.488 Y122.157 E.00857
G1 X133.802 Y122.65 E.00864
G1 X134.072 Y123.169 E.00864
G1 X134.296 Y123.708 E.00863
G1 X134.472 Y124.266 E.00864
G1 X134.597 Y124.833 E.00858
G1 X134.675 Y125.42 E.00876
G1 X134.7 Y126 E.00857
M73 P63 R5
G1 X134.674 Y126.584 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.473 Y127.73 E.00858
G1 X134.294 Y128.295 E.00876
G1 X134.072 Y128.831 E.00857
G1 X133.802 Y129.35 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.135 Y130.303 E.00857
G1 X132.738 Y130.738 E.0087
G1 X132.307 Y131.132 E.00864
G1 X131.843 Y131.488 E.00864
G1 X131.35 Y131.802 E.00864
G1 X130.835 Y132.07 E.00858
G1 X130.288 Y132.297 E.00876
G1 X129.734 Y132.472 E.00858
G1 X129.163 Y132.598 E.00864
G1 X128.584 Y132.674 E.00864
G1 X128.004 Y132.7 E.00857
G1 X127.412 Y132.674 E.00875
G1 X126.837 Y132.598 E.00858
G1 X126.266 Y132.472 E.00864
G1 X125.708 Y132.296 E.00864
G1 X125.172 Y132.074 E.00858
G1 X124.647 Y131.8 E.00876
G1 X124.157 Y131.488 E.00858
G1 X123.693 Y131.132 E.00864
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.84 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00863
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y125.996 E.0087
G3 X122.511 Y122.157 I6.694 J.001 E.06042
G1 X122.813 Y121.765 E.00731
; CHANGE_LAYER
; Z_HEIGHT: 9.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.867 Y121.693 E-.03414
G1 X123.262 Y121.262 E-.22211
G1 X123.503 Y121.042 E-.12374
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 47/74
; update layer progress
M73 L47
M991 S0 P46 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z9.6 I.448 J1.131 P1  F30000
G1 X126.909 Y119.693 Z9.6
G1 Z9.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1080
G1 X127.47 Y119.619 E.01821
G3 X128.558 Y119.622 I.525 J7.857 E.03499
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.85 Y119.702 I-.558 J6.375 E1.23783
M204 S250
G1 X126.959 Y120.081 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1080
M204 S5000
G1 X127.502 Y120.011 E.01631
G3 X128.522 Y120.013 I.495 J7.406 E.03038
G3 X126.9 Y120.091 I-.522 J5.985 E1.0758
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.502 Y120.011 E-.23083
G1 X127.895 Y119.993 E-.14917
; WIPE_END
G1 E-.02 F1800
G17
G3 Z9.8 I-.336 J-1.17 P1  F30000
G1 X122.642 Y121.504 Z9.8
G1 Z9.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1080
G3 X126.904 Y119.091 I5.36 J4.495 E.1609
G3 X128.484 Y119.02 I1.14 J7.848 E.05095
G3 X122.604 Y121.55 I-.482 J6.979 E1.19957
M204 S250
G1 X122.342 Y121.252 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1080
M204 S5000
G3 X126.85 Y118.702 I5.66 J4.748 E.15763
G3 X128.504 Y118.629 I1.196 J8.287 E.0494
G3 X122.303 Y121.298 I-.502 J7.371 E1.17382
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230025
G1 F1080
M73 P64 R5
G1 X122.872 Y121.697 E.00045
G3 X128.568 Y119.324 I5.141 J4.317 E.09476
G1 X129.168 Y119.403 E.00894
G1 X129.734 Y119.528 E.00857
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00864
G1 X131.346 Y120.196 E.00858
G1 X131.846 Y120.514 E.00876
G1 X132.307 Y120.868 E.00858
G1 X132.738 Y121.262 E.00864
G1 X133.132 Y121.693 E.00864
G1 X133.486 Y122.154 E.00858
G1 X133.804 Y122.654 E.00876
G1 X134.072 Y123.169 E.00858
G1 X134.296 Y123.708 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.597 Y124.833 E.00858
G1 X134.675 Y125.42 E.00876
G1 X134.7 Y126 E.00858
G1 X134.674 Y126.584 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.473 Y127.73 E.00858
G1 X134.294 Y128.295 E.00876
G1 X134.072 Y128.831 E.00858
G1 X133.802 Y129.35 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.135 Y130.303 E.00858
G1 X132.735 Y130.74 E.00876
G1 X132.307 Y131.132 E.00858
G1 X131.843 Y131.488 E.00864
G1 X131.35 Y131.802 E.00864
G1 X130.835 Y132.07 E.00858
G1 X130.288 Y132.297 E.00876
G1 X129.734 Y132.472 E.00858
G1 X129.163 Y132.598 E.00864
G1 X128.584 Y132.674 E.00864
G1 X128.004 Y132.7 E.00858
G1 X127.412 Y132.674 E.00876
G1 X126.837 Y132.598 E.00858
G1 X126.266 Y132.472 E.00864
G1 X125.708 Y132.296 E.00864
G1 X125.172 Y132.074 E.00858
G1 X124.65 Y131.802 E.0087
G1 X124.16 Y131.49 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X122.517 Y122.16 I6.713 J.019 E.0604
G1 X122.813 Y121.765 E.00731
; CHANGE_LAYER
; Z_HEIGHT: 9.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03414
G1 X123.265 Y121.26 E-.22356
G1 X123.503 Y121.042 E-.1223
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 48/74
; update layer progress
M73 L48
M991 S0 P47 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z9.8 I.447 J1.132 P1  F30000
G1 X126.921 Y119.691 Z9.8
G1 Z9.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1080
G1 X127.473 Y119.619 E.0179
G3 X128.557 Y119.622 I.523 J7.749 E.03491
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.861 Y119.7 I-.558 J6.377 E1.23859
M204 S250
G1 X126.971 Y120.079 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1080
M204 S5000
G1 X127.505 Y120.01 E.01602
G3 X128.521 Y120.013 I.492 J7.302 E.03031
G3 X126.912 Y120.089 I-.521 J5.985 E1.07627
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.505 Y120.01 E-.22712
G1 X127.907 Y119.993 E-.15288
; WIPE_END
G1 E-.02 F1800
G17
G3 Z10 I-.336 J-1.17 P1  F30000
G1 X122.643 Y121.505 Z10
G1 Z9.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1080
G3 X126.93 Y119.087 I5.36 J4.494 E.16173
G3 X128.465 Y119.019 I1.116 J7.889 E.04949
G3 X122.605 Y121.551 I-.462 J6.979 E1.20006
M204 S250
G1 X122.343 Y121.253 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1080
M204 S5000
M73 P65 R5
G3 X126.876 Y118.698 I5.661 J4.746 E.1584
G3 X128.485 Y118.628 I1.172 J8.334 E.04803
G3 X122.304 Y121.299 I-.482 J7.371 E1.17423
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230044
G1 F1080
G1 X122.872 Y121.697 E.00045
G3 X128.568 Y119.324 I5.141 J4.317 E.09476
G1 X129.17 Y119.403 E.00898
G1 X129.734 Y119.528 E.00854
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00863
G1 X131.346 Y120.196 E.00858
G1 X131.846 Y120.514 E.00876
G1 X132.307 Y120.868 E.00858
G1 X132.738 Y121.262 E.00864
G1 X133.132 Y121.693 E.00864
G1 X133.486 Y122.154 E.00858
G1 X133.804 Y122.654 E.00876
G1 X134.072 Y123.169 E.00858
G1 X134.296 Y123.708 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.597 Y124.833 E.00858
G1 X134.675 Y125.42 E.00876
G1 X134.7 Y126 E.00858
G1 X134.674 Y126.584 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.473 Y127.73 E.00858
G1 X134.294 Y128.295 E.00876
G1 X134.072 Y128.831 E.00858
G1 X133.802 Y129.35 E.00865
G1 X133.488 Y129.843 E.00864
G1 X133.135 Y130.303 E.00858
G1 X132.735 Y130.74 E.00876
G1 X132.307 Y131.132 E.00858
G1 X131.843 Y131.488 E.00864
G1 X131.35 Y131.802 E.00864
G1 X130.835 Y132.07 E.00858
G1 X130.288 Y132.297 E.00876
G1 X129.734 Y132.472 E.00858
G1 X129.163 Y132.598 E.00864
G1 X128.584 Y132.674 E.00864
G1 X128.004 Y132.7 E.00858
G1 X127.412 Y132.674 E.00876
G1 X126.837 Y132.598 E.00858
G1 X126.266 Y132.472 E.00864
G1 X125.708 Y132.296 E.00864
G1 X125.172 Y132.074 E.00858
G1 X124.647 Y131.8 E.00876
G1 X124.157 Y131.488 E.00858
G1 X123.693 Y131.132 E.00864
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.84 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00865
G1 X121.704 Y128.292 E.00864
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y125.996 E.0087
G3 X122.517 Y122.16 I6.713 J.019 E.0604
G1 X122.813 Y121.765 E.00731
; CHANGE_LAYER
; Z_HEIGHT: 9.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03416
G1 X123.265 Y121.26 E-.22356
G1 X123.503 Y121.042 E-.12227
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 49/74
; update layer progress
M73 L49
M991 S0 P48 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z10 I.446 J1.132 P1  F30000
G1 X126.939 Y119.69 Z10
G1 Z9.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1080
G1 X127.634 Y119.61 E.02251
G3 X128.936 Y119.668 I.31 J7.631 E.04195
G3 X126.879 Y119.698 I-.936 J6.33 E1.22641
M204 S250
G1 X126.983 Y120.078 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1080
M204 S5000
G1 X127.653 Y120.001 E.02008
G3 X128.316 Y120 I.342 J5.202 E.01977
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.924 Y120.088 I-.32 J5.998 E1.0825
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.653 Y120.001 E-.27891
M73 P66 R5
G1 X127.919 Y120.001 E-.10109
; WIPE_END
G1 E-.02 F1800
G17
G3 Z10.2 I-.333 J-1.17 P1  F30000
G1 X122.641 Y121.503 Z10.2
G1 Z9.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1080
G3 X126.941 Y119.085 I5.359 J4.497 E.16211
G3 X128.42 Y119.017 I1.107 J7.944 E.0477
G3 X122.603 Y121.549 I-.42 J6.984 E1.20184
M204 S250
G1 X122.337 Y121.248 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1080
M204 S5000
G3 X126.087 Y118.862 I5.657 J4.751 E.13449
G3 X128.44 Y118.625 I1.982 J7.886 E.07069
G3 X122.299 Y121.294 I-.446 J7.374 E1.17553
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230044
G1 F1080
G1 X122.872 Y121.697 E.00044
G3 X128.974 Y119.373 I5.137 J4.315 E.1008
G1 X129.734 Y119.528 E.01146
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.84 Y120.51 E.00858
G1 X132.307 Y120.868 E.0087
G1 X132.738 Y121.262 E.00864
G1 X133.13 Y121.69 E.00858
G1 X133.49 Y122.16 E.00876
G1 X133.802 Y122.65 E.00858
G1 X134.072 Y123.169 E.00865
G1 X134.296 Y123.708 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.599 Y124.841 E.0087
G1 X134.674 Y125.416 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.599 Y127.159 E.00858
G1 X134.47 Y127.738 E.00876
G1 X134.296 Y128.292 E.00858
G1 X134.072 Y128.831 E.00864
G1 X133.802 Y129.35 E.00865
G1 X133.49 Y129.84 E.00858
G1 X133.13 Y130.31 E.00876
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.84 Y131.49 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00865
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.16 Y131.49 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X122.519 Y122.157 I6.709 J.016 E.06047
G1 X122.813 Y121.765 E.00725
; CHANGE_LAYER
; Z_HEIGHT: 10
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03405
G1 X123.26 Y121.265 E-.22047
G1 X123.503 Y121.042 E-.12548
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 50/74
; update layer progress
M73 L50
M991 S0 P49 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z10.2 I.445 J1.133 P1  F30000
G1 X126.951 Y119.688 Z10.2
G1 Z10
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G1 X127.646 Y119.609 E.02248
G3 X128.925 Y119.666 I.294 J7.732 E.04121
G3 X126.882 Y119.697 I-.925 J6.335 E1.22747
G1 X126.892 Y119.696 E.00031
M204 S250
G1 X126.995 Y120.077 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P67 R5
G1 F1074
M204 S5000
G1 X127.665 Y120 E.02007
G3 X128.302 Y119.999 I.33 J5.22 E.019
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.936 Y120.086 I-.306 J6 E1.08353
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.665 Y120 E-.27878
G1 X127.931 Y120 E-.10122
; WIPE_END
G1 E-.02 F1800
G17
G3 Z10.4 I-.333 J-1.171 P1  F30000
G1 X122.641 Y121.504 Z10.4
G1 Z10
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G3 X126.959 Y119.082 I5.36 J4.497 E.1627
G3 X128.398 Y119.015 I1.094 J8.035 E.04639
G3 X122.603 Y121.55 I-.397 J6.985 E1.2025
M204 S250
G1 X122.337 Y121.248 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1074
M204 S5000
G3 X126.087 Y118.862 I5.657 J4.751 E.13448
G3 X128.418 Y118.624 I1.985 J7.906 E.07003
G3 X122.299 Y121.294 I-.424 J7.375 E1.17622
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230048
G1 F1074
G1 X122.872 Y121.697 E.00044
G3 X128.963 Y119.372 I5.137 J4.315 E.10064
G1 X129.734 Y119.528 E.01163
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.84 Y120.51 E.00858
G1 X132.307 Y120.868 E.0087
G1 X132.738 Y121.262 E.00864
G1 X133.13 Y121.69 E.00858
G1 X133.49 Y122.16 E.00876
G1 X133.802 Y122.65 E.00858
G1 X134.072 Y123.169 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.472 Y124.266 E.00864
M73 P68 R5
G1 X134.598 Y124.837 E.00864
G1 X134.674 Y125.412 E.00858
G1 X134.7 Y126.004 E.00876
G1 X134.674 Y126.584 E.00858
G1 X134.598 Y127.163 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.297 Y128.288 E.00858
G1 X134.07 Y128.835 E.00876
G1 X133.802 Y129.35 E.00858
G1 X133.488 Y129.843 E.00864
G1 X133.132 Y130.307 E.00864
G1 X132.74 Y130.735 E.00858
G1 X132.307 Y131.132 E.0087
G1 X131.84 Y131.49 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00864
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.16 Y131.49 E.00858
G1 X123.693 Y131.132 E.0087
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.84 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00864
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y126 E.00864
G3 X122.519 Y122.157 I6.709 J.013 E.06053
G1 X122.813 Y121.765 E.00725
; CHANGE_LAYER
; Z_HEIGHT: 10.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03405
G1 X123.26 Y121.265 E-.22047
G1 X123.503 Y121.042 E-.12548
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 51/74
; update layer progress
M73 L51
M991 S0 P50 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z10.4 I.444 J1.133 P1  F30000
G1 X126.959 Y119.686 Z10.4
G1 Z10.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G1 X127.52 Y119.616 E.01819
G3 X128.555 Y119.622 I.475 J7.442 E.03332
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.882 Y119.697 I-.554 J6.375 E1.23894
G1 X126.899 Y119.694 E.00057
M204 S250
G1 X127.008 Y120.075 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1074
M204 S5000
G1 X127.545 Y120.007 E.01613
G3 X128.52 Y120.012 I.451 J7.014 E.02907
G3 X126.948 Y120.083 I-.519 J5.985 E1.07728
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.545 Y120.007 E-.22862
G1 X127.943 Y119.991 E-.15138
; WIPE_END
G1 E-.02 F1800
G17
G3 Z10.6 I-.334 J-1.17 P1  F30000
G1 X122.642 Y121.504 Z10.6
G1 Z10.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G3 X126.978 Y119.079 I5.36 J4.496 E.1633
G3 X128.376 Y119.014 I1.082 J8.15 E.04509
G3 X122.604 Y121.55 I-.375 J6.985 E1.20307
M204 S250
G1 X122.342 Y121.252 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1074
M204 S5000
G3 X126.925 Y118.691 I5.66 J4.748 E.15987
G3 X128.396 Y118.622 I1.138 J8.622 E.04393
G3 X122.303 Y121.298 I-.394 J7.377 E1.17706
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230054
G1 F1074
M73 P69 R4
G1 X122.872 Y121.697 E.00045
G3 X128.952 Y119.37 I5.137 J4.315 E.10048
G1 X129.734 Y119.528 E.01179
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.84 Y120.51 E.00858
G1 X132.307 Y120.868 E.0087
G1 X132.738 Y121.262 E.00864
G1 X133.13 Y121.69 E.00858
G1 X133.49 Y122.16 E.00876
G1 X133.802 Y122.65 E.00858
G1 X134.072 Y123.169 E.00865
G1 X134.296 Y123.708 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.599 Y124.841 E.0087
G1 X134.674 Y125.416 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.599 Y127.159 E.00858
G1 X134.47 Y127.738 E.00876
G1 X134.296 Y128.292 E.00858
G1 X134.072 Y128.831 E.00864
G1 X133.802 Y129.35 E.00865
G1 X133.49 Y129.84 E.00858
G1 X133.13 Y130.31 E.00876
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.843 Y131.488 E.00864
G1 X131.353 Y131.8 E.00858
G1 X130.831 Y132.072 E.0087
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.16 Y131.49 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X122.519 Y122.157 I6.709 J.017 E.06047
G1 X122.813 Y121.765 E.00724
; CHANGE_LAYER
; Z_HEIGHT: 10.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03416
G1 X123.26 Y121.265 E-.22047
G1 X123.503 Y121.042 E-.12537
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 52/74
; update layer progress
M73 L52
M991 S0 P51 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z10.6 I.444 J1.133 P1  F30000
G1 X126.971 Y119.685 Z10.6
G1 Z10.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G1 X127.524 Y119.616 E.01791
G1 X127.958 Y119.598 E.01398
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.882 Y119.697 I.045 J6.399 E1.25815
G1 X126.912 Y119.693 E.00098
M204 S250
G1 X127.02 Y120.073 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1073
M204 S5000
G1 X127.549 Y120.007 E.01588
G1 X127.962 Y119.99 E.01231
G3 X126.954 Y120.082 I.04 J6.007 E1.0941
G1 X126.96 Y120.081 E.00019
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.549 Y120.007 E-.22539
G1 X127.955 Y119.99 E-.15461
; WIPE_END
G1 E-.02 F1800
G17
G3 Z10.8 I-.334 J-1.17 P1  F30000
G1 X122.642 Y121.504 Z10.8
G1 Z10.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G3 X126.996 Y119.077 I5.36 J4.494 E.16389
G3 X128.355 Y119.013 I1.071 J8.301 E.04379
G3 X122.604 Y121.551 I-.352 J6.986 E1.20364
M204 S250
G1 X122.342 Y121.252 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1073
M204 S5000
M73 P70 R4
G3 X126.943 Y118.688 I5.66 J4.746 E.16043
G3 X128.374 Y118.621 I1.128 J8.776 E.04271
G3 X122.304 Y121.299 I-.371 J7.378 E1.17756
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230063
G1 F1073
G1 X122.868 Y121.693 E.00044
G3 X129.151 Y119.4 I5.133 J4.307 E.10353
G1 X129.738 Y119.529 E.00888
G1 X130.292 Y119.704 E.00859
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.84 Y120.509 E.00858
G1 X132.31 Y120.87 E.00876
G1 X132.738 Y121.262 E.00858
G1 X133.132 Y121.693 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.8 Y122.647 E.00858
G1 X134.074 Y123.172 E.00876
G1 X134.296 Y123.708 E.00858
G1 X134.472 Y124.266 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.674 Y125.412 E.00858
G1 X134.7 Y126.004 E.00876
G1 X134.674 Y126.584 E.00858
G1 X134.598 Y127.163 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.297 Y128.288 E.00858
G1 X134.07 Y128.835 E.00876
G1 X133.802 Y129.35 E.00858
G1 X133.488 Y129.843 E.00864
G1 X133.132 Y130.307 E.00864
G1 X132.74 Y130.735 E.00858
G1 X132.307 Y131.132 E.0087
G1 X131.84 Y131.49 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00864
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.16 Y131.49 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X122.514 Y122.154 I6.7 J.004 E.0605
G1 X122.813 Y121.765 E.00725
; CHANGE_LAYER
; Z_HEIGHT: 10.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X122.868 Y121.693 E-.03421
G1 X123.26 Y121.265 E-.22055
G1 X123.502 Y121.043 E-.12524
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 53/74
; update layer progress
M73 L53
M991 S0 P52 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z10.8 I.443 J1.133 P1  F30000
G1 X126.957 Y119.692 Z10.8
G1 Z10.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G1 X127.106 Y119.661 E.0049
G3 X127.719 Y119.605 I.894 J6.339 E.0198
G3 X128.277 Y119.605 I.281 J5.618 E.01795
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.343 Y119.817 I-.277 J6.396 E1.23061
G1 X126.898 Y119.704 E.01821
M204 S250
G1 X127.034 Y120.075 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1074
M204 S5000
G1 X127.16 Y120.05 E.00382
G3 X127.738 Y119.996 I.84 J5.95 E.01729
G3 X128.261 Y119.996 I.262 J5.264 E.01558
G3 X126.445 Y120.196 I-.261 J6.003 E1.07
G1 X126.975 Y120.087 E.01614
; WIPE_START
G1 F11933.819
M204 S10000
M73 P71 R4
G1 X127.16 Y120.05 E-.07158
G1 X127.738 Y119.996 E-.22048
G1 X127.969 Y119.996 E-.08794
; WIPE_END
G1 E-.02 F1800
G17
G3 Z11 I-.332 J-1.171 P1  F30000
G1 X122.643 Y121.505 Z11
G1 Z10.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G3 X127.026 Y119.072 I5.361 J4.493 E.16485
G3 X128.333 Y119.011 I1.052 J8.505 E.04211
G3 X122.605 Y121.551 I-.329 J6.987 E1.20435
M204 S250
G1 X122.343 Y121.253 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1074
M204 S5000
G3 X126.974 Y118.684 I5.661 J4.745 E.16134
G3 X128.352 Y118.62 I1.108 J8.993 E.04112
G3 X122.305 Y121.299 I-.347 J7.379 E1.17822
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230058
G1 F1074
G1 X122.872 Y121.697 E.00045
G3 X128.93 Y119.366 I5.138 J4.316 E.10015
G1 X129.734 Y119.528 E.01213
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.84 Y120.509 E.00858
G1 X132.307 Y120.868 E.0087
G1 X132.738 Y121.262 E.00864
G1 X133.13 Y121.69 E.00858
G1 X133.491 Y122.16 E.00876
G1 X133.802 Y122.65 E.00858
G1 X134.072 Y123.169 E.00865
G1 X134.296 Y123.708 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.674 Y125.412 E.00858
G1 X134.7 Y126.004 E.00876
G1 X134.674 Y126.584 E.00858
G1 X134.598 Y127.163 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.297 Y128.288 E.00858
G1 X134.07 Y128.835 E.00876
G1 X133.802 Y129.35 E.00858
G1 X133.488 Y129.843 E.00864
G1 X133.13 Y130.31 E.0087
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.84 Y131.491 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00865
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.647 Y131.8 E.0087
G1 X124.157 Y131.488 E.00858
G1 X123.693 Y131.132 E.00864
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.839 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00865
G1 X121.704 Y128.292 E.00864
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y126 E.00864
G3 X122.519 Y122.157 I6.71 J.013 E.06053
G1 X122.813 Y121.765 E.00725
; CHANGE_LAYER
; Z_HEIGHT: 10.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.872 Y121.697 E-.03419
G1 X123.26 Y121.265 E-.22047
G1 X123.503 Y121.042 E-.12534
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 54/74
; update layer progress
M73 L54
M991 S0 P53 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z11 I.442 J1.134 P1  F30000
G1 X126.97 Y119.689 Z11
G1 Z10.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G1 X127.117 Y119.66 E.00483
G3 X127.737 Y119.604 I.884 J6.338 E.02002
G3 X128.262 Y119.604 I.264 J5.771 E.01689
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.343 Y119.817 I-.261 J6.394 E1.2307
G1 X126.911 Y119.701 E.01863
M204 S250
G1 X127.047 Y120.073 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P72 R4
G1 F1074
M204 S5000
G1 X127.171 Y120.048 E.00376
G3 X127.753 Y119.996 I.83 J5.949 E.01743
G3 X128.246 Y119.996 I.247 J5.425 E.0147
G3 X126.445 Y120.195 I-.246 J6.002 E1.07002
G1 X126.988 Y120.085 E.01652
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.171 Y120.048 E-.07072
G1 X127.753 Y119.996 E-.22225
G1 X127.982 Y119.996 E-.08703
; WIPE_END
G1 E-.02 F1800
G17
G3 Z11.2 I-.33 J-1.171 P1  F30000
G1 X122.64 Y121.502 Z11.2
G1 Z10.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1074
G3 X127.686 Y119.01 I5.36 J4.498 E.18626
G3 X128.311 Y119.01 I.314 J6.298 E.02009
G3 X122.602 Y121.548 I-.311 J6.99 E1.20547
M204 S250
G1 X122.34 Y121.25 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1074
M204 S5000
G3 X127.67 Y118.618 I5.66 J4.75 E.18223
G3 X128.329 Y118.618 I.33 J6.647 E.01965
G3 X122.301 Y121.296 I-.329 J7.382 E1.17931
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230055
G1 F1074
G1 X122.868 Y121.693 E.00044
G3 X129.155 Y119.4 I5.133 J4.307 E.10358
G1 X129.738 Y119.529 E.00883
G1 X130.292 Y119.704 E.00859
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.84 Y120.51 E.00858
M73 P73 R4
G1 X132.31 Y120.87 E.00876
G1 X132.738 Y121.262 E.00858
G1 X133.132 Y121.693 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.8 Y122.647 E.00858
G1 X134.074 Y123.172 E.00876
G1 X134.296 Y123.708 E.00858
G1 X134.472 Y124.266 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.674 Y125.412 E.00858
G1 X134.7 Y126.004 E.00876
G1 X134.674 Y126.584 E.00858
G1 X134.598 Y127.163 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.297 Y128.288 E.00858
G1 X134.07 Y128.835 E.00876
G1 X133.802 Y129.35 E.00858
G1 X133.488 Y129.843 E.00864
G1 X133.13 Y130.31 E.0087
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.84 Y131.49 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00864
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.16 Y131.49 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X122.514 Y122.154 I6.7 J.004 E.0605
G1 X122.813 Y121.765 E.00725
; CHANGE_LAYER
; Z_HEIGHT: 11
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.868 Y121.693 E-.03415
G1 X123.26 Y121.265 E-.22055
G1 X123.503 Y121.043 E-.1253
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 55/74
; update layer progress
M73 L55
M991 S0 P54 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z11.2 I.442 J1.134 P1  F30000
G1 X126.983 Y119.687 Z11.2
G1 Z11
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G1 X127.128 Y119.658 E.00477
G3 X127.751 Y119.603 I.874 J6.34 E.02013
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X131.417 Y120.592 I.248 J6.365 E.12397
G1 X131.672 Y120.755 E.00975
G3 X126.343 Y119.817 I-3.671 J5.242 E1.11333
G1 X126.924 Y119.699 E.01905
M204 S250
G1 X127.06 Y120.071 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1073
M204 S5000
G1 X127.181 Y120.047 E.0037
G3 X127.767 Y119.995 I.826 J5.95 E.01751
G1 X127.957 Y119.99 E.00565
G3 X126.445 Y120.197 I.05 J6.007 E1.07869
G1 X127.001 Y120.083 E.0169
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.181 Y120.047 E-.07001
G1 X127.767 Y119.995 E-.22335
G1 X127.957 Y119.99 E-.07212
G1 X127.995 Y119.992 E-.01452
; WIPE_END
G1 E-.02 F1800
G17
G3 Z11.4 I-.33 J-1.171 P1  F30000
G1 X122.64 Y121.502 Z11.4
G1 Z11
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1073
G3 X123.986 Y120.268 I5.359 J4.494 E.05891
G1 X124.269 Y120.088 E.01075
G3 X128.29 Y119.009 I3.737 J5.888 E.13596
G3 X122.602 Y121.549 I-.291 J6.988 E1.20552
M204 S250
G1 X122.339 Y121.25 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1073
M204 S5000
G3 X123.761 Y119.947 I5.659 J4.746 E.05763
G1 X124.058 Y119.758 E.01047
G3 X128.308 Y118.617 I3.948 J6.219 E.1331
G3 X122.301 Y121.296 I-.309 J7.38 E1.17934
M204 S10000
G1 X122.849 Y121.717 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230062
G1 F1073
M73 P74 R4
G1 X122.873 Y121.698 E.00045
G3 X129.148 Y119.399 I5.14 J4.317 E.10342
G1 X129.737 Y119.529 E.00892
G1 X130.292 Y119.704 E.00859
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.84 Y120.51 E.00858
G1 X132.31 Y120.87 E.00876
G1 X132.738 Y121.262 E.00858
G1 X133.132 Y121.693 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.8 Y122.647 E.00858
G1 X134.074 Y123.172 E.00876
G1 X134.296 Y123.708 E.00858
G1 X134.472 Y124.266 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.633 Y125.103 E.00397
G1 X134.674 Y125.416 E.00467
G1 X134.7 Y126 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.599 Y127.159 E.00858
G1 X134.47 Y127.738 E.00876
G1 X134.296 Y128.292 E.00858
G1 X134.072 Y128.831 E.00864
G1 X133.802 Y129.35 E.00865
G1 X133.49 Y129.84 E.00858
G1 X133.13 Y130.31 E.00876
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.84 Y131.49 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00864
G1 X130.292 Y132.296 E.00864
G1 X129.734 Y132.472 E.00864
G1 X129.163 Y132.598 E.00864
G1 X128.897 Y132.633 E.00397
G1 X128.584 Y132.674 E.00467
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.837 Y132.598 E.00864
G1 X126.262 Y132.47 E.0087
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.16 Y131.49 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X122.519 Y122.157 I6.712 J.019 E.06047
G1 X122.813 Y121.765 E.00725
; CHANGE_LAYER
; Z_HEIGHT: 11.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X122.873 Y121.698 E-.03412
G1 X123.26 Y121.265 E-.22048
G1 X123.503 Y121.042 E-.1254
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 56/74
; update layer progress
M73 L56
M991 S0 P55 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z11.4 I.446 J1.132 P1  F30000
G1 X126.963 Y119.68 Z11.4
G1 Z11.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1030
G2 X129.037 Y119.678 I1.043 J6.315 E1.22626
G1 X129.037 Y119.083 E.01914
G3 X126.189 Y119.241 I-1.044 J6.916 E1.32084
G3 X126.963 Y119.081 I1.614 J5.855 E.02542
G1 X126.963 Y119.62 E.01733
M204 S250
G1 X127.355 Y120.027 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1030
M204 S5000
G2 X128.645 Y120.027 I.645 J5.974 E1.08612
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X128.645 Y118.639 E.04134
G3 X127.355 Y118.638 I-.648 J7.359 E1.3441
M73 P75 R4
G1 X127.355 Y119.967 E.03956
M204 S10000
G1 X126.759 Y119.42 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230015
M73 P75 R3
G1 F1030
G1 X126.266 Y119.528 E.00746
G1 X125.712 Y119.703 E.00858
G1 X125.172 Y119.926 E.00864
G1 X124.65 Y120.198 E.0087
G1 X124.16 Y120.509 E.00858
G1 X123.693 Y120.868 E.0087
G1 X123.262 Y121.262 E.00864
G1 X122.868 Y121.693 E.00864
G1 X122.514 Y122.154 E.00858
G1 X122.198 Y122.65 E.0087
G1 X121.928 Y123.169 E.00864
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.528 Y127.734 E.00864
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00863
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.265 Y130.74 E.0087
G1 X123.693 Y131.132 E.00858
G1 X124.16 Y131.49 E.0087
G1 X124.65 Y131.802 E.00858
G1 X125.165 Y132.07 E.00858
G1 X125.705 Y132.294 E.00864
G1 X126.266 Y132.472 E.0087
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.295 Y132.294 E.0087
G1 X130.835 Y132.07 E.00864
G1 X131.35 Y131.802 E.00858
G1 X131.84 Y131.49 E.00858
G1 X132.307 Y131.132 E.0087
G1 X132.735 Y130.74 E.00858
G1 X133.132 Y130.307 E.0087
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00863
G1 X133.802 Y122.65 E.00864
G1 X133.486 Y122.154 E.0087
G1 X133.132 Y121.693 E.00858
G1 X132.738 Y121.262 E.00864
G1 X132.307 Y120.868 E.00864
G1 X131.84 Y120.509 E.0087
G1 X131.35 Y120.198 E.00858
G1 X130.828 Y119.926 E.0087
G1 X130.288 Y119.703 E.00864
G1 X129.734 Y119.528 E.00858
G1 X129.241 Y119.419 E.00746
; CHANGE_LAYER
; Z_HEIGHT: 11.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X129.734 Y119.528 E-.19192
G1 X130.206 Y119.677 E-.18808
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 57/74
; update layer progress
M73 L57
M991 S0 P56 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z11.6 I-.022 J-1.217 P1  F30000
G1 X126.684 Y119.74 Z11.6
G1 Z11.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1016
G2 X131.201 Y120.455 I1.324 J6.261 E1.14262
G2 X129.316 Y119.74 I-3.129 J5.406 E.06513
G1 X129.316 Y119.131 E.01957
G3 X126.684 Y119.131 I-1.316 J6.867 E1.32761
G1 X126.684 Y119.68 E.01764
M204 S250
G1 X127.076 Y120.063 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P76 R3
G1 F1016
M204 S5000
G2 X128.924 Y120.063 I.924 J5.935 E1.06887
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X128.924 Y118.67 E.04151
G3 X127.076 Y118.67 I-.924 J7.328 E1.32708
G1 X127.076 Y120.003 E.03973
M204 S10000
G1 X126.481 Y119.481 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230009
G1 F1016
G1 X126.266 Y119.528 E.00325
G1 X125.708 Y119.704 E.00864
G1 X125.169 Y119.928 E.00864
G1 X124.65 Y120.198 E.00864
G1 X124.157 Y120.512 E.00864
G1 X123.693 Y120.868 E.00864
G1 X123.262 Y121.262 E.00864
G1 X122.868 Y121.693 E.00864
G1 X122.512 Y122.157 E.00864
G1 X122.198 Y122.65 E.00864
G1 X121.928 Y123.169 E.00864
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.528 Y127.734 E.00864
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00864
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.265 Y130.74 E.0087
G1 X123.693 Y131.132 E.00858
G1 X124.161 Y131.491 E.0087
G1 X124.65 Y131.802 E.00858
G1 X125.165 Y132.07 E.00858
G1 X125.705 Y132.294 E.00864
G1 X126.266 Y132.472 E.0087
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.295 Y132.294 E.0087
G1 X130.831 Y132.072 E.00857
G1 X131.35 Y131.802 E.00864
G1 X131.639 Y131.618 E.00507
G1 X131.843 Y131.488 E.00357
G1 X132.307 Y131.132 E.00864
G1 X132.735 Y130.74 E.00858
G1 X133.132 Y130.307 E.0087
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00864
G1 X133.802 Y122.65 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.132 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.307 Y120.868 E.00864
G1 X131.843 Y120.512 E.00864
G1 X131.35 Y120.198 E.00864
G1 X130.831 Y119.928 E.00864
G1 X130.292 Y119.704 E.00863
G1 X129.734 Y119.528 E.00864
G1 X129.519 Y119.481 E.00325
; CHANGE_LAYER
; Z_HEIGHT: 11.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X129.734 Y119.528 E-.08361
G1 X130.292 Y119.704 E-.22216
G1 X130.472 Y119.779 E-.07423
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 58/74
; update layer progress
M73 L58
M991 S0 P57 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z11.8 I.002 J-1.217 P1  F30000
G1 X126.532 Y119.774 Z11.8
G1 Z11.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1007
G2 X130.706 Y120.197 I1.477 J6.227 E1.15552
G2 X129.468 Y119.774 I-2.867 J6.359 E.04213
G1 X129.468 Y119.165 E.01957
M73 P77 R3
G1 X129.811 Y119.241 E.01129
G3 X126.189 Y119.241 I-1.811 J6.756 E1.2953
G1 X126.532 Y119.165 E.0113
G1 X126.532 Y119.714 E.01764
M204 S250
G1 X126.924 Y120.088 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1007
M204 S5000
G2 X129.076 Y120.088 I1.076 J5.909 E1.05972
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X129.076 Y118.69 E.04164
G1 X129.281 Y118.722 E.00618
G3 X126.924 Y118.69 I-1.276 J7.276 E1.31202
G1 X126.924 Y120.028 E.03985
M204 S10000
G1 X126.235 Y119.538 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230011
G1 F1007
G1 X125.708 Y119.704 E.00816
G1 X125.172 Y119.926 E.00858
G1 X124.654 Y120.196 E.00864
G1 X124.157 Y120.512 E.0087
G1 X123.697 Y120.865 E.00858
G1 X123.262 Y121.262 E.0087
G1 X122.868 Y121.693 E.00864
M73 P78 R3
G1 X122.512 Y122.157 E.00864
G1 X122.2 Y122.647 E.00858
G1 X121.928 Y123.169 E.0087
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.401 Y127.159 E.00858
G1 X121.528 Y127.734 E.0087
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00864
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.262 Y130.738 E.00864
G1 X123.693 Y131.132 E.00864
G1 X124.157 Y131.488 E.00864
G1 X124.65 Y131.802 E.00864
G1 X125.169 Y132.072 E.00864
G1 X125.708 Y132.296 E.00863
G1 X126.266 Y132.472 E.00864
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.292 Y132.296 E.00864
G1 X130.831 Y132.072 E.00864
G1 X131.35 Y131.802 E.00864
G1 X131.843 Y131.488 E.00864
G1 X132.307 Y131.132 E.00864
G1 X132.738 Y130.738 E.00864
G1 X133.132 Y130.307 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.599 Y127.159 E.0087
G1 X134.674 Y126.584 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00863
G1 X133.8 Y122.647 E.0087
G1 X133.488 Y122.157 E.00858
G1 X133.132 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.303 Y120.865 E.0087
G1 X131.843 Y120.512 E.00858
G1 X131.346 Y120.196 E.0087
G1 X130.828 Y119.926 E.00864
G1 X130.292 Y119.704 E.00858
G1 X129.765 Y119.538 E.00816
; CHANGE_LAYER
; Z_HEIGHT: 11.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X130.292 Y119.704 E-.20976
G1 X130.706 Y119.876 E-.17024
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 59/74
; update layer progress
M73 L59
M991 S0 P58 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z12 I.023 J-1.217 P1  F30000
G1 X126.444 Y119.793 Z12
G1 Z11.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1004
G2 X129.556 Y119.793 I1.556 J6.206 E1.19156
G1 X129.556 Y119.185 E.01958
G3 X123.986 Y120.268 I-1.564 J6.817 E1.22522
G3 X126.444 Y119.185 I4.065 J5.892 E.08688
G1 X126.444 Y119.733 E.01765
M204 S250
G1 X126.836 Y120.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1004
M204 S5000
G2 X131.005 Y120.795 I1.172 J5.891 E.99564
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G2 X129.164 Y120.11 I-2.937 J5.075 E.05879
G1 X129.164 Y118.704 E.04186
G1 X129.281 Y118.722 E.00354
G3 X126.836 Y118.704 I-1.275 J7.276 E1.30935
G1 X126.836 Y120.05 E.04007
M204 S10000
G1 X126.24 Y119.536 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230011
M73 P79 R3
G1 F1004
G1 X125.708 Y119.704 E.00824
G1 X125.172 Y119.926 E.00858
G1 X124.654 Y120.196 E.00864
G1 X124.157 Y120.512 E.0087
G1 X123.697 Y120.865 E.00858
G1 X123.262 Y121.262 E.0087
G1 X122.868 Y121.693 E.00864
G1 X122.512 Y122.157 E.00864
G1 X122.2 Y122.647 E.00858
G1 X121.928 Y123.169 E.0087
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.401 Y127.159 E.00858
G1 X121.528 Y127.734 E.0087
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00864
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.262 Y130.738 E.00864
G1 X123.693 Y131.132 E.00864
G1 X124.157 Y131.488 E.00864
G1 X124.65 Y131.802 E.00864
G1 X125.169 Y132.072 E.00864
G1 X125.708 Y132.296 E.00863
G1 X126.266 Y132.472 E.00864
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.292 Y132.296 E.00864
G1 X130.831 Y132.072 E.00864
G1 X131.35 Y131.802 E.00864
G1 X131.843 Y131.488 E.00864
G1 X132.307 Y131.132 E.00864
G1 X132.738 Y130.738 E.00864
G1 X133.132 Y130.307 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.599 Y127.159 E.0087
G1 X134.674 Y126.584 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00864
G1 X133.8 Y122.647 E.0087
G1 X133.488 Y122.157 E.00858
G1 X133.132 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.303 Y120.865 E.0087
G1 X131.843 Y120.512 E.00858
G1 X131.346 Y120.196 E.0087
G1 X130.828 Y119.926 E.00864
G1 X130.292 Y119.704 E.00858
G1 X129.76 Y119.536 E.00825
; CHANGE_LAYER
; Z_HEIGHT: 12
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X130.292 Y119.704 E-.21201
G1 X130.7 Y119.873 E-.16799
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 60/74
; update layer progress
M73 L60
M991 S0 P59 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z12.2 I.022 J-1.217 P1  F30000
G1 X126.403 Y119.797 Z12.2
G1 Z12
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1002
G2 X129.597 Y119.797 I1.597 J6.199 E1.18951
G1 X129.598 Y119.194 E.01938
G3 X124.501 Y119.94 I-1.606 J6.807 E1.2435
G3 X126.403 Y119.194 I3.407 J5.884 E.06595
G1 X126.403 Y119.737 E.01746
M204 S250
G1 X126.795 Y120.117 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1002
M204 S5000
G2 X130.54 Y120.553 I1.213 J5.884 E1.01007
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G2 X129.205 Y120.117 I-2.654 J5.868 E.04191
G1 X129.207 Y118.711 E.0419
M73 P80 R3
G3 X126.795 Y118.71 I-1.207 J7.29 E1.31077
G1 X126.795 Y120.057 E.04012
M204 S10000
G1 X126.2 Y119.549 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.23001
G1 F1002
G1 X125.708 Y119.704 E.00761
G1 X125.172 Y119.926 E.00858
G1 X124.654 Y120.196 E.00864
G1 X124.157 Y120.512 E.0087
G1 X123.697 Y120.865 E.00858
G1 X123.262 Y121.262 E.0087
G1 X122.868 Y121.693 E.00864
G1 X122.512 Y122.157 E.00864
G1 X122.2 Y122.647 E.00858
G1 X121.928 Y123.169 E.0087
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.401 Y127.159 E.00858
G1 X121.528 Y127.734 E.0087
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00864
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.262 Y130.738 E.00864
G1 X123.693 Y131.132 E.00864
G1 X124.157 Y131.488 E.00864
G1 X124.65 Y131.802 E.00864
G1 X125.169 Y132.072 E.00864
G1 X125.708 Y132.296 E.00863
G1 X126.266 Y132.472 E.00864
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.292 Y132.296 E.00864
G1 X130.831 Y132.072 E.00864
G1 X131.35 Y131.802 E.00864
G1 X131.843 Y131.488 E.00864
G1 X132.307 Y131.132 E.00864
G1 X132.738 Y130.738 E.00864
G1 X133.132 Y130.307 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.599 Y127.159 E.0087
G1 X134.674 Y126.584 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00864
G1 X133.8 Y122.647 E.0087
G1 X133.488 Y122.157 E.00858
G1 X133.132 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.303 Y120.865 E.0087
G1 X131.843 Y120.512 E.00858
G1 X131.346 Y120.196 E.0087
G1 X130.828 Y119.926 E.00864
G1 X130.292 Y119.704 E.00858
G1 X129.801 Y119.549 E.0076
; CHANGE_LAYER
; Z_HEIGHT: 12.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X130.292 Y119.704 E-.19536
G1 X130.741 Y119.89 E-.18464
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 61/74
; update layer progress
M73 L61
M991 S0 P60 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z12.4 I.026 J-1.217 P1  F30000
G1 X126.403 Y119.797 Z12.4
G1 Z12.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1002
G2 X129.597 Y119.797 I1.597 J6.199 E1.1896
G1 X129.597 Y119.194 E.01939
G1 X129.811 Y119.241 E.00706
G3 X130.393 Y132.575 I-1.82 J6.759 E.56911
G3 X126.403 Y119.194 I-2.392 J-6.572 E.73325
G1 X126.403 Y119.737 E.01746
M204 S250
M73 P81 R3
G1 X126.795 Y120.117 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1002
M204 S5000
G2 X130.54 Y120.553 I1.213 J5.884 E1.01007
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G2 X129.205 Y120.117 I-2.653 J5.868 E.04192
G1 X129.205 Y118.71 E.04191
G1 X129.281 Y118.722 E.00229
G3 X126.795 Y118.71 I-1.277 J7.276 E1.30816
G1 X126.795 Y120.057 E.04012
M204 S10000
G1 X126.2 Y119.549 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230011
M73 P81 R2
G1 F1002
G1 X125.708 Y119.704 E.00761
G1 X125.172 Y119.926 E.00857
G1 X124.654 Y120.196 E.00864
G1 X124.157 Y120.512 E.0087
G1 X123.697 Y120.865 E.00858
G1 X123.262 Y121.262 E.0087
G1 X122.868 Y121.693 E.00864
G1 X122.512 Y122.157 E.00864
G1 X122.2 Y122.647 E.00858
G1 X121.928 Y123.169 E.0087
G1 X121.704 Y123.708 E.00864
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.401 Y127.159 E.00858
G1 X121.528 Y127.734 E.0087
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00863
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.262 Y130.738 E.00864
G1 X123.693 Y131.132 E.00864
G1 X124.157 Y131.488 E.00864
G1 X124.65 Y131.802 E.00864
G1 X125.169 Y132.072 E.00864
G1 X125.708 Y132.296 E.00864
G1 X126.266 Y132.472 E.00864
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.292 Y132.296 E.00864
G1 X130.831 Y132.072 E.00863
G1 X131.35 Y131.802 E.00864
G1 X131.843 Y131.488 E.00864
G1 X132.307 Y131.132 E.00864
G1 X132.738 Y130.738 E.00864
G1 X133.132 Y130.307 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.599 Y127.159 E.0087
G1 X134.674 Y126.584 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00863
G1 X133.8 Y122.647 E.0087
G1 X133.488 Y122.157 E.00858
G1 X133.132 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.303 Y120.865 E.0087
G1 X131.843 Y120.512 E.00858
G1 X131.346 Y120.196 E.0087
G1 X130.828 Y119.926 E.00864
G1 X130.292 Y119.704 E.00858
G1 X129.8 Y119.549 E.00761
; CHANGE_LAYER
; Z_HEIGHT: 12.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X130.292 Y119.704 E-.19571
G1 X130.74 Y119.89 E-.18429
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 62/74
; update layer progress
M73 L62
M991 S0 P61 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z12.6 I.027 J-1.217 P1  F30000
G1 X126.444 Y119.793 Z12.6
G1 Z12.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
M73 P82 R2
G1 F1004
G2 X129.556 Y119.793 I1.556 J6.206 E1.19161
G1 X129.556 Y119.185 E.01958
G1 X129.811 Y119.241 E.0084
G3 X126.189 Y119.241 I-1.811 J6.756 E1.29539
G1 X126.444 Y119.185 E.0084
G1 X126.444 Y119.733 E.01765
M204 S250
G1 X126.836 Y120.11 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1004
M204 S5000
G2 X131.005 Y120.795 I1.172 J5.892 E.9957
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G2 X129.164 Y120.11 I-2.937 J5.075 E.05879
G1 X129.164 Y118.704 E.04186
G1 X129.281 Y118.722 E.00354
G3 X126.836 Y118.704 I-1.276 J7.275 E1.30915
G1 X126.836 Y120.05 E.04007
M204 S10000
G1 X126.24 Y119.536 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230011
G1 F1004
M73 P83 R2
G1 X125.708 Y119.704 E.00825
G1 X125.172 Y119.926 E.00858
G1 X124.654 Y120.196 E.00864
G1 X124.157 Y120.512 E.0087
G1 X123.697 Y120.865 E.00858
G1 X123.262 Y121.262 E.0087
G1 X122.868 Y121.693 E.00864
G1 X122.512 Y122.157 E.00864
G1 X122.2 Y122.647 E.00858
G1 X121.928 Y123.169 E.0087
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.401 Y127.159 E.00858
G1 X121.528 Y127.734 E.0087
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00863
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.262 Y130.738 E.00864
G1 X123.693 Y131.132 E.00864
G1 X124.157 Y131.488 E.00864
G1 X124.65 Y131.802 E.00864
G1 X125.169 Y132.072 E.00864
G1 X125.708 Y132.296 E.00863
G1 X126.266 Y132.472 E.00864
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.292 Y132.296 E.00864
G1 X130.831 Y132.072 E.00863
G1 X131.35 Y131.802 E.00864
G1 X131.843 Y131.488 E.00864
G1 X132.307 Y131.132 E.00864
G1 X132.738 Y130.738 E.00864
G1 X133.132 Y130.307 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.599 Y127.159 E.0087
G1 X134.674 Y126.584 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00864
G1 X133.8 Y122.647 E.0087
G1 X133.488 Y122.157 E.00858
G1 X133.132 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.303 Y120.865 E.0087
G1 X131.843 Y120.512 E.00858
G1 X131.346 Y120.196 E.0087
G1 X130.828 Y119.926 E.00864
G1 X130.292 Y119.704 E.00858
G1 X129.76 Y119.536 E.00825
; CHANGE_LAYER
; Z_HEIGHT: 12.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X130.292 Y119.704 E-.21201
G1 X130.7 Y119.873 E-.16799
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 63/74
; update layer progress
M73 L63
M991 S0 P62 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z12.8 I.029 J-1.217 P1  F30000
G1 X126.532 Y119.774 Z12.8
G1 Z12.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1013
G2 X130.706 Y120.197 I1.476 J6.227 E1.15559
G2 X129.468 Y119.774 I-2.868 J6.361 E.04213
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X129.468 Y119.165 E.01957
G1 X129.811 Y119.241 E.01129
G3 X126.189 Y119.241 I-1.811 J6.759 E1.29594
G1 X126.532 Y119.165 E.0113
G1 X126.532 Y119.714 E.01764
M204 S250
G1 X126.924 Y120.088 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1013
M204 S5000
G1 X126.877 Y120.099 E.00143
M106 S127.5
G2 X129.123 Y120.099 I1.123 J5.9 E1.05673
G1 X129.076 Y120.088 E.00143
G1 X129.076 Y118.692 E.04159
M106 S99.45
G1 X129.123 Y118.699 E.00141
G1 X129.282 Y118.722 E.00478
M106 S127.5
G3 X126.718 Y118.722 I-1.282 J7.275 E1.30577
G1 X126.877 Y118.699 E.00478
G1 X126.924 Y118.692 E.00141
M73 P84 R2
G1 X126.924 Y120.028 E.0398
M106 S99.45
M204 S10000
G1 X126.235 Y119.538 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230009
G1 F1013
G1 X125.708 Y119.704 E.00816
G1 X125.172 Y119.926 E.00858
G1 X124.654 Y120.196 E.00864
G1 X124.157 Y120.512 E.0087
G1 X123.697 Y120.865 E.00858
G1 X123.262 Y121.262 E.0087
G1 X122.868 Y121.693 E.00864
G1 X122.512 Y122.157 E.00864
G1 X122.2 Y122.647 E.00858
G1 X121.928 Y123.169 E.0087
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.401 Y127.159 E.00858
G1 X121.528 Y127.734 E.0087
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00863
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.262 Y130.738 E.00864
G1 X123.693 Y131.132 E.00864
G1 X124.157 Y131.488 E.00864
G1 X124.65 Y131.802 E.00864
G1 X125.169 Y132.072 E.00864
G1 X125.708 Y132.296 E.00863
G1 X126.266 Y132.472 E.00864
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.292 Y132.296 E.00864
G1 X130.831 Y132.072 E.00863
G1 X131.35 Y131.802 E.00864
G1 X131.843 Y131.488 E.00864
G1 X132.307 Y131.132 E.00864
G1 X132.738 Y130.738 E.00864
G1 X133.132 Y130.307 E.00864
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.599 Y127.159 E.0087
G1 X134.674 Y126.584 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00863
G1 X133.8 Y122.647 E.0087
G1 X133.488 Y122.157 E.00858
G1 X133.132 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.303 Y120.865 E.0087
G1 X131.843 Y120.512 E.00858
G1 X131.346 Y120.196 E.0087
G1 X130.828 Y119.926 E.00864
G1 X130.292 Y119.704 E.00858
G1 X129.765 Y119.538 E.00816
; CHANGE_LAYER
; Z_HEIGHT: 12.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X130.292 Y119.704 E-.20976
G1 X130.706 Y119.876 E-.17024
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 64/74
; update layer progress
M73 L64
M991 S0 P63 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z13 I.041 J-1.216 P1  F30000
G1 X126.684 Y119.74 Z13
G1 Z12.8
G1 E.4 F1800
M106 S127.5
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1022
G2 X131.201 Y120.455 I1.324 J6.261 E1.14262
G2 X129.316 Y119.74 I-3.13 J5.407 E.06513
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X129.316 Y119.131 E.01957
G1 X129.811 Y119.241 E.01632
G3 X126.684 Y119.131 I-1.803 J6.758 E1.31165
G1 X126.684 Y119.68 E.01764
M204 S250
G1 X127.076 Y120.063 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1022
M204 S5000
G1 X126.965 Y120.08 E.00336
M106 S99.45
M73 P85 R2
G1 X126.445 Y120.195 E.01588
M106 S127.5
G2 X129.555 Y120.195 I1.555 J5.802 E1.03054
G1 X129.035 Y120.08 E.01588
G1 X128.924 Y120.063 E.00336
M106 S99.45
M106 S127.5
G1 X128.924 Y118.67 E.0415
M106 S99.45
M106 S127.5
G1 X129.017 Y118.682 E.00281
M106 S99.45
G1 X129.035 Y118.684 E.00054
G1 X129.427 Y118.764 E.01191
G1 X129.912 Y118.863 E.01476
M106 S127.5
G3 X126.088 Y118.864 I-1.911 J7.135 E1.26719
G1 X126.328 Y118.809 E.00734
G1 X126.719 Y118.722 E.01191
G1 X126.965 Y118.685 E.00742
G1 X127.011 Y118.678 E.00138
G1 X127.076 Y118.67 E.00197
M106 S99.45
M106 S127.5
G1 X127.076 Y120.003 E.03971
M106 S99.45
M204 S10000
G1 X126.481 Y119.481 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230009
G1 F1022
G1 X126.266 Y119.528 E.00325
G1 X125.708 Y119.704 E.00864
G1 X125.169 Y119.928 E.00863
G1 X124.65 Y120.198 E.00864
G1 X124.157 Y120.512 E.00864
G1 X123.693 Y120.867 E.00864
G1 X123.262 Y121.262 E.00864
G1 X122.868 Y121.693 E.00864
G1 X122.512 Y122.157 E.00864
G1 X122.198 Y122.65 E.00864
G1 X121.928 Y123.169 E.00864
G1 X121.704 Y123.708 E.00863
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.528 Y127.734 E.00864
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00863
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.867 Y130.307 E.00864
G1 X123.265 Y130.74 E.0087
G1 X123.693 Y131.132 E.00858
G1 X124.16 Y131.49 E.0087
G1 X124.65 Y131.802 E.00858
G1 X125.165 Y132.07 E.00858
G1 X125.705 Y132.294 E.00864
G1 X126.266 Y132.472 E.0087
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.295 Y132.294 E.0087
G1 X130.831 Y132.072 E.00857
G1 X131.346 Y131.804 E.00858
G1 X131.84 Y131.49 E.00864
G1 X132.307 Y131.133 E.0087
G1 X132.735 Y130.74 E.00858
G1 X133.132 Y130.307 E.0087
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00863
G1 X134.472 Y127.734 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00863
G1 X133.802 Y122.65 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.133 Y121.693 E.00864
G1 X132.738 Y121.262 E.00864
G1 X132.307 Y120.868 E.00864
G1 X131.843 Y120.512 E.00864
G1 X131.35 Y120.198 E.00864
G1 X130.831 Y119.928 E.00864
G1 X130.292 Y119.704 E.00863
G1 X129.734 Y119.528 E.00864
G1 X129.519 Y119.481 E.00325
; CHANGE_LAYER
; Z_HEIGHT: 13
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X129.734 Y119.528 E-.08364
G1 X130.292 Y119.704 E-.22211
G1 X130.472 Y119.779 E-.07424
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 65/74
; update layer progress
M73 L65
M991 S0 P64 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z13.2 I.035 J-1.216 P1  F30000
G1 X126.963 Y119.679 Z13.2
G1 Z13
G1 E.4 F1800
M106 S127.5
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1036
G2 X121.679 Y126.992 I1.048 J6.322 E.32184
G2 X129.037 Y119.678 I6.323 J-.997 E.9043
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X129.037 Y119.081 E.0192
G1 X129.209 Y119.108 E.00557
G3 X126.189 Y119.241 I-1.208 J6.89 E1.31538
G1 X126.696 Y119.129 E.01671
G3 X126.963 Y119.082 I.479 J1.937 E.0087
M73 P86 R2
G1 X126.963 Y119.619 E.01729
M204 S250
G1 X127.23 Y120.04 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1036
M204 S5000
G1 X127.117 Y120.057 E.0034
M106 S99.45
G1 X126.725 Y120.137 E.01191
M106 S127.5
G1 X126.445 Y120.196 E.00854
G2 X129.555 Y120.197 I1.554 J5.8 E1.03
G1 X129.275 Y120.137 E.00854
G1 X128.883 Y120.057 E.01191
G1 X128.77 Y120.04 E.00339
M106 S99.45
M106 S127.5
G1 X128.645 Y120.027 E.00373
M106 S99.45
M106 S127.5
G1 X128.645 Y118.638 E.04137
M106 S99.45
M106 S127.5
G1 X128.875 Y118.664 E.00688
M106 S99.45
G1 X128.883 Y118.665 E.00023
G1 X129.281 Y118.722 E.01198
G1 X129.671 Y118.809 E.01191
M106 S127.5
G1 X129.912 Y118.864 E.00736
G3 X126.088 Y118.865 I-1.91 J7.134 E1.26692
G1 X126.328 Y118.809 E.00734
G1 X126.719 Y118.722 E.01191
G1 X127.117 Y118.666 E.01199
G1 X127.318 Y118.642 E.00601
M106 S99.45
M106 S127.5
G1 X127.355 Y118.639 E.0011
M106 S99.45
M106 S127.5
G1 X127.355 Y120.027 E.04136
M106 S99.45
M106 S127.5
G1 X127.29 Y120.034 E.00194
M106 S99.45
M204 S10000
G1 X126.759 Y119.419 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230013
G1 F1036
G1 X126.266 Y119.528 E.00746
G1 X125.712 Y119.703 E.00858
G1 X125.172 Y119.926 E.00864
G1 X124.65 Y120.198 E.0087
G1 X124.16 Y120.51 E.00858
G1 X123.693 Y120.868 E.0087
G1 X123.262 Y121.262 E.00864
G1 X122.868 Y121.693 E.00864
G1 X122.514 Y122.154 E.00858
G1 X122.198 Y122.65 E.0087
G1 X121.928 Y123.169 E.00864
G1 X121.704 Y123.708 E.00864
G1 X121.528 Y124.266 E.00864
G1 X121.402 Y124.837 E.00864
G1 X121.326 Y125.416 E.00864
G1 X121.3 Y126 E.00864
G1 X121.326 Y126.584 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.528 Y127.734 E.00864
G1 X121.704 Y128.292 E.00864
G1 X121.928 Y128.831 E.00864
G1 X122.198 Y129.35 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.868 Y130.307 E.00864
G1 X123.265 Y130.74 E.0087
G1 X123.693 Y131.132 E.00858
G1 X124.16 Y131.49 E.0087
G1 X124.654 Y131.804 E.00864
G1 X125.169 Y132.072 E.00858
G1 X125.705 Y132.294 E.00858
G1 X126.266 Y132.472 E.0087
G1 X126.837 Y132.598 E.00864
G1 X127.416 Y132.674 E.00864
G1 X128 Y132.7 E.00864
G1 X128.584 Y132.674 E.00864
G1 X129.163 Y132.598 E.00864
G1 X129.734 Y132.472 E.00864
G1 X130.295 Y132.294 E.0087
G1 X130.835 Y132.07 E.00864
G1 X131.35 Y131.802 E.00858
G1 X131.73 Y131.56 E.00666
G1 X132.307 Y131.132 E.01061
G1 X132.735 Y130.74 E.00858
G1 X133.132 Y130.307 E.0087
G1 X133.488 Y129.843 E.00864
G1 X133.802 Y129.35 E.00864
G1 X134.072 Y128.831 E.00864
G1 X134.296 Y128.292 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.7 Y126 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.296 Y123.708 E.00864
G1 X134.072 Y123.169 E.00864
G1 X133.802 Y122.65 E.00864
G1 X133.486 Y122.154 E.0087
G1 X133.132 Y121.693 E.00858
G1 X132.738 Y121.262 E.00864
G1 X132.307 Y120.868 E.00864
G1 X131.84 Y120.509 E.0087
G1 X131.35 Y120.198 E.00858
G1 X130.828 Y119.926 E.0087
G1 X130.288 Y119.703 E.00864
G1 X129.734 Y119.528 E.00858
G1 X129.241 Y119.419 E.00747
M106 S127.5
; CHANGE_LAYER
; Z_HEIGHT: 13.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X129.734 Y119.528 E-.19197
G1 X130.206 Y119.677 E-.18803
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 66/74
; update layer progress
M73 L66
M991 S0 P65 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z13.4 I.006 J-1.217 P1  F30000
G1 X127.139 Y119.662 Z13.4
G1 Z13.2
M73 P87 R2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1079
G1 X127.382 Y119.63 E.0079
G1 X127.478 Y119.619 E.0031
M106 S99.45
M106 S127.5
G1 X127.688 Y119.606 E.00677
M106 S99.45
M106 S127.5
G1 F600
G1 X127.765 Y119.604 E.00246
M106 S99.45
M106 S127.5
; FEATURE: Overhang wall

M204 S5000
G3 X128.235 Y119.603 I.238 J4.743 E.01515
M106 S99.45
M106 S127.5
; FEATURE: Inner wall
M204 S10000
G1 X128.268 Y119.604 E.00104
M106 S99.45
M106 S127.5
G1 F1079
G1 X128.554 Y119.622 E.00923
M106 S99.45
G1 X128.618 Y119.629 E.00206
G1 X129.111 Y119.695 E.01599
G1 X129.657 Y119.815 E.01799
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

M106 S127.5
G3 X126.882 Y119.699 I-1.649 J6.184 E1.2031
G1 X127.079 Y119.671 E.0064
M204 S250
G1 X127.19 Y120.051 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1079
M204 S5000
G1 X127.396 Y120.023 E.00619
G1 X127.513 Y120.01 E.00351
M106 S99.45
M106 S127.5
G1 X127.706 Y119.998 E.00578
M106 S99.45
M106 S127.5
G1 F600
G1 X127.765 Y119.996 E.00173
M106 S99.45
M106 S127.5
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45

G3 X128.235 Y119.996 I.239 J4.743 E.01515
M106 S99.45
M106 S127.5
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 X128.252 Y119.996 E.00049
M106 S99.45
M106 S127.5
G1 F1079
G1 X128.519 Y120.012 E.00799
M106 S99.45
M106 S127.5
G1 X128.604 Y120.022 E.00255
M106 S99.45
G1 X129.04 Y120.08 E.01308
G1 X129.556 Y120.195 E.01574
M106 S127.5
G3 X126.955 Y120.085 I-1.547 J5.805 E1.0462
G1 X127.13 Y120.059 E.00529
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.396 Y120.023 E-.10172
G1 X127.513 Y120.01 E-.04482
G1 X127.706 Y119.998 E-.07377
G1 X127.765 Y119.996 E-.02209
G1 X128.127 Y119.996 E-.1376
; WIPE_END
G1 E-.02 F1800
G17
G3 Z13.6 I1.17 J.335 P1  F30000
G1 X128.408 Y119.015 Z13.6
G1 Z13.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1079
G1 X128.536 Y119.023 E.00415
M106 S99.45
M106 S127.5
G1 X128.618 Y119.032 E.00264
M106 S99.45
G1 X129.209 Y119.111 E.01918
M106 S127.5
G3 X126.189 Y119.241 I-1.216 J6.887 E1.31504
G3 X126.79 Y119.11 I1.888 J7.209 E.0198
G1 X127.382 Y119.03 E.0192
M73 P87 R1
G1 X127.408 Y119.027 E.00084
G1 X127.692 Y119.01 E.00916
M106 S99.45
M106 S127.5
G1 F600
G1 X127.765 Y119.008 E.00233
M106 S99.45
M106 S127.5
; FEATURE: Overhang wall

M204 S5000
G3 X128.235 Y119.008 I.24 J4.905 E.01515
M106 S99.45
M106 S127.5
; FEATURE: Inner wall
M204 S10000
G1 X128.307 Y119.01 E.00231
M106 S99.45
M106 S127.5
G1 F803.577
G1 X128.348 Y119.012 E.00131
M106 S99.45
M106 S127.5
M204 S250
G1 X128.43 Y118.624 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1079
M204 S5000
G1 X128.57 Y118.632 E.00416
M106 S99.45
G1 X128.604 Y118.636 E.00104
G1 X129.001 Y118.686 E.01191
G1 X129.281 Y118.724 E.00841
M106 S127.5
G3 X126.719 Y118.722 I-1.286 J7.273 E1.30557
G1 X126.999 Y118.686 E.00842
G1 X127.396 Y118.635 E.01191
G1 X127.676 Y118.618 E.00837
M106 S99.45
M106 S127.5
G1 F600
G1 X127.765 Y118.616 E.00264
M106 S99.45
M106 S127.5
; FEATURE: Overhang wall
; LINE_WIDTH: 0.45

M73 P88 R1
G3 X128.235 Y118.615 I.241 J4.903 E.01515
M106 S99.45
M106 S127.5
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 X128.324 Y118.618 E.00264
M106 S99.45
M106 S127.5
G1 F836.118
G1 X128.37 Y118.621 E.00139
M106 S99.45
M204 S10000
G1 X128.359 Y119.318 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230059
G1 F1079
G1 X128.511 Y119.32 E.00223
G3 X129.155 Y119.4 I-.51 J6.681 E.00961
G1 X129.738 Y119.529 E.00882
G1 X130.292 Y119.704 E.00858
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.839 Y120.509 E.00858
G1 X132.31 Y120.87 E.00876
G1 X132.738 Y121.262 E.00858
G1 X133.132 Y121.693 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.8 Y122.647 E.00858
G1 X134.074 Y123.172 E.00876
G1 X134.296 Y123.708 E.00858
G1 X134.472 Y124.266 E.00864
G1 X134.598 Y124.837 E.00864
G1 X134.674 Y125.412 E.00858
G1 X134.7 Y126.004 E.00876
G1 X134.674 Y126.584 E.00858
G1 X134.598 Y127.163 E.00864
G1 X134.472 Y127.734 E.00864
G1 X134.297 Y128.288 E.00858
G1 X134.07 Y128.835 E.00876
G1 X133.802 Y129.35 E.00858
G1 X133.488 Y129.843 E.00864
G1 X133.13 Y130.31 E.0087
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.839 Y131.491 E.0087
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00864
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.161 Y131.491 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.353 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X127.705 Y119.307 I6.7 J.004 E.15115
G1 X128.299 Y119.317 E.00879
; CHANGE_LAYER
; Z_HEIGHT: 13.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X128.511 Y119.32 E-.08024
G1 X129.155 Y119.4 E-.24695
G1 X129.291 Y119.431 E-.05282
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 67/74
; update layer progress
M73 L67
M991 S0 P66 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z13.6 I-.133 J-1.21 P1  F30000
G1 X127.155 Y119.665 Z13.6
G1 Z13.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1060
G1 X127.65 Y119.608 E.01602
G3 X128.313 Y119.607 I.345 J5.534 E.02134
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.882 Y119.697 I-.316 J6.392 E1.24688
G1 X127.096 Y119.672 E.00692
M204 S250
G1 X127.199 Y120.054 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1060
M204 S5000
G1 X127.669 Y120 E.01408
G3 X128.296 Y119.999 I.326 J5.234 E.01869
G3 X126.954 Y120.082 I-.299 J6 E1.08427
G1 X127.14 Y120.061 E.00557
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.669 Y120 E-.20238
G1 X128.136 Y119.999 E-.17762
; WIPE_END
G1 E-.02 F1800
G17
G3 Z13.8 I1.172 J.328 P1  F30000
G1 X128.41 Y119.019 Z13.8
G1 Z13.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1060
G1 X129.21 Y119.108 E.02586
G3 X126.993 Y119.077 I-1.204 J6.89 E1.34168
G3 X128.35 Y119.012 I1.013 J6.936 E.04375
G1 X128.351 Y119.012 E.00002
M204 S250
G1 X128.454 Y118.63 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1060
M204 S5000
G1 X129.281 Y118.723 E.02481
M73 P89 R1
G3 X126.94 Y118.689 I-1.276 J7.276 E1.31245
G3 X128.367 Y118.621 I1.066 J7.333 E.04262
G1 X128.394 Y118.624 E.00079
M204 S10000
G1 X128.366 Y119.315 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230058
G1 F1060
G1 X128.519 Y119.32 E.00227
G3 X129.155 Y119.4 I-.519 J6.68 E.00948
G1 X129.738 Y119.529 E.00882
G1 X130.292 Y119.704 E.00858
G1 X130.831 Y119.928 E.00864
G1 X131.35 Y120.198 E.00865
G1 X131.839 Y120.509 E.00858
G1 X132.31 Y120.87 E.00876
G1 X132.738 Y121.262 E.00858
G1 X133.132 Y121.693 E.00864
G1 X133.488 Y122.157 E.00864
G1 X133.8 Y122.646 E.00858
G1 X134.074 Y123.172 E.00876
G1 X134.296 Y123.708 E.00858
G1 X134.472 Y124.266 E.00864
G1 X134.599 Y124.841 E.0087
G1 X134.674 Y125.416 E.00858
G1 X134.7 Y126 E.00864
G1 X134.674 Y126.584 E.00864
G1 X134.599 Y127.159 E.00858
G1 X134.47 Y127.738 E.00876
G1 X134.296 Y128.292 E.00858
G1 X134.072 Y128.831 E.00864
G1 X133.802 Y129.35 E.00865
G1 X133.491 Y129.84 E.00858
G1 X133.13 Y130.31 E.00876
G1 X132.738 Y130.738 E.00858
G1 X132.307 Y131.132 E.00864
G1 X131.843 Y131.488 E.00864
G1 X131.354 Y131.8 E.00858
G1 X130.831 Y132.072 E.0087
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00865
G1 X124.16 Y131.491 E.00858
G1 X123.693 Y131.132 E.0087
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.509 Y129.839 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00864
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y126 E.00864
G3 X128.024 Y119.3 I6.7 J0 E.15594
G1 X128.306 Y119.312 E.00416
; CHANGE_LAYER
; Z_HEIGHT: 13.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X128.519 Y119.32 E-.08111
G1 X129.155 Y119.4 E-.24365
G1 X129.297 Y119.432 E-.05524
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 68/74
; update layer progress
M73 L68
M991 S0 P67 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z13.8 I-.129 J-1.21 P1  F30000
G1 X127.161 Y119.66 Z13.8
G1 Z13.6
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X127.469 Y119.62 E.01001
G3 X129.114 Y119.695 I.519 J6.623 E.05309
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.882 Y119.696 I-1.114 J6.305 E1.2214
G1 X127.101 Y119.667 E.00711
M204 S250
G1 X127.211 Y120.048 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X127.502 Y120.011 E.00873
G3 X129.043 Y120.081 I.489 J6.201 E.04607
G3 X126.954 Y120.082 I-1.043 J5.917 E1.06198
G1 X127.152 Y120.056 E.00593
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.502 Y120.011 E-.13412
G1 X127.972 Y119.99 E-.17893
G1 X128.148 Y119.995 E-.06695
; WIPE_END
G1 E-.02 F1800
G17
G3 Z14 I1.167 J.346 P1  F30000
G1 X128.438 Y119.02 Z14
G1 Z13.6
M73 P90 R1
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X129.21 Y119.109 E.02498
G3 X126.958 Y119.083 I-1.206 J6.89 E1.34047
G3 X128.378 Y119.014 I1.052 J7.046 E.0458
M204 S250
G1 X128.482 Y118.631 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X129.281 Y118.723 E.02396
G3 X126.905 Y118.694 I-1.278 J7.275 E1.31137
G3 X128.411 Y118.623 I1.105 J7.435 E.04499
G1 X128.422 Y118.625 E.00034
M204 S10000
G1 X128.393 Y119.319 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230068
G1 F1061
G1 X128.582 Y119.326 E.00279
G1 X129.171 Y119.404 E.00878
G1 X129.734 Y119.528 E.00852
G1 X130.295 Y119.706 E.0087
G1 X130.831 Y119.928 E.00858
G1 X131.35 Y120.198 E.00864
G1 X131.843 Y120.512 E.00864
G1 X132.303 Y120.865 E.00858
G1 X132.74 Y121.265 E.00876
G1 X133.132 Y121.693 E.00858
G1 X133.488 Y122.157 E.00864
G1 X133.802 Y122.65 E.00864
G1 X134.07 Y123.165 E.00858
G1 X134.297 Y123.712 E.00876
G1 X134.472 Y124.266 E.00858
G1 X134.598 Y124.837 E.00864
G1 X134.674 Y125.416 E.00864
G1 X134.7 Y125.996 E.00858
G1 X134.674 Y126.588 E.00876
G1 X134.598 Y127.163 E.00858
G1 X134.472 Y127.734 E.00864
G1 X134.296 Y128.292 E.00864
G1 X134.074 Y128.828 E.00858
G1 X133.8 Y129.353 E.00876
G1 X133.488 Y129.843 E.00858
G1 X133.132 Y130.307 E.00864
G1 X132.738 Y130.738 E.00864
G1 X132.31 Y131.13 E.00858
G1 X131.839 Y131.491 E.00876
G1 X131.35 Y131.802 E.00858
G1 X130.831 Y132.072 E.00864
G1 X130.292 Y132.296 E.00864
G1 X129.738 Y132.47 E.00858
G1 X129.159 Y132.599 E.00876
G1 X128.584 Y132.674 E.00858
G1 X128 Y132.7 E.00864
G1 X127.416 Y132.674 E.00864
G1 X126.841 Y132.599 E.00858
G1 X126.262 Y132.47 E.00876
G1 X125.708 Y132.296 E.00858
G1 X125.169 Y132.072 E.00864
G1 X124.65 Y131.802 E.00864
G1 X124.161 Y131.491 E.00858
G1 X123.69 Y131.13 E.00876
G1 X123.262 Y130.738 E.00858
G1 X122.868 Y130.307 E.00864
G1 X122.512 Y129.843 E.00864
G1 X122.2 Y129.354 E.00858
G1 X121.926 Y128.828 E.00876
G1 X121.704 Y128.292 E.00858
G1 X121.528 Y127.734 E.00864
G1 X121.402 Y127.163 E.00864
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X127.964 Y119.301 I6.698 J.003 E.15499
G1 X128.334 Y119.316 E.00547
; CHANGE_LAYER
; Z_HEIGHT: 13.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X128.582 Y119.326 E-.09463
G1 X129.171 Y119.404 E-.22576
G1 X129.325 Y119.438 E-.05961
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 69/74
; update layer progress
M73 L69
M991 S0 P68 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z14 I-.124 J-1.211 P1  F30000
G1 X127.17 Y119.658 Z14
G1 Z13.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X127.444 Y119.622 E.00887
G3 X128.557 Y119.622 I.556 J6.617 E.03583
G3 X126.888 Y119.695 I-.557 J6.377 E1.23953
G1 X127.111 Y119.665 E.00722
M204 S250
G1 X127.222 Y120.046 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P91 R1
G1 F1061
M204 S5000
G1 X127.478 Y120.012 E.00771
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G1 X127.976 Y119.99 E.01485
G3 X126.956 Y120.081 I.021 J6.008 E1.09393
G1 X127.162 Y120.054 E.00618
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.478 Y120.012 E-.12118
G1 X127.976 Y119.99 E-.1894
G1 X128.159 Y119.998 E-.06942
; WIPE_END
G1 E-.02 F1800
G17
G3 Z14.2 I1.161 J.366 P1  F30000
G1 X128.467 Y119.02 Z14.2
G1 Z13.8
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X129.21 Y119.109 E.02404
G3 X126.914 Y119.089 I-1.207 J6.89 E1.3391
G3 X128.407 Y119.016 I1.102 J7.219 E.04815
M204 S250
G1 X128.513 Y118.631 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X129.281 Y118.723 E.02304
G3 X126.86 Y118.701 I-1.278 J7.275 E1.31003
G3 X128.453 Y118.626 I1.156 J7.608 E.04759
M204 S10000
G1 X128.427 Y119.319 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230082
G1 F1061
G1 X128.567 Y119.324 E.00207
G1 X129.164 Y119.402 E.0089
G1 X129.734 Y119.528 E.00863
G1 X130.292 Y119.704 E.00864
G1 X130.831 Y119.928 E.00864
G1 X131.346 Y120.196 E.00858
G1 X131.846 Y120.514 E.00876
G1 X132.307 Y120.868 E.00858
G1 X132.738 Y121.262 E.00864
G1 X133.132 Y121.693 E.00864
G1 X133.486 Y122.154 E.00858
G1 X133.804 Y122.654 E.00877
G1 X134.072 Y123.169 E.00858
G1 X134.296 Y123.708 E.00864
G1 X134.472 Y124.266 E.00864
G1 X134.597 Y124.833 E.00858
G1 X134.675 Y125.42 E.00876
G1 X134.7 Y126 E.00858
G1 X134.674 Y126.584 E.00864
G1 X134.598 Y127.163 E.00864
G1 X134.473 Y127.73 E.00858
G1 X134.294 Y128.295 E.00876
G1 X134.072 Y128.831 E.00858
G1 X133.802 Y129.35 E.00865
G1 X133.488 Y129.843 E.00864
G1 X133.135 Y130.303 E.00858
G1 X132.735 Y130.74 E.00876
G1 X132.307 Y131.132 E.00858
G1 X131.843 Y131.488 E.00864
G1 X131.35 Y131.802 E.00864
G1 X130.835 Y132.07 E.00858
G1 X130.288 Y132.297 E.00876
G1 X129.734 Y132.472 E.00858
G1 X129.163 Y132.598 E.00864
G1 X128.584 Y132.674 E.00864
G1 X128.004 Y132.7 E.00858
G1 X127.412 Y132.674 E.00876
G1 X126.837 Y132.598 E.00858
G1 X126.266 Y132.472 E.00864
G1 X125.708 Y132.296 E.00864
G1 X125.172 Y132.074 E.00858
G1 X124.647 Y131.8 E.00876
G1 X124.157 Y131.488 E.00858
G1 X123.693 Y131.132 E.00864
G1 X123.262 Y130.738 E.00864
G1 X122.87 Y130.31 E.00858
G1 X122.51 Y129.84 E.00876
G1 X122.198 Y129.35 E.00858
G1 X121.928 Y128.831 E.00864
G1 X121.704 Y128.292 E.00864
G1 X121.53 Y127.738 E.00858
G1 X121.401 Y127.159 E.00876
G1 X121.326 Y126.584 E.00858
G1 X121.3 Y125.996 E.0087
G3 X127.961 Y119.301 I6.713 J.019 E.15485
G1 X128.367 Y119.317 E.00601
; CHANGE_LAYER
; Z_HEIGHT: 14
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
M73 P92 R1
G1 X128.567 Y119.324 E-.0761
G1 X129.164 Y119.402 E-.22884
G1 X129.357 Y119.445 E-.07506
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 70/74
; update layer progress
M73 L70
M991 S0 P69 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z14.2 I-.118 J-1.211 P1  F30000
G1 X127.18 Y119.656 Z14.2
G1 Z14
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X127.442 Y119.622 E.00848
G1 X127.986 Y119.597 E.01752
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.888 Y119.695 I.013 J6.4 E1.25751
G1 X127.121 Y119.664 E.00755
M204 S250
G1 X127.232 Y120.045 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X127.476 Y120.013 E.00735
G1 X127.987 Y119.99 E.01521
G3 X126.956 Y120.081 I.013 J6.007 E1.09345
G1 X127.172 Y120.053 E.00649
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.476 Y120.013 E-.11658
G1 X127.987 Y119.99 E-.1941
G1 X128.169 Y119.998 E-.06932
; WIPE_END
G1 E-.02 F1800
G17
G3 Z14.4 I1.153 J.389 P1  F30000
G1 X128.498 Y119.022 Z14.4
G1 Z14
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X129.215 Y119.11 E.02323
G3 X126.785 Y119.109 I-1.219 J6.888 E1.33473
G3 X128.438 Y119.018 I1.259 J7.825 E.05335
M204 S250
G1 X128.546 Y118.633 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X129.283 Y118.725 E.02213
G3 X126.717 Y118.722 I-1.289 J7.274 E1.30572
G3 X128.486 Y118.628 I1.329 J8.282 E.05287
M204 S10000
G1 X128.459 Y119.319 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230086
M73 P93 R1
G1 F1061
G1 X128.481 Y119.317 E.00032
G3 X121.523 Y127.71 I-.484 J6.679 E.43377
G1 X121.402 Y127.163 E.00827
G1 X121.326 Y126.588 E.00858
G1 X121.3 Y125.996 E.00876
G3 X127.99 Y119.3 I6.696 J0 E.15541
G1 X128.399 Y119.316 E.00606
; CHANGE_LAYER
; Z_HEIGHT: 14.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X128.481 Y119.317 E-.03112
G1 X129.157 Y119.401 E-.25888
G1 X129.388 Y119.452 E-.09
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 71/74
; update layer progress
M73 L71
M991 S0 P70 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z14.4 I-.112 J-1.212 P1  F30000
G1 X127.191 Y119.655 Z14.4
G1 Z14.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X127.442 Y119.622 E.00816
G1 X127.993 Y119.597 E.01773
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.918 Y119.689 I.007 J6.4 E1.25826
G1 X127.131 Y119.662 E.0069
M204 S250
G1 X127.241 Y120.043 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X127.476 Y120.013 E.00706
G1 X127.993 Y119.99 E.01542
G3 X126.985 Y120.076 I.006 J6.007 E1.09413
G1 X127.182 Y120.051 E.00589
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.476 Y120.013 E-.1129
G1 X127.993 Y119.99 E-.19673
G1 X128.179 Y119.998 E-.07038
; WIPE_END
M73 P94 R0
G1 E-.02 F1800
G17
G3 Z14.6 I1.133 J.445 P1  F30000
G1 X128.56 Y119.027 Z14.6
G1 Z14.2
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X128.604 Y119.029 E.00142
G3 X129.215 Y132.891 I-.612 J6.972 E.64776
G3 X128.013 Y119.003 I-1.214 J-6.891 E.74651
G1 X128.5 Y119.024 E.01569
M204 S250
G1 X128.578 Y118.635 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X128.639 Y118.638 E.00182
G3 X128.013 Y118.61 I-.638 J7.36 E1.36404
G1 X128.518 Y118.633 E.01504
M204 S10000
G1 X128.488 Y119.321 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.230069
G1 F1061
G1 X128.579 Y119.328 E.00134
G3 X121.924 Y128.822 I-.582 J6.671 E.41484
G1 X121.704 Y128.291 E.00849
G1 X121.53 Y127.738 E.00858
G1 X121.403 Y127.167 E.00864
G1 X121.326 Y126.584 E.0087
G1 X121.3 Y125.995 E.00871
G3 X127.997 Y119.303 I6.697 J.005 E.15544
G1 X128.428 Y119.319 E.00638
; CHANGE_LAYER
; Z_HEIGHT: 14.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X128.579 Y119.328 E-.05726
G1 X129.164 Y119.402 E-.22395
G1 X129.417 Y119.458 E-.09879
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 72/74
; update layer progress
M73 L72
M991 S0 P71 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z14.6 I-.104 J-1.213 P1  F30000
G1 X127.199 Y119.648 Z14.6
G1 Z14.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X127.441 Y119.616 E.00787
G1 X127.997 Y119.592 E.0179
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.887 Y119.689 I.001 J6.405 E1.25819
G1 X127.139 Y119.656 E.00817
M204 S250
G1 X127.25 Y120.037 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
M73 P95 R0
G1 F1061
M204 S5000
G1 X127.476 Y120.007 E.00678
G1 X127.997 Y119.985 E.01556
G3 X126.955 Y120.076 I.001 J6.013 E1.09409
G1 X127.191 Y120.045 E.00706
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.476 Y120.007 E-.10924
G1 X127.997 Y119.985 E-.19854
G1 X128.187 Y119.993 E-.07223
; WIPE_END
G1 E-.02 F1800
G17
G3 Z14.8 I1.123 J.47 P1  F30000
G1 X128.591 Y119.028 Z14.8
G1 Z14.4
G1 E.4 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1061
G1 X128.607 Y119.029 E.0005
G3 X128.008 Y119.003 I-.607 J6.968 E1.39382
G1 X128.531 Y119.026 E.01685
M204 S250
G1 X128.609 Y118.637 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1061
M204 S5000
G1 X128.641 Y118.638 E.00097
G3 X128.008 Y118.61 I-.641 J7.358 E1.36349
G1 X128.549 Y118.634 E.01612
M204 S10000
G1 X128.519 Y119.32 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.224742
G1 F1061
G1 X128.58 Y119.323 E.00088
G1 X129.168 Y119.4 E.00851
G1 X129.735 Y119.526 E.00835
G1 X130.292 Y119.702 E.0084
G1 X130.832 Y119.925 E.0084
G1 X131.348 Y120.193 E.00834
G1 X131.845 Y120.51 E.00848
G1 X132.308 Y120.866 E.00838
G1 X132.739 Y121.261 E.0084
G1 X133.134 Y121.692 E.0084
G1 X133.488 Y122.152 E.00834
G1 X133.806 Y122.652 E.00851
G1 X134.075 Y123.168 E.00835
G1 X134.299 Y123.709 E.00841
G1 X134.474 Y124.265 E.00838
G1 X134.601 Y124.836 E.0084
G1 X134.677 Y125.416 E.0084
G1 X134.702 Y125.996 E.00834
G1 X134.677 Y126.588 E.00851
G1 X134.601 Y127.164 E.00834
G1 X134.474 Y127.735 E.0084
G1 X134.298 Y128.292 E.0084
G1 X134.076 Y128.829 E.00834
G1 X133.803 Y129.354 E.00851
M73 P96 R0
G1 X133.49 Y129.844 E.00834
G1 X133.134 Y130.308 E.0084
G1 X132.739 Y130.739 E.0084
G1 X132.312 Y131.131 E.00833
G1 X131.841 Y131.493 E.00852
G1 X131.351 Y131.805 E.00834
G1 X130.832 Y132.075 E.0084
G1 X130.292 Y132.298 E.00839
G1 X129.739 Y132.473 E.00833
G1 X129.16 Y132.601 E.00852
G1 X128.584 Y132.677 E.00834
G1 X128 Y132.703 E.0084
G1 X127.416 Y132.677 E.0084
G1 X126.84 Y132.601 E.00834
G1 X126.261 Y132.473 E.00852
G1 X125.708 Y132.298 E.00834
G1 X125.168 Y132.075 E.00839
G1 X124.649 Y131.805 E.0084
G1 X124.159 Y131.492 E.00834
G1 X123.689 Y131.132 E.00851
G1 X123.261 Y130.739 E.00834
G1 X122.866 Y130.308 E.0084
G1 X122.509 Y129.844 E.0084
G1 X122.198 Y129.355 E.00833
G1 X121.924 Y128.829 E.00852
G1 X121.702 Y128.292 E.00834
G1 X121.526 Y127.735 E.0084
G1 X121.399 Y127.164 E.0084
G1 X121.323 Y126.588 E.00834
G1 X121.298 Y125.996 E.00852
G3 X128.001 Y119.299 I6.716 J.018 E.15107
G1 X128.459 Y119.318 E.00658
; CHANGE_LAYER
; Z_HEIGHT: 14.6
; LAYER_HEIGHT: 0.200001
; WIPE_START
G1 F15000
G1 X128.58 Y119.323 E-.04608
G1 X129.168 Y119.4 E-.22514
G1 X129.447 Y119.462 E-.10878
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 73/74
; update layer progress
M73 L73
M991 S0 P72 ;notify layer change
; OBJECT_ID: 15
G17
G3 Z14.8 I-.032 J-1.217 P1  F30000
G1 X127.191 Y119.521 Z14.8
G1 Z14.6
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F663
M204 S5000
G1 X127.431 Y119.496 E.00718
G3 X127.736 Y119.476 I.577 J6.507 E.00911
G3 X132.201 Y120.993 I.258 J6.568 E.14367
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X126.866 Y119.571 I-4.193 J5.009 E1.05278
G1 X127.132 Y119.53 E.008
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.431 Y119.496 E-.11443
G1 X127.736 Y119.476 E-.11618
G1 X128 Y119.464 E-.10039
G1 X128.129 Y119.47 E-.04901
; WIPE_END
G1 E-.02 F1800
G17
G3 Z15 I1.039 J.634 P1  F30000
G1 X128.637 Y118.638 Z15
G1 Z14.6
G1 E.4 F1800
G1 F663
M204 S5000
G1 X128.644 Y118.638 E.00022
G3 X128.003 Y118.61 I-.644 J7.358 E1.36321
G1 X128.577 Y118.635 E.01712
M204 S10000
G1 X128.558 Y119.062 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.504094
M73 P97 R0
G1 F663
G1 X128.606 Y119.068 E.00178
G3 X121.272 Y127.793 I-.61 J6.932 E1.10642
G1 X121.143 Y127.209 E.02178
G1 X121.065 Y126.617 E.02176
G1 X121.038 Y125.99 E.02286
G3 X128.01 Y119.041 I6.959 J.011 E.39832
G1 X128.498 Y119.059 E.01779
; CHANGE_LAYER
; Z_HEIGHT: 14.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9757.706
G1 X128.606 Y119.068 E-.04135
G1 X129.193 Y119.141 E-.22442
G1 X129.486 Y119.205 E-.11423
; WIPE_END
G1 E-.02 F1800
; layer num/total_layer_count: 74/74
; update layer progress
M73 L74
M991 S0 P73 ;notify layer change
M106 S102
; OBJECT_ID: 15
G17
G3 Z15 I.102 J-1.213 P1  F30000
G1 X127.144 Y119.007 Z15
G1 Z14.8
G1 E.4 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F600
M204 S5000
G1 X127.484 Y118.967 E.01021
G3 X130.982 Y119.605 I.529 J7.002 E.10708
G3 X126.776 Y119.056 I-2.975 J6.395 E1.19169
G1 X127.084 Y119.015 E.00927
; WIPE_START
G1 F11933.819
M204 S10000
G1 X127.484 Y118.967 E-.15305
G1 X127.484 Y118.967 E0
G1 X128 Y118.944 E-.19632
G1 X128.081 Y118.948 E-.03063
; WIPE_END
G1 E-.02 F1800
G17
G3 Z15.2 I.532 J1.095 P1  F30000
G1 X128.658 Y118.667 Z15.2
G1 Z14.8
G1 E.4 F1800
G1 F600
M204 S5000
G1 X129.278 Y118.75 E.01864
G3 X129.279 Y133.251 I-1.286 J7.251 E.61207
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

G3 X128.598 Y118.661 I-1.272 J-7.251 E.74468
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F11933.819
M204 S10000
M73 P98 R0
G1 X129.278 Y118.75 E-.26062
G1 X129.585 Y118.817 E-.11938
; WIPE_END
G1 E-.02 F1800
G17
G3 Z15.2 I1.217 J0 P1  F30000
M106 S0
M106 P2 S0
M981 S0 P20000 ; close spaghetti detector
; FEATURE: Custom
; MACHINE_END_GCODE_START
; filament end gcode 

;===== date: 20230428 =====================
M400 ; wait for buffer to clear
G92 E0 ; zero the extruder
G1 E-0.8 F1800 ; retract
G1 Z15.3 F900 ; lower z a little
G1 X65 Y245 F12000 ; move to safe pos 
G1 Y265 F3000

G1 X65 Y245 F12000
G1 Y265 F3000
M140 S0 ; turn off bed
M106 S0 ; turn off fan
M106 P2 S0 ; turn off remote part cooling fan
M106 P3 S0 ; turn off chamber cooling fan

G1 X100 F12000 ; wipe
; pull back filament to AMS
M620 S255
G1 X20 Y50 F12000
G1 Y-3
T255
G1 X65 F12000
G1 Y265
G1 X100 F12000 ; wipe
M621 S255
M104 S0 ; turn off hotend

M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
    M400 ; wait all motion done
    M991 S0 P-1 ;end smooth timelapse at safe pos
    M400 S3 ;wait for last picture to be taken
M623; end of "timelapse_record_flag"

M400 ; wait all motion done
M17 S
M17 Z0.4 ; lower z motor current to reduce impact if there is something in the bottom

    G1 Z114.8 F600
    G1 Z112.8

M400 P100
M17 R ; restore z current

G90
G1 X128 Y250 F3600

M220 S100  ; Reset feedrate magnitude
M201.2 K1.0 ; Reset acc magnitude
M73.2   R1.0 ;Reset left time magnitude
M1002 set_gcode_claim_speed_level : 0

M17 X0.8 Y0.8 Z0.5 ; lower motor current to 45% power
M73 P100 R0
; EXECUTABLE_BLOCK_END

