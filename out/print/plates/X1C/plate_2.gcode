; HEADER_BLOCK_START
; BambuStudio 02.08.02.61
; model printing time: 10m 5s; total estimated time: 10m 25s
; total layer number: 15
; total filament length [mm] : 1034.46
; total filament volume [cm^3] : 2488.18
; total filament weight [g] : 3.09
; model label id: 795,817,839,861
; object max height: 1.00,3.00,2.00,1.00
; filament_density: 1.24
; filament_diameter: 1.75
; max_z_height: 3.00
; filament: 1
; support_material_on_wipe_tower: 0
; HEADER_BLOCK_END

; CONFIG_BLOCK_START
; accel_to_decel_enable = 0
; accel_to_decel_factor = 50%
; activate_air_filtration = 0
; additional_cooling_fan_speed = 70
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
; close_additional_fan_first_x_layers = 1
; close_fan_the_first_x_layers = 1
; compatible_printers_condition = 
; complete_print_exhaust_fan_speed = 70
; cool_plate_temp = 35
; cool_plate_temp_initial_layer = 35
; cooling_filter_enabled = 0
; cooling_perimeter_transition_distance = 10
; cooling_slowdown_logic = uniform_cooling
; counter_coef_1 = 0
; counter_coef_2 = 0.008
; counter_coef_3 = -0.041
; counter_limit_max = 0.033
; counter_limit_min = -0.035
; counterbore_hole_bridging = none
; curr_bed_type = Cool Plate
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
; enable_prime_tower = 0
; enable_support = 0
; enable_support_ironing = 0
; enable_tower_interface_features = 0
; enable_wrapping_detection = 0
; enforce_support_layers = 0
; eng_plate_temp = 0
; eng_plate_temp_initial_layer = 0
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
; fan_cooling_layer_time = 100
; fan_direction = left
; fan_max_speed = 100
; fan_min_speed = 100
; farthest_point_timelapse = 1
; filament_adaptive_volumetric_speed = 0
; filament_adhesiveness_category = 100
; filament_bridge_speed = 25
; filament_change_length = 10
; filament_change_length_nc = 10
; filament_colour = #00AE42
; filament_cooling_before_tower = 0
; filament_cost = 20
; filament_density = 1.24
; filament_dev_ams_drying_ams_limitations = 1
; filament_dev_ams_drying_heat_distortion_temperature = 45
; filament_dev_ams_drying_temperature = 45
; filament_dev_ams_drying_time = 12
; filament_dev_chamber_drying_bed_temperature = 70
; filament_dev_chamber_drying_time = 12
; filament_dev_drying_cooling_temperature = 45
; filament_dev_drying_softening_temperature = 50
; filament_diameter = 1.75
; filament_enable_overhang_speed = 1
; filament_end_gcode = "; filament end gcode \n\n"
; filament_extruder_compatibility = 0
; filament_extruder_variant = "Direct Drive Standard"
; filament_flow_ratio = 0.98
; filament_flush_temp = 0
; filament_flush_temp_fast = 0
; filament_flush_volumetric_speed = 0
; filament_ids = GFL99
; filament_is_mixed = 0
; filament_is_support = 0
; filament_map = 1
; filament_map_2 = 0
; filament_map_mode = Auto For Flush
; filament_max_volumetric_speed = 12
; filament_metal_stickiness = None
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
; filament_scarf_gap = 15%
; filament_scarf_height = 10%
; filament_scarf_length = 10
; filament_scarf_seam_type = none
; filament_self_index = 1
; filament_settings_id = "Generic PLA"
; filament_shrink = 100%
; filament_soluble = 0
; filament_start_gcode = "; filament start gcode\n{if  (bed_temperature[current_extruder] >55)||(bed_temperature_initial_layer[current_extruder] >55)}M106 P3 S200\n{elsif(bed_temperature[current_extruder] >50)||(bed_temperature_initial_layer[current_extruder] >50)}M106 P3 S150\n{elsif(bed_temperature[current_extruder] >45)||(bed_temperature_initial_layer[current_extruder] >45)}M106 P3 S50\n{endif}\n\n{if activate_air_filtration[current_extruder] && support_air_filtration}\nM106 P3 S{during_print_exhaust_fan_speed_num[current_extruder]} \n{endif}"
; filament_tower_interface_pre_extrusion_dist = 10
; filament_tower_interface_pre_extrusion_length = 0
; filament_tower_interface_print_temp = -1
; filament_tower_interface_purge_volume = 20
; filament_tower_ironing_area = 4
; filament_type = PLA
; filament_velocity_adaptation_factor = 1
; filament_vendor = Generic
; filament_volume_map = 0
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
; hot_plate_temp = 55
; hot_plate_temp_initial_layer = 55
; hotend_cooling_rate = 2
; hotend_heating_rate = 2
; impact_strength_z = 10
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
; nozzle_temperature = 220
; nozzle_temperature_initial_layer = 220
; nozzle_temperature_range_high = 240
; nozzle_temperature_range_low = 190
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
; overhang_fan_speed = 100
; overhang_fan_threshold = 50%
; overhang_threshold_participating_cooling = 95%
; overhang_totally_speed = 10
; override_filament_scarf_seam_setting = 0
; override_process_overhang_speed = 0
; physical_extruder_map = 0
; post_process = 
; pre_start_fan_time = 0
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
; slow_down_layer_time = 8
; slow_down_min_speed = 20
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
; supertack_plate_temp = 45
; supertack_plate_temp_initial_layer = 45
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
; temperature_vitrification = 45
; template_custom_gcode = 
; textured_plate_temp = 55
; textured_plate_temp_initial_layer = 55
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
M73 P0 R10
M201 X20000 Y20000 Z500 E5000
M203 X500 Y500 Z20 E30
M204 P20000 R5000 T20000
M205 X9.00 Y9.00 Z3.00 E2.50
M106 S0
M106 P2 S0
M190 S35 ; set bed temperature and wait for it to be reached
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
M73 P1 R10
G1 X110 Y110 Z2.0 F3000 ;Move Z Axis up
; MACHINE_START_GCODE_END
; filament start gcode


;VT0 H-1
G90
G21
M83 ; use relative distances for extrusion
M981 S1 P20000 ;open spaghetti detector
; CHANGE_LAYER
; Z_HEIGHT: 0.2
; LAYER_HEIGHT: 0.2
G1 E-.8 F1800
; layer num/total_layer_count: 1/15
; update layer progress
M73 L1
M991 S0 P0 ;notify layer change
M106 S0
M106 P2 S0
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
M73 P2 R10
G1 X126.021 Y170.787 F30000
M204 S6000
M73 P3 R10
G1 Z.4
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G1 X125.978 Y170.787 E.00162
G3 X125.567 Y170.737 I-.061 J-1.229 E.01547
G3 X125.939 Y167.745 I.499 J-1.457 E.15653
G3 X127.07 Y168.102 I.129 J1.561 E.04533
G3 X127.379 Y169.795 I-.789 J1.018 E.07018
G3 X126.579 Y170.595 I-1.345 J-.545 E.04327
G3 X126.242 Y170.744 I-.662 J-1.038 E.01379
G1 X126.08 Y170.776 E.00614
; WIPE_START
G1 X125.978 Y170.787 E-.03917
G1 X125.697 Y170.769 E-.10676
G1 X125.567 Y170.737 E-.05086
G1 X125.432 Y170.694 E-.0539
G1 X125.19 Y170.559 E-.1054
G1 X124.979 Y170.387 E-.10325
G1 X124.804 Y170.179 E-.10333
G1 X124.669 Y169.945 E-.10271
G1 X124.584 Y169.711 E-.09461
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X128.097 Y166.073 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G1 X128.068 Y165.889 E.00695
G3 X129.474 Y164.21 I1.533 J-.145 E.09074
G3 X130.605 Y164.566 I.129 J1.561 E.0453
G3 X130.915 Y166.259 I-.788 J1.019 E.07019
G3 X130.115 Y167.059 I-1.345 J-.545 E.04329
G3 X129.108 Y167.203 I-.661 J-1.036 E.03904
G3 X128.117 Y166.154 I.493 J-1.459 E.05594
G1 X128.112 Y166.131 E.00086
M204 S6000
G1 X127.658 Y166.201 F30000
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X127.732 Y166.438 E.00922
G2 X128.795 Y167.583 I1.887 J-.686 E.0598
G2 X129.293 Y167.718 I1.192 J-3.423 E.01924
G2 X128.037 Y168.974 I15.365 J16.621 E.06617
G2 X124.187 Y169.976 I-1.975 J.309 E.24875
G1 X124.289 Y170.224 E.00998
G1 X124.102 Y170.349 E.00838
G1 X113.701 Y159.947 E.54788
G1 X113.826 Y159.76 E.00838
G2 X115.576 Y156.148 I.925 J-1.782 E.23906
G2 X115.091 Y156.016 I-1.106 J3.114 E.01873
G2 X116.336 Y154.772 I-32.09 J-33.358 E.06555
G2 X120.182 Y153.754 I1.973 J-.323 E.24829
G1 X120.08 Y153.506 E.00997
G1 X120.267 Y153.381 E.00838
G1 X130.668 Y163.783 E.54788
G1 X130.543 Y163.97 E.00838
G2 X127.641 Y166.101 I-.925 J1.782 E.16633
G1 X127.648 Y166.142 E.00155
; WIPE_START
G1 X127.732 Y166.438 E-.11674
G1 X127.79 Y166.603 E-.06657
G1 X127.965 Y166.906 E-.13321
G1 X128.194 Y167.178 E-.13475
G1 X128.468 Y167.402 E-.13463
G1 X128.795 Y167.583 E-.14208
G1 X128.876 Y167.605 E-.03203
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X123.619 Y162.072 Z.6 F30000
G1 X116.855 Y154.952 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3000
M204 S500
G1 X116.818 Y154.817 E.00522
G3 X116.943 Y154.016 I1.279 J-.211 E.03069
G3 X117.704 Y153.172 I1.505 J.59 E.04327
G3 X118.251 Y152.958 I.923 J1.555 E.02197
G3 X118.802 Y152.993 I.187 J1.426 E.02073
G3 X117.299 Y155.628 I-.502 J1.46 E.20216
G3 X116.891 Y155.082 I.798 J-1.021 E.02567
G1 X116.871 Y155.01 E.0028
; WIPE_START
G1 X116.818 Y154.817 E-.07608
G1 X116.791 Y154.536 E-.10711
G1 X116.834 Y154.271 E-.10198
G1 X116.943 Y154.016 E-.10535
G1 X117.083 Y153.74 E-.11766
G1 X117.223 Y153.54 E-.09273
G1 X117.396 Y153.368 E-.09278
G1 X117.543 Y153.274 E-.06632
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X113.261 Y158.133 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G1 X113.266 Y158.073 E.00223
G3 X113.455 Y157.471 I1.286 J.072 E.02374
G3 X114.168 Y156.707 I1.315 J.513 E.03988
G3 X114.715 Y156.493 I.925 J1.561 E.02196
G3 X115.267 Y156.528 I.187 J1.425 E.02072
G3 X113.764 Y159.163 I-.502 J1.46 E.20216
G3 X113.281 Y158.353 I.789 J-1.018 E.03597
G1 X113.267 Y158.192 E.00599
; WIPE_START
G1 X113.266 Y158.073 E-.04534
G1 X113.298 Y157.807 E-.10194
G1 X113.348 Y157.668 E-.05595
G1 X113.455 Y157.471 E-.08518
G1 X113.613 Y157.173 E-.12831
G1 X113.77 Y156.986 E-.09274
G1 X113.957 Y156.829 E-.09279
G1 X114.168 Y156.707 E-.09265
G1 X114.321 Y156.63 E-.06512
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X118.192 Y152.342 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G1 X118.447 Y152.237 E.01025
G3 X118.723 Y152.158 I.944 J2.777 E.01071
G3 X119.134 Y152.139 I.285 J1.791 E.01537
G3 X120.14 Y152.608 I-.175 J1.689 E.04211
G1 X131.442 Y163.91 E.5953
G3 X131.709 Y165.878 I-1.185 J1.163 E.07933
G3 X131.189 Y166.649 I-3.612 J-1.874 E.0347
G1 X130.505 Y167.334 E.03605
G2 X127.653 Y170.185 I7.784 J10.635 E.15078
G1 X126.969 Y170.869 E.03605
G3 X125.646 Y171.572 I-1.987 J-2.141 E.05642
G3 X124.229 Y171.122 I-.274 J-1.593 E.05755
G1 X112.928 Y159.821 E.59529
G3 X112.661 Y157.851 I1.185 J-1.164 E.07935
G3 X113.152 Y157.109 I3.685 J1.907 E.03321
M73 P4 R10
G3 X114.134 Y156.175 I6.666 J6.024 E.05052
G2 X115.227 Y155.246 I-4.238 J-6.09 E.0535
G2 X116.212 Y154.206 I-10.984 J-11.394 E.05337
G3 X116.781 Y153.48 I4.804 J3.179 E.03441
G1 X117.423 Y152.838 E.0338
G3 X118.037 Y152.411 I1.967 J2.175 E.02795
G1 X118.137 Y152.366 E.00409
M204 S6000
G1 X118.196 Y152.586 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.381213
G1 F3000
M204 S500
G3 X118.756 Y152.565 I.685 J10.899 E.01544
G1 X118.793 Y152.565 E.00102
; LINE_WIDTH: 0.431848
G1 X118.9 Y152.571 E.0034
; LINE_WIDTH: 0.468094
G1 X119.002 Y152.584 E.00358
; LINE_WIDTH: 0.498708
G1 X119.095 Y152.601 E.00348
; LINE_WIDTH: 0.527058
G1 X119.199 Y152.631 E.00429
; LINE_WIDTH: 0.568183
G1 X119.378 Y152.703 E.00825
; LINE_WIDTH: 0.628474
G3 X119.747 Y152.959 I-.641 J1.319 E.02153
G1 X120.038 Y153.26 E.01995
M204 S6000
G1 X120.502 Y153.97 F30000
; LINE_WIDTH: 0.122161
G1 F3000
M204 S500
M73 P4 R9
G1 X120.549 Y154.057 E.00064
G1 X120.549 Y154.24 E.00118
M204 S6000
G1 X120.749 Y154.423 F30000
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5148
G1 F6300
M204 S500
G1 X129.421 Y163.095 E.47158
G1 X129.421 Y163.373 E.01068
G2 X129.078 Y163.419 I.008 J1.336 E.01335
G1 X120.627 Y154.969 E.45955
G3 X120.454 Y155.463 I-1.49 J-.243 E.02025
G1 X128.581 Y163.59 E.44191
G1 X128.234 Y163.79 E.0154
G1 X128.169 Y163.845 E.00328
G1 X120.204 Y155.88 E.43312
G3 X119.885 Y156.229 I-1.148 J-.728 E.01826
G1 X127.82 Y164.163 E.43146
G2 X127.537 Y164.548 I1.324 J1.265 E.01841
G1 X119.501 Y156.512 E.437
G3 X119.037 Y156.715 I-1.144 J-1.988 E.01953
G1 X127.335 Y165.013 E.45125
G2 X127.221 Y165.566 I2.45 J.794 E.02176
G1 X118.477 Y156.822 E.47548
G3 X117.756 Y156.769 I-.169 J-2.604 E.02789
G1 X127.278 Y166.291 E.51783
G2 X128.549 Y167.891 I2.331 J-.547 E.08113
G1 X128.375 Y168.056 E.0092
G1 X117.051 Y156.732 E.6158
G1 X116.89 Y156.892 E.00875
G3 X117.091 Y157.439 I-1.748 J.952 E.02245
G1 X126.611 Y166.959 E.51771
G2 X125.886 Y166.901 I-.527 J2.024 E.02812
G1 X117.149 Y158.164 E.47512
G3 X117.035 Y158.717 I-2.55 J-.239 E.02176
G1 X125.333 Y167.015 E.45126
G2 X124.874 Y167.224 I.533 J1.779 E.01943
G1 X116.826 Y159.175 E.43767
G3 X116.546 Y159.563 I-1.24 J-.599 E.01848
G1 X124.484 Y167.501 E.43165
G2 X124.166 Y167.85 I.829 J1.077 E.01826
G1 X116.201 Y159.885 E.43312
G1 X116.135 Y159.94 E.00329
G1 X115.789 Y160.14 E.01539
G1 X123.915 Y168.267 E.44191
G2 X123.742 Y168.761 I1.312 J.736 E.02025
G1 X115.289 Y160.308 E.45971
G3 X114.956 Y160.356 I-.305 J-.926 E.01297
M73 P5 R9
G1 X114.957 Y160.643 E.01104
G1 X123.622 Y169.308 E.47118
M204 S6000
G1 X123.82 Y169.49 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.122127
G1 F3000
M204 S500
G1 X123.82 Y169.673 E.00118
G1 X123.867 Y169.76 E.00064
M204 S6000
G1 X124.332 Y170.47 F30000
; LINE_WIDTH: 0.632698
G1 F3000
M204 S500
G2 X124.892 Y170.975 I1.704 J-1.33 E.03643
; LINE_WIDTH: 0.591044
G2 X125.053 Y171.055 I1.099 J-1.997 E.00803
G1 X125.074 Y171.064 E.00102
; LINE_WIDTH: 0.547817
G2 X125.237 Y171.12 I.996 J-2.669 E.00709
; LINE_WIDTH: 0.503926
G1 X125.367 Y171.146 E.00498
; LINE_WIDTH: 0.473002
G1 X125.441 Y171.156 E.00262
; LINE_WIDTH: 0.436857
G1 X125.577 Y171.165 E.00435
; LINE_WIDTH: 0.381265
G2 X126.173 Y171.144 I.073 J-6.623 E.01645
; WIPE_START
G1 X125.577 Y171.165 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X127.73 Y169.67 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.136532
G1 F3000
M204 S500
G2 X127.894 Y169.355 I-3.305 J-1.925 E.00271
; WIPE_START
G1 X127.73 Y169.67 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X129.675 Y167.575 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.135921
G1 F3000
M204 S500
G2 X129.991 Y167.409 I-1.546 J-3.334 E.00271
; WIPE_START
G1 X129.675 Y167.575 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X131.464 Y165.853 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.381214
G1 F3000
M204 S500
G2 X131.484 Y165.257 I-6.605 J-.524 E.01645
; LINE_WIDTH: 0.436848
G1 X131.476 Y165.121 E.00436
; LINE_WIDTH: 0.473013
G1 X131.466 Y165.048 E.00262
; LINE_WIDTH: 0.503868
G1 X131.439 Y164.918 E.00498
; LINE_WIDTH: 0.547649
G2 X131.384 Y164.754 I-2.627 J.798 E.00709
; LINE_WIDTH: 0.591236
G1 X131.375 Y164.733 E.00102
G2 X131.294 Y164.572 I-1.836 J.817 E.00804
; LINE_WIDTH: 0.632695
G2 X130.79 Y164.012 I-1.834 J1.144 E.03642
M204 S6000
G1 X130.079 Y163.547 F30000
; LINE_WIDTH: 0.122211
G1 F3000
M204 S500
G1 X129.992 Y163.5 E.00064
G1 X129.809 Y163.5 E.00118
; WIPE_START
G1 X129.992 Y163.5 E-.49293
G1 X130.079 Y163.547 E-.26707
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X122.616 Y161.952 Z.6 F30000
G1 X114.568 Y160.231 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.123064
G1 F3000
M204 S500
G1 X114.38 Y160.231 E.00123
G1 X114.29 Y160.183 E.00067
M204 S6000
G1 X113.579 Y159.718 F30000
; LINE_WIDTH: 0.628504
G1 F3000
M204 S500
G1 X113.279 Y159.427 E.01996
G3 X113.023 Y159.058 I1.064 J-1.01 E.02152
; LINE_WIDTH: 0.568821
G1 X112.953 Y158.884 E.00805
; LINE_WIDTH: 0.528074
G1 X112.921 Y158.776 E.00444
; LINE_WIDTH: 0.498911
G1 X112.904 Y158.683 E.00354
; LINE_WIDTH: 0.46818
G1 X112.891 Y158.58 E.00358
; LINE_WIDTH: 0.431955
G1 X112.885 Y158.473 E.00339
; LINE_WIDTH: 0.381228
G1 X112.885 Y158.436 E.00102
G3 X112.905 Y157.877 I10.946 J.125 E.01544
; WIPE_START
G1 X112.885 Y158.436 E-.71273
G1 X112.885 Y158.473 E-.04727
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X114.357 Y156.328 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.135714
G1 F3000
M204 S500
G3 X114.701 Y156.158 I1.989 J3.583 E.0029
; WIPE_START
G1 X114.357 Y156.328 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X116.777 Y156.457 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.577606
G1 F3000
M204 S500
G1 X116.352 Y156.032 E.02616
; LINE_WIDTH: 0.613584
G1 X116.283 Y155.963 E.00456
; LINE_WIDTH: 0.662011
G1 X115.88 Y155.561 E.0287
; WIPE_START
G1 X116.283 Y155.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X116.477 Y154.382 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.135994
G1 F3000
M204 S500
G3 X116.647 Y154.038 I3.761 J1.65 E.00291
; OBJECT_ID: 795
; WIPE_START
G1 X116.477 Y154.382 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 795
M624 AQAAAAAAAAA=
M204 S6000
G1 X123.852 Y152.416 Z.6 F30000
G1 X147.394 Y146.142 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G3 X146.038 Y145.505 I-1.23 J.857 E.29253
G1 X146.158 Y145.5 E.00445
G3 X147.359 Y146.094 I.006 J1.5 E.05172
; WIPE_START
G1 X147.529 Y146.366 E-.12194
G1 X147.618 Y146.61 E-.09879
G1 X147.664 Y146.869 E-.10002
G1 X147.664 Y147.131 E-.09934
G1 X147.58 Y147.512 E-.14823
G1 X147.468 Y147.75 E-.09998
G1 X147.33 Y147.948 E-.0917
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X150.107 Y155.057 Z.6 F30000
G1 X156.061 Y170.3 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X159.346 Y151.104 I3.385 J-9.3 E1.02561
G3 X165.04 Y152.836 I.125 J9.814 E.22523
G3 X156.118 Y170.32 I-5.594 J8.164 E1.06301
; WIPE_START
G1 X155.262 Y169.973 E-.35094
G1 X154.496 Y169.574 E-.32817
G1 X154.316 Y169.46 E-.0809
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X153.354 Y161.888 Z.6 F30000
G1 X150.192 Y137.006 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X150.321 Y136.894 E.00637
G3 X151.276 Y136.55 I1.118 J1.606 E.03821
G1 X151.433 Y136.543 E.00588
G3 X150.059 Y137.113 I.007 J1.957 E.4011
G1 X150.146 Y137.044 E.00413
M204 S6000
G1 X150.48 Y137.348 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X151.315 Y137.005 I.961 J1.151 E.03417
G1 X151.435 Y137 E.00446
G3 X150.435 Y137.388 I.006 J1.5 E.31007
; WIPE_START
G1 X150.812 Y137.14 E-.17149
G1 X151.058 Y137.051 E-.09939
G1 X151.315 Y137.005 E-.09941
G1 X151.435 Y137 E-.04546
G1 X151.707 Y137.023 E-.1036
G1 X151.959 Y137.09 E-.09938
G1 X152.196 Y137.201 E-.09941
G1 X152.287 Y137.264 E-.04187
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X158.008 Y132.212 Z.6 F30000
G1 X161.965 Y128.719 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X162.229 Y128.821 E.01056
G3 X163.303 Y130.481 I-.799 J1.694 E.07758
G1 X163.303 Y133.519 E.11314
G3 X161.465 Y135.357 I-1.873 J-.035 E.10702
G1 X150.427 Y135.357 E.41111
G3 X148.589 Y133.519 I.035 J-1.873 E.10702
G1 X148.589 Y130.481 E.11314
M73 P6 R9
G3 X150.427 Y128.643 I1.873 J.035 E.10702
G1 X161.465 Y128.643 E.41111
G3 X161.906 Y128.704 I-.035 J1.873 E.01664
M204 S6000
G1 X161.808 Y129.15 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X162.846 Y130.491 I-.374 J1.362 E.06775
G1 X162.846 Y133.509 E.11239
G3 X161.455 Y134.9 I-1.412 J-.021 E.08106
G1 X150.437 Y134.9 E.41036
G3 X149.046 Y133.509 I.021 J-1.412 E.08106
G1 X149.046 Y130.491 E.1124
G3 X150.437 Y129.1 I1.412 J.021 E.08106
G1 X161.455 Y129.1 E.41036
G3 X161.75 Y129.136 I-.021 J1.412 E.01108
; WIPE_START
G1 X162.038 Y129.231 E-.11532
G1 X162.249 Y129.353 E-.09271
G1 X162.436 Y129.51 E-.09281
G1 X162.593 Y129.697 E-.09275
G1 X162.715 Y129.908 E-.09272
G1 X162.799 Y130.138 E-.09279
G1 X162.846 Y130.491 E-.13559
G1 X162.846 Y130.611 E-.04531
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X155.238 Y130.001 Z.6 F30000
G1 X145.379 Y129.212 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X145.662 Y129.108 E.01123
G3 X145.998 Y129.05 I.501 J1.892 E.01273
G1 X146.156 Y129.043 E.00588
G3 X145.323 Y129.232 I.007 J1.957 E.42586
M204 S6000
G1 X145.534 Y129.639 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X146.038 Y129.505 I.629 J1.361 E.01952
G1 X146.158 Y129.5 E.00446
G3 X145.481 Y129.665 I.006 J1.5 E.32473
; WIPE_START
G1 X145.781 Y129.551 E-.12201
G1 X146.038 Y129.505 E-.09942
G1 X146.158 Y129.5 E-.04546
G1 X146.43 Y129.523 E-.10359
G1 X146.682 Y129.59 E-.09939
G1 X146.919 Y129.701 E-.09941
G1 X147.133 Y129.851 E-.09937
G1 X147.303 Y130.021 E-.09136
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X154.051 Y133.588 Z.6 F30000
G1 X166.221 Y140.023 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X166.186 Y140.002 E.00151
G3 X167.276 Y136.55 I1.254 J-1.502 E.17216
G1 X167.433 Y136.543 E.00588
G3 X166.469 Y140.199 I.007 J1.957 E.26704
G1 X166.27 Y140.058 E.00912
M204 S6000
G1 X166.48 Y139.651 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X167.315 Y137.005 I.96 J-1.152 E.13197
G1 X167.435 Y137 E.00446
G3 X166.527 Y139.689 I.006 J1.5 E.21227
; WIPE_START
G1 X166.297 Y139.464 E-.12213
G1 X166.087 Y139.136 E-.14822
G1 X165.997 Y138.888 E-.09999
G1 X165.951 Y138.631 E-.0994
G1 X165.951 Y138.369 E-.09938
G1 X165.997 Y138.112 E-.09941
G1 X166.089 Y137.889 E-.09147
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X166.441 Y145.514 Z.6 F30000
G1 X166.757 Y152.38 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X166.718 Y152.38 E.00147
G3 X165.353 Y152.135 I-.282 J-2.351 E.05242
G1 X164.43 Y151.597 E.03979
G2 X156.049 Y150.915 I-4.984 J9.403 E.32199
G2 X153.542 Y152.133 I4.176 J11.777 E.10403
G3 X150.123 Y150.451 I-1.085 J-2.109 E.1648
G3 X150.089 Y149.32 I6.397 J-.759 E.04217
G3 X151.555 Y147.156 I2.401 J.048 E.10293
G1 X165.589 Y141.55 E.56288
G3 X166.334 Y141.391 I1.023 J2.971 E.02845
G3 X168.803 Y143.727 I.109 J2.358 E.14136
G1 X168.803 Y150.064 E.23601
G3 X167.111 Y152.298 I-2.368 J-.035 E.11171
G1 X166.816 Y152.366 E.0113
M204 S6000
G1 X166.665 Y151.927 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X165.564 Y151.729 I-.228 J-1.895 E.04228
G1 X164.644 Y151.193 E.03967
G2 X155.903 Y150.481 I-5.198 J9.807 E.33583
G2 X153.329 Y151.728 I4.306 J12.165 E.10674
G3 X150.574 Y150.371 I-.874 J-1.7 E.13286
G3 X150.546 Y149.33 I5.96 J-.679 E.03884
G3 X151.734 Y147.577 I1.937 J.033 E.08343
G1 X165.749 Y141.978 E.56215
G3 X166.354 Y141.848 I.83 J2.392 E.02311
G3 X168.346 Y143.737 I.089 J1.901 E.11421
G1 X168.346 Y150.054 E.23529
G3 X166.725 Y151.919 I-1.909 J-.022 E.10011
; WIPE_START
G1 X166.504 Y151.945 E-.08449
M73 P7 R9
G1 X166.341 Y151.943 E-.06182
G1 X166.02 Y151.898 E-.1234
G1 X165.863 Y151.854 E-.06181
G1 X165.564 Y151.729 E-.123
G1 X164.87 Y151.324 E-.30547
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X157.268 Y150.646 Z.6 F30000
G1 X128.938 Y148.12 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X128.887 Y147.946 E.00677
G2 X126.381 Y129.005 I-5.231 J-8.944 E.90547
G1 X126.413 Y128.775 E.00864
G1 X158.728 Y127.858 E1.2041
G1 X159.158 Y127.876 E.01605
G1 X159.685 Y127.899 E.01964
G3 X169.87 Y138.639 I-.981 J11.129 E.60258
G1 X169.626 Y158.107 E.72517
G1 X169.395 Y158.141 E.00871
G2 X150.531 Y155.735 I-9.951 J2.867 E.8975
G1 X150.329 Y155.669 E.00791
G2 X147.571 Y150.344 I-5.859 J-.342 E.23445
G1 X145.549 Y149.1 E.08841
G1 X145.636 Y148.885 E.00864
G2 X144.881 Y148.473 I.538 J-1.882 E.42569
G1 X144.751 Y148.668 E.00875
G2 X142.683 Y148.147 I-2.509 J5.592 E.07984
G2 X144.026 Y146.019 I-1.116 J-2.192 E.09839
G1 X144.026 Y131.981 E.52285
G2 X141.688 Y129.643 I-2.378 J.039 E.13619
G1 X134.605 Y129.643 E.2638
G2 X132.536 Y133.096 I.033 J2.366 E.17928
G3 X133.754 Y135.603 I-10.558 J6.683 E.10403
G3 X133.072 Y143.984 I-10.086 J3.397 E.32199
G1 X132.536 Y144.904 E.03967
G2 X133.305 Y147.955 I2.097 J1.094 E.12821
G1 X133.242 Y148.143 E.00737
G1 X128.98 Y148.143 E.15874
; WIPE_START
G1 X128.887 Y147.946 E-.08305
G1 X129.61 Y147.485 E-.3259
G1 X130.327 Y146.935 E-.34335
G1 X130.342 Y146.921 E-.00769
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X131.632 Y139.398 Z.6 F30000
G1 X133.093 Y130.885 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X134.615 Y130.1 I1.543 J1.122 E.06616
G1 X141.678 Y130.1 E.26306
G3 X143.569 Y131.991 I-.026 J1.917 E.11024
G1 X143.569 Y146.009 E.5221
G3 X141.678 Y147.9 I-1.917 J-.026 E.11024
G1 X134.615 Y147.9 E.26306
G3 X132.941 Y145.117 I.02 J-1.907 E.14472
G1 X133.476 Y144.198 E.03961
M73 P8 R9
G2 X134.188 Y135.457 I-9.808 J-5.198 E.33583
G2 X132.941 Y132.883 I-12.164 J4.306 E.10674
G3 X133.058 Y130.934 I1.695 J-.876 E.07633
; WIPE_START
G1 X133.3 Y130.636 E-.14597
G1 X133.551 Y130.431 E-.12286
G1 X133.69 Y130.345 E-.06237
G1 X133.986 Y130.21 E-.12345
G1 X134.141 Y130.162 E-.06176
G1 X134.3 Y130.127 E-.06178
G1 X134.615 Y130.1 E-.12025
G1 X134.777 Y130.1 E-.06156
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X127.186 Y130.898 Z.6 F30000
G1 X116.671 Y132.002 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X123.569 Y129.104 I6.998 J6.998 E.28577
G3 X129.263 Y130.836 I.125 J9.814 E.22523
G3 X116.629 Y132.045 I-5.594 J8.164 E1.80286
; WIPE_START
G1 X117.305 Y131.416 E-.35092
G1 X117.99 Y130.89 E-.32817
G1 X118.17 Y130.776 E-.08091
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X121.905 Y137.432 Z.6 F30000
G1 X128.173 Y148.6 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X116.892 Y147.15 I-4.489 J-9.688 E.44676
G3 X123.377 Y128.404 I6.792 J-8.145 E.95498
G1 X158.731 Y127.4 E1.31734
G1 X159.178 Y127.419 E.01666
G1 X159.724 Y127.443 E.02037
G3 X170.328 Y138.624 I-1.021 J11.586 E.62734
G1 X170.045 Y161.125 E.83812
; object ids of layer 1 start: 795,817,839,861
M624 DwAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer1 end: 795,817,839,861
M625
G3 X149.252 Y158.096 I-10.598 J-.129 E1.34486
G1 X149.683 Y156.797 E.05098
G2 X147.323 Y150.728 I-5.218 J-1.464 E.26016
G1 X145.157 Y149.396 E.09471
G2 X142.343 Y148.6 I-2.851 J4.706 E.11024
G1 X128.233 Y148.6 E.52554
M204 S6000
G1 X128.678 Y148.046 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.285224
G1 F3000
M204 S500
G1 X128.081 Y148.254 E.01248
G3 X113.984 Y135.654 I-4.409 J-9.253 E.47522
G3 X124.117 Y128.751 I9.744 J3.415 E.25919
; LINE_WIDTH: 0.33742
G1 X124.559 Y128.754 E.01061
; LINE_WIDTH: 0.377338
M73 P9 R9
G1 X124.867 Y128.77 E.00842
; LINE_WIDTH: 0.425418
G1 X125.162 Y128.785 E.00921
; LINE_WIDTH: 0.472429
G1 X125.457 Y128.8 E.01034
; LINE_WIDTH: 0.51547
G3 X125.708 Y128.824 I-.403 J5.663 E.00969
; LINE_WIDTH: 0.550987
G1 X125.938 Y128.846 E.00959
; LINE_WIDTH: 0.584997
G1 X126.169 Y128.868 E.01023
; WIPE_START
G1 X125.938 Y128.846 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X132.013 Y132.125 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.116842
G1 F3000
M204 S500
G1 X132.009 Y132.249 E.00075
; LINE_WIDTH: 0.144681
G1 X132.005 Y132.373 E.00103
; LINE_WIDTH: 0.16226
G1 X132.007 Y132.493 E.00117
; WIPE_START
G1 X132.005 Y132.373 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X133.091 Y128.768 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50122
G1 F6300
M204 S500
G1 X133.734 Y129.411 E.03394
G2 X133.279 Y129.605 I.526 J1.858 E.01849
G1 X132.661 Y128.986 E.03268
G1 X132.03 Y129.004 E.02355
G1 X132.895 Y129.868 E.04563
G1 X132.563 Y130.185 E.01712
G1 X131.4 Y129.022 E.06141
G1 X130.77 Y129.04 E.02355
G1 X132.293 Y130.563 E.08045
G2 X132.077 Y130.995 I1.141 J.841 E.01813
G1 X130.14 Y129.058 E.10231
G1 X129.51 Y129.076 E.02355
G1 X131.927 Y131.493 E.12765
G1 X131.9 Y131.733 E.00904
G1 X131.578 Y131.724 E.01202
G1 X131.578 Y131.739 E.00057
G1 X131.268 Y131.401 E.0171
G1 X130.475 Y130.69 E.03977
G1 X128.879 Y129.094 E.0843
G1 X128.249 Y129.112 E.02355
G1 X129.131 Y129.994 E.04658
; WIPE_START
G1 X128.249 Y129.112 E-.47397
G1 X128.879 Y129.094 E-.23959
G1 X128.966 Y129.18 E-.04644
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X134.188 Y129.108 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.699063
G1 F3000
M204 S500
G3 X135.972 Y129.074 I1.695 J42.094 E.09542
; LINE_WIDTH: 0.736788
G1 X137.344 Y129.054 E.07758
; WIPE_START
G1 X135.972 Y129.074 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X143.582 Y128.491 Z.6 F30000
G1 X144.002 Y128.459 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50537
G1 F6300
M204 S500
G1 X144.71 Y129.166 E.03773
G1 X144.376 Y129.486 E.01743
G1 X143.566 Y128.677 E.04313
G1 X142.93 Y128.695 E.02397
G1 X144.112 Y129.877 E.06299
G2 X143.924 Y130.342 I1.218 J.765 E.01902
G1 X142.294 Y128.713 E.08683
G1 X141.658 Y128.731 E.02397
G1 X142.245 Y129.317 E.03124
G2 X141.528 Y129.255 I-.73 J4.25 E.02712
G1 X141.023 Y128.749 E.02696
G1 X140.387 Y128.767 E.02397
G1 X140.875 Y129.256 E.02603
G1 X140.222 Y129.256 E.02462
G1 X139.751 Y128.785 E.02511
G1 X139.115 Y128.803 E.02397
G1 X139.569 Y129.257 E.02419
G1 X138.915 Y129.258 E.02462
G1 X138.479 Y128.821 E.02326
G1 X137.843 Y128.839 E.02397
G1 X138.467 Y129.464 E.03329
; WIPE_START
G1 X137.843 Y128.839 E-.33564
G1 X138.479 Y128.821 E-.24176
G1 X138.819 Y129.161 E-.1826
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X144.255 Y132.194 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.150924
G1 F3000
M204 S500
G1 X144.335 Y132.282 E.00104
; LINE_WIDTH: 0.123753
G1 X144.469 Y132.416 E.00125
; WIPE_START
G1 X144.335 Y132.282 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X148.089 Y132.1 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.123279
G1 F3000
M204 S500
G1 X148.196 Y131.947 E.00122
; LINE_WIDTH: 0.157859
G1 X148.24 Y131.878 E.00078
; LINE_WIDTH: 0.185882
G1 X148.282 Y131.811 E.00091
; LINE_WIDTH: 0.173781
G1 X148.307 Y131.664 E.00159
; LINE_WIDTH: 0.135978
G1 X148.322 Y131.564 E.00077
; LINE_WIDTH: 0.111795
G1 X148.334 Y131.452 E.00063
M204 S6000
G1 X148.334 Y130.548 F30000
; LINE_WIDTH: 0.115374
G1 F3000
M204 S500
G1 X148.322 Y130.425 E.00073
; LINE_WIDTH: 0.145085
G1 X148.307 Y130.316 E.00091
; LINE_WIDTH: 0.168943
G3 X148.324 Y130.246 I.074 J-.019 E.00077
; LINE_WIDTH: 0.130636
G1 X148.345 Y130.218 E.00025
; LINE_WIDTH: 0.108269
G1 X148.363 Y130.15 E.00038
; WIPE_START
G1 X148.345 Y130.218 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X149.404 Y128.663 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.12093
G1 F3000
M204 S500
G1 X149.542 Y128.566 E.00107
; LINE_WIDTH: 0.155571
G1 X149.624 Y128.514 E.00089
; LINE_WIDTH: 0.18845
G1 X149.702 Y128.465 E.0011
; LINE_WIDTH: 0.213437
G3 X149.883 Y128.413 I.173 J.264 E.00266
; LINE_WIDTH: 0.175315
G1 X150.072 Y128.389 E.00205
; LINE_WIDTH: 0.155958
G1 X150.422 Y128.368 E.00324
G1 X152.083 Y128.345 E.0153
; LINE_WIDTH: 0.205974
G1 X153.743 Y128.321 E.02206
; LINE_WIDTH: 0.253113
G1 X155.404 Y128.298 E.02844
; LINE_WIDTH: 0.300252
G1 X157.064 Y128.274 E.03482
; LINE_WIDTH: 0.347391
G1 X158.725 Y128.25 E.0412
; LINE_WIDTH: 0.351103
G1 X159.653 Y128.27 E.02333
; LINE_WIDTH: 0.311536
G1 X159.961 Y128.29 E.00674
; LINE_WIDTH: 0.272066
G1 X160.268 Y128.31 E.00575
; LINE_WIDTH: 0.232595
G1 X160.576 Y128.33 E.00476
; LINE_WIDTH: 0.194541
G1 X160.757 Y128.349 E.00225
; LINE_WIDTH: 0.157893
G1 X160.937 Y128.368 E.0017
; LINE_WIDTH: 0.121244
G1 X161.118 Y128.388 E.00116
; WIPE_START
G1 X160.937 Y128.368 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X162.859 Y128.933 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.128198
G1 F3000
M204 S500
G3 X163.21 Y129.163 I-5.429 J8.699 E.00292
M204 S6000
G1 X163.151 Y129.192 F30000
; LINE_WIDTH: 0.201417
G1 F3000
M204 S500
G1 X163.033 Y128.977 E.00317
M204 S6000
G1 X163.151 Y129.192 F30000
; LINE_WIDTH: 0.156446
G1 F3000
M204 S500
G1 X163.194 Y129.274 E.00086
; LINE_WIDTH: 0.121462
G1 X163.267 Y129.43 E.00111
; WIPE_START
G1 X163.194 Y129.274 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X167.803 Y132.865 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50184
G1 F6300
M204 S500
G1 X166.204 Y131.265 E.0846
G2 X163.826 Y129.536 I-7.273 J7.503 E.11031
G1 X168.191 Y133.902 E.23088
G1 X168.371 Y134.229 E.01396
G1 X168.761 Y135.12 E.03638
G1 X163.627 Y129.986 E.27152
G3 X163.692 Y130.7 I-2.858 J.62 E.02688
G1 X169.08 Y136.089 E.28497
G1 X169.14 Y136.329 E.00925
G2 X168.819 Y136.477 I.649 J1.829 E.01325
M73 P10 R9
G1 X163.692 Y131.349 E.27117
G1 X163.692 Y131.998 E.02427
G1 X167.898 Y136.205 E.22247
G2 X167.211 Y136.167 I-.502 J2.818 E.0258
G1 X163.692 Y132.647 E.18612
G1 X163.692 Y133.296 E.02427
G1 X166.684 Y136.289 E.15825
G2 X166.241 Y136.495 I.364 J1.358 E.01836
G1 X163.655 Y133.908 E.1368
G3 X163.5 Y134.403 I-1.954 J-.338 E.01944
G1 X165.868 Y136.771 E.12521
G2 X165.562 Y137.114 I.817 J1.038 E.01728
G1 X163.265 Y134.817 E.12147
G3 X162.956 Y135.157 I-1.614 J-1.158 E.01722
G1 X165.321 Y137.522 E.1251
G2 X165.158 Y138.008 I1.571 J.799 E.01923
G1 X162.586 Y135.436 E.13603
G1 X162.215 Y135.612 E.01537
G1 X162.135 Y135.634 E.00309
G1 X165.34 Y138.839 E.16949
; WIPE_START
G1 X163.926 Y137.424 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.032 Y139.935 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X169.46 Y140.363 E.02263
G1 X169.452 Y141.004 E.02397
G1 X168.836 Y140.387 E.03261
G1 X168.43 Y140.631 E.01769
G1 X169.444 Y141.645 E.05362
G1 X169.436 Y142.286 E.02397
G1 X167.938 Y140.788 E.0792
G3 X167.34 Y140.839 I-.443 J-1.671 E.02257
G1 X169.42 Y142.919 E.11
; WIPE_START
G1 X168.006 Y141.505 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X167.162 Y141.31 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X161.592 Y135.739 E.2946
G1 X160.943 Y135.74 E.02426
G1 X166.217 Y141.014 E.27895
G2 X165.673 Y141.119 I.04 J1.679 E.02083
G1 X160.294 Y135.74 E.28445
G1 X159.646 Y135.74 E.02426
G1 X165.194 Y141.289 E.29345
G1 X164.731 Y141.474 E.01868
G1 X158.997 Y135.741 E.30322
G1 X158.348 Y135.741 E.02426
G1 X164.267 Y141.66 E.313
G1 X163.803 Y141.845 E.01868
G1 X157.7 Y135.742 E.32278
G1 X157.051 Y135.742 E.02426
G1 X163.339 Y142.03 E.33256
G1 X162.876 Y142.215 E.01868
G1 X156.402 Y135.742 E.34234
G1 X155.754 Y135.743 E.02426
G1 X162.412 Y142.401 E.35212
G1 X161.948 Y142.586 E.01868
G1 X155.105 Y135.743 E.3619
G1 X154.456 Y135.743 E.02426
G1 X161.484 Y142.771 E.37168
G1 X161.021 Y142.956 E.01867
G1 X153.808 Y135.744 E.38145
M73 P11 R9
G1 X153.159 Y135.744 E.02426
G1 X160.557 Y143.142 E.39123
G1 X160.093 Y143.327 E.01868
G1 X152.51 Y135.744 E.40101
G1 X151.862 Y135.745 E.02426
G1 X159.629 Y143.512 E.41079
G1 X159.166 Y143.697 E.01867
G1 X153.785 Y138.317 E.28456
G3 X153.752 Y138.933 I-2.595 J.168 E.02311
G1 X158.702 Y143.883 E.2618
G1 X158.238 Y144.068 E.01867
G1 X153.595 Y139.425 E.24553
G3 X153.362 Y139.841 I-1.29 J-.45 E.01792
G1 X157.774 Y144.253 E.23334
G1 X157.311 Y144.439 E.01868
G1 X153.066 Y140.194 E.22448
G3 X152.7 Y140.477 I-.986 J-.897 E.01739
G1 X156.847 Y144.624 E.21931
G1 X156.383 Y144.809 E.01868
G1 X152.265 Y140.691 E.21779
G3 X151.747 Y140.822 I-.63 J-1.403 E.02008
G1 X155.919 Y144.994 E.22066
G1 X155.456 Y145.18 E.01868
G1 X150.822 Y140.546 E.24507
; WIPE_START
G1 X152.236 Y141.96 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X149.254 Y134.934 Z.6 F30000
G1 X148.407 Y132.939 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X147.972 Y132.504 E.02305
G1 X147.643 Y132.824 E.01716
G1 X148.412 Y133.593 E.04071
; WIPE_START
G1 X147.643 Y132.824 E-.41367
G1 X147.972 Y132.504 E-.1744
G1 X148.291 Y132.823 E-.17192
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X151.008 Y135.54 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X151.629 Y136.161 E.03285
G2 X151.019 Y136.2 I-.191 J1.763 E.02295
G1 X150.353 Y135.534 E.03525
; WIPE_START
G1 X151.019 Y136.2 E-.35817
G1 X151.241 Y136.161 E-.08562
G1 X151.629 Y136.161 E-.14725
G1 X151.314 Y135.846 E-.16896
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X150.679 Y136.509 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X149.828 Y135.658 E.04501
G3 X148.295 Y134.125 I.646 J-2.178 E.08449
G1 X147.25 Y133.08 E.05527
G3 X146.786 Y133.265 I-.942 J-1.691 E.01874
G1 X150.099 Y136.578 E.17519
G2 X149.751 Y136.879 I.973 J1.47 E.01725
G1 X146.211 Y133.339 E.18724
G3 X145.457 Y133.234 I-.017 J-2.636 E.02858
G1 X149.469 Y137.246 E.2122
G1 X149.413 Y137.326 E.00366
G1 X149.25 Y137.676 E.01443
G1 X144.505 Y132.931 E.25096
G1 X144.425 Y133.01 E.00419
G1 X144.407 Y132.991 E.00097
G1 X144.407 Y133.482 E.01836
G1 X149.124 Y138.199 E.24946
G2 X149.134 Y138.858 I1.94 J.3 E.02477
G1 X144.408 Y134.132 E.24998
G1 X144.408 Y134.781 E.02429
G1 X154.992 Y145.365 E.55974
M73 P12 R9
G1 X154.528 Y145.55 E.01867
G1 X144.408 Y135.43 E.53519
G1 X144.409 Y136.08 E.02429
G1 X154.064 Y145.735 E.51065
G1 X153.601 Y145.921 E.01868
G1 X144.409 Y136.729 E.4861
G1 X144.41 Y137.379 E.02428
G1 X153.137 Y146.106 E.46155
G1 X152.673 Y146.291 E.01867
G1 X144.41 Y138.028 E.43701
G1 X144.41 Y138.677 E.02428
G1 X152.209 Y146.476 E.41246
G1 X151.746 Y146.662 E.01868
G1 X144.411 Y139.327 E.38792
G1 X144.411 Y139.976 E.02428
G1 X151.29 Y146.855 E.36379
G2 X150.874 Y147.088 I.719 J1.765 E.01787
G1 X144.411 Y140.626 E.3418
G1 X144.412 Y141.275 E.02428
G1 X150.522 Y147.385 E.32312
G1 X150.222 Y147.734 E.01721
G1 X144.412 Y141.924 E.30728
G1 X144.413 Y142.574 E.02428
G1 X146.527 Y144.688 E.11184
G1 X146.37 Y144.661 E.00597
G1 X145.964 Y144.661 E.01517
G1 X145.868 Y144.678 E.00366
G1 X144.413 Y143.223 E.07696
G1 X144.413 Y143.872 E.02428
G1 X145.345 Y144.804 E.04926
G1 X144.995 Y144.967 E.01442
G1 X144.915 Y145.023 E.00367
G1 X144.208 Y144.316 E.03739
; WIPE_START
G1 X144.915 Y145.023 E-.37994
G1 X144.995 Y144.967 E-.03725
G1 X145.345 Y144.804 E-.14654
G1 X144.98 Y144.439 E-.19626
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X148.215 Y146.376 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X149.979 Y148.14 E.09333
G2 X149.805 Y148.616 I1.866 J.952 E.01897
G1 X148.491 Y147.301 E.06951
G3 X148.365 Y147.824 I-2.444 J-.311 E.02016
G1 X149.712 Y149.171 E.07124
G2 X149.701 Y149.809 I3.652 J.385 E.02387
G1 X148.148 Y148.257 E.0821
G3 X147.863 Y148.62 I-1.524 J-.902 E.01734
G1 X150.02 Y150.778 E.11411
; WIPE_START
G1 X148.606 Y149.363 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X151.725 Y152.482 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X152.175 Y152.932 E.02378
G1 X152.171 Y153.07 E.00516
G1 X152.205 Y153.073 E.0013
G1 X151.924 Y153.33 E.01425
G1 X147.516 Y148.923 E.23311
G1 X147.096 Y149.152 E.01789
G1 X151.607 Y153.663 E.23857
G1 X151.297 Y154.001 E.01718
G1 X150.269 Y152.974 E.05435
G3 X150.572 Y153.925 I-6.376 J2.549 E.03736
G1 X151.154 Y154.508 E.03082
M204 S6000
G1 X150.588 Y154.955 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.114214
M73 P13 R9
G1 F3000
M204 S500
G3 X150.588 Y155.181 I-.28 J.113 E.00135
M204 S6000
G1 X150.366 Y155.921 F30000
; LINE_WIDTH: 0.499445
G1 F3000
M204 S500
G1 X150.286 Y156.168 E.00964
; LINE_WIDTH: 0.453298
G1 X150.207 Y156.414 E.00866
; LINE_WIDTH: 0.427787
G1 X150.201 Y156.43 E.00053
; LINE_WIDTH: 0.411316
G1 X150.161 Y156.537 E.00343
; LINE_WIDTH: 0.381497
G1 X150.117 Y156.657 E.00354
; LINE_WIDTH: 0.345656
G1 X150.037 Y156.904 E.00639
; LINE_WIDTH: 0.285834
G2 X149.716 Y164.21 I9.676 J4.085 E.14785
G1 X149.817 Y164.499 E.00607
G2 X151.051 Y166.873 I10.023 J-3.705 E.05309
; LINE_WIDTH: 0.284804
G2 X169.697 Y160.995 I8.397 J-5.875 E.51134
; LINE_WIDTH: 0.311059
G1 X169.683 Y160.111 E.01932
; LINE_WIDTH: 0.336533
G1 X169.683 Y160.098 E.00031
; LINE_WIDTH: 0.358336
G1 X169.665 Y159.803 E.00759
; LINE_WIDTH: 0.400654
G1 X169.648 Y159.509 E.00861
; LINE_WIDTH: 0.444323
G2 X169.629 Y159.195 I-7.155 J.276 E.01027
; LINE_WIDTH: 0.489487
G1 X169.6 Y158.914 E.0103
; LINE_WIDTH: 0.533295
G1 X169.571 Y158.632 E.01131
; LINE_WIDTH: 0.577102
G1 X169.542 Y158.35 E.01232
; WIPE_START
G1 X169.571 Y158.632 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.402 Y157.288 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.43924
G1 F3000
M204 S500
G1 X169.152 Y156.127 E.03833
; WIPE_START
G1 X169.402 Y157.288 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.518 Y152.187 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.55081
G1 F6300
M204 S500
G1 X168.792 Y151.461 E.04249
G3 X168.487 Y151.874 I-1.37 J-.691 E.02136
G1 X169.306 Y152.693 E.04791
G1 X169.297 Y153.402 E.02936
G1 X168.113 Y152.219 E.06928
G3 X167.671 Y152.494 I-1.015 J-1.136 E.02169
G1 X169.288 Y154.111 E.09466
G1 X169.279 Y154.821 E.02936
G1 X167.15 Y152.692 E.12459
G3 X166.713 Y152.776 I-.627 J-2.076 E.01846
G1 X166.719 Y152.979 E.0084
G1 X169.473 Y155.733 E.16119
; WIPE_START
G1 X168.059 Y154.319 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X166.321 Y152.656 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.11656
G1 F3000
M204 S500
G1 X166.199 Y152.66 E.00073
; LINE_WIDTH: 0.152875
G1 X165.954 Y152.662 E.0022
; WIPE_START
G1 X166.199 Y152.66 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.195 Y150.943 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.560072
G1 F3000
M204 S500
G1 X169.241 Y150.54 E.01712
; LINE_WIDTH: 0.528475
G2 X169.258 Y150.297 I-5.589 J-.527 E.00962
G1 X169.265 Y150.079 E.00864
G2 X169.285 Y146.896 I-147.842 J-2.523 E.12595
; LINE_WIDTH: 0.569184
G1 X169.305 Y143.722 E.13608
; LINE_WIDTH: 0.603834
G2 X169.279 Y143.11 I-9.489 J.091 E.02803
; WIPE_START
G1 X169.305 Y143.722 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.366 Y139.6 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.12575
G1 F3000
M204 S500
G1 X169.48 Y139.435 E.00135
; LINE_WIDTH: 0.17278
G2 X169.565 Y139.274 I-.52 J-.375 E.00193
G1 X169.581 Y139.173 E.00108
; LINE_WIDTH: 0.136773
G1 X169.596 Y139.078 E.00074
; LINE_WIDTH: 0.112674
G1 X169.611 Y138.953 E.00071
; WIPE_START
G1 X169.596 Y139.078 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.554 Y137.831 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.111803
G1 F3000
M204 S500
G1 X169.532 Y137.722 E.00063
; LINE_WIDTH: 0.144228
G1 X169.482 Y137.548 E.0015
; LINE_WIDTH: 0.180811
G1 X169.452 Y137.456 E.00109
; LINE_WIDTH: 0.226288
G2 X169.194 Y136.727 I-16.796 J5.52 E.01155
M204 S6000
G1 X169.173 Y136.741 F30000
; LINE_WIDTH: 0.31121
G1 F3000
M204 S500
G1 X169.572 Y137.723 E.02317
M204 S6000
G1 X169.554 Y137.61 F30000
; LINE_WIDTH: 0.418351
G1 F3000
M204 S500
G2 X169.156 Y136.753 I-20.492 J9.006 E.02893
; WIPE_START
G1 X169.554 Y137.61 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X162.55 Y134.578 Z.6 F30000
G1 X148.139 Y128.341 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5506
G1 F6300
M204 S500
G1 X148.789 Y128.991 E.03805
G2 X148.49 Y129.41 I1.039 J1.059 E.0214
G1 X147.441 Y128.361 E.06139
M204 S6000
G1 X147.057 Y128.697 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.518691
G1 F3000
M204 S500
G2 X146.786 Y128.659 I-.988 J6.174 E.01061
; LINE_WIDTH: 0.487321
G1 X146.594 Y128.641 E.00696
; LINE_WIDTH: 0.433321
G1 X146.162 Y128.629 E.01376
; LINE_WIDTH: 0.421483
G1 X145.747 Y128.653 E.01283
; LINE_WIDTH: 0.459344
G1 X145.537 Y128.679 E.00716
; LINE_WIDTH: 0.500689
G1 X145.153 Y128.744 E.01455
; WIPE_START
G1 X145.537 Y128.679 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X145.056 Y136.297 Z.6 F30000
G1 X144.47 Y145.583 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.123824
G1 F3000
M204 S500
G1 X144.335 Y145.718 E.00126
; LINE_WIDTH: 0.151055
G1 X144.255 Y145.806 E.00105
; WIPE_START
G1 X144.335 Y145.718 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X143.971 Y147.216 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.567242
M73 P13 R8
G1 F3000
M204 S500
G1 X143.86 Y147.832 E.02673
G2 X144.305 Y148.244 I11.042 J-11.467 E.02595
; WIPE_START
G1 X143.86 Y147.832 E-.37434
G1 X143.971 Y147.216 E-.38566
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X142.394 Y148.029 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.122442
G1 F3000
M204 S500
G1 X142.231 Y148.105 E.00117
; LINE_WIDTH: 0.158715
G1 X142.144 Y148.141 E.00089
; LINE_WIDTH: 0.206635
G3 X141.559 Y148.372 I-5.808 J-13.903 E.00839
M204 S6000
G1 X142.129 Y148.229 F30000
; LINE_WIDTH: 0.286908
G1 F3000
M204 S500
G1 X141.683 Y148.25 E.00889
G1 X134.61 Y148.25 E.14062
G1 X134.232 Y148.233 E.00753
; LINE_WIDTH: 0.340589
G1 X134.036 Y148.212 E.00478
; LINE_WIDTH: 0.375913
G1 X133.945 Y148.198 E.0025
; LINE_WIDTH: 0.405876
G1 X133.838 Y148.182 E.00321
; LINE_WIDTH: 0.435524
G1 X133.665 Y148.148 E.00562
; LINE_WIDTH: 0.461171
G1 X133.493 Y148.114 E.00599
M204 S6000
G1 X132.946 Y147.96 F30000
; FEATURE: Bottom surface
; LINE_WIDTH: 0.55699
G1 F6300
M204 S500
G1 X131.419 Y146.434 E.09042
G3 X131.054 Y146.796 I-2.248 J-1.908 E.02156
G1 X132.013 Y147.755 E.05682
G1 X131.286 Y147.755 E.03045
G1 X130.529 Y146.998 E.04485
M204 S6000
G1 X130.159 Y147.674 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.309554
G1 F3000
M204 S500
G1 X129.437 Y147.901 E.01643
; WIPE_START
G1 X130.159 Y147.674 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X132.013 Y145.875 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.116538
G1 F3000
M204 S500
G1 X132.009 Y145.753 E.00073
; LINE_WIDTH: 0.143786
G1 X132.006 Y145.632 E.001
; LINE_WIDTH: 0.161683
G1 X132.007 Y145.508 E.0012
; WIPE_START
G1 X132.006 Y145.632 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X139.402 Y147.515 Z.6 F30000
G1 X146.239 Y149.257 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.152316
G1 F3000
M204 S500
G1 X146.362 Y149.229 E.00112
; LINE_WIDTH: 0.123811
G1 X146.546 Y149.18 E.00126
; WIPE_START
G1 X146.362 Y149.229 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X152.572 Y152.656 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.116827
G1 F3000
M204 S500
G1 X152.695 Y152.66 E.00074
; LINE_WIDTH: 0.144631
G1 X152.819 Y152.664 E.00102
; LINE_WIDTH: 0.162201
G1 X152.939 Y152.662 E.00116
; OBJECT_ID: 861
; WIPE_START
G1 X152.819 Y152.664 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 795
M625
; start printing object, unique label id: 861
M624 CAAAAAAAAAA=
M204 S6000
G1 X152.049 Y145.07 Z.6 F30000
G1 X147.394 Y99.146 Z.6
G1 Z.2
M73 P14 R8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G3 X146.038 Y98.509 I-1.23 J.857 E.29253
G1 X146.158 Y98.503 E.00445
G3 X147.359 Y99.097 I.006 J1.5 E.05172
; WIPE_START
G1 X147.529 Y99.369 E-.12194
G1 X147.618 Y99.613 E-.09879
G1 X147.664 Y99.873 E-.10002
G1 X147.664 Y100.134 E-.09934
G1 X147.58 Y100.515 E-.14823
G1 X147.468 Y100.753 E-.09998
G1 X147.33 Y100.951 E-.0917
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X150.107 Y108.06 Z.6 F30000
G1 X156.061 Y123.303 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X159.346 Y104.107 I3.385 J-9.3 E1.02561
G3 X165.04 Y105.839 I.125 J9.814 E.22523
G3 X156.118 Y123.323 I-5.594 J8.164 E1.06301
; WIPE_START
G1 X155.262 Y122.976 E-.35094
G1 X154.496 Y122.577 E-.32817
G1 X154.316 Y122.463 E-.0809
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X153.354 Y114.891 Z.6 F30000
G1 X150.192 Y90.009 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X150.321 Y89.897 E.00637
G3 X151.276 Y89.553 I1.118 J1.606 E.03821
G1 X151.433 Y89.546 E.00588
G3 X150.059 Y90.116 I.007 J1.957 E.4011
G1 X150.146 Y90.047 E.00413
M204 S6000
G1 X150.48 Y90.352 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X151.315 Y90.009 I.961 J1.151 E.03417
G1 X151.435 Y90.003 E.00446
G3 X150.435 Y90.391 I.006 J1.5 E.31007
; WIPE_START
G1 X150.812 Y90.144 E-.17149
G1 X151.058 Y90.054 E-.09939
G1 X151.315 Y90.009 E-.09941
G1 X151.435 Y90.003 E-.04546
G1 X151.707 Y90.026 E-.1036
G1 X151.959 Y90.093 E-.09938
G1 X152.196 Y90.204 E-.09941
G1 X152.287 Y90.267 E-.04187
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X158.008 Y85.216 Z.6 F30000
G1 X161.965 Y81.722 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X162.229 Y81.825 E.01056
G3 X163.303 Y83.485 I-.799 J1.694 E.07758
G1 X163.303 Y86.522 E.11314
G3 X161.465 Y88.36 I-1.873 J-.035 E.10702
G1 X150.427 Y88.36 E.41111
G3 X148.589 Y86.522 I.035 J-1.873 E.10702
G1 X148.589 Y83.485 E.11314
G3 X150.427 Y81.646 I1.873 J.035 E.10702
G1 X161.465 Y81.646 E.41111
G3 X161.906 Y81.707 I-.035 J1.873 E.01664
M204 S6000
G1 X161.808 Y82.154 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X162.846 Y83.495 I-.374 J1.362 E.06775
G1 X162.846 Y86.512 E.11239
G3 X161.455 Y87.903 I-1.412 J-.021 E.08106
G1 X150.437 Y87.903 E.41036
G3 X149.046 Y86.512 I.021 J-1.412 E.08106
G1 X149.046 Y83.494 E.1124
G3 X150.437 Y82.103 I1.412 J.021 E.08106
G1 X161.455 Y82.103 E.41036
G3 X161.75 Y82.139 I-.021 J1.412 E.01108
; WIPE_START
G1 X162.038 Y82.234 E-.11532
G1 X162.249 Y82.356 E-.09271
G1 X162.436 Y82.513 E-.09281
G1 X162.593 Y82.7 E-.09275
G1 X162.715 Y82.911 E-.09272
G1 X162.799 Y83.141 E-.09279
G1 X162.846 Y83.495 E-.13559
G1 X162.846 Y83.614 E-.04531
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X155.238 Y83.005 Z.6 F30000
G1 X145.379 Y82.215 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X145.662 Y82.111 E.01123
G3 X145.998 Y82.053 I.501 J1.892 E.01273
G1 X146.156 Y82.046 E.00588
G3 X145.323 Y82.235 I.007 J1.957 E.42586
M204 S6000
G1 X145.534 Y82.642 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X146.038 Y82.509 I.629 J1.361 E.01952
G1 X146.158 Y82.503 E.00446
G3 X145.481 Y82.668 I.006 J1.5 E.32473
; WIPE_START
G1 X145.781 Y82.554 E-.12201
G1 X146.038 Y82.509 E-.09942
M73 P15 R8
G1 X146.158 Y82.503 E-.04546
G1 X146.43 Y82.526 E-.10359
G1 X146.682 Y82.593 E-.09939
G1 X146.919 Y82.704 E-.09941
G1 X147.133 Y82.854 E-.09937
G1 X147.303 Y83.024 E-.09136
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X154.051 Y86.592 Z.6 F30000
G1 X166.221 Y93.026 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X166.186 Y93.005 E.00151
G3 X167.276 Y89.553 I1.254 J-1.502 E.17216
G1 X167.433 Y89.546 E.00588
G3 X166.469 Y93.202 I.007 J1.957 E.26704
G1 X166.27 Y93.061 E.00912
M204 S6000
G1 X166.48 Y92.655 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X167.315 Y90.009 I.96 J-1.152 E.13197
G1 X167.435 Y90.003 E.00446
G3 X166.527 Y92.692 I.006 J1.5 E.21227
; WIPE_START
G1 X166.297 Y92.468 E-.12213
G1 X166.087 Y92.139 E-.14822
G1 X165.997 Y91.892 E-.09999
G1 X165.951 Y91.634 E-.0994
G1 X165.951 Y91.373 E-.09938
G1 X165.997 Y91.115 E-.09941
G1 X166.089 Y90.892 E-.09147
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X166.441 Y98.517 Z.6 F30000
G1 X166.757 Y105.383 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X166.718 Y105.383 E.00147
G3 X165.353 Y105.138 I-.282 J-2.351 E.05242
G1 X164.43 Y104.6 E.03979
G2 X156.049 Y103.918 I-4.984 J9.403 E.32199
G2 X153.542 Y105.137 I4.176 J11.777 E.10403
G3 X150.123 Y103.454 I-1.085 J-2.109 E.1648
G3 X150.089 Y102.323 I6.397 J-.759 E.04217
G3 X151.555 Y100.159 I2.401 J.048 E.10293
G1 X165.589 Y94.553 E.56288
G3 X166.334 Y94.394 I1.023 J2.971 E.02845
G3 X168.803 Y96.731 I.109 J2.358 E.14136
G1 X168.803 Y103.067 E.23601
G3 X167.111 Y105.302 I-2.368 J-.035 E.11171
G1 X166.816 Y105.37 E.0113
M204 S6000
G1 X166.665 Y104.93 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X165.564 Y104.732 I-.228 J-1.895 E.04228
G1 X164.644 Y104.196 E.03967
G2 X155.903 Y103.484 I-5.198 J9.807 E.33583
G2 X153.329 Y104.732 I4.306 J12.165 E.10674
G3 X150.574 Y103.374 I-.874 J-1.7 E.13286
G3 X150.546 Y102.333 I5.96 J-.679 E.03884
G3 X151.734 Y100.58 I1.937 J.033 E.08343
G1 X165.749 Y94.981 E.56215
G3 X166.354 Y94.851 I.83 J2.392 E.02311
G3 X168.346 Y96.74 I.089 J1.901 E.11421
G1 X168.346 Y103.057 E.23529
G3 X166.725 Y104.922 I-1.909 J-.022 E.10011
; WIPE_START
G1 X166.504 Y104.948 E-.08449
G1 X166.341 Y104.946 E-.06182
G1 X166.02 Y104.901 E-.1234
G1 X165.863 Y104.858 E-.06181
G1 X165.564 Y104.732 E-.123
G1 X164.87 Y104.328 E-.30547
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X157.268 Y103.65 Z.6 F30000
G1 X128.938 Y101.123 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X128.887 Y100.949 E.00677
G2 X126.381 Y82.008 I-5.231 J-8.944 E.90547
G1 X126.413 Y81.778 E.00864
G1 X158.728 Y80.861 E1.2041
G1 X159.158 Y80.879 E.01605
G1 X159.685 Y80.902 E.01964
G3 X169.87 Y91.642 I-.981 J11.129 E.60258
G1 X169.626 Y111.11 E.72517
G1 X169.395 Y111.144 E.00871
G2 X150.531 Y108.738 I-9.951 J2.867 E.8975
M73 P16 R8
G1 X150.329 Y108.672 E.00791
G2 X147.571 Y103.347 I-5.859 J-.342 E.23445
G1 X145.549 Y102.104 E.08841
G1 X145.636 Y101.889 E.00864
G2 X144.881 Y101.476 I.538 J-1.882 E.42569
G1 X144.751 Y101.672 E.00875
G2 X142.683 Y101.15 I-2.509 J5.592 E.07984
G2 X144.026 Y99.022 I-1.116 J-2.192 E.09839
G1 X144.026 Y84.985 E.52285
G2 X141.688 Y82.646 I-2.378 J.039 E.13619
G1 X134.605 Y82.646 E.2638
G2 X132.536 Y86.099 I.033 J2.366 E.17928
G3 X133.754 Y88.606 I-10.558 J6.683 E.10403
G3 X133.072 Y96.987 I-10.086 J3.397 E.32199
G1 X132.536 Y97.907 E.03967
G2 X133.305 Y100.959 I2.097 J1.094 E.12821
G1 X133.242 Y101.146 E.00737
G1 X128.98 Y101.146 E.15874
; WIPE_START
G1 X128.887 Y100.949 E-.08305
G1 X129.61 Y100.488 E-.3259
G1 X130.327 Y99.938 E-.34335
G1 X130.342 Y99.924 E-.00769
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X131.632 Y92.402 Z.6 F30000
G1 X133.093 Y83.889 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X134.615 Y83.103 I1.543 J1.122 E.06616
G1 X141.678 Y83.103 E.26306
G3 X143.569 Y84.995 I-.026 J1.917 E.11024
G1 X143.569 Y99.012 E.5221
G3 X141.678 Y100.903 I-1.917 J-.026 E.11024
G1 X134.615 Y100.903 E.26306
G3 X132.941 Y98.12 I.02 J-1.907 E.14472
G1 X133.476 Y97.202 E.03961
G2 X134.188 Y88.46 I-9.808 J-5.198 E.33583
G2 X132.941 Y85.886 I-12.164 J4.306 E.10674
G3 X133.058 Y83.938 I1.695 J-.876 E.07633
; WIPE_START
G1 X133.3 Y83.639 E-.14597
G1 X133.551 Y83.435 E-.12286
G1 X133.69 Y83.348 E-.06237
G1 X133.986 Y83.213 E-.12345
G1 X134.141 Y83.165 E-.06176
G1 X134.3 Y83.131 E-.06178
G1 X134.615 Y83.103 E-.12025
G1 X134.777 Y83.103 E-.06156
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X127.186 Y83.901 Z.6 F30000
G1 X116.671 Y85.005 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X123.569 Y82.107 I6.998 J6.998 E.28577
G3 X129.263 Y83.839 I.125 J9.814 E.22523
G3 X116.629 Y85.048 I-5.594 J8.164 E1.80286
; WIPE_START
G1 X117.305 Y84.419 E-.35092
G1 X117.99 Y83.893 E-.32817
G1 X118.17 Y83.779 E-.08091
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X121.905 Y90.435 Z.6 F30000
G1 X128.173 Y101.603 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X116.892 Y100.154 I-4.489 J-9.688 E.44676
M73 P17 R8
G3 X123.377 Y81.407 I6.792 J-8.145 E.95498
G1 X158.731 Y80.404 E1.31734
G1 X159.178 Y80.423 E.01666
G1 X159.724 Y80.446 E.02037
G3 X170.328 Y91.627 I-1.021 J11.586 E.62734
G1 X170.045 Y114.128 E.83812
G3 X149.252 Y111.099 I-10.598 J-.129 E1.34486
G1 X149.683 Y109.8 E.05098
G2 X147.323 Y103.731 I-5.218 J-1.464 E.26016
G1 X145.157 Y102.399 E.09471
G2 X142.343 Y101.603 I-2.851 J4.706 E.11024
G1 X128.233 Y101.603 E.52554
M204 S6000
G1 X128.678 Y101.05 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.285224
G1 F3000
M204 S500
G1 X128.081 Y101.258 E.01248
G3 X113.984 Y88.657 I-4.409 J-9.253 E.47522
G3 X124.117 Y81.754 I9.744 J3.415 E.25919
; LINE_WIDTH: 0.33742
G1 X124.559 Y81.758 E.01061
; LINE_WIDTH: 0.377338
G1 X124.867 Y81.773 E.00842
; LINE_WIDTH: 0.425418
G1 X125.162 Y81.788 E.00921
; LINE_WIDTH: 0.472429
G1 X125.457 Y81.803 E.01034
; LINE_WIDTH: 0.51547
G3 X125.708 Y81.827 I-.403 J5.663 E.00969
; LINE_WIDTH: 0.550987
G1 X125.938 Y81.849 E.00959
; LINE_WIDTH: 0.584997
G1 X126.169 Y81.871 E.01023
; WIPE_START
G1 X125.938 Y81.849 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X132.013 Y85.129 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.116842
G1 F3000
M204 S500
G1 X132.009 Y85.252 E.00075
; LINE_WIDTH: 0.144681
G1 X132.005 Y85.376 E.00103
; LINE_WIDTH: 0.16226
G1 X132.007 Y85.496 E.00117
; WIPE_START
G1 X132.005 Y85.376 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X133.091 Y81.772 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50122
G1 F6300
M204 S500
G1 X133.734 Y82.414 E.03394
G2 X133.279 Y82.608 I.526 J1.858 E.01849
G1 X132.661 Y81.99 E.03268
G1 X132.03 Y82.007 E.02355
G1 X132.895 Y82.871 E.04563
G1 X132.563 Y83.188 E.01712
G1 X131.4 Y82.025 E.06141
G1 X130.77 Y82.043 E.02355
G1 X132.293 Y83.566 E.08045
G2 X132.077 Y83.998 I1.141 J.841 E.01813
G1 X130.14 Y82.061 E.10231
G1 X129.51 Y82.079 E.02355
G1 X131.927 Y84.496 E.12765
G1 X131.9 Y84.737 E.00904
G1 X131.578 Y84.727 E.01202
G1 X131.578 Y84.742 E.00057
G1 X131.268 Y84.404 E.0171
G1 X130.475 Y83.693 E.03977
G1 X128.879 Y82.097 E.0843
G1 X128.249 Y82.115 E.02355
G1 X129.131 Y82.997 E.04658
; WIPE_START
G1 X128.249 Y82.115 E-.47397
G1 X128.879 Y82.097 E-.23959
G1 X128.966 Y82.183 E-.04644
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X134.188 Y82.111 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.699063
M73 P18 R8
G1 F3000
M204 S500
G3 X135.972 Y82.077 I1.695 J42.094 E.09542
; LINE_WIDTH: 0.736788
G1 X137.344 Y82.057 E.07758
; WIPE_START
G1 X135.972 Y82.077 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X143.582 Y81.494 Z.6 F30000
G1 X144.002 Y81.462 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50537
G1 F6300
M204 S500
G1 X144.71 Y82.17 E.03773
G1 X144.376 Y82.489 E.01743
G1 X143.566 Y81.68 E.04313
G1 X142.93 Y81.698 E.02397
G1 X144.112 Y82.88 E.06299
G2 X143.924 Y83.345 I1.218 J.765 E.01902
G1 X142.294 Y81.716 E.08683
G1 X141.658 Y81.734 E.02397
G1 X142.245 Y82.32 E.03124
G2 X141.528 Y82.258 I-.73 J4.25 E.02712
G1 X141.023 Y81.752 E.02696
G1 X140.387 Y81.77 E.02397
G1 X140.875 Y82.259 E.02603
G1 X140.222 Y82.259 E.02462
G1 X139.751 Y81.788 E.02511
G1 X139.115 Y81.806 E.02397
G1 X139.569 Y82.26 E.02419
G1 X138.915 Y82.261 E.02462
G1 X138.479 Y81.824 E.02326
G1 X137.843 Y81.842 E.02397
G1 X138.467 Y82.467 E.03329
; WIPE_START
G1 X137.843 Y81.842 E-.33564
G1 X138.479 Y81.824 E-.24176
G1 X138.819 Y82.164 E-.1826
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X144.255 Y85.197 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.150924
G1 F3000
M204 S500
G1 X144.335 Y85.285 E.00104
; LINE_WIDTH: 0.123753
G1 X144.469 Y85.42 E.00125
; WIPE_START
G1 X144.335 Y85.285 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X148.089 Y85.103 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.123279
G1 F3000
M204 S500
G1 X148.196 Y84.951 E.00122
; LINE_WIDTH: 0.157859
G1 X148.24 Y84.881 E.00078
; LINE_WIDTH: 0.185882
G1 X148.282 Y84.815 E.00091
; LINE_WIDTH: 0.173781
G1 X148.307 Y84.667 E.00159
; LINE_WIDTH: 0.135978
G1 X148.322 Y84.567 E.00077
; LINE_WIDTH: 0.111795
G1 X148.334 Y84.455 E.00063
M204 S6000
G1 X148.334 Y83.551 F30000
; LINE_WIDTH: 0.115374
G1 F3000
M204 S500
G1 X148.322 Y83.428 E.00073
; LINE_WIDTH: 0.145085
G1 X148.307 Y83.32 E.00091
; LINE_WIDTH: 0.168943
G3 X148.324 Y83.249 I.074 J-.019 E.00077
; LINE_WIDTH: 0.130636
G1 X148.345 Y83.222 E.00025
; LINE_WIDTH: 0.108269
G1 X148.363 Y83.153 E.00038
; WIPE_START
G1 X148.345 Y83.222 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X149.404 Y81.666 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.12093
G1 F3000
M204 S500
G1 X149.542 Y81.57 E.00107
; LINE_WIDTH: 0.155571
G1 X149.624 Y81.518 E.00089
; LINE_WIDTH: 0.18845
G1 X149.702 Y81.468 E.0011
; LINE_WIDTH: 0.213437
G3 X149.883 Y81.416 I.173 J.264 E.00266
; LINE_WIDTH: 0.175315
G1 X150.072 Y81.393 E.00205
; LINE_WIDTH: 0.155958
G1 X150.422 Y81.372 E.00324
G1 X152.083 Y81.348 E.0153
; LINE_WIDTH: 0.205974
G1 X153.743 Y81.324 E.02206
; LINE_WIDTH: 0.253113
G1 X155.404 Y81.301 E.02844
; LINE_WIDTH: 0.300252
G1 X157.064 Y81.277 E.03482
; LINE_WIDTH: 0.347391
G1 X158.725 Y81.254 E.0412
; LINE_WIDTH: 0.351103
G1 X159.653 Y81.274 E.02333
; LINE_WIDTH: 0.311536
G1 X159.961 Y81.293 E.00674
; LINE_WIDTH: 0.272066
G1 X160.268 Y81.313 E.00575
; LINE_WIDTH: 0.232595
G1 X160.576 Y81.333 E.00476
; LINE_WIDTH: 0.194541
G1 X160.757 Y81.352 E.00225
; LINE_WIDTH: 0.157893
G1 X160.937 Y81.372 E.0017
; LINE_WIDTH: 0.121244
G1 X161.118 Y81.391 E.00116
; WIPE_START
G1 X160.937 Y81.372 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X162.859 Y81.937 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.128198
G1 F3000
M204 S500
G3 X163.21 Y82.166 I-5.429 J8.699 E.00292
M204 S6000
G1 X163.151 Y82.195 F30000
; LINE_WIDTH: 0.201417
G1 F3000
M204 S500
G1 X163.033 Y81.98 E.00317
M204 S6000
G1 X163.151 Y82.195 F30000
; LINE_WIDTH: 0.156446
G1 F3000
M204 S500
G1 X163.194 Y82.277 E.00086
; LINE_WIDTH: 0.121462
G1 X163.267 Y82.433 E.00111
; WIPE_START
G1 X163.194 Y82.277 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X167.803 Y85.868 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50184
G1 F6300
M204 S500
G1 X166.204 Y84.268 E.0846
G2 X163.826 Y82.54 I-7.273 J7.503 E.11031
G1 X168.191 Y86.905 E.23088
G1 X168.371 Y87.232 E.01396
G1 X168.761 Y88.124 E.03638
G1 X163.627 Y82.99 E.27152
G3 X163.692 Y83.703 I-2.858 J.62 E.02688
G1 X169.08 Y89.092 E.28497
G1 X169.14 Y89.332 E.00925
G2 X168.819 Y89.48 I.649 J1.829 E.01325
G1 X163.692 Y84.352 E.27117
G1 X163.692 Y85.002 E.02427
G1 X167.898 Y89.208 E.22247
G2 X167.211 Y89.17 I-.502 J2.818 E.0258
G1 X163.692 Y85.651 E.18612
G1 X163.692 Y86.3 E.02427
G1 X166.684 Y89.292 E.15825
G2 X166.241 Y89.498 I.364 J1.358 E.01836
G1 X163.655 Y86.912 E.1368
G3 X163.5 Y87.406 I-1.954 J-.338 E.01944
G1 X165.868 Y89.774 E.12521
G2 X165.562 Y90.117 I.817 J1.038 E.01728
G1 X163.265 Y87.82 E.12147
G3 X162.956 Y88.16 I-1.614 J-1.158 E.01722
G1 X165.321 Y90.525 E.1251
G2 X165.158 Y91.011 I1.571 J.799 E.01923
G1 X162.586 Y88.439 E.13603
G1 X162.215 Y88.616 E.01537
G1 X162.135 Y88.637 E.00309
G1 X165.34 Y91.842 E.16949
; WIPE_START
G1 X163.926 Y90.428 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.032 Y92.938 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X169.46 Y93.366 E.02263
G1 X169.452 Y94.007 E.02397
G1 X168.836 Y93.391 E.03261
G1 X168.43 Y93.634 E.01769
G1 X169.444 Y94.648 E.05362
M73 P19 R8
G1 X169.436 Y95.289 E.02397
G1 X167.938 Y93.791 E.0792
G3 X167.34 Y93.842 I-.443 J-1.671 E.02257
G1 X169.42 Y95.922 E.11
; WIPE_START
G1 X168.006 Y94.508 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X167.162 Y94.313 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X161.592 Y88.743 E.2946
G1 X160.943 Y88.743 E.02426
G1 X166.217 Y94.017 E.27895
G2 X165.673 Y94.122 I.04 J1.679 E.02083
G1 X160.294 Y88.743 E.28445
G1 X159.646 Y88.744 E.02426
G1 X165.194 Y94.292 E.29345
G1 X164.731 Y94.478 E.01868
G1 X158.997 Y88.744 E.30322
G1 X158.348 Y88.744 E.02426
G1 X164.267 Y94.663 E.313
G1 X163.803 Y94.848 E.01868
G1 X157.7 Y88.745 E.32278
G1 X157.051 Y88.745 E.02426
G1 X163.339 Y95.033 E.33256
G1 X162.876 Y95.219 E.01868
G1 X156.402 Y88.745 E.34234
G1 X155.754 Y88.746 E.02426
G1 X162.412 Y95.404 E.35212
G1 X161.948 Y95.589 E.01868
G1 X155.105 Y88.746 E.3619
G1 X154.456 Y88.747 E.02426
G1 X161.484 Y95.774 E.37168
G1 X161.021 Y95.96 E.01867
G1 X153.808 Y88.747 E.38145
G1 X153.159 Y88.747 E.02426
G1 X160.557 Y96.145 E.39123
G1 X160.093 Y96.33 E.01868
G1 X152.51 Y88.748 E.40101
G1 X151.862 Y88.748 E.02426
G1 X159.629 Y96.515 E.41079
G1 X159.166 Y96.701 E.01867
G1 X153.785 Y91.32 E.28456
G3 X153.752 Y91.936 I-2.595 J.168 E.02311
G1 X158.702 Y96.886 E.2618
G1 X158.238 Y97.071 E.01867
G1 X153.595 Y92.429 E.24553
G3 X153.362 Y92.844 I-1.29 J-.45 E.01792
G1 X157.774 Y97.256 E.23334
G1 X157.311 Y97.442 E.01868
G1 X153.066 Y93.197 E.22448
G3 X152.7 Y93.48 I-.986 J-.897 E.01739
G1 X156.847 Y97.627 E.21931
M73 P20 R8
G1 X156.383 Y97.812 E.01868
G1 X152.265 Y93.694 E.21779
G3 X151.747 Y93.825 I-.63 J-1.403 E.02008
G1 X155.919 Y97.998 E.22066
G1 X155.456 Y98.183 E.01868
G1 X150.822 Y93.549 E.24507
; WIPE_START
G1 X152.236 Y94.963 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X149.254 Y87.937 Z.6 F30000
G1 X148.407 Y85.943 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X147.972 Y85.507 E.02305
G1 X147.643 Y85.827 E.01716
G1 X148.412 Y86.596 E.04071
; WIPE_START
G1 X147.643 Y85.827 E-.41367
G1 X147.972 Y85.507 E-.1744
G1 X148.291 Y85.827 E-.17192
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X151.008 Y88.543 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X151.629 Y89.164 E.03285
G2 X151.019 Y89.204 I-.191 J1.763 E.02295
G1 X150.353 Y88.537 E.03525
; WIPE_START
G1 X151.019 Y89.204 E-.35817
G1 X151.241 Y89.165 E-.08562
G1 X151.629 Y89.164 E-.14725
G1 X151.314 Y88.85 E-.16896
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X150.679 Y89.512 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X149.828 Y88.661 E.04501
G3 X148.295 Y87.129 I.646 J-2.178 E.08449
G1 X147.25 Y86.084 E.05527
G3 X146.786 Y86.268 I-.942 J-1.691 E.01874
G1 X150.099 Y89.581 E.17519
G2 X149.751 Y89.883 I.973 J1.47 E.01725
G1 X146.211 Y86.342 E.18724
G3 X145.457 Y86.237 I-.017 J-2.636 E.02858
G1 X149.469 Y90.249 E.2122
G1 X149.413 Y90.329 E.00366
G1 X149.25 Y90.679 E.01443
G1 X144.505 Y85.934 E.25096
G1 X144.425 Y86.013 E.00419
G1 X144.407 Y85.994 E.00097
G1 X144.407 Y86.485 E.01836
G1 X149.124 Y91.202 E.24946
G2 X149.134 Y91.862 I1.94 J.3 E.02477
G1 X144.408 Y87.135 E.24998
G1 X144.408 Y87.784 E.02429
G1 X154.992 Y98.368 E.55974
G1 X154.528 Y98.553 E.01867
G1 X144.408 Y88.434 E.53519
G1 X144.409 Y89.083 E.02429
G1 X154.064 Y98.739 E.51065
G1 X153.601 Y98.924 E.01868
G1 X144.409 Y89.732 E.4861
G1 X144.41 Y90.382 E.02428
G1 X153.137 Y99.109 E.46155
G1 X152.673 Y99.294 E.01867
G1 X144.41 Y91.031 E.43701
G1 X144.41 Y91.681 E.02428
G1 X152.209 Y99.48 E.41246
G1 X151.746 Y99.665 E.01868
G1 X144.411 Y92.33 E.38792
G1 X144.411 Y92.979 E.02428
G1 X151.29 Y99.858 E.36379
M73 P21 R8
G2 X150.874 Y100.092 I.719 J1.765 E.01787
G1 X144.411 Y93.629 E.3418
G1 X144.412 Y94.278 E.02428
G1 X150.522 Y100.388 E.32312
G1 X150.222 Y100.738 E.01721
G1 X144.412 Y94.928 E.30728
G1 X144.413 Y95.577 E.02428
G1 X146.527 Y97.692 E.11184
G1 X146.37 Y97.664 E.00597
G1 X145.964 Y97.664 E.01517
G1 X145.868 Y97.681 E.00366
G1 X144.413 Y96.226 E.07696
G1 X144.413 Y96.876 E.02428
G1 X145.345 Y97.807 E.04926
G1 X144.995 Y97.97 E.01442
G1 X144.915 Y98.026 E.00367
G1 X144.208 Y97.319 E.03739
; WIPE_START
G1 X144.915 Y98.026 E-.37994
G1 X144.995 Y97.97 E-.03725
G1 X145.345 Y97.807 E-.14654
G1 X144.98 Y97.442 E-.19626
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X148.215 Y99.379 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X149.979 Y101.144 E.09333
G2 X149.805 Y101.619 I1.866 J.952 E.01897
G1 X148.491 Y100.304 E.06951
G3 X148.365 Y100.828 I-2.444 J-.311 E.02016
G1 X149.712 Y102.175 E.07124
G2 X149.701 Y102.812 I3.652 J.385 E.02387
G1 X148.148 Y101.26 E.0821
G3 X147.863 Y101.623 I-1.524 J-.902 E.01734
G1 X150.02 Y103.781 E.11411
; WIPE_START
G1 X148.606 Y102.367 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X151.725 Y105.485 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X152.175 Y105.935 E.02378
G1 X152.171 Y106.073 E.00516
G1 X152.205 Y106.076 E.0013
G1 X151.924 Y106.334 E.01425
G1 X147.516 Y101.926 E.23311
G1 X147.096 Y102.155 E.01789
G1 X151.607 Y106.666 E.23857
G1 X151.297 Y107.005 E.01718
G1 X150.269 Y105.977 E.05435
G3 X150.572 Y106.928 I-6.376 J2.549 E.03736
G1 X151.154 Y107.511 E.03082
M204 S6000
G1 X150.588 Y107.958 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.114214
G1 F3000
M204 S500
G3 X150.588 Y108.184 I-.28 J.113 E.00135
M204 S6000
G1 X150.366 Y108.925 F30000
; LINE_WIDTH: 0.499445
G1 F3000
M204 S500
G1 X150.286 Y109.171 E.00964
; LINE_WIDTH: 0.453298
G1 X150.207 Y109.417 E.00866
; LINE_WIDTH: 0.427787
G1 X150.201 Y109.433 E.00053
; LINE_WIDTH: 0.411316
G1 X150.161 Y109.54 E.00343
; LINE_WIDTH: 0.381497
G1 X150.117 Y109.661 E.00354
; LINE_WIDTH: 0.345656
G1 X150.037 Y109.907 E.00639
; LINE_WIDTH: 0.285834
G2 X149.716 Y117.213 I9.676 J4.085 E.14785
G1 X149.817 Y117.503 E.00607
G2 X151.051 Y119.876 I10.023 J-3.705 E.05309
; LINE_WIDTH: 0.284804
G2 X169.697 Y113.998 I8.397 J-5.876 E.51134
; LINE_WIDTH: 0.311059
G1 X169.683 Y113.114 E.01932
; LINE_WIDTH: 0.336533
G1 X169.683 Y113.101 E.00031
; LINE_WIDTH: 0.358336
G1 X169.665 Y112.807 E.00759
; LINE_WIDTH: 0.400654
G1 X169.648 Y112.512 E.00861
; LINE_WIDTH: 0.444323
G2 X169.629 Y112.199 I-7.155 J.276 E.01027
; LINE_WIDTH: 0.489487
G1 X169.6 Y111.917 E.0103
; LINE_WIDTH: 0.533295
G1 X169.571 Y111.635 E.01131
; LINE_WIDTH: 0.577102
G1 X169.542 Y111.354 E.01232
; WIPE_START
G1 X169.571 Y111.635 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.402 Y110.291 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.43924
G1 F3000
M204 S500
G1 X169.152 Y109.131 E.03833
; WIPE_START
G1 X169.402 Y110.291 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.518 Y105.19 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.55081
G1 F6300
M204 S500
G1 X168.792 Y104.464 E.04249
G3 X168.487 Y104.877 I-1.37 J-.691 E.02136
G1 X169.306 Y105.696 E.04791
G1 X169.297 Y106.405 E.02936
G1 X168.113 Y105.222 E.06928
G3 X167.671 Y105.497 I-1.015 J-1.136 E.02169
G1 X169.288 Y107.115 E.09466
G1 X169.279 Y107.824 E.02936
G1 X167.15 Y105.695 E.12459
G3 X166.713 Y105.78 I-.627 J-2.076 E.01846
G1 X166.719 Y105.983 E.0084
G1 X169.473 Y108.737 E.16119
; WIPE_START
G1 X168.059 Y107.322 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X166.321 Y105.659 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.11656
G1 F3000
M204 S500
M73 P22 R8
G1 X166.199 Y105.663 E.00073
; LINE_WIDTH: 0.152875
G1 X165.954 Y105.665 E.0022
; WIPE_START
G1 X166.199 Y105.663 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.195 Y103.946 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.560072
G1 F3000
M204 S500
G1 X169.241 Y103.543 E.01712
; LINE_WIDTH: 0.528475
G2 X169.258 Y103.3 I-5.589 J-.527 E.00962
G1 X169.265 Y103.082 E.00864
G2 X169.285 Y99.899 I-147.842 J-2.523 E.12595
; LINE_WIDTH: 0.569184
G1 X169.305 Y96.726 E.13608
; LINE_WIDTH: 0.603834
G2 X169.279 Y96.113 I-9.489 J.091 E.02803
; WIPE_START
G1 X169.305 Y96.726 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.366 Y92.603 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.12575
G1 F3000
M204 S500
G1 X169.48 Y92.439 E.00135
; LINE_WIDTH: 0.17278
G2 X169.565 Y92.277 I-.52 J-.375 E.00193
G1 X169.581 Y92.176 E.00108
; LINE_WIDTH: 0.136773
G1 X169.596 Y92.081 E.00074
; LINE_WIDTH: 0.112674
G1 X169.611 Y91.957 E.00071
; WIPE_START
G1 X169.596 Y92.081 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X169.554 Y90.835 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.111803
G1 F3000
M204 S500
G1 X169.532 Y90.725 E.00063
; LINE_WIDTH: 0.144228
G1 X169.482 Y90.551 E.0015
; LINE_WIDTH: 0.180811
G1 X169.452 Y90.459 E.00109
; LINE_WIDTH: 0.226288
G2 X169.194 Y89.73 I-16.796 J5.52 E.01155
M204 S6000
G1 X169.173 Y89.744 F30000
; LINE_WIDTH: 0.31121
G1 F3000
M204 S500
G1 X169.572 Y90.726 E.02317
M204 S6000
G1 X169.554 Y90.613 F30000
; LINE_WIDTH: 0.418351
G1 F3000
M204 S500
G2 X169.156 Y89.756 I-20.492 J9.006 E.02893
; WIPE_START
G1 X169.554 Y90.613 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X162.55 Y87.582 Z.6 F30000
G1 X148.139 Y81.344 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.5506
G1 F6300
M204 S500
G1 X148.789 Y81.995 E.03805
G2 X148.49 Y82.413 I1.039 J1.059 E.0214
G1 X147.441 Y81.364 E.06139
M204 S6000
G1 X147.057 Y81.7 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.518691
G1 F3000
M204 S500
G2 X146.786 Y81.663 I-.988 J6.174 E.01061
; LINE_WIDTH: 0.487321
G1 X146.594 Y81.644 E.00696
; LINE_WIDTH: 0.433321
G1 X146.162 Y81.632 E.01376
; LINE_WIDTH: 0.421483
G1 X145.747 Y81.656 E.01283
; LINE_WIDTH: 0.459344
G1 X145.537 Y81.683 E.00716
; LINE_WIDTH: 0.500689
G1 X145.153 Y81.748 E.01455
; WIPE_START
G1 X145.537 Y81.683 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X145.056 Y89.3 Z.6 F30000
G1 X144.47 Y98.587 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.123824
G1 F3000
M204 S500
G1 X144.335 Y98.722 E.00126
; LINE_WIDTH: 0.151055
G1 X144.255 Y98.809 E.00105
; WIPE_START
G1 X144.335 Y98.722 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X143.971 Y100.219 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.567242
G1 F3000
M204 S500
G1 X143.86 Y100.835 E.02673
G2 X144.305 Y101.248 I11.042 J-11.467 E.02595
; WIPE_START
G1 X143.86 Y100.835 E-.37434
G1 X143.971 Y100.219 E-.38566
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X142.394 Y101.032 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.122442
G1 F3000
M204 S500
G1 X142.231 Y101.108 E.00117
; LINE_WIDTH: 0.158715
G1 X142.144 Y101.145 E.00089
; LINE_WIDTH: 0.206635
G3 X141.559 Y101.375 I-5.808 J-13.903 E.00839
M204 S6000
G1 X142.129 Y101.232 F30000
; LINE_WIDTH: 0.286908
G1 F3000
M204 S500
G1 X141.683 Y101.253 E.00889
G1 X134.61 Y101.253 E.14062
G1 X134.232 Y101.236 E.00753
; LINE_WIDTH: 0.340589
G1 X134.036 Y101.215 E.00478
; LINE_WIDTH: 0.375913
G1 X133.945 Y101.201 E.0025
; LINE_WIDTH: 0.405876
G1 X133.838 Y101.185 E.00321
; LINE_WIDTH: 0.435524
G1 X133.665 Y101.151 E.00562
; LINE_WIDTH: 0.461171
G1 X133.493 Y101.118 E.00599
M204 S6000
G1 X132.946 Y100.964 F30000
; FEATURE: Bottom surface
; LINE_WIDTH: 0.55699
G1 F6300
M204 S500
G1 X131.419 Y99.437 E.09042
G3 X131.054 Y99.799 I-2.248 J-1.908 E.02156
G1 X132.013 Y100.758 E.05682
G1 X131.286 Y100.758 E.03045
G1 X130.529 Y100.001 E.04485
M204 S6000
G1 X130.159 Y100.677 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.309554
G1 F3000
M204 S500
G1 X129.437 Y100.904 E.01643
; WIPE_START
G1 X130.159 Y100.677 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X132.013 Y98.878 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.116538
G1 F3000
M204 S500
G1 X132.009 Y98.756 E.00073
; LINE_WIDTH: 0.143786
G1 X132.006 Y98.635 E.001
; LINE_WIDTH: 0.161683
G1 X132.007 Y98.511 E.0012
; WIPE_START
G1 X132.006 Y98.635 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X139.402 Y100.519 Z.6 F30000
G1 X146.239 Y102.26 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.152316
G1 F3000
M204 S500
G1 X146.362 Y102.233 E.00112
; LINE_WIDTH: 0.123811
G1 X146.546 Y102.183 E.00126
; WIPE_START
G1 X146.362 Y102.233 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X152.572 Y105.659 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.116827
G1 F3000
M204 S500
G1 X152.695 Y105.663 E.00074
; LINE_WIDTH: 0.144631
G1 X152.819 Y105.667 E.00102
; LINE_WIDTH: 0.162201
G1 X152.939 Y105.665 E.00116
; OBJECT_ID: 817
; WIPE_START
G1 X152.819 Y105.667 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 861
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
M204 S6000
G1 X146.394 Y109.788 Z.6 F30000
G1 X99.359 Y139.954 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.5
G1 F3000
M204 S500
G3 X100.772 Y138.4 I1.498 J-.057 E.08665
G1 X100.91 Y138.399 E.00515
G3 X99.363 Y140.014 I-.052 J1.499 E.25688
; WIPE_START
G1 X99.373 Y139.656 E-.13605
G1 X99.45 Y139.368 E-.11358
G1 X99.583 Y139.1 E-.11357
G1 X99.766 Y138.864 E-.11353
G1 X99.993 Y138.669 E-.11352
G1 X100.253 Y138.523 E-.11355
G1 X100.394 Y138.478 E-.05621
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X95.108 Y132.973 Z.6 F30000
G1 X89.626 Y127.264 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X88.044 Y125.673 I-1.496 J-.095 E.25646
G1 X88.182 Y125.671 E.00514
G3 X89.629 Y127.204 I-.052 J1.499 E.08708
; WIPE_START
G1 X89.575 Y127.559 E-.1362
G1 X89.469 Y127.838 E-.11351
G1 X89.313 Y128.088 E-.11198
G1 X89.16 Y128.258 E-.08698
G1 X88.924 Y128.441 E-.11345
G1 X88.656 Y128.574 E-.11347
G1 X88.442 Y128.631 E-.08442
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X95.419 Y131.726 Z.6 F30000
G1 X102.898 Y135.043 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
G1 F3000
M204 S500
G1 X102.426 Y135.01 E.0176
G3 X102.733 Y114.356 I.91 J-10.315 E1.15529
G3 X104.231 Y114.378 I.588 J11.468 E.05585
G3 X102.958 Y135.043 I-.895 J10.317 E1.19245
M204 S6000
G1 X102.926 Y134.587 F30000
; FEATURE: Outer wall
G1 F3000
M204 S500
M73 P23 R8
G1 X102.466 Y134.554 E.01718
G3 X102.76 Y114.813 I.87 J-9.86 E1.10431
G3 X104.191 Y114.833 I.561 J10.961 E.05335
G3 X102.986 Y134.586 I-.855 J9.861 E1.13937
; WIPE_START
G1 X102.466 Y134.554 E-.19798
G1 X101.975 Y134.503 E-.18755
G1 X101.488 Y134.423 E-.18765
G1 X101.007 Y134.32 E-.18682
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X99.189 Y140.935 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Inner wall
M73 P23 R7
G1 F3000
M204 S500
G1 X98.999 Y141.075 E.00879
G1 X86.949 Y129.025 E.63472
G1 X87.089 Y128.835 E.00879
G2 X88.199 Y125.214 I1.033 J-1.664 E.26685
G1 X87.754 Y125.219 E.01659
G1 X111.329 Y101.643 E1.24182
G3 X112.722 Y101.156 I1.198 J1.191 E.05688
G1 X112.758 Y101.362 E.00777
G2 X115.507 Y103.412 I.818 J1.77 E.30039
G2 X116.433 Y104.364 I12.907 J-11.626 E.04951
G2 X124.361 Y112.286 I982.001 J-974.773 E.41744
G1 X124.623 Y112.527 E.01325
G2 X124.822 Y116.399 I.255 J1.928 E.21595
G2 X126.669 Y115.263 I.045 J-1.998 E.08539
G1 X126.868 Y115.304 E.00755
G3 X126.381 Y116.695 I-1.678 J.193 E.05681
G1 X102.805 Y140.271 E1.24184
G2 X102.537 Y138.898 I-2.344 J-.255 E.05287
G2 X99.159 Y140.883 I-1.679 J1.01 E.22774
; WIPE_START
G1 X98.999 Y141.075 E-.09468
G1 X97.761 Y139.837 E-.66532
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X101.04 Y132.944 Z.6 F30000
G1 X114.913 Y103.783 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Outer wall
G1 F3000
M204 S500
G3 X112.165 Y103.624 I-1.342 J-.637 E.13115
G3 X113.432 Y101.67 I1.357 J-.508 E.10074
G3 X113.675 Y101.692 I.058 J.711 E.00912
G3 X114.739 Y102.435 I-.476 J1.818 E.04936
G3 X115.015 Y103.494 I-1.048 J.839 E.04201
G3 X114.938 Y103.728 I-1.444 J-.349 E.00918
; WIPE_START
G1 X114.85 Y103.922 E-.08095
G1 X114.712 Y104.113 E-.08961
G1 X114.502 Y104.313 E-.10999
G1 X114.249 Y104.472 E-.11361
G1 X114.112 Y104.532 E-.05685
G1 X113.97 Y104.578 E-.05691
G1 X113.675 Y104.626 E-.11346
G1 X113.525 Y104.628 E-.05692
G1 X113.312 Y104.599 E-.0817
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X119.506 Y109.059 Z.6 F30000
G1 X124.989 Y113.006 Z.6
G1 Z.2
M73 P24 R7
G1 E.8 F1800
G1 F3000
M204 S500
G3 X126.053 Y113.748 I-.477 J1.818 E.04936
G3 X126.329 Y114.808 I-1.048 J.839 E.04201
G3 X123.479 Y114.938 I-1.444 J-.349 E.14256
G3 X124.746 Y112.984 I1.357 J-.508 E.10074
G3 X124.93 Y112.993 I.058 J.711 E.0069
; WIPE_START
G1 X125.274 Y113.096 E-.13627
G1 X125.697 Y113.356 E-.18879
G1 X125.896 Y113.536 E-.10215
G1 X126.053 Y113.748 E-.10016
G1 X126.241 Y114.064 E-.13964
G1 X126.298 Y114.206 E-.05824
G1 X126.315 Y114.296 E-.03474
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X121.147 Y119.912 Z.6 F30000
G1 X100.5 Y142.347 Z.6
G1 Z.2
G1 E.8 F1800
G1 F3000
M204 S500
G3 X99.001 Y141.723 I0 J-2.111 E.06208
G1 X86.301 Y129.023 E.66897
G3 X86.301 Y126.025 I1.487 J-1.499 E.12415
G1 X111.022 Y101.304 E1.30216
G3 X112.921 Y100.716 I1.524 J1.562 E.07686
G1 X112.932 Y100.717 E.00041
G3 X114.097 Y101.272 I-.815 J3.213 E.04836
G1 X114.467 Y101.545 E.01712
G1 X115.131 Y102.204 E.03485
G2 X116.757 Y104.042 I10.476 J-7.629 E.09156
G2 X124.677 Y111.956 I983.078 J-975.852 E.41699
G2 X125.82 Y112.893 I7.331 J-7.779 E.05512
G1 X126.479 Y113.557 E.03485
G3 X127.187 Y114.69 I-4.329 J3.493 E.04988
G3 X126.72 Y117.002 I-1.974 J.804 E.09309
G1 X101.999 Y141.723 E1.30215
G3 X100.56 Y142.347 I-1.499 J-1.487 E.05984
M204 S6000
G1 X100.57 Y141.86 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.568419
G1 F3000
M204 S500
G3 X100.372 Y141.837 I.071 J-1.531 E.00855
; LINE_WIDTH: 0.599843
G1 X100.174 Y141.796 E.00916
; LINE_WIDTH: 0.638102
G3 X99.801 Y141.64 I.5 J-1.714 E.01966
; LINE_WIDTH: 0.671078
G1 X99.627 Y141.534 E.01042
G3 X99.227 Y141.191 I5.506 J-6.84 E.027
M204 S6000
G1 X98.662 Y140.415 F30000
; LINE_WIDTH: 0.123897
G1 F3000
M204 S500
G1 X98.655 Y140.143 E.0018
; WIPE_START
G1 X98.662 Y140.415 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X100.57 Y141.86 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.528603
G1 F3000
M204 S500
G2 X100.769 Y141.859 I.091 J-3.933 E.00786
; LINE_WIDTH: 0.489924
G2 X100.964 Y141.835 I-.019 J-.937 E.00719
; LINE_WIDTH: 0.44258
G2 X101.154 Y141.795 I-.937 J-4.923 E.00631
G1 X101.172 Y141.788 E.00062
; LINE_WIDTH: 0.393915
G1 X101.336 Y141.728 E.00499
; LINE_WIDTH: 0.367802
G1 X101.351 Y141.722 E.00043
; LINE_WIDTH: 0.346142
G2 X101.508 Y141.649 I-.294 J-.836 E.0043
G1 X101.52 Y141.642 E.00035
; LINE_WIDTH: 0.294215
G1 X101.669 Y141.551 E.00357
; LINE_WIDTH: 0.252719
G2 X101.82 Y141.445 I-1.851 J-2.796 E.00315
; LINE_WIDTH: 0.201722
G1 X102.097 Y141.201 E.00478
G1 X102.394 Y140.872 E.00574
; LINE_WIDTH: 0.24533
G1 X102.572 Y140.639 E.00484
; WIPE_START
G1 X102.394 Y140.872 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X107.338 Y135.057 Z.6 F30000
G1 X107.665 Y134.673 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.523931
G1 F3000
M204 S500
G1 X107.818 Y134.566 E.0073
; LINE_WIDTH: 0.488127
G1 X107.97 Y134.459 E.00676
; LINE_WIDTH: 0.452324
G1 X108.123 Y134.353 E.00621
; LINE_WIDTH: 0.412838
G1 X108.238 Y134.268 E.00432
; LINE_WIDTH: 0.371593
G1 X108.345 Y134.188 E.00357
; LINE_WIDTH: 0.331825
G1 X108.453 Y134.109 E.00314
; LINE_WIDTH: 0.292057
G1 X108.56 Y134.03 E.00271
; LINE_WIDTH: 0.249283
G1 X108.705 Y133.918 E.00308
; LINE_WIDTH: 0.204457
G1 X108.845 Y133.809 E.00233
; LINE_WIDTH: 0.160348
G1 X108.985 Y133.7 E.0017
; LINE_WIDTH: 0.120545
G1 X109.145 Y133.569 E.00131
; WIPE_START
G1 X108.985 Y133.7 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X112.202 Y130.512 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.120316
G1 F3000
M204 S500
G1 X112.331 Y130.354 E.00129
; LINE_WIDTH: 0.16001
G1 X112.442 Y130.212 E.00172
; LINE_WIDTH: 0.204425
G1 X112.55 Y130.072 E.00233
; LINE_WIDTH: 0.248544
G1 X112.659 Y129.932 E.00297
; LINE_WIDTH: 0.291192
G1 X112.742 Y129.82 E.00281
; LINE_WIDTH: 0.331803
G1 X112.821 Y129.713 E.00314
; LINE_WIDTH: 0.371561
G1 X112.9 Y129.605 E.00357
; LINE_WIDTH: 0.411319
G1 X112.98 Y129.498 E.004
; LINE_WIDTH: 0.451307
G1 X113.092 Y129.337 E.00653
; LINE_WIDTH: 0.488104
G1 X113.199 Y129.185 E.00676
; LINE_WIDTH: 0.52392
G1 X113.306 Y129.032 E.0073
; WIPE_START
G1 X113.199 Y129.185 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X118.521 Y123.714 Z.6 F30000
G1 X125.479 Y116.56 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.416598
G1 F3000
M204 S500
G1 X125.747 Y116.667 E.0088
; LINE_WIDTH: 0.452604
G1 X125.773 Y116.676 E.00091
G1 X125.856 Y116.619 E.00338
; LINE_WIDTH: 0.415047
G1 X125.94 Y116.562 E.00307
; LINE_WIDTH: 0.3805
G1 X126.028 Y116.497 E.00302
; LINE_WIDTH: 0.352946
G1 X126.101 Y116.441 E.00232
; LINE_WIDTH: 0.314894
G1 X126.22 Y116.333 E.00357
; LINE_WIDTH: 0.277516
G1 X126.301 Y116.258 E.00211
; LINE_WIDTH: 0.243708
G2 X126.392 Y116.152 I-.517 J-.534 E.00228
; LINE_WIDTH: 0.202033
G1 X126.452 Y116.077 E.00124
; LINE_WIDTH: 0.174045
G1 X126.592 Y115.882 E.00257
M204 S6000
G1 X126.814 Y115.059 F30000
; LINE_WIDTH: 0.383258
G1 F3000
M204 S500
G1 X126.654 Y114.194 E.02441
M204 S6000
G1 X126.593 Y114.209 F30000
; LINE_WIDTH: 0.175338
G1 F3000
M204 S500
G1 X126.628 Y114.29 E.00095
; LINE_WIDTH: 0.191952
G1 X126.953 Y115.088 E.01046
M204 S6000
G1 X126.854 Y115.067 F30000
; LINE_WIDTH: 0.276671
G1 F3000
M204 S500
G2 X126.574 Y114.072 I-10.609 J2.45 E.01969
M204 S6000
G1 X126.533 Y114.079 F30000
; LINE_WIDTH: 0.136345
G1 F3000
M204 S500
G1 X126.593 Y114.209 E.00109
M204 S6000
G1 X126.533 Y114.079 F30000
; LINE_WIDTH: 0.110219
G1 F3000
M204 S500
G1 X126.491 Y114.003 E.00048
; WIPE_START
G1 X126.533 Y114.079 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X125.326 Y112.843 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.125086
G1 F3000
M204 S500
G1 X125.276 Y112.815 E.00038
G2 X125.03 Y112.681 I-1.918 J3.225 E.00188
M204 S6000
G1 X124.89 Y112.733 F30000
; LINE_WIDTH: 0.136239
G1 F3000
M204 S500
G3 X125.225 Y112.732 I.219 J9.184 E.00255
; WIPE_START
G1 X124.89 Y112.733 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X119.124 Y107.733 Z.6 F30000
G1 X115.288 Y104.406 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.50534
G1 F6300
M204 S500
G1 X123.471 Y112.589 E.43608
G1 X123.373 Y112.656 E.00447
G1 X123.133 Y112.905 E.01303
G1 X115.119 Y104.891 E.42708
G3 X114.738 Y105.164 I-1.171 J-1.235 E.01772
G1 X122.861 Y113.287 E.43291
G2 X122.663 Y113.743 I1.433 J.894 E.0188
G1 X114.285 Y105.365 E.44647
G1 X114.179 Y105.399 E.00418
G1 X113.737 Y105.471 E.01688
M73 P25 R7
G1 X122.757 Y114.491 E.48065
; WIPE_START
G1 X121.343 Y113.076 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X125.215 Y117.602 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X124.32 Y116.708 E.04768
G1 X124.119 Y116.659 E.00777
G3 X122.63 Y115.018 I.771 J-2.196 E.08704
G1 X113.006 Y105.394 E.51286
G1 X112.806 Y105.346 E.00776
G3 X111.316 Y103.704 I.772 J-2.197 E.08705
G1 X110.567 Y102.955 E.03993
G1 X110.24 Y103.282 E.01742
G1 X124.742 Y117.784 E.77281
G1 X124.415 Y118.111 E.01742
G1 X109.913 Y103.609 E.77281
G1 X109.586 Y103.936 E.01742
G1 X124.088 Y118.438 E.77281
G1 X123.761 Y118.765 E.01742
G1 X109.259 Y104.263 E.77281
G1 X108.932 Y104.59 E.01742
G1 X123.434 Y119.092 E.77281
G1 X123.107 Y119.419 E.01742
G1 X108.605 Y104.917 E.77281
G1 X108.278 Y105.244 E.01742
G1 X122.78 Y119.746 E.77281
G1 X122.453 Y120.073 E.01742
G1 X107.951 Y105.571 E.77281
G1 X107.624 Y105.898 E.01742
G1 X122.126 Y120.4 E.77281
G1 X121.799 Y120.727 E.01742
G1 X107.297 Y106.225 E.77281
G1 X106.97 Y106.552 E.01742
G1 X121.472 Y121.054 E.77281
G1 X121.145 Y121.381 E.01742
G1 X106.643 Y106.879 E.77281
G1 X106.316 Y107.206 E.01742
G1 X120.818 Y121.708 E.77281
M73 P26 R7
G1 X120.491 Y122.035 E.01742
G1 X105.989 Y107.533 E.77281
G1 X105.662 Y107.86 E.01742
G1 X120.164 Y122.362 E.77281
G1 X119.837 Y122.689 E.01742
G1 X105.335 Y108.187 E.77281
G1 X105.008 Y108.513 E.01742
G1 X119.51 Y123.016 E.77281
G1 X119.184 Y123.343 E.01742
G1 X104.681 Y108.84 E.77281
G1 X104.354 Y109.167 E.01742
G1 X118.857 Y123.67 E.77281
G1 X118.53 Y123.997 E.01742
G1 X104.027 Y109.494 E.77281
G1 X103.7 Y109.821 E.01742
G1 X118.203 Y124.323 E.77281
G1 X117.876 Y124.65 E.01742
G1 X112.739 Y119.514 E.27373
G2 X108.51 Y115.285 I-9.355 J5.126 E.22841
G1 X103.374 Y110.148 E.27373
G1 X103.047 Y110.475 E.01742
G1 X107.274 Y114.703 E.22526
G2 X106.283 Y114.366 I-4.423 J11.385 E.03944
G1 X102.72 Y110.802 E.18989
G1 X102.393 Y111.129 E.01742
G1 X105.421 Y114.157 E.16136
G2 X104.642 Y114.033 I-2.359 J12.279 E.0297
G1 X102.066 Y111.456 E.13732
G1 X101.739 Y111.783 E.01742
G1 X103.925 Y113.969 E.11649
G2 X103.253 Y113.951 I-.517 J6.722 E.02534
G1 X101.412 Y112.11 E.09811
G1 X101.085 Y112.437 E.01742
G1 X102.623 Y113.976 E.08199
G2 X102.025 Y114.031 I.209 J5.53 E.02266
G1 X100.758 Y112.764 E.06751
G1 X100.431 Y113.091 E.01742
G1 X101.456 Y114.117 E.05465
G2 X100.913 Y114.228 I.837 J5.488 E.0209
G1 X100.104 Y113.418 E.04313
G1 X99.777 Y113.745 E.01742
G1 X100.393 Y114.361 E.03284
M73 P27 R7
G2 X99.894 Y114.516 I1.301 J5.076 E.0197
G1 X99.304 Y113.927 E.03141
; WIPE_START
G1 X99.894 Y114.516 E-.3168
G1 X100.393 Y114.361 E-.19858
G1 X99.938 Y113.906 E-.24462
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X106.773 Y117.302 Z.6 F30000
G1 X112.934 Y120.363 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X117.549 Y124.977 E.2459
G1 X117.222 Y125.304 E.01742
G1 X113.658 Y121.741 E.18989
G3 X113.867 Y122.603 I-8.535 J2.519 E.03345
G1 X116.895 Y125.631 E.16136
G1 X116.568 Y125.958 E.01742
G1 X113.991 Y123.382 E.13732
G3 X114.055 Y124.099 I-7.156 J.998 E.02716
G1 X116.241 Y126.285 E.11649
G1 X115.914 Y126.612 E.01742
G1 X114.073 Y124.771 E.09811
G3 X114.05 Y125.403 I-20.889 J-.432 E.02381
G1 X115.587 Y126.939 E.08189
G1 X115.26 Y127.266 E.01742
G1 X113.993 Y125.999 E.06751
G3 X113.907 Y126.568 I-5.73 J-.572 E.02167
G1 X114.933 Y127.593 E.05465
G1 X114.606 Y127.92 E.01742
G1 X113.796 Y127.111 E.04313
G3 X113.663 Y127.631 I-5.287 J-1.083 E.02025
G1 X114.279 Y128.247 E.03284
G1 X113.952 Y128.574 E.01742
G1 X113.346 Y127.969 E.03227
; WIPE_START
G1 X113.952 Y128.574 E-.32538
G1 X114.279 Y128.247 E-.17572
G1 X113.797 Y127.765 E-.2589
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X108.071 Y122.719 Z.6 F30000
G1 X98.992 Y114.718 Z.6
G1 Z.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.523934
G1 F3000
M204 S500
G1 X98.839 Y114.825 E.0073
; LINE_WIDTH: 0.488118
G1 X98.687 Y114.932 E.00676
; LINE_WIDTH: 0.451322
G1 X98.526 Y115.044 E.00653
; LINE_WIDTH: 0.41134
G1 X98.419 Y115.124 E.004
; LINE_WIDTH: 0.371582
G1 X98.311 Y115.203 E.00357
; LINE_WIDTH: 0.331824
G1 X98.204 Y115.282 E.00314
; LINE_WIDTH: 0.291213
G1 X98.092 Y115.365 E.00281
; LINE_WIDTH: 0.248559
G1 X97.952 Y115.474 E.00297
; LINE_WIDTH: 0.204436
G1 X97.812 Y115.582 E.00234
; LINE_WIDTH: 0.160017
G1 X97.67 Y115.693 E.00172
; LINE_WIDTH: 0.120319
G1 X97.512 Y115.822 E.00129
; WIPE_START
G1 X97.67 Y115.693 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X94.455 Y118.879 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.120541
G1 F3000
M204 S500
G1 X94.324 Y119.039 E.00131
; LINE_WIDTH: 0.16034
G1 X94.215 Y119.179 E.0017
; LINE_WIDTH: 0.204417
G1 X94.106 Y119.319 E.00233
; LINE_WIDTH: 0.24921
G1 X93.994 Y119.464 E.00308
; LINE_WIDTH: 0.291989
G1 X93.915 Y119.571 E.00271
; LINE_WIDTH: 0.331759
G1 X93.836 Y119.678 E.00314
; LINE_WIDTH: 0.371529
G1 X93.756 Y119.786 E.00357
; LINE_WIDTH: 0.412777
G1 X93.671 Y119.901 E.00432
; LINE_WIDTH: 0.452282
G1 X93.565 Y120.054 E.00622
; LINE_WIDTH: 0.488106
G1 X93.458 Y120.206 E.00676
; LINE_WIDTH: 0.523931
G1 X93.351 Y120.359 E.0073
; WIPE_START
G1 X93.458 Y120.206 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X93.305 Y121.439 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; FEATURE: Bottom surface
; LINE_WIDTH: 0.51599
G1 F6300
M204 S500
G1 X92.694 Y120.828 E.0333
G1 X92.359 Y121.163 E.01824
G1 X92.986 Y121.789 E.03415
G2 X92.85 Y122.322 I5.282 J1.626 E.02123
G1 X92.025 Y121.497 E.045
G1 X91.69 Y121.832 E.01824
G1 X92.739 Y122.88 E.05716
G2 X92.654 Y123.464 I5.809 J1.142 E.02277
G1 X91.356 Y122.166 E.07077
G1 X91.021 Y122.501 E.01824
G1 X92.601 Y124.081 E.08614
G2 X92.586 Y124.734 I6.538 J.485 E.0252
G1 X90.687 Y122.835 E.10351
G1 X90.352 Y123.17 E.01824
G1 X92.611 Y125.428 E.12312
G2 X92.684 Y126.171 I16.422 J-1.256 E.02878
G1 X90.018 Y123.504 E.14538
G1 X89.683 Y123.839 E.01824
G1 X92.833 Y126.989 E.17174
G2 X93.074 Y127.898 I10.775 J-2.363 E.03628
G1 X89.349 Y124.173 E.20309
G1 X89.014 Y124.508 E.01824
G1 X93.894 Y129.387 E.26601
; WIPE_START
G1 X92.479 Y127.973 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X99.365 Y131.266 Z.6 F30000
G1 X106.585 Y134.719 Z.6
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X107.196 Y135.33 E.0333
G1 X106.861 Y135.665 E.01824
G1 X106.235 Y135.038 E.03415
G3 X105.702 Y135.174 I-1.619 J-5.258 E.02123
G1 X106.527 Y135.999 E.045
G1 X106.192 Y136.334 E.01824
G1 X105.144 Y135.285 E.05716
G3 X104.56 Y135.37 I-1.141 J-5.805 E.02277
G1 X105.858 Y136.668 E.07077
G1 X105.523 Y137.003 E.01824
G1 X103.943 Y135.423 E.08614
G3 X103.29 Y135.438 I-.485 J-6.538 E.0252
G1 X105.189 Y137.337 E.10351
G1 X104.854 Y137.672 E.01824
G1 X102.596 Y135.413 E.12312
M73 P28 R7
G3 X101.853 Y135.34 I1.253 J-16.39 E.02878
G1 X104.52 Y138.006 E.14538
G1 X104.185 Y138.341 E.01824
G1 X101.035 Y135.191 E.17174
G3 X100.126 Y134.95 I2.364 J-10.776 E.03628
G1 X103.851 Y138.675 E.20309
G1 X103.516 Y139.01 E.01824
G1 X98.637 Y134.13 E.26601
; WIPE_START
G1 X100.051 Y135.545 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X103.327 Y139.49 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X103.105 Y139.268 E.0121
G1 X103.07 Y139.123 E.00575
G2 X101.479 Y137.641 I-2.201 J.769 E.08718
G1 X97.656 Y133.819 E.20841
G3 X94.205 Y130.368 I5.582 J-9.033 E.18982
G1 X90.377 Y126.54 E.20869
G1 X90.342 Y126.395 E.00574
G2 X88.756 Y124.919 I-2.19 J.763 E.08691
G1 X88.534 Y124.697 E.0121
; WIPE_START
G1 X88.756 Y124.919 E-.11931
G1 X88.901 Y124.954 E-.05671
G1 X89.325 Y125.151 E-.17766
G1 X89.694 Y125.423 E-.17407
G1 X89.873 Y125.602 E-.0962
G1 X90.085 Y125.89 E-.13605
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X90.265 Y127.097 Z.6 F30000
G1 Z.2
G1 E.8 F1800
G1 F6300
M204 S500
G1 X100.73 Y137.561 E.57047
G2 X100.158 Y137.658 I.08 J2.204 E.02243
G1 X90.36 Y127.86 E.53413
G3 X90.158 Y128.328 I-1.641 J-.431 E.0197
G1 X99.691 Y137.86 E.51966
G1 X99.301 Y138.14 E.01848
G1 X89.881 Y128.719 E.51358
G3 X89.536 Y129.044 I-1.712 J-1.47 E.01828
G1 X98.98 Y138.488 E.51485
G1 X98.73 Y138.907 E.01881
G1 X89.118 Y129.295 E.52401
G3 X88.613 Y129.459 I-.797 J-1.594 E.02054
G1 X98.565 Y139.411 E.54255
G1 X98.511 Y139.752 E.01333
G1 X98.234 Y139.749 E.01067
G1 X88.067 Y129.582 E.55427
M204 S6000
G1 X87.882 Y129.369 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.123958
G1 F3000
M204 S500
G1 X87.609 Y129.362 E.0018
M204 S6000
G1 X86.846 Y128.78 F30000
; LINE_WIDTH: 0.671065
G1 F3000
M204 S500
G3 X86.49 Y128.397 I1.866 J-2.089 E.02679
G1 X86.384 Y128.223 E.01044
; LINE_WIDTH: 0.638085
G3 X86.228 Y127.85 I1.556 J-.872 E.01966
; LINE_WIDTH: 0.599847
G1 X86.187 Y127.653 E.00914
; LINE_WIDTH: 0.568428
G3 X86.164 Y127.454 I1.515 J-.27 E.00857
; LINE_WIDTH: 0.528586
G3 X86.165 Y127.256 I3.987 J-.09 E.00785
; LINE_WIDTH: 0.489932
G3 X86.189 Y127.06 I.934 J.018 E.0072
; LINE_WIDTH: 0.442575
G3 X86.229 Y126.87 I4.849 J.922 E.00631
G1 X86.236 Y126.852 E.00062
; LINE_WIDTH: 0.393909
G1 X86.296 Y126.689 E.00498
; LINE_WIDTH: 0.367831
G1 X86.301 Y126.673 E.00043
; LINE_WIDTH: 0.346137
G3 X86.375 Y126.516 I.836 J.294 E.0043
G1 X86.382 Y126.504 E.00035
; LINE_WIDTH: 0.294193
G1 X86.473 Y126.355 E.00357
; LINE_WIDTH: 0.252722
G3 X86.579 Y126.204 I2.795 J1.85 E.00316
; LINE_WIDTH: 0.199224
G1 X86.819 Y125.932 E.00462
G1 X87.082 Y125.687 E.00457
; LINE_WIDTH: 0.245208
G1 X87.393 Y125.451 E.00644
; WIPE_START
G1 X87.082 Y125.687 E-.76
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X92.618 Y120.433 Z.6 F30000
G1 X111.464 Y102.545 Z.6
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.416272
G1 F3000
M204 S500
G1 X111.357 Y102.277 E.00879
; LINE_WIDTH: 0.452556
G1 X111.347 Y102.251 E.00091
G1 X111.405 Y102.168 E.00338
; LINE_WIDTH: 0.414991
G1 X111.462 Y102.084 E.00307
; LINE_WIDTH: 0.380443
G1 X111.528 Y101.996 E.00301
; LINE_WIDTH: 0.352937
G1 X111.583 Y101.923 E.00232
; LINE_WIDTH: 0.314918
G1 X111.691 Y101.804 E.00356
; LINE_WIDTH: 0.277595
G1 X111.766 Y101.723 E.0021
; LINE_WIDTH: 0.243697
G3 X111.872 Y101.632 I.537 J.52 E.0023
; LINE_WIDTH: 0.201744
G1 X111.947 Y101.572 E.00125
; LINE_WIDTH: 0.1738
G1 X112.142 Y101.432 E.00256
M204 S6000
G1 X112.962 Y101.202 F30000
; LINE_WIDTH: 0.338896
G1 F3000
M204 S500
G1 X113.851 Y101.384 E.02188
M204 S6000
G1 X113.816 Y101.431 F30000
; LINE_WIDTH: 0.144349
G1 F3000
M204 S500
G1 X113.896 Y101.466 E.00072
; LINE_WIDTH: 0.115204
G3 X114.021 Y101.533 I-1.059 J2.111 E.00084
M204 S6000
G1 X114.003 Y101.487 F30000
; LINE_WIDTH: 0.271788
G1 F3000
M204 S500
G2 X112.959 Y101.182 I-1.937 J4.685 E.02033
M204 S6000
G1 X112.94 Y101.071 F30000
; LINE_WIDTH: 0.189489
G1 F3000
M204 S500
G3 X113.816 Y101.431 I-8.855 J22.782 E.01132
M204 S6000
G1 X113.801 Y101.351 F30000
; LINE_WIDTH: 0.446544
G1 F3000
M204 S500
G2 X113.186 Y101.254 I-2.154 J11.705 E.02046
G1 X112.97 Y100.967 E.01181
; WIPE_START
G1 X113.186 Y101.254 E-.27824
G1 X113.801 Y101.351 E-.48176
; WIPE_END
G1 E-.04 F1800
M204 S6000
G1 X115.181 Y102.698 Z.6 F30000
G1 Z.2
G1 E.8 F1800
; LINE_WIDTH: 0.125942
G1 F3000
M204 S500
G3 X115.365 Y103.034 I-8.047 J4.614 E.00259
M204 S6000
G1 X115.303 Y103.2 F30000
; LINE_WIDTH: 0.181213
G1 F3000
M204 S500
G2 X115.31 Y102.82 I-8.771 J-.347 E.00429
; CHANGE_LAYER
; Z_HEIGHT: 0.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F3000
G1 X115.303 Y103.2 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 2/15
; update layer progress
M73 L2
M991 S0 P1 ;notify layer change
M106 S255
M106 P2 S178
; open powerlost recovery
M1003 S1
M976 S1 P1 ; scan model before printing 2nd layer
M400 P100
G1 E.8
; OBJECT_ID: 839
G1 E-.8
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
M204 S10000
G1 X116.5 Y110.738 Z.6 F30000
G1 X126.013 Y170.645 Z.6
G1 Z.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X125.955 Y170.645 E.00176
G3 X125.955 Y167.935 I.11 J-1.355 E.12445
G1 X126.058 Y167.93 E.00315
M73 P29 R7
G3 X126.193 Y170.643 I.008 J1.359 E.12753
G1 X126.073 Y170.644 E.00371
; WIPE_START
M204 S10000
G1 X125.955 Y170.645 E-.04461
G1 X125.722 Y170.603 E-.09013
G1 X125.499 Y170.522 E-.09007
G1 X125.199 Y170.332 E-.13495
G1 X125.032 Y170.164 E-.09005
G1 X124.896 Y169.97 E-.09013
G1 X124.796 Y169.755 E-.09012
G1 X124.721 Y169.421 E-.12995
; WIPE_END
G1 E-.04 F1800
G1 X128.287 Y166.059 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X128.247 Y165.873 E.00584
G3 X129.491 Y164.399 I1.354 J-.119 E.0659
G1 X129.593 Y164.395 E.00315
G3 X128.291 Y166.119 I.008 J1.359 E.18574
; WIPE_START
M204 S10000
G1 X128.247 Y165.873 E-.09468
G1 X128.27 Y165.518 E-.13532
G1 X128.331 Y165.289 E-.09013
G1 X128.431 Y165.074 E-.09012
G1 X128.567 Y164.88 E-.09005
G1 X128.735 Y164.712 E-.09008
G1 X129.034 Y164.521 E-.13495
G1 X129.12 Y164.49 E-.03467
; WIPE_END
G1 E-.04 F1800
G1 X124.017 Y158.814 Z.8 F30000
G1 X118.338 Y152.497 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G3 X119.102 Y152.34 I.697 J1.453 E.02611
G3 X120.001 Y152.754 I-.133 J1.472 E.03347
G1 X131.296 Y164.049 E.52988
G3 X131.553 Y165.71 I-1.022 J1.009 E.05956
G1 X131.368 Y165.687 E.00618
G2 X129.457 Y167.5 I-1.751 J.068 E.26631
G1 X129.824 Y167.516 E.01221
G1 X127.836 Y169.505 E.09328
G2 X127.079 Y167.854 I-1.898 J-.129 E.06279
G2 X126.007 Y171.047 I-.999 J1.441 E.21556
G1 X126.031 Y171.233 E.00622
G3 X124.369 Y170.976 I-.653 J-1.278 E.0596
G1 X113.074 Y159.681 E.52988
G3 X112.817 Y158.02 I1.021 J-1.008 E.05957
G1 X113.002 Y158.043 E.00618
G2 X114.909 Y156.23 I1.751 J-.068 E.26643
G1 X114.541 Y156.218 E.01221
G1 X116.534 Y154.226 E.09346
G2 X117.29 Y155.876 I1.898 J.129 E.06279
G2 X118.363 Y152.683 I.999 J-1.441 E.21557
G1 X118.346 Y152.557 E.00423
; WIPE_START
G1 X118.525 Y152.42 E-.08543
G1 X118.76 Y152.357 E-.09258
G1 X119.102 Y152.34 E-.12997
G1 X119.364 Y152.384 E-.10114
G1 X119.593 Y152.467 E-.09258
G1 X119.804 Y152.589 E-.0926
G1 X120.001 Y152.754 E-.09754
G1 X120.127 Y152.881 E-.06816
; WIPE_END
G1 E-.04 F1800
G1 X117.012 Y154.882 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X116.933 Y154.561 E.01015
G3 X118.177 Y153.085 I1.354 J-.121 E.06593
G1 X118.279 Y153.081 E.00315
G3 X117.023 Y154.939 I.008 J1.359 E.18139
; WIPE_START
M204 S10000
G1 X116.933 Y154.561 E-.14775
G1 X116.941 Y154.322 E-.09084
G1 X116.982 Y154.088 E-.09013
G1 X117.063 Y153.866 E-.09009
G1 X117.254 Y153.566 E-.13491
G1 X117.515 Y153.326 E-.13495
G1 X117.678 Y153.232 E-.07135
; WIPE_END
G1 E-.04 F1800
G1 X113.413 Y158.129 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X113.398 Y158.096 E.00111
G3 X114.642 Y156.621 I1.354 J-.121 E.06594
G1 X114.744 Y156.616 E.00315
G3 X113.475 Y158.444 I.008 J1.359 E.18241
G1 X113.424 Y158.188 E.00801
; WIPE_START
M204 S10000
G1 X113.398 Y158.096 E-.03626
G1 X113.405 Y157.857 E-.09085
G1 X113.446 Y157.625 E-.08968
G1 X113.527 Y157.401 E-.09051
G1 X113.718 Y157.102 E-.13495
G1 X113.886 Y156.934 E-.09007
G1 X114.185 Y156.743 E-.13493
G1 X114.408 Y156.662 E-.09009
G1 X114.415 Y156.661 E-.00266
; WIPE_END
G1 E-.04 F1800
G1 X118.134 Y152.171 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X118.391 Y152.053 E.0087
G3 X119.134 Y151.949 I.616 J1.697 E.0232
G3 X120.272 Y152.471 I-.175 J1.883 E.03921
G1 X131.579 Y163.778 E.49136
G3 X131.579 Y166.316 I-1.287 J1.269 E.08645
G1 X126.636 Y171.259 E.21481
G3 X124.098 Y171.259 I-1.269 J-1.287 E.08645
G1 X112.79 Y159.952 E.49136
G3 X112.79 Y157.414 I1.287 J-1.269 E.08645
G1 X116.995 Y153.21 E.18269
G3 X117.852 Y152.362 I10.146 J9.407 E.03707
G3 X118.081 Y152.2 I1.154 J1.388 E.00863
M204 S10000
G1 X118.156 Y152.617 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.235363
G1 F15000
G1 X117.727 Y152.89 E.00798
; LINE_WIDTH: 0.220023
G1 X117.669 Y152.928 E.001
; LINE_WIDTH: 0.191889
G1 X117.607 Y152.97 E.00091
; LINE_WIDTH: 0.155959
G1 X117.493 Y153.054 E.0013
; LINE_WIDTH: 0.112359
G1 X117.321 Y153.197 E.00126
G1 X117.052 Y153.466 F30000
; LINE_WIDTH: 0.112751
G1 F15000
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.157451
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.190484
G1 X116.716 Y153.915 E.00229
G1 X116.749 Y154.124 F30000
; LINE_WIDTH: 0.105811
G1 F15000
G1 X116.757 Y154.03 E.00049
; LINE_WIDTH: 0.139057
G1 X116.776 Y153.89 E.00111
; LINE_WIDTH: 0.164611
G1 X116.809 Y153.673 E.00218
G1 X118.191 Y152.883 F30000
; LINE_WIDTH: 0.387762
G1 F10439.586
G1 X117.995 Y152.735 E.00692
G2 X117.454 Y153.028 I4.476 J8.912 E.01731
G1 X117.417 Y153.065 F30000
; LINE_WIDTH: 0.306838
G1 F13640.639
G1 X118.159 Y152.636 E.01843
G1 X118.923 Y152.566 F30000
; LINE_WIDTH: 0.104964
G1 F15000
G1 X119.003 Y152.577 E.00041
; LINE_WIDTH: 0.143045
G3 X119.145 Y152.611 I-.381 J1.904 E.0012
G1 X119.151 Y152.613 E.00004
; LINE_WIDTH: 0.193335
G3 X119.313 Y152.67 I-.604 J1.968 E.00212
G1 X119.32 Y152.673 E.00009
; LINE_WIDTH: 0.242058
G3 X119.464 Y152.745 I-.741 J1.665 E.0026
G1 X119.544 Y152.796 E.00155
; LINE_WIDTH: 0.284604
G1 F14895.487
G3 X119.759 Y152.97 I-.722 J1.111 E.00545
G1 X120.005 Y153.237 E.00715
; LINE_WIDTH: 0.331279
G1 F12484.46
G1 X120.12 Y153.379 E.00431
; LINE_WIDTH: 0.365892
G1 F11146.501
G1 X120.179 Y153.46 E.00264
; LINE_WIDTH: 0.394245
G1 F10246.945
G1 X120.23 Y153.53 E.00248
; LINE_WIDTH: 0.424012
G1 F9446.553
G1 X120.384 Y153.758 E.00855
G1 X120.992 Y153.977 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F9531.878
G1 X120.179 Y154.791 E.0354
; WIPE_START
G1 X120.992 Y153.977 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.636 Y158.334 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9531.878
G1 X118.456 Y156.514 E.07922
G3 X117.946 Y156.49 I-.183 J-1.577 E.0158
G1 X116.814 Y157.621 E.04924
G2 X116.695 Y157.206 I-3.141 J.674 E.0133
G1 X117.528 Y156.374 E.03624
G3 X117.174 Y156.194 I.334 J-1.095 E.01229
G1 X116.513 Y156.854 E.02876
G2 X116.282 Y156.551 I-1.266 J.727 E.01176
G1 X116.873 Y155.961 E.02572
G3 X116.62 Y155.679 I.674 J-.857 E.0117
G1 X115.998 Y156.301 E.02707
G1 X115.667 Y156.098 E.01196
G1 X116.418 Y155.347 E.0327
G3 X116.275 Y154.956 I4.439 J-1.84 E.01283
G1 X115.133 Y156.098 E.0497
; WIPE_START
G1 X116.275 Y154.956 E-.6137
G1 X116.407 Y155.317 E-.1463
; WIPE_END
G1 E-.04 F1800
G1 X113.986 Y156.496 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.147547
G1 F15000
G3 X114.347 Y156.441 I1.385 J7.904 E.00311
; LINE_WIDTH: 0.102985
G1 X114.423 Y156.434 E.00037
G1 X114.224 Y156.404 F30000
; LINE_WIDTH: 0.187987
G1 F15000
G1 X114.071 Y156.506 E.00217
; LINE_WIDTH: 0.155925
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112362
G1 X113.786 Y156.732 E.00126
G1 X113.201 Y157.87 F30000
; LINE_WIDTH: 0.353185
G1 F11603
G1 X113.066 Y157.689 E.00572
; LINE_WIDTH: 0.392509
G1 F10297.81
G1 X113.056 Y157.675 E.0005
G1 X113.317 Y157.165 E.01633
G1 X113.38 Y157.102 F30000
; LINE_WIDTH: 0.308349
G1 F13562.98
G1 X112.957 Y157.84 E.01839
G1 X112.935 Y157.837 F30000
; LINE_WIDTH: 0.235356
G1 F15000
G1 X113.447 Y157.035 E.01491
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.112755
G1 F15000
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.174767
G2 X112.909 Y157.834 I13.737 J10.159 E.00864
G1 X112.885 Y158.603 F30000
; LINE_WIDTH: 0.104939
G1 F15000
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.143639
G2 X112.931 Y158.826 I1.657 J-.315 E.00121
G1 X112.932 Y158.831 E.00004
; LINE_WIDTH: 0.193567
G2 X112.99 Y158.994 I2.253 J-.713 E.00212
G1 X112.993 Y159.001 E.00009
; LINE_WIDTH: 0.242059
G2 X113.065 Y159.144 I1.68 J-.748 E.0026
G1 X113.115 Y159.225 E.00155
; LINE_WIDTH: 0.284601
G1 F14895.664
G2 X113.289 Y159.439 I1.11 J-.722 E.00546
G1 X113.556 Y159.685 E.00714
; LINE_WIDTH: 0.331315
G1 F12482.878
G1 X113.699 Y159.8 E.00431
; LINE_WIDTH: 0.365949
G1 F11144.53
G1 X113.78 Y159.86 E.00263
; LINE_WIDTH: 0.394278
G1 F10245.963
G1 X113.849 Y159.911 E.00247
; LINE_WIDTH: 0.424383
G1 F9437.365
G1 X114.08 Y160.065 E.00863
G1 X115.118 Y159.852 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F9531.878
G1 X114.417 Y160.553 E.03049
G1 X114.684 Y160.82 E.01162
G1 X121.139 Y154.364 E.28097
G1 X121.407 Y154.631 E.01162
G1 X114.951 Y161.087 E.28097
G1 X115.218 Y161.354 E.01162
G1 X121.674 Y154.898 E.28097
G1 X121.941 Y155.166 E.01162
G1 X115.485 Y161.621 E.28097
G1 X115.752 Y161.888 E.01162
G1 X122.208 Y155.433 E.28097
G1 X122.475 Y155.7 E.01162
G1 X116.019 Y162.155 E.28097
G1 X116.286 Y162.422 E.01162
G1 X122.742 Y155.967 E.28097
G1 X123.009 Y156.234 E.01162
G1 X116.553 Y162.689 E.28097
G1 X116.821 Y162.956 E.01162
G1 X123.276 Y156.501 E.28097
G1 X123.543 Y156.768 E.01162
G1 X117.088 Y163.223 E.28097
G1 X117.355 Y163.49 E.01162
G1 X123.81 Y157.035 E.28097
G1 X124.077 Y157.302 E.01162
G1 X117.622 Y163.757 E.28097
G1 X117.889 Y164.025 E.01162
G1 X124.344 Y157.569 E.28097
G1 X124.611 Y157.836 E.01162
G1 X118.156 Y164.292 E.28097
G1 X118.423 Y164.559 E.01162
G1 X124.878 Y158.103 E.28097
G1 X125.145 Y158.37 E.01162
G1 X118.69 Y164.826 E.28097
G1 X118.957 Y165.093 E.01162
G1 X125.412 Y158.637 E.28097
G1 X125.679 Y158.904 E.01162
G1 X119.224 Y165.36 E.28097
G1 X119.491 Y165.627 E.01162
G1 X125.947 Y159.171 E.28097
G1 X126.214 Y159.439 E.01162
G1 X119.758 Y165.894 E.28097
G1 X120.025 Y166.161 E.01162
G1 X126.481 Y159.706 E.28097
G1 X126.748 Y159.973 E.01162
G1 X120.292 Y166.428 E.28096
G1 X120.559 Y166.695 E.01162
G1 X127.015 Y160.24 E.28096
G1 X127.282 Y160.507 E.01162
G1 X120.826 Y166.962 E.28096
G1 X121.094 Y167.229 E.01162
G1 X127.549 Y160.774 E.28096
G1 X127.816 Y161.041 E.01162
G1 X121.361 Y167.496 E.28096
G1 X121.628 Y167.763 E.01162
G1 X128.083 Y161.308 E.28096
G1 X128.35 Y161.575 E.01162
G1 X121.895 Y168.03 E.28096
G1 X122.162 Y168.297 E.01162
G1 X128.617 Y161.842 E.28096
G1 X128.884 Y162.109 E.01162
G1 X122.429 Y168.565 E.28096
G1 X122.696 Y168.832 E.01162
G1 X129.151 Y162.376 E.28096
G1 X129.418 Y162.643 E.01162
G1 X122.963 Y169.099 E.28096
G1 X123.23 Y169.366 E.01162
G1 X129.685 Y162.91 E.28096
G1 X129.952 Y163.177 E.01162
G1 X129.252 Y163.878 E.0305
G1 X130.292 Y163.66 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.406407
G1 F9904.066
G3 X130.59 Y163.87 I-4.671 J6.915 E.01081
; LINE_WIDTH: 0.367969
G1 F11075.277
G1 X130.66 Y163.922 E.00229
; LINE_WIDTH: 0.334095
G1 F12363.73
G1 X130.804 Y164.037 E.00439
; LINE_WIDTH: 0.285108
G1 F14864.503
G3 X131.193 Y164.419 I-1.982 J2.406 E.01077
G1 X131.254 Y164.506 E.00209
; LINE_WIDTH: 0.242078
G1 F15000
G3 X131.376 Y164.73 I-1.081 J.734 E.00415
; LINE_WIDTH: 0.193097
G3 X131.437 Y164.899 I-2.378 J.945 E.0022
; LINE_WIDTH: 0.143355
G3 X131.473 Y165.047 I-1.717 J.493 E.00125
; LINE_WIDTH: 0.104939
G1 X131.484 Y165.127 E.00041
G1 X131.166 Y165.859 F30000
; LINE_WIDTH: 0.387799
G1 F10438.456
G1 X131.315 Y166.055 E.0069
G3 X131.02 Y166.597 I-8.974 J-4.517 E.01735
G1 X130.986 Y166.631 F30000
; LINE_WIDTH: 0.306774
M73 P30 R7
G1 F13643.905
G1 X131.413 Y165.89 E.01839
G1 X131.433 Y165.893 F30000
; LINE_WIDTH: 0.235364
G1 F15000
G1 X131.16 Y166.323 E.00799
; LINE_WIDTH: 0.219997
G1 X131.121 Y166.381 E.001
; LINE_WIDTH: 0.191868
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155938
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112352
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112754
G1 F15000
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157466
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.190504
G1 X130.135 Y167.334 E.00229
G1 X129.925 Y167.301 F30000
; LINE_WIDTH: 0.105812
G1 F15000
G1 X130.02 Y167.293 E.00049
; LINE_WIDTH: 0.139059
G1 X130.16 Y167.274 E.00111
; LINE_WIDTH: 0.164622
G1 X130.377 Y167.241 E.00218
; WIPE_START
G1 X130.16 Y167.274 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X125.723 Y167.407 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F9531.878
G1 X127.53 Y165.6 E.07865
G2 X127.56 Y166.104 I1.447 J.168 E.01563
G1 X126.43 Y167.234 E.04917
G3 X126.842 Y167.356 I-.26 J1.625 E.01325
G1 X127.676 Y166.522 E.03632
G2 X127.856 Y166.876 I1.422 J-.502 E.01226
G1 X127.196 Y167.536 E.02876
G3 X127.497 Y167.769 I-.511 J.971 E.01178
G1 X128.091 Y167.176 E.02584
G2 X128.373 Y167.427 I.853 J-.676 E.0117
G1 X127.747 Y168.054 E.02728
G3 X127.952 Y168.383 I-1.147 J.942 E.01197
G1 X128.703 Y167.632 E.03269
G2 X129.099 Y167.77 I.829 J-1.74 E.01293
G1 X127.948 Y168.921 E.05008
; WIPE_START
G1 X129.099 Y167.77 E-.61837
G1 X128.906 Y167.719 E-.07576
G1 X128.747 Y167.651 E-.06588
; WIPE_END
G1 E-.04 F1800
G1 X127.561 Y170.057 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.164616
G1 F15000
G1 X127.594 Y169.84 E.00217
; LINE_WIDTH: 0.139054
G1 X127.612 Y169.7 E.0011
; LINE_WIDTH: 0.105814
G1 X127.621 Y169.606 E.00049
G1 X127.653 Y169.815 F30000
; LINE_WIDTH: 0.190118
G1 F15000
G1 X127.544 Y169.978 E.00235
; LINE_WIDTH: 0.155935
G1 X127.46 Y170.092 E.0013
; LINE_WIDTH: 0.112359
G1 X127.318 Y170.264 E.00126
G1 X126.896 Y170.721 F30000
; LINE_WIDTH: 0.385406
G1 F10511.391
G1 X126.208 Y171.073 E.02158
G1 X126.211 Y171.094 F30000
; LINE_WIDTH: 0.306817
G1 F13641.719
G1 X126.952 Y170.666 E.0184
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.112751
G1 F15000
G1 X126.874 Y170.679 E.00129
; LINE_WIDTH: 0.157475
G1 X126.758 Y170.763 E.00134
; LINE_WIDTH: 0.19306
G1 X126.7 Y170.802 E.00085
; LINE_WIDTH: 0.233578
G3 X126.213 Y171.114 I-7.43 J-11.056 E.00899
G1 X125.446 Y171.165 F30000
; LINE_WIDTH: 0.104949
G1 F15000
G1 X125.367 Y171.153 E.00041
; LINE_WIDTH: 0.143632
G3 X125.218 Y171.118 I.37 J-1.883 E.00125
; LINE_WIDTH: 0.193565
G3 X125.049 Y171.057 I.95 J-2.901 E.00221
; LINE_WIDTH: 0.24207
G3 X124.825 Y170.935 I.511 J-1.204 E.00414
; LINE_WIDTH: 0.285105
G1 F14864.663
G1 X124.739 Y170.873 E.0021
G3 X124.357 Y170.485 I2.025 J-2.371 E.01076
; LINE_WIDTH: 0.3341
G1 F12363.513
G1 X124.241 Y170.34 E.0044
; LINE_WIDTH: 0.367971
G1 F11075.183
G1 X124.19 Y170.27 E.00229
; LINE_WIDTH: 0.406398
G1 F9904.312
G3 X123.981 Y169.974 I6.699 J-4.966 E.01074
G1 X123.377 Y169.753 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F9531.878
G1 X124.192 Y168.938 E.03547
; OBJECT_ID: 795
; WIPE_START
G1 X123.377 Y169.753 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 795
M624 AQAAAAAAAAA=
G1 X128.897 Y164.481 Z.8 F30000
G1 X147.778 Y146.451 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X147.845 Y146.705 E.00871
G3 X146.021 Y145.304 I-1.674 J.292 E.27041
G3 X146.312 Y145.303 I.151 J2.16 E.00966
G3 X147.76 Y146.394 I-.141 J1.694 E.06343
M204 S250
G1 X147.399 Y146.552 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.055 Y145.695 I-1.23 J.445 E.19979
G3 X146.281 Y145.695 I.115 J1.681 E.00696
G3 X147.378 Y146.497 I-.112 J1.303 E.04389
; WIPE_START
M204 S10000
G1 X147.459 Y146.773 E-.10939
G1 X147.479 Y147 E-.08677
G1 X147.459 Y147.228 E-.08677
G1 X147.4 Y147.448 E-.08681
G1 X147.304 Y147.655 E-.08674
G1 X147.097 Y147.925 E-.12921
G1 X146.921 Y148.073 E-.08758
G1 X146.723 Y148.187 E-.08672
; WIPE_END
G1 E-.04 F1800
G1 X149.181 Y140.962 Z.8 F30000
G1 X150.499 Y137.088 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X150.727 Y136.958 E.00871
G3 X151.298 Y136.804 I.721 J1.539 E.01971
G3 X151.589 Y136.803 I.151 J2.152 E.00965
G3 X150.449 Y137.122 I-.141 J1.694 E.31413
M204 S250
G1 X150.695 Y137.428 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X151.332 Y137.195 I.752 J1.07 E.02108
G3 X151.558 Y137.195 I.115 J1.677 E.00696
G3 X150.647 Y137.463 I-.112 J1.303 E.2226
; WIPE_START
M204 S10000
G1 X150.892 Y137.313 E-.10942
G1 X151.107 Y137.235 E-.08678
G1 X151.332 Y137.195 E-.0868
G1 X151.558 Y137.195 E-.08598
G1 X151.785 Y137.235 E-.08762
G1 X152 Y137.313 E-.08676
G1 X152.172 Y137.41 E-.07505
G1 X152.373 Y137.574 E-.09847
G1 X152.446 Y137.661 E-.04312
; WIPE_END
G1 E-.04 F1800
G1 X159.799 Y135.615 Z.8 F30000
G1 X161.811 Y135.055 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X161.459 Y135.102 E.01178
G1 X150.433 Y135.102 E.36577
G3 X148.844 Y133.513 I.027 J-1.616 E.08241
G1 X148.844 Y130.487 E.1004
G3 X150.433 Y128.898 I1.621 J.032 E.08234
G1 X161.459 Y128.898 E.36577
G3 X163.048 Y130.487 I-.027 J1.616 E.08241
G1 X163.048 Y133.513 E.1004
G3 X161.87 Y135.042 I-1.616 J-.027 E.06861
M204 S250
G1 X161.759 Y134.667 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X161.451 Y134.71 I-.323 J-1.177 E.00958
G1 X150.441 Y134.71 E.33829
G3 X149.236 Y133.505 I.016 J-1.221 E.05798
G1 X149.236 Y130.495 E.09247
G3 X150.441 Y129.29 I1.225 J.02 E.05792
G1 X161.451 Y129.29 E.33829
G3 X162.656 Y130.495 I-.016 J1.221 E.05798
G1 X162.656 Y133.505 E.09247
G3 X161.816 Y134.649 I-1.221 J-.016 E.04655
; WIPE_START
M204 S10000
G1 X161.451 Y134.71 E-.14076
G1 X159.821 Y134.71 E-.61924
; WIPE_END
G1 E-.04 F1800
G1 X152.619 Y132.183 Z.8 F30000
G1 X145.222 Y129.588 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X145.45 Y129.458 E.00871
G3 X146.021 Y129.304 I.721 J1.539 E.01971
G3 X146.311 Y129.303 I.151 J2.152 E.00965
G3 X145.172 Y129.622 I-.141 J1.694 E.31413
M204 S250
G1 X145.418 Y129.928 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.055 Y129.695 I.752 J1.07 E.02108
G3 X146.281 Y129.695 I.115 J1.677 E.00696
G3 X145.37 Y129.963 I-.112 J1.303 E.2226
; WIPE_START
M204 S10000
G1 X145.615 Y129.813 E-.10942
G1 X145.83 Y129.735 E-.08676
G1 X146.055 Y129.695 E-.08681
G1 X146.281 Y129.695 E-.08598
G1 X146.508 Y129.735 E-.08762
G1 X146.723 Y129.813 E-.08677
G1 X146.921 Y129.927 E-.08679
G1 X147.096 Y130.074 E-.08677
G1 X147.165 Y130.164 E-.04308
; WIPE_END
G1 E-.04 F1800
G1 X141.964 Y135.75 Z.8 F30000
G1 X132.532 Y145.885 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X132.543 Y145.705 E.00596
G3 X132.762 Y145.023 I2.084 J.293 E.02389
G1 X133.298 Y144.104 E.0353
G2 X133.996 Y135.521 I-9.741 J-5.113 E.29348
G2 X132.762 Y132.977 I-11.995 J4.249 E.094
G3 X134.611 Y129.898 I1.875 J-.969 E.1425
G1 X141.682 Y129.898 E.23458
G3 X143.771 Y131.987 I-.032 J2.121 E.10839
G1 X143.771 Y146.013 E.46529
G3 X141.682 Y148.102 I-2.112 J-.023 E.10851
G1 X134.611 Y148.102 E.23458
G3 X132.523 Y146.064 I.016 J-2.104 E.10693
G1 X132.529 Y145.945 E.00397
M204 S250
G1 X132.917 Y145.906 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X133.109 Y145.206 I1.709 J.092 E.02248
G1 X133.644 Y144.287 E.03266
G2 X134.368 Y135.396 I-10.092 J-5.297 E.28164
G2 X133.109 Y132.795 I-12.328 J4.361 E.08899
G3 X134.619 Y130.29 I1.525 J-.788 E.10754
G1 X141.674 Y130.29 E.21677
G3 X143.379 Y131.995 I-.02 J1.726 E.08205
G1 X143.379 Y146.005 E.43047
G3 X141.674 Y147.71 I-1.718 J-.013 E.08214
G1 X134.619 Y147.71 E.21677
G3 X132.915 Y145.966 I.007 J-1.712 E.0834
; WIPE_START
M204 S10000
G1 X132.957 Y145.616 E-.13377
G1 X133.03 Y145.383 E-.09308
G1 X133.109 Y145.206 E-.07366
G1 X133.644 Y144.287 E-.40389
G1 X133.708 Y144.155 E-.05561
; WIPE_END
G1 E-.04 F1800
G1 X127.498 Y139.718 Z.8 F30000
G1 X116.514 Y131.869 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X116.534 Y131.865 E.00067
G3 X123.394 Y128.909 I7.142 J7.139 E.25383
G3 X133.162 Y135.545 I.265 J10.118 E.41824
G3 X115.939 Y132.514 I-9.487 J3.459 E1.40321
G1 X116.474 Y131.914 E.02666
M204 S250
G1 X116.811 Y132.142 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X123.412 Y129.301 I6.865 J6.861 E.22619
G3 X132.469 Y134.896 I.249 J9.726 E.34616
G3 X116.769 Y132.185 I-8.794 J4.107 E1.2995
; WIPE_START
M204 S10000
G1 X117.427 Y131.562 E-.34453
G1 X118.099 Y131.046 E-.32186
G1 X118.307 Y130.914 E-.09361
; WIPE_END
G1 E-.04 F1800
G1 X123.569 Y136.442 Z.8 F30000
G1 X155.975 Y170.487 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X155.178 Y170.152 E.02867
G3 X159.172 Y150.909 I4.274 J-9.149 E.89661
G3 X168.94 Y157.545 I.265 J10.118 E.41824
G3 X156.032 Y170.504 I-9.487 J3.459 E.759
M204 S250
G1 X156.126 Y170.121 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X159.189 Y151.301 I3.326 J-9.118 E.82447
G3 X168.247 Y156.896 I.27 J9.693 E.34631
G3 X156.183 Y170.141 I-8.794 J4.107 E.70122
; WIPE_START
M204 S10000
G1 X155.342 Y169.801 E-.34462
G1 X154.591 Y169.409 E-.32187
M73 P31 R7
G1 X154.384 Y169.277 E-.09351
; WIPE_END
G1 E-.04 F1800
G1 X157.403 Y162.268 Z.8 F30000
G1 X166.285 Y141.652 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.317 Y141.648 E.00106
G3 X168.548 Y143.733 I.128 J2.1 E.11336
G1 X168.548 Y150.058 E.20983
G3 X165.469 Y151.907 I-2.104 J-.016 E.14276
G1 X164.549 Y151.371 E.0353
G2 X155.967 Y150.673 I-5.103 J9.629 E.29363
G2 X153.423 Y151.907 I4.248 J11.993 E.094
G3 X150.374 Y150.404 I-.975 J-1.866 E.13125
G3 X150.344 Y149.326 I6.158 J-.712 E.03582
G3 X151.655 Y147.391 I2.109 J.017 E.08215
G1 X165.678 Y141.789 E.50094
G3 X166.009 Y141.697 I.922 J2.672 E.01138
G1 X166.226 Y141.662 E.0073
M204 S250
G1 X166.336 Y142.04 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X168.156 Y143.741 I.109 J1.708 E.08573
G1 X168.156 Y150.05 E.19386
G3 X165.652 Y151.56 I-1.712 J-.007 E.10773
G1 X164.733 Y151.025 E.03266
G2 X155.842 Y150.301 I-5.287 J9.976 E.28179
G2 X153.241 Y151.56 I4.361 J12.327 E.08899
G3 X150.761 Y150.337 I-.793 J-1.518 E.09888
G3 X150.736 Y149.334 I5.791 J-.645 E.03087
G3 X151.808 Y147.752 I1.717 J.009 E.06226
G1 X165.816 Y142.156 E.46351
G3 X166.277 Y142.047 I.757 J2.175 E.01458
; WIPE_START
M204 S10000
G1 X166.666 Y142.049 E-.14791
G1 X166.949 Y142.111 E-.11008
G1 X167.086 Y142.159 E-.05508
G1 X167.344 Y142.29 E-.11014
G1 X167.577 Y142.463 E-.11014
G1 X167.682 Y142.563 E-.05504
G1 X167.864 Y142.789 E-.11014
G1 X167.942 Y142.93 E-.06146
; WIPE_END
G1 E-.04 F1800
G1 X165.778 Y138.171 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X165.849 Y137.919 E.0087
G3 X167.298 Y136.804 I1.598 J.578 E.06401
G3 X167.588 Y136.803 I.151 J2.152 E.00965
G3 X165.769 Y138.231 I-.141 J1.694 E.26984
M204 S250
G1 X166.158 Y138.273 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X167.332 Y137.195 I1.288 J.225 E.05266
G3 X167.558 Y137.195 I.115 J1.677 E.00696
G3 X166.149 Y138.332 I-.112 J1.303 E.19102
; WIPE_START
M204 S10000
G1 X166.215 Y138.052 E-.10942
G1 X166.356 Y137.775 E-.11828
G1 X166.52 Y137.574 E-.09845
G1 X166.695 Y137.427 E-.08675
G1 X166.892 Y137.313 E-.08684
G1 X167.107 Y137.235 E-.08676
G1 X167.332 Y137.195 E-.08679
G1 X167.558 Y137.195 E-.08598
G1 X167.56 Y137.195 E-.00074
; WIPE_END
G1 E-.04 F1800
G1 X160.219 Y139.282 Z.8 F30000
G1 X128.082 Y148.419 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X127.169 Y148.791 E.03272
G3 X123.387 Y128.606 I-3.491 J-9.793 E1.19188
G1 X158.73 Y127.603 E1.17285
G1 X159.425 Y127.632 E.0231
G1 X159.707 Y127.644 E.00935
G3 X170.125 Y138.631 I-1.003 J11.384 E.54897
G1 X169.843 Y161.118 E.74599
; object ids of layer 2 start: 795,817,839,861
M624 DwAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer2 end: 795,817,839,861
M625
G3 X149.447 Y158.151 I-10.396 J-.126 E1.1747
G1 X149.877 Y156.852 E.04541
G2 X147.433 Y150.558 I-5.416 J-1.518 E.24023
G1 X145.26 Y149.222 E.08462
G2 X142.347 Y148.398 I-2.994 J5.023 E.10156
G1 X128.138 Y148.398 E.47134
M204 S250
G1 X128.211 Y148.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X123.367 Y128.214 I-4.533 J-9.791 E1.17577
G1 X158.732 Y127.21 E1.08711
G1 X159.442 Y127.241 E.02182
G1 X159.74 Y127.253 E.00918
G3 X170.518 Y138.618 I-1.038 J11.776 E.52604
G1 X170.235 Y161.131 E.6918
G3 X149.069 Y158.044 I-10.788 J-.139 E1.12892
G1 X149.5 Y156.745 E.04205
G2 X147.22 Y150.888 I-5.038 J-1.411 E.20716
G1 X145.061 Y149.56 E.07789
G2 X142.339 Y148.79 I-2.79 J4.668 E.08791
G1 X128.271 Y148.79 E.4323
M204 S10000
G1 X128.393 Y148.185 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.331146
G1 F12490.228
G1 X129.207 Y147.967 E.01979
G1 X131.546 Y147.111 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.5849
G1 F6642.312
G2 X131.55 Y147.221 I-.029 J.056 E.01173
G1 X132.28 Y147.629 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X132.028 Y147.227 E.0146
G1 X131.857 Y146.767 E.01508
G1 X131.766 Y146.242 E.01635
G1 X131.374 Y146.67 E.01782
G1 X130.676 Y147.312 E.02914
G1 X130.249 Y147.629 E.01632
G1 X132.22 Y147.629 E.06056
G1 X132.895 Y147.789 F30000
G1 F9547.299
G1 X132.728 Y147.62 E.00729
G1 X132.398 Y147.125 E.01829
G3 X132.155 Y145.694 I2.354 J-1.135 E.0452
G1 X131.87 Y145.537 E.01002
G3 X130.421 Y147.034 I-8.806 J-7.067 E.06411
G3 X129.537 Y147.684 I-262.108 J-356.104 E.03372
G1 X129.623 Y148.006 E.01025
G1 X132.827 Y148.006 E.09844
G1 X132.826 Y147.873 E.00408
G1 X132.857 Y147.835 E.00151
G1 X133.297 Y147.916 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.12099
G1 F15000
G1 X133.464 Y148.052 E.00137
; LINE_WIDTH: 0.16541
G1 X133.654 Y148.194 E.00237
G1 X133.791 Y148.173 F30000
; LINE_WIDTH: 0.133894
G1 F15000
G3 X133.437 Y148.099 I1.489 J-8.021 E.00268
; WIPE_START
G1 X133.791 Y148.173 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.17 Y145.255 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.474755
G1 F8336.53
G1 X132.397 Y144.842 E.01659
; LINE_WIDTH: 0.431339
G1 F9268.358
G3 X132.754 Y144.255 I13.558 J7.853 E.02174
G2 X132.406 Y133.174 I-9.076 J-5.261 E.3697
; LINE_WIDTH: 0.473817
G1 F8354.671
G1 X132.17 Y132.746 E.01717
G1 X131.628 Y132.524 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X132.191 Y131.96 E.02458
G3 X132.281 Y131.335 I2.102 J-.017 E.01957
G1 X131.501 Y132.115 E.03402
G1 X131.245 Y131.835 E.01169
G1 X134.456 Y128.625 E.14006
G1 X135.007 Y128.609 E.01701
G1 X133.956 Y129.66 E.04585
G3 X134.586 Y129.566 I.665 J2.281 E.01971
G1 X135.558 Y128.594 E.04241
G1 X136.109 Y128.578 E.01701
G1 X135.122 Y129.565 E.04305
G1 X135.657 Y129.565 E.01652
G1 X136.66 Y128.562 E.04373
G1 X137.211 Y128.547 E.01701
G1 X136.193 Y129.565 E.04442
G1 X136.728 Y129.565 E.01652
G1 X137.762 Y128.531 E.0451
G1 X138.313 Y128.515 E.01701
G1 X137.264 Y129.565 E.04578
G1 X137.799 Y129.565 E.01652
G1 X138.864 Y128.5 E.04646
G1 X139.415 Y128.484 E.01701
G1 X138.334 Y129.565 E.04715
G1 X138.87 Y129.565 E.01652
G1 X139.966 Y128.469 E.04783
G1 X140.517 Y128.453 E.01701
G1 X139.405 Y129.565 E.04851
G1 X139.94 Y129.565 E.01652
G1 X141.068 Y128.437 E.04919
G1 X141.619 Y128.422 E.01701
G1 X140.476 Y129.565 E.04988
G1 X141.011 Y129.565 E.01652
G1 X142.17 Y128.406 E.05056
G1 X142.721 Y128.39 E.01701
G1 X141.547 Y129.565 E.05124
G3 X142.05 Y129.596 I.075 J2.839 E.01559
G1 X143.272 Y128.375 E.0533
G1 X143.823 Y128.359 E.01701
G1 X142.479 Y129.704 E.05866
G3 X142.847 Y129.871 I-2.004 J4.892 E.01247
G1 X144.374 Y128.343 E.06664
G1 X144.925 Y128.328 E.01701
G1 X143.166 Y130.087 E.07675
G3 X143.449 Y130.34 I-.818 J1.199 E.01173
G1 X145.476 Y128.312 E.08846
G1 X146.027 Y128.296 E.01701
G1 X143.562 Y130.762 E.10756
G1 X144.095 Y131.189 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.382438
G1 F10603.266
G1 X144.254 Y130.982 E.00722
G1 X144.095 Y131.189 F30000
; LINE_WIDTH: 0.413697
G1 F9709.35
G1 X144.08 Y131.21 E.00077
; LINE_WIDTH: 0.44913
G1 F8862.416
G1 X144.065 Y131.23 E.00085
; LINE_WIDTH: 0.450714
G1 F8828.004
G1 X144.168 Y131.695 E.01581
G1 X144.195 Y131.71 E.00104
; LINE_WIDTH: 0.410185
G1 F9802.183
G1 X144.445 Y131.836 E.00836
G1 X144.293 Y132.172 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X144.104 Y132.361 E.00823
G1 X144.104 Y132.897 E.01652
G1 X144.65 Y132.351 E.02382
G2 X144.928 Y132.608 I.869 J-.659 E.01175
G1 X144.104 Y133.432 E.03596
G1 X144.103 Y133.968 E.01652
G1 X145.257 Y132.814 E.05035
G2 X145.646 Y132.961 I.607 J-1.016 E.01287
G1 X144.103 Y134.504 E.0673
G1 X144.103 Y135.039 E.01652
G1 X146.113 Y133.029 E.08769
G2 X146.726 Y132.952 I.094 J-1.716 E.01916
G1 X143.933 Y135.745 E.12185
; WIPE_START
G1 X145.347 Y134.331 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.99 Y130.617 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X148.568 Y130.039 E.02522
G2 X148.516 Y130.626 I1.658 J.443 E.01828
G1 X148.198 Y130.944 E.01386
G3 X148.137 Y131.527 I-1.685 J.117 E.0182
G1 X148.129 Y131.548 E.00069
G1 X148.515 Y131.162 E.01684
G1 X148.514 Y131.699 E.01654
G1 X144.102 Y136.111 E.19248
G1 X144.102 Y136.646 E.01652
G1 X148.513 Y132.235 E.19245
G1 X148.512 Y132.771 E.01654
G1 X144.102 Y137.182 E.19242
M73 P32 R7
G1 X144.101 Y137.718 E.01652
G1 X148.511 Y133.308 E.19239
G2 X148.537 Y133.818 I2.802 J.115 E.01577
G1 X144.101 Y138.253 E.19352
G1 X144.101 Y138.789 E.01652
G1 X148.656 Y134.233 E.19874
G2 X148.843 Y134.582 I1.417 J-.533 E.01224
G1 X144.1 Y139.325 E.20689
G1 X144.1 Y139.86 E.01652
G1 X149.085 Y134.876 E.21745
G2 X149.384 Y135.112 I1.047 J-1.02 E.01179
G1 X144.1 Y140.396 E.23052
G1 X144.1 Y140.932 E.01652
G1 X149.736 Y135.295 E.2459
G2 X150.164 Y135.402 I.459 J-.927 E.01373
G1 X144.099 Y141.467 E.2646
G1 X144.099 Y142.003 E.01652
G1 X150.667 Y135.435 E.28653
G1 X151.203 Y135.435 E.01652
G1 X143.929 Y142.708 E.31732
G1 X144.442 Y146.163 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.429816
G1 F9304.835
G1 X144.18 Y146.298 E.00931
; LINE_WIDTH: 0.451624
G1 F8808.343
G1 X144.065 Y146.77 E.01615
; LINE_WIDTH: 0.449137
G1 F8862.266
G1 X144.08 Y146.79 E.00085
; LINE_WIDTH: 0.413774
G1 F9707.324
G1 X144.095 Y146.811 E.00077
; LINE_WIDTH: 0.382524
G1 F10600.581
G1 X144.254 Y147.018 E.00723
G1 X144.681 Y148.208 F30000
; LINE_WIDTH: 0.401514
G1 F10039.221
G1 X144.697 Y148.491 E.00828
G1 X144.765 Y148.537 E.00238
; LINE_WIDTH: 0.384377
G1 F10543.068
G1 X144.833 Y148.582 E.00227
; LINE_WIDTH: 0.351171
G1 F11678.824
G1 X144.988 Y148.676 E.00456
; LINE_WIDTH: 0.324131
G1 F12801.799
G1 X145.472 Y148.936 E.01258
; LINE_WIDTH: 0.369294
G1 F11030.293
G1 X145.649 Y149.016 E.00518
; LINE_WIDTH: 0.418482
G1 F9585.644
G1 X145.965 Y149.141 E.0104
G1 X146.157 Y149.582 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X147.168 Y148.571 E.04411
; WIPE_START
G1 X146.157 Y149.582 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.126 Y145.4 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X152.108 Y140.419 E.21732
G3 X151.462 Y140.529 I-.663 J-1.933 E.0203
G1 X146.889 Y145.102 E.19951
G2 X146.464 Y144.992 I-.525 J1.142 E.01361
G1 X150.98 Y140.476 E.19699
G3 X150.584 Y140.337 I.192 J-1.179 E.01302
G1 X145.941 Y144.98 E.20255
G2 X145.126 Y145.259 I.265 J2.1 E.02675
G1 X150.247 Y140.138 E.22342
G3 X149.963 Y139.887 I.57 J-.931 E.01176
G1 X144.199 Y145.651 E.25146
G1 X144.097 Y145.706 E.00359
G1 X144.097 Y145.217 E.0151
G1 X149.729 Y139.586 E.24568
G3 X149.551 Y139.228 I1.245 J-.84 E.01236
G1 X144.098 Y144.681 E.23793
G1 X144.098 Y144.146 E.01652
G1 X149.439 Y138.804 E.23302
G3 X149.417 Y138.323 I1.355 J-.304 E.01494
G1 X149.424 Y138.285 E.0012
G1 X144.098 Y143.61 E.23232
G1 X144.098 Y143.074 E.01652
G1 X151.738 Y135.435 E.33329
G1 X152.274 Y135.434 E.01652
G1 X151.231 Y136.477 E.04551
G3 X151.75 Y136.493 I.187 J2.411 E.01607
G1 X152.809 Y135.434 E.04621
G1 X153.345 Y135.434 E.01652
G1 X152.174 Y136.605 E.05111
G3 X152.532 Y136.783 I-.487 J1.432 E.01236
G1 X153.881 Y135.434 E.05885
G1 X154.416 Y135.433 E.01652
G1 X152.833 Y137.017 E.06909
G3 X153.084 Y137.301 I-.677 J.852 E.01176
G1 X154.952 Y135.433 E.0815
G1 X155.488 Y135.433 E.01652
G1 X153.288 Y137.633 E.09597
G3 X153.412 Y137.966 I-1.233 J.65 E.01102
G1 X153.424 Y138.032 E.00205
G1 X156.023 Y135.433 E.1134
G1 X156.559 Y135.432 E.01652
G1 X153.475 Y138.516 E.13452
G3 X153.365 Y139.162 I-2.008 J-.012 E.02032
G1 X157.095 Y135.432 E.16272
G1 X157.63 Y135.432 E.01652
G1 X147.55 Y145.512 E.43975
G3 X147.806 Y145.792 I-.929 J1.105 E.01172
G1 X158.166 Y135.431 E.45198
G1 X158.702 Y135.431 E.01652
G1 X148.008 Y146.125 E.46653
G1 X148.145 Y146.523 E.01299
G1 X159.237 Y135.431 E.48389
G1 X159.773 Y135.431 E.01652
G1 X148.198 Y147.005 E.50495
G3 X148.094 Y147.645 I-2.059 J-.008 E.02008
G1 X160.308 Y135.43 E.53288
G1 X160.844 Y135.43 E.01652
G1 X146.612 Y149.662 E.6209
G1 X146.943 Y149.866 E.01201
G1 X161.38 Y135.43 E.62981
G2 X161.994 Y135.351 I.096 J-1.685 E.01921
G1 X147.275 Y150.07 E.64214
G1 X147.607 Y150.274 E.01201
G1 X166.624 Y131.256 E.82968
G1 X166.885 Y131.531 E.01168
G1 X147.926 Y150.49 E.8271
G3 X148.229 Y150.722 I-1.19 J1.863 E.01179
G1 X150.051 Y148.9 E.07948
G2 X150.012 Y149.474 I4.613 J.599 E.01776
G1 X148.516 Y150.97 E.06525
G1 X148.789 Y151.233 E.01168
G1 X150.016 Y150.006 E.05355
G2 X150.064 Y150.494 I1.345 J.116 E.01521
G1 X149.037 Y151.52 E.04479
G1 X149.269 Y151.824 E.01178
G1 X150.177 Y150.915 E.03963
G2 X150.348 Y151.28 I2.023 J-.724 E.01244
G1 X149.491 Y152.137 E.03739
G1 X149.693 Y152.471 E.01203
G1 X150.573 Y151.591 E.0384
G2 X150.831 Y151.868 I1.205 J-.862 E.01172
G1 X149.87 Y152.829 E.04194
G3 X150.027 Y153.207 I-2.1 J1.098 E.01264
G1 X151.138 Y152.096 E.04844
G1 X151.489 Y152.281 E.01223
G1 X150.164 Y153.606 E.05781
G3 X150.276 Y154.029 I-2.384 J.859 E.01352
G1 X151.894 Y152.411 E.07058
G2 X152.368 Y152.472 I.415 J-1.34 E.01482
G1 X150.36 Y154.48 E.08759
G3 X150.41 Y154.965 I-2.77 J.532 E.01507
G1 X152.834 Y152.541 E.10576
G1 X152.986 Y152.815 E.00966
G2 X150.899 Y155.012 I6.221 J7.999 E.09381
G1 X150.634 Y155.277 E.01157
G1 X150.518 Y155.413 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.243802
G1 F15000
G1 X150.361 Y155.938 E.00897
; LINE_WIDTH: 0.217952
G1 X150.313 Y156.085 E.00221
; LINE_WIDTH: 0.169541
G1 X150.265 Y156.233 E.0016
; LINE_WIDTH: 0.121129
G1 X150.218 Y156.38 E.00099
G1 X150.224 Y156.382 F30000
; LINE_WIDTH: 0.310284
G1 F13464.832
G1 X150.515 Y155.412 E.02206
G1 X153.192 Y152.499 F30000
; LINE_WIDTH: 0.474748
G1 F8336.651
G1 X153.605 Y152.272 E.01658
; LINE_WIDTH: 0.431337
G1 F9268.405
G3 X165.272 Y152.263 I5.841 J8.741 E.39148
; LINE_WIDTH: 0.473815
G1 F8354.718
G1 X165.701 Y152.499 E.01718
G1 X165.807 Y152.953 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X166.285 Y152.475 E.02085
G1 X166.731 Y152.466 E.01378
G1 X166.858 Y152.438 E.00399
G1 X166.105 Y153.191 E.03284
; WIPE_START
G1 X166.858 Y152.438 E-.40451
G1 X166.731 Y152.466 E-.04918
G1 X166.285 Y152.475 E-.16969
G1 X166.031 Y152.729 E-.13663
; WIPE_END
G1 E-.04 F1800
G1 X168.998 Y157.258 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X169.566 Y156.69 E.02479
G1 X169.573 Y156.148 E.01673
G1 X168.971 Y156.749 E.02626
G2 X168.799 Y156.386 I-2.163 J.802 E.01242
G1 X169.579 Y155.605 E.03406
G1 X169.586 Y155.063 E.01673
G1 X168.615 Y156.034 E.04236
G2 X168.425 Y155.689 I-2.066 J.915 E.01217
G1 X169.593 Y154.521 E.05096
G1 X169.6 Y153.979 E.01673
G1 X168.217 Y155.362 E.06035
G1 X168.008 Y155.035 E.01196
G1 X169.607 Y153.437 E.06973
G1 X169.613 Y152.894 E.01673
G1 X167.777 Y154.731 E.0801
G1 X167.545 Y154.428 E.01178
G1 X169.62 Y152.352 E.09054
G1 X169.627 Y151.81 E.01673
G1 X167.299 Y154.138 E.10154
G1 X167.043 Y153.858 E.01169
G1 X169.634 Y151.268 E.11301
G1 X169.641 Y150.726 E.01673
G1 X166.784 Y153.582 E.12463
G1 X166.505 Y153.326 E.01169
G1 X169.647 Y150.184 E.13711
G1 X169.654 Y149.641 E.01673
G1 X168.839 Y150.456 E.03555
G2 X168.874 Y149.886 I-1.632 J-.386 E.01771
G1 X169.661 Y149.099 E.03432
G1 X169.668 Y148.557 E.01673
G1 X168.874 Y149.351 E.03462
G1 X168.874 Y148.815 E.01652
G1 X169.675 Y148.015 E.03491
G1 X169.681 Y147.473 E.01673
G1 X168.874 Y148.28 E.03521
M73 P32 R6
G1 X168.874 Y147.744 E.01652
G1 X169.688 Y146.931 E.0355
G1 X169.695 Y146.388 E.01673
G1 X168.874 Y147.209 E.0358
G1 X168.874 Y146.674 E.01652
G1 X169.702 Y145.846 E.0361
G1 X169.709 Y145.304 E.01673
G1 X168.874 Y146.138 E.03639
G1 X168.874 Y145.603 E.01652
G1 X169.715 Y144.762 E.03669
G1 X169.722 Y144.22 E.01673
G1 X168.874 Y145.067 E.03699
G1 X168.874 Y144.532 E.01652
G1 X169.729 Y143.677 E.03728
G1 X169.736 Y143.135 E.01673
G1 X168.874 Y143.997 E.03758
G1 X168.863 Y143.473 E.01617
G1 X169.743 Y142.593 E.03837
G1 X169.749 Y142.051 E.01673
G1 X168.772 Y143.028 E.04264
G2 X168.616 Y142.649 I-1.558 J.422 E.01268
G1 X169.756 Y141.509 E.04976
G1 X169.763 Y140.967 E.01673
G1 X168.412 Y142.318 E.05894
G2 X168.165 Y142.029 I-.966 J.578 E.01177
G1 X169.77 Y140.424 E.07001
G1 X169.776 Y139.882 E.01673
G1 X167.876 Y141.783 E.08291
G2 X167.544 Y141.579 I-.759 J.868 E.01207
G1 X169.783 Y139.34 E.0977
G1 X169.79 Y138.798 E.01673
G1 X167.169 Y141.419 E.11436
G1 X166.725 Y141.327 E.01397
G1 X167.523 Y140.529 E.0348
G3 X167.028 Y140.489 I-.108 J-1.733 E.01537
M73 P33 R6
G1 X166.188 Y141.329 E.03665
G2 X165.468 Y141.514 I.385 J2.999 E.02299
G1 X166.625 Y140.356 E.0505
G3 X166.283 Y140.163 I.373 J-1.061 E.01219
G1 X164.577 Y141.87 E.07446
G1 X163.685 Y142.226 E.02962
G1 X165.994 Y139.917 E.10072
G3 X165.754 Y139.622 I.72 J-.827 E.0118
G1 X162.793 Y142.582 E.12916
G1 X161.902 Y142.938 E.02962
G1 X165.567 Y139.273 E.15991
G3 X165.448 Y138.857 I1.408 J-.628 E.0134
G1 X161.01 Y143.295 E.19362
G1 X160.119 Y143.651 E.02962
G1 X165.62 Y138.15 E.23998
; WIPE_START
G1 X164.205 Y139.564 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.288 Y138.764 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X169.765 Y138.287 E.02082
G1 X169.728 Y137.789 E.0154
G1 X169.427 Y138.09 E.01311
G2 X169.303 Y137.679 I-1.023 J.087 E.01333
G1 X169.66 Y137.322 E.0156
G1 X169.585 Y136.861 E.0144
G1 X169.109 Y137.337 E.02077
G2 X168.863 Y137.048 I-.94 J.549 E.01178
G1 X169.485 Y136.426 E.02711
G1 X169.377 Y135.998 E.01361
G1 X168.568 Y136.808 E.03531
G2 X168.219 Y136.622 I-.87 J1.212 E.01224
G1 X169.25 Y135.59 E.04502
G1 X169.113 Y135.192 E.01299
G1 X167.803 Y136.502 E.05719
G2 X167.299 Y136.471 I-.341 J1.399 E.01565
G1 X168.965 Y134.804 E.0727
G1 X168.801 Y134.433 E.01252
G1 X159.227 Y144.007 E.41766
G1 X158.336 Y144.363 E.02962
G1 X168.635 Y134.064 E.4493
G1 X168.445 Y133.719 E.01216
G1 X157.444 Y144.719 E.47991
G1 X156.553 Y145.075 E.02962
G1 X168.255 Y133.373 E.51053
G2 X168.048 Y133.044 I-2.024 J1.04 E.012
G1 X155.661 Y145.432 E.54042
G1 X154.77 Y145.788 E.02962
G1 X167.834 Y132.723 E.56997
G2 X167.615 Y132.407 I-1.952 J1.123 E.01188
G1 X153.878 Y146.144 E.59929
G1 X152.986 Y146.5 E.02962
G1 X167.377 Y132.109 E.62782
G1 X167.14 Y131.812 E.01175
G1 X151.791 Y147.161 E.66962
; WIPE_START
G1 X153.205 Y145.746 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.773 Y147.485 Z.8 F30000
G1 X143.388 Y148.044 Z.8
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.5542
G1 F7041.152
G3 X144.019 Y148.187 I-.442 J3.399 E.02699
G1 X144.026 Y147.938 E.01039
G1 X144.173 Y147.798 E.00842
G1 X144.132 Y147.655 E.0062
G1 X144.077 Y147.675 E.00248
G3 X143.757 Y147.485 I.113 J-.553 E.01581
G1 X143.351 Y147.916 E.02466
G1 X143.396 Y147.986 E.00348
G1 X142.855 Y148.007 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.109678
G1 F15000
G1 X142.763 Y148.071 E.0006
; LINE_WIDTH: 0.138429
G1 X142.655 Y148.148 E.00103
G1 X142.698 Y148.208 E.00057
; WIPE_START
G1 X142.655 Y148.148 E-.26999
G1 X142.763 Y148.071 E-.49001
; WIPE_END
G1 E-.04 F1800
G1 X143.918 Y140.526 Z.8 F30000
G1 X145.649 Y129.211 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X146.578 Y128.281 E.04056
G1 X147.129 Y128.265 E.01701
G1 X146.414 Y128.981 E.03121
G3 X146.849 Y129.081 I-.165 J1.7 E.0138
G1 X147.68 Y128.25 E.03629
G1 X148.231 Y128.234 E.01701
G1 X147.212 Y129.253 E.04447
G1 X147.52 Y129.481 E.01181
G1 X148.782 Y128.218 E.05508
G1 X149.333 Y128.203 E.01701
G1 X147.777 Y129.759 E.06789
G3 X147.983 Y130.088 I-.831 J.748 E.01205
G1 X149.884 Y128.187 E.08295
G1 X150.435 Y128.171 E.01701
G1 X149.985 Y128.622 E.01967
G3 X150.577 Y128.565 I.509 J2.173 E.01842
G1 X150.986 Y128.156 E.01785
G1 X151.537 Y128.14 E.01701
G1 X151.113 Y128.565 E.01853
G1 X151.648 Y128.565 E.01652
G1 X152.089 Y128.124 E.01922
G1 X152.64 Y128.109 E.01701
G1 X152.183 Y128.565 E.0199
G1 X152.719 Y128.565 E.01652
G1 X153.191 Y128.093 E.02058
G1 X153.742 Y128.077 E.01701
G1 X153.254 Y128.565 E.02126
G1 X153.79 Y128.565 E.01652
G1 X154.293 Y128.062 E.02195
G1 X154.844 Y128.046 E.01701
G1 X154.325 Y128.565 E.02263
G1 X154.86 Y128.565 E.01652
G1 X155.395 Y128.031 E.02331
G1 X155.946 Y128.015 E.01701
G1 X155.396 Y128.565 E.024
G1 X155.931 Y128.565 E.01652
G1 X156.497 Y127.999 E.02468
G1 X157.048 Y127.984 E.01701
G1 X156.466 Y128.565 E.02536
G1 X157.002 Y128.565 E.01652
G1 X157.599 Y127.968 E.02604
G1 X158.15 Y127.952 E.01701
G1 X157.537 Y128.565 E.02672
G1 X158.073 Y128.565 E.01652
G1 X158.701 Y127.937 E.02741
G3 X159.216 Y127.957 I.116 J3.631 E.01592
G1 X158.608 Y128.565 E.02653
G1 X159.143 Y128.565 E.01652
G1 X159.726 Y127.983 E.0254
G1 X160.2 Y128.044 E.01475
G1 X159.679 Y128.565 E.02273
G1 X160.214 Y128.565 E.01652
G1 X160.67 Y128.109 E.01988
G1 X160.712 Y128.118 E.00134
G1 X160.628 Y128.174 E.00313
G1 X160.831 Y128.483 E.01142
G1 X160.58 Y128.735 E.01097
G1 X161.319 Y128.117 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.551367
G1 F7080.392
G1 X161.528 Y128.434 E.0157
G1 X161.615 Y128.449 E.00365
; LINE_WIDTH: 0.515349
G1 F7620.197
G3 X162.456 Y128.71 I-.753 J3.907 E.03399
G1 X162.459 Y128.724 E.00055
; LINE_WIDTH: 0.497907
G1 F7912.312
G1 X162.53 Y129.04 E.012
G1 X163.265 Y128.726 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X163.098 Y128.91 E.00768
G1 X163.171 Y129.238 E.01036
G1 X162.952 Y129.287 E.00692
G1 X163.071 Y129.456 E.00637
G1 X163.502 Y129.024 E.01884
G1 X163.858 Y129.204 E.01228
G1 X163.249 Y129.813 E.02653
G3 X163.36 Y130.237 I-1.423 J.598 E.01358
G1 X164.209 Y129.388 E.03703
G1 X164.539 Y129.593 E.01199
G1 X163.381 Y130.751 E.05052
G1 X163.381 Y131.287 E.01652
G1 X164.87 Y129.798 E.06493
G3 X165.183 Y130.02 I-1.137 J1.938 E.01186
G1 X163.381 Y131.822 E.07861
G1 X163.381 Y132.357 E.01652
G1 X165.49 Y130.249 E.09198
G3 X165.791 Y130.483 I-1.216 J1.873 E.01178
G1 X163.381 Y132.893 E.10512
G1 X163.381 Y133.428 E.01652
G1 X166.074 Y130.735 E.11748
G1 X166.358 Y130.987 E.0117
G1 X162.991 Y134.354 E.14688
; WIPE_START
G1 X164.405 Y132.94 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.932 Y140.418 Z.8 F30000
G1 X169.419 Y157.507 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.479329
G1 F8249.14
G1 X169.448 Y157.702 E.00704
; LINE_WIDTH: 0.434779
G1 F9186.996
G1 X169.477 Y157.898 E.00633
; LINE_WIDTH: 0.390228
G1 F10365.463
G1 X169.506 Y158.094 E.00561
; LINE_WIDTH: 0.344279
G1 F11945.906
G1 X169.537 Y158.303 E.00517
; LINE_WIDTH: 0.299199
G1 F14047.221
G1 X169.555 Y158.483 E.00378
; LINE_WIDTH: 0.25753
G1 F15000
G1 X169.574 Y158.663 E.00317
; LINE_WIDTH: 0.215861
G1 X169.592 Y158.843 E.00255
; LINE_WIDTH: 0.174193
G1 X169.611 Y159.023 E.00194
; LINE_WIDTH: 0.13218
G1 X169.63 Y159.206 E.00134
; LINE_WIDTH: 0.10403
G1 X169.637 Y159.332 E.00063
; WIPE_START
G1 X169.63 Y159.206 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X163.406 Y154.787 Z.8 F30000
G1 X130.864 Y131.682 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X133.905 Y128.641 E.13266
G1 X133.354 Y128.656 E.01701
G1 X130.705 Y131.305 E.11557
G1 X130.425 Y131.049 E.01169
G1 X132.803 Y128.672 E.10372
G1 X132.252 Y128.688 E.01701
G1 X130.126 Y130.813 E.09272
G1 X129.823 Y130.581 E.01178
G1 X131.701 Y128.703 E.0819
G1 X131.15 Y128.719 E.01701
G1 X129.51 Y130.359 E.07154
G1 X129.183 Y130.15 E.01196
G1 X130.599 Y128.735 E.06177
G1 X130.048 Y128.75 E.01701
G1 X128.853 Y129.944 E.0521
G1 X128.501 Y129.761 E.01225
G1 X129.497 Y128.766 E.04343
G1 X128.946 Y128.781 E.01701
G1 X128.149 Y129.578 E.03475
G2 X127.776 Y129.416 I-1.112 J2.051 E.01257
G1 X128.395 Y128.797 E.027
G1 X127.843 Y128.813 E.01701
G1 X127.267 Y129.389 E.02514
G1 X127.017 Y128.977 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.483236
G1 F8175.961
G1 X126.807 Y128.947 E.00762
; LINE_WIDTH: 0.438314
G1 F9104.843
G1 X126.596 Y128.918 E.00684
; LINE_WIDTH: 0.391837
G1 F10317.664
G1 X126.372 Y128.887 E.00645
; LINE_WIDTH: 0.344492
G1 F11937.479
G1 X126.191 Y128.87 E.00445
; LINE_WIDTH: 0.299927
G1 F14007.406
G1 X126.011 Y128.853 E.0038
; LINE_WIDTH: 0.255363
G1 F15000
G1 X125.83 Y128.835 E.00314
; LINE_WIDTH: 0.210799
G1 X125.65 Y128.818 E.00248
; LINE_WIDTH: 0.165695
G1 X125.465 Y128.801 E.00186
; LINE_WIDTH: 0.119988
G1 X125.149 Y128.784 E.00199
; OBJECT_ID: 861
; WIPE_START
G1 X125.465 Y128.801 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 795
M625
; start printing object, unique label id: 861
M624 CAAAAAAAAAA=
G1 X130.085 Y122.725 Z.8 F30000
G1 X147.778 Y99.454 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X147.845 Y99.708 E.00871
G3 X146.021 Y98.307 I-1.674 J.292 E.27041
G3 X146.312 Y98.306 I.151 J2.16 E.00966
G3 X147.76 Y99.397 I-.141 J1.694 E.06343
M204 S250
G1 X147.399 Y99.556 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.055 Y98.698 I-1.23 J.445 E.19979
G3 X146.281 Y98.698 I.115 J1.681 E.00696
G3 X147.378 Y99.5 I-.112 J1.303 E.04389
; WIPE_START
M204 S10000
G1 X147.459 Y99.776 E-.10939
G1 X147.479 Y100.003 E-.08677
G1 X147.459 Y100.231 E-.08677
G1 X147.4 Y100.451 E-.08681
G1 X147.304 Y100.658 E-.08674
G1 X147.097 Y100.928 E-.12921
G1 X146.921 Y101.077 E-.08758
G1 X146.723 Y101.191 E-.08672
; WIPE_END
G1 E-.04 F1800
G1 X149.181 Y93.965 Z.8 F30000
G1 X150.499 Y90.092 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X150.727 Y89.961 E.00871
G3 X151.298 Y89.807 I.721 J1.539 E.01971
G3 X151.589 Y89.806 I.151 J2.152 E.00965
G3 X150.449 Y90.125 I-.141 J1.694 E.31413
M204 S250
G1 X150.695 Y90.431 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X151.332 Y90.198 I.752 J1.07 E.02108
G3 X151.558 Y90.198 I.115 J1.677 E.00696
G3 X150.647 Y90.466 I-.112 J1.303 E.2226
; WIPE_START
M204 S10000
G1 X150.892 Y90.316 E-.10942
G1 X151.107 Y90.238 E-.08678
G1 X151.332 Y90.198 E-.0868
G1 X151.558 Y90.198 E-.08598
G1 X151.785 Y90.238 E-.08762
G1 X152 Y90.316 E-.08676
G1 X152.172 Y90.413 E-.07505
G1 X152.373 Y90.577 E-.09847
G1 X152.446 Y90.664 E-.04312
; WIPE_END
G1 E-.04 F1800
G1 X159.799 Y88.618 Z.8 F30000
G1 X161.811 Y88.058 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X161.459 Y88.105 E.01178
G1 X150.433 Y88.105 E.36577
G3 X148.844 Y86.517 I.027 J-1.616 E.08241
G1 X148.844 Y83.49 E.1004
G3 X150.433 Y81.901 I1.621 J.032 E.08234
G1 X161.459 Y81.901 E.36577
G3 X163.048 Y83.49 I-.027 J1.616 E.08241
M73 P34 R6
G1 X163.048 Y86.517 E.1004
G3 X161.87 Y88.045 I-1.616 J-.027 E.06861
M204 S250
G1 X161.759 Y87.67 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X161.451 Y87.713 I-.323 J-1.177 E.00958
G1 X150.441 Y87.713 E.33829
G3 X149.236 Y86.508 I.016 J-1.221 E.05798
G1 X149.236 Y83.499 E.09247
G3 X150.441 Y82.293 I1.225 J.02 E.05792
G1 X161.451 Y82.293 E.33829
G3 X162.656 Y83.499 I-.016 J1.221 E.05798
G1 X162.656 Y86.508 E.09247
G3 X161.816 Y87.652 I-1.221 J-.016 E.04655
; WIPE_START
M204 S10000
G1 X161.451 Y87.713 E-.14076
G1 X159.821 Y87.713 E-.61924
; WIPE_END
G1 E-.04 F1800
G1 X152.619 Y85.187 Z.8 F30000
G1 X145.222 Y82.592 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X145.45 Y82.461 E.00871
G3 X146.021 Y82.307 I.721 J1.539 E.01971
G3 X146.311 Y82.306 I.151 J2.152 E.00965
G3 X145.172 Y82.625 I-.141 J1.694 E.31413
M204 S250
G1 X145.418 Y82.931 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.055 Y82.698 I.752 J1.07 E.02108
G3 X146.281 Y82.698 I.115 J1.677 E.00696
G3 X145.37 Y82.966 I-.112 J1.303 E.2226
; WIPE_START
M204 S10000
G1 X145.615 Y82.816 E-.10942
G1 X145.83 Y82.738 E-.08676
G1 X146.055 Y82.698 E-.08681
G1 X146.281 Y82.698 E-.08598
G1 X146.508 Y82.738 E-.08762
G1 X146.723 Y82.816 E-.08677
G1 X146.921 Y82.93 E-.08679
G1 X147.096 Y83.077 E-.08677
G1 X147.165 Y83.167 E-.04308
; WIPE_END
G1 E-.04 F1800
G1 X141.964 Y88.754 Z.8 F30000
G1 X132.532 Y98.888 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X132.543 Y98.709 E.00596
G3 X132.762 Y98.026 I2.084 J.293 E.02389
G1 X133.298 Y97.107 E.0353
G2 X133.996 Y88.525 I-9.741 J-5.113 E.29348
G2 X132.762 Y85.98 I-11.995 J4.249 E.094
G3 X134.611 Y82.901 I1.875 J-.969 E.1425
G1 X141.682 Y82.901 E.23458
G3 X143.771 Y84.99 I-.032 J2.121 E.10839
G1 X143.771 Y99.017 E.46529
G3 X141.682 Y101.105 I-2.112 J-.023 E.10851
G1 X134.611 Y101.105 E.23458
G3 X132.523 Y99.067 I.016 J-2.104 E.10693
G1 X132.529 Y98.948 E.00397
M204 S250
G1 X132.917 Y98.909 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X133.109 Y98.209 I1.709 J.092 E.02248
G1 X133.644 Y97.291 E.03266
G2 X134.368 Y88.399 I-10.092 J-5.297 E.28164
G2 X133.109 Y85.798 I-12.328 J4.361 E.08899
G3 X134.619 Y83.293 I1.525 J-.788 E.10754
G1 X141.674 Y83.293 E.21677
G3 X143.379 Y84.999 I-.02 J1.726 E.08205
G1 X143.379 Y99.008 E.43047
G3 X141.674 Y100.713 I-1.718 J-.013 E.08214
G1 X134.619 Y100.713 E.21677
G3 X132.915 Y98.969 I.007 J-1.712 E.0834
; WIPE_START
M204 S10000
G1 X132.957 Y98.62 E-.13377
G1 X133.03 Y98.386 E-.09308
G1 X133.109 Y98.209 E-.07366
G1 X133.644 Y97.291 E-.40389
G1 X133.708 Y97.159 E-.05561
; WIPE_END
G1 E-.04 F1800
G1 X127.498 Y92.721 Z.8 F30000
G1 X116.514 Y84.872 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X116.534 Y84.868 E.00067
G3 X123.394 Y81.913 I7.142 J7.139 E.25383
G3 X133.162 Y88.548 I.265 J10.118 E.41824
G3 X115.939 Y85.517 I-9.487 J3.459 E1.40321
G1 X116.474 Y84.917 E.02666
M204 S250
G1 X116.811 Y85.145 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X123.412 Y82.304 I6.865 J6.861 E.22619
G3 X132.469 Y87.9 I.249 J9.726 E.34616
G3 X116.769 Y85.188 I-8.794 J4.107 E1.2995
; WIPE_START
M204 S10000
G1 X117.427 Y84.565 E-.34453
G1 X118.099 Y84.049 E-.32186
G1 X118.307 Y83.917 E-.09361
; WIPE_END
G1 E-.04 F1800
G1 X123.569 Y89.445 Z.8 F30000
G1 X155.975 Y123.49 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X155.178 Y123.155 E.02867
G3 X159.172 Y103.913 I4.274 J-9.149 E.89661
G3 X168.94 Y110.548 I.265 J10.118 E.41824
G3 X156.032 Y123.508 I-9.487 J3.459 E.759
M204 S250
G1 X156.126 Y123.124 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X159.189 Y104.304 I3.326 J-9.118 E.82447
G3 X168.247 Y109.9 I.27 J9.693 E.34631
G3 X156.183 Y123.145 I-8.794 J4.107 E.70122
; WIPE_START
M204 S10000
G1 X155.342 Y122.804 E-.34462
G1 X154.591 Y122.413 E-.32187
G1 X154.384 Y122.28 E-.09351
; WIPE_END
G1 E-.04 F1800
G1 X157.403 Y115.271 Z.8 F30000
G1 X166.285 Y94.656 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.317 Y94.651 E.00106
G3 X168.548 Y96.736 I.128 J2.1 E.11336
G1 X168.548 Y103.062 E.20983
G3 X165.469 Y104.911 I-2.104 J-.016 E.14276
G1 X164.549 Y104.375 E.0353
G2 X155.967 Y103.676 I-5.103 J9.629 E.29363
G2 X153.423 Y104.911 I4.248 J11.993 E.094
G3 X150.374 Y103.407 I-.975 J-1.866 E.13125
G3 X150.344 Y102.329 I6.158 J-.712 E.03582
G3 X151.655 Y100.394 I2.109 J.017 E.08215
G1 X165.678 Y94.792 E.50094
G3 X166.009 Y94.7 I.922 J2.672 E.01138
G1 X166.226 Y94.665 E.0073
M204 S250
G1 X166.336 Y95.043 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X168.156 Y96.744 I.109 J1.708 E.08573
G1 X168.156 Y103.053 E.19386
G3 X165.652 Y104.563 I-1.712 J-.007 E.10773
G1 X164.733 Y104.028 E.03266
G2 X155.842 Y103.304 I-5.287 J9.976 E.28179
G2 X153.241 Y104.563 I4.361 J12.327 E.08899
G3 X150.761 Y103.34 I-.793 J-1.518 E.09888
G3 X150.736 Y102.337 I5.791 J-.645 E.03087
G3 X151.808 Y100.755 I1.717 J.009 E.06226
G1 X165.816 Y95.159 E.46351
G3 X166.277 Y95.05 I.757 J2.175 E.01458
; WIPE_START
M204 S10000
G1 X166.666 Y95.053 E-.14791
G1 X166.949 Y95.114 E-.11008
G1 X167.086 Y95.162 E-.05508
G1 X167.344 Y95.293 E-.11014
G1 X167.577 Y95.466 E-.11014
G1 X167.682 Y95.566 E-.05504
G1 X167.864 Y95.792 E-.11014
G1 X167.942 Y95.933 E-.06146
; WIPE_END
G1 E-.04 F1800
G1 X165.778 Y91.175 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X165.849 Y90.922 E.0087
G3 X167.298 Y89.807 I1.598 J.578 E.06401
G3 X167.588 Y89.806 I.151 J2.152 E.00965
G3 X165.769 Y91.234 I-.141 J1.694 E.26984
M204 S250
G1 X166.158 Y91.276 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X167.332 Y90.198 I1.288 J.225 E.05266
G3 X167.558 Y90.198 I.115 J1.677 E.00696
G3 X166.149 Y91.336 I-.112 J1.303 E.19102
; WIPE_START
M204 S10000
G1 X166.215 Y91.055 E-.10942
G1 X166.356 Y90.778 E-.11828
G1 X166.52 Y90.577 E-.09845
G1 X166.695 Y90.43 E-.08675
G1 X166.892 Y90.316 E-.08684
G1 X167.107 Y90.238 E-.08676
G1 X167.332 Y90.198 E-.08679
G1 X167.558 Y90.198 E-.08598
G1 X167.56 Y90.198 E-.00074
; WIPE_END
G1 E-.04 F1800
G1 X160.219 Y92.285 Z.8 F30000
G1 X128.082 Y101.422 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X127.169 Y101.794 E.03272
G3 X123.387 Y81.609 I-3.491 J-9.793 E1.19188
G1 X158.73 Y80.606 E1.17285
G1 X159.425 Y80.635 E.0231
G1 X159.707 Y80.648 E.00935
M73 P35 R6
G3 X170.125 Y91.634 I-1.003 J11.384 E.54897
G1 X169.843 Y114.121 E.74599
G3 X149.447 Y111.155 I-10.396 J-.126 E1.1747
G1 X149.877 Y109.855 E.04541
G2 X147.433 Y103.561 I-5.416 J-1.518 E.24023
G1 X145.26 Y102.225 E.08462
G2 X142.347 Y101.401 I-2.994 J5.023 E.10156
G1 X128.138 Y101.401 E.47134
M204 S250
G1 X128.211 Y101.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X123.367 Y81.218 I-4.533 J-9.791 E1.17577
G1 X158.732 Y80.213 E1.08711
G1 X159.442 Y80.244 E.02182
G1 X159.74 Y80.257 E.00918
G3 X170.518 Y91.622 I-1.038 J11.776 E.52604
G1 X170.235 Y114.134 E.6918
G3 X149.069 Y111.047 I-10.788 J-.139 E1.12892
G1 X149.5 Y109.748 E.04205
G2 X147.22 Y103.891 I-5.038 J-1.411 E.20716
G1 X145.061 Y102.563 E.07789
G2 X142.339 Y101.793 I-2.79 J4.668 E.08791
G1 X128.271 Y101.793 E.4323
M204 S10000
G1 X128.393 Y101.188 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.331146
G1 F12490.228
G1 X129.207 Y100.97 E.01979
G1 X131.546 Y100.114 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.5849
G1 F6642.312
G2 X131.55 Y100.225 I-.029 J.056 E.01173
G1 X132.28 Y100.632 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X132.028 Y100.23 E.0146
G1 X131.857 Y99.77 E.01508
G1 X131.766 Y99.246 E.01635
G1 X131.374 Y99.673 E.01782
G1 X130.676 Y100.315 E.02914
G1 X130.249 Y100.632 E.01632
G1 X132.22 Y100.632 E.06056
G1 X132.895 Y100.792 F30000
G1 F9547.299
G1 X132.728 Y100.624 E.00729
G1 X132.398 Y100.128 E.01829
G3 X132.155 Y98.697 I2.354 J-1.135 E.0452
G1 X131.87 Y98.54 E.01002
G3 X130.421 Y100.037 I-8.806 J-7.067 E.06411
G3 X129.537 Y100.687 I-262.108 J-356.104 E.03372
G1 X129.623 Y101.009 E.01025
G1 X132.827 Y101.009 E.09844
G1 X132.826 Y100.876 E.00408
G1 X132.857 Y100.838 E.00151
G1 X133.297 Y100.92 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.12099
G1 F15000
G1 X133.464 Y101.056 E.00137
; LINE_WIDTH: 0.16541
G1 X133.654 Y101.198 E.00237
G1 X133.791 Y101.176 F30000
; LINE_WIDTH: 0.133894
G1 F15000
G3 X133.437 Y101.102 I1.489 J-8.021 E.00268
; WIPE_START
G1 X133.791 Y101.176 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.17 Y98.258 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.474755
G1 F8336.53
G1 X132.397 Y97.845 E.01659
; LINE_WIDTH: 0.431339
G1 F9268.358
G3 X132.754 Y97.258 I13.558 J7.853 E.02174
G2 X132.406 Y86.177 I-9.076 J-5.261 E.3697
; LINE_WIDTH: 0.473817
G1 F8354.671
G1 X132.17 Y85.749 E.01717
G1 X131.628 Y85.527 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X132.191 Y84.964 E.02458
G3 X132.281 Y84.338 I2.102 J-.017 E.01957
G1 X131.501 Y85.118 E.03402
G1 X131.245 Y84.839 E.01169
G1 X134.456 Y81.628 E.14006
G1 X135.007 Y81.613 E.01701
G1 X133.956 Y82.664 E.04585
G3 X134.586 Y82.569 I.665 J2.281 E.01971
G1 X135.558 Y81.597 E.04241
G1 X136.109 Y81.581 E.01701
G1 X135.122 Y82.568 E.04305
G1 X135.657 Y82.568 E.01652
G1 X136.66 Y81.566 E.04373
G1 X137.211 Y81.55 E.01701
G1 X136.193 Y82.568 E.04442
G1 X136.728 Y82.568 E.01652
G1 X137.762 Y81.534 E.0451
G1 X138.313 Y81.519 E.01701
G1 X137.264 Y82.568 E.04578
G1 X137.799 Y82.568 E.01652
G1 X138.864 Y81.503 E.04646
G1 X139.415 Y81.487 E.01701
G1 X138.334 Y82.568 E.04715
G1 X138.87 Y82.568 E.01652
G1 X139.966 Y81.472 E.04783
G1 X140.517 Y81.456 E.01701
G1 X139.405 Y82.568 E.04851
G1 X139.94 Y82.568 E.01652
G1 X141.068 Y81.44 E.04919
G1 X141.619 Y81.425 E.01701
G1 X140.476 Y82.568 E.04988
G1 X141.011 Y82.568 E.01652
G1 X142.17 Y81.409 E.05056
G1 X142.721 Y81.394 E.01701
G1 X141.547 Y82.568 E.05124
G3 X142.05 Y82.6 I.075 J2.839 E.01559
G1 X143.272 Y81.378 E.0533
G1 X143.823 Y81.362 E.01701
G1 X142.479 Y82.707 E.05866
G3 X142.847 Y82.874 I-2.004 J4.892 E.01247
G1 X144.374 Y81.347 E.06664
G1 X144.925 Y81.331 E.01701
G1 X143.166 Y83.09 E.07675
G3 X143.449 Y83.343 I-.818 J1.199 E.01173
G1 X145.476 Y81.315 E.08846
G1 X146.027 Y81.3 E.01701
G1 X143.562 Y83.765 E.10756
G1 X144.095 Y84.192 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.382438
G1 F10603.266
G1 X144.254 Y83.985 E.00722
G1 X144.095 Y84.192 F30000
; LINE_WIDTH: 0.413697
G1 F9709.35
G1 X144.08 Y84.213 E.00077
; LINE_WIDTH: 0.44913
G1 F8862.416
G1 X144.065 Y84.234 E.00085
; LINE_WIDTH: 0.450714
G1 F8828.004
G1 X144.168 Y84.698 E.01581
G1 X144.195 Y84.713 E.00104
; LINE_WIDTH: 0.410185
G1 F9802.183
G1 X144.445 Y84.839 E.00836
G1 X144.293 Y85.176 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X144.104 Y85.364 E.00823
G1 X144.104 Y85.9 E.01652
G1 X144.65 Y85.354 E.02382
G2 X144.928 Y85.611 I.869 J-.659 E.01175
G1 X144.104 Y86.436 E.03596
G1 X144.103 Y86.971 E.01652
G1 X145.257 Y85.817 E.05035
G2 X145.646 Y85.964 I.607 J-1.016 E.01287
G1 X144.103 Y87.507 E.0673
G1 X144.103 Y88.043 E.01652
G1 X146.113 Y86.033 E.08769
G2 X146.726 Y85.955 I.094 J-1.716 E.01916
G1 X143.933 Y88.748 E.12185
; WIPE_START
G1 X145.347 Y87.334 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.99 Y83.62 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X148.568 Y83.042 E.02522
G2 X148.516 Y83.629 I1.658 J.443 E.01828
G1 X148.198 Y83.947 E.01386
G3 X148.137 Y84.531 I-1.685 J.117 E.0182
G1 X148.129 Y84.552 E.00069
G1 X148.515 Y84.166 E.01684
G1 X148.514 Y84.702 E.01654
G1 X144.102 Y89.114 E.19248
G1 X144.102 Y89.65 E.01652
G1 X148.513 Y85.238 E.19245
G1 X148.512 Y85.775 E.01654
G1 X144.102 Y90.185 E.19242
G1 X144.101 Y90.721 E.01652
G1 X148.511 Y86.311 E.19239
G2 X148.537 Y86.821 I2.802 J.115 E.01577
G1 X144.101 Y91.257 E.19352
G1 X144.101 Y91.792 E.01652
G1 X148.656 Y87.237 E.19874
G2 X148.843 Y87.586 I1.417 J-.533 E.01224
G1 X144.1 Y92.328 E.20689
G1 X144.1 Y92.864 E.01652
G1 X149.085 Y87.879 E.21745
G2 X149.384 Y88.115 I1.047 J-1.02 E.01179
G1 X144.1 Y93.399 E.23052
G1 X144.1 Y93.935 E.01652
G1 X149.736 Y88.298 E.2459
G2 X150.164 Y88.405 I.459 J-.927 E.01373
G1 X144.099 Y94.471 E.2646
G1 X144.099 Y95.006 E.01652
G1 X150.667 Y88.438 E.28653
G1 X151.203 Y88.438 E.01652
G1 X143.929 Y95.712 E.31732
G1 X144.442 Y99.167 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.429816
G1 F9304.835
G1 X144.18 Y99.302 E.00931
; LINE_WIDTH: 0.451624
G1 F8808.343
G1 X144.065 Y99.773 E.01615
; LINE_WIDTH: 0.449137
G1 F8862.266
G1 X144.08 Y99.794 E.00085
; LINE_WIDTH: 0.413774
G1 F9707.324
G1 X144.095 Y99.814 E.00077
; LINE_WIDTH: 0.382524
G1 F10600.581
G1 X144.254 Y100.022 E.00723
G1 X144.681 Y101.212 F30000
; LINE_WIDTH: 0.401514
G1 F10039.221
G1 X144.697 Y101.494 E.00828
G1 X144.765 Y101.54 E.00238
; LINE_WIDTH: 0.384377
G1 F10543.068
G1 X144.833 Y101.585 E.00227
; LINE_WIDTH: 0.351171
G1 F11678.824
G1 X144.988 Y101.679 E.00456
; LINE_WIDTH: 0.324131
G1 F12801.799
G1 X145.472 Y101.939 E.01258
; LINE_WIDTH: 0.369294
G1 F11030.293
G1 X145.649 Y102.019 E.00518
; LINE_WIDTH: 0.418482
G1 F9585.644
G1 X145.965 Y102.144 E.0104
G1 X146.157 Y102.585 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X147.168 Y101.574 E.04411
; WIPE_START
G1 X146.157 Y102.585 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.126 Y98.403 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X152.108 Y93.422 E.21732
G3 X151.462 Y93.533 I-.663 J-1.933 E.0203
G1 X146.889 Y98.106 E.19951
G2 X146.464 Y97.995 I-.525 J1.142 E.01361
G1 X150.98 Y93.479 E.19699
G3 X150.584 Y93.34 I.192 J-1.179 E.01302
G1 X145.941 Y97.983 E.20255
G2 X145.126 Y98.262 I.265 J2.1 E.02675
G1 X150.247 Y93.141 E.22342
G3 X149.963 Y92.89 I.57 J-.931 E.01176
G1 X144.199 Y98.654 E.25146
G1 X144.097 Y98.71 E.00359
G1 X144.097 Y98.22 E.0151
G1 X149.729 Y92.589 E.24568
G3 X149.551 Y92.231 I1.245 J-.84 E.01236
G1 X144.098 Y97.685 E.23793
G1 X144.098 Y97.149 E.01652
G1 X149.439 Y91.808 E.23302
G3 X149.417 Y91.326 I1.355 J-.304 E.01494
G1 X149.424 Y91.288 E.0012
G1 X144.098 Y96.613 E.23232
G1 X144.098 Y96.078 E.01652
G1 X151.738 Y88.438 E.33329
G1 X152.274 Y88.438 E.01652
G1 X151.231 Y89.481 E.04551
G3 X151.75 Y89.496 I.187 J2.411 E.01607
G1 X152.809 Y88.437 E.04621
G1 X153.345 Y88.437 E.01652
G1 X152.174 Y89.609 E.05111
G3 X152.532 Y89.786 I-.487 J1.432 E.01236
M73 P36 R6
G1 X153.881 Y88.437 E.05885
G1 X154.416 Y88.437 E.01652
G1 X152.833 Y90.02 E.06909
G3 X153.084 Y90.304 I-.677 J.852 E.01176
G1 X154.952 Y88.436 E.0815
G1 X155.488 Y88.436 E.01652
G1 X153.288 Y90.636 E.09597
G3 X153.412 Y90.97 I-1.233 J.65 E.01102
G1 X153.424 Y91.035 E.00205
G1 X156.023 Y88.436 E.1134
G1 X156.559 Y88.435 E.01652
G1 X153.475 Y91.519 E.13452
G3 X153.365 Y92.165 I-2.008 J-.012 E.02032
G1 X157.095 Y88.435 E.16272
G1 X157.63 Y88.435 E.01652
G1 X147.55 Y98.515 E.43975
G3 X147.806 Y98.795 I-.929 J1.105 E.01172
G1 X158.166 Y88.435 E.45198
G1 X158.702 Y88.434 E.01652
G1 X148.008 Y99.128 E.46653
G1 X148.145 Y99.526 E.01299
G1 X159.237 Y88.434 E.48389
G1 X159.773 Y88.434 E.01652
G1 X148.198 Y100.008 E.50495
G3 X148.094 Y100.648 I-2.059 J-.008 E.02008
G1 X160.308 Y88.434 E.53288
G1 X160.844 Y88.433 E.01652
G1 X146.612 Y102.666 E.6209
G1 X146.943 Y102.869 E.01201
G1 X161.38 Y88.433 E.62981
G2 X161.994 Y88.354 I.096 J-1.685 E.01921
G1 X147.275 Y103.073 E.64214
G1 X147.607 Y103.277 E.01201
G1 X166.624 Y84.259 E.82968
G1 X166.885 Y84.534 E.01168
G1 X147.926 Y103.493 E.8271
G3 X148.229 Y103.725 I-1.19 J1.863 E.01179
G1 X150.051 Y101.904 E.07948
G2 X150.012 Y102.478 I4.613 J.599 E.01776
G1 X148.516 Y103.973 E.06525
G1 X148.789 Y104.236 E.01168
G1 X150.016 Y103.009 E.05355
G2 X150.064 Y103.497 I1.345 J.116 E.01521
G1 X149.037 Y104.523 E.04479
G1 X149.269 Y104.827 E.01178
G1 X150.177 Y103.919 E.03963
G2 X150.348 Y104.283 I2.023 J-.724 E.01244
G1 X149.491 Y105.14 E.03739
G1 X149.693 Y105.474 E.01203
G1 X150.573 Y104.594 E.0384
G2 X150.831 Y104.871 I1.205 J-.862 E.01172
G1 X149.87 Y105.832 E.04194
G3 X150.027 Y106.21 I-2.1 J1.098 E.01264
G1 X151.138 Y105.1 E.04844
G1 X151.489 Y105.284 E.01223
G1 X150.164 Y106.609 E.05781
G3 X150.276 Y107.032 I-2.384 J.859 E.01352
G1 X151.894 Y105.414 E.07058
G2 X152.368 Y105.476 I.415 J-1.34 E.01482
G1 X150.36 Y107.483 E.08759
G3 X150.41 Y107.969 I-2.77 J.532 E.01507
G1 X152.834 Y105.544 E.10576
G1 X152.986 Y105.819 E.00966
G2 X150.899 Y108.015 I6.221 J7.999 E.09381
G1 X150.634 Y108.28 E.01157
G1 X150.518 Y108.416 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.243802
G1 F15000
G1 X150.361 Y108.941 E.00897
; LINE_WIDTH: 0.217952
G1 X150.313 Y109.089 E.00221
; LINE_WIDTH: 0.169541
G1 X150.265 Y109.236 E.0016
; LINE_WIDTH: 0.121129
G1 X150.218 Y109.383 E.00099
G1 X150.224 Y109.385 F30000
; LINE_WIDTH: 0.310284
G1 F13464.832
G1 X150.515 Y108.416 E.02206
G1 X153.192 Y105.502 F30000
; LINE_WIDTH: 0.474748
G1 F8336.651
G1 X153.605 Y105.275 E.01658
; LINE_WIDTH: 0.431337
G1 F9268.405
G3 X165.272 Y105.266 I5.841 J8.741 E.39148
; LINE_WIDTH: 0.473815
G1 F8354.718
G1 X165.701 Y105.502 E.01718
G1 X165.807 Y105.956 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X166.285 Y105.478 E.02085
G1 X166.731 Y105.469 E.01378
G1 X166.858 Y105.441 E.00399
G1 X166.105 Y106.194 E.03284
; WIPE_START
G1 X166.858 Y105.441 E-.40451
G1 X166.731 Y105.469 E-.04918
G1 X166.285 Y105.478 E-.16969
G1 X166.031 Y105.733 E-.13663
; WIPE_END
G1 E-.04 F1800
G1 X168.998 Y110.261 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X169.566 Y109.693 E.02479
G1 X169.573 Y109.151 E.01673
G1 X168.971 Y109.753 E.02626
G2 X168.799 Y109.389 I-2.163 J.802 E.01242
G1 X169.579 Y108.609 E.03406
G1 X169.586 Y108.066 E.01673
G1 X168.615 Y109.037 E.04236
G2 X168.425 Y108.692 I-2.066 J.915 E.01217
G1 X169.593 Y107.524 E.05096
G1 X169.6 Y106.982 E.01673
G1 X168.217 Y108.365 E.06035
G1 X168.008 Y108.038 E.01196
G1 X169.607 Y106.44 E.06973
G1 X169.613 Y105.898 E.01673
G1 X167.777 Y107.734 E.0801
G1 X167.545 Y107.431 E.01178
G1 X169.62 Y105.356 E.09054
G1 X169.627 Y104.813 E.01673
G1 X167.299 Y107.141 E.10154
G1 X167.043 Y106.862 E.01169
G1 X169.634 Y104.271 E.11301
G1 X169.641 Y103.729 E.01673
G1 X166.784 Y106.586 E.12463
G1 X166.505 Y106.33 E.01169
G1 X169.647 Y103.187 E.13711
G1 X169.654 Y102.645 E.01673
G1 X168.839 Y103.459 E.03555
G2 X168.874 Y102.889 I-1.632 J-.386 E.01771
G1 X169.661 Y102.102 E.03432
G1 X169.668 Y101.56 E.01673
G1 X168.874 Y102.354 E.03462
G1 X168.874 Y101.818 E.01652
G1 X169.675 Y101.018 E.03491
G1 X169.681 Y100.476 E.01673
G1 X168.874 Y101.283 E.03521
G1 X168.874 Y100.748 E.01652
G1 X169.688 Y99.934 E.0355
G1 X169.695 Y99.392 E.01673
G1 X168.874 Y100.212 E.0358
G1 X168.874 Y99.677 E.01652
G1 X169.702 Y98.849 E.0361
G1 X169.709 Y98.307 E.01673
G1 X168.874 Y99.141 E.03639
G1 X168.874 Y98.606 E.01652
G1 X169.715 Y97.765 E.03669
G1 X169.722 Y97.223 E.01673
G1 X168.874 Y98.071 E.03699
G1 X168.874 Y97.535 E.01652
G1 X169.729 Y96.681 E.03728
G1 X169.736 Y96.139 E.01673
G1 X168.874 Y97 E.03758
G1 X168.863 Y96.476 E.01617
G1 X169.743 Y95.596 E.03837
G1 X169.749 Y95.054 E.01673
G1 X168.772 Y96.031 E.04264
G2 X168.616 Y95.653 I-1.558 J.422 E.01268
G1 X169.756 Y94.512 E.04976
G1 X169.763 Y93.97 E.01673
G1 X168.412 Y95.321 E.05894
G2 X168.165 Y95.032 I-.966 J.578 E.01177
G1 X169.77 Y93.428 E.07001
G1 X169.776 Y92.885 E.01673
G1 X167.876 Y94.786 E.08291
G2 X167.544 Y94.583 I-.759 J.868 E.01207
G1 X169.783 Y92.343 E.0977
G1 X169.79 Y91.801 E.01673
G1 X167.169 Y94.422 E.11436
G1 X166.725 Y94.33 E.01397
G1 X167.523 Y93.533 E.0348
G3 X167.028 Y93.492 I-.108 J-1.733 E.01537
G1 X166.188 Y94.332 E.03665
G2 X165.468 Y94.517 I.385 J2.999 E.02299
G1 X166.625 Y93.36 E.0505
G3 X166.283 Y93.166 I.373 J-1.061 E.01219
G1 X164.577 Y94.873 E.07446
G1 X163.685 Y95.229 E.02962
G1 X165.994 Y92.921 E.10072
G3 X165.754 Y92.625 I.72 J-.827 E.0118
G1 X162.793 Y95.585 E.12916
G1 X161.902 Y95.942 E.02962
G1 X165.567 Y92.276 E.15991
G3 X165.448 Y91.86 I1.408 J-.628 E.0134
G1 X161.01 Y96.298 E.19362
G1 X160.119 Y96.654 E.02962
G1 X165.62 Y91.153 E.23998
; WIPE_START
G1 X164.205 Y92.567 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.288 Y91.768 Z.8 F30000
G1 Z.4
G1 E.8 F1800
G1 F9509.47
G1 X169.765 Y91.29 E.02082
G1 X169.728 Y90.792 E.0154
G1 X169.427 Y91.093 E.01311
G2 X169.303 Y90.683 I-1.023 J.087 E.01333
G1 X169.66 Y90.325 E.0156
G1 X169.585 Y89.864 E.0144
G1 X169.109 Y90.34 E.02077
G2 X168.863 Y90.051 I-.94 J.549 E.01178
G1 X169.485 Y89.43 E.02711
G1 X169.377 Y89.002 E.01361
G1 X168.568 Y89.811 E.03531
G2 X168.219 Y89.625 I-.87 J1.212 E.01224
G1 X169.25 Y88.593 E.04502
G1 X169.113 Y88.195 E.01299
G1 X167.803 Y89.506 E.05719
G2 X167.299 Y89.474 I-.341 J1.399 E.01565
G1 X168.965 Y87.808 E.0727
G1 X168.801 Y87.437 E.01252
G1 X159.227 Y97.01 E.41766
G1 X158.336 Y97.366 E.02962
G1 X168.635 Y87.067 E.4493
G1 X168.445 Y86.722 E.01216
G1 X157.444 Y97.722 E.47991
G1 X156.553 Y98.079 E.02962
G1 X168.255 Y86.376 E.51053
G2 X168.048 Y86.047 I-2.024 J1.04 E.012
G1 X155.661 Y98.435 E.54042
G1 X154.77 Y98.791 E.02962
G1 X167.834 Y85.726 E.56997
G2 X167.615 Y85.41 I-1.952 J1.123 E.01188
G1 X153.878 Y99.147 E.59929
G1 X152.986 Y99.503 E.02962
G1 X167.377 Y85.113 E.62782
G1 X167.14 Y84.815 E.01175
G1 X151.791 Y100.164 E.66962
; WIPE_START
G1 X153.205 Y98.75 E-.76
; WIPE_END
G1 E-.04 F1800
M73 P37 R6
G1 X145.773 Y100.489 Z.8 F30000
G1 X143.388 Y101.047 Z.8
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.5542
G1 F7041.152
G3 X144.019 Y101.19 I-.442 J3.399 E.02699
G1 X144.026 Y100.941 E.01039
G1 X144.173 Y100.802 E.00842
G1 X144.132 Y100.658 E.0062
G1 X144.077 Y100.679 E.00248
G3 X143.757 Y100.488 I.113 J-.553 E.01581
G1 X143.351 Y100.919 E.02466
G1 X143.396 Y100.989 E.00348
G1 X142.855 Y101.01 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.109678
G1 F15000
G1 X142.763 Y101.074 E.0006
; LINE_WIDTH: 0.138429
G1 X142.655 Y101.152 E.00103
G1 X142.698 Y101.211 E.00057
; WIPE_START
G1 X142.655 Y101.152 E-.26999
G1 X142.763 Y101.074 E-.49001
; WIPE_END
G1 E-.04 F1800
G1 X143.918 Y93.529 Z.8 F30000
G1 X145.649 Y82.214 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X146.578 Y81.284 E.04056
G1 X147.129 Y81.268 E.01701
G1 X146.414 Y81.984 E.03121
G3 X146.849 Y82.084 I-.165 J1.7 E.0138
G1 X147.68 Y81.253 E.03629
G1 X148.231 Y81.237 E.01701
G1 X147.212 Y82.256 E.04447
G1 X147.52 Y82.484 E.01181
G1 X148.782 Y81.221 E.05508
G1 X149.333 Y81.206 E.01701
G1 X147.777 Y82.762 E.06789
G3 X147.983 Y83.092 I-.831 J.748 E.01205
G1 X149.884 Y81.19 E.08295
G1 X150.435 Y81.175 E.01701
G1 X149.985 Y81.625 E.01967
G3 X150.577 Y81.568 I.509 J2.173 E.01842
G1 X150.986 Y81.159 E.01785
G1 X151.537 Y81.143 E.01701
G1 X151.113 Y81.568 E.01853
G1 X151.648 Y81.568 E.01652
G1 X152.089 Y81.128 E.01922
G1 X152.64 Y81.112 E.01701
G1 X152.183 Y81.568 E.0199
G1 X152.719 Y81.568 E.01652
G1 X153.191 Y81.096 E.02058
G1 X153.742 Y81.081 E.01701
G1 X153.254 Y81.568 E.02126
G1 X153.79 Y81.568 E.01652
G1 X154.293 Y81.065 E.02195
G1 X154.844 Y81.049 E.01701
G1 X154.325 Y81.568 E.02263
G1 X154.86 Y81.568 E.01652
G1 X155.395 Y81.034 E.02331
G1 X155.946 Y81.018 E.01701
G1 X155.396 Y81.568 E.024
G1 X155.931 Y81.568 E.01652
G1 X156.497 Y81.002 E.02468
G1 X157.048 Y80.987 E.01701
G1 X156.466 Y81.568 E.02536
G1 X157.002 Y81.568 E.01652
G1 X157.599 Y80.971 E.02604
G1 X158.15 Y80.955 E.01701
G1 X157.537 Y81.568 E.02672
G1 X158.073 Y81.568 E.01652
G1 X158.701 Y80.94 E.02741
G3 X159.216 Y80.96 I.116 J3.631 E.01592
G1 X158.608 Y81.568 E.02653
G1 X159.143 Y81.568 E.01652
G1 X159.726 Y80.986 E.0254
G1 X160.2 Y81.047 E.01475
G1 X159.679 Y81.568 E.02273
G1 X160.214 Y81.568 E.01652
G1 X160.67 Y81.112 E.01988
G1 X160.712 Y81.122 E.00134
G1 X160.628 Y81.177 E.00313
G1 X160.831 Y81.486 E.01142
G1 X160.58 Y81.738 E.01097
G1 X161.319 Y81.121 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.551367
G1 F7080.392
G1 X161.528 Y81.437 E.0157
G1 X161.615 Y81.452 E.00365
; LINE_WIDTH: 0.515349
G1 F7620.197
G3 X162.456 Y81.714 I-.753 J3.907 E.03399
G1 X162.459 Y81.728 E.00055
; LINE_WIDTH: 0.497907
G1 F7912.312
G1 X162.53 Y82.043 E.012
G1 X163.265 Y81.729 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X163.098 Y81.913 E.00768
G1 X163.171 Y82.241 E.01036
G1 X162.952 Y82.29 E.00692
G1 X163.071 Y82.459 E.00637
G1 X163.502 Y82.027 E.01884
G1 X163.858 Y82.208 E.01228
G1 X163.249 Y82.816 E.02653
G3 X163.36 Y83.24 I-1.423 J.598 E.01358
G1 X164.209 Y82.392 E.03703
G1 X164.539 Y82.597 E.01199
G1 X163.381 Y83.755 E.05052
G1 X163.381 Y84.29 E.01652
G1 X164.87 Y82.802 E.06493
G3 X165.183 Y83.024 I-1.137 J1.938 E.01186
G1 X163.381 Y84.825 E.07861
G1 X163.381 Y85.361 E.01652
G1 X165.49 Y83.252 E.09198
G3 X165.791 Y83.487 I-1.216 J1.873 E.01178
G1 X163.381 Y85.896 E.10512
G1 X163.381 Y86.431 E.01652
G1 X166.074 Y83.739 E.11748
G1 X166.358 Y83.99 E.0117
G1 X162.991 Y87.357 E.14688
; WIPE_START
G1 X164.405 Y85.943 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.932 Y93.421 Z.8 F30000
G1 X169.419 Y110.51 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.479329
G1 F8249.14
G1 X169.448 Y110.706 E.00704
; LINE_WIDTH: 0.434779
G1 F9186.996
G1 X169.477 Y110.902 E.00633
; LINE_WIDTH: 0.390228
G1 F10365.463
G1 X169.506 Y111.098 E.00561
; LINE_WIDTH: 0.344279
G1 F11945.906
G1 X169.537 Y111.306 E.00517
; LINE_WIDTH: 0.299199
G1 F14047.221
G1 X169.555 Y111.486 E.00378
; LINE_WIDTH: 0.25753
G1 F15000
G1 X169.574 Y111.666 E.00317
; LINE_WIDTH: 0.215861
G1 X169.592 Y111.846 E.00255
; LINE_WIDTH: 0.174193
G1 X169.611 Y112.026 E.00194
; LINE_WIDTH: 0.13218
G1 X169.63 Y112.209 E.00134
; LINE_WIDTH: 0.10403
G1 X169.637 Y112.335 E.00063
; WIPE_START
G1 X169.63 Y112.209 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X163.406 Y107.791 Z.8 F30000
G1 X130.864 Y84.685 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X133.905 Y81.644 E.13266
G1 X133.354 Y81.66 E.01701
G1 X130.705 Y84.309 E.11557
G1 X130.425 Y84.053 E.01169
G1 X132.803 Y81.675 E.10372
G1 X132.252 Y81.691 E.01701
G1 X130.126 Y83.816 E.09272
G1 X129.823 Y83.584 E.01178
G1 X131.701 Y81.706 E.0819
G1 X131.15 Y81.722 E.01701
G1 X129.51 Y83.362 E.07154
G1 X129.183 Y83.154 E.01196
G1 X130.599 Y81.738 E.06177
G1 X130.048 Y81.753 E.01701
G1 X128.853 Y82.948 E.0521
G1 X128.501 Y82.764 E.01225
G1 X129.497 Y81.769 E.04343
G1 X128.946 Y81.785 E.01701
G1 X128.149 Y82.581 E.03475
G2 X127.776 Y82.419 I-1.112 J2.051 E.01257
G1 X128.395 Y81.8 E.027
G1 X127.843 Y81.816 E.01701
G1 X127.267 Y82.392 E.02514
G1 X127.017 Y81.98 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.483236
G1 F8175.961
G1 X126.807 Y81.95 E.00762
; LINE_WIDTH: 0.438314
G1 F9104.843
G1 X126.596 Y81.921 E.00684
; LINE_WIDTH: 0.391837
G1 F10317.664
G1 X126.372 Y81.89 E.00645
; LINE_WIDTH: 0.344492
G1 F11937.479
G1 X126.191 Y81.873 E.00445
; LINE_WIDTH: 0.299927
G1 F14007.406
G1 X126.011 Y81.856 E.0038
; LINE_WIDTH: 0.255363
G1 F15000
G1 X125.83 Y81.839 E.00314
; LINE_WIDTH: 0.210799
G1 X125.65 Y81.821 E.00248
; LINE_WIDTH: 0.165695
G1 X125.465 Y81.804 E.00186
; LINE_WIDTH: 0.119988
G1 X125.149 Y81.788 E.00199
; OBJECT_ID: 817
; WIPE_START
G1 X125.465 Y81.804 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 861
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X122.576 Y88.868 Z.8 F30000
G1 X101.983 Y139.227 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X100.793 Y138.59 I-1.125 J.67 E.20919
G1 X100.903 Y138.589 E.00339
G3 X101.951 Y139.177 I-.045 J1.309 E.03836
; WIPE_START
M204 S10000
G1 X102.09 Y139.466 E-.12188
G1 X102.152 Y139.719 E-.09919
G1 X102.161 Y139.98 E-.09916
G1 X102.119 Y140.237 E-.09909
G1 X102.027 Y140.482 E-.09917
G1 X101.889 Y140.701 E-.09861
G1 X101.756 Y140.848 E-.07508
G1 X101.615 Y140.957 E-.06782
; WIPE_END
G1 E-.04 F1800
G1 X96.517 Y135.278 Z.8 F30000
G1 X88.065 Y125.862 Z.8
G1 Z.4
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X88.175 Y125.861 E.00339
G3 X88.005 Y125.866 I-.045 J1.309 E.24754
; WIPE_START
M204 S10000
G1 X88.175 Y125.861 E-.06475
G1 X88.433 Y125.897 E-.09887
G1 X88.679 Y125.983 E-.09923
G1 X88.904 Y126.116 E-.09908
G1 X89.097 Y126.291 E-.09923
G1 X89.252 Y126.501 E-.09909
G1 X89.362 Y126.738 E-.09917
G1 X89.424 Y126.991 E-.09912
G1 X89.424 Y126.995 E-.00146
; WIPE_END
G1 E-.04 F1800
G1 X96.035 Y130.808 Z.8 F30000
G1 X102.939 Y134.79 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X102.448 Y134.756 E.01632
G3 X102.856 Y114.607 I.89 J-10.061 E1.00701
G3 X105.699 Y114.875 I.489 J10.01 E.09504
G3 X102.999 Y134.79 I-2.361 J9.82 E.98476
M204 S250
G1 X102.965 Y134.396 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X102.871 Y114.999 I.372 J-9.701 E.91135
G3 X105.607 Y115.257 I.474 J9.622 E.08473
G3 X103.025 Y134.399 I-2.269 J9.439 E.87635
; WIPE_START
M204 S10000
G1 X102.482 Y134.369 E-.20667
G1 X102.001 Y134.314 E-.18398
G1 X101.523 Y134.236 E-.18405
G1 X101.05 Y134.135 E-.18392
G1 X101.046 Y134.134 E-.00138
; WIPE_END
G1 E-.04 F1800
G1 X103.592 Y126.938 Z.8 F30000
G1 X112.803 Y100.908 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X112.891 Y100.917 E.00291
G3 X113.849 Y101.426 I-.477 J2.055 E.03641
G2 X112.237 Y102.084 I-.194 J1.828 E.06017
G2 X115.281 Y103.235 I1.347 J1.039 E.21059
G1 X115.286 Y102.856 E.01257
G1 X125.169 Y112.739 E.46364
G2 X123.661 Y113.269 I-.187 J1.878 E.05473
G2 X126.595 Y114.549 I1.234 J1.172 E.21672
G1 X126.599 Y114.176 E.01237
G3 X126.57 Y116.866 I-1.37 J1.33 E.09902
G1 X102.416 Y141.02 E1.13309
G1 X102.247 Y140.891 E.00706
G2 X100.96 Y141.598 I-1.383 J-.993 E.30447
G2 X101.846 Y141.291 I-.146 J-1.858 E.03146
G1 X101.975 Y141.461 E.00706
G3 X100.5 Y142.147 I-1.539 J-1.381 E.05545
G3 X99.137 Y141.573 I.011 J-1.932 E.05034
G1 X86.451 Y128.887 E.59514
G3 X86.451 Y126.161 I1.345 J-1.363 E.10062
G1 X86.563 Y126.049 E.00525
G1 X86.733 Y126.178 E.00706
G2 X88.191 Y125.469 I1.384 J.993 E.29895
G2 X87.133 Y125.785 I-.053 J1.749 E.03726
G1 X86.997 Y125.615 E.00724
G1 X111.158 Y101.454 E1.13343
G3 X112.744 Y100.901 I1.374 J1.387 E.05759
; WIPE_START
G1 X112.891 Y100.917 E-.05614
G1 X113.246 Y101.024 E-.14116
G1 X113.574 Y101.2 E-.14117
G1 X113.849 Y101.426 E-.13537
G1 X113.387 Y101.437 E-.17562
G1 X113.103 Y101.499 E-.11055
; WIPE_END
G1 E-.04 F1800
M73 P38 R6
G1 X112.314 Y103.435 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X113.521 Y101.82 I1.273 J-.307 E.07068
G1 X113.631 Y101.82 E.00339
G3 X112.329 Y103.493 I-.044 J1.309 E.17687
; WIPE_START
M204 S10000
G1 X112.272 Y103.178 E-.12152
G1 X112.288 Y102.917 E-.09918
G1 X112.356 Y102.665 E-.09918
G1 X112.472 Y102.432 E-.09916
G1 X112.632 Y102.226 E-.09912
G1 X112.83 Y102.056 E-.09911
G1 X113.058 Y101.928 E-.09923
G1 X113.167 Y101.893 E-.04351
; WIPE_END
G1 E-.04 F1800
G1 X117.953 Y107.838 Z.8 F30000
G1 X123.713 Y114.994 Z.8
G1 Z.4
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X124.834 Y113.134 I1.187 J-.552 E.07868
G1 X124.945 Y113.133 E.00339
G3 X123.739 Y115.048 I-.044 J1.309 E.16887
; WIPE_START
M204 S10000
G1 X123.621 Y114.75 E-.12171
G1 X123.586 Y114.492 E-.09903
G1 X123.602 Y114.231 E-.09918
G1 X123.67 Y113.979 E-.09914
G1 X123.786 Y113.745 E-.09922
G1 X123.946 Y113.539 E-.0991
G1 X124.144 Y113.369 E-.09917
G1 X124.243 Y113.313 E-.04345
; WIPE_END
G1 E-.04 F1800
G1 X119.166 Y107.615 Z.8 F30000
G1 X112.842 Y100.518 Z.8
G1 Z.4
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X112.967 Y100.53 E.00388
G3 X114.147 Y101.163 I-.586 J2.508 E.04162
G1 X126.861 Y113.877 E.55246
G3 X126.861 Y117.13 I-1.62 J1.627 E.11109
G1 X102.127 Y141.864 E1.07482
G3 X98.873 Y141.864 I-1.627 J-1.62 E.11109
G1 X86.16 Y129.15 E.55246
G3 X86.16 Y125.897 I1.62 J-1.626 E.11108
G1 X110.894 Y101.163 E1.07483
G3 X112.782 Y100.511 I1.637 J1.678 E.0634
M204 S10000
G1 X113.08 Y101.187 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.439845
G1 F9069.74
G1 X112.551 Y101.29 E.01743
G1 X112.479 Y101.566 E.00923
G1 X112.292 Y101.244 F30000
; LINE_WIDTH: 0.203395
G1 F15000
G1 X113.209 Y101.236 E.012
; WIPE_START
G1 X112.292 Y101.244 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X114.426 Y101.719 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.127119
G1 F15000
G2 X113.947 Y101.644 I-1.794 J9.839 E.00333
G1 X113.949 Y101.629 F30000
; LINE_WIDTH: 0.196576
G1 F15000
G1 X114.254 Y101.695 E.00391
G3 X114.383 Y101.773 I-.028 J.193 E.00193
; LINE_WIDTH: 0.147843
G1 X114.624 Y101.98 E.00272
G1 X114.933 Y102.322 E.00394
; LINE_WIDTH: 0.19835
G1 X115.009 Y102.424 E.00161
G3 X115.083 Y102.766 I-6.742 J1.645 E.00443
G1 X115.068 Y102.768 F30000
; LINE_WIDTH: 0.128698
G1 F15000
G2 X114.993 Y102.286 I-9.699 J1.262 E.00341
; WIPE_START
G1 X115.068 Y102.768 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.843 Y103.644 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42022
G1 F9541.479
G1 X105.076 Y114.411 E.46812
G3 X105.524 Y114.497 I-.642 J4.53 E.01401
G1 X115.99 Y104.031 E.45506
G1 X116.256 Y104.298 E.0116
G1 X105.955 Y114.599 E.4479
G3 X106.372 Y114.716 I-.964 J4.245 E.01332
G1 X116.523 Y104.565 E.44138
G1 X116.79 Y104.831 E.0116
G1 X106.775 Y114.846 E.43543
G1 X107.163 Y114.992 E.01273
G1 X117.057 Y105.098 E.43019
G1 X117.323 Y105.365 E.0116
G1 X107.538 Y115.15 E.42547
G3 X107.903 Y115.319 I-1.515 J3.745 E.01236
G1 X117.59 Y105.632 E.42122
G1 X117.857 Y105.899 E.0116
G1 X108.257 Y115.499 E.41742
G1 X108.599 Y115.69 E.01205
G1 X118.124 Y106.165 E.41415
G1 X118.391 Y106.432 E.0116
G1 X108.929 Y115.894 E.4114
G3 X109.25 Y116.106 I-1.967 J3.319 E.01184
G1 X118.657 Y106.699 E.40904
G1 X118.924 Y106.966 E.0116
G1 X109.562 Y116.328 E.40707
G1 X109.862 Y116.561 E.01169
G1 X119.191 Y107.233 E.40561
G1 X119.458 Y107.499 E.0116
G1 X110.152 Y116.805 E.4046
G3 X110.434 Y117.057 I-2.38 J2.946 E.01162
G1 X119.725 Y107.766 E.40395
G1 X119.991 Y108.033 E.0116
G1 X110.708 Y117.317 E.40366
G1 X110.968 Y117.59 E.0116
G1 X120.258 Y108.3 E.40395
G1 X120.525 Y108.566 E.0116
G1 X111.22 Y117.872 E.4046
G3 X111.463 Y118.162 I-2.779 J2.58 E.01165
G1 X120.792 Y108.833 E.40561
G1 X121.059 Y109.1 E.0116
G1 X111.696 Y118.462 E.40707
G3 X111.918 Y118.774 I-3.009 J2.369 E.01177
G1 X121.325 Y109.367 E.40904
G1 X121.592 Y109.634 E.0116
G1 X112.13 Y119.095 E.4114
G3 X112.334 Y119.426 I-3.208 J2.204 E.01193
G1 X121.859 Y109.9 E.41416
G1 X122.126 Y110.167 E.0116
G1 X112.526 Y119.767 E.41742
G3 X112.705 Y120.122 I-3.454 J1.971 E.01221
G1 X122.393 Y110.434 E.42122
G1 X122.659 Y110.701 E.0116
G1 X112.874 Y120.486 E.42547
G3 X113.032 Y120.862 I-3.678 J1.769 E.01253
G1 X122.926 Y110.968 E.4302
G1 X123.193 Y111.234 E.0116
G1 X113.178 Y121.249 E.43544
G1 X113.308 Y121.653 E.01304
G1 X123.46 Y111.501 E.44138
G1 X123.726 Y111.768 E.0116
G1 X113.425 Y122.069 E.44791
G3 X113.527 Y122.501 I-4.26 J1.237 E.01364
G1 X123.993 Y112.035 E.45507
G1 X124.26 Y112.302 E.0116
G1 X113.613 Y122.948 E.46291
G3 X113.682 Y123.413 I-4.609 J.919 E.01445
G1 X122.873 Y114.222 E.39963
G2 X122.877 Y114.721 I1.657 J.238 E.0154
G1 X122.883 Y114.746 E.0008
G1 X113.731 Y123.898 E.39791
G3 X113.758 Y124.404 I-5.065 J.521 E.01561
G1 X122.995 Y115.168 E.40161
G2 X123.177 Y115.519 I1.258 J-.429 E.01222
G1 X113.759 Y124.937 E.40948
G3 X113.73 Y125.499 I-5.648 J-.007 E.01732
G1 X123.403 Y115.827 E.42057
G1 X123.684 Y116.079 E.01162
G1 X113.666 Y126.097 E.43556
M73 P39 R6
G3 X113.56 Y126.737 I-6.474 J-.75 E.01996
G1 X124.024 Y116.273 E.45498
G2 X124.41 Y116.42 I.68 J-1.209 E.01277
G1 X113.398 Y127.433 E.47883
G3 X113.15 Y128.214 I-7.939 J-2.089 E.02522
G1 X124.887 Y116.477 E.51035
G2 X125.422 Y116.411 I.049 J-1.808 E.01664
G1 X125.526 Y116.372 E.0034
G1 X112.775 Y129.123 E.55441
G3 X112.174 Y130.232 I-10.064 J-4.736 E.0388
G1 X112.188 Y130.243 E.00056
G1 X126.399 Y116.032 E.61791
G1 X126.4 Y116.084 E.00159
G1 X126.697 Y116.079 E.00913
G3 X126.324 Y116.641 I-1.905 J-.859 E.02084
G1 X112.354 Y130.611 E.60741
G1 X112.117 Y130.623 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.563485
G1 F6915.564
G1 X111.886 Y130.891 E.01504
; LINE_WIDTH: 0.530026
G1 F7390.6
G1 X111.647 Y131.169 E.01454
; LINE_WIDTH: 0.499828
G1 F7879.051
G1 X111.474 Y131.36 E.00958
; LINE_WIDTH: 0.473639
G1 F8358.126
G1 X111.295 Y131.558 E.0094
; LINE_WIDTH: 0.443386
G1 F8989.539
G1 X110.57 Y132.301 E.03385
G1 X110.183 Y132.669 E.01743
; LINE_WIDTH: 0.474168
G1 F8347.88
G1 X109.992 Y132.842 E.00905
; LINE_WIDTH: 0.500435
G1 F7868.601
G1 X109.793 Y133.022 E.01004
; LINE_WIDTH: 0.530582
G1 F7382.16
G1 X109.524 Y133.253 E.01408
; LINE_WIDTH: 0.563475
G1 F6915.704
G1 X109.255 Y133.485 E.01503
; WIPE_START
G1 X109.524 Y133.253 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X103.255 Y137.607 Z.8 F30000
G1 X99.044 Y140.53 Z.8
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.409698
G1 F9815.2
G1 X98.956 Y140.794 E.00832
; LINE_WIDTH: 0.437943
G1 F9113.398
G1 X98.951 Y140.81 E.00055
G1 X99.004 Y140.883 E.0029
; LINE_WIDTH: 0.41089
G1 F9783.428
G1 X99.058 Y140.955 E.0027
; LINE_WIDTH: 0.375864
G1 F10812.628
G1 X99.19 Y141.117 E.00566
; LINE_WIDTH: 0.344084
G1 F11953.624
G1 X99.327 Y141.27 E.00505
; LINE_WIDTH: 0.318786
G1 F13049.844
G2 X99.477 Y141.41 I1.439 J-1.386 E.0046
G1 X99.638 Y141.542 E.00469
G1 X99.809 Y141.644 E.00447
; LINE_WIDTH: 0.283095
G1 F14989.107
G2 X99.992 Y141.732 I.698 J-1.233 E.00398
G1 X100.182 Y141.799 E.00395
; LINE_WIDTH: 0.24409
G1 F15000
G1 X100.381 Y141.839 E.00331
; LINE_WIDTH: 0.212709
G2 X100.579 Y141.86 I.271 J-1.618 E.00276
; LINE_WIDTH: 0.172725
G1 X100.777 Y141.859 E.0021
; LINE_WIDTH: 0.133669
G2 X100.973 Y141.833 I-.041 J-1.056 E.00146
; LINE_WIDTH: 0.10167
G1 X101.051 Y141.817 E.00038
; WIPE_START
G1 X100.973 Y141.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X102.334 Y141.379 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.27086
G1 F15000
G1 X102.195 Y141.24 E.00365
; LINE_WIDTH: 0.234705
G1 X102.057 Y141.101 E.00307
; LINE_WIDTH: 0.19855
G1 X101.918 Y140.963 E.00249
; WIPE_START
G1 X102.057 Y141.101 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X102.752 Y140.396 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.114001
G1 F15000
G1 X102.764 Y140.167 E.00133
G1 X103.967 Y136.722 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.50437
G1 F7801.496
G3 X102.614 Y136.717 I-.629 J-12.735 E.05091
G3 X103.397 Y137.292 I-2.002 J3.543 E.03662
G1 X103.925 Y136.764 E.02808
G1 X98.304 Y136.398 F30000
; LINE_WIDTH: 0.38223
G1 F10609.766
G3 X97.088 Y135.796 I4.206 J-10.042 E.03755
G1 X97.962 Y136.67 E.03418
G1 X98.257 Y136.435 E.01045
G1 X91.627 Y129.723 F30000
; LINE_WIDTH: 0.38361
G1 F10566.79
G1 X91.352 Y130.06 E.01207
G1 X92.225 Y130.932 E.03425
G3 X91.651 Y129.778 I9.139 J-5.257 E.03581
G1 X91.695 Y128.923 F30000
; LINE_WIDTH: 0.418663
G1 F9581.036
G1 X91.439 Y129.375 E.0159
G1 X91.012 Y129.905 E.02083
G1 X90.847 Y130.062 E.00699
G3 X93.471 Y132.71 I-87.802 J89.631 E.11414
; LINE_WIDTH: 0.363866
G1 F11216.867
G2 X95.233 Y134.476 I48.085 J-46.215 E.06526
; LINE_WIDTH: 0.39935
G1 F10100.16
G1 X95.689 Y134.905 E.01816
; LINE_WIDTH: 0.431523
G1 F9263.965
G1 X95.92 Y135.117 E.00994
; LINE_WIDTH: 0.449941
G1 F8844.767
G3 X96.578 Y135.793 I-3.7 J4.261 E.03131
; LINE_WIDTH: 0.423584
G1 F9457.173
G1 X97.961 Y137.176 E.0607
G1 X98.42 Y136.754 E.01934
G1 X99.089 Y136.33 E.02458
G3 X96.517 Y135.054 I5.301 J-13.922 E.0892
G1 X96.017 Y134.689 E.01919
; LINE_WIDTH: 0.40636
G1 F9905.349
G1 X95.54 Y134.296 E.01829
; LINE_WIDTH: 0.363873
G1 F11216.622
G3 X93.795 Y132.561 I14.651 J-16.485 E.0644
; LINE_WIDTH: 0.416799
G1 F9628.801
G3 X91.717 Y128.979 I8.86 J-7.534 E.12684
G1 X91.693 Y127.634 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G3 X91.121 Y129.173 I-3.976 J-.602 E.05081
G1 X90.727 Y129.659 E.01922
G1 X90.291 Y130.04 E.01777
G1 X97.983 Y137.732 E.33424
G1 X98.38 Y137.283 E.0184
G1 X98.875 Y136.895 E.01934
G3 X100.383 Y136.329 I2.017 J3.08 E.04987
G3 X91.709 Y127.692 I2.937 J-11.624 E.39472
G1 X91.302 Y124.057 F30000
; LINE_WIDTH: 0.50438
G1 F7801.327
G1 X90.732 Y124.627 E.03034
G1 X91.154 Y125.149 E.02523
G1 X91.307 Y125.401 E.0111
G3 X91.301 Y124.117 I11.699 J-.701 E.04832
G1 X91.84 Y122.926 F30000
; LINE_WIDTH: 0.420139
G1 F9543.55
G1 X90.123 Y124.643 E.07463
G1 X90.555 Y125.047 E.01816
G3 X91.096 Y125.925 I-2.322 J2.039 E.03187
; LINE_WIDTH: 0.440064
G1 F9064.737
G1 X91.152 Y126.023 E.00363
; LINE_WIDTH: 0.47565
G1 F8319.275
G1 X91.207 Y126.12 E.00395
; LINE_WIDTH: 0.520301
G1 F7541.152
G1 X91.262 Y126.218 E.00436
G1 X91.381 Y126.859 E.02535
; LINE_WIDTH: 0.491015
G1 F8034.01
G1 X91.361 Y127.143 E.01041
; LINE_WIDTH: 0.420359
G1 F9537.981
G3 X91.089 Y128.448 I-3.87 J-.127 E.04121
G1 X90.839 Y128.91 E.01615
G1 X90.441 Y129.413 E.01973
G1 X89.954 Y129.824 E.01959
G1 X89.696 Y129.978 E.00924
G1 X98.043 Y138.324 E.36303
G1 X98.391 Y137.818 E.0189
G1 X98.776 Y137.429 E.01683
G1 X99.393 Y137.025 E.02267
G1 X99.969 Y136.798 E.01907
G1 X100.51 Y136.69 E.01695
; LINE_WIDTH: 0.44462
G1 F8961.911
G1 X100.781 Y136.66 E.00894
; LINE_WIDTH: 0.508435
G1 F7733.374
G1 X101.053 Y136.629 E.01036
G1 X101.609 Y136.713 E.02132
; LINE_WIDTH: 0.48938
G1 F8063.433
G1 X101.85 Y136.818 E.00956
; LINE_WIDTH: 0.420852
G1 F9525.545
G3 X102.977 Y137.469 I-2.454 J5.548 E.04018
G1 X103.363 Y137.876 E.01727
G1 X103.404 Y137.877 E.00127
G1 X105.098 Y136.184 E.07375
G3 X102.348 Y136.279 I-1.79 J-11.916 E.08492
; LINE_WIDTH: 0.444573
G1 F8962.972
G1 X102.064 Y136.273 E.00929
; LINE_WIDTH: 0.509493
G1 F7715.835
G1 X101.781 Y136.267 E.01079
G1 X101.191 Y136.171 E.02269
; LINE_WIDTH: 0.491735
G1 F8021.122
G1 X100.917 Y136.089 E.0105
; LINE_WIDTH: 0.420516
G1 F9533.997
G3 X99.52 Y135.679 I11.571 J-42.066 E.04478
G3 X92.036 Y127.455 I3.823 J-10.996 E.35671
; LINE_WIDTH: 0.436992
G1 F9135.394
G1 X91.978 Y127.27 E.00623
; LINE_WIDTH: 0.470995
G1 F8409.741
G1 X91.92 Y127.085 E.00676
; LINE_WIDTH: 0.515962
G1 F7610.325
G1 X91.862 Y126.9 E.00747
G1 X91.769 Y126.325 E.02246
; LINE_WIDTH: 0.497833
G1 F7913.609
G1 X91.758 Y126.065 E.00965
; LINE_WIDTH: 0.459058
G1 F8650.987
G1 X91.748 Y125.805 E.00882
; LINE_WIDTH: 0.422227
G1 F9491.009
G3 X91.832 Y122.986 I12.672 J-1.031 E.08736
G1 X92.469 Y121.764 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X89.523 Y124.71 E.12801
G1 X89.891 Y124.937 E.01328
G1 X90.265 Y125.288 E.01576
G1 X90.62 Y125.798 E.01909
G1 X90.842 Y126.319 E.01742
G1 X90.957 Y126.874 E.01742
G1 X90.967 Y127.387 E.01576
G1 X90.878 Y127.896 E.01587
G1 X90.696 Y128.395 E.01632
G1 X90.403 Y128.879 E.0174
G1 X90.019 Y129.296 E.01741
G1 X89.524 Y129.645 E.01862
G1 X89.042 Y129.857 E.01616
G1 X98.164 Y138.979 E.3964
G1 X98.347 Y138.548 E.0144
G1 X98.664 Y138.078 E.01742
G1 X99.069 Y137.681 E.01742
G1 X99.543 Y137.371 E.01742
G1 X100.055 Y137.165 E.01694
G1 X100.545 Y137.066 E.01537
G3 X102.033 Y137.304 I.245 J3.231 E.04672
G1 X102.653 Y137.698 E.02257
G1 X103.084 Y138.129 E.01873
G1 X103.314 Y138.501 E.01344
G1 X106.26 Y135.555 E.12802
G3 X92.454 Y121.822 I-2.929 J-10.861 E.72324
G1 X93.368 Y120.334 F30000
; LINE_WIDTH: 0.41999
G1 F9547.301
G2 X88.884 Y124.818 I580.476 J585.099 E.19485
G1 X89.522 Y125.135 E.02189
G1 X89.92 Y125.471 E.01601
G1 X90.234 Y125.879 E.0158
G1 X90.476 Y126.408 E.01788
G1 X90.581 Y126.91 E.01575
G3 X90.367 Y128.21 I-2.691 J.225 E.04092
G1 X90.04 Y128.722 E.01867
G1 X89.788 Y128.999 E.0115
G1 X89.372 Y129.3 E.01578
G1 X88.851 Y129.529 E.01747
G3 X88.288 Y129.637 I-.875 J-3.048 E.01764
G1 X98.387 Y139.735 E.43882
G1 X98.482 Y139.205 E.01656
G1 X98.667 Y138.749 E.01512
G1 X98.938 Y138.338 E.01511
G1 X99.285 Y137.989 E.01512
G1 X99.792 Y137.674 E.01837
G3 X101.967 Y137.696 I1.064 J2.26 E.06913
G1 X102.445 Y138.012 E.01762
G1 X102.804 Y138.382 E.01584
G1 X103.153 Y139.003 E.02188
G1 X103.208 Y139.135 E.00438
G2 X107.69 Y134.656 I-1194.144 J-1199.436 E.19469
G3 X93.347 Y120.39 I-4.357 J-9.962 E.79849
G1 X94.41 Y119.174 F30000
; LINE_WIDTH: 0.41999
G1 F9547.3
G1 X94.185 Y118.981 E.00909
G1 X88.216 Y124.951 E.25941
G1 X88.25 Y125.086 E.00429
G1 X88.795 Y125.186 E.01703
G1 X89.346 Y125.469 E.01904
G1 X89.692 Y125.779 E.01426
G1 X89.936 Y126.117 E.01281
G1 X90.139 Y126.618 E.01661
G3 X90.038 Y128.026 I-2.039 J.562 E.04422
G1 X89.754 Y128.477 E.01636
G1 X89.556 Y128.701 E.0092
G1 X89.22 Y128.955 E.01294
G1 X88.7 Y129.184 E.01747
G1 X88.222 Y129.262 E.01487
G1 X87.997 Y129.242 E.00695
G1 X87.969 Y129.413 E.00533
G1 X87.673 Y129.555 E.01008
G1 X98.469 Y140.351 E.4691
G1 X98.611 Y140.055 E.01008
G1 X98.782 Y140.027 E.00533
G1 X98.764 Y139.749 E.00857
G3 X99.943 Y138.019 I2.131 J.186 E.06722
G3 X101.759 Y138.011 I.917 J1.906 E.05766
G1 X102.237 Y138.327 E.01762
G1 X102.551 Y138.673 E.01437
G1 X102.82 Y139.18 E.01762
G1 X102.933 Y139.676 E.01564
G1 X102.937 Y139.777 E.00311
G1 X103.073 Y139.809 E.00428
G1 X109.043 Y133.839 E.25943
G1 X108.85 Y133.614 E.00909
G1 X108.004 Y134.091 E.02984
G3 X94.379 Y119.226 I-4.675 J-9.392 E.83215
G1 X94.539 Y118.769 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.563482
G1 F6915.603
G1 X94.771 Y118.5 E.01504
; LINE_WIDTH: 0.530568
G1 F7382.384
G1 X95.002 Y118.231 E.01408
; LINE_WIDTH: 0.50041
G1 F7869.035
G1 X95.182 Y118.031 E.01004
; LINE_WIDTH: 0.47415
G1 F8348.222
G1 X95.355 Y117.841 E.00905
; LINE_WIDTH: 0.443383
G1 F8989.594
G1 X95.723 Y117.454 E.01743
G1 X96.466 Y116.729 E.03385
; LINE_WIDTH: 0.473645
G1 F8358.004
G1 X96.664 Y116.549 E.0094
; LINE_WIDTH: 0.499822
G1 F7879.15
G1 X96.855 Y116.377 E.00958
; LINE_WIDTH: 0.530024
G1 F7390.624
G1 X97.133 Y116.138 E.01454
; LINE_WIDTH: 0.563482
G1 F6915.605
G1 X97.401 Y115.907 E.01504
G1 X97.414 Y115.67 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42022
G1 F9541.479
G1 X111.387 Y101.697 E.60755
G3 X111.924 Y101.334 I1.183 J1.169 E.02007
G1 X111.959 Y101.323 E.00115
G1 X111.96 Y101.365 E.00131
G1 X111.867 Y101.751 E.01218
G1 X97.781 Y115.837 E.61247
G1 X97.792 Y115.85 E.00054
G3 X98.902 Y115.249 I5.838 J9.451 E.03884
G1 X111.651 Y102.5 E.5543
G2 X111.553 Y103.132 I1.607 J.573 E.01977
G1 X99.811 Y114.874 E.51054
G3 X100.592 Y114.626 I2.873 J7.703 E.02522
G1 X111.611 Y103.607 E.47911
G2 X111.745 Y104.007 I1.841 J-.394 E.01299
G1 X101.288 Y114.464 E.4547
G3 X101.928 Y114.358 I1.39 J6.368 E.01996
G1 X111.951 Y104.334 E.43582
G2 X112.203 Y104.616 I.823 J-.483 E.0117
G1 X102.521 Y114.298 E.42099
G3 X103.08 Y114.272 I.473 J4.12 E.01724
G1 X112.5 Y104.852 E.40958
G2 X112.858 Y105.028 I.762 J-1.096 E.0123
G1 X103.618 Y114.268 E.40173
G3 X104.127 Y114.293 I.077 J3.632 E.01567
G1 X113.285 Y105.135 E.3982
G2 X113.807 Y105.146 I.296 J-1.545 E.01612
G1 X104.458 Y114.495 E.40649
; WIPE_START
G1 X105.872 Y113.081 E-.76
; WIPE_END
M73 P40 R6
G1 E-.04 F1800
G1 X99.55 Y117.357 Z.8 F30000
G1 X87.864 Y125.26 Z.8
G1 Z.4
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.118993
G1 F15000
G1 X87.627 Y125.273 E.00147
; WIPE_START
G1 X87.864 Y125.26 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.062 Y126.106 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.196007
G1 F15000
G1 X86.921 Y125.969 E.00245
; LINE_WIDTH: 0.229378
G1 X86.781 Y125.832 E.00298
; LINE_WIDTH: 0.262748
G1 X86.64 Y125.695 E.00352
; WIPE_START
G1 X86.781 Y125.832 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X86.207 Y126.973 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.101657
G1 F15000
G1 X86.191 Y127.051 E.00038
; LINE_WIDTH: 0.133671
G2 X86.165 Y127.247 I1.029 J.236 E.00146
; LINE_WIDTH: 0.172703
G1 X86.164 Y127.445 E.00209
; LINE_WIDTH: 0.212703
G2 X86.185 Y127.643 I1.636 J-.071 E.00277
; LINE_WIDTH: 0.244095
G1 X86.225 Y127.842 E.00331
; LINE_WIDTH: 0.28312
G1 F14987.533
G1 X86.293 Y128.032 E.00396
G2 X86.38 Y128.216 I1.327 J-.518 E.00398
; LINE_WIDTH: 0.318809
G1 F13048.722
G1 X86.482 Y128.386 E.00447
G1 X86.614 Y128.547 E.00469
G2 X86.754 Y128.697 I1.534 J-1.298 E.00461
; LINE_WIDTH: 0.344103
G1 F11952.896
G1 X86.907 Y128.834 E.00504
; LINE_WIDTH: 0.375901
G1 F10811.425
G1 X87.069 Y128.966 E.00567
; LINE_WIDTH: 0.410927
G1 F9782.423
G1 X87.141 Y129.02 E.0027
; LINE_WIDTH: 0.437966
G1 F9112.873
G1 X87.214 Y129.073 E.0029
G1 X87.23 Y129.068 E.00055
; LINE_WIDTH: 0.409706
G1 F9814.991
G1 X87.494 Y128.98 E.00832
; WIPE_START
G1 X87.23 Y129.068 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X94.276 Y126.134 Z.8 F30000
G1 X125.74 Y113.033 Z.8
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.127072
G1 F15000
G2 X125.261 Y112.958 I-1.779 J9.728 E.00332
G1 X125.263 Y112.943 F30000
; LINE_WIDTH: 0.196496
G1 F15000
G1 X125.568 Y113.009 E.0039
G3 X125.697 Y113.087 I-.028 J.193 E.00193
; LINE_WIDTH: 0.147835
G1 X125.938 Y113.294 E.00272
G1 X126.247 Y113.636 E.00394
; LINE_WIDTH: 0.198336
G1 X126.322 Y113.738 E.00161
G3 X126.396 Y114.079 I-6.585 J1.608 E.00443
G1 X126.381 Y114.081 F30000
; LINE_WIDTH: 0.12872
G1 F15000
G2 X126.306 Y113.599 I-9.611 J1.251 E.00341
; WIPE_START
G1 X126.381 Y114.081 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X126.751 Y115.716 Z.8 F30000
G1 Z.4
G1 E.8 F1800
; LINE_WIDTH: 0.278486
G1 F15000
G2 X126.795 Y114.827 I-17.819 J-1.322 E.01708
G1 X126.783 Y114.805 F30000
; LINE_WIDTH: 0.144259
G1 F15000
G1 X126.799 Y115.744 E.00775
; CHANGE_LAYER
; Z_HEIGHT: 0.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X126.783 Y114.805 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 3/15
; update layer progress
M73 L3
M991 S0 P2 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z.8 I-1.217 J-.016 P1  F30000
G1 X126.032 Y170.646 Z.8
G1 Z.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X125.839 Y170.624 E.006
G3 X125.955 Y167.935 I.236 J-1.337 E.12012
G3 X126.191 Y167.934 I.119 J1.691 E.00723
G3 X126.092 Y170.645 I-.116 J1.353 E.12692
; WIPE_START
M204 S10000
G1 X125.839 Y170.624 E-.09672
G1 X125.609 Y170.568 E-.08995
G1 X125.394 Y170.468 E-.09009
G1 X125.199 Y170.332 E-.09015
G1 X124.96 Y170.07 E-.13491
G1 X124.841 Y169.865 E-.09008
G1 X124.76 Y169.642 E-.09008
G1 X124.724 Y169.44 E-.07802
; WIPE_END
G1 E-.04 F1800
G1 X128.292 Y166.082 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X128.252 Y165.756 E.01008
G3 X129.491 Y164.399 I1.358 J-.004 E.06201
G3 X129.726 Y164.399 I.119 J1.687 E.00723
G3 X128.309 Y166.139 I-.116 J1.353 E.18092
; WIPE_START
M204 S10000
G1 X128.252 Y165.756 E-.1472
G1 X128.27 Y165.518 E-.09068
G1 X128.331 Y165.289 E-.0901
G1 X128.431 Y165.074 E-.09011
G1 X128.567 Y164.88 E-.09009
G1 X128.829 Y164.64 E-.13494
G1 X129.035 Y164.521 E-.09009
G1 X129.101 Y164.497 E-.02678
; WIPE_END
G1 E-.04 F1800
G1 X124.005 Y158.815 Z1 F30000
G1 X118.338 Y152.497 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G3 X119.107 Y152.341 I.697 J1.453 E.02629
G3 X120 Y152.754 I-.111 J1.412 E.03335
G1 X131.296 Y164.049 E.52988
G3 X131.552 Y165.711 I-1.021 J1.009 E.0596
G1 X131.367 Y165.687 E.00622
G2 X129.457 Y167.5 I-1.75 J.069 E.26626
G1 X129.824 Y167.516 E.01221
G1 X127.836 Y169.505 E.09328
G2 X127.053 Y167.838 I-1.891 J-.13 E.06378
G2 X126.007 Y171.047 I-.975 J1.457 E.21459
G1 X126.031 Y171.233 E.00622
G3 X125.626 Y171.369 I-.759 J-1.581 E.0142
G3 X124.369 Y170.976 I-.257 J-1.384 E.04547
G1 X113.074 Y159.681 E.52989
G3 X112.817 Y158.019 I1 J-1.005 E.05971
G1 X113.003 Y158.043 E.00622
G2 X114.908 Y156.229 I1.75 J-.069 E.26643
G1 X114.539 Y156.22 E.01222
G1 X116.534 Y154.226 E.09355
G2 X117.29 Y155.876 I1.897 J.129 E.06279
G2 X118.363 Y152.683 I1 J-1.441 E.21562
G1 X118.346 Y152.557 E.00423
; WIPE_START
G1 X118.525 Y152.42 E-.08546
G1 X118.76 Y152.357 E-.09253
G1 X119.107 Y152.341 E-.13204
G1 X119.364 Y152.384 E-.09911
G1 X119.593 Y152.467 E-.0926
G1 X119.804 Y152.589 E-.09258
G1 X120 Y152.754 E-.09748
G1 X120.127 Y152.881 E-.06821
; WIPE_END
G1 E-.04 F1800
G1 X117.001 Y154.846 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X116.985 Y154.792 E.00175
G3 X118.177 Y153.085 I1.311 J-.354 E.07286
G3 X118.412 Y153.085 I.119 J1.674 E.00723
G3 X117.067 Y155.014 I-.116 J1.353 E.17474
G1 X117.023 Y154.902 E.00367
; WIPE_START
M204 S10000
G1 X116.985 Y154.792 E-.0444
G1 X116.935 Y154.44 E-.13477
G1 X116.956 Y154.204 E-.09008
G1 X117.063 Y153.866 E-.13496
G1 X117.181 Y153.66 E-.0901
G1 X117.334 Y153.479 E-.09009
G1 X117.515 Y153.326 E-.09011
G1 X117.71 Y153.214 E-.0855
; WIPE_END
G1 E-.04 F1800
G1 X113.416 Y158.157 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X113.403 Y157.976 E.00558
G3 X114.642 Y156.621 I1.358 J-.003 E.06195
G3 X114.877 Y156.621 I.119 J1.691 E.00723
G3 X113.425 Y158.216 I-.116 J1.353 E.1855
; WIPE_START
M204 S10000
G1 X113.403 Y157.976 E-.09177
G1 X113.421 Y157.74 E-.09
G1 X113.482 Y157.511 E-.09011
G1 X113.582 Y157.296 E-.09006
G1 X113.718 Y157.102 E-.09014
G1 X113.886 Y156.934 E-.09009
G1 X114.08 Y156.798 E-.09012
G1 X114.391 Y156.669 E-.12772
; WIPE_END
G1 E-.04 F1800
G1 X118.156 Y152.163 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X118.249 Y152.117 E.00318
G3 X119.124 Y151.949 I.778 J1.685 E.02766
G3 X120.272 Y152.471 I-.127 J1.802 E.03956
G1 X131.579 Y163.778 E.49136
G3 X131.579 Y166.316 I-1.269 J1.269 E.08661
G1 X126.636 Y171.259 E.21482
G3 X124.098 Y171.259 I-1.269 J-1.287 E.08644
G1 X112.79 Y159.952 E.49136
G3 X112.791 Y157.414 I1.287 J-1.269 E.08645
G1 X117.734 Y152.471 E.21482
G3 X117.979 Y152.271 I1.293 J1.331 E.00972
G1 X118.105 Y152.194 E.00454
M204 S10000
G1 X118.152 Y152.588 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.174557
G1 F15000
G2 X117.493 Y153.054 I11.158 J16.485 E.00867
; LINE_WIDTH: 0.112353
G1 X117.321 Y153.196 E.00126
G1 X117.355 Y153.127 F30000
; LINE_WIDTH: 0.235375
G1 F15000
G1 X118.156 Y152.616 E.0149
G1 X118.159 Y152.637 F30000
; LINE_WIDTH: 0.306759
G1 F13644.709
G1 X117.418 Y153.064 E.0184
G1 X117.449 Y153.032 F30000
; LINE_WIDTH: 0.387808
G1 F10438.189
G3 X117.995 Y152.735 I4.706 J7.984 E.01747
G1 X118.191 Y152.884 E.00692
G1 X118.923 Y152.566 F30000
; LINE_WIDTH: 0.104947
G1 F15000
G1 X119.003 Y152.577 E.00041
; LINE_WIDTH: 0.143439
G3 X119.146 Y152.611 I-.35 J1.791 E.0012
G1 X119.151 Y152.613 E.00004
; LINE_WIDTH: 0.193504
G3 X119.313 Y152.67 I-.676 J2.155 E.00212
G1 X119.32 Y152.673 E.00009
; LINE_WIDTH: 0.242039
G3 X119.464 Y152.745 I-.748 J1.68 E.0026
G1 X119.544 Y152.795 E.00154
; LINE_WIDTH: 0.284594
G1 F14896.124
G3 X119.759 Y152.97 I-.723 J1.111 E.00546
G1 X120.005 Y153.237 E.00714
; LINE_WIDTH: 0.331301
G1 F12483.492
G1 X120.12 Y153.379 E.00431
; LINE_WIDTH: 0.36593
G1 F11145.172
G1 X120.179 Y153.46 E.00263
; LINE_WIDTH: 0.394239
G1 F10247.123
G1 X120.23 Y153.53 E.00247
; LINE_WIDTH: 0.424373
G1 F9437.606
G1 X120.385 Y153.76 E.00864
; WIPE_START
G1 X120.23 Y153.53 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X117.052 Y153.466 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.112743
G1 F15000
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.157453
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.190489
G1 X116.716 Y153.915 E.00229
G1 X116.749 Y154.125 F30000
; LINE_WIDTH: 0.106139
G1 F15000
G1 X116.758 Y154.027 E.00051
; LINE_WIDTH: 0.154991
G3 X116.809 Y153.673 I7.747 J.949 E.00327
G1 X113.983 Y156.499 F30000
; LINE_WIDTH: 0.143607
G1 F15000
G3 X114.348 Y156.442 I1.508 J8.575 E.00303
; LINE_WIDTH: 0.101318
G1 X114.412 Y156.436 E.00031
G1 X114.218 Y156.408 F30000
; LINE_WIDTH: 0.186847
G1 F15000
G1 X114.071 Y156.506 E.00207
; LINE_WIDTH: 0.155942
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112367
G1 X113.786 Y156.732 E.00126
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.11278
G1 F15000
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.157491
G1 X113.286 Y157.292 E.00134
; LINE_WIDTH: 0.193052
G1 X113.248 Y157.35 E.00085
; LINE_WIDTH: 0.23353
G2 X112.936 Y157.837 I11.219 J7.538 E.00899
G1 X112.956 Y157.839 F30000
; LINE_WIDTH: 0.306762
G1 F13644.545
G1 X113.384 Y157.098 E.01839
G1 X113.354 Y157.128 F30000
; LINE_WIDTH: 0.38776
G1 F10439.636
G2 X113.055 Y157.675 I7.825 J4.635 E.01755
G1 X113.203 Y157.872 E.00692
G1 X112.885 Y158.603 F30000
; LINE_WIDTH: 0.104946
G1 F15000
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.143617
G2 X112.931 Y158.826 I1.659 J-.316 E.00121
G1 X112.932 Y158.831 E.00004
; LINE_WIDTH: 0.193577
G2 X112.99 Y158.994 I2.253 J-.713 E.00212
G1 X112.993 Y159.001 E.00009
; LINE_WIDTH: 0.242078
G2 X113.065 Y159.144 I1.674 J-.745 E.0026
G1 X113.115 Y159.225 E.00154
; LINE_WIDTH: 0.284604
G1 F14895.52
G2 X113.289 Y159.439 I1.108 J-.72 E.00546
G1 X113.556 Y159.685 E.00714
; LINE_WIDTH: 0.332078
G1 F12449.965
G1 X113.705 Y159.805 E.00449
; LINE_WIDTH: 0.370588
G1 F10986.729
G1 X113.798 Y159.873 E.00309
; LINE_WIDTH: 0.405069
G1 F9940.675
G1 X113.879 Y159.931 E.00293
; LINE_WIDTH: 0.431185
G1 F9272.033
G1 X114.08 Y160.065 E.00767
G1 X114.139 Y160.272 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42317
G1 F9467.455
G1 X123.657 Y169.791 E.41711
G1 X123.974 Y169.569 E.01196
G1 X114.476 Y160.072 E.41617
G1 X114.498 Y160.04 E.00119
G2 X114.989 Y160.047 I.271 J-1.834 E.01527
G1 X124.006 Y169.064 E.39514
G3 X124.103 Y168.623 I1.547 J.108 E.01404
G1 X115.426 Y159.946 E.38023
G2 X115.796 Y159.779 I-.29 J-1.132 E.01265
G1 X124.266 Y168.248 E.37112
G1 X124.489 Y167.934 E.01195
G1 X116.112 Y159.556 E.36711
G2 X116.381 Y159.288 I-1.141 J-1.413 E.0118
G1 X124.763 Y167.67 E.3673
G1 X125.087 Y167.456 E.01203
G1 X116.594 Y158.963 E.37215
G2 X116.754 Y158.585 I-1.357 J-.795 E.01276
G1 X125.468 Y167.299 E.38187
G3 X125.921 Y167.215 I.473 J1.28 E.01436
G1 X116.839 Y158.133 E.39798
G2 X116.797 Y157.553 I-1.668 J-.169 E.01812
G1 X126.492 Y167.247 E.42483
G3 X128.09 Y168.749 I-.418 J2.046 E.07154
G1 X128.094 Y168.775 E.0008
G1 X128.326 Y168.544 E.01013
G1 X115.506 Y155.724 E.56175
G1 X115.775 Y155.455 E.01178
G1 X128.594 Y168.275 E.56175
G1 X128.863 Y168.006 E.01178
G1 X116.044 Y155.186 E.56175
G1 X116.275 Y154.955 E.01013
G2 X117.878 Y156.483 I2.047 J-.543 E.07219
G1 X127.572 Y166.177 E.42481
G3 X127.53 Y165.597 I1.695 J-.415 E.0181
G1 X118.447 Y156.514 E.39801
G2 X118.901 Y156.431 I-.01 J-1.33 E.01438
G1 X127.619 Y165.148 E.38201
M73 P41 R6
G3 X127.775 Y164.767 I1.159 J.253 E.01284
G1 X119.281 Y156.272 E.37223
G2 X119.603 Y156.057 I-.449 J-1.022 E.01208
G1 X127.989 Y164.443 E.36746
G1 X128.254 Y164.17 E.01178
G1 X119.876 Y155.792 E.36711
G2 X120.104 Y155.482 I-1.067 J-1.022 E.01195
G1 X128.568 Y163.946 E.37092
G3 X128.943 Y163.784 I.805 J1.344 E.01271
G1 X120.27 Y155.11 E.38008
G2 X120.367 Y154.669 I-1.625 J-.588 E.01403
G1 X129.38 Y163.683 E.39499
G3 X129.874 Y163.687 I.225 J2.945 E.01531
G1 X129.893 Y163.658 E.00107
G1 X120.392 Y154.157 E.41635
G1 X120.714 Y153.941 E.01201
G1 X130.231 Y163.458 E.41702
G1 X130.289 Y163.665 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.425246
G1 F9416.048
G1 X130.507 Y163.81 E.00815
; LINE_WIDTH: 0.39677
G1 F10173.812
G1 X130.59 Y163.87 E.00296
; LINE_WIDTH: 0.367961
G1 F11075.549
G1 X130.66 Y163.922 E.00229
; LINE_WIDTH: 0.33407
G1 F12364.755
G1 X130.804 Y164.037 E.0044
; LINE_WIDTH: 0.285082
G1 F14866.101
G3 X131.193 Y164.419 I-1.983 J2.407 E.01076
G1 X131.254 Y164.506 E.0021
; LINE_WIDTH: 0.242054
G1 F15000
G3 X131.376 Y164.73 I-1.081 J.734 E.00414
; LINE_WIDTH: 0.193565
G3 X131.437 Y164.899 I-2.853 J1.124 E.00221
; LINE_WIDTH: 0.143634
G3 X131.473 Y165.047 I-1.864 J.522 E.00125
; LINE_WIDTH: 0.104947
G1 X131.484 Y165.127 E.00041
G1 X131.166 Y165.858 F30000
; LINE_WIDTH: 0.387803
G1 F10438.319
G1 X131.315 Y166.055 E.00692
G3 X131.022 Y166.595 I-9.308 J-4.684 E.01728
G1 X130.985 Y166.632 F30000
; LINE_WIDTH: 0.306758
G1 F13644.765
G1 X131.413 Y165.891 E.01841
G1 X131.433 Y165.893 F30000
; LINE_WIDTH: 0.235396
G1 F15000
G1 X131.16 Y166.323 E.00799
; LINE_WIDTH: 0.220022
G1 X131.122 Y166.381 E.001
; LINE_WIDTH: 0.191861
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155924
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112354
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112752
G1 F15000
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157459
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.190488
G1 X130.135 Y167.334 E.00229
G1 X129.925 Y167.301 F30000
; LINE_WIDTH: 0.106116
G1 F15000
G1 X130.023 Y167.292 E.00051
; LINE_WIDTH: 0.154993
G2 X130.377 Y167.241 I-.941 J-7.676 E.00327
G1 X127.561 Y170.057 F30000
; LINE_WIDTH: 0.164658
G1 F15000
G1 X127.594 Y169.84 E.00218
; LINE_WIDTH: 0.139074
G1 X127.612 Y169.7 E.00111
; LINE_WIDTH: 0.105812
G1 X127.621 Y169.606 E.00049
G1 X127.653 Y169.815 F30000
; LINE_WIDTH: 0.190112
G1 F15000
G1 X127.544 Y169.979 E.00235
; LINE_WIDTH: 0.155936
G1 X127.46 Y170.092 E.0013
; LINE_WIDTH: 0.112809
G1 X127.313 Y170.269 E.00131
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.112769
G1 F15000
G1 X126.873 Y170.679 E.00129
; LINE_WIDTH: 0.157481
G1 X126.758 Y170.763 E.00134
; LINE_WIDTH: 0.193037
G1 X126.7 Y170.802 E.00085
; LINE_WIDTH: 0.233559
G3 X126.213 Y171.114 I-7.443 J-11.078 E.00899
G1 X126.211 Y171.094 F30000
; LINE_WIDTH: 0.306772
G1 F13644.021
G1 X126.952 Y170.666 E.0184
G1 X126.918 Y170.699 F30000
; LINE_WIDTH: 0.387856
G1 F10436.737
G3 X126.374 Y170.995 I-4.845 J-8.266 E.0174
G1 X126.178 Y170.847 E.00692
G1 X125.446 Y171.165 F30000
; LINE_WIDTH: 0.104947
G1 F15000
G1 X125.367 Y171.153 E.00041
; LINE_WIDTH: 0.143629
G3 X125.218 Y171.118 I.371 J-1.89 E.00125
; LINE_WIDTH: 0.193547
G3 X125.049 Y171.057 I.95 J-2.9 E.00221
; LINE_WIDTH: 0.242067
G3 X124.825 Y170.935 I.511 J-1.205 E.00415
; LINE_WIDTH: 0.285119
G1 F14863.803
G1 X124.739 Y170.873 E.0021
G3 X124.357 Y170.485 I2.025 J-2.371 E.01076
; LINE_WIDTH: 0.334079
G1 F12364.39
G1 X124.241 Y170.34 E.0044
; LINE_WIDTH: 0.367946
G1 F11076.035
G1 X124.19 Y170.27 E.00229
; LINE_WIDTH: 0.406388
G1 F9904.597
G3 X123.979 Y169.972 I6.698 J-4.966 E.01082
; OBJECT_ID: 795
; WIPE_START
G1 X124.19 Y170.27 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 795
M624 AQAAAAAAAAA=
G1 X129.511 Y164.798 Z1 F30000
G1 X147.638 Y146.152 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X147.716 Y146.279 E.00494
G3 X146.095 Y145.301 I-1.539 J.719 E.28746
G3 X146.465 Y145.323 I.074 J1.818 E.01231
G3 X147.567 Y146.021 I-.288 J1.674 E.04442
G1 X147.609 Y146.099 E.00295
M204 S250
G1 X147.31 Y146.341 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.112 Y145.692 I-1.131 J.658 E.20869
G3 X146.283 Y145.695 I.072 J.976 E.00527
G3 X147.279 Y146.29 I-.105 J1.305 E.03693
; WIPE_START
M204 S10000
G1 X147.4 Y146.552 E-.10956
G1 X147.459 Y146.773 E-.08678
G1 X147.479 Y147 E-.08678
G1 X147.459 Y147.228 E-.08678
G1 X147.4 Y147.448 E-.08678
G1 X147.273 Y147.703 E-.10837
G1 X147.096 Y147.927 E-.10835
G1 X146.921 Y148.073 E-.0866
; WIPE_END
G1 E-.04 F1800
G1 X150.744 Y141.467 Z1 F30000
G1 X152.935 Y137.68 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X153.052 Y137.916 E.00873
G3 X151.372 Y136.801 I-1.598 J.584 E.28302
G3 X151.742 Y136.823 I.074 J1.82 E.01232
G3 X152.913 Y137.625 I-.288 J1.677 E.04855
M204 S250
G1 X152.587 Y137.841 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X151.389 Y137.192 I-1.132 J.659 E.20877
G3 X151.56 Y137.195 I.071 J.975 E.00527
G3 X152.556 Y137.79 I-.105 J1.305 E.03692
; WIPE_START
M204 S10000
G1 X152.677 Y138.052 E-.10966
G1 X152.751 Y138.386 E-.12998
G1 X152.751 Y138.614 E-.08676
G1 X152.677 Y138.948 E-.12999
G1 X152.581 Y139.155 E-.08677
G1 X152.45 Y139.342 E-.08683
G1 X152.288 Y139.504 E-.08674
G1 X152.195 Y139.569 E-.04328
; WIPE_END
G1 E-.04 F1800
G1 X159.104 Y136.326 Z1 F30000
G1 X161.811 Y135.055 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X161.459 Y135.102 E.01178
G1 X150.433 Y135.102 E.36577
G3 X148.844 Y133.513 I.027 J-1.616 E.08241
G1 X148.844 Y130.487 E.1004
G3 X150.433 Y128.898 I1.616 J.027 E.08241
G1 X161.459 Y128.898 E.36578
G3 X163.048 Y130.487 I-.027 J1.616 E.08241
G1 X163.048 Y133.513 E.1004
G3 X161.87 Y135.042 I-1.616 J-.027 E.06861
M204 S250
G1 X161.759 Y134.667 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X161.451 Y134.71 I-.324 J-1.177 E.00958
G1 X150.441 Y134.71 E.33829
G3 X149.236 Y133.505 I.007 J-1.212 E.05808
G1 X149.236 Y130.495 E.09247
G3 X150.441 Y129.29 I1.221 J.016 E.05798
G1 X161.451 Y129.29 E.33829
G3 X162.656 Y130.495 I-.016 J1.221 E.05798
G1 X162.656 Y133.505 E.09247
G3 X161.816 Y134.649 I-1.221 J-.016 E.04655
; WIPE_START
M204 S10000
G1 X161.451 Y134.71 E-.14077
G1 X159.821 Y134.71 E-.61923
; WIPE_END
G1 E-.04 F1800
G1 X152.433 Y132.796 Z1 F30000
G1 X144.489 Y130.739 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X144.498 Y130.705 E.00114
G3 X146.095 Y129.301 I1.674 J.293 E.07622
G3 X147.604 Y131.914 I.066 J1.704 E.12288
G3 X144.472 Y131 I-1.432 J-.916 E.14498
G1 X144.485 Y130.798 E.0067
M204 S250
G1 X144.889 Y130.774 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.112 Y129.692 I1.29 J.226 E.05418
G3 X146.283 Y129.695 I.071 J.975 E.00527
G3 X144.88 Y130.834 I-.105 J1.305 E.1915
; WIPE_START
M204 S10000
G1 X144.982 Y130.446 E-.1522
G1 X145.096 Y130.249 E-.08675
G1 X145.243 Y130.074 E-.08682
G1 X145.417 Y129.927 E-.08675
G1 X145.615 Y129.813 E-.08684
G1 X145.83 Y129.735 E-.08675
G1 X146.112 Y129.692 E-.10836
G1 X146.283 Y129.695 E-.0651
G1 X146.284 Y129.695 E-.00043
; WIPE_END
G1 E-.04 F1800
G1 X142.901 Y130.3 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X143.154 Y130.515 E.01102
G3 X143.771 Y131.987 I-1.489 J1.489 E.0543
G1 X143.771 Y146.013 E.46529
G3 X141.682 Y148.102 I-2.121 J-.032 E.1084
G1 X134.611 Y148.102 E.23458
G3 X132.762 Y145.023 I.026 J-2.11 E.14249
G1 X133.298 Y144.103 E.0353
G2 X133.996 Y135.521 I-9.629 J-5.103 E.29364
G2 X132.762 Y132.977 I-11.994 J4.249 E.09399
G3 X134.611 Y129.898 I1.875 J-.969 E.14249
G1 X141.682 Y129.898 E.23459
G3 X142.853 Y130.265 I-.017 J2.106 E.04128
M204 S250
G1 X142.649 Y130.6 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X143.379 Y131.995 I-.984 J1.403 E.05026
G1 X143.379 Y146.005 E.43047
G3 X141.674 Y147.71 I-1.725 J-.02 E.08205
G1 X134.619 Y147.71 E.21677
G3 X133.109 Y145.206 I.016 J-1.717 E.10753
G1 X133.644 Y144.287 E.03266
G2 X134.368 Y135.396 I-9.975 J-5.287 E.28179
G2 X133.109 Y132.795 I-12.327 J4.361 E.08898
G3 X134.619 Y130.29 I1.525 J-.788 E.10753
G1 X141.674 Y130.29 E.21678
G3 X142.599 Y130.567 I-.008 J1.714 E.0301
; WIPE_START
M204 S10000
G1 X142.878 Y130.791 E-.13592
G1 X143.07 Y131.019 E-.11327
G1 X143.219 Y131.277 E-.11328
G1 X143.321 Y131.557 E-.11328
G1 X143.353 Y131.703 E-.0567
G1 X143.379 Y131.995 E-.11151
G1 X143.379 Y132.301 E-.11604
; WIPE_END
G1 E-.04 F1800
G1 X135.774 Y132.945 Z1 F30000
G1 X114.506 Y134.746 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X114.514 Y134.731 E.00057
G3 X122.789 Y128.936 I9.155 J4.267 E.35092
G1 X123.229 Y128.917 E.01461
G1 X123.669 Y128.897 E.01462
G3 X114.177 Y135.545 I0 J10.1 E1.69574
G1 X114.484 Y134.802 E.02667
M204 S250
G1 X114.87 Y134.897 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X122.823 Y129.327 I8.799 J4.1 E.31243
G1 X123.246 Y129.308 E.01301
G1 X123.669 Y129.29 E.01301
G3 X114.845 Y134.952 I0 J9.707 E1.53377
; WIPE_START
M204 S10000
G1 X115.26 Y134.145 E-.34461
G1 X115.715 Y133.43 E-.32196
G1 X115.865 Y133.235 E-.09343
; WIPE_END
G1 E-.04 F1800
G1 X122.915 Y136.159 Z1 F30000
G1 X167.196 Y154.52 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X167.721 Y155.206 E.02866
G3 X158.566 Y150.936 I-8.275 J5.792 E1.75422
G1 X159.006 Y150.917 E.01461
G1 X159.446 Y150.897 E.01462
G3 X167.157 Y154.474 I0 J10.1 E.29102
M204 S250
G1 X166.884 Y154.759 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
M73 P42 R6
G3 X158.6 Y151.327 I-7.438 J6.238 E1.58767
G1 X159.023 Y151.308 E.01301
G1 X159.446 Y151.29 E.01301
G3 X166.845 Y154.713 I0 J9.707 E.25852
; WIPE_START
M204 S10000
G1 X167.4 Y155.43 E-.34461
G1 X167.855 Y156.145 E-.32196
G1 X167.969 Y156.363 E-.09343
; WIPE_END
G1 E-.04 F1800
G1 X166.722 Y152.127 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.689 Y152.128 E.00112
G3 X165.469 Y151.907 I-.251 J-2.096 E.04174
G1 X164.549 Y151.371 E.0353
G2 X155.967 Y150.673 I-5.103 J9.629 E.29363
G2 X153.423 Y151.907 I4.248 J11.992 E.094
G3 X150.374 Y150.404 I-.975 J-1.866 E.13125
G3 X150.344 Y149.326 I6.159 J-.712 E.03582
G3 X151.655 Y147.391 I2.109 J.017 E.08215
G1 X165.678 Y141.789 E.50094
G3 X166.183 Y141.659 I.828 J2.185 E.01731
G3 X168.548 Y143.733 I.261 J2.088 E.11784
G1 X168.548 Y150.058 E.20983
G3 X167.04 Y152.055 I-2.11 J-.026 E.08887
G1 X166.781 Y152.114 E.0088
M204 S250
G1 X166.644 Y151.739 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X165.652 Y151.56 I-.204 J-1.705 E.03144
G1 X164.733 Y151.025 E.03266
G2 X155.842 Y150.301 I-5.287 J9.976 E.28179
G2 X153.241 Y151.56 I4.361 J12.327 E.08898
G3 X150.761 Y150.337 I-.793 J-1.518 E.09888
G3 X150.736 Y149.334 I5.791 J-.645 E.03087
G3 X151.808 Y147.752 I1.717 J.009 E.06226
G1 X165.816 Y142.156 E.46351
G3 X166.232 Y142.049 I.682 J1.787 E.01323
G3 X168.156 Y143.741 I.212 J1.699 E.08897
G1 X168.156 Y150.05 E.19386
G3 X166.703 Y151.731 I-1.717 J-.015 E.07426
; WIPE_START
M204 S10000
G1 X166.498 Y151.755 E-.07833
G1 X166.352 Y151.753 E-.05564
G1 X166.062 Y151.712 E-.11105
G1 X165.784 Y151.623 E-.11109
G1 X165.652 Y151.56 E-.05573
G1 X164.86 Y151.099 E-.34817
; WIPE_END
G1 E-.04 F1800
G1 X167.064 Y143.791 Z1 F30000
G1 X168.915 Y137.652 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X168.995 Y137.778 E.00494
G3 X167.372 Y136.801 I-1.541 J.723 E.2881
G3 X167.742 Y136.823 I.074 J1.82 E.01232
G3 X168.845 Y137.521 I-.288 J1.677 E.04443
G1 X168.887 Y137.599 E.00294
M204 S250
G1 X168.587 Y137.841 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X167.389 Y137.192 I-1.132 J.659 E.20885
G3 X167.56 Y137.195 I.071 J.975 E.00527
G3 X168.556 Y137.79 I-.105 J1.306 E.03693
; WIPE_START
M204 S10000
G1 X168.677 Y138.052 E-.10968
G1 X168.751 Y138.386 E-.12998
G1 X168.751 Y138.614 E-.08676
G1 X168.712 Y138.839 E-.0868
G1 X168.634 Y139.054 E-.08679
G1 X168.45 Y139.342 E-.12999
G1 X168.288 Y139.504 E-.08674
G1 X168.195 Y139.569 E-.04326
; WIPE_END
G1 E-.04 F1800
G1 X160.742 Y141.213 Z1 F30000
G1 X128.082 Y148.419 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X127.169 Y148.791 E.03272
G3 X123.387 Y128.606 I-3.491 J-9.793 E1.19188
G1 X158.73 Y127.603 E1.17285
G1 X159.707 Y127.644 E.03245
G3 X170.125 Y138.631 I-1.003 J11.384 E.54897
G1 X169.843 Y161.118 E.74599
; object ids of layer 3 start: 795,817,839,861
M624 DwAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer3 end: 795,817,839,861
M625
G3 X149.447 Y158.151 I-10.396 J-.124 E1.17487
G1 X149.877 Y156.852 E.04541
G2 X147.433 Y150.558 I-5.389 J-1.528 E.24039
M73 P42 R5
G1 X145.26 Y149.222 E.08462
G2 X142.347 Y148.398 I-2.921 J4.766 E.10168
G1 X128.138 Y148.398 E.47134
M204 S250
G1 X128.211 Y148.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X118.058 Y129.784 I-4.533 J-9.793 E1.00388
G1 X118.875 Y129.334 E.02864
G3 X123.367 Y128.214 I4.905 J10.107 E.1433
G1 X158.732 Y127.21 E1.08711
G1 X159.74 Y127.253 E.031
G3 X170.518 Y138.618 I-1.038 J11.776 E.52604
G1 X170.235 Y161.131 E.6918
G3 X149.069 Y158.044 I-10.789 J-.133 E1.1294
G1 X149.5 Y156.745 E.04205
G2 X147.22 Y150.888 I-5.013 J-1.421 E.20731
G1 X145.061 Y149.56 E.07789
G2 X142.339 Y148.79 I-2.724 J4.436 E.088
G1 X128.271 Y148.79 E.4323
M204 S10000
G1 X128.393 Y148.185 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.331146
G1 F12490.228
G1 X129.207 Y147.967 E.01979
G1 X131.546 Y147.111 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.58492
G1 F6642.067
G2 X131.55 Y147.221 I-.029 J.056 E.01173
G1 X132.28 Y147.629 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X132.028 Y147.227 E.01459
G1 X131.857 Y146.767 E.01508
G1 X131.766 Y146.242 E.01635
G1 X131.374 Y146.67 E.01782
G1 X130.676 Y147.312 E.02914
G1 X130.249 Y147.629 E.01632
G1 X132.22 Y147.629 E.06055
G1 X132.898 Y147.786 F30000
G1 F9547.299
G1 X132.725 Y147.617 E.00742
G1 X132.398 Y147.125 E.01815
G3 X132.155 Y145.694 I2.354 J-1.135 E.0452
G1 X131.87 Y145.537 E.01002
G3 X130.421 Y147.034 I-8.807 J-7.067 E.06411
G3 X129.537 Y147.684 I-262.108 J-356.104 E.03372
G1 X129.623 Y148.006 E.01025
G1 X132.827 Y148.006 E.09844
G1 X132.826 Y147.873 E.00408
G1 X132.86 Y147.832 E.00163
G1 X133.297 Y147.916 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.121009
G1 F15000
G1 X133.464 Y148.052 E.00137
; LINE_WIDTH: 0.165445
G1 X133.654 Y148.194 E.00237
G1 X133.791 Y148.173 F30000
; LINE_WIDTH: 0.133873
G1 F15000
G3 X133.437 Y148.099 I1.455 J-7.846 E.00268
; WIPE_START
G1 X133.791 Y148.173 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.17 Y145.255 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.474748
G1 F8336.657
G1 X132.397 Y144.842 E.01659
; LINE_WIDTH: 0.431339
G1 F9268.36
G3 X132.754 Y144.255 I13.594 J7.875 E.02173
G2 X132.406 Y133.174 I-9.076 J-5.261 E.36971
; LINE_WIDTH: 0.473821
G1 F8354.599
G1 X132.17 Y132.746 E.01718
G1 X128.452 Y129.927 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X127.372 Y128.847 E.04702
G1 X127.374 Y128.826 E.00064
G1 X127.871 Y128.812 E.01529
G1 X129.257 Y130.198 E.06031
G3 X131.664 Y132.292 I-5.376 J8.609 E.0986
G1 X131.854 Y132.54 E.00961
G1 X132.034 Y132.44 E.00632
G1 X128.39 Y128.797 E.15856
G1 X128.91 Y128.782 E.01599
G1 X132.192 Y132.064 E.14284
G3 X132.233 Y131.571 I2.574 J-.033 E.01525
G1 X129.429 Y128.768 E.12203
G1 X129.948 Y128.753 E.01599
G1 X132.348 Y131.152 E.10443
G3 X132.518 Y130.789 I1.138 J.312 E.01242
G1 X130.468 Y128.738 E.08925
G1 X130.987 Y128.723 E.01599
G1 X132.735 Y130.471 E.07608
G3 X132.994 Y130.196 I.926 J.611 E.01169
G1 X131.507 Y128.709 E.06473
G1 X132.026 Y128.694 E.01599
G1 X133.294 Y129.962 E.0552
G1 X133.639 Y129.773 E.01211
G1 X132.545 Y128.679 E.04761
G1 X133.065 Y128.664 E.01599
G1 X134.037 Y129.637 E.04232
G3 X134.507 Y129.573 I.487 J1.81 E.01463
G1 X133.584 Y128.65 E.04017
G1 X134.103 Y128.635 E.01599
G1 X135.033 Y129.565 E.04047
G1 X135.567 Y129.565 E.01644
G1 X134.623 Y128.62 E.04111
G1 X135.142 Y128.606 E.01599
G1 X136.101 Y129.565 E.04175
G1 X136.636 Y129.565 E.01644
G1 X135.661 Y128.591 E.0424
G1 X136.181 Y128.576 E.01599
G1 X137.17 Y129.565 E.04304
G1 X137.704 Y129.565 E.01644
G1 X136.7 Y128.561 E.04368
G1 X137.22 Y128.547 E.01599
G1 X138.238 Y129.565 E.04432
G1 X138.772 Y129.565 E.01644
G1 X137.739 Y128.532 E.04496
G1 X138.258 Y128.517 E.01599
G1 X139.306 Y129.565 E.0456
G1 X139.84 Y129.565 E.01644
G1 X138.778 Y128.502 E.04625
G1 X139.297 Y128.488 E.01599
G1 X140.374 Y129.565 E.04689
G1 X140.908 Y129.565 E.01644
G1 X139.816 Y128.473 E.04753
G1 X140.336 Y128.458 E.01599
G1 X141.443 Y129.565 E.04817
G3 X142.004 Y129.592 I.127 J3.162 E.01732
G1 X140.855 Y128.443 E.05
G1 X141.374 Y128.429 E.01599
G1 X142.789 Y129.844 E.06158
G3 X143.742 Y130.727 I-1.19 J2.237 E.04044
G1 X143.827 Y130.611 E.00443
G1 X143.841 Y130.622 E.00054
M73 P43 R5
G1 X143.856 Y130.601 E.00079
G1 X143.875 Y130.614 E.0007
G1 X143.97 Y130.49 E.00482
G1 X141.894 Y128.414 E.09037
G1 X142.413 Y128.399 E.01599
G1 X144.278 Y130.264 E.08115
G3 X144.456 Y129.908 I1.097 J.329 E.01231
G1 X142.933 Y128.384 E.06632
G1 X143.452 Y128.37 E.01599
G1 X144.689 Y129.607 E.05385
G3 X144.972 Y129.356 I.854 J.677 E.0117
G1 X143.971 Y128.355 E.04355
G1 X144.491 Y128.34 E.01599
G1 X145.306 Y129.155 E.03548
G1 X145.706 Y129.022 E.013
G1 X145.01 Y128.325 E.03032
G1 X145.529 Y128.311 E.01599
G1 X146.192 Y128.973 E.02882
G3 X146.829 Y129.076 I.065 J1.617 E.02
G1 X146.049 Y128.296 E.03395
G1 X146.568 Y128.281 E.01599
G1 X148.532 Y130.245 E.08546
G3 X148.64 Y129.819 I1.26 J.095 E.01358
G1 X147.087 Y128.266 E.06759
G1 X147.607 Y128.252 E.01599
G1 X148.817 Y129.462 E.05268
G3 X149.051 Y129.161 I.97 J.511 E.01178
G1 X148.126 Y128.237 E.04023
G1 X148.645 Y128.222 E.01599
G1 X149.336 Y128.913 E.03006
G1 X149.682 Y128.725 E.01212
G1 X149.165 Y128.207 E.02251
G1 X149.684 Y128.193 E.01599
G1 X150.098 Y128.607 E.01803
G3 X150.591 Y128.565 I.402 J1.807 E.01525
G1 X150.204 Y128.178 E.01684
G1 X150.723 Y128.163 E.01599
G1 X151.125 Y128.565 E.01748
G1 X151.659 Y128.565 E.01644
G1 X151.242 Y128.148 E.01813
G1 X151.762 Y128.134 E.01599
G1 X152.193 Y128.565 E.01877
G1 X152.727 Y128.565 E.01644
G1 X152.281 Y128.119 E.01941
G1 X152.8 Y128.104 E.01599
G1 X153.261 Y128.565 E.02005
G1 X153.795 Y128.565 E.01644
G1 X153.32 Y128.089 E.02069
G1 X153.839 Y128.075 E.01599
G1 X154.329 Y128.565 E.02133
G1 X154.863 Y128.565 E.01644
G1 X154.358 Y128.06 E.02198
G1 X154.878 Y128.045 E.01599
G1 X155.397 Y128.565 E.02262
G1 X155.932 Y128.565 E.01644
G1 X155.397 Y128.03 E.02326
G1 X155.917 Y128.016 E.01599
G1 X156.466 Y128.565 E.0239
G1 X157 Y128.565 E.01644
G1 X156.436 Y128.001 E.02454
G1 X156.955 Y127.986 E.01599
G1 X157.534 Y128.565 E.02518
G1 X158.068 Y128.565 E.01644
G1 X157.475 Y127.971 E.02583
G1 X157.994 Y127.957 E.01599
G1 X158.602 Y128.565 E.02647
G1 X159.136 Y128.565 E.01644
G1 X158.513 Y127.942 E.02711
G3 X159.055 Y127.95 I.215 J3.81 E.0167
G1 X159.67 Y128.565 E.02676
G1 X160.204 Y128.565 E.01644
G1 X159.613 Y127.974 E.02573
G3 X160.22 Y128.046 I-.121 J3.58 E.01883
G1 X160.908 Y128.735 E.02995
G1 X161.319 Y128.117 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.551427
G1 F7079.55
G1 X161.528 Y128.434 E.01571
G1 X161.615 Y128.449 E.00365
; LINE_WIDTH: 0.515349
G1 F7620.192
G3 X162.456 Y128.71 I-.753 J3.908 E.03399
G1 X162.459 Y128.725 E.00056
; LINE_WIDTH: 0.497546
G1 F7918.606
G1 X162.53 Y129.04 E.01198
G1 X167.912 Y132.534 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X166.427 Y131.049 E.06463
G2 X164.271 Y129.427 I-8.35 J8.855 E.08321
G1 X168.3 Y133.456 E.17537
G3 X168.847 Y134.536 I-6.025 J3.724 E.0373
G1 X163.188 Y128.878 E.24628
G1 X163.097 Y128.841 E.00304
G1 X163.171 Y129.238 E.01243
G1 X163.043 Y129.267 E.00405
G1 X169.19 Y135.414 E.26755
G3 X169.423 Y136.181 I-4.363 J1.745 E.02471
G1 X163.338 Y130.096 E.26485
G3 X163.381 Y130.674 I-3.032 J.519 E.01786
G1 X169.589 Y136.881 E.27016
G1 X169.692 Y137.518 E.01987
G1 X163.381 Y131.208 E.27465
G1 X163.381 Y131.742 E.01644
G1 X169.752 Y138.113 E.27728
G3 X169.791 Y138.686 I-3.239 J.509 E.01771
G1 X169.469 Y138.363 E.01406
G3 X169.442 Y138.87 I-1.454 J.177 E.01571
G1 X169.785 Y139.214 E.01494
G1 X169.778 Y139.741 E.01623
G1 X169.321 Y139.283 E.01992
G3 X169.136 Y139.632 I-1.083 J-.35 E.01222
G1 X169.772 Y140.269 E.02768
G1 X169.765 Y140.796 E.01624
G1 X168.897 Y139.928 E.03778
G1 X168.608 Y140.173 E.01166
G1 X169.758 Y141.323 E.05008
G1 X169.752 Y141.851 E.01623
G1 X168.263 Y140.362 E.06479
G3 X167.859 Y140.492 I-.695 J-1.47 E.0131
G1 X169.745 Y142.378 E.0821
G1 X169.739 Y142.906 E.01624
G1 X167.176 Y140.343 E.11154
G1 X167.524 Y141.759 F30000
G1 F9532.131
G1 X161.194 Y135.43 E.27548
G1 X160.661 Y135.43 E.01643
G1 X166.542 Y141.311 E.25596
G2 X166.042 Y141.345 I-.117 J1.972 E.01547
G1 X160.127 Y135.431 E.25743
G1 X159.593 Y135.431 E.01643
G1 X165.62 Y141.458 E.26233
G2 X165.235 Y141.607 I.667 J2.3 E.01273
G1 X159.059 Y135.431 E.26879
G1 X158.525 Y135.431 E.01643
G1 X164.853 Y141.759 E.27542
G1 X164.472 Y141.912 E.01265
G1 X157.991 Y135.432 E.28204
G1 X157.457 Y135.432 E.01643
G1 X164.09 Y142.064 E.28866
G1 X163.708 Y142.217 E.01265
G1 X156.924 Y135.432 E.29529
G1 X156.39 Y135.432 E.01643
G1 X163.327 Y142.369 E.30191
G1 X162.945 Y142.522 E.01265
G1 X155.856 Y135.433 E.30854
G1 X155.322 Y135.433 E.01643
G1 X162.563 Y142.674 E.31516
G1 X162.182 Y142.827 E.01265
G1 X154.788 Y135.433 E.32178
G1 X154.254 Y135.433 E.01643
G1 X161.8 Y142.979 E.32841
G1 X161.418 Y143.132 E.01265
G1 X153.721 Y135.434 E.33503
G1 X153.187 Y135.434 E.01643
G1 X161.037 Y143.284 E.34166
G1 X160.655 Y143.436 E.01265
G1 X152.653 Y135.434 E.34828
G1 X152.119 Y135.434 E.01643
G1 X160.274 Y143.589 E.35491
G1 X159.892 Y143.741 E.01265
G1 X151.585 Y135.435 E.36153
G1 X151.051 Y135.435 E.01643
G1 X159.51 Y143.894 E.36815
G1 X159.129 Y144.046 E.01265
G1 X153.474 Y138.391 E.24612
G3 X153.442 Y138.893 I-2.541 J.09 E.01551
G1 X158.747 Y144.199 E.2309
G1 X158.365 Y144.351 E.01265
G1 X153.311 Y139.297 E.21997
G1 X153.124 Y139.644 E.01213
G1 X157.984 Y144.504 E.21152
G1 X157.602 Y144.656 E.01265
G1 X152.886 Y139.941 E.20524
G1 X152.593 Y140.181 E.01168
G1 X157.22 Y144.809 E.2014
G1 X156.839 Y144.961 E.01265
G1 X152.246 Y140.368 E.19988
G3 X151.84 Y140.496 I-.688 J-1.478 E.01314
G1 X156.457 Y145.114 E.20095
G1 X156.075 Y145.266 E.01265
G1 X151.15 Y140.341 E.21435
; WIPE_START
G1 X152.565 Y141.755 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.605 Y138.796 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F9532.131
G1 X144.104 Y133.294 E.23945
G1 X144.104 Y132.76 E.01643
G1 X149.45 Y138.106 E.23267
G3 X149.578 Y137.7 I1.606 J.282 E.01314
G1 X144.23 Y132.352 E.23276
G1 X144.239 Y132.335 E.00058
G1 X144.498 Y132.467 E.00895
G1 X144.593 Y132.279 E.00649
G2 X145.19 Y132.778 I1.588 J-1.293 E.02407
G1 X149.765 Y137.353 E.19913
G1 X150.006 Y137.06 E.01168
G1 X145.965 Y133.019 E.17585
G2 X146.489 Y133.009 I.233 J-1.489 E.01621
G1 X150.299 Y136.819 E.16582
G1 X150.646 Y136.632 E.01213
G1 X146.906 Y132.892 E.16279
G2 X147.261 Y132.713 I-.329 J-1.098 E.0123
G1 X148.59 Y134.041 E.05782
G3 X148.511 Y133.429 I1.935 J-.56 E.01908
G1 X147.562 Y132.48 E.04129
G1 X147.808 Y132.192 E.01166
G1 X148.512 Y132.896 E.03063
G1 X148.513 Y132.362 E.01641
G1 X148.005 Y131.855 E.02209
G2 X148.146 Y131.462 I-.895 J-.542 E.01294
G1 X148.514 Y131.829 E.016
G1 X148.515 Y131.296 E.01641
G1 X148.205 Y130.986 E.01349
G2 X148.086 Y130.333 I-1.86 J.002 E.02055
G1 X148.685 Y130.932 E.02608
; WIPE_START
G1 X148.086 Y130.333 E-.32207
G1 X148.176 Y130.654 E-.12658
G1 X148.205 Y130.986 E-.12684
G1 X148.515 Y131.296 E-.16652
G1 X148.515 Y131.343 E-.01799
; WIPE_END
G1 E-.04 F1800
G1 X144.445 Y131.836 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.410382
G1 F9796.949
G1 X144.195 Y131.71 E.00837
; LINE_WIDTH: 0.450727
G1 F8827.712
G1 X144.168 Y131.695 E.00104
G1 X144.065 Y131.23 E.01581
; LINE_WIDTH: 0.449138
G1 F8862.248
G1 X144.08 Y131.21 E.00085
; LINE_WIDTH: 0.413713
G1 F9708.939
G1 X144.095 Y131.189 E.00077
; LINE_WIDTH: 0.382445
G1 F10603.061
G1 X144.254 Y130.982 E.00723
; WIPE_START
G1 X144.095 Y131.189 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.145 Y135.842 Z1 F30000
G1 X151.208 Y136.66 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X149.905 Y135.357 E.05672
G1 X150.411 Y135.435 E.01575
G1 X150.518 Y135.435 E.00329
G1 X151.742 Y136.66 E.05328
; WIPE_START
G1 X150.518 Y135.435 E-.65792
G1 X150.411 Y135.435 E-.04065
G1 X150.251 Y135.41 E-.06144
; WIPE_END
G1 E-.04 F1800
G1 X153.928 Y142.099 Z1 F30000
G1 X155.824 Y145.549 Z1
G1 Z.6
G1 E.8 F1800
G1 F9532.131
G1 X144.103 Y133.828 E.51013
G1 X144.103 Y134.362 E.01643
G1 X155.312 Y145.571 E.48785
G1 X154.931 Y145.723 E.01265
G1 X144.103 Y134.896 E.47126
M73 P44 R5
G1 X144.102 Y135.429 E.01643
G1 X154.549 Y145.876 E.45466
G1 X154.167 Y146.028 E.01265
G1 X144.102 Y135.963 E.43806
G1 X144.102 Y136.497 E.01643
G1 X153.786 Y146.181 E.42146
G1 X153.404 Y146.333 E.01265
G1 X144.102 Y137.031 E.40486
G1 X144.101 Y137.565 E.01643
G1 X153.022 Y146.486 E.38827
G1 X152.641 Y146.638 E.01265
G1 X144.101 Y138.099 E.37167
G1 X144.101 Y138.632 E.01643
G1 X152.259 Y146.791 E.35507
G1 X151.877 Y146.943 E.01265
G1 X144.101 Y139.166 E.33847
G1 X144.1 Y139.7 E.01643
G1 X151.497 Y147.097 E.32194
G1 X151.146 Y147.28 E.01219
G1 X144.1 Y140.234 E.30667
G1 X144.1 Y140.768 E.01643
G1 X150.839 Y147.507 E.29331
G2 X150.579 Y147.781 I1.073 J1.279 E.01165
G1 X144.099 Y141.302 E.282
G1 X144.099 Y141.835 E.01643
G1 X150.359 Y148.095 E.27245
G2 X150.183 Y148.454 I.955 J.691 E.01234
G1 X148.099 Y146.369 E.09072
G3 X148.206 Y147 I-1.783 J.627 E.01978
G1 X150.059 Y148.863 E.08086
G2 X150.011 Y149.35 I4.876 J.723 E.01505
G1 X148.141 Y147.48 E.08138
G3 X148.001 Y147.874 I-1.186 J-.201 E.01293
G1 X150.015 Y149.888 E.08768
G2 X150.054 Y150.461 I1.758 J.17 E.01774
G1 X147.801 Y148.208 E.09805
G3 X147.55 Y148.491 I-1.23 J-.838 E.01168
G1 X152.387 Y153.328 E.21051
G1 X152.665 Y153.072 E.01163
G1 X152.033 Y152.439 E.02754
G1 X152.164 Y152.466 E.00413
G1 X152.603 Y152.476 E.01351
G1 X153.082 Y152.955 E.02086
G1 X153.192 Y152.499 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.474743
G1 F8336.759
G1 X153.605 Y152.272 E.01659
; LINE_WIDTH: 0.431333
G1 F9268.496
G3 X165.272 Y152.263 I5.84 J8.741 E.39147
; LINE_WIDTH: 0.473811
G1 F8354.783
G1 X165.701 Y152.499 E.01718
; WIPE_START
G1 X165.272 Y152.263 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.419 Y157.507 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.479327
G1 F8249.184
G1 X169.448 Y157.702 E.00704
; LINE_WIDTH: 0.434771
G1 F9187.164
G1 X169.477 Y157.898 E.00633
; LINE_WIDTH: 0.390216
G1 F10365.816
G1 X169.506 Y158.094 E.00561
; LINE_WIDTH: 0.344261
G1 F11946.596
G1 X169.537 Y158.303 E.00517
; LINE_WIDTH: 0.299198
G1 F14047.265
G1 X169.555 Y158.483 E.00378
; LINE_WIDTH: 0.257529
G1 F15000
G1 X169.574 Y158.663 E.00317
; LINE_WIDTH: 0.215861
G1 X169.592 Y158.843 E.00255
; LINE_WIDTH: 0.174192
G1 X169.611 Y159.023 E.00194
; LINE_WIDTH: 0.13218
G1 X169.63 Y159.206 E.00134
; LINE_WIDTH: 0.104029
G1 X169.637 Y159.332 E.00063
G1 X169.71 Y157.298 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X168.799 Y156.388 E.03964
G2 X168.056 Y155.11 I-7.669 J3.607 E.04554
G1 X169.567 Y156.621 E.06574
G1 X169.573 Y156.093 E.01624
G1 X166.045 Y152.565 E.15357
G1 X166.108 Y152.45 E.00403
G2 X166.488 Y152.474 I.258 J-1.087 E.01176
G1 X169.58 Y155.566 E.13458
G1 X169.586 Y155.038 E.01624
G1 X166.966 Y152.418 E.11406
G2 X167.376 Y152.294 I-.348 J-1.9 E.01322
G1 X169.593 Y154.511 E.09647
G1 X169.6 Y153.983 E.01624
G1 X167.731 Y152.114 E.08135
G2 X168.034 Y151.883 I-.744 J-1.288 E.01176
G1 X169.606 Y153.456 E.06845
G1 X169.613 Y152.928 E.01623
G1 X168.3 Y151.615 E.05716
G2 X168.527 Y151.308 I-1.074 J-1.035 E.01178
G1 X169.62 Y152.401 E.04755
G1 X169.626 Y151.873 E.01623
G1 X168.703 Y150.95 E.0402
G2 X168.825 Y150.538 I-1.6 J-.701 E.01325
G1 X169.633 Y151.346 E.03515
G1 X169.639 Y150.818 E.01623
G1 X168.874 Y150.053 E.03329
G1 X168.875 Y149.52 E.01642
G1 X169.646 Y150.291 E.03355
G1 X169.653 Y149.763 E.01623
G1 X168.876 Y148.986 E.03382
G1 X168.876 Y148.453 E.01642
G1 X169.659 Y149.236 E.03408
G1 X169.666 Y148.708 E.01623
G1 X168.877 Y147.919 E.03434
G1 X168.877 Y147.386 E.01642
G1 X169.672 Y148.181 E.0346
G1 X169.679 Y147.653 E.01623
G1 X168.878 Y146.852 E.03487
G1 X168.879 Y146.319 E.01642
G1 X169.686 Y147.126 E.03513
G1 X169.692 Y146.598 E.01624
G1 X168.879 Y145.785 E.03539
G1 X168.88 Y145.252 E.01642
G1 X169.699 Y146.071 E.03565
G1 X169.706 Y145.543 E.01623
G1 X168.88 Y144.718 E.03592
G1 X168.881 Y144.185 E.01642
G1 X169.712 Y145.016 E.03618
G1 X169.719 Y144.488 E.01624
G1 X168.875 Y143.645 E.03672
G2 X168.76 Y142.996 I-1.969 J.014 E.02038
G1 X169.725 Y143.961 E.04201
G1 X169.732 Y143.433 E.01623
G1 X161.714 Y135.416 E.34895
G2 X162.109 Y135.32 I-.165 J-1.543 E.01252
G1 X162.139 Y135.306 E.00103
G1 X165.416 Y138.584 E.14265
G1 X165.409 Y138.5 E.00258
G1 X165.456 Y138.089 E.01272
G1 X162.493 Y135.127 E.12895
G2 X162.791 Y134.89 I-.75 J-1.253 E.01173
G1 X165.585 Y137.684 E.12159
G1 X165.773 Y137.338 E.01212
G1 X163.033 Y134.598 E.11925
G2 X163.225 Y134.256 I-1.183 J-.887 E.01211
G1 X166.018 Y137.049 E.12158
G1 X166.314 Y136.811 E.01169
G1 X163.341 Y133.838 E.12939
G2 X163.381 Y133.344 I-1.813 J-.398 E.01528
G1 X166.663 Y136.626 E.14282
G3 X167.079 Y136.508 I.498 J.964 E.0134
G1 X163.381 Y132.81 E.16093
G1 X163.381 Y132.276 E.01644
G1 X167.766 Y136.661 E.19085
; WIPE_START
G1 X166.352 Y135.247 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X159.607 Y138.819 Z1 F30000
G1 X147.147 Y145.417 Z1
G1 Z.6
G1 E.8 F1800
G1 F9532.131
G1 X144.099 Y142.369 E.13266
G1 X144.099 Y142.903 E.01643
G1 X146.167 Y144.971 E.09002
G1 X146.081 Y144.966 E.00266
G1 X145.686 Y145.025 E.01227
G1 X144.098 Y143.437 E.06911
G1 X144.098 Y143.971 E.01643
G1 X145.291 Y145.164 E.05192
G1 X144.959 Y145.366 E.01196
G1 X144.098 Y144.505 E.0375
G1 X144.097 Y145.038 E.01643
G1 X144.679 Y145.619 E.02529
G1 X144.593 Y145.721 E.00408
G1 X144.498 Y145.533 E.00648
G1 X144.238 Y145.665 E.00896
G1 X144.226 Y145.641 E.00083
G1 X144.187 Y145.662 E.00136
G1 X143.928 Y145.403 E.01128
G1 X144.445 Y146.164 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.410538
G1 F9792.793
G1 X144.195 Y146.291 E.00838
; LINE_WIDTH: 0.450721
G1 F8827.848
G1 X144.168 Y146.305 E.00103
G1 X144.065 Y146.77 E.01581
; LINE_WIDTH: 0.4491
G1 F8863.066
G1 X144.08 Y146.79 E.00085
; LINE_WIDTH: 0.41363
G1 F9711.104
G1 X144.095 Y146.811 E.00077
; LINE_WIDTH: 0.382337
G1 F10606.443
G1 X144.254 Y147.018 E.00722
G1 X144.682 Y148.208 F30000
; LINE_WIDTH: 0.401232
G1 F10047.12
G1 X144.697 Y148.491 E.00827
G1 X144.765 Y148.536 E.00238
; LINE_WIDTH: 0.384394
G1 F10542.543
G1 X144.833 Y148.582 E.00227
; LINE_WIDTH: 0.351175
G1 F11678.645
G1 X144.988 Y148.676 E.00457
; LINE_WIDTH: 0.323649
G1 F12823.752
G1 X145.46 Y148.93 E.01226
; LINE_WIDTH: 0.366234
G1 F11134.708
G1 X145.638 Y149.011 E.00516
; LINE_WIDTH: 0.417149
G1 F9619.787
G1 X145.778 Y149.068 E.00462
G1 X145.799 Y149.056 E.00072
; LINE_WIDTH: 0.393983
G1 F10254.594
G1 X146.025 Y148.91 E.00769
G1 X147.059 Y150.137 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X146.304 Y149.381 E.03286
G1 X146.366 Y149.344 E.00222
G1 X146.356 Y149.328 E.00057
G1 X146.592 Y149.177 E.00862
G1 X146.517 Y149.06 E.00426
G1 X151.594 Y154.137 E.22095
G1 X151.849 Y153.858 E.01163
G1 X146.889 Y148.898 E.21589
G2 X147.246 Y148.721 I-.321 J-1.102 E.01234
G1 X152.228 Y153.703 E.21681
G1 X151.47 Y154.547 F30000
G1 F9532.131
G1 X149.962 Y153.039 E.06562
G3 X150.234 Y153.845 I-4.52 J1.974 E.02621
G1 X151.117 Y154.728 E.03842
G2 X150.886 Y155.032 I1.621 J1.471 E.01175
G1 X150.158 Y154.304 E.03168
G1 X150.516 Y155.412 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.310266
G1 F13465.739
G1 X150.224 Y156.382 E.02206
G1 X150.218 Y156.38 F30000
; LINE_WIDTH: 0.121127
G1 F15000
G1 X150.265 Y156.233 E.00099
; LINE_WIDTH: 0.169533
G1 X150.313 Y156.085 E.0016
; LINE_WIDTH: 0.217939
G1 X150.361 Y155.938 E.00221
; LINE_WIDTH: 0.243794
G1 X150.518 Y155.413 E.00897
; WIPE_START
G1 X150.361 Y155.938 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.307 Y150.218 Z1 F30000
G1 X143.386 Y148.044 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.55283
G1 F7060.07
G3 X144.02 Y148.188 I-.443 J3.409 E.02707
G1 X144.028 Y147.937 E.01043
G1 X144.173 Y147.799 E.00831
G1 X144.129 Y147.655 E.00627
G1 X144.074 Y147.675 E.00243
G1 X143.874 Y147.589 E.00904
G1 X143.756 Y147.457 E.00737
G3 X143.345 Y147.908 I-1.163 J-.647 E.02559
G1 X143.396 Y147.986 E.00387
G1 X142.854 Y148.007 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.109651
G1 F15000
G1 X142.763 Y148.071 E.0006
; LINE_WIDTH: 0.138436
G1 X142.655 Y148.148 E.00103
G1 X142.698 Y148.208 E.00057
; WIPE_START
G1 X142.655 Y148.148 E-.2701
G1 X142.763 Y148.071 E-.4899
; WIPE_END
G1 E-.04 F1800
G1 X137.907 Y142.182 Z1 F30000
G1 X127.017 Y128.977 Z1
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.483234
G1 F8175.998
G1 X126.807 Y128.947 E.00762
; LINE_WIDTH: 0.438304
G1 F9105.075
G1 X126.596 Y128.918 E.00684
; LINE_WIDTH: 0.39182
G1 F10318.158
G1 X126.372 Y128.887 E.00645
; LINE_WIDTH: 0.344474
G1 F11938.175
G1 X126.191 Y128.87 E.00445
; LINE_WIDTH: 0.299914
G1 F14008.152
G1 X126.011 Y128.853 E.00379
; LINE_WIDTH: 0.255353
G1 F15000
G1 X125.83 Y128.835 E.00314
; LINE_WIDTH: 0.210793
G1 X125.65 Y128.818 E.00248
; LINE_WIDTH: 0.165693
G1 X125.465 Y128.801 E.00186
; LINE_WIDTH: 0.119988
G1 X125.149 Y128.784 E.00199
; OBJECT_ID: 861
; WIPE_START
G1 X125.465 Y128.801 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 795
M625
; start printing object, unique label id: 861
M624 CAAAAAAAAAA=
G1 X130.037 Y122.689 Z1 F30000
G1 X147.638 Y99.155 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X147.716 Y99.282 E.00494
G3 X146.095 Y98.304 I-1.539 J.719 E.28746
G3 X146.465 Y98.327 I.074 J1.818 E.01231
G3 X147.567 Y99.025 I-.288 J1.674 E.04442
G1 X147.609 Y99.103 E.00295
M204 S250
G1 X147.31 Y99.345 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.112 Y98.696 I-1.131 J.658 E.20869
G3 X146.283 Y98.698 I.072 J.976 E.00527
G3 X147.279 Y99.294 I-.105 J1.305 E.03693
; WIPE_START
M204 S10000
G1 X147.4 Y99.555 E-.10956
G1 X147.459 Y99.776 E-.08678
G1 X147.479 Y100.003 E-.08678
G1 X147.459 Y100.231 E-.08678
G1 X147.4 Y100.451 E-.08678
G1 X147.273 Y100.707 E-.10837
G1 X147.096 Y100.93 E-.10835
G1 X146.921 Y101.076 E-.0866
; WIPE_END
G1 E-.04 F1800
G1 X150.744 Y94.47 Z1 F30000
G1 X152.935 Y90.683 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X153.052 Y90.919 E.00873
G3 X151.372 Y89.804 I-1.598 J.584 E.28302
G3 X151.742 Y89.827 I.074 J1.82 E.01232
G3 X152.913 Y90.628 I-.288 J1.677 E.04855
M204 S250
G1 X152.587 Y90.844 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X151.389 Y90.196 I-1.132 J.659 E.20877
G3 X151.56 Y90.198 I.071 J.975 E.00527
G3 X152.556 Y90.793 I-.105 J1.305 E.03692
; WIPE_START
M204 S10000
G1 X152.677 Y91.055 E-.10966
G1 X152.751 Y91.389 E-.12998
G1 X152.751 Y91.617 E-.08676
G1 X152.677 Y91.951 E-.12999
G1 X152.581 Y92.158 E-.08677
G1 X152.45 Y92.346 E-.08683
G1 X152.288 Y92.507 E-.08674
G1 X152.195 Y92.572 E-.04328
; WIPE_END
G1 E-.04 F1800
M73 P45 R5
G1 X159.104 Y89.329 Z1 F30000
G1 X161.811 Y88.058 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X161.459 Y88.105 E.01178
G1 X150.433 Y88.105 E.36577
G3 X148.844 Y86.517 I.027 J-1.616 E.08241
G1 X148.844 Y83.49 E.1004
G3 X150.433 Y81.901 I1.616 J.027 E.08241
G1 X161.459 Y81.901 E.36578
G3 X163.048 Y83.49 I-.027 J1.616 E.08241
G1 X163.048 Y86.517 E.1004
G3 X161.87 Y88.045 I-1.616 J-.027 E.06861
M204 S250
G1 X161.759 Y87.67 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X161.451 Y87.713 I-.324 J-1.177 E.00958
G1 X150.441 Y87.713 E.33829
G3 X149.236 Y86.508 I.007 J-1.212 E.05808
G1 X149.236 Y83.499 E.09247
G3 X150.441 Y82.293 I1.221 J.016 E.05798
G1 X161.451 Y82.293 E.33829
G3 X162.656 Y83.499 I-.016 J1.221 E.05798
G1 X162.656 Y86.508 E.09247
G3 X161.816 Y87.652 I-1.221 J-.016 E.04655
; WIPE_START
M204 S10000
G1 X161.451 Y87.713 E-.14077
G1 X159.821 Y87.713 E-.61923
; WIPE_END
G1 E-.04 F1800
G1 X152.433 Y85.799 Z1 F30000
G1 X144.489 Y83.742 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X144.498 Y83.709 E.00114
G3 X146.095 Y82.304 I1.674 J.293 E.07622
G3 X147.604 Y84.917 I.066 J1.704 E.12288
G3 X144.472 Y84.003 I-1.432 J-.916 E.14498
G1 X144.485 Y83.802 E.0067
M204 S250
G1 X144.889 Y83.778 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.112 Y82.696 I1.29 J.226 E.05418
G3 X146.283 Y82.698 I.071 J.975 E.00527
G3 X144.88 Y83.837 I-.105 J1.305 E.1915
; WIPE_START
M204 S10000
G1 X144.982 Y83.45 E-.1522
G1 X145.096 Y83.252 E-.08675
G1 X145.243 Y83.077 E-.08682
G1 X145.417 Y82.93 E-.08675
G1 X145.615 Y82.816 E-.08684
G1 X145.83 Y82.738 E-.08675
G1 X146.112 Y82.696 E-.10836
G1 X146.283 Y82.698 E-.0651
G1 X146.284 Y82.698 E-.00043
; WIPE_END
G1 E-.04 F1800
G1 X142.901 Y83.303 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X143.154 Y83.518 E.01102
G3 X143.771 Y84.99 I-1.489 J1.489 E.0543
G1 X143.771 Y99.017 E.46529
G3 X141.682 Y101.105 I-2.121 J-.032 E.1084
G1 X134.611 Y101.105 E.23458
G3 X132.762 Y98.026 I.026 J-2.11 E.14249
G1 X133.298 Y97.107 E.0353
G2 X133.996 Y88.524 I-9.629 J-5.103 E.29364
G2 X132.762 Y85.98 I-11.994 J4.249 E.09399
G3 X134.611 Y82.901 I1.875 J-.969 E.14249
G1 X141.682 Y82.901 E.23459
G3 X142.853 Y83.268 I-.017 J2.106 E.04128
M204 S250
G1 X142.649 Y83.604 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X143.379 Y84.999 I-.984 J1.403 E.05026
G1 X143.379 Y99.008 E.43047
G3 X141.674 Y100.713 I-1.725 J-.02 E.08205
G1 X134.619 Y100.713 E.21677
G3 X133.109 Y98.209 I.016 J-1.717 E.10753
G1 X133.644 Y97.29 E.03266
G2 X134.368 Y88.399 I-9.975 J-5.287 E.28179
G2 X133.109 Y85.798 I-12.327 J4.361 E.08898
G3 X134.619 Y83.293 I1.525 J-.788 E.10753
G1 X141.674 Y83.293 E.21678
G3 X142.599 Y83.57 I-.008 J1.714 E.0301
; WIPE_START
M204 S10000
G1 X142.878 Y83.794 E-.13592
G1 X143.07 Y84.022 E-.11327
G1 X143.219 Y84.281 E-.11328
G1 X143.321 Y84.561 E-.11328
G1 X143.353 Y84.706 E-.0567
G1 X143.379 Y84.999 E-.11151
G1 X143.379 Y85.304 E-.11604
; WIPE_END
G1 E-.04 F1800
G1 X135.774 Y85.948 Z1 F30000
G1 X114.506 Y87.75 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X114.514 Y87.734 E.00057
G3 X122.789 Y81.939 I9.155 J4.267 E.35092
G1 X123.229 Y81.92 E.01461
G1 X123.669 Y81.901 E.01462
G3 X114.177 Y88.549 I0 J10.1 E1.69574
G1 X114.484 Y87.805 E.02667
M204 S250
G1 X114.87 Y87.9 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X122.823 Y82.33 I8.799 J4.1 E.31243
G1 X123.246 Y82.312 E.01301
G1 X123.669 Y82.293 E.01301
G3 X114.845 Y87.955 I0 J9.707 E1.53377
; WIPE_START
M204 S10000
G1 X115.26 Y87.148 E-.34461
G1 X115.715 Y86.434 E-.32196
G1 X115.865 Y86.239 E-.09343
; WIPE_END
G1 E-.04 F1800
G1 X122.915 Y89.162 Z1 F30000
G1 X167.196 Y107.523 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X167.721 Y108.209 E.02866
G3 X158.566 Y103.939 I-8.275 J5.792 E1.75422
G1 X159.006 Y103.92 E.01461
G1 X159.446 Y103.901 E.01462
G3 X167.157 Y107.477 I0 J10.1 E.29102
M204 S250
G1 X166.884 Y107.762 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X158.6 Y104.33 I-7.438 J6.238 E1.58767
G1 X159.023 Y104.312 E.01301
G1 X159.446 Y104.293 E.01301
G3 X166.845 Y107.717 I0 J9.707 E.25852
; WIPE_START
M204 S10000
G1 X167.4 Y108.434 E-.34461
G1 X167.855 Y109.148 E-.32196
G1 X167.969 Y109.366 E-.09343
; WIPE_END
G1 E-.04 F1800
G1 X166.722 Y105.131 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.689 Y105.131 E.00112
G3 X165.469 Y104.911 I-.251 J-2.096 E.04174
G1 X164.549 Y104.375 E.0353
G2 X155.967 Y103.676 I-5.103 J9.629 E.29363
G2 X153.423 Y104.911 I4.248 J11.992 E.094
G3 X150.374 Y103.407 I-.975 J-1.866 E.13125
G3 X150.344 Y102.329 I6.159 J-.712 E.03582
G3 X151.655 Y100.394 I2.109 J.017 E.08215
G1 X165.678 Y94.792 E.50094
G3 X166.183 Y94.663 I.828 J2.185 E.01731
G3 X168.548 Y96.736 I.261 J2.088 E.11784
G1 X168.548 Y103.062 E.20983
G3 X167.04 Y105.059 I-2.11 J-.026 E.08887
G1 X166.781 Y105.117 E.0088
M204 S250
G1 X166.644 Y104.743 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X165.652 Y104.563 I-.204 J-1.705 E.03144
G1 X164.733 Y104.028 E.03266
G2 X155.842 Y103.304 I-5.287 J9.976 E.28179
G2 X153.241 Y104.563 I4.361 J12.327 E.08898
G3 X150.761 Y103.34 I-.793 J-1.518 E.09888
G3 X150.736 Y102.337 I5.791 J-.645 E.03087
G3 X151.808 Y100.755 I1.717 J.009 E.06226
G1 X165.816 Y95.159 E.46351
G3 X166.232 Y95.052 I.682 J1.787 E.01323
G3 X168.156 Y96.744 I.212 J1.699 E.08897
G1 X168.156 Y103.053 E.19386
G3 X166.703 Y104.734 I-1.717 J-.015 E.07426
; WIPE_START
M204 S10000
G1 X166.498 Y104.758 E-.07833
G1 X166.352 Y104.756 E-.05564
G1 X166.062 Y104.715 E-.11105
G1 X165.784 Y104.626 E-.11109
G1 X165.652 Y104.563 E-.05573
G1 X164.86 Y104.102 E-.34817
; WIPE_END
G1 E-.04 F1800
G1 X167.064 Y96.794 Z1 F30000
G1 X168.915 Y90.655 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X168.995 Y90.781 E.00494
G3 X167.372 Y89.804 I-1.541 J.723 E.2881
G3 X167.742 Y89.827 I.074 J1.82 E.01232
G3 X168.845 Y90.524 I-.288 J1.677 E.04443
G1 X168.887 Y90.602 E.00294
M204 S250
G1 X168.587 Y90.844 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X167.389 Y90.196 I-1.132 J.659 E.20885
G3 X167.56 Y90.198 I.071 J.975 E.00527
G3 X168.556 Y90.793 I-.105 J1.306 E.03693
; WIPE_START
M204 S10000
G1 X168.677 Y91.055 E-.10968
G1 X168.751 Y91.389 E-.12998
G1 X168.751 Y91.617 E-.08676
G1 X168.712 Y91.842 E-.0868
G1 X168.634 Y92.057 E-.08679
G1 X168.45 Y92.346 E-.12999
G1 X168.288 Y92.507 E-.08674
G1 X168.195 Y92.572 E-.04326
; WIPE_END
G1 E-.04 F1800
G1 X160.742 Y94.217 Z1 F30000
G1 X128.082 Y101.422 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X127.169 Y101.794 E.03272
G3 X123.387 Y81.609 I-3.491 J-9.793 E1.19188
G1 X158.73 Y80.606 E1.17285
G1 X159.707 Y80.648 E.03245
M73 P46 R5
G3 X170.125 Y91.634 I-1.003 J11.384 E.54897
G1 X169.843 Y114.121 E.74599
G3 X149.447 Y111.155 I-10.396 J-.124 E1.17487
G1 X149.877 Y109.855 E.04541
G2 X147.433 Y103.561 I-5.389 J-1.528 E.24039
G1 X145.26 Y102.225 E.08462
G2 X142.347 Y101.401 I-2.921 J4.766 E.10168
G1 X128.138 Y101.401 E.47134
M204 S250
G1 X128.211 Y101.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X118.058 Y82.787 I-4.533 J-9.793 E1.00388
G1 X118.875 Y82.337 E.02864
G3 X123.367 Y81.218 I4.905 J10.107 E.1433
G1 X158.732 Y80.213 E1.08711
G1 X159.74 Y80.257 E.031
G3 X170.518 Y91.622 I-1.038 J11.776 E.52604
G1 X170.235 Y114.134 E.6918
G3 X149.069 Y111.047 I-10.789 J-.133 E1.1294
G1 X149.5 Y109.748 E.04205
G2 X147.22 Y103.891 I-5.013 J-1.421 E.20731
G1 X145.061 Y102.563 E.07789
G2 X142.339 Y101.793 I-2.724 J4.436 E.088
G1 X128.271 Y101.793 E.4323
M204 S10000
G1 X128.393 Y101.188 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.331146
G1 F12490.228
G1 X129.207 Y100.97 E.01979
G1 X131.546 Y100.114 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.58492
G1 F6642.067
G2 X131.55 Y100.225 I-.029 J.056 E.01173
G1 X132.28 Y100.632 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X132.028 Y100.23 E.01459
G1 X131.857 Y99.77 E.01508
G1 X131.766 Y99.246 E.01635
G1 X131.374 Y99.673 E.01782
G1 X130.676 Y100.315 E.02914
G1 X130.249 Y100.632 E.01632
G1 X132.22 Y100.632 E.06055
G1 X132.898 Y100.789 F30000
G1 F9547.299
G1 X132.725 Y100.62 E.00742
G1 X132.398 Y100.128 E.01815
G3 X132.155 Y98.697 I2.354 J-1.135 E.0452
G1 X131.87 Y98.54 E.01002
G3 X130.421 Y100.037 I-8.807 J-7.067 E.06411
G3 X129.537 Y100.687 I-262.108 J-356.104 E.03372
G1 X129.623 Y101.009 E.01025
G1 X132.827 Y101.009 E.09844
G1 X132.826 Y100.876 E.00408
G1 X132.86 Y100.835 E.00163
G1 X133.297 Y100.92 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.121009
G1 F15000
G1 X133.464 Y101.056 E.00137
; LINE_WIDTH: 0.165445
G1 X133.654 Y101.198 E.00237
G1 X133.791 Y101.176 F30000
; LINE_WIDTH: 0.133873
G1 F15000
G3 X133.437 Y101.102 I1.455 J-7.846 E.00268
; WIPE_START
G1 X133.791 Y101.176 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.17 Y98.258 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.474748
G1 F8336.657
G1 X132.397 Y97.845 E.01659
; LINE_WIDTH: 0.431339
G1 F9268.36
G3 X132.754 Y97.258 I13.594 J7.875 E.02173
G2 X132.406 Y86.177 I-9.076 J-5.261 E.36971
; LINE_WIDTH: 0.473821
G1 F8354.599
G1 X132.17 Y85.749 E.01718
G1 X128.452 Y82.93 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X127.372 Y81.85 E.04702
G1 X127.374 Y81.829 E.00064
G1 X127.871 Y81.815 E.01529
G1 X129.257 Y83.201 E.06031
G3 X131.664 Y85.295 I-5.376 J8.609 E.0986
G1 X131.854 Y85.543 E.00961
G1 X132.034 Y85.444 E.00632
G1 X128.39 Y81.8 E.15856
G1 X128.91 Y81.786 E.01599
G1 X132.192 Y85.068 E.14284
G3 X132.233 Y84.575 I2.574 J-.033 E.01525
G1 X129.429 Y81.771 E.12203
G1 X129.948 Y81.756 E.01599
G1 X132.348 Y84.156 E.10443
G3 X132.518 Y83.792 I1.138 J.312 E.01242
G1 X130.468 Y81.741 E.08925
G1 X130.987 Y81.727 E.01599
G1 X132.735 Y83.475 E.07608
G3 X132.994 Y83.199 I.926 J.611 E.01169
G1 X131.507 Y81.712 E.06473
G1 X132.026 Y81.697 E.01599
G1 X133.294 Y82.965 E.0552
G1 X133.639 Y82.776 E.01211
G1 X132.545 Y81.682 E.04761
G1 X133.065 Y81.668 E.01599
G1 X134.037 Y82.64 E.04232
G3 X134.507 Y82.576 I.487 J1.81 E.01463
G1 X133.584 Y81.653 E.04017
G1 X134.103 Y81.638 E.01599
G1 X135.033 Y82.568 E.04047
G1 X135.567 Y82.568 E.01644
G1 X134.623 Y81.623 E.04111
G1 X135.142 Y81.609 E.01599
G1 X136.101 Y82.568 E.04175
G1 X136.636 Y82.568 E.01644
G1 X135.661 Y81.594 E.0424
G1 X136.181 Y81.579 E.01599
G1 X137.17 Y82.568 E.04304
G1 X137.704 Y82.568 E.01644
G1 X136.7 Y81.564 E.04368
G1 X137.22 Y81.55 E.01599
G1 X138.238 Y82.568 E.04432
G1 X138.772 Y82.568 E.01644
G1 X137.739 Y81.535 E.04496
G1 X138.258 Y81.52 E.01599
G1 X139.306 Y82.568 E.0456
G1 X139.84 Y82.568 E.01644
G1 X138.778 Y81.506 E.04625
G1 X139.297 Y81.491 E.01599
G1 X140.374 Y82.568 E.04689
G1 X140.908 Y82.568 E.01644
G1 X139.816 Y81.476 E.04753
G1 X140.336 Y81.461 E.01599
G1 X141.443 Y82.568 E.04817
G3 X142.004 Y82.595 I.127 J3.162 E.01732
G1 X140.855 Y81.447 E.05
G1 X141.374 Y81.432 E.01599
G1 X142.789 Y82.847 E.06158
G3 X143.742 Y83.731 I-1.19 J2.237 E.04044
G1 X143.827 Y83.615 E.00443
G1 X143.841 Y83.625 E.00054
G1 X143.856 Y83.604 E.00079
G1 X143.875 Y83.618 E.0007
G1 X143.97 Y83.493 E.00482
G1 X141.894 Y81.417 E.09037
G1 X142.413 Y81.402 E.01599
G1 X144.278 Y83.267 E.08115
G3 X144.456 Y82.911 I1.097 J.329 E.01231
G1 X142.933 Y81.388 E.06632
G1 X143.452 Y81.373 E.01599
G1 X144.689 Y82.61 E.05385
G3 X144.972 Y82.359 I.854 J.677 E.0117
G1 X143.971 Y81.358 E.04355
G1 X144.491 Y81.343 E.01599
G1 X145.306 Y82.158 E.03548
G1 X145.706 Y82.025 E.013
G1 X145.01 Y81.329 E.03032
G1 X145.529 Y81.314 E.01599
G1 X146.192 Y81.976 E.02882
G3 X146.829 Y82.079 I.065 J1.617 E.02
G1 X146.049 Y81.299 E.03395
G1 X146.568 Y81.284 E.01599
G1 X148.532 Y83.248 E.08546
G3 X148.64 Y82.823 I1.26 J.095 E.01358
G1 X147.087 Y81.27 E.06759
G1 X147.607 Y81.255 E.01599
G1 X148.817 Y82.465 E.05268
G3 X149.051 Y82.164 I.97 J.511 E.01178
G1 X148.126 Y81.24 E.04023
G1 X148.645 Y81.225 E.01599
G1 X149.336 Y81.916 E.03006
G1 X149.682 Y81.728 E.01212
G1 X149.165 Y81.211 E.02251
G1 X149.684 Y81.196 E.01599
G1 X150.098 Y81.61 E.01803
G3 X150.591 Y81.568 I.402 J1.807 E.01525
G1 X150.204 Y81.181 E.01684
G1 X150.723 Y81.166 E.01599
G1 X151.125 Y81.568 E.01748
G1 X151.659 Y81.568 E.01644
G1 X151.242 Y81.152 E.01813
G1 X151.762 Y81.137 E.01599
G1 X152.193 Y81.568 E.01877
G1 X152.727 Y81.568 E.01644
G1 X152.281 Y81.122 E.01941
G1 X152.8 Y81.107 E.01599
G1 X153.261 Y81.568 E.02005
G1 X153.795 Y81.568 E.01644
G1 X153.32 Y81.093 E.02069
G1 X153.839 Y81.078 E.01599
G1 X154.329 Y81.568 E.02133
G1 X154.863 Y81.568 E.01644
G1 X154.358 Y81.063 E.02198
G1 X154.878 Y81.048 E.01599
G1 X155.397 Y81.568 E.02262
G1 X155.932 Y81.568 E.01644
G1 X155.397 Y81.034 E.02326
G1 X155.917 Y81.019 E.01599
G1 X156.466 Y81.568 E.0239
G1 X157 Y81.568 E.01644
G1 X156.436 Y81.004 E.02454
G1 X156.955 Y80.989 E.01599
G1 X157.534 Y81.568 E.02518
G1 X158.068 Y81.568 E.01644
G1 X157.475 Y80.975 E.02583
G1 X157.994 Y80.96 E.01599
G1 X158.602 Y81.568 E.02647
G1 X159.136 Y81.568 E.01644
G1 X158.513 Y80.945 E.02711
G3 X159.055 Y80.953 I.215 J3.81 E.0167
G1 X159.67 Y81.568 E.02676
G1 X160.204 Y81.568 E.01644
G1 X159.613 Y80.977 E.02573
G3 X160.22 Y81.05 I-.121 J3.58 E.01883
G1 X160.908 Y81.738 E.02995
G1 X161.319 Y81.121 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.551427
G1 F7079.55
G1 X161.528 Y81.437 E.01571
G1 X161.615 Y81.452 E.00365
; LINE_WIDTH: 0.515349
G1 F7620.192
G3 X162.456 Y81.714 I-.753 J3.908 E.03399
G1 X162.459 Y81.728 E.00056
; LINE_WIDTH: 0.497546
G1 F7918.606
G1 X162.53 Y82.043 E.01198
G1 X167.912 Y85.537 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X166.427 Y84.052 E.06463
G2 X164.271 Y82.43 I-8.35 J8.855 E.08321
G1 X168.3 Y86.459 E.17537
G3 X168.847 Y87.54 I-6.025 J3.724 E.0373
G1 X163.188 Y81.881 E.24628
G1 X163.097 Y81.844 E.00304
G1 X163.171 Y82.241 E.01243
G1 X163.043 Y82.27 E.00405
G1 X169.19 Y88.417 E.26755
G3 X169.423 Y89.185 I-4.363 J1.745 E.02471
G1 X163.338 Y83.099 E.26485
G3 X163.381 Y83.677 I-3.032 J.519 E.01786
G1 X169.589 Y89.884 E.27016
G1 X169.692 Y90.521 E.01987
G1 X163.381 Y84.211 E.27465
G1 X163.381 Y84.745 E.01644
G1 X169.752 Y91.116 E.27728
G3 X169.791 Y91.689 I-3.239 J.509 E.01771
G1 X169.469 Y91.366 E.01406
G3 X169.442 Y91.873 I-1.454 J.177 E.01571
G1 X169.785 Y92.217 E.01494
G1 X169.778 Y92.744 E.01623
G1 X169.321 Y92.287 E.01992
G3 X169.136 Y92.636 I-1.083 J-.35 E.01222
G1 X169.772 Y93.272 E.02768
G1 X169.765 Y93.799 E.01624
G1 X168.897 Y92.931 E.03778
G1 X168.608 Y93.176 E.01166
G1 X169.758 Y94.327 E.05008
G1 X169.752 Y94.854 E.01623
G1 X168.263 Y93.366 E.06479
G3 X167.859 Y93.495 I-.695 J-1.47 E.0131
G1 X169.745 Y95.382 E.0821
G1 X169.739 Y95.909 E.01624
G1 X167.176 Y93.346 E.11154
G1 X167.524 Y94.763 F30000
G1 F9532.131
G1 X161.194 Y88.433 E.27548
G1 X160.661 Y88.433 E.01643
G1 X166.542 Y94.314 E.25596
G2 X166.042 Y94.349 I-.117 J1.972 E.01547
M73 P47 R5
G1 X160.127 Y88.434 E.25743
G1 X159.593 Y88.434 E.01643
G1 X165.62 Y94.461 E.26233
G2 X165.235 Y94.61 I.667 J2.3 E.01273
G1 X159.059 Y88.434 E.26879
G1 X158.525 Y88.435 E.01643
G1 X164.853 Y94.763 E.27542
G1 X164.472 Y94.915 E.01265
G1 X157.991 Y88.435 E.28204
G1 X157.457 Y88.435 E.01643
G1 X164.09 Y95.068 E.28866
G1 X163.708 Y95.22 E.01265
G1 X156.924 Y88.435 E.29529
G1 X156.39 Y88.436 E.01643
G1 X163.327 Y95.372 E.30191
G1 X162.945 Y95.525 E.01265
G1 X155.856 Y88.436 E.30854
G1 X155.322 Y88.436 E.01643
G1 X162.563 Y95.677 E.31516
G1 X162.182 Y95.83 E.01265
G1 X154.788 Y88.436 E.32178
G1 X154.254 Y88.437 E.01643
G1 X161.8 Y95.982 E.32841
G1 X161.418 Y96.135 E.01265
G1 X153.721 Y88.437 E.33503
G1 X153.187 Y88.437 E.01643
G1 X161.037 Y96.287 E.34166
G1 X160.655 Y96.44 E.01265
G1 X152.653 Y88.437 E.34828
G1 X152.119 Y88.438 E.01643
G1 X160.274 Y96.592 E.35491
G1 X159.892 Y96.745 E.01265
G1 X151.585 Y88.438 E.36153
G1 X151.051 Y88.438 E.01643
G1 X159.51 Y96.897 E.36815
G1 X159.129 Y97.05 E.01265
G1 X153.474 Y91.395 E.24612
G3 X153.442 Y91.897 I-2.541 J.09 E.01551
G1 X158.747 Y97.202 E.2309
G1 X158.365 Y97.354 E.01265
G1 X153.311 Y92.3 E.21997
G1 X153.124 Y92.647 E.01213
G1 X157.984 Y97.507 E.21152
G1 X157.602 Y97.659 E.01265
G1 X152.886 Y92.944 E.20524
G1 X152.593 Y93.184 E.01168
G1 X157.22 Y97.812 E.2014
G1 X156.839 Y97.964 E.01265
G1 X152.246 Y93.372 E.19988
G3 X151.84 Y93.5 I-.688 J-1.478 E.01314
G1 X156.457 Y98.117 E.20095
G1 X156.075 Y98.269 E.01265
G1 X151.15 Y93.344 E.21435
; WIPE_START
G1 X152.565 Y94.758 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.605 Y91.799 Z1 F30000
G1 Z.6
G1 E.8 F1800
G1 F9532.131
G1 X144.104 Y86.297 E.23945
G1 X144.104 Y85.764 E.01643
G1 X149.45 Y91.11 E.23267
G3 X149.578 Y90.703 I1.606 J.282 E.01314
G1 X144.23 Y85.355 E.23276
G1 X144.239 Y85.339 E.00058
G1 X144.498 Y85.47 E.00895
G1 X144.593 Y85.282 E.00649
G2 X145.19 Y85.781 I1.588 J-1.293 E.02407
G1 X149.765 Y90.356 E.19913
G1 X150.006 Y90.063 E.01168
G1 X145.965 Y86.023 E.17585
G2 X146.489 Y86.012 I.233 J-1.489 E.01621
G1 X150.299 Y89.822 E.16582
G1 X150.646 Y89.635 E.01213
G1 X146.906 Y85.895 E.16279
G2 X147.261 Y85.716 I-.329 J-1.098 E.0123
G1 X148.59 Y87.045 E.05782
G3 X148.511 Y86.432 I1.935 J-.56 E.01908
G1 X147.562 Y85.483 E.04129
G1 X147.808 Y85.195 E.01166
G1 X148.512 Y85.899 E.03063
G1 X148.513 Y85.366 E.01641
G1 X148.005 Y84.858 E.02209
G2 X148.146 Y84.465 I-.895 J-.543 E.01294
G1 X148.514 Y84.832 E.016
G1 X148.515 Y84.299 E.01641
G1 X148.205 Y83.989 E.01349
G2 X148.086 Y83.336 I-1.86 J.002 E.02055
G1 X148.685 Y83.936 E.02608
; WIPE_START
G1 X148.086 Y83.336 E-.32207
G1 X148.176 Y83.657 E-.12658
G1 X148.205 Y83.989 E-.12684
G1 X148.515 Y84.299 E-.16652
G1 X148.515 Y84.347 E-.01799
; WIPE_END
G1 E-.04 F1800
G1 X144.445 Y84.839 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.410382
G1 F9796.949
G1 X144.195 Y84.713 E.00837
; LINE_WIDTH: 0.450727
G1 F8827.712
G1 X144.168 Y84.698 E.00104
G1 X144.065 Y84.234 E.01581
; LINE_WIDTH: 0.449138
G1 F8862.248
G1 X144.08 Y84.213 E.00085
; LINE_WIDTH: 0.413713
G1 F9708.939
G1 X144.095 Y84.192 E.00077
; LINE_WIDTH: 0.382445
G1 F10603.061
G1 X144.254 Y83.985 E.00723
; WIPE_START
G1 X144.095 Y84.192 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.145 Y88.845 Z1 F30000
G1 X151.208 Y89.663 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X149.905 Y88.36 E.05672
G1 X150.411 Y88.439 E.01575
G1 X150.518 Y88.438 E.00329
G1 X151.742 Y89.663 E.05328
; WIPE_START
G1 X150.518 Y88.438 E-.65792
G1 X150.411 Y88.439 E-.04065
G1 X150.251 Y88.414 E-.06144
; WIPE_END
G1 E-.04 F1800
G1 X153.928 Y95.102 Z1 F30000
G1 X155.824 Y98.552 Z1
G1 Z.6
G1 E.8 F1800
G1 F9532.131
G1 X144.103 Y86.831 E.51013
G1 X144.103 Y87.365 E.01643
G1 X155.312 Y98.574 E.48785
G1 X154.931 Y98.727 E.01265
G1 X144.103 Y87.899 E.47126
G1 X144.102 Y88.433 E.01643
G1 X154.549 Y98.879 E.45466
G1 X154.167 Y99.032 E.01265
G1 X144.102 Y88.967 E.43806
G1 X144.102 Y89.5 E.01643
G1 X153.786 Y99.184 E.42146
G1 X153.404 Y99.336 E.01265
G1 X144.102 Y90.034 E.40486
G1 X144.101 Y90.568 E.01643
G1 X153.022 Y99.489 E.38827
G1 X152.641 Y99.641 E.01265
G1 X144.101 Y91.102 E.37167
G1 X144.101 Y91.636 E.01643
G1 X152.259 Y99.794 E.35507
G1 X151.877 Y99.946 E.01265
G1 X144.101 Y92.169 E.33847
G1 X144.1 Y92.703 E.01643
G1 X151.497 Y100.1 E.32194
G1 X151.146 Y100.283 E.01219
G1 X144.1 Y93.237 E.30667
G1 X144.1 Y93.771 E.01643
G1 X150.839 Y100.51 E.29331
G2 X150.579 Y100.784 I1.073 J1.279 E.01165
G1 X144.099 Y94.305 E.282
G1 X144.099 Y94.839 E.01643
G1 X150.359 Y101.099 E.27245
G2 X150.183 Y101.457 I.955 J.691 E.01234
G1 X148.099 Y99.373 E.09072
G3 X148.206 Y100.003 I-1.783 J.627 E.01978
G1 X150.059 Y101.866 E.08086
G2 X150.011 Y102.353 I4.876 J.723 E.01505
G1 X148.141 Y100.483 E.08138
G3 X148.001 Y100.877 I-1.186 J-.201 E.01293
G1 X150.015 Y102.891 E.08768
G2 X150.054 Y103.464 I1.758 J.17 E.01774
G1 X147.801 Y101.211 E.09805
G3 X147.55 Y101.494 I-1.23 J-.838 E.01168
G1 X152.387 Y106.331 E.21051
G1 X152.665 Y106.075 E.01163
G1 X152.033 Y105.443 E.02754
G1 X152.164 Y105.469 E.00413
G1 X152.603 Y105.479 E.01351
G1 X153.082 Y105.958 E.02086
G1 X153.192 Y105.502 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.474743
G1 F8336.759
G1 X153.605 Y105.275 E.01659
; LINE_WIDTH: 0.431333
G1 F9268.496
G3 X165.272 Y105.266 I5.84 J8.741 E.39147
; LINE_WIDTH: 0.473811
G1 F8354.783
G1 X165.701 Y105.502 E.01718
; WIPE_START
G1 X165.272 Y105.266 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.419 Y110.51 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.479327
G1 F8249.184
G1 X169.448 Y110.706 E.00704
; LINE_WIDTH: 0.434771
G1 F9187.164
G1 X169.477 Y110.902 E.00633
; LINE_WIDTH: 0.390216
G1 F10365.816
G1 X169.506 Y111.098 E.00561
; LINE_WIDTH: 0.344261
G1 F11946.596
G1 X169.537 Y111.306 E.00517
; LINE_WIDTH: 0.299198
G1 F14047.265
G1 X169.555 Y111.486 E.00378
; LINE_WIDTH: 0.257529
G1 F15000
G1 X169.574 Y111.666 E.00317
; LINE_WIDTH: 0.215861
G1 X169.592 Y111.846 E.00255
; LINE_WIDTH: 0.174192
G1 X169.611 Y112.026 E.00194
; LINE_WIDTH: 0.13218
G1 X169.63 Y112.209 E.00134
; LINE_WIDTH: 0.104029
G1 X169.637 Y112.335 E.00063
G1 X169.71 Y110.302 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X168.799 Y109.391 E.03964
G2 X168.056 Y108.114 I-7.669 J3.607 E.04554
G1 X169.567 Y109.624 E.06574
G1 X169.573 Y109.096 E.01624
G1 X166.045 Y105.568 E.15357
G1 X166.108 Y105.453 E.00403
M73 P48 R5
G2 X166.488 Y105.477 I.258 J-1.087 E.01176
G1 X169.58 Y108.569 E.13458
G1 X169.586 Y108.042 E.01624
G1 X166.966 Y105.421 E.11406
G2 X167.376 Y105.297 I-.348 J-1.9 E.01322
G1 X169.593 Y107.514 E.09647
G1 X169.6 Y106.987 E.01624
G1 X167.731 Y105.118 E.08135
G2 X168.034 Y104.886 I-.744 J-1.288 E.01176
G1 X169.606 Y106.459 E.06845
G1 X169.613 Y105.932 E.01623
G1 X168.3 Y104.618 E.05716
G2 X168.527 Y104.312 I-1.074 J-1.035 E.01178
G1 X169.62 Y105.404 E.04755
G1 X169.626 Y104.877 E.01623
G1 X168.703 Y103.953 E.0402
G2 X168.825 Y103.541 I-1.6 J-.701 E.01325
G1 X169.633 Y104.349 E.03515
G1 X169.639 Y103.822 E.01623
G1 X168.874 Y103.057 E.03329
G1 X168.875 Y102.523 E.01642
G1 X169.646 Y103.294 E.03355
G1 X169.653 Y102.767 E.01623
G1 X168.876 Y101.99 E.03382
G1 X168.876 Y101.456 E.01642
G1 X169.659 Y102.239 E.03408
G1 X169.666 Y101.712 E.01623
G1 X168.877 Y100.923 E.03434
G1 X168.877 Y100.389 E.01642
G1 X169.672 Y101.184 E.0346
G1 X169.679 Y100.657 E.01623
G1 X168.878 Y99.856 E.03487
G1 X168.879 Y99.322 E.01642
G1 X169.686 Y100.129 E.03513
G1 X169.692 Y99.602 E.01624
G1 X168.879 Y98.788 E.03539
G1 X168.88 Y98.255 E.01642
G1 X169.699 Y99.074 E.03565
G1 X169.706 Y98.547 E.01623
G1 X168.88 Y97.721 E.03592
G1 X168.881 Y97.188 E.01642
G1 X169.712 Y98.019 E.03618
G1 X169.719 Y97.492 E.01624
G1 X168.875 Y96.648 E.03672
G2 X168.76 Y95.999 I-1.969 J.014 E.02038
G1 X169.725 Y96.964 E.04201
G1 X169.732 Y96.437 E.01623
G1 X161.714 Y88.419 E.34895
G2 X162.109 Y88.324 I-.165 J-1.543 E.01252
G1 X162.139 Y88.309 E.00103
G1 X165.416 Y91.587 E.14265
G1 X165.409 Y91.503 E.00258
G1 X165.456 Y91.093 E.01272
G1 X162.493 Y88.13 E.12895
G2 X162.791 Y87.894 I-.75 J-1.253 E.01173
G1 X165.585 Y90.687 E.12159
G1 X165.773 Y90.341 E.01212
G1 X163.033 Y87.601 E.11925
G2 X163.225 Y87.259 I-1.183 J-.887 E.01211
G1 X166.018 Y90.052 E.12158
G1 X166.314 Y89.814 E.01169
G1 X163.341 Y86.841 E.12939
G2 X163.381 Y86.347 I-1.813 J-.398 E.01528
G1 X166.663 Y89.629 E.14282
G3 X167.079 Y89.511 I.498 J.964 E.0134
G1 X163.381 Y85.813 E.16093
G1 X163.381 Y85.279 E.01644
G1 X167.766 Y89.664 E.19085
; WIPE_START
G1 X166.352 Y88.25 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X159.607 Y91.822 Z1 F30000
G1 X147.147 Y98.421 Z1
G1 Z.6
G1 E.8 F1800
G1 F9532.131
G1 X144.099 Y95.372 E.13266
G1 X144.099 Y95.906 E.01643
G1 X146.167 Y97.974 E.09002
G1 X146.081 Y97.969 E.00266
G1 X145.686 Y98.028 E.01227
G1 X144.098 Y96.44 E.06911
G1 X144.098 Y96.974 E.01643
G1 X145.291 Y98.167 E.05192
G1 X144.959 Y98.369 E.01196
G1 X144.098 Y97.508 E.0375
G1 X144.097 Y98.042 E.01643
G1 X144.679 Y98.623 E.02529
G1 X144.593 Y98.724 E.00408
G1 X144.498 Y98.536 E.00648
G1 X144.238 Y98.668 E.00896
G1 X144.226 Y98.644 E.00083
G1 X144.187 Y98.665 E.00136
G1 X143.928 Y98.406 E.01128
G1 X144.445 Y99.167 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.410538
G1 F9792.793
G1 X144.195 Y99.294 E.00838
; LINE_WIDTH: 0.450721
G1 F8827.848
G1 X144.168 Y99.308 E.00103
G1 X144.065 Y99.773 E.01581
; LINE_WIDTH: 0.4491
G1 F8863.066
G1 X144.08 Y99.794 E.00085
; LINE_WIDTH: 0.41363
G1 F9711.104
G1 X144.095 Y99.814 E.00077
; LINE_WIDTH: 0.382337
G1 F10606.443
G1 X144.254 Y100.022 E.00722
G1 X144.682 Y101.212 F30000
; LINE_WIDTH: 0.401232
G1 F10047.12
G1 X144.697 Y101.494 E.00827
G1 X144.765 Y101.54 E.00238
; LINE_WIDTH: 0.384394
G1 F10542.543
G1 X144.833 Y101.585 E.00227
; LINE_WIDTH: 0.351175
G1 F11678.645
G1 X144.988 Y101.679 E.00457
; LINE_WIDTH: 0.323649
G1 F12823.752
G1 X145.46 Y101.933 E.01226
; LINE_WIDTH: 0.366234
G1 F11134.708
G1 X145.638 Y102.015 E.00516
; LINE_WIDTH: 0.417149
G1 F9619.787
G1 X145.778 Y102.071 E.00462
G1 X145.799 Y102.059 E.00072
; LINE_WIDTH: 0.393983
G1 F10254.594
G1 X146.025 Y101.914 E.00769
G1 X147.059 Y103.14 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42059
G1 F9532.131
G1 X146.304 Y102.385 E.03286
G1 X146.366 Y102.347 E.00222
G1 X146.356 Y102.331 E.00057
G1 X146.592 Y102.18 E.00862
G1 X146.517 Y102.063 E.00426
G1 X151.594 Y107.14 E.22095
G1 X151.849 Y106.861 E.01163
G1 X146.889 Y101.901 E.21589
G2 X147.246 Y101.725 I-.321 J-1.102 E.01234
G1 X152.228 Y106.706 E.21681
G1 X151.47 Y107.55 F30000
G1 F9532.131
G1 X149.962 Y106.043 E.06562
G3 X150.234 Y106.849 I-4.52 J1.974 E.02621
G1 X151.117 Y107.731 E.03842
G2 X150.886 Y108.035 I1.621 J1.471 E.01175
G1 X150.158 Y107.307 E.03168
G1 X150.516 Y108.416 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.310266
G1 F13465.739
G1 X150.224 Y109.385 E.02206
G1 X150.218 Y109.383 F30000
; LINE_WIDTH: 0.121127
G1 F15000
G1 X150.265 Y109.236 E.00099
; LINE_WIDTH: 0.169533
G1 X150.313 Y109.089 E.0016
; LINE_WIDTH: 0.217939
G1 X150.361 Y108.941 E.00221
; LINE_WIDTH: 0.243794
G1 X150.518 Y108.416 E.00897
; WIPE_START
G1 X150.361 Y108.941 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.307 Y103.222 Z1 F30000
G1 X143.386 Y101.047 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.55283
G1 F7060.07
G3 X144.02 Y101.191 I-.443 J3.409 E.02707
G1 X144.028 Y100.94 E.01043
G1 X144.173 Y100.803 E.00831
G1 X144.129 Y100.658 E.00627
G1 X144.074 Y100.678 E.00243
G1 X143.874 Y100.593 E.00904
G1 X143.756 Y100.46 E.00737
G3 X143.345 Y100.911 I-1.163 J-.647 E.02559
G1 X143.396 Y100.989 E.00387
G1 X142.854 Y101.01 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.109651
G1 F15000
G1 X142.763 Y101.074 E.0006
; LINE_WIDTH: 0.138436
G1 X142.655 Y101.152 E.00103
G1 X142.698 Y101.211 E.00057
; WIPE_START
G1 X142.655 Y101.152 E-.2701
G1 X142.763 Y101.074 E-.4899
; WIPE_END
G1 E-.04 F1800
G1 X137.907 Y95.186 Z1 F30000
G1 X127.017 Y81.98 Z1
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.483234
G1 F8175.998
G1 X126.807 Y81.95 E.00762
; LINE_WIDTH: 0.438304
G1 F9105.075
G1 X126.596 Y81.921 E.00684
; LINE_WIDTH: 0.39182
G1 F10318.158
G1 X126.372 Y81.89 E.00645
; LINE_WIDTH: 0.344474
G1 F11938.175
G1 X126.191 Y81.873 E.00445
; LINE_WIDTH: 0.299914
G1 F14008.152
G1 X126.011 Y81.856 E.00379
; LINE_WIDTH: 0.255353
G1 F15000
G1 X125.83 Y81.839 E.00314
; LINE_WIDTH: 0.210793
G1 X125.65 Y81.821 E.00248
; LINE_WIDTH: 0.165693
G1 X125.465 Y81.804 E.00186
; LINE_WIDTH: 0.119988
G1 X125.149 Y81.788 E.00199
; OBJECT_ID: 817
; WIPE_START
G1 X125.465 Y81.804 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 861
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X122.358 Y88.775 Z1 F30000
G1 X99.551 Y139.947 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X100.805 Y138.59 I1.308 J-.049 E.06303
G1 X100.904 Y138.589 E.00304
G3 X99.555 Y140.007 I-.044 J1.309 E.18486
; WIPE_START
M204 S10000
G1 X99.56 Y139.687 E-.1216
G1 X99.628 Y139.435 E-.09914
G1 X99.744 Y139.201 E-.09921
G1 X99.904 Y138.995 E-.09909
G1 X100.102 Y138.825 E-.09915
G1 X100.33 Y138.697 E-.0992
G1 X100.578 Y138.617 E-.09905
G1 X100.692 Y138.603 E-.04356
; WIPE_END
G1 E-.04 F1800
G1 X95.322 Y133.18 Z1 F30000
G1 X88.077 Y125.862 Z1
G1 Z.6
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X88.176 Y125.861 E.00304
G3 X88.017 Y125.865 I-.044 J1.309 E.24789
; WIPE_START
M204 S10000
G1 X88.176 Y125.861 E-.06038
G1 X88.433 Y125.897 E-.09871
G1 X88.679 Y125.983 E-.09923
G1 X88.904 Y126.116 E-.09919
G1 X89.097 Y126.291 E-.09906
G1 X89.252 Y126.501 E-.09913
G1 X89.362 Y126.738 E-.09913
G1 X89.424 Y126.991 E-.09925
G1 X89.424 Y127.007 E-.00592
; WIPE_END
G1 E-.04 F1800
G1 X96.041 Y130.811 Z1 F30000
G1 X102.963 Y134.791 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X102.951 Y134.79 E.00042
G3 X102.951 Y114.604 I.387 J-10.093 E1.02693
G3 X106.186 Y115.006 I.373 J10.204 E.10859
G3 X103.454 Y134.797 I-2.848 J9.691 E.95301
G1 X103.023 Y134.792 E.01431
M204 S250
G1 X102.968 Y134.399 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X102.965 Y134.398 E.00009
G3 X102.965 Y114.995 I.372 J-9.702 E.91432
G3 X106.075 Y115.382 I.359 J9.808 E.09669
G3 X103.449 Y134.405 I-2.737 J9.315 E.84851
G1 X103.028 Y134.4 E.01295
; WIPE_START
M204 S10000
G1 X102.965 Y134.398 E-.02385
G1 X102.482 Y134.369 E-.18389
G1 X102.001 Y134.314 E-.18398
G1 X101.523 Y134.236 E-.18405
G1 X101.05 Y134.135 E-.18392
G1 X101.049 Y134.134 E-.00032
; WIPE_END
G1 E-.04 F1800
G1 X93.901 Y131.46 Z1 F30000
G1 X86.196 Y128.577 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G3 X86.451 Y126.161 I1.599 J-1.053 E.08729
G1 X86.563 Y126.049 E.00526
G1 X86.733 Y126.178 E.00706
G2 X88.192 Y125.469 I1.384 J.993 E.29891
G2 X87.133 Y125.785 I-.054 J1.748 E.0373
G1 X86.997 Y125.615 E.00724
G1 X111.158 Y101.454 E1.13343
G3 X112.891 Y100.917 I1.387 J1.41 E.06251
G3 X113.825 Y101.406 I-.466 J2.026 E.03539
G2 X112.605 Y101.734 I-.065 J2.196 E.04251
G2 X115.281 Y103.235 I.977 J1.394 E.22798
G1 X115.286 Y102.856 E.01257
G1 X125.17 Y112.74 E.46369
G2 X123.551 Y113.397 I-.202 J1.827 E.0604
G2 X126.595 Y114.549 I1.347 J1.039 E.2106
G1 X126.599 Y114.176 E.01237
G3 X126.57 Y116.866 I-1.37 J1.33 E.09902
G1 X102.409 Y141.027 E1.13343
G1 X102.239 Y140.891 E.00724
G2 X101.611 Y141.423 I-1.383 J-.993 E.32717
G1 X101.846 Y141.291 E.00894
G1 X101.975 Y141.461 E.00706
G3 X100.5 Y142.147 I-1.539 J-1.381 E.05546
G3 X99.137 Y141.573 I.011 J-1.932 E.05034
G1 X86.451 Y128.887 E.59514
G3 X86.23 Y128.626 I1.345 J-1.363 E.01135
; WIPE_START
G1 X86.021 Y128.249 E-.1638
M73 P49 R5
G1 X85.913 Y127.894 E-.14116
G1 X85.877 Y127.524 E-.14116
G1 X85.913 Y127.154 E-.14116
G1 X86.021 Y126.799 E-.14116
G1 X86.06 Y126.726 E-.03155
; WIPE_END
G1 E-.04 F1800
G1 X91.787 Y121.68 Z1 F30000
G1 X112.351 Y103.559 Z1
G1 Z.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X113.533 Y101.82 I1.236 J-.431 E.075
G1 X113.632 Y101.82 E.00304
G3 X112.372 Y103.615 I-.044 J1.309 E.17289
; WIPE_START
M204 S10000
G1 X112.283 Y103.308 E-.12161
G1 X112.272 Y103.178 E-.04962
G1 X112.288 Y102.917 E-.09911
G1 X112.356 Y102.665 E-.09921
G1 X112.472 Y102.432 E-.09917
G1 X112.632 Y102.226 E-.09907
G1 X112.83 Y102.055 E-.09924
G1 X113.044 Y101.936 E-.09298
; WIPE_END
G1 E-.04 F1800
G1 X118.698 Y107.062 Z1 F30000
G1 X125.675 Y113.386 Z1
G1 Z.6
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X124.846 Y113.134 I-.774 J1.056 E.22568
G1 X124.945 Y113.133 E.00304
G3 X125.626 Y113.351 I-.044 J1.309 E.02225
; WIPE_START
M204 S10000
G1 X125.867 Y113.563 E-.12187
G1 X126.022 Y113.773 E-.09919
G1 X126.132 Y114.01 E-.09914
G1 X126.193 Y114.263 E-.09915
G1 X126.203 Y114.524 E-.09919
G1 X126.161 Y114.782 E-.09906
G1 X126.068 Y115.026 E-.09919
G1 X126.008 Y115.122 E-.04321
; WIPE_END
G1 E-.04 F1800
G1 X118.783 Y117.583 Z1 F30000
G1 X85.869 Y128.796 Z1
G1 Z.6
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X86.16 Y125.897 I1.911 J-1.272 E.09695
G1 X110.894 Y101.163 E1.07482
G3 X112.967 Y100.53 I1.655 J1.709 E.06915
G3 X114.147 Y101.163 I-.586 J2.508 E.04162
G1 X126.861 Y113.877 E.55246
G3 X127.152 Y116.775 I-1.663 J1.631 E.09669
G1 X126.861 Y117.13 E.01411
G1 X102.127 Y141.864 E1.07482
G3 X98.873 Y141.864 I-1.627 J-1.62 E.11109
G1 X86.16 Y129.15 E.55246
G3 X85.903 Y128.845 I1.62 J-1.626 E.01229
M204 S10000
G1 X86.38 Y128.215 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.318792
G1 F13049.567
G1 X86.482 Y128.386 E.00448
G1 X86.614 Y128.548 E.0047
G2 X86.754 Y128.697 I1.523 J-1.288 E.0046
; LINE_WIDTH: 0.34408
G1 F11953.787
G1 X86.907 Y128.834 E.00505
; LINE_WIDTH: 0.375899
G1 F10811.514
G1 X87.069 Y128.966 E.00567
; LINE_WIDTH: 0.410957
G1 F9781.645
G1 X87.141 Y129.02 E.0027
; LINE_WIDTH: 0.437954
G1 F9113.147
G1 X87.214 Y129.073 E.00289
G1 X87.23 Y129.068 E.00056
; LINE_WIDTH: 0.409352
G1 F9824.489
G1 X87.494 Y128.98 E.00831
G1 X86.38 Y128.215 F30000
; LINE_WIDTH: 0.283084
G1 F14989.777
G3 X86.292 Y128.032 I1.238 J-.7 E.00398
G1 X86.225 Y127.841 E.00395
; LINE_WIDTH: 0.244045
G1 F15000
G1 X86.185 Y127.643 E.00331
; LINE_WIDTH: 0.212704
G3 X86.164 Y127.445 I1.612 J-.27 E.00276
; LINE_WIDTH: 0.172693
G1 X86.165 Y127.246 E.0021
; LINE_WIDTH: 0.133611
G3 X86.191 Y127.051 I1.052 J.04 E.00146
; LINE_WIDTH: 0.101648
G1 X86.207 Y126.973 E.00038
; WIPE_START
G1 X86.191 Y127.051 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.062 Y126.106 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.195906
G1 F15000
G1 X86.921 Y125.969 E.00245
; LINE_WIDTH: 0.229262
G1 X86.781 Y125.832 E.00298
; LINE_WIDTH: 0.262618
G1 X86.64 Y125.695 E.00351
; WIPE_START
G1 X86.781 Y125.832 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.627 Y125.273 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.118994
G1 F15000
G1 X87.864 Y125.26 E.00147
G1 X93.368 Y120.334 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F9547.301
G2 X88.883 Y124.818 I575.238 J579.869 E.19485
G1 X89.522 Y125.135 E.0219
G1 X89.919 Y125.471 E.01599
G1 X90.234 Y125.879 E.01582
G1 X90.476 Y126.408 E.01788
G1 X90.581 Y126.91 E.01576
G3 X90.365 Y128.215 I-2.768 J.211 E.04104
G1 X90.04 Y128.722 E.01851
G1 X89.787 Y128.999 E.01151
G1 X89.372 Y129.3 E.01576
G1 X88.852 Y129.529 E.01747
G3 X88.288 Y129.637 I-.872 J-3.033 E.01765
G1 X98.387 Y139.735 E.43883
G1 X98.482 Y139.205 E.01656
G1 X98.667 Y138.748 E.01512
G1 X98.938 Y138.338 E.01512
G1 X99.285 Y137.989 E.01511
G1 X99.793 Y137.673 E.01838
G3 X101.966 Y137.696 I1.064 J2.258 E.06911
G1 X102.441 Y138.009 E.01747
G1 X102.93 Y138.565 E.02276
G3 X103.208 Y139.135 I-2.778 J1.705 E.0195
G2 X107.69 Y134.656 I-1175.854 J-1181.15 E.19468
G3 X93.347 Y120.391 I-4.357 J-9.962 E.79849
G1 X92.469 Y121.764 F30000
; LINE_WIDTH: 0.41999
G1 F9547.303
G1 X89.523 Y124.71 E.12801
G1 X89.891 Y124.937 E.01328
G1 X90.265 Y125.288 E.01575
G1 X90.62 Y125.798 E.01909
G1 X90.842 Y126.319 E.01742
G1 X90.957 Y126.875 E.01743
G1 X90.967 Y127.388 E.01578
G1 X90.874 Y127.923 E.01667
G1 X90.693 Y128.399 E.01566
G1 X90.403 Y128.879 E.01725
G1 X90.019 Y129.297 E.01742
G1 X89.524 Y129.645 E.0186
G1 X89.042 Y129.857 E.01617
G1 X98.164 Y138.979 E.39639
G1 X98.347 Y138.548 E.0144
G1 X98.665 Y138.078 E.01742
G1 X99.069 Y137.681 E.01741
G1 X99.543 Y137.371 E.01742
G1 X100.055 Y137.165 E.01693
G1 X100.546 Y137.065 E.01539
G3 X102.033 Y137.304 I.244 J3.231 E.0467
G1 X102.648 Y137.694 E.0224
G1 X102.858 Y137.883 E.00865
G1 X103.222 Y138.326 E.01762
G1 X103.325 Y138.49 E.00597
G1 X106.26 Y135.555 E.12753
G3 X92.454 Y121.822 I-2.929 J-10.861 E.72324
G1 X91.84 Y122.926 F30000
; LINE_WIDTH: 0.420138
G1 F9543.567
G1 X90.123 Y124.643 E.07463
G1 X90.555 Y125.047 E.01816
G3 X91.096 Y125.925 I-2.322 J2.039 E.03188
; LINE_WIDTH: 0.440057
G1 F9064.889
G1 X91.152 Y126.023 E.00363
; LINE_WIDTH: 0.47565
G1 F8319.275
G1 X91.207 Y126.12 E.00395
; LINE_WIDTH: 0.520311
G1 F7540.995
G1 X91.262 Y126.218 E.00436
G1 X91.381 Y126.859 E.02536
; LINE_WIDTH: 0.530545
G1 F7382.722
G1 X91.411 Y127.238 E.0151
; LINE_WIDTH: 0.525324
G1 F7462.635
G1 X91.365 Y127.449 E.0085
; LINE_WIDTH: 0.48319
G1 F8176.8
G1 X91.318 Y127.66 E.00776
; LINE_WIDTH: 0.420246
G1 F9540.82
G3 X90.441 Y129.413 I-3.519 J-.665 E.06106
G1 X89.955 Y129.824 E.01957
G1 X89.696 Y129.978 E.00924
G1 X98.043 Y138.324 E.36292
G1 X98.391 Y137.818 E.0189
G1 X98.776 Y137.429 E.01682
G1 X99.393 Y137.025 E.02267
G1 X99.969 Y136.798 E.01906
G1 X100.51 Y136.69 E.01695
; LINE_WIDTH: 0.444623
G1 F8961.856
G1 X100.781 Y136.66 E.00894
; LINE_WIDTH: 0.508437
G1 F7733.338
G1 X101.053 Y136.629 E.01036
G1 X101.609 Y136.713 E.02132
; LINE_WIDTH: 0.489373
G1 F8063.567
G1 X101.85 Y136.818 E.00956
; LINE_WIDTH: 0.420846
G1 F9525.671
G3 X102.976 Y137.469 I-2.446 J5.533 E.04013
G1 X103.37 Y137.912 E.01827
G1 X105.098 Y136.184 E.07526
G3 X102.348 Y136.279 I-1.79 J-11.916 E.08491
; LINE_WIDTH: 0.44457
G1 F8963.028
G1 X102.064 Y136.273 E.00929
; LINE_WIDTH: 0.509481
G1 F7716.037
G1 X101.781 Y136.267 E.01079
G1 X101.191 Y136.171 E.02269
; LINE_WIDTH: 0.49172
G1 F8021.39
G1 X100.918 Y136.089 E.01043
; LINE_WIDTH: 0.420975
G1 F9522.445
G3 X99.52 Y135.679 I11.699 J-42.521 E.04489
G3 X92.028 Y127.469 I3.854 J-11.04 E.35681
; LINE_WIDTH: 0.45869
G1 F8658.633
G1 X91.989 Y127.371 E.00358
; LINE_WIDTH: 0.49377
G1 F7984.917
G1 X91.949 Y127.273 E.00389
; LINE_WIDTH: 0.523916
G1 F7484.475
G1 X91.909 Y127.175 E.00415
G2 X91.74 Y126.134 I-48.714 J7.382 E.04136
; LINE_WIDTH: 0.510865
G1 F7693.212
G1 X91.736 Y125.903 E.00879
; LINE_WIDTH: 0.474515
G1 F8341.152
G1 X91.733 Y125.673 E.0081
; LINE_WIDTH: 0.421545
G1 F9508.107
G3 X91.724 Y124.004 I26.206 J-.983 E.05149
G3 X91.832 Y122.986 I10.337 J.584 E.03162
G1 X91.302 Y124.057 F30000
; LINE_WIDTH: 0.50439
G1 F7801.157
G1 X90.732 Y124.627 E.03034
G1 X91.154 Y125.149 E.02523
G1 X91.307 Y125.401 E.0111
G3 X91.301 Y124.117 I11.696 J-.701 E.04832
G1 X91.693 Y127.632 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X91.598 Y128.134 E.01568
G3 X90.726 Y129.659 I-3.778 J-1.147 E.05444
G1 X90.291 Y130.04 E.01776
G1 X97.983 Y137.732 E.33424
G1 X98.38 Y137.283 E.0184
G1 X98.875 Y136.895 E.01933
G3 X100.382 Y136.329 I2.017 J3.08 E.04988
G3 X91.709 Y127.69 I2.937 J-11.623 E.39477
G1 X91.695 Y128.923 F30000
; LINE_WIDTH: 0.418663
G1 F9581.035
G1 X91.439 Y129.375 E.0159
G1 X91.012 Y129.905 E.02084
G1 X90.847 Y130.062 E.00698
G3 X93.471 Y132.71 I-87.802 J89.631 E.11414
; LINE_WIDTH: 0.363866
G1 F11216.867
G2 X95.233 Y134.476 I48.085 J-46.215 E.06526
; LINE_WIDTH: 0.399345
G1 F10100.301
G1 X95.688 Y134.905 E.01815
; LINE_WIDTH: 0.43152
G1 F9264.025
G1 X95.92 Y135.117 E.00994
; LINE_WIDTH: 0.449954
G1 F8844.475
G3 X96.577 Y135.793 I-3.701 J4.262 E.03131
; LINE_WIDTH: 0.423583
G1 F9457.189
G1 X97.961 Y137.176 E.0607
G1 X98.42 Y136.754 E.01933
G1 X99.089 Y136.33 E.02459
G3 X96.517 Y135.054 I5.297 J-13.914 E.0892
G1 X96.017 Y134.689 E.0192
; LINE_WIDTH: 0.406355
G1 F9905.485
G1 X95.54 Y134.296 E.01829
; LINE_WIDTH: 0.363873
G1 F11216.625
G3 X93.795 Y132.561 I14.652 J-16.487 E.0644
; LINE_WIDTH: 0.416799
G1 F9628.801
G3 X91.717 Y128.979 I8.858 J-7.533 E.12684
G1 X91.627 Y129.723 F30000
; LINE_WIDTH: 0.38361
G1 F10566.79
G1 X91.352 Y130.06 E.01207
G1 X92.225 Y130.932 E.03425
G3 X91.651 Y129.778 I9.143 J-5.259 E.03581
G1 X98.304 Y136.398 F30000
; LINE_WIDTH: 0.38223
G1 F10609.766
G3 X97.087 Y135.796 I4.203 J-10.037 E.03755
G1 X97.962 Y136.67 E.03418
G1 X98.257 Y136.435 E.01045
G1 X103.967 Y136.722 F30000
; LINE_WIDTH: 0.50446
G1 F7799.975
G3 X102.613 Y136.716 I-.626 J-12.583 E.05096
G3 X103.393 Y137.296 I-1.768 J3.193 E.03666
G1 X103.925 Y136.764 E.02829
G1 X108.85 Y133.614 F30000
; LINE_WIDTH: 0.41999
G1 F9547.301
G1 X108.004 Y134.091 E.02984
G3 X94.41 Y119.174 I-4.674 J-9.393 E.834
G1 X94.185 Y118.981 E.00909
G1 X88.216 Y124.951 E.25941
G1 X88.25 Y125.086 E.00428
G1 X88.795 Y125.186 E.01702
G1 X89.346 Y125.469 E.01905
G1 X89.691 Y125.779 E.01425
G1 X89.936 Y126.117 E.01282
G1 X90.139 Y126.618 E.01661
G3 X90.036 Y128.03 I-2.037 J.562 E.04437
G1 X89.754 Y128.476 E.01621
G1 X89.556 Y128.701 E.00922
G1 X89.22 Y128.955 E.01292
G1 X88.7 Y129.184 E.01747
G1 X88.225 Y129.262 E.01481
G1 X87.995 Y129.244 E.00707
G1 X87.969 Y129.413 E.00526
G1 X87.673 Y129.555 E.01008
G1 X98.469 Y140.351 E.46911
G1 X98.611 Y140.055 E.01008
G1 X98.782 Y140.027 E.00533
G1 X98.764 Y139.749 E.00857
G3 X99.943 Y138.019 I2.131 J.186 E.06723
G3 X101.759 Y138.011 I.916 J1.904 E.05765
G1 X102.233 Y138.324 E.01747
G1 X102.639 Y138.804 E.01933
G1 X102.837 Y139.224 E.01426
G1 X102.937 Y139.777 E.01726
G1 X103.073 Y139.808 E.0043
G1 X109.043 Y133.839 E.25941
G1 X108.889 Y133.66 E.00725
G1 X109.255 Y133.485 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.563474
G1 F6915.714
G1 X109.524 Y133.253 E.01504
; LINE_WIDTH: 0.530567
G1 F7382.399
G1 X109.793 Y133.022 E.01409
; LINE_WIDTH: 0.500409
G1 F7869.045
G1 X109.993 Y132.842 E.01004
; LINE_WIDTH: 0.474146
G1 F8348.301
G1 X110.183 Y132.669 E.00905
; LINE_WIDTH: 0.443384
G1 F8989.576
G1 X110.57 Y132.301 E.01743
G1 X111.295 Y131.558 E.03385
; LINE_WIDTH: 0.473634
G1 F8358.219
G1 X111.474 Y131.36 E.0094
; LINE_WIDTH: 0.499814
G1 F7879.301
G1 X111.647 Y131.169 E.00958
; LINE_WIDTH: 0.53002
G1 F7390.692
G1 X111.886 Y130.891 E.01454
; LINE_WIDTH: 0.563491
G1 F6915.482
G1 X112.117 Y130.623 E.01504
G1 X112.834 Y130.371 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4221
G1 F9494.171
G1 X112.368 Y129.905 E.02036
G2 X112.558 Y129.558 I-3.375 J-2.075 E.01221
G1 X112.982 Y129.982 E.01854
G1 X113.25 Y129.714 E.01172
G1 X112.738 Y129.202 E.0224
G2 X112.907 Y128.835 I-3.601 J-1.882 E.01249
G1 X113.519 Y129.446 E.02672
G1 X113.787 Y129.178 E.01172
G1 X113.062 Y128.454 E.03166
G2 X113.204 Y128.059 I-3.873 J-1.616 E.01296
G1 X114.055 Y128.91 E.03718
G1 X114.323 Y128.642 E.01172
G1 X113.333 Y127.652 E.04326
G2 X113.448 Y127.231 I-4.166 J-1.367 E.01349
G1 X114.591 Y128.374 E.04994
G1 X114.859 Y128.106 E.01172
G1 X113.549 Y126.795 E.05727
G2 X113.632 Y126.342 I-4.492 J-1.065 E.01423
G1 X115.127 Y127.838 E.06533
G1 X115.395 Y127.569 E.01172
G1 X113.697 Y125.871 E.0742
G2 X113.741 Y125.379 I-5.015 J-.691 E.01529
G1 X115.664 Y127.301 E.08402
G1 X115.932 Y127.033 E.01172
G1 X113.762 Y124.863 E.09482
G2 X113.757 Y124.322 I-5.431 J-.222 E.01673
G1 X116.2 Y126.765 E.10675
G1 X116.468 Y126.497 E.01172
G1 X113.72 Y123.749 E.12007
G2 X113.644 Y123.137 I-6.157 J.451 E.01906
G1 X116.736 Y126.229 E.13509
G1 X117.004 Y125.961 E.01172
G1 X113.523 Y122.479 E.15214
G2 X113.343 Y121.763 I-7.245 J1.437 E.02281
G1 X117.272 Y125.693 E.1717
G1 X117.54 Y125.424 E.01172
G1 X113.065 Y120.949 E.19557
G2 X112.637 Y119.984 I-9.89 J3.814 E.03262
G1 X117.929 Y125.276 E.23124
M73 P50 R5
G1 X124.452 Y116.249 F30000
G1 F9494.171
G1 X125.584 Y117.381 E.04947
G1 X125.852 Y117.113 E.01172
G1 X125.192 Y116.453 E.02885
G2 X125.619 Y116.343 I-.149 J-1.469 E.01367
G1 X126.12 Y116.845 E.02191
G2 X126.382 Y116.57 I-1.263 J-1.466 E.01174
G1 X125.974 Y116.162 E.01782
G1 X126.267 Y115.942 E.01132
G1 X126.263 Y116.023 E.00251
G1 X126.378 Y116.03 E.00356
G1 X126.731 Y116.383 E.01544
G1 X126.798 Y115.743 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.144267
G1 F15000
G1 X126.784 Y114.806 E.00774
G1 X126.795 Y114.827 F30000
; LINE_WIDTH: 0.278613
G1 F15000
G3 X126.751 Y115.718 I-18.136 J-.444 E.01713
; WIPE_START
G1 X126.795 Y114.827 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X126.397 Y114.079 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.198339
G1 F15000
G2 X126.322 Y113.738 I-7.032 J1.355 E.00443
G1 X126.247 Y113.636 E.00161
; LINE_WIDTH: 0.14784
G1 X125.938 Y113.294 E.00394
G1 X125.697 Y113.087 E.00272
; LINE_WIDTH: 0.198273
G2 X125.56 Y113.009 I-.178 J.153 E.00203
; LINE_WIDTH: 0.175831
G1 X125.485 Y112.994 E.00083
; LINE_WIDTH: 0.14528
G1 X125.405 Y112.979 E.00068
; LINE_WIDTH: 0.113359
G1 X125.266 Y112.959 E.00081
G1 X124.569 Y112.612 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4221
G1 F9494.171
G1 X115.555 Y103.598 E.3939
G3 X115.42 Y104 I-1.4 J-.244 E.01314
G1 X124.026 Y112.605 E.37604
G2 X123.689 Y112.804 I.492 J1.219 E.01214
G1 X115.219 Y104.334 E.37011
G1 X114.968 Y104.619 E.01174
G1 X123.405 Y113.056 E.36867
G1 X123.171 Y113.359 E.01181
G1 X114.665 Y104.853 E.37169
G3 X114.3 Y105.025 I-.751 J-1.122 E.0125
G1 X122.999 Y113.724 E.38012
G2 X122.882 Y114.143 I1.685 J.696 E.01348
G1 X113.875 Y105.135 E.39361
G3 X113.346 Y105.143 I-.286 J-1.485 E.01641
G1 X123.092 Y114.888 E.42584
; WIPE_START
G1 X121.677 Y113.474 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X126.381 Y114.081 Z1 F30000
G1 Z.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.128656
G1 F15000
G2 X126.306 Y113.599 I-9.554 J1.241 E.00341
; WIPE_START
G1 X126.381 Y114.081 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X120.989 Y108.68 Z1 F30000
G1 X115.083 Y102.766 Z1
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.198325
G1 F15000
G2 X115.009 Y102.424 I-6.96 J1.337 E.00443
G1 X114.933 Y102.322 E.00161
; LINE_WIDTH: 0.147842
G1 X114.624 Y101.98 E.00394
G1 X114.383 Y101.773 E.00272
; LINE_WIDTH: 0.203995
G1 X114.253 Y101.678 E.00212
; LINE_WIDTH: 0.231338
G1 X114.111 Y101.583 E.00263
G1 X114.097 Y101.647 F30000
; LINE_WIDTH: 0.169656
G1 F15000
G1 X114.393 Y101.686 E.00309
G1 X114.097 Y101.647 F30000
; LINE_WIDTH: 0.154792
G1 F15000
G1 X114.021 Y101.638 E.0007
; LINE_WIDTH: 0.115367
G1 X113.852 Y101.625 E.001
G1 X113.21 Y101.236 F30000
; LINE_WIDTH: 0.20326
G1 F15000
G1 X112.291 Y101.244 E.012
G1 X112.479 Y101.566 F30000
; LINE_WIDTH: 0.439867
G1 F9069.223
G1 X112.551 Y101.29 E.00924
G1 X113.08 Y101.187 E.01743
G1 X112.212 Y101.864 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4221
G1 F9494.171
G1 X111.766 Y101.418 E.01947
G2 X111.454 Y101.642 I.408 J.897 E.01195
G1 X111.857 Y102.045 E.01762
G2 X111.679 Y102.403 I1.702 J1.071 E.01238
G1 X111.179 Y101.904 E.02183
G1 X110.911 Y102.172 E.01172
G1 X111.569 Y102.829 E.02872
G2 X111.561 Y103.358 I1.75 J.289 E.0164
G1 X110.643 Y102.44 E.04011
G1 X110.375 Y102.708 E.01172
G1 X125.316 Y117.649 E.65287
G1 X125.048 Y117.917 E.01172
G1 X110.107 Y102.976 E.65287
G1 X109.839 Y103.244 E.01172
G1 X124.78 Y118.185 E.65287
G1 X124.512 Y118.453 E.01172
G1 X109.571 Y103.512 E.65287
G1 X109.303 Y103.781 E.01172
G1 X124.243 Y118.721 E.65287
G1 X123.975 Y118.99 E.01172
G1 X109.034 Y104.049 E.65287
G1 X108.766 Y104.317 E.01172
G1 X123.707 Y119.258 E.65287
G1 X123.439 Y119.526 E.01172
G1 X108.498 Y104.585 E.65287
G1 X108.23 Y104.853 E.01172
G1 X123.171 Y119.794 E.65287
G1 X122.903 Y120.062 E.01172
G1 X107.962 Y105.121 E.65287
G1 X107.694 Y105.389 E.01172
G1 X122.635 Y120.33 E.65287
G1 X122.367 Y120.598 E.01172
G1 X107.426 Y105.657 E.65287
G1 X107.158 Y105.926 E.01172
G1 X122.098 Y120.866 E.65287
G1 X121.83 Y121.135 E.01172
G1 X106.889 Y106.194 E.65287
G1 X106.621 Y106.462 E.01172
G1 X121.562 Y121.403 E.65287
G1 X121.294 Y121.671 E.01172
G1 X106.353 Y106.73 E.65287
G1 X106.085 Y106.998 E.01172
G1 X121.026 Y121.939 E.65287
G1 X120.758 Y122.207 E.01172
G1 X105.817 Y107.266 E.65287
G1 X105.549 Y107.534 E.01172
G1 X120.49 Y122.475 E.65287
G1 X120.222 Y122.743 E.01172
G1 X105.281 Y107.802 E.65287
G1 X105.013 Y108.07 E.01172
G1 X119.953 Y123.011 E.65287
G1 X119.685 Y123.279 E.01172
G1 X104.745 Y108.339 E.65287
G1 X104.476 Y108.607 E.01172
G1 X119.417 Y123.548 E.65287
G1 X119.149 Y123.816 E.01172
G1 X104.208 Y108.875 E.65287
G1 X103.94 Y109.143 E.01172
G1 X118.881 Y124.084 E.65287
G1 X118.613 Y124.352 E.01172
G1 X103.672 Y109.411 E.65287
G1 X103.404 Y109.679 E.01172
G1 X118.345 Y124.62 E.65287
G1 X118.077 Y124.888 E.01172
G1 X103.136 Y109.947 E.65287
M73 P51 R5
G1 X102.868 Y110.215 E.01172
G1 X108.04 Y115.387 E.22599
G2 X107.075 Y114.959 I-4.78 J9.466 E.03262
G1 X102.6 Y110.484 E.19557
G1 X102.331 Y110.752 E.01172
G1 X106.261 Y114.681 E.1717
G2 X105.545 Y114.501 I-2.154 J7.07 E.02281
G1 X102.063 Y111.02 E.15214
G1 X101.795 Y111.288 E.01172
G1 X104.887 Y114.38 E.13509
G2 X104.275 Y114.304 I-1.063 J6.085 E.01906
G1 X101.527 Y111.556 E.12007
G1 X101.259 Y111.824 E.01172
G1 X103.702 Y114.267 E.10675
G1 X103.168 Y114.269 E.0165
G1 X100.991 Y112.092 E.09513
G1 X100.723 Y112.36 E.01172
G1 X102.653 Y114.291 E.08434
G2 X102.153 Y114.327 I.02 J3.758 E.01551
G1 X100.455 Y112.629 E.0742
G1 X100.186 Y112.897 E.01172
G1 X101.681 Y114.392 E.06533
G2 X101.229 Y114.475 I.614 J4.583 E.01423
G1 X99.918 Y113.165 E.05727
G1 X99.65 Y113.433 E.01172
G1 X100.793 Y114.576 E.04994
G2 X100.372 Y114.691 I.945 J4.277 E.01349
G1 X99.382 Y113.701 E.04326
G1 X99.114 Y113.969 E.01172
G1 X99.965 Y114.82 E.03718
G2 X99.57 Y114.962 I1.219 J4.01 E.01296
G1 X98.846 Y114.237 E.03166
G1 X98.578 Y114.505 E.01172
G1 X99.189 Y115.117 E.02672
G2 X98.822 Y115.286 I1.515 J3.77 E.01249
G1 X98.31 Y114.774 E.0224
G1 X98.042 Y115.042 E.01172
G1 X98.466 Y115.466 E.01854
G2 X98.119 Y115.656 I1.73 J3.567 E.01221
G1 X97.653 Y115.19 E.02036
G1 X97.401 Y115.907 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.563485
G1 F6915.569
G1 X97.133 Y116.138 E.01504
; LINE_WIDTH: 0.530024
G1 F7390.622
G1 X96.855 Y116.377 E.01454
; LINE_WIDTH: 0.499815
G1 F7879.273
G1 X96.664 Y116.549 E.00958
; LINE_WIDTH: 0.473624
G1 F8358.411
G1 X96.466 Y116.729 E.0094
; LINE_WIDTH: 0.443378
G1 F8989.705
G1 X95.723 Y117.454 E.03385
G1 X95.355 Y117.841 E.01743
; LINE_WIDTH: 0.474146
G1 F8348.291
G1 X95.182 Y118.031 E.00905
; LINE_WIDTH: 0.5004
G1 F7869.204
G1 X95.002 Y118.231 E.01004
; LINE_WIDTH: 0.530559
G1 F7382.519
G1 X94.771 Y118.5 E.01409
; LINE_WIDTH: 0.563479
G1 F6915.643
G1 X94.539 Y118.769 E.01504
; WIPE_START
G1 X94.771 Y118.5 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X96.224 Y125.993 Z1 F30000
G1 X99.044 Y140.53 Z1
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.409506
G1 F9820.339
G1 X98.956 Y140.794 E.00832
; LINE_WIDTH: 0.437957
G1 F9113.071
G1 X98.951 Y140.81 E.00055
G1 X99.004 Y140.883 E.00289
; LINE_WIDTH: 0.410976
G1 F9781.134
G1 X99.058 Y140.955 E.00269
; LINE_WIDTH: 0.375955
G1 F10809.699
G1 X99.189 Y141.117 E.00567
; LINE_WIDTH: 0.344097
G1 F11953.103
G1 X99.327 Y141.27 E.00506
; LINE_WIDTH: 0.318775
G1 F13050.366
G2 X99.477 Y141.41 I1.437 J-1.384 E.0046
G1 X99.638 Y141.542 E.00469
G1 X99.809 Y141.645 E.00448
; LINE_WIDTH: 0.283071
G1 F14990.577
G2 X99.992 Y141.732 I.699 J-1.236 E.00397
G1 X100.183 Y141.799 E.00396
; LINE_WIDTH: 0.244077
G1 F15000
G1 X100.381 Y141.839 E.00331
; LINE_WIDTH: 0.212722
G2 X100.579 Y141.86 I.27 J-1.616 E.00276
; LINE_WIDTH: 0.172728
G1 X100.777 Y141.859 E.0021
; LINE_WIDTH: 0.13367
G2 X100.973 Y141.833 I-.041 J-1.056 E.00146
; LINE_WIDTH: 0.101661
G1 X101.051 Y141.817 E.00038
; WIPE_START
G1 X100.973 Y141.833 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X101.918 Y140.962 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.19599
G1 F15000
G1 X102.055 Y141.103 E.00245
; LINE_WIDTH: 0.229327
G1 X102.192 Y141.243 E.00298
; LINE_WIDTH: 0.262663
G1 X102.329 Y141.384 E.00352
; WIPE_START
G1 X102.192 Y141.243 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X102.752 Y140.396 Z1 F30000
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.114043
G1 F15000
G1 X102.764 Y140.167 E.00133
; WIPE_START
G1 X102.752 Y140.396 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X105.126 Y133.142 Z1 F30000
G1 X115.068 Y102.768 Z1
G1 Z.6
G1 E.8 F1800
; LINE_WIDTH: 0.128673
G1 F15000
G2 X114.993 Y102.286 I-9.699 J1.261 E.00341
; CHANGE_LAYER
; Z_HEIGHT: 0.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X115.068 Y102.768 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 4/15
; update layer progress
M73 L4
M991 S0 P3 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z1 I-1.201 J.194 P1  F30000
G1 X126.041 Y170.647 Z1
G1 Z.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X125.839 Y170.624 E.00627
G3 X125.955 Y167.935 I.236 J-1.337 E.12011
G3 X126.19 Y167.934 I.12 J1.818 E.00722
G3 X126.101 Y170.644 I-.116 J1.353 E.12667
; WIPE_START
M204 S10000
G1 X125.839 Y170.624 E-.10007
G1 X125.609 Y170.568 E-.08995
G1 X125.394 Y170.468 E-.09011
G1 X125.199 Y170.332 E-.0901
G1 X125.032 Y170.164 E-.09013
G1 X124.841 Y169.864 E-.13491
G1 X124.771 Y169.677 E-.07586
G1 X124.727 Y169.448 E-.08887
; WIPE_END
G1 E-.04 F1800
G1 X128.297 Y166.093 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X128.273 Y165.99 E.00327
G3 X129.491 Y164.399 I1.337 J-.238 E.06922
G3 X129.726 Y164.399 I.12 J1.82 E.00722
G3 X128.335 Y166.218 I-.116 J1.353 E.17839
G1 X128.315 Y166.151 E.00216
; WIPE_START
M204 S10000
G1 X128.273 Y165.99 E-.06323
G1 X128.249 Y165.754 E-.08997
G1 X128.27 Y165.518 E-.09008
G1 X128.331 Y165.289 E-.09011
G1 X128.431 Y165.074 E-.09012
G1 X128.567 Y164.88 E-.09005
G1 X128.735 Y164.712 E-.09017
G1 X128.929 Y164.576 E-.09005
G1 X129.09 Y164.509 E-.06622
; WIPE_END
G1 E-.04 F1800
G1 X124 Y158.822 Z1.2 F30000
G1 X118.338 Y152.497 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G3 X119.09 Y152.34 I.697 J1.454 E.02571
G3 X120 Y152.754 I-.091 J1.409 E.03392
G1 X131.296 Y164.049 E.52989
G3 X131.508 Y164.319 I-1.097 J1.081 E.0114
G3 X131.552 Y165.711 I-1.215 J.736 E.0483
G1 X131.367 Y165.687 E.00622
G2 X129.457 Y167.5 I-1.75 J.069 E.26626
G1 X129.824 Y167.516 E.0122
G1 X127.836 Y169.505 E.09328
G2 X127.195 Y167.942 I-1.913 J-.128 E.058
G2 X126.007 Y171.047 I-1.119 J1.351 E.2208
G1 X126.031 Y171.233 E.00622
G3 X124.369 Y170.976 I-.657 J-1.257 E.05972
G1 X113.074 Y159.681 E.52989
G3 X112.817 Y158.019 I1 J-1.005 E.05971
G1 X113.003 Y158.043 E.00622
G2 X114.906 Y156.229 I1.751 J-.069 E.2665
G1 X114.538 Y156.221 E.01222
G1 X116.534 Y154.226 E.09363
G2 X117.29 Y155.876 I1.897 J.129 E.06279
G2 X118.363 Y152.683 I.999 J-1.441 E.21557
G1 X118.346 Y152.557 E.00423
; WIPE_START
G1 X118.525 Y152.42 E-.0854
G1 X118.76 Y152.357 E-.09263
G1 X119.09 Y152.34 E-.1254
G1 X119.364 Y152.384 E-.10569
G1 X119.593 Y152.467 E-.09251
G1 X119.804 Y152.589 E-.09264
G1 X120 Y152.754 E-.09742
G1 X120.127 Y152.881 E-.0683
; WIPE_END
G1 E-.04 F1800
G1 X116.998 Y154.817 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X116.967 Y154.713 E.00333
G3 X118.177 Y153.085 I1.329 J-.275 E.07037
G3 X118.412 Y153.085 I.12 J1.809 E.00722
G3 X117.067 Y155.013 I-.116 J1.353 E.17476
G1 X117.018 Y154.873 E.00456
; WIPE_START
M204 S10000
G1 X116.967 Y154.713 E-.06399
G1 X116.935 Y154.44 E-.10415
G1 X116.956 Y154.204 E-.09008
G1 X117.017 Y153.975 E-.09014
G1 X117.118 Y153.76 E-.0901
G1 X117.254 Y153.566 E-.09005
G1 X117.421 Y153.398 E-.09017
G1 X117.721 Y153.208 E-.13491
G1 X117.737 Y153.202 E-.00642
; WIPE_END
G1 E-.04 F1800
G1 X113.417 Y158.174 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X113.403 Y157.976 E.0061
G3 X114.642 Y156.621 I1.358 J-.003 E.06195
G3 X114.876 Y156.621 I.12 J1.818 E.00722
G3 X113.428 Y158.233 I-.116 J1.353 E.185
; WIPE_START
M204 S10000
G1 X113.403 Y157.976 E-.09815
G1 X113.438 Y157.661 E-.1206
G1 X113.527 Y157.401 E-.10424
G1 X113.646 Y157.196 E-.09014
G1 X113.798 Y157.014 E-.09003
G1 X113.98 Y156.862 E-.09012
G1 X114.185 Y156.743 E-.09008
G1 X114.375 Y156.674 E-.07664
; WIPE_END
G1 E-.04 F1800
G1 X118.176 Y152.152 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X118.249 Y152.117 E.00249
G3 X119.107 Y151.948 I.777 J1.684 E.02712
G3 X120.272 Y152.471 I-.108 J1.8 E.0401
G1 X131.579 Y163.778 E.49137
G3 X131.579 Y166.316 I-1.287 J1.269 E.08645
G1 X126.636 Y171.259 E.21482
G3 X124.098 Y171.259 I-1.269 J-1.269 E.08661
G1 X112.79 Y159.952 E.49136
G3 X112.79 Y157.414 I1.269 J-1.269 E.0866
G1 X117.734 Y152.471 E.21482
G3 X117.979 Y152.271 I1.293 J1.331 E.00973
G1 X118.125 Y152.183 E.00524
M204 S10000
G1 X118.152 Y152.588 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.174552
G1 F15000
G2 X117.493 Y153.054 I11.156 J16.481 E.00867
; LINE_WIDTH: 0.112351
G1 X117.321 Y153.197 E.00126
G1 X117.355 Y153.127 F30000
; LINE_WIDTH: 0.235447
G1 F15000
G1 X118.156 Y152.616 E.0149
G1 X118.159 Y152.636 F30000
; LINE_WIDTH: 0.306762
G1 F13644.555
G1 X117.417 Y153.065 E.01842
G1 X117.445 Y153.037 F30000
; LINE_WIDTH: 0.387774
G1 F10439.203
G3 X117.995 Y152.735 I4.425 J7.414 E.01763
G1 X118.191 Y152.884 E.00692
G1 X118.923 Y152.566 F30000
; LINE_WIDTH: 0.104933
G1 F15000
G1 X119.003 Y152.577 E.00041
; LINE_WIDTH: 0.143008
G3 X119.146 Y152.611 I-.421 J2.074 E.0012
G1 X119.151 Y152.613 E.00004
; LINE_WIDTH: 0.193437
G3 X119.313 Y152.67 I-.617 J2 E.00212
G1 X119.32 Y152.674 E.00009
; LINE_WIDTH: 0.242072
G3 X119.463 Y152.745 I-.746 J1.676 E.0026
G1 X119.544 Y152.796 E.00155
; LINE_WIDTH: 0.284607
G1 F14895.325
G3 X119.759 Y152.97 I-.721 J1.109 E.00545
G1 X120.005 Y153.237 E.00715
; LINE_WIDTH: 0.331285
G1 F12484.182
G1 X120.12 Y153.379 E.00431
; LINE_WIDTH: 0.365904
G1 F11146.088
G1 X120.179 Y153.46 E.00263
; LINE_WIDTH: 0.394193
G1 F10248.442
G1 X120.23 Y153.529 E.00247
; LINE_WIDTH: 0.424339
G1 F9438.458
G1 X120.385 Y153.76 E.00864
G1 X120.381 Y154.205 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X120.714 Y153.96 E.01372
G1 X121.564 Y154.81 E.03989
G1 X115.13 Y161.244 E.30184
G1 X118.968 Y165.082 E.18005
G1 X125.402 Y158.648 E.30184
G1 X129.24 Y162.486 E.18005
G1 X122.806 Y168.92 E.30184
G1 X123.656 Y169.77 E.03989
G1 X123.99 Y169.547 E.01334
G3 X128.104 Y168.744 I2.086 J-.251 E.20878
G1 X128.584 Y168.264 E.02251
G1 X115.786 Y155.466 E.60039
G1 X115.305 Y155.947 E.02255
G3 X116.135 Y156.389 I-.571 J2.071 E.03146
; WIPE_START
G1 X115.817 Y156.16 E-.14904
G1 X115.305 Y155.947 E-.21082
G1 X115.786 Y155.466 E-.25827
G1 X116.05 Y155.73 E-.14187
; WIPE_END
G1 E-.04 F1800
G1 X113.98 Y156.502 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.140402
G1 F15000
G3 X114.348 Y156.444 I1.47 J8.122 E.00296
; LINE_WIDTH: 0.099943
G1 X114.401 Y156.438 E.00025
G1 X114.213 Y156.411 F30000
; LINE_WIDTH: 0.185893
G1 F15000
G1 X114.071 Y156.506 E.00199
; LINE_WIDTH: 0.155911
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112342
G1 X113.786 Y156.732 E.00126
G1 X113.203 Y157.872 F30000
; LINE_WIDTH: 0.387836
G1 F10437.33
G1 X113.055 Y157.675 E.00692
G3 X113.358 Y157.124 I7.589 J3.811 E.01768
G1 X113.379 Y157.103 F30000
; LINE_WIDTH: 0.330538
G1 F12516.598
G1 X112.959 Y157.84 E.01988
G1 X112.939 Y157.837 F30000
; LINE_WIDTH: 0.237815
G1 F15000
G1 X113.439 Y157.043 E.0149
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.112775
G1 F15000
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.174727
G2 X112.907 Y157.833 I15.556 J11.492 E.00864
G1 X112.885 Y158.603 F30000
; LINE_WIDTH: 0.104951
G1 F15000
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.143642
G2 X112.931 Y158.826 I1.657 J-.316 E.00121
G1 X112.932 Y158.831 E.00004
; LINE_WIDTH: 0.19357
G2 X112.99 Y158.994 I2.256 J-.714 E.00212
G1 X112.993 Y159.001 E.00009
; LINE_WIDTH: 0.242061
G2 X113.065 Y159.144 I1.676 J-.746 E.0026
G1 X113.115 Y159.224 E.00154
; LINE_WIDTH: 0.284601
G1 F14895.698
G2 X113.289 Y159.439 I1.108 J-.72 E.00546
G1 X113.556 Y159.685 E.00714
; LINE_WIDTH: 0.332302
G1 F12440.332
G1 X113.706 Y159.806 E.00454
; LINE_WIDTH: 0.372225
G1 F10932.122
G1 X113.805 Y159.877 E.00326
; LINE_WIDTH: 0.409021
G1 F9833.36
G1 X113.89 Y159.938 E.00311
; LINE_WIDTH: 0.433704
G1 F9212.257
G1 X114.08 Y160.065 E.0073
; WIPE_START
G1 X113.89 Y159.938 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.809 Y153.673 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.164668
G1 F15000
G1 X116.776 Y153.89 E.00218
; LINE_WIDTH: 0.139083
G1 X116.757 Y154.03 E.00111
; LINE_WIDTH: 0.105812
G1 X116.749 Y154.125 E.00049
G1 X116.716 Y153.915 F30000
; LINE_WIDTH: 0.190491
G1 F15000
G1 X116.822 Y153.757 E.00229
; LINE_WIDTH: 0.15745
G1 X116.907 Y153.641 E.00134
; LINE_WIDTH: 0.112752
G1 X117.052 Y153.466 E.00129
; WIPE_START
G1 X116.907 Y153.641 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X123.017 Y158.214 Z1.2 F30000
G1 X130.292 Y163.659 Z1.2
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.406364
G1 F9905.245
M73 P52 R5
G3 X130.59 Y163.871 I-4.728 J6.992 E.01082
; LINE_WIDTH: 0.367918
G1 F11077
G1 X130.66 Y163.922 E.00229
; LINE_WIDTH: 0.33407
G1 F12364.772
G1 X130.804 Y164.037 E.00439
; LINE_WIDTH: 0.285111
G1 F14864.354
G3 X131.193 Y164.419 I-1.983 J2.407 E.01077
G1 X131.254 Y164.506 E.00209
; LINE_WIDTH: 0.24206
G1 F15000
G3 X131.376 Y164.73 I-1.08 J.733 E.00414
; LINE_WIDTH: 0.193593
G3 X131.437 Y164.899 I-2.858 J1.126 E.00221
; LINE_WIDTH: 0.143659
G3 X131.473 Y165.047 I-1.854 J.519 E.00125
; LINE_WIDTH: 0.104953
G1 X131.484 Y165.127 E.00041
G1 X131.166 Y165.858 F30000
; LINE_WIDTH: 0.387819
G1 F10437.861
G1 X131.315 Y166.055 E.00692
G3 X131.015 Y166.603 I-7.776 J-3.899 E.01757
G1 X130.986 Y166.632 F30000
; LINE_WIDTH: 0.306785
G1 F13643.357
G1 X131.413 Y165.891 E.0184
G1 X131.434 Y165.894 F30000
; LINE_WIDTH: 0.235346
G1 F15000
G1 X131.16 Y166.323 E.00799
; LINE_WIDTH: 0.220002
G1 X131.122 Y166.381 E.001
; LINE_WIDTH: 0.191884
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155929
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112352
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112751
G1 F15000
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157464
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.1905
G1 X130.135 Y167.334 E.00229
G1 X129.925 Y167.301 F30000
; LINE_WIDTH: 0.106119
G1 F15000
G1 X130.023 Y167.292 E.00051
; LINE_WIDTH: 0.154989
G2 X130.377 Y167.241 I-.95 J-7.751 E.00327
G1 X127.56 Y170.057 F30000
; LINE_WIDTH: 0.155023
G1 F15000
G2 X127.612 Y169.704 I-7.702 J-1.304 E.00327
; LINE_WIDTH: 0.10614
G1 X127.621 Y169.606 E.00051
G1 X127.653 Y169.815 F30000
; LINE_WIDTH: 0.190143
G1 F15000
G1 X127.544 Y169.978 E.00235
; LINE_WIDTH: 0.155948
G1 X127.46 Y170.092 E.0013
; LINE_WIDTH: 0.112367
G1 X127.318 Y170.264 E.00126
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.112751
G1 F15000
G1 X126.874 Y170.679 E.00129
; LINE_WIDTH: 0.157475
G1 X126.758 Y170.763 E.00134
; LINE_WIDTH: 0.193051
G1 X126.7 Y170.802 E.00085
; LINE_WIDTH: 0.233528
G3 X126.213 Y171.114 I-7.297 J-10.855 E.00898
G1 X126.211 Y171.095 F30000
; LINE_WIDTH: 0.286339
G1 F14789.318
G1 X126.961 Y170.657 E.01724
G1 X126.918 Y170.7 F30000
; LINE_WIDTH: 0.387131
G1 F10458.723
G3 X126.374 Y170.995 I-3.518 J-5.824 E.01737
G1 X126.178 Y170.844 E.00695
G1 X125.446 Y171.165 F30000
; LINE_WIDTH: 0.104947
G1 F15000
G1 X125.367 Y171.153 E.00041
; LINE_WIDTH: 0.143677
G3 X125.218 Y171.118 I.37 J-1.883 E.00125
; LINE_WIDTH: 0.193599
G3 X125.049 Y171.057 I.957 J-2.919 E.00221
; LINE_WIDTH: 0.242073
G3 X124.825 Y170.935 I.51 J-1.203 E.00415
; LINE_WIDTH: 0.285106
G1 F14864.654
G1 X124.739 Y170.873 E.0021
G3 X124.357 Y170.485 I2.025 J-2.371 E.01076
; LINE_WIDTH: 0.334066
G1 F12364.925
G1 X124.241 Y170.34 E.0044
; LINE_WIDTH: 0.367949
G1 F11075.943
G1 X124.19 Y170.27 E.00229
; LINE_WIDTH: 0.396768
G1 F10173.863
G1 X124.13 Y170.187 E.00296
; LINE_WIDTH: 0.425254
G1 F9415.871
G1 X123.984 Y169.97 E.00815
; OBJECT_ID: 795
; WIPE_START
G1 X124.13 Y170.187 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 795
M624 AQAAAAAAAAA=
G1 X129.322 Y164.593 Z1.2 F30000
G1 X147.017 Y145.531 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X147.147 Y145.603 E.00493
M73 P52 R4
G3 X146.055 Y145.302 I-.971 J1.394 E.31583
G3 X146.317 Y145.304 I.122 J1.495 E.0087
G3 X146.89 Y145.455 I-.141 J1.693 E.01973
G1 X146.966 Y145.5 E.00294
M204 S250
G1 X146.825 Y145.863 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.086 Y145.694 I-.65 J1.135 E.22876
G3 X146.283 Y145.695 I.091 J1.128 E.00608
G3 X146.773 Y145.835 I-.108 J1.303 E.01575
; WIPE_START
M204 S10000
G1 X147.011 Y145.996 E-.10945
G1 X147.173 Y146.158 E-.08681
G1 X147.318 Y146.372 E-.09843
G1 X147.4 Y146.552 E-.07507
G1 X147.459 Y146.773 E-.08679
G1 X147.479 Y147 E-.08677
G1 X147.453 Y147.258 E-.09845
G1 X147.4 Y147.448 E-.07505
G1 X147.348 Y147.549 E-.0432
; WIPE_END
G1 E-.04 F1800
G1 X151.089 Y140.896 Z1.2 F30000
G1 X151.48 Y140.2 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X151.446 Y140.196 E.00114
G3 X151.333 Y136.802 I.007 J-1.699 E.1728
G3 X151.595 Y136.804 I.122 J1.491 E.0087
G3 X151.741 Y140.172 I-.141 J1.693 E.16281
G1 X151.54 Y140.193 E.00671
M204 S250
G1 X151.446 Y139.805 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X151.363 Y137.194 I.006 J-1.307 E.12325
G3 X151.56 Y137.195 I.091 J1.125 E.00608
G3 X151.506 Y139.804 I-.108 J1.303 E.12125
; WIPE_START
M204 S10000
G1 X151.107 Y139.766 E-.1523
G1 X150.892 Y139.688 E-.08677
G1 X150.695 Y139.573 E-.0868
G1 X150.52 Y139.427 E-.08678
G1 X150.372 Y139.25 E-.0876
G1 X150.215 Y138.948 E-.12917
G1 X150.156 Y138.728 E-.08679
G1 X150.146 Y138.613 E-.04378
; WIPE_END
G1 E-.04 F1800
G1 X157.446 Y136.386 Z1.2 F30000
G1 X161.811 Y135.055 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X161.459 Y135.102 E.01178
G1 X150.433 Y135.102 E.36577
G3 X148.844 Y133.513 I.027 J-1.616 E.08241
G1 X148.844 Y130.487 E.1004
G3 X150.433 Y128.898 I1.616 J.027 E.08241
G1 X161.459 Y128.898 E.36578
G3 X163.048 Y130.487 I-.027 J1.616 E.08241
G1 X163.048 Y133.513 E.1004
G3 X161.87 Y135.042 I-1.616 J-.027 E.06861
M204 S250
G1 X161.759 Y134.667 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X161.451 Y134.71 I-.323 J-1.177 E.00958
G1 X150.441 Y134.71 E.33829
G3 X149.236 Y133.505 I.016 J-1.221 E.05798
G1 X149.236 Y130.495 E.09247
G3 X150.441 Y129.29 I1.221 J.016 E.05798
G1 X161.451 Y129.29 E.33829
G3 X162.656 Y130.495 I-.016 J1.221 E.05798
G1 X162.656 Y133.505 E.09247
G3 X161.816 Y134.649 I-1.221 J-.016 E.04655
; WIPE_START
M204 S10000
G1 X161.451 Y134.71 E-.14076
G1 X159.821 Y134.71 E-.61924
; WIPE_END
G1 E-.04 F1800
G1 X152.518 Y132.491 Z1.2 F30000
G1 X144.714 Y130.12 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X144.874 Y129.906 E.00888
G3 X146.055 Y129.302 I1.302 J1.091 E.0452
G3 X146.317 Y129.304 I.122 J1.491 E.0087
G3 X144.69 Y130.175 I-.141 J1.693 E.28939
M204 S250
G1 X145.041 Y130.349 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.086 Y129.694 I1.135 J.649 E.03946
G3 X146.283 Y129.695 I.091 J1.125 E.00608
G3 X145.012 Y130.401 I-.108 J1.303 E.20504
; WIPE_START
M204 S10000
G1 X145.167 Y130.156 E-.11008
G1 X145.418 Y129.927 E-.12919
G1 X145.615 Y129.813 E-.08678
G1 X145.83 Y129.735 E-.08678
G1 X146.086 Y129.694 E-.09843
G1 X146.283 Y129.695 E-.07506
G1 X146.508 Y129.735 E-.08679
G1 X146.723 Y129.813 E-.08676
G1 X146.723 Y129.813 E-.00012
; WIPE_END
G1 E-.04 F1800
G1 X145.292 Y137.31 Z1.2 F30000
G1 X143.409 Y147.176 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X143.385 Y147.202 E.00114
G3 X141.682 Y148.102 I-1.735 J-1.22 E.06633
G1 X134.611 Y148.102 E.23459
G3 X132.762 Y145.023 I.026 J-2.11 E.14249
G1 X133.298 Y144.104 E.0353
G2 X134.245 Y141.629 I-10.9 J-5.59 E.08805
G2 X133.996 Y135.521 I-10.788 J-2.621 E.20544
G2 X132.762 Y132.977 I-11.992 J4.248 E.09399
G3 X134.611 Y129.898 I1.875 J-.969 E.14249
G1 X141.682 Y129.898 E.23459
G3 X143.771 Y131.987 I-.028 J2.116 E.10845
G1 X143.771 Y146.013 E.46529
G3 X143.569 Y146.886 I-2.121 J-.032 E.02994
G1 X143.438 Y147.124 E.00902
M204 S250
G1 X143.065 Y146.977 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X141.674 Y147.71 I-1.411 J-.993 E.05016
G1 X134.619 Y147.71 E.21678
G3 X133.109 Y145.206 I.016 J-1.717 E.10753
G1 X133.644 Y144.287 E.03266
G2 X134.625 Y141.724 I-11.293 J-5.792 E.0845
G2 X134.368 Y135.396 I-11.18 J-2.715 E.19715
G2 X133.109 Y132.795 I-12.327 J4.361 E.08898
G3 X134.619 Y130.29 I1.517 J-.793 E.10773
G1 X141.674 Y130.29 E.21678
G3 X143.379 Y131.995 I-.017 J1.722 E.08209
G1 X143.379 Y146.005 E.43047
G3 X143.099 Y146.928 I-1.725 J-.02 E.03004
; WIPE_START
M204 S10000
G1 X142.878 Y147.209 E-.13586
G1 X142.65 Y147.401 E-.11331
G1 X142.392 Y147.55 E-.11327
G1 X142.112 Y147.652 E-.11325
G1 X141.966 Y147.684 E-.05672
G1 X141.674 Y147.71 E-.1115
G1 X141.368 Y147.71 E-.1161
; WIPE_END
G1 E-.04 F1800
G1 X134.494 Y144.393 Z1.2 F30000
G1 X114.506 Y134.746 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X114.517 Y134.732 E.00058
G3 X122.789 Y128.936 I9.154 J4.264 E.35087
G1 X123.063 Y128.924 E.00912
G3 X131.945 Y133.205 I.621 J10.065 E.34173
G1 X132.418 Y133.949 E.02924
G3 X114.18 Y135.546 I-8.747 J5.047 E1.34448
G1 X114.484 Y134.802 E.02667
M204 S250
G1 X114.872 Y134.898 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X122.823 Y129.327 I8.799 J4.098 E.31239
G1 X123.08 Y129.316 E.00792
G3 X131.623 Y133.43 I.603 J9.674 E.30445
G1 X132.078 Y134.145 E.02604
G3 X114.847 Y134.953 I-8.407 J4.851 E1.22122
; WIPE_START
M204 S10000
G1 X115.26 Y134.145 E-.34455
G1 X115.715 Y133.43 E-.32198
G1 X115.865 Y133.235 E-.09348
; WIPE_END
G1 E-.04 F1800
G1 X121.532 Y138.347 Z1.2 F30000
G1 X157.675 Y170.946 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X156.834 Y170.749 E.02866
G3 X158.566 Y150.936 I2.612 J-9.754 E.93542
G1 X158.84 Y150.924 E.00912
G1 X159.446 Y150.897 E.02012
G3 X157.734 Y170.947 I0 J10.098 E1.10941
M204 S250
G1 X157.762 Y170.554 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X158.6 Y151.327 I1.685 J-9.558 E.85884
G1 X158.857 Y151.316 E.00792
G1 X159.446 Y151.29 E.01811
G3 X157.821 Y170.564 I0 J9.706 E.98709
; WIPE_START
M204 S10000
G1 X156.933 Y170.379 E-.34458
G1 X156.125 Y170.125 E-.32186
G1 X155.898 Y170.03 E-.09356
; WIPE_END
G1 E-.04 F1800
G1 X159.847 Y163.499 Z1.2 F30000
G1 X166.722 Y152.127 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.689 Y152.133 E.00111
G3 X165.469 Y151.907 I-.245 J-2.09 E.04179
G1 X164.549 Y151.371 E.0353
G2 X155.967 Y150.673 I-5.103 J9.629 E.29363
G2 X153.423 Y151.907 I4.247 J11.991 E.09399
G3 X150.509 Y150.859 I-.969 J-1.881 E.11527
G3 X150.374 Y150.404 I2.086 J-.865 E.01576
G3 X150.344 Y149.326 I6.153 J-.712 E.03583
G3 X151.654 Y147.391 I2.137 J.037 E.082
G1 X165.678 Y141.789 E.50094
G3 X166.227 Y141.656 I.792 J2.069 E.01877
G3 X168.548 Y143.733 I.206 J2.105 E.11614
M73 P53 R4
G1 X168.548 Y150.058 E.20983
G3 X167.041 Y152.061 I-2.104 J-.016 E.08904
G1 X166.781 Y152.115 E.00881
M204 S250
G1 X166.644 Y151.743 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X165.652 Y151.56 I-.2 J-1.7 E.03147
G1 X164.733 Y151.025 E.03266
G2 X155.842 Y150.301 I-5.287 J9.976 E.28179
G2 X153.241 Y151.56 I4.36 J12.326 E.08898
G3 X150.761 Y150.337 I-.793 J-1.518 E.09888
G3 X150.736 Y149.334 I5.786 J-.645 E.03087
G3 X151.808 Y147.752 I1.74 J.024 E.06215
G1 X165.816 Y142.156 E.46351
G3 X166.272 Y142.045 I.65 J1.687 E.01446
G3 X168.156 Y143.741 I.164 J1.713 E.08756
G1 X168.156 Y150.05 E.19386
G3 X166.703 Y151.735 I-1.712 J-.007 E.07442
; WIPE_START
M204 S10000
G1 X166.498 Y151.755 E-.07833
G1 X166.352 Y151.753 E-.05564
G1 X166.062 Y151.712 E-.11107
G1 X165.784 Y151.623 E-.11108
G1 X165.652 Y151.56 E-.05569
G1 X164.86 Y151.099 E-.34819
; WIPE_END
G1 E-.04 F1800
G1 X166.304 Y143.604 Z1.2 F30000
G1 X166.973 Y140.133 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.725 Y140.032 E.00888
G3 X167.333 Y136.802 I.729 J-1.535 E.14807
G3 X167.595 Y136.804 I.122 J1.491 E.0087
G3 X167.032 Y140.143 I-.141 J1.693 E.18652
M204 S250
G1 X167.109 Y139.759 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X167.363 Y137.194 I.344 J-1.261 E.11276
G3 X167.56 Y137.195 I.091 J1.125 E.00608
G3 X167.167 Y139.774 I-.108 J1.303 E.13175
; WIPE_START
M204 S10000
G1 X166.89 Y139.687 E-.11011
G1 X166.695 Y139.573 E-.08598
G1 X166.52 Y139.427 E-.08679
G1 X166.312 Y139.155 E-.12995
G1 X166.214 Y138.946 E-.08761
G1 X166.156 Y138.728 E-.086
G1 X166.136 Y138.5 E-.08678
G1 X166.166 Y138.274 E-.08677
; WIPE_END
G1 E-.04 F1800
G1 X158.791 Y140.238 Z1.2 F30000
G1 X128.082 Y148.419 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X127.169 Y148.791 E.03272
G3 X123.387 Y128.606 I-3.493 J-9.792 E1.19205
G1 X158.73 Y127.603 E1.17285
G1 X159.016 Y127.615 E.0095
G1 X159.707 Y127.644 E.02295
G3 X170.125 Y138.631 I-1.003 J11.384 E.54897
G1 X169.843 Y161.118 E.74599
; object ids of layer 4 start: 795,817,839,861
M624 DwAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer4 end: 795,817,839,861
M625
G3 X149.447 Y158.151 I-10.396 J-.124 E1.17487
G1 X149.877 Y156.852 E.04541
G2 X147.433 Y150.558 I-5.413 J-1.519 E.24025
G1 X145.26 Y149.222 E.08462
G2 X142.347 Y148.398 I-2.959 J4.9 E.10161
G1 X128.138 Y148.398 E.47134
M204 S250
G1 X128.211 Y148.79 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X123.367 Y128.214 I-4.532 J-9.791 E1.17566
G1 X158.732 Y127.21 E1.08711
G1 X159.032 Y127.223 E.00922
G1 X159.74 Y127.253 E.02178
G3 X170.518 Y138.618 I-1.038 J11.776 E.52604
G1 X170.235 Y161.131 E.6918
G3 X149.069 Y158.044 I-10.788 J-.138 E1.12902
G1 X149.5 Y156.745 E.04205
G2 X147.22 Y150.888 I-5.035 J-1.413 E.20718
G1 X145.061 Y149.56 E.07789
G2 X142.339 Y148.79 I-2.759 J4.558 E.08795
G1 X128.271 Y148.79 E.4323
M204 S10000
G1 X128.393 Y148.185 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.331188
G1 F12488.394
G1 X129.207 Y147.967 E.0198
G1 X131.546 Y147.111 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.58492
G1 F6642.067
G2 X131.55 Y147.221 I-.029 J.056 E.01173
G1 X132.28 Y147.629 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X132.028 Y147.227 E.01459
G1 X131.857 Y146.767 E.01508
G1 X131.766 Y146.242 E.01635
G1 X131.374 Y146.67 E.01782
G1 X130.676 Y147.312 E.02914
G1 X130.249 Y147.629 E.01632
G1 X132.22 Y147.629 E.06056
G1 X132.896 Y147.788 F30000
G1 F9547.299
G1 X132.727 Y147.619 E.00733
G1 X132.398 Y147.125 E.01825
G3 X132.155 Y145.694 I2.354 J-1.135 E.0452
G1 X131.87 Y145.537 E.01002
G3 X130.421 Y147.034 I-8.806 J-7.067 E.06411
G3 X129.537 Y147.684 I-269.874 J-366.676 E.03372
G1 X129.623 Y148.006 E.01025
G1 X132.827 Y148.006 E.09845
G1 X132.826 Y147.873 E.00408
G1 X132.858 Y147.834 E.00155
G1 X133.297 Y147.917 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.120985
G1 F15000
G1 X133.464 Y148.052 E.00137
; LINE_WIDTH: 0.165392
G1 X133.654 Y148.194 E.00237
G1 X133.791 Y148.173 F30000
; LINE_WIDTH: 0.133892
G1 F15000
G3 X133.438 Y148.099 I1.585 J-8.51 E.00268
; WIPE_START
G1 X133.791 Y148.173 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.17 Y145.255 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.474748
G1 F8336.654
G1 X132.397 Y144.842 E.01659
; LINE_WIDTH: 0.431336
G1 F9268.417
G3 X132.754 Y144.255 I13.437 J7.779 E.02174
G2 X132.406 Y133.174 I-9.076 J-5.261 E.36969
; LINE_WIDTH: 0.473823
G1 F8354.554
G1 X132.17 Y132.746 E.01718
G1 X131.628 Y132.524 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X132.196 Y131.956 E.02478
G3 X132.281 Y131.335 I1.839 J-.063 E.01943
G1 X131.501 Y132.115 E.03402
G1 X131.245 Y131.835 E.01169
G1 X134.456 Y128.625 E.14006
G1 X135.007 Y128.609 E.01701
G1 X133.956 Y129.66 E.04585
G3 X134.586 Y129.566 I.665 J2.28 E.01971
G1 X135.558 Y128.594 E.04241
G1 X136.109 Y128.578 E.01701
G1 X135.122 Y129.565 E.04305
G1 X135.657 Y129.565 E.01652
G1 X136.66 Y128.562 E.04373
G1 X137.211 Y128.547 E.01701
G1 X136.193 Y129.565 E.04442
G1 X136.728 Y129.565 E.01652
G1 X137.762 Y128.531 E.0451
G1 X138.313 Y128.515 E.01701
G1 X137.264 Y129.565 E.04578
G1 X137.799 Y129.565 E.01652
G1 X138.864 Y128.5 E.04646
G1 X139.415 Y128.484 E.01701
G1 X138.334 Y129.565 E.04715
G1 X138.87 Y129.565 E.01652
G1 X139.966 Y128.469 E.04783
G1 X140.517 Y128.453 E.01701
G1 X139.405 Y129.565 E.04851
G1 X139.94 Y129.565 E.01652
G1 X141.068 Y128.437 E.04919
G1 X141.619 Y128.422 E.01701
G1 X140.476 Y129.565 E.04988
G1 X141.011 Y129.565 E.01652
G1 X142.17 Y128.406 E.05056
G1 X142.721 Y128.39 E.01701
G1 X141.547 Y129.565 E.05124
G3 X142.05 Y129.596 I.075 J2.84 E.01559
G1 X143.272 Y128.375 E.0533
G1 X143.823 Y128.359 E.01701
G1 X142.473 Y129.709 E.0589
G3 X142.848 Y129.87 I-.424 J1.505 E.01261
G1 X144.374 Y128.343 E.06659
G1 X144.925 Y128.328 E.01701
G1 X143.167 Y130.085 E.07668
G3 X143.447 Y130.342 I-1.072 J1.448 E.01171
G1 X145.476 Y128.312 E.08854
G1 X146.027 Y128.296 E.01701
G1 X143.562 Y130.762 E.10756
G1 X144.095 Y131.189 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.382549
G1 F10599.811
G1 X144.254 Y130.982 E.00723
G1 X144.095 Y131.189 F30000
; LINE_WIDTH: 0.413801
G1 F9706.615
G1 X144.08 Y131.21 E.00077
; LINE_WIDTH: 0.449156
G1 F8861.861
G1 X144.065 Y131.23 E.00085
; LINE_WIDTH: 0.450691
G1 F8828.487
G1 X144.168 Y131.695 E.0158
G1 X144.195 Y131.71 E.00105
; LINE_WIDTH: 0.407986
G1 F9861.234
G1 X144.447 Y131.838 E.00838
G1 X144.293 Y132.172 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X144.104 Y132.361 E.00825
G1 X144.104 Y132.897 E.01652
G1 X144.65 Y132.351 E.02382
G2 X144.928 Y132.608 I.896 J-.687 E.01174
G1 X144.104 Y133.432 E.03595
G1 X144.103 Y133.968 E.01652
G1 X145.259 Y132.812 E.05044
G2 X145.646 Y132.961 I.584 J-.939 E.01285
G1 X144.103 Y134.504 E.06731
G1 X144.103 Y135.039 E.01652
G1 X146.11 Y133.032 E.08758
G2 X146.696 Y132.968 I.078 J-1.991 E.01826
G1 X146.717 Y132.96 E.00069
G1 X143.933 Y135.745 E.12149
; WIPE_START
G1 X145.347 Y134.331 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.649 Y129.211 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X146.578 Y128.281 E.04056
G1 X147.129 Y128.265 E.01701
G1 X146.408 Y128.987 E.03148
G1 X146.517 Y128.992 E.00337
G1 X146.849 Y129.081 E.0106
G1 X147.68 Y128.25 E.03629
G1 X148.231 Y128.234 E.01701
G1 X147.212 Y129.253 E.04446
G1 X147.52 Y129.481 E.01181
G1 X148.782 Y128.218 E.05508
G1 X149.333 Y128.203 E.01701
G1 X147.655 Y129.881 E.07324
; WIPE_START
G1 X149.069 Y128.467 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X156.699 Y128.644 Z1.2 F30000
G1 X160.58 Y128.735 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X160.831 Y128.483 E.01096
G1 X160.627 Y128.174 E.01142
G1 X160.712 Y128.118 E.00313
G1 X160.67 Y128.109 E.00134
G1 X160.214 Y128.565 E.01988
G1 X159.679 Y128.565 E.01652
G1 X160.2 Y128.044 E.02273
G1 X159.726 Y127.983 E.01475
G1 X159.143 Y128.565 E.0254
G1 X158.608 Y128.565 E.01652
G1 X159.216 Y127.957 E.02653
G2 X158.701 Y127.937 I-1.123 J22.14 E.01591
G1 X158.073 Y128.565 E.02741
G1 X157.537 Y128.565 E.01652
G1 X158.15 Y127.952 E.02672
G1 X157.599 Y127.968 E.01701
G1 X157.002 Y128.565 E.02604
G1 X156.466 Y128.565 E.01652
G1 X157.048 Y127.984 E.02536
G1 X156.497 Y127.999 E.01701
M73 P54 R4
G1 X155.931 Y128.565 E.02468
G1 X155.396 Y128.565 E.01652
G1 X155.946 Y128.015 E.02399
G1 X155.395 Y128.031 E.01701
G1 X154.86 Y128.565 E.02331
G1 X154.325 Y128.565 E.01652
G1 X154.844 Y128.046 E.02263
G1 X154.293 Y128.062 E.01701
G1 X153.79 Y128.565 E.02195
G1 X153.254 Y128.565 E.01652
G1 X153.742 Y128.077 E.02126
G1 X153.191 Y128.093 E.01701
G1 X152.719 Y128.565 E.02058
G1 X152.183 Y128.565 E.01652
G1 X152.64 Y128.109 E.0199
G1 X152.089 Y128.124 E.01701
G1 X151.648 Y128.565 E.01922
G1 X151.113 Y128.565 E.01652
G1 X151.537 Y128.14 E.01853
G1 X150.986 Y128.156 E.01701
G1 X150.577 Y128.565 E.01785
G2 X149.986 Y128.621 I-.083 J2.27 E.01838
G1 X150.435 Y128.171 E.01962
G1 X149.884 Y128.187 E.01701
G1 X147.982 Y130.089 E.08298
G1 X148.136 Y130.47 E.01269
G1 X148.568 Y130.039 E.01884
G2 X148.516 Y130.626 I1.658 J.443 E.01828
G1 X148.198 Y130.944 E.01386
G3 X148.129 Y131.548 I-2.502 J.02 E.01882
G1 X148.515 Y131.162 E.01684
G1 X148.514 Y131.699 E.01654
G1 X144.102 Y136.111 E.19248
G1 X144.102 Y136.646 E.01652
G1 X148.513 Y132.235 E.19245
G1 X148.512 Y132.771 E.01654
G1 X144.102 Y137.182 E.19242
G1 X144.101 Y137.718 E.01652
G1 X148.511 Y133.308 E.19239
G2 X148.537 Y133.818 I2.799 J.115 E.01577
G1 X144.101 Y138.253 E.19352
G1 X144.101 Y138.789 E.01652
G1 X148.658 Y134.232 E.19882
G2 X148.842 Y134.583 I1.425 J-.524 E.01227
G1 X144.1 Y139.325 E.20688
G1 X144.1 Y139.86 E.01652
G1 X149.085 Y134.876 E.21745
G2 X149.384 Y135.112 I1.046 J-1.018 E.01179
G1 X144.1 Y140.396 E.23052
G1 X144.1 Y140.932 E.01652
G1 X149.736 Y135.295 E.2459
G2 X150.164 Y135.402 I.459 J-.926 E.01373
G1 X144.099 Y141.467 E.2646
G1 X144.099 Y142.003 E.01652
G1 X150.667 Y135.435 E.28653
G1 X151.202 Y135.435 E.01652
G1 X144.099 Y142.539 E.30991
G1 X144.098 Y143.074 E.01652
G1 X151.738 Y135.435 E.33329
G1 X152.274 Y135.434 E.01652
G1 X151.226 Y136.482 E.04571
G1 X151.314 Y136.468 E.00276
G1 X151.753 Y136.49 E.01356
G1 X152.809 Y135.434 E.04608
G1 X153.345 Y135.434 E.01652
G1 X152.177 Y136.602 E.05095
G3 X152.532 Y136.783 I-.336 J1.095 E.01234
G1 X153.881 Y135.434 E.05886
G1 X154.416 Y135.433 E.01652
G1 X152.833 Y137.017 E.06908
G3 X153.084 Y137.301 I-.681 J.854 E.01176
G1 X154.952 Y135.433 E.0815
G1 X155.488 Y135.433 E.01652
G1 X153.283 Y137.637 E.09618
G3 X153.424 Y138.032 I-1.429 J.734 E.01295
G1 X156.023 Y135.433 E.11339
G1 X156.559 Y135.432 E.01652
G1 X153.482 Y138.509 E.13421
G3 X153.372 Y139.155 I-1.89 J.008 E.02033
G1 X157.095 Y135.432 E.16242
G1 X157.63 Y135.432 E.01652
G1 X147.55 Y145.512 E.43975
G3 X147.802 Y145.796 I-.621 J.801 E.01177
G1 X158.166 Y135.431 E.45216
G1 X158.702 Y135.431 E.01652
G1 X148 Y146.133 E.46687
G1 X148.146 Y146.523 E.01284
G1 X159.237 Y135.431 E.48389
G1 X159.773 Y135.431 E.01652
G1 X148.198 Y147.005 E.50496
G3 X148.101 Y147.638 I-2.231 J-.02 E.01982
G1 X160.308 Y135.43 E.53258
G1 X160.844 Y135.43 E.01652
G1 X146.612 Y149.662 E.6209
G1 X146.943 Y149.866 E.01201
G1 X161.38 Y135.43 E.62981
G2 X161.994 Y135.351 I.096 J-1.685 E.01921
G1 X147.275 Y150.07 E.64214
G1 X147.607 Y150.274 E.01201
G1 X166.624 Y131.256 E.82968
G1 X166.885 Y131.531 E.01168
G1 X147.926 Y150.49 E.8271
G3 X148.229 Y150.722 I-1.19 J1.863 E.01179
G1 X150.051 Y148.9 E.07948
G2 X150.012 Y149.474 I4.613 J.599 E.01776
G1 X148.516 Y150.97 E.06525
G1 X148.789 Y151.233 E.01168
G1 X150.016 Y150.006 E.05355
G2 X150.06 Y150.497 I1.516 J.113 E.01529
G1 X149.038 Y151.519 E.04458
G3 X149.272 Y151.82 I-1.624 J1.504 E.01178
G1 X150.176 Y150.916 E.03943
G2 X150.349 Y151.28 I2.595 J-1.008 E.01241
G1 X149.491 Y152.137 E.03742
G1 X149.693 Y152.471 E.01203
G1 X150.567 Y151.596 E.03816
G2 X150.833 Y151.866 I1.3 J-1.012 E.0117
G1 X149.87 Y152.829 E.04202
G3 X150.027 Y153.207 I-2.099 J1.098 E.01264
G1 X151.141 Y152.094 E.04857
G2 X151.49 Y152.279 I.711 J-.919 E.01228
G1 X150.164 Y153.606 E.05788
G3 X150.276 Y154.029 I-2.388 J.86 E.01352
G1 X151.89 Y152.415 E.0704
G2 X152.368 Y152.472 I.483 J-2.008 E.01489
G1 X150.36 Y154.48 E.08759
G3 X150.41 Y154.965 I-2.776 J.532 E.01507
G1 X152.834 Y152.541 E.10576
G1 X152.986 Y152.815 E.00966
G2 X150.899 Y155.012 I6.221 J7.999 E.09382
G1 X150.634 Y155.277 E.01157
G1 X150.518 Y155.413 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.243791
G1 F15000
G1 X150.361 Y155.938 E.00897
; LINE_WIDTH: 0.217934
G1 X150.313 Y156.085 E.00221
; LINE_WIDTH: 0.16953
G1 X150.265 Y156.233 E.0016
; LINE_WIDTH: 0.121126
G1 X150.218 Y156.38 E.00099
G1 X150.224 Y156.382 F30000
; LINE_WIDTH: 0.310249
G1 F13466.566
G1 X150.516 Y155.412 E.02206
G1 X153.192 Y152.499 F30000
; LINE_WIDTH: 0.474747
G1 F8336.677
G1 X153.605 Y152.272 E.01659
; LINE_WIDTH: 0.431334
G1 F9268.458
G3 X165.272 Y152.263 I5.84 J8.741 E.39147
; LINE_WIDTH: 0.47381
G1 F8354.817
G1 X165.701 Y152.499 E.01718
G1 X165.807 Y152.953 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X166.285 Y152.475 E.02085
G1 X166.728 Y152.466 E.01367
G1 X166.855 Y152.44 E.004
G1 X166.105 Y153.191 E.03273
; WIPE_START
G1 X166.855 Y152.44 E-.40315
G1 X166.728 Y152.466 E-.04926
G1 X166.285 Y152.475 E-.16845
G1 X166.026 Y152.734 E-.13914
; WIPE_END
G1 E-.04 F1800
G1 X168.998 Y157.258 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X169.566 Y156.69 E.02479
G1 X169.573 Y156.148 E.01673
G1 X168.971 Y156.749 E.02626
G2 X168.799 Y156.386 I-2.163 J.802 E.01242
G1 X169.579 Y155.605 E.03406
G1 X169.586 Y155.063 E.01673
G1 X168.615 Y156.034 E.04236
G2 X168.425 Y155.689 I-2.066 J.915 E.01217
G1 X169.593 Y154.521 E.05096
G1 X169.6 Y153.979 E.01673
G1 X168.217 Y155.362 E.06034
G1 X168.008 Y155.035 E.01196
G1 X169.607 Y153.437 E.06973
G1 X169.613 Y152.894 E.01673
G1 X167.777 Y154.731 E.0801
G1 X167.545 Y154.428 E.01178
G1 X169.62 Y152.352 E.09054
G1 X169.627 Y151.81 E.01673
G1 X167.299 Y154.138 E.10154
G1 X167.043 Y153.858 E.01169
G1 X169.634 Y151.268 E.11301
G1 X169.641 Y150.726 E.01673
G1 X166.784 Y153.582 E.12463
G1 X166.505 Y153.326 E.01169
G1 X169.647 Y150.184 E.13711
G1 X169.654 Y149.641 E.01673
G1 X168.839 Y150.456 E.03555
G2 X168.875 Y149.886 I-1.645 J-.388 E.01773
G1 X169.661 Y149.099 E.0343
G1 X169.668 Y148.557 E.01673
G1 X168.875 Y149.35 E.03457
G1 X168.876 Y148.814 E.01653
G1 X169.675 Y148.015 E.03485
G1 X169.681 Y147.473 E.01673
G1 X168.876 Y148.278 E.03512
G1 X168.877 Y147.742 E.01653
G1 X169.688 Y146.931 E.03539
G1 X169.695 Y146.388 E.01673
G1 X168.878 Y147.206 E.03566
G1 X168.878 Y146.67 E.01653
G1 X169.702 Y145.846 E.03593
G1 X169.709 Y145.304 E.01673
G1 X168.879 Y146.134 E.0362
G1 X168.879 Y145.598 E.01653
G1 X169.715 Y144.762 E.03647
G1 X169.722 Y144.22 E.01673
G1 X168.88 Y145.062 E.03674
G1 X168.881 Y144.526 E.01653
G1 X169.729 Y143.677 E.03701
G1 X169.736 Y143.135 E.01673
G1 X168.881 Y143.99 E.03728
G2 X168.86 Y143.475 I-2.946 J-.139 E.01591
G1 X169.743 Y142.593 E.03849
G1 X169.749 Y142.051 E.01673
G1 X168.769 Y143.031 E.04275
G2 X168.616 Y142.649 I-1.19 J.258 E.01275
G1 X169.756 Y141.509 E.04976
G1 X169.763 Y140.967 E.01673
G1 X168.412 Y142.318 E.05894
G2 X168.168 Y142.026 I-1.549 J1.05 E.01174
G1 X169.77 Y140.424 E.06988
G1 X169.776 Y139.882 E.01673
G1 X167.881 Y141.778 E.08269
G1 X167.55 Y141.573 E.012
G1 X169.783 Y139.34 E.09743
G1 X169.79 Y138.798 E.01673
G1 X167.163 Y141.416 E.11442
G2 X166.726 Y141.327 I-.568 J1.661 E.0138
G1 X167.523 Y140.529 E.03478
G3 X167.03 Y140.487 I-.127 J-1.422 E.01535
G1 X166.193 Y141.324 E.03649
G2 X165.468 Y141.514 I.471 J3.278 E.02318
G1 X166.622 Y140.36 E.05036
G1 X166.579 Y140.344 E.00142
G3 X166.278 Y140.168 I.533 J-1.258 E.01077
G1 X164.577 Y141.87 E.07425
G1 X163.685 Y142.226 E.02962
G1 X165.994 Y139.917 E.10072
G3 X165.754 Y139.622 I.719 J-.827 E.0118
G1 X162.793 Y142.582 E.12916
G1 X161.902 Y142.938 E.02962
G1 X165.568 Y139.273 E.15992
G3 X165.442 Y138.863 I1.089 J-.556 E.0133
G1 X161.01 Y143.295 E.19336
G1 X160.119 Y143.651 E.02962
G1 X165.62 Y138.15 E.23998
; WIPE_START
G1 X164.205 Y139.564 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.286 Y138.766 Z1.2 F30000
M73 P55 R4
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X169.765 Y138.287 E.0209
G1 X169.728 Y137.789 E.0154
G1 X169.433 Y138.084 E.01285
G2 X169.306 Y137.676 I-1.219 J.157 E.01325
G1 X169.66 Y137.322 E.01545
G1 X169.585 Y136.861 E.0144
G1 X169.11 Y137.337 E.02076
G2 X168.863 Y137.048 I-.935 J.546 E.01178
G1 X169.485 Y136.426 E.0271
G1 X169.377 Y135.998 E.01361
G1 X168.568 Y136.808 E.03532
G2 X168.219 Y136.621 I-.703 J.895 E.01226
G1 X169.25 Y135.59 E.045
G1 X169.113 Y135.192 E.01299
G1 X167.809 Y136.496 E.05692
G1 X167.299 Y136.47 E.01573
G1 X168.965 Y134.804 E.07268
G1 X168.801 Y134.433 E.01252
G1 X159.227 Y144.007 E.41766
G1 X158.336 Y144.363 E.02962
G1 X168.635 Y134.064 E.4493
G1 X168.445 Y133.719 E.01216
G1 X157.444 Y144.719 E.47991
G1 X156.553 Y145.075 E.02962
G1 X168.255 Y133.373 E.51052
G2 X168.048 Y133.044 I-2.022 J1.039 E.012
G1 X155.661 Y145.432 E.54042
G1 X154.77 Y145.788 E.02962
G1 X167.834 Y132.723 E.56997
G2 X167.615 Y132.407 I-1.952 J1.123 E.01188
G1 X153.878 Y146.144 E.59929
G1 X152.986 Y146.5 E.02962
G1 X167.377 Y132.109 E.62782
G1 X167.14 Y131.812 E.01175
G1 X151.791 Y147.16 E.66962
G1 X147.168 Y148.57 F30000
G1 F9509.47
G1 X146.157 Y149.582 E.04412
G1 X145.799 Y149.056 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.394049
G1 F10252.658
G1 X146.025 Y148.911 E.0077
G1 X145.799 Y149.056 F30000
; LINE_WIDTH: 0.417163
G1 F9619.43
G1 X145.778 Y149.068 E.00072
G1 X145.638 Y149.011 E.00462
; LINE_WIDTH: 0.366216
G1 F11135.315
G1 X145.46 Y148.93 E.00516
; LINE_WIDTH: 0.323999
G1 F12807.824
G1 X144.988 Y148.676 E.01227
; LINE_WIDTH: 0.351176
G1 F11678.606
G1 X144.833 Y148.582 E.00456
; LINE_WIDTH: 0.395976
G1 F10196.699
G1 X144.698 Y148.492 E.00465
G1 X144.684 Y148.211 E.00809
G1 X144.254 Y147.018 F30000
; LINE_WIDTH: 0.38249
G1 F10601.658
G1 X144.095 Y146.811 E.00723
; LINE_WIDTH: 0.413757
G1 F9707.777
G1 X144.08 Y146.79 E.00077
; LINE_WIDTH: 0.44913
G1 F8862.426
G1 X144.065 Y146.77 E.00085
; LINE_WIDTH: 0.450714
G1 F8828.003
G1 X144.168 Y146.305 E.01581
G1 X144.195 Y146.291 E.00104
; LINE_WIDTH: 0.41033
G1 F9798.322
G1 X144.445 Y146.164 E.00837
G1 X143.387 Y148.043 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.55467
G1 F7034.685
G3 X144.025 Y148.189 I-.453 J3.449 E.02732
G1 X144.032 Y147.94 E.01037
G1 X144.123 Y147.82 E.0063
G1 X144.184 Y147.799 E.00269
G1 X144.121 Y147.661 E.00632
G1 X143.927 Y147.636 E.00815
G1 X143.756 Y147.459 E.0103
G3 X143.346 Y147.908 I-1.16 J-.645 E.0256
G1 X143.397 Y147.985 E.00384
G1 X142.855 Y148.007 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.109661
G1 F15000
G1 X142.764 Y148.071 E.0006
; LINE_WIDTH: 0.138482
G1 X142.656 Y148.148 E.00104
G1 X142.698 Y148.208 E.00057
; WIPE_START
G1 X142.656 Y148.148 E-.27014
G1 X142.764 Y148.071 E-.48986
; WIPE_END
G1 E-.04 F1800
G1 X143.928 Y143.78 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X149.428 Y138.28 E.23994
G2 X149.439 Y138.804 I1.594 J.229 E.01626
G1 X144.098 Y144.146 E.23302
G1 X144.098 Y144.681 E.01652
G1 X149.556 Y139.223 E.23814
G2 X149.731 Y139.583 I.925 J-.226 E.01245
G1 X144.097 Y145.217 E.24579
G1 X144.097 Y145.71 E.0152
G1 X144.189 Y145.66 E.00322
G1 X149.963 Y139.887 E.25189
G2 X150.247 Y140.138 I.855 J-.681 E.01176
G1 X145.145 Y145.24 E.22257
G3 X145.936 Y144.984 I1.071 J1.965 E.02579
G1 X150.584 Y140.337 E.20275
G2 X150.98 Y140.476 I.592 J-1.054 E.01302
G1 X146.466 Y144.99 E.19692
G1 X146.893 Y145.098 E.01358
G1 X151.455 Y140.536 E.19905
G2 X151.979 Y140.467 I-.001 J-2.028 E.01635
G1 X152.115 Y140.412 E.0045
G1 X147.126 Y145.4 E.21763
; WIPE_START
G1 X148.541 Y143.986 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.892 Y139.753 Z1.2 F30000
G1 X162.991 Y134.354 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X166.358 Y130.987 E.14688
G1 X166.074 Y130.735 E.0117
G1 X163.381 Y133.428 E.11748
G1 X163.381 Y132.893 E.01652
G1 X165.791 Y130.483 E.10512
G2 X165.49 Y130.249 I-1.52 J1.642 E.01178
G1 X163.381 Y132.357 E.09198
G1 X163.381 Y131.822 E.01652
G1 X165.183 Y130.02 E.07861
G2 X164.87 Y129.798 I-1.452 J1.718 E.01186
G1 X163.381 Y131.287 E.06493
G1 X163.381 Y130.751 E.01652
G1 X164.539 Y129.593 E.05052
G1 X164.209 Y129.388 E.01199
G1 X163.36 Y130.237 E.03703
G2 X163.249 Y129.813 I-1.534 J.174 E.01358
G1 X163.858 Y129.204 E.02653
G1 X163.502 Y129.024 E.01228
G1 X163.071 Y129.456 E.01884
G1 X162.952 Y129.287 E.00637
G1 X163.171 Y129.238 E.00692
G1 X163.098 Y128.91 E.01035
G1 X163.265 Y128.726 E.00768
G1 X162.53 Y129.04 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.497778
G1 F7914.561
G1 X162.459 Y128.724 E.01199
; LINE_WIDTH: 0.515345
G1 F7620.257
G1 X162.456 Y128.71 E.00056
G2 X161.615 Y128.449 I-1.594 J3.644 E.03399
; LINE_WIDTH: 0.55143
G1 F7079.508
G1 X161.528 Y128.434 E.00365
G1 X161.319 Y128.117 E.01571
; WIPE_START
G1 X161.528 Y128.434 E-.61673
G1 X161.615 Y128.449 E-.14327
; WIPE_END
G1 E-.04 F1800
G1 X163.594 Y135.82 Z1.2 F30000
G1 X169.419 Y157.507 Z1.2
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.479327
G1 F8249.184
G1 X169.448 Y157.702 E.00704
; LINE_WIDTH: 0.434771
G1 F9187.164
G1 X169.477 Y157.898 E.00633
; LINE_WIDTH: 0.390216
G1 F10365.816
G1 X169.506 Y158.094 E.00561
; LINE_WIDTH: 0.344261
G1 F11946.596
G1 X169.537 Y158.303 E.00517
; LINE_WIDTH: 0.299198
G1 F14047.265
G1 X169.555 Y158.483 E.00378
; LINE_WIDTH: 0.257529
G1 F15000
G1 X169.574 Y158.663 E.00317
; LINE_WIDTH: 0.215861
G1 X169.592 Y158.843 E.00255
; LINE_WIDTH: 0.174192
G1 X169.611 Y159.023 E.00194
; LINE_WIDTH: 0.13218
G1 X169.63 Y159.206 E.00134
; LINE_WIDTH: 0.104029
G1 X169.637 Y159.332 E.00063
; WIPE_START
G1 X169.63 Y159.206 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X163.406 Y154.787 Z1.2 F30000
G1 X130.864 Y131.682 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X133.905 Y128.641 E.13266
G1 X133.354 Y128.656 E.01701
G1 X130.705 Y131.305 E.11557
G1 X130.425 Y131.049 E.01169
G1 X132.803 Y128.672 E.10372
G1 X132.252 Y128.688 E.01701
G1 X130.126 Y130.813 E.09272
G1 X129.823 Y130.581 E.01178
G1 X131.701 Y128.703 E.0819
G1 X131.15 Y128.719 E.01701
G1 X129.51 Y130.359 E.07154
G1 X129.183 Y130.15 E.01196
G1 X130.599 Y128.735 E.06177
G1 X130.048 Y128.75 E.01701
G1 X128.853 Y129.944 E.0521
G1 X128.501 Y129.761 E.01225
G1 X129.497 Y128.766 E.04343
G1 X128.946 Y128.781 E.01701
G1 X128.149 Y129.578 E.03475
G2 X127.776 Y129.416 I-1.114 J2.056 E.01257
G1 X128.395 Y128.797 E.027
G1 X127.843 Y128.813 E.01701
G1 X127.267 Y129.389 E.02514
G1 X127.017 Y128.977 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.483241
G1 F8175.854
G1 X126.807 Y128.947 E.00762
; LINE_WIDTH: 0.438309
G1 F9104.96
G1 X126.596 Y128.918 E.00684
; LINE_WIDTH: 0.391822
G1 F10318.1
G1 X126.372 Y128.887 E.00645
; LINE_WIDTH: 0.344474
G1 F11938.175
G1 X126.191 Y128.87 E.00445
; LINE_WIDTH: 0.299914
G1 F14008.155
G1 X126.011 Y128.853 E.00379
; LINE_WIDTH: 0.255353
G1 F15000
G1 X125.83 Y128.835 E.00314
; LINE_WIDTH: 0.210793
G1 X125.65 Y128.818 E.00248
; LINE_WIDTH: 0.165693
G1 X125.465 Y128.801 E.00186
; LINE_WIDTH: 0.119988
G1 X125.149 Y128.784 E.00199
; OBJECT_ID: 861
; WIPE_START
G1 X125.465 Y128.801 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 795
M625
; start printing object, unique label id: 861
M624 CAAAAAAAAAA=
G1 X129.892 Y122.583 Z1.2 F30000
G1 X147.017 Y98.534 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X147.147 Y98.606 E.00493
G3 X146.055 Y98.306 I-.971 J1.395 E.31583
G3 X146.317 Y98.307 I.122 J1.495 E.0087
G3 X146.89 Y98.458 I-.141 J1.693 E.01973
G1 X146.966 Y98.504 E.00294
M204 S250
G1 X146.825 Y98.866 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.086 Y98.697 I-.65 J1.135 E.22876
G3 X146.283 Y98.698 I.091 J1.128 E.00608
G3 X146.773 Y98.838 I-.108 J1.303 E.01575
; WIPE_START
M204 S10000
G1 X147.011 Y99 E-.10945
G1 X147.173 Y99.161 E-.08681
G1 X147.318 Y99.376 E-.09843
G1 X147.4 Y99.555 E-.07507
G1 X147.459 Y99.776 E-.08679
G1 X147.479 Y100.003 E-.08677
G1 X147.453 Y100.261 E-.09845
G1 X147.4 Y100.451 E-.07505
G1 X147.348 Y100.552 E-.0432
; WIPE_END
G1 E-.04 F1800
G1 X151.089 Y93.899 Z1.2 F30000
G1 X151.48 Y93.203 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X151.446 Y93.199 E.00114
G3 X151.333 Y89.806 I.007 J-1.699 E.1728
G3 X151.595 Y89.807 I.122 J1.491 E.0087
G3 X151.741 Y93.175 I-.141 J1.693 E.16281
G1 X151.54 Y93.197 E.00671
M204 S250
G1 X151.446 Y92.809 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X151.363 Y90.197 I.006 J-1.307 E.12325
G3 X151.56 Y90.198 I.091 J1.125 E.00608
G3 X151.506 Y92.807 I-.108 J1.303 E.12125
; WIPE_START
M204 S10000
G1 X151.107 Y92.769 E-.1523
G1 X150.892 Y92.691 E-.08677
G1 X150.695 Y92.577 E-.0868
G1 X150.52 Y92.43 E-.08678
G1 X150.372 Y92.253 E-.0876
G1 X150.215 Y91.951 E-.12917
G1 X150.156 Y91.731 E-.08679
G1 X150.146 Y91.616 E-.04378
; WIPE_END
G1 E-.04 F1800
G1 X157.446 Y89.389 Z1.2 F30000
G1 X161.811 Y88.058 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X161.459 Y88.105 E.01178
G1 X150.433 Y88.105 E.36577
G3 X148.844 Y86.517 I.027 J-1.616 E.08241
G1 X148.844 Y83.49 E.1004
G3 X150.433 Y81.901 I1.616 J.027 E.08241
G1 X161.459 Y81.901 E.36578
G3 X163.048 Y83.49 I-.027 J1.616 E.08241
G1 X163.048 Y86.517 E.1004
G3 X161.87 Y88.045 I-1.616 J-.027 E.06861
M204 S250
G1 X161.759 Y87.67 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X161.451 Y87.713 I-.323 J-1.177 E.00958
G1 X150.441 Y87.713 E.33829
G3 X149.236 Y86.508 I.016 J-1.221 E.05798
G1 X149.236 Y83.499 E.09247
G3 X150.441 Y82.293 I1.221 J.016 E.05798
G1 X161.451 Y82.293 E.33829
G3 X162.656 Y83.499 I-.016 J1.221 E.05798
G1 X162.656 Y86.508 E.09247
G3 X161.816 Y87.652 I-1.221 J-.016 E.04655
; WIPE_START
M204 S10000
G1 X161.451 Y87.713 E-.14076
M73 P56 R4
G1 X159.821 Y87.713 E-.61924
; WIPE_END
G1 E-.04 F1800
G1 X152.518 Y85.495 Z1.2 F30000
G1 X144.714 Y83.124 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X144.874 Y82.909 E.00888
G3 X146.055 Y82.306 I1.302 J1.091 E.0452
G3 X146.317 Y82.307 I.122 J1.491 E.0087
G3 X144.69 Y83.178 I-.141 J1.693 E.28939
M204 S250
G1 X145.041 Y83.352 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.086 Y82.697 I1.135 J.649 E.03946
G3 X146.283 Y82.698 I.091 J1.125 E.00608
G3 X145.012 Y83.404 I-.108 J1.303 E.20504
; WIPE_START
M204 S10000
G1 X145.167 Y83.159 E-.11008
G1 X145.418 Y82.93 E-.12919
G1 X145.615 Y82.816 E-.08678
G1 X145.83 Y82.738 E-.08678
G1 X146.086 Y82.697 E-.09843
G1 X146.283 Y82.698 E-.07506
G1 X146.508 Y82.738 E-.08679
G1 X146.723 Y82.816 E-.08676
G1 X146.723 Y82.816 E-.00012
; WIPE_END
G1 E-.04 F1800
G1 X145.292 Y90.313 Z1.2 F30000
G1 X143.409 Y100.18 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X143.385 Y100.205 E.00114
G3 X141.682 Y101.105 I-1.735 J-1.22 E.06633
G1 X134.611 Y101.105 E.23459
G3 X132.762 Y98.026 I.026 J-2.11 E.14249
G1 X133.298 Y97.107 E.0353
G2 X134.245 Y94.633 I-10.9 J-5.59 E.08805
G2 X133.996 Y88.524 I-10.788 J-2.621 E.20544
G2 X132.762 Y85.98 I-11.992 J4.248 E.09399
G3 X134.611 Y82.901 I1.875 J-.969 E.14249
G1 X141.682 Y82.901 E.23459
G3 X143.771 Y84.99 I-.028 J2.116 E.10845
G1 X143.771 Y99.017 E.46529
G3 X143.569 Y99.889 I-2.121 J-.032 E.02994
G1 X143.438 Y100.127 E.00902
M204 S250
G1 X143.065 Y99.981 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X141.674 Y100.713 I-1.411 J-.993 E.05016
G1 X134.619 Y100.713 E.21678
G3 X133.109 Y98.209 I.016 J-1.717 E.10753
G1 X133.644 Y97.291 E.03266
G2 X134.625 Y94.727 I-11.293 J-5.792 E.0845
G2 X134.368 Y88.399 I-11.18 J-2.715 E.19715
G2 X133.109 Y85.798 I-12.327 J4.361 E.08898
G3 X134.619 Y83.293 I1.517 J-.793 E.10773
G1 X141.674 Y83.293 E.21678
G3 X143.379 Y84.999 I-.017 J1.722 E.08209
G1 X143.379 Y99.008 E.43047
G3 X143.099 Y99.931 I-1.725 J-.02 E.03004
; WIPE_START
M204 S10000
G1 X142.878 Y100.213 E-.13586
G1 X142.65 Y100.404 E-.11331
G1 X142.392 Y100.553 E-.11327
G1 X142.112 Y100.655 E-.11325
G1 X141.966 Y100.688 E-.05672
G1 X141.674 Y100.713 E-.1115
G1 X141.368 Y100.713 E-.1161
; WIPE_END
G1 E-.04 F1800
G1 X134.494 Y97.396 Z1.2 F30000
G1 X114.506 Y87.75 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X114.517 Y87.735 E.00058
G3 X122.789 Y81.939 I9.154 J4.264 E.35087
G1 X123.063 Y81.927 E.00912
G3 X131.945 Y86.209 I.621 J10.065 E.34173
G1 X132.418 Y86.952 E.02924
G3 X114.18 Y88.55 I-8.747 J5.047 E1.34448
G1 X114.484 Y87.805 E.02667
M204 S250
G1 X114.872 Y87.901 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X122.823 Y82.33 I8.799 J4.098 E.31239
G1 X123.08 Y82.319 E.00792
G3 X131.623 Y86.434 I.603 J9.674 E.30445
G1 X132.078 Y87.148 E.02604
G3 X114.847 Y87.956 I-8.407 J4.851 E1.22122
; WIPE_START
M204 S10000
G1 X115.26 Y87.148 E-.34455
G1 X115.715 Y86.434 E-.32198
G1 X115.865 Y86.239 E-.09348
; WIPE_END
G1 E-.04 F1800
G1 X121.532 Y91.35 Z1.2 F30000
G1 X157.675 Y123.949 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X156.834 Y123.753 E.02866
G3 X158.566 Y103.939 I2.612 J-9.754 E.93542
G1 X158.84 Y103.927 E.00912
G1 X159.446 Y103.901 E.02012
G3 X157.734 Y123.95 I0 J10.098 E1.10941
M204 S250
G1 X157.762 Y123.557 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X158.6 Y104.33 I1.685 J-9.558 E.85884
G1 X158.857 Y104.319 E.00792
G1 X159.446 Y104.293 E.01811
G3 X157.821 Y123.567 I0 J9.706 E.98709
; WIPE_START
M204 S10000
G1 X156.933 Y123.383 E-.34458
G1 X156.125 Y123.128 E-.32186
G1 X155.898 Y123.034 E-.09356
; WIPE_END
G1 E-.04 F1800
G1 X159.847 Y116.502 Z1.2 F30000
G1 X166.722 Y105.131 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.689 Y105.136 E.00111
G3 X165.469 Y104.911 I-.245 J-2.09 E.04179
G1 X164.549 Y104.375 E.0353
G2 X155.967 Y103.676 I-5.103 J9.629 E.29363
G2 X153.423 Y104.911 I4.247 J11.991 E.09399
G3 X150.509 Y103.862 I-.969 J-1.881 E.11527
G3 X150.374 Y103.407 I2.086 J-.865 E.01576
G3 X150.344 Y102.329 I6.153 J-.712 E.03583
G3 X151.654 Y100.394 I2.137 J.037 E.082
G1 X165.678 Y94.792 E.50094
G3 X166.227 Y94.659 I.792 J2.069 E.01877
G3 X168.548 Y96.736 I.206 J2.105 E.11614
G1 X168.548 Y103.062 E.20983
G3 X167.041 Y105.064 I-2.104 J-.016 E.08904
G1 X166.781 Y105.118 E.00881
M204 S250
G1 X166.644 Y104.746 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X165.652 Y104.563 I-.2 J-1.7 E.03147
G1 X164.733 Y104.028 E.03266
G2 X155.842 Y103.304 I-5.287 J9.976 E.28179
G2 X153.241 Y104.563 I4.36 J12.326 E.08898
G3 X150.761 Y103.34 I-.793 J-1.518 E.09888
G3 X150.736 Y102.337 I5.786 J-.645 E.03087
G3 X151.808 Y100.755 I1.74 J.024 E.06215
G1 X165.816 Y95.159 E.46351
G3 X166.272 Y95.049 I.65 J1.687 E.01446
G3 X168.156 Y96.744 I.164 J1.713 E.08756
G1 X168.156 Y103.053 E.19386
G3 X166.703 Y104.738 I-1.712 J-.007 E.07442
; WIPE_START
M204 S10000
G1 X166.498 Y104.758 E-.07833
G1 X166.352 Y104.756 E-.05564
G1 X166.062 Y104.715 E-.11107
G1 X165.784 Y104.626 E-.11108
G1 X165.652 Y104.563 E-.05569
G1 X164.86 Y104.102 E-.34819
; WIPE_END
G1 E-.04 F1800
G1 X166.304 Y96.607 Z1.2 F30000
G1 X166.973 Y93.136 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X166.725 Y93.035 E.00888
G3 X167.333 Y89.806 I.729 J-1.535 E.14807
G3 X167.595 Y89.807 I.122 J1.491 E.0087
G3 X167.032 Y93.146 I-.141 J1.693 E.18652
M204 S250
G1 X167.109 Y92.763 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X167.363 Y90.197 I.344 J-1.261 E.11276
G3 X167.56 Y90.198 I.091 J1.125 E.00608
G3 X167.167 Y92.777 I-.108 J1.303 E.13175
; WIPE_START
M204 S10000
G1 X166.89 Y92.69 E-.11011
G1 X166.695 Y92.577 E-.08598
G1 X166.52 Y92.43 E-.08679
G1 X166.312 Y92.158 E-.12995
G1 X166.214 Y91.949 E-.08761
G1 X166.156 Y91.731 E-.086
G1 X166.136 Y91.503 E-.08678
G1 X166.166 Y91.277 E-.08677
; WIPE_END
G1 E-.04 F1800
G1 X158.791 Y93.242 Z1.2 F30000
G1 X128.082 Y101.422 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X127.169 Y101.794 E.03272
G3 X123.387 Y81.609 I-3.493 J-9.792 E1.19205
G1 X158.73 Y80.606 E1.17285
G1 X159.016 Y80.618 E.0095
G1 X159.707 Y80.648 E.02295
G3 X170.125 Y91.634 I-1.003 J11.384 E.54897
G1 X169.843 Y114.121 E.74599
G3 X149.447 Y111.155 I-10.396 J-.124 E1.17487
G1 X149.877 Y109.855 E.04541
M73 P57 R4
G2 X147.433 Y103.561 I-5.413 J-1.519 E.24025
G1 X145.26 Y102.225 E.08462
G2 X142.347 Y101.401 I-2.959 J4.9 E.10161
G1 X128.138 Y101.401 E.47134
M204 S250
G1 X128.211 Y101.793 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X123.367 Y81.218 I-4.532 J-9.791 E1.17566
G1 X158.732 Y80.213 E1.08711
G1 X159.032 Y80.226 E.00922
G1 X159.74 Y80.257 E.02178
G3 X170.518 Y91.622 I-1.038 J11.776 E.52604
G1 X170.235 Y114.134 E.6918
G3 X149.069 Y111.047 I-10.788 J-.138 E1.12902
G1 X149.5 Y109.748 E.04205
G2 X147.22 Y103.891 I-5.035 J-1.413 E.20718
G1 X145.061 Y102.563 E.07789
G2 X142.339 Y101.793 I-2.759 J4.558 E.08795
G1 X128.271 Y101.793 E.4323
M204 S10000
G1 X128.393 Y101.188 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.331188
G1 F12488.394
G1 X129.207 Y100.97 E.0198
G1 X131.546 Y100.114 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.58492
G1 F6642.067
G2 X131.55 Y100.225 I-.029 J.056 E.01173
G1 X132.28 Y100.632 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X132.028 Y100.23 E.01459
G1 X131.857 Y99.77 E.01508
G1 X131.766 Y99.246 E.01635
G1 X131.374 Y99.673 E.01782
G1 X130.676 Y100.315 E.02914
G1 X130.249 Y100.632 E.01632
G1 X132.22 Y100.632 E.06056
G1 X132.896 Y100.791 F30000
G1 F9547.299
G1 X132.727 Y100.623 E.00733
G1 X132.398 Y100.128 E.01825
G3 X132.155 Y98.697 I2.354 J-1.135 E.0452
G1 X131.87 Y98.54 E.01002
G3 X130.421 Y100.037 I-8.806 J-7.067 E.06411
G3 X129.537 Y100.687 I-269.874 J-366.676 E.03372
G1 X129.623 Y101.009 E.01025
G1 X132.827 Y101.009 E.09845
G1 X132.826 Y100.876 E.00408
G1 X132.858 Y100.837 E.00155
G1 X133.297 Y100.92 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.120985
G1 F15000
G1 X133.464 Y101.056 E.00137
; LINE_WIDTH: 0.165392
G1 X133.654 Y101.198 E.00237
G1 X133.791 Y101.176 F30000
; LINE_WIDTH: 0.133892
G1 F15000
G3 X133.438 Y101.102 I1.585 J-8.51 E.00268
; WIPE_START
G1 X133.791 Y101.176 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.17 Y98.258 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.474748
G1 F8336.654
G1 X132.397 Y97.845 E.01659
; LINE_WIDTH: 0.431336
G1 F9268.417
G3 X132.754 Y97.258 I13.437 J7.779 E.02174
G2 X132.406 Y86.177 I-9.076 J-5.261 E.36969
; LINE_WIDTH: 0.473823
G1 F8354.554
G1 X132.17 Y85.749 E.01718
G1 X131.628 Y85.527 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X132.196 Y84.959 E.02478
G3 X132.281 Y84.338 I1.839 J-.063 E.01943
G1 X131.501 Y85.118 E.03402
G1 X131.245 Y84.839 E.01169
G1 X134.456 Y81.628 E.14006
G1 X135.007 Y81.613 E.01701
G1 X133.956 Y82.664 E.04585
G3 X134.586 Y82.569 I.665 J2.28 E.01971
G1 X135.558 Y81.597 E.04241
G1 X136.109 Y81.581 E.01701
G1 X135.122 Y82.568 E.04305
G1 X135.657 Y82.568 E.01652
G1 X136.66 Y81.566 E.04373
G1 X137.211 Y81.55 E.01701
G1 X136.193 Y82.568 E.04442
G1 X136.728 Y82.568 E.01652
G1 X137.762 Y81.534 E.0451
G1 X138.313 Y81.519 E.01701
G1 X137.264 Y82.568 E.04578
G1 X137.799 Y82.568 E.01652
G1 X138.864 Y81.503 E.04646
G1 X139.415 Y81.487 E.01701
G1 X138.334 Y82.568 E.04715
G1 X138.87 Y82.568 E.01652
G1 X139.966 Y81.472 E.04783
G1 X140.517 Y81.456 E.01701
G1 X139.405 Y82.568 E.04851
G1 X139.94 Y82.568 E.01652
G1 X141.068 Y81.44 E.04919
G1 X141.619 Y81.425 E.01701
G1 X140.476 Y82.568 E.04988
G1 X141.011 Y82.568 E.01652
G1 X142.17 Y81.409 E.05056
G1 X142.721 Y81.394 E.01701
G1 X141.547 Y82.568 E.05124
G3 X142.05 Y82.6 I.075 J2.84 E.01559
G1 X143.272 Y81.378 E.0533
G1 X143.823 Y81.362 E.01701
G1 X142.473 Y82.712 E.0589
G3 X142.848 Y82.873 I-.424 J1.505 E.01261
G1 X144.374 Y81.347 E.06659
G1 X144.925 Y81.331 E.01701
G1 X143.167 Y83.089 E.07668
G3 X143.447 Y83.345 I-1.072 J1.448 E.01171
G1 X145.476 Y81.315 E.08854
G1 X146.027 Y81.3 E.01701
G1 X143.562 Y83.765 E.10756
G1 X144.095 Y84.192 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.382549
G1 F10599.811
G1 X144.254 Y83.985 E.00723
G1 X144.095 Y84.192 F30000
; LINE_WIDTH: 0.413801
G1 F9706.615
G1 X144.08 Y84.213 E.00077
; LINE_WIDTH: 0.449156
G1 F8861.861
G1 X144.065 Y84.234 E.00085
; LINE_WIDTH: 0.450691
G1 F8828.487
G1 X144.168 Y84.698 E.0158
G1 X144.195 Y84.713 E.00105
; LINE_WIDTH: 0.407986
G1 F9861.234
G1 X144.447 Y84.841 E.00838
G1 X144.293 Y85.175 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X144.104 Y85.364 E.00825
G1 X144.104 Y85.9 E.01652
G1 X144.65 Y85.354 E.02382
G2 X144.928 Y85.612 I.896 J-.687 E.01174
G1 X144.104 Y86.436 E.03595
G1 X144.103 Y86.971 E.01652
G1 X145.259 Y85.815 E.05044
G2 X145.646 Y85.964 I.584 J-.939 E.01285
G1 X144.103 Y87.507 E.06731
G1 X144.103 Y88.043 E.01652
G1 X146.11 Y86.035 E.08758
G2 X146.696 Y85.971 I.078 J-1.991 E.01826
G1 X146.717 Y85.963 E.00069
G1 X143.933 Y88.748 E.12149
; WIPE_START
G1 X145.347 Y87.334 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.649 Y82.214 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X146.578 Y81.284 E.04056
G1 X147.129 Y81.268 E.01701
G1 X146.408 Y81.99 E.03148
G1 X146.517 Y81.996 E.00337
G1 X146.849 Y82.084 E.0106
G1 X147.68 Y81.253 E.03629
G1 X148.231 Y81.237 E.01701
G1 X147.212 Y82.256 E.04446
G1 X147.52 Y82.484 E.01181
G1 X148.782 Y81.221 E.05508
G1 X149.333 Y81.206 E.01701
G1 X147.655 Y82.885 E.07324
; WIPE_START
G1 X149.069 Y81.47 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X156.699 Y81.648 Z1.2 F30000
G1 X160.58 Y81.738 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X160.831 Y81.486 E.01096
G1 X160.627 Y81.177 E.01142
G1 X160.712 Y81.122 E.00313
G1 X160.67 Y81.112 E.00134
G1 X160.214 Y81.568 E.01988
G1 X159.679 Y81.568 E.01652
G1 X160.2 Y81.047 E.02273
G1 X159.726 Y80.986 E.01475
G1 X159.143 Y81.568 E.0254
G1 X158.608 Y81.568 E.01652
G1 X159.216 Y80.96 E.02653
G2 X158.701 Y80.94 I-1.123 J22.14 E.01591
G1 X158.073 Y81.568 E.02741
G1 X157.537 Y81.568 E.01652
G1 X158.15 Y80.956 E.02672
G1 X157.599 Y80.971 E.01701
G1 X157.002 Y81.568 E.02604
G1 X156.466 Y81.568 E.01652
G1 X157.048 Y80.987 E.02536
G1 X156.497 Y81.002 E.01701
G1 X155.931 Y81.568 E.02468
G1 X155.396 Y81.568 E.01652
G1 X155.946 Y81.018 E.02399
G1 X155.395 Y81.034 E.01701
G1 X154.86 Y81.568 E.02331
G1 X154.325 Y81.568 E.01652
G1 X154.844 Y81.049 E.02263
G1 X154.293 Y81.065 E.01701
G1 X153.79 Y81.568 E.02195
G1 X153.254 Y81.568 E.01652
G1 X153.742 Y81.081 E.02126
G1 X153.191 Y81.096 E.01701
G1 X152.719 Y81.568 E.02058
G1 X152.183 Y81.568 E.01652
G1 X152.64 Y81.112 E.0199
G1 X152.089 Y81.128 E.01701
G1 X151.648 Y81.568 E.01922
G1 X151.113 Y81.568 E.01652
G1 X151.537 Y81.143 E.01853
G1 X150.986 Y81.159 E.01701
G1 X150.577 Y81.568 E.01785
G2 X149.986 Y81.624 I-.083 J2.27 E.01838
G1 X150.435 Y81.175 E.01962
G1 X149.884 Y81.19 E.01701
G1 X147.982 Y83.092 E.08298
G1 X148.136 Y83.474 E.01269
G1 X148.568 Y83.042 E.01884
G2 X148.516 Y83.629 I1.658 J.443 E.01828
G1 X148.198 Y83.947 E.01386
G3 X148.129 Y84.552 I-2.502 J.02 E.01882
G1 X148.515 Y84.166 E.01684
G1 X148.514 Y84.702 E.01654
G1 X144.102 Y89.114 E.19248
G1 X144.102 Y89.65 E.01652
G1 X148.513 Y85.238 E.19245
G1 X148.512 Y85.775 E.01654
G1 X144.102 Y90.185 E.19242
G1 X144.101 Y90.721 E.01652
G1 X148.511 Y86.311 E.19239
G2 X148.537 Y86.821 I2.799 J.115 E.01577
G1 X144.101 Y91.257 E.19352
G1 X144.101 Y91.792 E.01652
G1 X148.658 Y87.235 E.19882
G2 X148.842 Y87.586 I1.425 J-.524 E.01227
G1 X144.1 Y92.328 E.20688
G1 X144.1 Y92.864 E.01652
G1 X149.085 Y87.879 E.21745
G2 X149.384 Y88.115 I1.046 J-1.018 E.01179
G1 X144.1 Y93.399 E.23052
G1 X144.1 Y93.935 E.01652
G1 X149.736 Y88.298 E.2459
G2 X150.164 Y88.405 I.459 J-.926 E.01373
G1 X144.099 Y94.471 E.2646
G1 X144.099 Y95.006 E.01652
G1 X150.667 Y88.438 E.28653
G1 X151.202 Y88.438 E.01652
G1 X144.099 Y95.542 E.30991
G1 X144.098 Y96.078 E.01652
G1 X151.738 Y88.438 E.33329
G1 X152.274 Y88.438 E.01652
G1 X151.226 Y89.485 E.04571
G1 X151.314 Y89.471 E.00276
G1 X151.753 Y89.494 E.01356
G1 X152.809 Y88.437 E.04608
G1 X153.345 Y88.437 E.01652
G1 X152.177 Y89.605 E.05095
G3 X152.532 Y89.786 I-.336 J1.095 E.01234
G1 X153.881 Y88.437 E.05886
G1 X154.416 Y88.437 E.01652
G1 X152.833 Y90.02 E.06908
G3 X153.084 Y90.304 I-.681 J.854 E.01176
G1 X154.952 Y88.436 E.0815
G1 X155.488 Y88.436 E.01652
G1 X153.283 Y90.641 E.09618
G3 X153.424 Y91.035 I-1.429 J.734 E.01295
G1 X156.023 Y88.436 E.11339
G1 X156.559 Y88.436 E.01652
G1 X153.482 Y91.512 E.13421
G3 X153.372 Y92.158 I-1.89 J.008 E.02033
G1 X157.095 Y88.435 E.16242
G1 X157.63 Y88.435 E.01652
G1 X147.55 Y98.515 E.43975
G3 X147.802 Y98.799 I-.621 J.801 E.01177
G1 X158.166 Y88.435 E.45216
M73 P58 R4
G1 X158.702 Y88.434 E.01652
G1 X148 Y99.136 E.46687
G1 X148.146 Y99.526 E.01284
G1 X159.237 Y88.434 E.48389
G1 X159.773 Y88.434 E.01652
G1 X148.198 Y100.008 E.50496
G3 X148.101 Y100.641 I-2.231 J-.02 E.01982
G1 X160.308 Y88.434 E.53258
G1 X160.844 Y88.433 E.01652
G1 X146.612 Y102.666 E.6209
G1 X146.943 Y102.869 E.01201
G1 X161.38 Y88.433 E.62981
G2 X161.994 Y88.354 I.096 J-1.685 E.01921
G1 X147.275 Y103.073 E.64214
G1 X147.607 Y103.277 E.01201
G1 X166.624 Y84.259 E.82968
G1 X166.885 Y84.534 E.01168
G1 X147.926 Y103.493 E.8271
G3 X148.229 Y103.725 I-1.19 J1.863 E.01179
G1 X150.051 Y101.904 E.07948
G2 X150.012 Y102.478 I4.613 J.599 E.01776
G1 X148.516 Y103.973 E.06525
G1 X148.789 Y104.236 E.01168
G1 X150.016 Y103.009 E.05355
G2 X150.06 Y103.5 I1.516 J.113 E.01529
G1 X149.038 Y104.522 E.04458
G3 X149.272 Y104.823 I-1.624 J1.504 E.01178
G1 X150.176 Y103.919 E.03943
G2 X150.349 Y104.283 I2.595 J-1.008 E.01241
G1 X149.491 Y105.14 E.03742
G1 X149.693 Y105.474 E.01203
G1 X150.567 Y104.599 E.03816
G2 X150.833 Y104.869 I1.3 J-1.012 E.0117
G1 X149.87 Y105.832 E.04202
G3 X150.027 Y106.21 I-2.099 J1.098 E.01264
G1 X151.141 Y105.097 E.04857
G2 X151.49 Y105.282 I.711 J-.919 E.01228
G1 X150.164 Y106.609 E.05788
G3 X150.276 Y107.032 I-2.388 J.86 E.01352
G1 X151.89 Y105.418 E.0704
G2 X152.368 Y105.476 I.483 J-2.008 E.01489
G1 X150.36 Y107.483 E.08759
G3 X150.41 Y107.969 I-2.776 J.533 E.01507
G1 X152.834 Y105.544 E.10576
G1 X152.986 Y105.819 E.00966
G2 X150.899 Y108.015 I6.221 J7.999 E.09382
G1 X150.634 Y108.28 E.01157
G1 X150.518 Y108.416 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.243791
G1 F15000
G1 X150.361 Y108.941 E.00897
; LINE_WIDTH: 0.217934
G1 X150.313 Y109.089 E.00221
; LINE_WIDTH: 0.16953
G1 X150.265 Y109.236 E.0016
; LINE_WIDTH: 0.121126
G1 X150.218 Y109.383 E.00099
G1 X150.224 Y109.385 F30000
; LINE_WIDTH: 0.310249
G1 F13466.566
G1 X150.516 Y108.416 E.02206
G1 X153.192 Y105.502 F30000
; LINE_WIDTH: 0.474747
G1 F8336.677
G1 X153.605 Y105.275 E.01659
; LINE_WIDTH: 0.431334
G1 F9268.458
G3 X165.272 Y105.266 I5.84 J8.741 E.39147
; LINE_WIDTH: 0.47381
G1 F8354.817
G1 X165.701 Y105.502 E.01718
G1 X165.807 Y105.956 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X166.285 Y105.478 E.02085
G1 X166.728 Y105.469 E.01367
G1 X166.855 Y105.444 E.004
G1 X166.105 Y106.194 E.03273
; WIPE_START
G1 X166.855 Y105.444 E-.40315
G1 X166.728 Y105.469 E-.04926
G1 X166.285 Y105.478 E-.16845
G1 X166.026 Y105.737 E-.13914
; WIPE_END
G1 E-.04 F1800
G1 X168.998 Y110.261 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X169.566 Y109.693 E.02479
G1 X169.573 Y109.151 E.01673
G1 X168.971 Y109.753 E.02626
G2 X168.799 Y109.389 I-2.163 J.802 E.01242
G1 X169.579 Y108.609 E.03406
G1 X169.586 Y108.066 E.01673
G1 X168.615 Y109.037 E.04236
G2 X168.425 Y108.692 I-2.066 J.915 E.01217
G1 X169.593 Y107.524 E.05096
G1 X169.6 Y106.982 E.01673
G1 X168.217 Y108.365 E.06034
G1 X168.008 Y108.038 E.01196
G1 X169.607 Y106.44 E.06973
G1 X169.613 Y105.898 E.01673
G1 X167.777 Y107.734 E.0801
G1 X167.545 Y107.431 E.01178
G1 X169.62 Y105.356 E.09054
G1 X169.627 Y104.813 E.01673
G1 X167.299 Y107.141 E.10154
G1 X167.043 Y106.862 E.01169
G1 X169.634 Y104.271 E.11301
G1 X169.641 Y103.729 E.01673
G1 X166.784 Y106.586 E.12463
G1 X166.505 Y106.33 E.01169
G1 X169.647 Y103.187 E.13711
G1 X169.654 Y102.645 E.01673
G1 X168.839 Y103.46 E.03555
G2 X168.875 Y102.889 I-1.645 J-.388 E.01773
G1 X169.661 Y102.102 E.0343
G1 X169.668 Y101.56 E.01673
G1 X168.875 Y102.353 E.03457
G1 X168.876 Y101.817 E.01653
G1 X169.675 Y101.018 E.03485
G1 X169.681 Y100.476 E.01673
G1 X168.876 Y101.281 E.03512
G1 X168.877 Y100.745 E.01653
G1 X169.688 Y99.934 E.03539
G1 X169.695 Y99.392 E.01673
G1 X168.878 Y100.209 E.03566
G1 X168.878 Y99.673 E.01653
G1 X169.702 Y98.849 E.03593
G1 X169.709 Y98.307 E.01673
G1 X168.879 Y99.137 E.0362
G1 X168.879 Y98.601 E.01653
G1 X169.715 Y97.765 E.03647
G1 X169.722 Y97.223 E.01673
G1 X168.88 Y98.065 E.03674
G1 X168.881 Y97.529 E.01653
G1 X169.729 Y96.681 E.03701
G1 X169.736 Y96.139 E.01673
G1 X168.881 Y96.993 E.03728
G2 X168.86 Y96.478 I-2.946 J-.139 E.01591
G1 X169.743 Y95.596 E.03849
G1 X169.749 Y95.054 E.01673
G1 X168.769 Y96.034 E.04275
G2 X168.616 Y95.653 I-1.19 J.258 E.01275
G1 X169.756 Y94.512 E.04976
G1 X169.763 Y93.97 E.01673
G1 X168.412 Y95.321 E.05894
G2 X168.168 Y95.029 I-1.549 J1.05 E.01174
G1 X169.77 Y93.428 E.06988
G1 X169.776 Y92.885 E.01673
G1 X167.881 Y94.781 E.08269
G1 X167.55 Y94.576 E.012
G1 X169.783 Y92.343 E.09743
G1 X169.79 Y91.801 E.01673
G1 X167.163 Y94.419 E.11442
G2 X166.726 Y94.33 I-.568 J1.661 E.0138
G1 X167.523 Y93.533 E.03478
G3 X167.03 Y93.491 I-.127 J-1.422 E.01535
G1 X166.193 Y94.327 E.03649
G2 X165.468 Y94.517 I.471 J3.278 E.02318
G1 X166.622 Y93.363 E.05036
G1 X166.579 Y93.347 E.00142
G3 X166.278 Y93.171 I.533 J-1.258 E.01077
G1 X164.577 Y94.873 E.07425
G1 X163.685 Y95.229 E.02962
G1 X165.994 Y92.921 E.10072
G3 X165.754 Y92.625 I.719 J-.827 E.0118
G1 X162.793 Y95.585 E.12916
G1 X161.902 Y95.942 E.02962
G1 X165.568 Y92.276 E.15992
G3 X165.442 Y91.866 I1.089 J-.556 E.0133
G1 X161.01 Y96.298 E.19336
G1 X160.119 Y96.654 E.02962
G1 X165.62 Y91.153 E.23998
; WIPE_START
G1 X164.205 Y92.567 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.286 Y91.769 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X169.765 Y91.29 E.0209
G1 X169.728 Y90.792 E.0154
G1 X169.433 Y91.087 E.01285
G2 X169.306 Y90.679 I-1.219 J.157 E.01325
G1 X169.66 Y90.325 E.01545
G1 X169.585 Y89.864 E.0144
G1 X169.11 Y90.34 E.02076
G2 X168.863 Y90.051 I-.935 J.546 E.01178
G1 X169.485 Y89.43 E.0271
G1 X169.377 Y89.002 E.01361
G1 X168.568 Y89.811 E.03532
G2 X168.219 Y89.625 I-.703 J.895 E.01226
G1 X169.25 Y88.593 E.045
G1 X169.113 Y88.195 E.01299
G1 X167.809 Y89.5 E.05692
G1 X167.299 Y89.473 E.01573
G1 X168.965 Y87.808 E.07268
G1 X168.801 Y87.437 E.01252
G1 X159.227 Y97.01 E.41766
G1 X158.336 Y97.366 E.02962
G1 X168.635 Y87.067 E.4493
G1 X168.445 Y86.722 E.01216
G1 X157.444 Y97.722 E.47991
G1 X156.553 Y98.079 E.02962
G1 X168.255 Y86.376 E.51052
G2 X168.048 Y86.047 I-2.022 J1.039 E.012
G1 X155.661 Y98.435 E.54042
G1 X154.77 Y98.791 E.02962
G1 X167.834 Y85.726 E.56997
G2 X167.615 Y85.41 I-1.952 J1.123 E.01188
G1 X153.878 Y99.147 E.59929
G1 X152.986 Y99.503 E.02962
G1 X167.377 Y85.113 E.62782
G1 X167.14 Y84.815 E.01175
G1 X151.791 Y100.164 E.66962
G1 X147.168 Y101.574 F30000
G1 F9509.47
G1 X146.157 Y102.585 E.04412
G1 X145.799 Y102.059 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.394049
G1 F10252.658
G1 X146.025 Y101.914 E.0077
G1 X145.799 Y102.059 F30000
; LINE_WIDTH: 0.417163
G1 F9619.43
G1 X145.778 Y102.071 E.00072
G1 X145.638 Y102.015 E.00462
; LINE_WIDTH: 0.366216
G1 F11135.315
G1 X145.46 Y101.933 E.00516
; LINE_WIDTH: 0.323999
G1 F12807.824
G1 X144.988 Y101.679 E.01227
; LINE_WIDTH: 0.351176
G1 F11678.606
G1 X144.833 Y101.585 E.00456
; LINE_WIDTH: 0.395976
G1 F10196.699
G1 X144.698 Y101.495 E.00465
G1 X144.684 Y101.215 E.00809
G1 X144.254 Y100.022 F30000
; LINE_WIDTH: 0.38249
G1 F10601.658
G1 X144.095 Y99.814 E.00723
; LINE_WIDTH: 0.413757
G1 F9707.777
G1 X144.08 Y99.794 E.00077
; LINE_WIDTH: 0.44913
G1 F8862.426
G1 X144.065 Y99.773 E.00085
; LINE_WIDTH: 0.450714
G1 F8828.003
G1 X144.168 Y99.308 E.01581
G1 X144.195 Y99.294 E.00104
; LINE_WIDTH: 0.41033
G1 F9798.322
G1 X144.445 Y99.167 E.00837
G1 X143.387 Y101.046 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.55467
G1 F7034.685
G3 X144.025 Y101.192 I-.453 J3.449 E.02732
G1 X144.032 Y100.943 E.01037
G1 X144.123 Y100.823 E.0063
G1 X144.184 Y100.802 E.00269
G1 X144.121 Y100.664 E.00632
G1 X143.927 Y100.639 E.00815
G1 X143.756 Y100.462 E.0103
G3 X143.346 Y100.911 I-1.16 J-.645 E.0256
G1 X143.397 Y100.989 E.00384
G1 X142.855 Y101.01 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.109661
G1 F15000
G1 X142.764 Y101.074 E.0006
; LINE_WIDTH: 0.138482
G1 X142.656 Y101.152 E.00104
G1 X142.698 Y101.211 E.00057
; WIPE_START
G1 X142.656 Y101.152 E-.27014
G1 X142.764 Y101.074 E-.48986
; WIPE_END
G1 E-.04 F1800
G1 X143.928 Y96.783 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
M73 P59 R4
G1 F9509.47
G1 X149.428 Y91.283 E.23994
G2 X149.439 Y91.808 I1.594 J.229 E.01626
G1 X144.098 Y97.149 E.23302
G1 X144.098 Y97.685 E.01652
G1 X149.556 Y92.226 E.23814
G2 X149.731 Y92.586 I.925 J-.226 E.01245
G1 X144.097 Y98.22 E.24579
G1 X144.097 Y98.713 E.0152
G1 X144.189 Y98.664 E.00322
G1 X149.963 Y92.89 E.25189
G2 X150.247 Y93.141 I.855 J-.681 E.01176
G1 X145.145 Y98.243 E.22257
G3 X145.936 Y97.987 I1.071 J1.965 E.02579
G1 X150.584 Y93.34 E.20275
G2 X150.98 Y93.479 I.592 J-1.054 E.01302
G1 X146.466 Y97.993 E.19692
G1 X146.893 Y98.102 E.01358
G1 X151.455 Y93.539 E.19905
G2 X151.979 Y93.47 I-.001 J-2.028 E.01635
G1 X152.115 Y93.415 E.0045
G1 X147.126 Y98.403 E.21763
; WIPE_START
G1 X148.541 Y96.989 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.892 Y92.756 Z1.2 F30000
G1 X162.991 Y87.357 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F9509.47
G1 X166.358 Y83.99 E.14688
G1 X166.074 Y83.739 E.0117
G1 X163.381 Y86.431 E.11748
G1 X163.381 Y85.896 E.01652
G1 X165.791 Y83.487 E.10512
G2 X165.49 Y83.252 I-1.52 J1.642 E.01178
G1 X163.381 Y85.361 E.09198
G1 X163.381 Y84.825 E.01652
G1 X165.183 Y83.024 E.07861
G2 X164.87 Y82.802 I-1.452 J1.718 E.01186
G1 X163.381 Y84.29 E.06493
G1 X163.381 Y83.755 E.01652
G1 X164.539 Y82.597 E.05052
G1 X164.209 Y82.392 E.01199
G1 X163.36 Y83.24 E.03703
G2 X163.249 Y82.816 I-1.534 J.174 E.01358
G1 X163.858 Y82.208 E.02653
G1 X163.502 Y82.027 E.01228
G1 X163.071 Y82.459 E.01884
G1 X162.952 Y82.29 E.00637
G1 X163.171 Y82.241 E.00692
G1 X163.098 Y81.913 E.01035
G1 X163.265 Y81.729 E.00768
G1 X162.53 Y82.043 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.497778
G1 F7914.561
G1 X162.459 Y81.728 E.01199
; LINE_WIDTH: 0.515345
G1 F7620.257
G1 X162.456 Y81.714 E.00056
G2 X161.615 Y81.452 I-1.594 J3.644 E.03399
; LINE_WIDTH: 0.55143
G1 F7079.508
G1 X161.528 Y81.437 E.00365
G1 X161.319 Y81.121 E.01571
; WIPE_START
G1 X161.528 Y81.437 E-.61673
G1 X161.615 Y81.452 E-.14327
; WIPE_END
G1 E-.04 F1800
G1 X163.594 Y88.823 Z1.2 F30000
G1 X169.419 Y110.51 Z1.2
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.479327
G1 F8249.184
G1 X169.448 Y110.706 E.00704
; LINE_WIDTH: 0.434771
G1 F9187.164
G1 X169.477 Y110.902 E.00633
; LINE_WIDTH: 0.390216
G1 F10365.816
G1 X169.506 Y111.098 E.00561
; LINE_WIDTH: 0.344261
G1 F11946.596
G1 X169.537 Y111.306 E.00517
; LINE_WIDTH: 0.299198
G1 F14047.265
G1 X169.555 Y111.486 E.00378
; LINE_WIDTH: 0.257529
G1 F15000
G1 X169.574 Y111.666 E.00317
; LINE_WIDTH: 0.215861
G1 X169.592 Y111.846 E.00255
; LINE_WIDTH: 0.174192
G1 X169.611 Y112.026 E.00194
; LINE_WIDTH: 0.13218
G1 X169.63 Y112.209 E.00134
; LINE_WIDTH: 0.104029
G1 X169.637 Y112.335 E.00063
; WIPE_START
G1 X169.63 Y112.209 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X163.406 Y107.791 Z1.2 F30000
G1 X130.864 Y84.685 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42149
G1 F9509.47
G1 X133.905 Y81.644 E.13266
G1 X133.354 Y81.66 E.01701
G1 X130.705 Y84.309 E.11557
G1 X130.425 Y84.053 E.01169
G1 X132.803 Y81.675 E.10372
G1 X132.252 Y81.691 E.01701
G1 X130.126 Y83.816 E.09272
G1 X129.823 Y83.584 E.01178
G1 X131.701 Y81.706 E.0819
G1 X131.15 Y81.722 E.01701
G1 X129.51 Y83.362 E.07154
G1 X129.183 Y83.154 E.01196
G1 X130.599 Y81.738 E.06177
G1 X130.048 Y81.753 E.01701
G1 X128.853 Y82.948 E.0521
G1 X128.501 Y82.764 E.01225
G1 X129.497 Y81.769 E.04343
G1 X128.946 Y81.785 E.01701
G1 X128.149 Y82.581 E.03475
G2 X127.776 Y82.419 I-1.114 J2.056 E.01257
G1 X128.395 Y81.8 E.027
G1 X127.843 Y81.816 E.01701
G1 X127.267 Y82.392 E.02514
G1 X127.017 Y81.98 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.483241
G1 F8175.854
G1 X126.807 Y81.95 E.00762
; LINE_WIDTH: 0.438309
G1 F9104.96
G1 X126.596 Y81.921 E.00684
; LINE_WIDTH: 0.391822
G1 F10318.1
G1 X126.372 Y81.89 E.00645
; LINE_WIDTH: 0.344474
G1 F11938.175
G1 X126.191 Y81.873 E.00445
; LINE_WIDTH: 0.299914
G1 F14008.155
G1 X126.011 Y81.856 E.00379
; LINE_WIDTH: 0.255353
G1 F15000
G1 X125.83 Y81.839 E.00314
; LINE_WIDTH: 0.210793
G1 X125.65 Y81.821 E.00248
; LINE_WIDTH: 0.165693
G1 X125.465 Y81.804 E.00186
; LINE_WIDTH: 0.119988
G1 X125.149 Y81.788 E.00199
; OBJECT_ID: 817
; WIPE_START
G1 X125.465 Y81.804 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 861
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X122.607 Y88.881 Z1.2 F30000
G1 X102.122 Y139.592 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X100.707 Y138.596 I-1.273 J.306 E.19469
G1 X100.816 Y138.589 E.00339
G3 X102.106 Y139.534 I.032 J1.309 E.05286
; WIPE_START
M204 S10000
G1 X102.163 Y139.849 E-.12155
G1 X102.161 Y139.98 E-.04973
G1 X102.119 Y140.237 E-.0991
G1 X102.027 Y140.481 E-.09911
G1 X101.888 Y140.702 E-.09917
G1 X101.708 Y140.891 E-.09913
G1 X101.495 Y141.041 E-.09915
G1 X101.27 Y141.139 E-.09304
; WIPE_END
G1 E-.04 F1800
G1 X96.426 Y135.241 Z1.2 F30000
G1 X89.002 Y126.202 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X87.979 Y125.868 I-.881 J.968 E.2187
G1 X88.089 Y125.861 E.00339
G3 X88.957 Y126.162 I.032 J1.309 E.02885
; WIPE_START
M204 S10000
G1 X89.18 Y126.392 E-.12166
G1 X89.313 Y126.617 E-.09919
G1 X89.399 Y126.863 E-.09917
G1 X89.435 Y127.121 E-.09911
G1 X89.419 Y127.382 E-.09918
G1 X89.351 Y127.634 E-.09911
G1 X89.235 Y127.867 E-.09914
G1 X89.165 Y127.958 E-.04343
; WIPE_END
G1 E-.04 F1800
G1 X96.007 Y131.34 Z1.2 F30000
G1 X102.988 Y134.791 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X102.951 Y134.79 E.00125
G3 X103.045 Y114.6 I.388 J-10.093 E1.03002
G3 X105.699 Y114.875 I.303 J10.004 E.08876
G3 X103.454 Y134.797 I-2.36 J9.821 E.96975
G1 X103.048 Y134.792 E.01347
M204 S250
G1 X102.993 Y134.399 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X102.965 Y134.398 E.00086
G3 X103.06 Y114.992 I.373 J-9.701 E.91718
G3 X105.607 Y115.257 I.287 J9.617 E.07891
G3 X103.449 Y134.404 I-2.269 J9.44 E.86339
G1 X103.053 Y134.4 E.01218
; WIPE_START
M204 S10000
G1 X102.965 Y134.398 E-.03343
G1 X102.482 Y134.369 E-.18389
G1 X102.001 Y134.314 E-.18398
G1 X101.523 Y134.236 E-.18405
G1 X101.074 Y134.14 E-.17466
; WIPE_END
G1 E-.04 F1800
G1 X103.575 Y126.929 Z1.2 F30000
G1 X112.608 Y100.889 Z1.2
G1 Z.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G3 X113.827 Y101.408 I-.048 J1.804 E.045
G2 X112.605 Y101.734 I-.075 J2.173 E.04259
G2 X115.281 Y103.235 I.978 J1.394 E.22797
G1 X115.286 Y102.856 E.01257
G1 X125.171 Y112.741 E.46374
G2 X123.551 Y113.398 I-.205 J1.822 E.06045
G2 X126.595 Y114.549 I1.347 J1.039 E.2106
G1 X126.599 Y114.176 E.01236
G3 X126.57 Y116.866 I-1.37 J1.33 E.09902
G1 X102.416 Y141.02 E1.13309
G1 X102.247 Y140.891 E.00706
G2 X100.875 Y141.601 I-1.383 J-.993 E.30168
G2 X101.846 Y141.283 I-.088 J-1.912 E.03431
G1 X101.982 Y141.454 E.00724
G3 X100.13 Y142.111 I-1.514 J-1.329 E.06808
G3 X99.137 Y141.573 I.492 J-2.097 E.03791
G1 X86.451 Y128.887 E.59513
G3 X86.451 Y126.161 I1.345 J-1.363 E.10062
G1 X86.563 Y126.049 E.00525
G1 X86.733 Y126.178 E.00706
G2 X88.193 Y125.469 I1.384 J.993 E.2989
G2 X87.133 Y125.785 I-.056 J1.747 E.03734
G1 X86.997 Y125.615 E.00724
G1 X111.158 Y101.454 E1.13343
G3 X112.521 Y100.888 I1.381 J1.399 E.0502
G1 X112.548 Y100.888 E.0009
; WIPE_START
G1 X112.608 Y100.889 E-.02281
G1 X112.89 Y100.917 E-.10783
G1 X113.246 Y101.024 E-.14119
G1 X113.574 Y101.2 E-.14114
G1 X113.827 Y101.408 E-.12466
G1 X113.244 Y101.462 E-.22238
; WIPE_END
G1 E-.04 F1800
G1 X112.94 Y101.984 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X113.434 Y101.827 I.637 J1.144 E.01606
G1 X113.544 Y101.82 E.00339
G3 X112.888 Y102.015 I.032 J1.309 E.23149
; WIPE_START
M204 S10000
G1 X113.18 Y101.882 E-.12181
G1 X113.434 Y101.827 E-.09904
G1 X113.544 Y101.82 E-.04189
G1 X113.76 Y101.831 E-.08222
G1 X114.014 Y101.892 E-.09915
G1 X114.251 Y102.002 E-.09921
G1 X114.461 Y102.157 E-.09915
G1 X114.636 Y102.351 E-.09909
G1 X114.66 Y102.392 E-.01844
; WIPE_END
G1 E-.04 F1800
G1 X120.051 Y107.795 Z1.2 F30000
G1 X125.563 Y113.319 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F9547.055
M204 S5000
M73 P60 R4
G3 X124.748 Y113.141 I-.673 J1.123 E.2267
G1 X124.858 Y113.133 E.00339
G3 X125.511 Y113.289 I.032 J1.309 E.02085
; WIPE_START
M204 S10000
G1 X125.774 Y113.471 E-.12173
G1 X125.949 Y113.665 E-.09915
G1 X126.083 Y113.889 E-.09912
G1 X126.169 Y114.135 E-.09917
G1 X126.205 Y114.393 E-.09907
G1 X126.188 Y114.654 E-.09913
G1 X126.121 Y114.906 E-.09915
G1 X126.07 Y115.008 E-.04348
; WIPE_END
G1 E-.04 F1800
G1 X120.887 Y109.406 Z1.2 F30000
G1 X112.647 Y100.499 Z1.2
G1 Z.8
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X112.967 Y100.53 E.00991
G3 X114.147 Y101.163 I-.586 J2.508 E.04163
G1 X126.861 Y113.877 E.55245
G3 X126.861 Y117.13 I-1.62 J1.627 E.11109
G1 X102.127 Y141.864 E1.07482
G1 X101.772 Y142.155 E.01411
G1 X101.376 Y142.367 E.01379
G3 X98.873 Y141.864 I-.875 J-2.124 E.08316
G1 X86.16 Y129.151 E.55246
G3 X86.16 Y125.897 I1.62 J-1.627 E.11108
G1 X110.894 Y101.163 E1.07482
G3 X112.587 Y100.497 I1.642 J1.686 E.05739
M204 S10000
G1 X112.291 Y101.244 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.20333
G1 F15000
G1 X113.21 Y101.236 E.012
G1 X113.093 Y101.191 F30000
; LINE_WIDTH: 0.436629
G1 F9143.824
G1 X112.551 Y101.29 E.01766
G1 X112.479 Y101.566 E.00916
; WIPE_START
G1 X112.551 Y101.29 E-.25953
G1 X113.093 Y101.191 E-.50047
; WIPE_END
G1 E-.04 F1800
G1 X113.858 Y101.626 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.114235
G1 F15000
G1 X114.02 Y101.639 E.00094
; LINE_WIDTH: 0.1523
G1 X114.096 Y101.648 E.00068
; LINE_WIDTH: 0.166963
G1 X114.396 Y101.689 E.00306
G1 X114.383 Y101.773 F30000
; LINE_WIDTH: 0.14784
G1 F15000
G1 X114.624 Y101.98 E.00272
G1 X114.933 Y102.322 E.00394
; LINE_WIDTH: 0.198398
G1 X115.009 Y102.424 E.00161
G3 X115.083 Y102.766 I-6.988 J1.703 E.00443
G1 X115.068 Y102.768 F30000
; LINE_WIDTH: 0.128685
G1 F15000
G2 X114.993 Y102.286 I-9.795 J1.274 E.00341
G1 X114.383 Y101.773 F30000
; LINE_WIDTH: 0.204028
G1 F15000
G1 X114.253 Y101.678 E.00212
; LINE_WIDTH: 0.230618
G1 X114.114 Y101.585 E.00256
; WIPE_START
G1 X114.253 Y101.678 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.843 Y103.644 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42022
G1 F9541.479
G1 X105.076 Y114.411 E.46812
G3 X105.524 Y114.497 I-.642 J4.531 E.01401
G1 X115.99 Y104.031 E.45506
G1 X116.256 Y104.298 E.0116
G1 X105.955 Y114.599 E.4479
G3 X106.372 Y114.716 I-.964 J4.245 E.01332
G1 X116.523 Y104.565 E.44138
G1 X116.79 Y104.831 E.0116
G1 X106.775 Y114.846 E.43543
G1 X107.163 Y114.992 E.01273
G1 X117.057 Y105.098 E.43019
G1 X117.323 Y105.365 E.0116
G1 X107.538 Y115.15 E.42547
G3 X107.903 Y115.319 I-1.514 J3.743 E.01236
G1 X117.59 Y105.632 E.42122
G1 X117.857 Y105.899 E.0116
G1 X108.257 Y115.499 E.41742
G1 X108.599 Y115.69 E.01205
G1 X118.124 Y106.165 E.41415
G1 X118.391 Y106.432 E.0116
G1 X108.929 Y115.894 E.4114
G3 X109.25 Y116.106 I-1.97 J3.324 E.01184
G1 X118.657 Y106.699 E.40904
G1 X118.924 Y106.966 E.0116
G1 X109.562 Y116.328 E.40707
G1 X109.862 Y116.561 E.01169
G1 X119.191 Y107.233 E.40561
G1 X119.458 Y107.499 E.0116
G1 X110.152 Y116.805 E.4046
G3 X110.434 Y117.057 I-2.381 J2.947 E.01162
G1 X119.725 Y107.766 E.40395
G1 X119.991 Y108.033 E.0116
G1 X110.708 Y117.317 E.40366
G1 X110.968 Y117.59 E.0116
G1 X120.258 Y108.3 E.40395
G1 X120.525 Y108.566 E.0116
G1 X111.22 Y117.872 E.4046
G3 X111.463 Y118.162 I-2.785 J2.585 E.01165
G1 X120.792 Y108.833 E.40561
G1 X121.059 Y109.1 E.0116
G1 X111.696 Y118.462 E.40707
G3 X111.918 Y118.774 I-3.011 J2.37 E.01177
G1 X121.325 Y109.367 E.40904
G1 X121.592 Y109.634 E.0116
G1 X112.13 Y119.095 E.4114
G3 X112.334 Y119.426 I-3.2 J2.199 E.01193
G1 X121.859 Y109.9 E.41416
G1 X122.126 Y110.167 E.0116
G1 X112.526 Y119.767 E.41742
G3 X112.705 Y120.122 I-3.454 J1.971 E.01221
G1 X122.393 Y110.434 E.42122
G1 X122.659 Y110.701 E.0116
G1 X112.874 Y120.486 E.42547
G3 X113.032 Y120.862 I-3.671 J1.766 E.01253
G1 X122.926 Y110.968 E.4302
G1 X123.193 Y111.234 E.0116
G1 X113.178 Y121.249 E.43544
G1 X113.308 Y121.653 E.01304
G1 X123.46 Y111.501 E.44138
G1 X123.726 Y111.768 E.0116
G1 X113.425 Y122.069 E.44791
G3 X113.527 Y122.501 I-4.26 J1.237 E.01364
G1 X123.993 Y112.035 E.45507
G1 X124.26 Y112.302 E.0116
G1 X113.613 Y122.948 E.46291
G3 X113.682 Y123.413 I-4.609 J.919 E.01445
G1 X122.873 Y114.222 E.39963
G2 X122.876 Y114.713 I1.628 J.235 E.01514
G1 X122.883 Y114.746 E.00105
G1 X113.731 Y123.898 E.39791
G3 X113.758 Y124.404 I-5.065 J.521 E.01561
G1 X122.999 Y115.163 E.40182
G2 X123.173 Y115.523 I1.522 J-.512 E.01232
G1 X113.759 Y124.937 E.40932
G3 X113.73 Y125.499 I-5.648 J-.007 E.01732
G1 X123.403 Y115.827 E.42057
G2 X123.69 Y116.073 I.961 J-.829 E.01168
G1 X113.666 Y126.097 E.43584
G3 X113.56 Y126.737 I-6.474 J-.75 E.01996
G1 X124.024 Y116.273 E.45498
G2 X124.41 Y116.42 I.68 J-1.208 E.01277
G1 X113.398 Y127.433 E.47883
G3 X113.15 Y128.214 I-7.945 J-2.09 E.02522
G1 X124.889 Y116.475 E.51044
M73 P61 R4
G2 X125.529 Y116.368 I.037 J-1.757 E.02005
G1 X112.775 Y129.123 E.55455
G3 X112.174 Y130.232 I-10.058 J-4.732 E.0388
G1 X112.188 Y130.243 E.00056
G1 X126.397 Y116.034 E.61782
G1 X126.398 Y116.083 E.00149
G1 X126.697 Y116.078 E.0092
G3 X126.324 Y116.641 I-1.903 J-.857 E.02085
G1 X112.354 Y130.611 E.60741
G1 X112.117 Y130.623 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.563485
G1 F6915.564
G1 X111.886 Y130.891 E.01504
; LINE_WIDTH: 0.530026
G1 F7390.6
G1 X111.647 Y131.169 E.01454
; LINE_WIDTH: 0.499828
G1 F7879.051
G1 X111.474 Y131.36 E.00958
; LINE_WIDTH: 0.473639
G1 F8358.126
G1 X111.295 Y131.558 E.0094
; LINE_WIDTH: 0.443387
G1 F8989.502
G1 X110.57 Y132.301 E.03385
G1 X110.183 Y132.669 E.01743
; LINE_WIDTH: 0.474161
G1 F8348.016
G1 X109.992 Y132.842 E.00904
; LINE_WIDTH: 0.500414
G1 F7868.958
G1 X109.793 Y133.022 E.01003
; LINE_WIDTH: 0.530574
G1 F7382.291
G1 X109.524 Y133.253 E.01409
; LINE_WIDTH: 0.563477
G1 F6915.672
G1 X109.255 Y133.485 E.01504
G1 X102.764 Y140.167 F30000
; LINE_WIDTH: 0.114035
G1 F15000
G1 X102.752 Y140.396 E.00133
G1 X102.058 Y141.1 F30000
; LINE_WIDTH: 0.196038
G1 F15000
G1 X101.918 Y140.963 E.00245
G1 X102.058 Y141.1 F30000
; LINE_WIDTH: 0.229395
G1 F15000
G1 X102.199 Y141.237 E.00298
; LINE_WIDTH: 0.262752
G1 X102.339 Y141.374 E.00352
; WIPE_START
G1 X102.199 Y141.237 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X101.051 Y141.818 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.114357
G1 F15000
G1 X100.876 Y141.849 E.00104
; LINE_WIDTH: 0.155043
G3 X100.679 Y141.861 I-.22 J-2.081 E.0018
; LINE_WIDTH: 0.193616
G3 X100.479 Y141.855 I-.071 J-.92 E.00246
; LINE_WIDTH: 0.22746
G1 X100.281 Y141.821 E.00301
; LINE_WIDTH: 0.259954
G3 X100.087 Y141.767 I.3 J-1.449 E.00357
; LINE_WIDTH: 0.292569
G1 F14420.277
G1 X99.902 Y141.696 E.00404
G1 X99.721 Y141.593 E.00424
; LINE_WIDTH: 0.328073
G1 F12624.803
G3 X99.189 Y141.117 I1.324 J-2.011 E.01664
; LINE_WIDTH: 0.375931
G1 F10810.465
G1 X99.058 Y140.955 E.00566
; LINE_WIDTH: 0.410952
G1 F9781.776
G1 X99.004 Y140.883 E.0027
; LINE_WIDTH: 0.437904
G1 F9114.292
G1 X98.951 Y140.81 E.00289
G1 X98.956 Y140.794 E.00057
; LINE_WIDTH: 0.408952
G1 F9835.214
G1 X99.045 Y140.53 E.00829
G1 X87.383 Y129.191 F30000
; LINE_WIDTH: 0.438923
G1 F9090.845
G3 X87.138 Y129.019 I3.38 J-5.071 E.00967
; LINE_WIDTH: 0.397471
G1 F10153.702
G1 X86.987 Y128.901 E.00553
; LINE_WIDTH: 0.357781
G1 F11433.63
G1 X86.834 Y128.77 E.00518
; LINE_WIDTH: 0.321787
G1 F12909.386
G3 X86.613 Y128.545 I1.33 J-1.531 E.00717
G1 X86.482 Y128.386 E.00468
G1 X86.38 Y128.215 E.00452
; LINE_WIDTH: 0.283091
G1 F14989.321
G3 X86.292 Y128.032 I1.234 J-.698 E.00398
G1 X86.225 Y127.841 E.00396
; LINE_WIDTH: 0.244088
G1 F15000
G1 X86.185 Y127.643 E.00331
; LINE_WIDTH: 0.212715
G3 X86.164 Y127.445 I1.618 J-.27 E.00277
; LINE_WIDTH: 0.172688
G1 X86.165 Y127.247 E.0021
; LINE_WIDTH: 0.133621
G3 X86.191 Y127.051 I1.053 J.04 E.00146
; LINE_WIDTH: 0.101653
G1 X86.207 Y126.973 E.00038
; WIPE_START
G1 X86.191 Y127.051 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.062 Y126.106 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.196026
G1 F15000
G1 X86.921 Y125.969 E.00245
; LINE_WIDTH: 0.229373
G1 X86.781 Y125.832 E.00298
; LINE_WIDTH: 0.26272
G1 X86.64 Y125.695 E.00352
; WIPE_START
G1 X86.781 Y125.832 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.627 Y125.273 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.118939
G1 F15000
G1 X87.864 Y125.26 E.00147
G1 X92.469 Y121.764 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.41999
G1 F9547.299
G1 X89.531 Y124.702 E.12765
G1 X89.891 Y124.937 E.0132
G1 X90.265 Y125.288 E.01575
G1 X90.62 Y125.798 E.01909
G1 X90.85 Y126.359 E.01863
G1 X90.958 Y126.922 E.01762
G1 X90.951 Y127.503 E.01786
G1 X90.82 Y128.089 E.01845
G1 X90.585 Y128.604 E.01742
G1 X90.275 Y129.034 E.01628
G1 X89.839 Y129.444 E.01839
G1 X89.138 Y129.827 E.02454
G1 X89.044 Y129.859 E.00303
G1 X98.164 Y138.979 E.39629
G1 X98.347 Y138.548 E.0144
G1 X98.665 Y138.078 E.01742
G1 X99.069 Y137.68 E.01742
G1 X99.544 Y137.371 E.01742
G1 X100.055 Y137.165 E.01693
G1 X100.546 Y137.065 E.01541
G3 X102.035 Y137.305 I.242 J3.238 E.04675
G1 X102.655 Y137.7 E.0226
G1 X102.862 Y137.887 E.00855
G1 X103.222 Y138.326 E.01746
G1 X103.325 Y138.49 E.00595
G1 X106.26 Y135.555 E.12753
G3 X92.454 Y121.822 I-2.928 J-10.862 E.72321
G1 X91.84 Y122.926 F30000
G1 F9547.299
G1 X90.124 Y124.642 E.07458
G1 X90.554 Y125.047 E.01815
G3 X91.095 Y125.926 I-2.29 J2.016 E.03187
; LINE_WIDTH: 0.437309
G1 F9128.059
G1 X91.157 Y126.06 E.00477
; LINE_WIDTH: 0.471945
G1 F8391.119
G1 X91.219 Y126.195 E.00518
; LINE_WIDTH: 0.517745
G1 F7581.752
G1 X91.281 Y126.33 E.00574
G3 X91.403 Y127.046 I-7.767 J1.689 E.02813
; LINE_WIDTH: 0.50744
G1 F7749.936
G1 X91.377 Y127.218 E.00655
; LINE_WIDTH: 0.47246
G1 F8381.058
G1 X91.351 Y127.389 E.00606
; LINE_WIDTH: 0.420158
G1 F9543.06
G3 X91.185 Y128.186 I-5.699 J-.774 E.02506
G1 X90.923 Y128.772 E.01973
G1 X90.572 Y129.266 E.0186
G1 X90.085 Y129.73 E.0207
G1 X89.69 Y129.972 E.01423
G1 X98.043 Y138.324 E.36311
G1 X98.391 Y137.818 E.01889
G1 X98.776 Y137.429 E.01682
G1 X99.393 Y137.025 E.02267
G1 X99.969 Y136.798 E.01905
G1 X100.51 Y136.69 E.01696
; LINE_WIDTH: 0.444623
G1 F8961.856
G1 X100.782 Y136.66 E.00894
; LINE_WIDTH: 0.508439
G1 F7733.303
G1 X101.053 Y136.629 E.01036
G1 X101.609 Y136.713 E.02131
; LINE_WIDTH: 0.48938
G1 F8063.433
G1 X101.852 Y136.819 E.00965
; LINE_WIDTH: 0.420855
G1 F9525.456
G3 X102.977 Y137.47 I-2.38 J5.407 E.0401
G1 X103.37 Y137.912 E.01822
G1 X105.098 Y136.184 E.07526
G3 X102.348 Y136.279 I-1.79 J-11.916 E.08492
; LINE_WIDTH: 0.444578
G1 F8962.86
G1 X102.065 Y136.273 E.00929
; LINE_WIDTH: 0.509488
G1 F7715.928
G1 X101.781 Y136.267 E.01079
G1 X101.192 Y136.171 E.0227
; LINE_WIDTH: 0.49169
G1 F8021.927
G1 X100.92 Y136.089 E.01037
; LINE_WIDTH: 0.420511
G1 F9534.133
G3 X99.52 Y135.679 I11.853 J-43.068 E.04488
G3 X92.044 Y127.488 I3.821 J-10.995 E.35566
; LINE_WIDTH: 0.43748
G1 F9124.088
G1 X91.989 Y127.321 E.00566
; LINE_WIDTH: 0.47246
G1 F8381.058
G1 X91.934 Y127.154 E.00616
; LINE_WIDTH: 0.520059
G1 F7544.973
G1 X91.879 Y126.987 E.00684
G1 X91.767 Y126.325 E.02608
; LINE_WIDTH: 0.50484
G1 F7793.557
G1 X91.763 Y126.15 E.00661
; LINE_WIDTH: 0.4709
G1 F8411.608
G1 X91.76 Y125.974 E.00612
; LINE_WIDTH: 0.420985
G1 F9522.187
G3 X91.704 Y124.623 I42.405 J-2.428 E.04166
G3 X91.832 Y122.986 I12.448 J.148 E.05064
G1 X91.302 Y124.057 F30000
; LINE_WIDTH: 0.50439
G1 F7801.157
G1 X90.732 Y124.627 E.03034
G1 X91.154 Y125.149 E.02523
G1 X91.307 Y125.401 E.0111
G3 X91.301 Y124.117 I11.694 J-.701 E.04832
G1 X91.693 Y127.635 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G3 X91.135 Y129.152 I-4.276 J-.711 E.04996
G1 X90.614 Y129.771 E.02486
G1 X90.292 Y130.041 E.01291
G1 X97.983 Y137.732 E.3342
G1 X98.38 Y137.283 E.01841
G1 X98.875 Y136.895 E.01932
G3 X100.382 Y136.329 I2.017 J3.079 E.04988
G3 X91.709 Y127.693 I2.937 J-11.624 E.3947
G1 X91.693 Y128.917 F30000
; LINE_WIDTH: 0.42509
G1 F9419.901
G3 X90.86 Y130.075 I-4.213 J-2.152 E.0446
G1 X92.231 Y131.447 E.0604
G3 X93.042 Y132.253 I-6.368 J7.216 E.03563
; LINE_WIDTH: 0.406345
G1 F9905.757
G1 X93.471 Y132.71 E.01857
; LINE_WIDTH: 0.363866
G1 F11216.867
G2 X95.233 Y134.476 I48.085 J-46.215 E.06526
; LINE_WIDTH: 0.399345
G1 F10100.301
G1 X95.688 Y134.905 E.01815
; LINE_WIDTH: 0.431523
G1 F9263.965
G1 X95.92 Y135.117 E.00994
; LINE_WIDTH: 0.44996
G1 F8844.339
G3 X96.577 Y135.793 I-3.703 J4.264 E.03131
; LINE_WIDTH: 0.423585
G1 F9457.14
G1 X97.961 Y137.176 E.0607
G1 X98.42 Y136.754 E.01935
G1 X99.089 Y136.33 E.02459
G3 X96.517 Y135.054 I5.29 J-13.903 E.08921
G1 X96.017 Y134.689 E.0192
; LINE_WIDTH: 0.40636
G1 F9905.349
G1 X95.54 Y134.296 E.01829
; LINE_WIDTH: 0.363868
G1 F11216.799
G3 X93.795 Y132.561 I14.653 J-16.488 E.0644
; LINE_WIDTH: 0.399355
G1 F10100.017
G1 X93.4 Y132.088 E.01791
; LINE_WIDTH: 0.431525
G1 F9263.905
G1 X93.211 Y131.843 E.00979
; LINE_WIDTH: 0.449955
G1 F8844.449
G1 X93.021 Y131.599 E.01026
G1 X92.712 Y131.063 E.02051
; LINE_WIDTH: 0.41999
G1 F9547.299
G3 X91.714 Y128.973 I10.449 J-6.273 E.07127
G1 X91.627 Y129.722 F30000
; LINE_WIDTH: 0.38328
G1 F10577.036
G1 X91.351 Y130.059 E.01208
G1 X92.225 Y130.933 E.0343
G3 X91.651 Y129.777 I9.145 J-5.261 E.03583
G1 X98.304 Y136.398 F30000
; LINE_WIDTH: 0.38222
G1 F10610.08
G3 X97.087 Y135.796 I4.204 J-10.038 E.03755
G1 X97.962 Y136.67 E.03419
G1 X98.257 Y136.435 E.01045
G1 X103.967 Y136.722 F30000
; LINE_WIDTH: 0.50461
G1 F7797.44
G3 X102.625 Y136.72 I-.648 J-13.796 E.05051
G3 X103.392 Y137.296 I-1.872 J3.292 E.03622
G1 X103.924 Y136.764 E.0283
G1 X107.69 Y134.656 F30000
; LINE_WIDTH: 0.41999
G1 F9547.299
G3 X93.368 Y120.334 I-4.355 J-9.966 E.80031
G2 X88.866 Y124.833 I616.496 J621.383 E.19555
G1 X89.221 Y124.956 E.01151
G1 X89.638 Y125.216 E.01512
G1 X89.995 Y125.554 E.0151
G1 X90.278 Y125.957 E.01512
G1 X90.479 Y126.43 E.01578
G1 X90.587 Y126.993 E.01762
G1 X90.573 Y127.513 E.016
G1 X90.419 Y128.09 E.01835
G1 X90.187 Y128.532 E.01533
G1 X89.877 Y128.914 E.01512
G1 X89.477 Y129.235 E.01576
G1 X88.969 Y129.49 E.01746
G3 X88.301 Y129.649 I-1.917 J-6.554 E.02111
G1 X98.387 Y139.735 E.43829
G1 X98.482 Y139.205 E.01656
G1 X98.667 Y138.749 E.01512
G1 X98.938 Y138.338 E.01511
G1 X99.285 Y137.989 E.01512
G1 X99.793 Y137.673 E.01837
G3 X101.973 Y137.699 I1.064 J2.258 E.06934
G1 X102.446 Y138.014 E.01747
G1 X102.931 Y138.565 E.02255
G3 X103.208 Y139.135 I-2.776 J1.704 E.01949
G2 X107.649 Y134.7 I-264.82 J-269.611 E.19285
G1 X108.85 Y133.614 F30000
G1 F9547.299
G1 X108.003 Y134.091 E.02985
G3 X94.41 Y119.174 I-4.674 J-9.393 E.83399
G1 X94.185 Y118.981 E.00909
G1 X88.215 Y124.951 E.25942
G1 X88.249 Y125.085 E.00426
G1 X88.436 Y125.1 E.00574
G1 X88.985 Y125.261 E.01758
G1 X89.385 Y125.496 E.01427
G3 X90.119 Y126.552 I-1.385 J1.746 E.0401
G1 X90.218 Y127.069 E.01615
G1 X90.19 Y127.527 E.01411
G1 X90.044 Y127.997 E.01514
G3 X89.308 Y128.898 I-2.068 J-.939 E.03615
G1 X88.8 Y129.152 E.01746
G1 X88.325 Y129.254 E.01491
G1 X87.833 Y129.232 E.01515
M73 P61 R3
G1 X87.634 Y129.516 E.01064
G1 X98.469 Y140.351 E.47081
G1 X98.611 Y140.055 E.01008
G1 X98.783 Y140.028 E.00533
G1 X98.764 Y139.749 E.00859
G3 X99.943 Y138.019 I2.131 J.186 E.06723
G3 X101.764 Y138.013 I.917 J1.905 E.05783
G1 X102.237 Y138.328 E.01747
G1 X102.639 Y138.804 E.01916
G1 X102.837 Y139.224 E.01426
G1 X102.937 Y139.777 E.01726
G1 X103.073 Y139.808 E.0043
G1 X109.043 Y133.839 E.25941
G1 X108.889 Y133.66 E.00725
; WIPE_START
G1 X109.043 Y133.839 E-.08967
G1 X107.796 Y135.086 E-.67034
; WIPE_END
G1 E-.04 F1800
G1 X106.574 Y127.552 Z1.2 F30000
G1 X104.458 Y114.495 Z1.2
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.42022
G1 F9541.479
G1 X113.8 Y105.154 E.40617
G1 X113.404 Y105.159 E.01217
G1 X113.284 Y105.136 E.00375
G1 X104.127 Y114.293 E.39814
G2 X103.619 Y114.267 I-.462 J4.099 E.01565
G1 X112.861 Y105.025 E.40186
G3 X112.5 Y104.852 I.392 J-1.286 E.01235
G1 X103.086 Y114.267 E.40935
G2 X102.518 Y114.301 I-.028 J4.219 E.01752
G1 X112.2 Y104.619 E.42101
G1 X112.141 Y104.57 E.00238
G1 X111.949 Y104.336 E.00928
G1 X101.928 Y114.358 E.43575
G2 X101.288 Y114.464 I.749 J6.471 E.01996
G1 X111.748 Y104.004 E.4548
G3 X111.611 Y103.607 I1.074 J-.591 E.01297
G1 X100.592 Y114.626 E.4791
G2 X99.811 Y114.874 I2.095 J7.958 E.02522
G1 X111.55 Y103.135 E.51041
G3 X111.651 Y102.5 I1.622 J-.067 E.01989
G1 X98.902 Y115.249 E.5543
G2 X97.792 Y115.85 I4.73 J10.056 E.03884
G1 X97.781 Y115.837 E.00054
G1 X111.867 Y101.751 E.61246
G1 X111.959 Y101.374 E.01192
G1 X111.959 Y101.323 E.00157
G1 X111.924 Y101.334 E.00113
G2 X111.386 Y101.698 I.646 J1.534 E.02008
G1 X97.414 Y115.67 E.60754
G1 X97.401 Y115.907 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.563484
G1 F6915.583
M73 P62 R3
G1 X97.133 Y116.138 E.01504
; LINE_WIDTH: 0.530014
G1 F7390.781
G1 X96.855 Y116.377 E.01454
; LINE_WIDTH: 0.499818
G1 F7879.23
G1 X96.664 Y116.549 E.00958
; LINE_WIDTH: 0.473632
G1 F8358.27
G1 X96.466 Y116.729 E.0094
; LINE_WIDTH: 0.443386
G1 F8989.528
G1 X95.723 Y117.454 E.03385
G1 X95.355 Y117.841 E.01743
; LINE_WIDTH: 0.474151
G1 F8348.21
G1 X95.182 Y118.031 E.00905
; LINE_WIDTH: 0.500412
G1 F7869.002
G1 X95.002 Y118.231 E.01004
; LINE_WIDTH: 0.530568
G1 F7382.381
G1 X94.771 Y118.5 E.01409
; LINE_WIDTH: 0.563483
G1 F6915.593
G1 X94.539 Y118.769 E.01504
; WIPE_START
G1 X94.771 Y118.5 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X102.28 Y117.136 Z1.2 F30000
G1 X125.272 Y112.961 Z1.2
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.112153
G1 F15000
G1 X125.405 Y112.98 E.00076
; LINE_WIDTH: 0.142685
G1 X125.484 Y112.995 E.00066
; LINE_WIDTH: 0.172856
G1 X125.559 Y113.01 E.00081
; LINE_WIDTH: 0.197246
G3 X125.697 Y113.087 I-.042 J.238 E.00202
; LINE_WIDTH: 0.147837
G1 X125.938 Y113.294 E.00272
G1 X126.247 Y113.636 E.00394
; LINE_WIDTH: 0.198359
G1 X126.322 Y113.738 E.00161
G3 X126.397 Y114.079 I-6.9 J1.681 E.00443
G1 X126.381 Y114.082 F30000
; LINE_WIDTH: 0.128657
G1 F15000
G2 X126.307 Y113.6 I-9.935 J1.293 E.00341
; WIPE_START
G1 X126.381 Y114.082 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X126.784 Y114.806 Z1.2 F30000
G1 Z.8
G1 E.8 F1800
; LINE_WIDTH: 0.144266
G1 F15000
G1 X126.798 Y115.743 E.00774
G1 X126.751 Y115.718 F30000
; LINE_WIDTH: 0.278462
G1 F15000
G2 X126.795 Y114.827 I-18.064 J-1.334 E.01712
; CHANGE_LAYER
; Z_HEIGHT: 1
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F15000
G1 X126.751 Y115.718 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 5/15
; update layer progress
M73 L5
M991 S0 P4 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z1.2 I-1.217 J-.015 P1  F30000
G1 X126.052 Y170.647 Z1.2
G1 Z1
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X125.775 Y170.614 E.00856
G3 X126.02 Y167.932 I.309 J-1.324 E.11968
G3 X126.192 Y167.935 I.07 J.981 E.00532
G3 X126.112 Y170.649 I-.109 J1.355 E.12703
; WIPE_START
M204 S10000
G1 X125.775 Y170.614 E-.1285
G1 X125.499 Y170.522 E-.11053
G1 X125.294 Y170.404 E-.09009
G1 X125.112 Y170.251 E-.09009
G1 X124.96 Y170.07 E-.09014
G1 X124.841 Y169.864 E-.09007
G1 X124.734 Y169.526 E-.13493
G1 X124.728 Y169.459 E-.02565
; WIPE_END
G1 E-.04 F1800
G1 X128.305 Y166.111 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X128.28 Y165.989 E.00384
G3 X129.555 Y164.396 I1.34 J-.234 E.07088
G3 X129.728 Y164.399 I.071 J.984 E.00532
G3 X128.36 Y166.266 I-.108 J1.355 E.17744
G1 X128.325 Y166.168 E.00321
; WIPE_START
M204 S10000
G1 X128.28 Y165.989 E-.0702
G1 X128.249 Y165.754 E-.08984
G1 X128.296 Y165.402 E-.13496
G1 X128.377 Y165.179 E-.09008
G1 X128.495 Y164.974 E-.09008
G1 X128.648 Y164.792 E-.09011
G1 X128.829 Y164.64 E-.09014
G1 X129.034 Y164.521 E-.09003
G1 X129.07 Y164.508 E-.01457
; WIPE_END
G1 E-.04 F1800
G1 X123.988 Y158.814 Z1.4 F30000
G1 X118.346 Y152.494 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X118.525 Y152.422 E.00643
G3 X119.072 Y152.339 I.512 J1.535 E.01844
G3 X120 Y152.754 I-.073 J1.408 E.0345
G1 X131.296 Y164.049 E.52988
G3 X131.552 Y165.711 I-1.021 J1.009 E.0596
G1 X131.367 Y165.687 E.00622
G2 X129.457 Y167.5 I-1.75 J.069 E.26626
G1 X129.824 Y167.516 E.0122
G1 X127.836 Y169.505 E.09328
G2 X127.784 Y168.916 I-2.591 J-.07 E.01966
G2 X126.007 Y171.047 I-1.712 J.379 E.25922
G1 X126.031 Y171.233 E.00622
G3 X124.369 Y170.976 I-.657 J-1.257 E.05972
G1 X113.074 Y159.681 E.52988
G3 X112.817 Y158.019 I1 J-1.005 E.05972
G1 X113.003 Y158.043 E.00622
G2 X116.376 Y158.651 I1.754 J-.072 E.15741
G2 X114.913 Y156.23 I-1.628 J-.668 E.10896
G1 X114.545 Y156.214 E.0122
G1 X116.534 Y154.226 E.09328
G2 X117.29 Y155.876 I1.897 J.129 E.0628
G2 X118.363 Y152.683 I1.003 J-1.44 E.21596
G1 X118.345 Y152.549 E.00449
; WIPE_START
G1 X118.525 Y152.422 E-.08382
G1 X118.76 Y152.357 E-.09249
G1 X119.072 Y152.339 E-.11889
G1 X119.365 Y152.384 E-.1123
G1 X119.593 Y152.467 E-.09251
G1 X119.804 Y152.589 E-.09261
G1 X120 Y152.754 E-.09744
G1 X120.131 Y152.884 E-.06995
; WIPE_END
G1 E-.04 F1800
G1 X116.99 Y154.785 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X116.967 Y154.675 E.00347
G3 X118.241 Y153.083 I1.339 J-.234 E.07087
G3 X118.414 Y153.085 I.07 J.983 E.00532
G3 X117.072 Y155.011 I-.108 J1.355 E.1754
G1 X117.011 Y154.842 E.00554
; WIPE_START
M204 S10000
G1 X116.967 Y154.675 E-.06555
G1 X116.935 Y154.44 E-.08982
G1 X116.982 Y154.088 E-.13496
G1 X117.063 Y153.866 E-.09008
G1 X117.181 Y153.66 E-.09009
G1 X117.334 Y153.479 E-.0901
G1 X117.515 Y153.326 E-.09006
G1 X117.721 Y153.208 E-.09011
G1 X117.768 Y153.19 E-.01923
; WIPE_END
G1 E-.04 F1800
G1 X113.419 Y158.19 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X113.411 Y157.976 E.00659
G3 X114.706 Y156.618 I1.359 J0 E.06364
G3 X114.879 Y156.621 I.07 J.981 E.00532
G3 X113.438 Y158.246 I-.109 J1.355 E.18515
; WIPE_START
M204 S10000
G1 X113.411 Y157.976 E-.10312
G1 X113.435 Y157.677 E-.11398
G1 X113.527 Y157.401 E-.1106
G1 X113.646 Y157.196 E-.09009
G1 X113.798 Y157.014 E-.09011
G1 X113.98 Y156.862 E-.09009
G1 X114.185 Y156.743 E-.09012
G1 X114.363 Y156.678 E-.07189
; WIPE_END
G1 E-.04 F1800
G1 X118.197 Y152.14 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X118.249 Y152.117 E.00176
G3 X119.089 Y151.947 I.778 J1.685 E.02658
G3 X120.272 Y152.471 I-.09 J1.799 E.04063
G1 X131.579 Y163.778 E.49136
G3 X131.579 Y166.316 I-1.269 J1.269 E.08661
G1 X126.636 Y171.259 E.21482
G3 X124.098 Y171.259 I-1.269 J-1.269 E.08661
G1 X112.791 Y159.952 E.49135
G3 X112.79 Y157.414 I1.286 J-1.269 E.08645
G1 X117.734 Y152.471 E.21481
G3 X117.978 Y152.271 I1.293 J1.331 E.00973
G1 X118.145 Y152.171 E.00597
M204 S10000
G1 X118.153 Y152.588 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.174512
G1 F15000
G2 X117.493 Y153.054 I11.165 J16.494 E.00866
; LINE_WIDTH: 0.112367
G1 X117.321 Y153.196 E.00126
G1 X117.356 Y153.126 F30000
; LINE_WIDTH: 0.235442
G1 F15000
G1 X118.156 Y152.616 E.01489
G1 X118.159 Y152.636 F30000
; LINE_WIDTH: 0.306737
G1 F13645.862
G1 X117.417 Y153.065 E.01842
G1 X117.453 Y153.029 F30000
; LINE_WIDTH: 0.387719
G1 F10440.891
G3 X117.995 Y152.735 I5.247 J9.026 E.01735
G1 X118.191 Y152.884 E.00692
G1 X118.923 Y152.566 F30000
; LINE_WIDTH: 0.104935
G1 F15000
G1 X119.003 Y152.577 E.00041
; LINE_WIDTH: 0.143604
G1 X119.151 Y152.612 E.00125
; LINE_WIDTH: 0.193537
G3 X119.313 Y152.67 I-.715 J2.259 E.00211
G1 X119.32 Y152.673 E.00009
; LINE_WIDTH: 0.242063
G3 X119.464 Y152.745 I-.741 J1.667 E.0026
G1 X119.544 Y152.795 E.00154
; LINE_WIDTH: 0.284598
G1 F14895.854
G3 X119.759 Y152.97 I-.721 J1.109 E.00546
G1 X120.005 Y153.236 E.00714
; LINE_WIDTH: 0.33131
G1 F12483.118
G1 X120.12 Y153.379 E.00431
; LINE_WIDTH: 0.36592
G1 F11145.518
G1 X120.179 Y153.46 E.00263
; LINE_WIDTH: 0.394212
G1 F10247.899
G1 X120.23 Y153.529 E.00247
; LINE_WIDTH: 0.410175
G1 F9802.46
G1 X120.39 Y153.758 E.00834
; WIPE_START
G1 X120.23 Y153.529 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X117.052 Y153.466 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.11275
G1 F15000
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.157458
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.1905
G1 X116.716 Y153.915 E.00229
G1 X116.758 Y154.027 F30000
; LINE_WIDTH: 0.154984
G1 F15000
G3 X116.809 Y153.673 I7.676 J.94 E.00327
G1 X116.758 Y154.027 F30000
; LINE_WIDTH: 0.106118
G1 F15000
G1 X116.749 Y154.125 E.00051
; WIPE_START
G1 X116.758 Y154.027 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X114.444 Y156.429 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.106119
G1 F15000
G1 X114.346 Y156.438 E.00051
; LINE_WIDTH: 0.154987
G2 X113.992 Y156.489 I.962 J7.843 E.00327
G1 X114.071 Y156.506 F30000
; LINE_WIDTH: 0.190142
G1 F15000
G1 X114.234 Y156.397 E.00235
G1 X114.071 Y156.506 F30000
; LINE_WIDTH: 0.155935
G1 F15000
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112356
G1 X113.786 Y156.732 E.00126
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.112752
G1 F15000
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.174714
G2 X112.908 Y157.833 I14.589 J10.783 E.00863
G1 X112.936 Y157.837 F30000
; LINE_WIDTH: 0.235444
G1 F15000
G1 X113.446 Y157.036 E.01489
G1 X113.383 Y157.099 F30000
; LINE_WIDTH: 0.306746
G1 F13645.376
G1 X112.956 Y157.839 E.01838
G1 X113.203 Y157.872 F30000
; LINE_WIDTH: 0.387815
G1 F10437.957
G1 X113.055 Y157.675 E.00692
G3 X113.352 Y157.13 I8.278 J4.158 E.01747
; WIPE_START
G1 X113.055 Y157.675 E-.54426
G1 X113.203 Y157.872 E-.21574
; WIPE_END
G1 E-.04 F1800
G1 X112.885 Y158.603 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.104948
G1 F15000
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.143649
G2 X112.931 Y158.826 I1.657 J-.315 E.00121
G1 X112.932 Y158.831 E.00004
; LINE_WIDTH: 0.193605
G2 X112.99 Y158.994 I2.26 J-.716 E.00212
G1 X112.993 Y159.001 E.00009
; LINE_WIDTH: 0.242054
G2 X113.065 Y159.144 I1.674 J-.745 E.0026
G1 X113.115 Y159.224 E.00154
; LINE_WIDTH: 0.284601
G1 F14895.674
G2 X113.289 Y159.439 I1.11 J-.722 E.00546
G1 X113.556 Y159.685 E.00714
; LINE_WIDTH: 0.331319
G1 F12482.727
G1 X113.699 Y159.8 E.00431
; LINE_WIDTH: 0.365918
G1 F11145.584
G1 X113.78 Y159.86 E.00263
; LINE_WIDTH: 0.394191
G1 F10248.501
G1 X113.849 Y159.911 E.00247
; LINE_WIDTH: 0.410146
G1 F9803.25
G1 X114.078 Y160.071 E.00835
G1 X116.548 Y162.129 F30000
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X115.396 Y160.977 E.05401
G1 X121.297 Y155.077 E.27681
G1 X125.135 Y158.915 E.18005
G1 X119.234 Y164.815 E.27682
G1 X123.072 Y168.653 E.18005
G1 X128.973 Y162.753 E.27682
G1 X127.822 Y161.601 E.05401
G1 X130.289 Y163.665 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.425244
G1 F9416.103
G1 X130.507 Y163.81 E.00815
; LINE_WIDTH: 0.396773
G1 F10173.72
G1 X130.59 Y163.87 E.00296
; LINE_WIDTH: 0.367981
G1 F11074.859
G1 X130.659 Y163.921 E.00229
; LINE_WIDTH: 0.334074
G1 F12364.61
G1 X130.804 Y164.037 E.0044
; LINE_WIDTH: 0.285093
G1 F14865.424
G3 X131.193 Y164.419 I-1.982 J2.406 E.01076
G1 X131.254 Y164.506 E.0021
; LINE_WIDTH: 0.242063
G1 F15000
G3 X131.376 Y164.73 I-1.079 J.733 E.00415
; LINE_WIDTH: 0.193547
G3 X131.437 Y164.899 I-2.859 J1.126 E.00221
; LINE_WIDTH: 0.143618
G3 X131.473 Y165.047 I-1.842 J.516 E.00125
; LINE_WIDTH: 0.104942
G1 X131.484 Y165.127 E.00041
G1 X131.413 Y165.891 F30000
; LINE_WIDTH: 0.306774
G1 F13643.905
G1 X130.985 Y166.633 E.01842
G1 X131.015 Y166.603 F30000
; LINE_WIDTH: 0.387822
G1 F10437.752
G2 X131.315 Y166.055 I-7.323 J-4.363 E.01757
G1 X131.166 Y165.858 E.00692
G1 X131.433 Y165.894 F30000
; LINE_WIDTH: 0.235387
G1 F15000
G1 X131.16 Y166.323 E.00799
; LINE_WIDTH: 0.220029
G1 X131.122 Y166.38 E.001
; LINE_WIDTH: 0.19188
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155945
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112366
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112755
G1 F15000
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157469
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.190493
G1 X130.135 Y167.334 E.00229
G1 X130.16 Y167.274 F30000
; LINE_WIDTH: 0.164623
G1 F15000
G1 X130.377 Y167.241 E.00218
G1 X130.16 Y167.274 F30000
; LINE_WIDTH: 0.13907
G1 F15000
G1 X130.02 Y167.293 E.00111
; LINE_WIDTH: 0.105812
G1 X129.925 Y167.301 E.00049
; WIPE_START
G1 X130.02 Y167.293 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X128.087 Y167.705 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Sparse infill
; LINE_WIDTH: 0.45
G1 F8843.478
G2 X128.403 Y167.912 I1.338 J-1.703 E.01254
G1 X128.317 Y167.997 E.00403
G1 X116.052 Y155.733 E.57536
G1 X115.966 Y155.819 E.00403
G3 X116.281 Y156.026 I-.998 J1.858 E.01253
G1 X123.565 Y169.659 F30000
; FEATURE: Floating vertical shell
; LINE_WIDTH: 0.383853
G1 F10559.282
G1 X123.66 Y169.726 E.00322
G1 X123.962 Y169.534 E.00992
G1 X123.988 Y168.948 E.0163
G1 X124.149 Y168.415 E.01546
G1 X124.469 Y167.923 E.0163
G3 X126.095 Y167.176 I1.627 J1.396 E.05129
G1 X126.606 Y167.245 E.01433
G1 X127.191 Y167.504 E.01778
G1 X127.677 Y167.912 E.01763
G1 X127.982 Y168.382 E.01557
; LINE_WIDTH: 0.40036
G1 F10071.62
G1 X128.058 Y168.506 E.00422
; LINE_WIDTH: 0.425658
G1 F9405.929
G1 X128.133 Y168.629 E.00452
G1 X128.286 Y168.541 E.00551
; LINE_WIDTH: 0.38292
G1 F10588.235
G1 X128.861 Y167.967 E.02251
; LINE_WIDTH: 0.398575
G1 F10122.169
G1 X128.904 Y167.894 E.00245
; LINE_WIDTH: 0.416303
G1 F9641.576
G1 X128.947 Y167.821 E.00257
G1 X128.477 Y167.528 E.01686
; LINE_WIDTH: 0.383323
G1 F10575.717
G3 X127.974 Y167.094 I.824 J-1.463 E.01855
G1 X127.67 Y166.576 E.01665
G1 X127.505 Y165.963 E.01761
G3 X127.998 Y164.384 I2.241 J-.168 E.04699
G1 X128.276 Y164.115 E.01072
G1 X128.704 Y163.844 E.01405
G3 X129.52 Y163.647 I.864 J1.791 E.02348
G1 X129.846 Y163.648 E.00905
G2 X130.045 Y163.341 I-.537 J-.565 E.01024
G1 X129.979 Y163.246 E.00321
G1 X120.804 Y154.071 E.35991
G1 X120.708 Y154.004 E.00326
G1 X120.403 Y154.205 E.01012
G1 X120.373 Y154.8 E.0165
G3 X120.12 Y155.51 I-2.302 J-.419 E.021
G1 X119.776 Y155.941 E.01532
G1 X119.488 Y156.187 E.01049
G1 X118.945 Y156.444 E.01665
G1 X118.32 Y156.552 E.01761
G1 X117.781 Y156.485 E.01507
G3 X116.45 Y155.472 I.555 J-2.11 E.0476
; LINE_WIDTH: 0.402245
G1 F10018.785
G1 X116.345 Y155.287 E.00623
; LINE_WIDTH: 0.431928
G1 F9254.321
G1 X116.24 Y155.102 E.00675
G1 X116.08 Y155.192 E.00584
; LINE_WIDTH: 0.38292
G1 F10588.235
G1 X115.509 Y155.763 E.02238
; LINE_WIDTH: 0.402335
G1 F10016.276
G1 X115.463 Y155.844 E.0027
; LINE_WIDTH: 0.42883
G1 F9328.619
G1 X115.418 Y155.924 E.0029
G1 X115.543 Y156.025 E.00506
; LINE_WIDTH: 0.383148
G1 F10581.14
G1 X115.923 Y156.213 E.01175
G1 X116.316 Y156.554 E.01441
G1 X116.599 Y156.93 E.01307
G3 X116.867 Y158.145 I-2.042 J1.087 E.0349
G1 X116.713 Y158.766 E.01776
G1 X116.391 Y159.308 E.01747
G1 X115.99 Y159.696 E.01547
G3 X114.529 Y160.083 I-1.259 J-1.805 E.04277
G1 X114.358 Y160.304 E.00777
G1 X114.324 Y160.388 E.00251
G1 X114.391 Y160.485 E.00327
G1 X123.523 Y169.617 E.35805
G1 X123.984 Y169.97 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.425252
G1 F9415.912
G1 X124.13 Y170.187 E.00815
; LINE_WIDTH: 0.396761
G1 F10174.079
G1 X124.19 Y170.27 E.00296
; LINE_WIDTH: 0.367955
G1 F11075.726
G1 X124.241 Y170.34 E.00229
; LINE_WIDTH: 0.334102
G1 F12363.4
G1 X124.357 Y170.485 E.00439
; LINE_WIDTH: 0.285119
G1 F14863.835
G2 X124.739 Y170.873 I2.405 J-1.981 E.01076
G1 X124.825 Y170.935 E.0021
; LINE_WIDTH: 0.242071
G1 F15000
G2 X125.049 Y171.057 I.734 J-1.081 E.00415
; LINE_WIDTH: 0.193562
G2 X125.219 Y171.118 I1.123 J-2.851 E.00221
; LINE_WIDTH: 0.14362
G2 X125.367 Y171.153 I.519 J-1.851 E.00125
; LINE_WIDTH: 0.104939
G1 X125.446 Y171.165 E.00041
G1 X126.211 Y171.094 F30000
; LINE_WIDTH: 0.306776
G1 F13643.825
G1 X126.953 Y170.665 E.01844
G1 X126.923 Y170.695 F30000
; LINE_WIDTH: 0.387814
G1 F10438.003
G3 X126.374 Y170.995 I-4.533 J-7.633 E.01757
G1 X126.178 Y170.846 E.00692
G1 X126.213 Y171.114 F30000
; LINE_WIDTH: 0.235446
G1 F15000
G1 X127.013 Y170.604 E.01488
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.112761
G1 F15000
G1 X126.873 Y170.679 E.00129
; LINE_WIDTH: 0.174707
G3 X126.217 Y171.142 I-10.779 J-14.583 E.00863
G1 X127.318 Y170.264 F30000
; LINE_WIDTH: 0.112345
G1 F15000
G1 X127.46 Y170.093 E.00126
; LINE_WIDTH: 0.15594
G1 X127.544 Y169.978 E.0013
; LINE_WIDTH: 0.190133
G1 X127.653 Y169.815 E.00235
G1 X127.594 Y169.84 F30000
; LINE_WIDTH: 0.164637
G1 F15000
G1 X127.561 Y170.057 E.00217
G1 X127.594 Y169.84 F30000
; LINE_WIDTH: 0.139076
G1 F15000
G1 X127.612 Y169.7 E.00111
; LINE_WIDTH: 0.105824
G1 X127.621 Y169.606 E.00049
; OBJECT_ID: 795
; WIPE_START
G1 X127.612 Y169.7 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 795
M624 AQAAAAAAAAA=
G1 X132.64 Y163.957 Z1.4 F30000
G1 X147.484 Y147 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.065 Y145.694 I-1.309 J-.001 E.18623
G1 X146.169 Y145.69 E.00319
G3 X147.483 Y146.94 I.005 J1.309 E.06155
; WIPE_START
M204 S10000
G1 X147.457 Y147.238 E-.11354
G1 X147.357 Y147.554 E-.12604
G1 X147.242 Y147.752 E-.08675
G1 X147.088 Y147.934 E-.09074
G1 X146.824 Y148.135 E-.12601
G1 X146.617 Y148.231 E-.0868
G1 X146.397 Y148.29 E-.08682
G1 X146.283 Y148.3 E-.0433
; WIPE_END
G1 E-.04 F1800
G1 X150.492 Y141.933 Z1.4 F30000
G1 X152.761 Y138.5 Z1.4
G1 Z1
M73 P63 R3
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X151.342 Y137.194 I-1.309 J-.001 E.18623
G1 X151.446 Y137.19 E.00319
G3 X152.76 Y138.44 I.005 J1.309 E.06155
; WIPE_START
M204 S10000
G1 X152.736 Y138.728 E-.10985
G1 X152.634 Y139.054 E-.12969
G1 X152.519 Y139.252 E-.08679
G1 X152.373 Y139.427 E-.08677
G1 X152.198 Y139.573 E-.08679
G1 X152 Y139.688 E-.0868
G1 X151.674 Y139.79 E-.13
G1 X151.56 Y139.8 E-.04332
; WIPE_END
G1 E-.04 F1800
G1 X158.271 Y136.165 Z1.4 F30000
G1 X162.613 Y133.813 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X161.451 Y134.71 I-1.177 J-.323 E.0484
G1 X150.441 Y134.71 E.33829
G3 X149.236 Y133.505 I.016 J-1.221 E.05798
G1 X149.236 Y130.495 E.09247
G3 X150.441 Y129.29 I1.221 J.016 E.05798
G1 X161.451 Y129.29 E.33829
G3 X162.656 Y130.495 I-.016 J1.221 E.05798
G1 X162.656 Y133.505 E.09247
G3 X162.627 Y133.755 I-1.221 J-.016 E.00774
; WIPE_START
M204 S10000
G1 X162.543 Y134.012 E-.10276
G1 X162.437 Y134.194 E-.08014
G1 X162.302 Y134.356 E-.08015
G1 X162.14 Y134.491 E-.08017
G1 X161.958 Y134.597 E-.08015
G1 X161.759 Y134.669 E-.08016
G1 X161.451 Y134.71 E-.11831
G1 X161.087 Y134.71 E-.13818
; WIPE_END
G1 E-.04 F1800
G1 X153.582 Y133.32 Z1.4 F30000
G1 X145.1 Y131.748 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X146.065 Y129.694 I1.075 J-.748 E.08432
G1 X146.169 Y129.69 E.00319
G3 X145.135 Y131.796 I.005 J1.309 E.16345
; WIPE_START
M204 S10000
G1 X144.938 Y131.448 E-.15204
G1 X144.879 Y131.228 E-.0868
G1 X144.859 Y131 E-.08671
G1 X144.879 Y130.773 E-.08681
G1 X144.942 Y130.542 E-.09074
G1 X145.034 Y130.345 E-.08285
G1 X145.166 Y130.157 E-.08709
G1 X145.335 Y130.003 E-.08696
; WIPE_END
G1 E-.04 F1800
G1 X144.323 Y137.568 Z1.4 F30000
G1 X143.065 Y146.978 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X141.674 Y147.71 I-1.41 J-.993 E.05014
G1 X134.619 Y147.71 E.21677
G3 X133.109 Y145.206 I.016 J-1.717 E.10753
G1 X133.644 Y144.287 E.03266
G2 X134.368 Y135.396 I-10.092 J-5.297 E.28163
G2 X133.109 Y132.795 I-12.327 J4.361 E.08899
G3 X134.619 Y130.29 I1.525 J-.788 E.10753
G1 X141.674 Y130.29 E.21678
G3 X143.379 Y131.995 I-.019 J1.725 E.08206
G1 X143.379 Y146.005 E.43047
G3 X143.098 Y146.929 I-1.725 J-.019 E.03007
; WIPE_START
M204 S10000
G1 X142.878 Y147.209 E-.13551
G1 X142.638 Y147.408 E-.11852
G1 X142.392 Y147.55 E-.10798
G1 X142.098 Y147.655 E-.11854
G1 X141.818 Y147.704 E-.10802
G1 X141.674 Y147.71 E-.05491
G1 X141.367 Y147.71 E-.11652
; WIPE_END
G1 E-.04 F1800
G1 X135.162 Y143.266 Z1.4 F30000
G1 X118.1 Y131.047 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X122.823 Y129.327 I5.569 J7.949 E.15622
G1 X122.915 Y129.323 E.00283
G1 X123.669 Y129.29 E.0232
G3 X118.051 Y131.081 I0 J9.706 E1.6897
; WIPE_START
M204 S10000
G1 X118.814 Y130.591 E-.34472
G1 X119.565 Y130.2 E-.32184
G1 X119.792 Y130.106 E-.09344
; WIPE_END
G1 E-.04 F1800
G1 X125.016 Y135.671 Z1.4 F30000
G1 X157.761 Y170.557 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X158.6 Y151.327 I1.685 J-9.56 E.85897
G1 X158.692 Y151.323 E.00283
G1 X159.446 Y151.29 E.0232
G3 X157.82 Y170.567 I0 J9.707 E.98726
; WIPE_START
M204 S10000
G1 X156.933 Y170.379 E-.3446
G1 X156.125 Y170.125 E-.32188
G1 X155.898 Y170.031 E-.09353
; WIPE_END
G1 E-.04 F1800
G1 X158.707 Y162.934 Z1.4 F30000
G1 X166.948 Y142.115 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X168.156 Y143.741 I-.513 J1.643 E.06655
G1 X168.156 Y150.05 E.19386
G3 X165.652 Y151.56 I-1.717 J-.016 E.10753
G1 X164.733 Y151.025 E.03266
G2 X155.842 Y150.301 I-5.287 J9.976 E.28178
G2 X153.241 Y151.56 I4.36 J12.326 E.08899
G3 X150.761 Y150.337 I-.787 J-1.53 E.09867
G3 X150.736 Y149.334 I5.794 J-.645 E.03087
G3 X151.808 Y147.752 I1.744 J.027 E.06213
G1 X165.816 Y142.156 E.46351
G3 X166.245 Y142.048 I.667 J1.741 E.01364
G3 X166.89 Y142.098 I.189 J1.711 E.01999
; WIPE_START
M204 S10000
G1 X167.219 Y142.22 E-.13304
G1 X167.464 Y142.371 E-.10977
G1 X167.577 Y142.463 E-.05514
G1 X167.682 Y142.563 E-.05508
G1 X167.864 Y142.789 E-.11008
G1 X168.005 Y143.042 E-.11017
G1 X168.101 Y143.315 E-.1101
G1 X168.132 Y143.457 E-.05507
G1 X168.137 Y143.513 E-.02155
; WIPE_END
G1 E-.04 F1800
G1 X168.741 Y138.272 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X167.342 Y137.194 I-1.29 J.228 E.19328
G1 X167.446 Y137.19 E.00319
G3 X168.729 Y138.213 I.005 J1.309 E.05451
; WIPE_START
M204 S10000
G1 X168.756 Y138.5 E-.1095
G1 X168.712 Y138.839 E-.13
G1 X168.633 Y139.055 E-.08709
G1 X168.519 Y139.252 E-.08647
G1 X168.373 Y139.427 E-.08677
G1 X168.198 Y139.573 E-.08679
G1 X168 Y139.688 E-.0868
G1 X167.783 Y139.756 E-.0866
; WIPE_END
G1 E-.04 F1800
G1 X160.341 Y141.455 Z1.4 F30000
G1 X128.211 Y148.79 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X123.367 Y128.214 I-4.533 J-9.791 E1.17571
G1 X158.827 Y127.214 E1.09002
G3 X170.518 Y138.618 I-.09 J11.786 E.55438
G1 X170.235 Y161.131 E.6918
; object ids of layer 5 start: 795,817,839,861
M624 DwAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer5 end: 795,817,839,861
M625
G3 X149.069 Y158.044 I-10.788 J-.139 E1.12892
G1 X149.5 Y156.745 E.04205
G2 X147.22 Y150.888 I-5.035 J-1.413 E.20718
G1 X145.061 Y149.56 E.07788
G2 X142.339 Y148.79 I-2.754 J4.542 E.08796
G1 X128.271 Y148.79 E.4323
; WIPE_START
M204 S10000
G1 X127.301 Y149.16 E-.39452
G1 X126.41 Y149.436 E-.35411
G1 X126.381 Y149.442 E-.01137
; WIPE_END
G1 E-.04 F1800
G1 X133.131 Y145.88 Z1.4 F30000
G1 X164.818 Y129.157 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Top surface
G1 F9547.055
M204 S2000
G1 X168.602 Y132.941 E.16445
; WIPE_START
M204 S10000
G1 X167.188 Y131.527 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.213 Y134.085 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X163.642 Y128.514 E.24211
G1 X162.727 Y128.133
G1 X169.595 Y135.001 E.29846
G1 X169.861 Y135.8
G1 X161.941 Y127.88 E.34419
G1 X161.228 Y127.7
G1 X170.04 Y136.512 E.38292
M73 P64 R3
G1 X170.159 Y137.165
G1 X160.563 Y127.568 E.41699
G1 X159.951 Y127.49
G1 X161.552 Y129.091 E.06959
G1 X161.011 Y129.083
G1 X159.373 Y127.445 E.07116
G1 X158.817 Y127.422
G1 X160.478 Y129.083 E.07216
G1 X159.944 Y129.083
G1 X158.298 Y127.437 E.07153
G1 X157.78 Y127.451
G1 X159.411 Y129.083 E.07089
G1 X158.878 Y129.083
G1 X157.261 Y127.466 E.07026
G1 X156.742 Y127.481
G1 X158.345 Y129.083 E.06962
G1 X157.811 Y129.083
G1 X156.224 Y127.495 E.06899
G1 X155.705 Y127.51
G1 X157.278 Y129.083 E.06835
G1 X156.745 Y129.083
G1 X155.187 Y127.524 E.06772
G1 X154.668 Y127.539
G1 X156.212 Y129.083 E.06708
G1 X155.678 Y129.083
G1 X154.149 Y127.554 E.06644
G1 X153.631 Y127.568
G1 X155.145 Y129.083 E.06581
G1 X154.612 Y129.083
G1 X153.112 Y127.583 E.06517
G1 X152.593 Y127.598
G1 X154.079 Y129.083 E.06454
G1 X153.545 Y129.083
G1 X152.075 Y127.612 E.0639
G1 X151.556 Y127.627
G1 X153.012 Y129.083 E.06327
G1 X152.479 Y129.083
G1 X151.037 Y127.641 E.06263
G1 X150.519 Y127.656
G1 X151.945 Y129.083 E.062
G1 X151.412 Y129.083
G1 X150 Y127.671 E.06136
G1 X149.482 Y127.685
G1 X150.879 Y129.083 E.06072
G1 X150.353 Y129.09
G1 X148.963 Y127.7 E.06039
G1 X148.444 Y127.715
G1 X149.92 Y129.19 E.06411
G1 X149.579 Y129.383
G1 X147.926 Y127.729 E.07186
G1 X147.407 Y127.744
G1 X149.314 Y129.651 E.08287
G1 X149.126 Y129.996
G1 X146.888 Y127.758 E.09723
G1 X146.37 Y127.773
G1 X149.033 Y130.436 E.11573
G1 X149.032 Y130.969
G1 X145.851 Y127.788 E.13824
G1 X145.333 Y127.802
G1 X149.032 Y131.501 E.16074
G1 X149.031 Y132.034
G1 X147.642 Y130.646 E.06033
G1 X147.667 Y131.203
G1 X149.03 Y132.566 E.05923
G1 X149.029 Y133.099
G1 X147.549 Y131.619 E.06431
G1 X147.349 Y131.952
G1 X149.04 Y133.643 E.07349
; WIPE_START
M204 S10000
G1 X147.626 Y132.229 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.527 Y129.53 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X144.814 Y127.817 E.07444
G1 X144.295 Y127.832
G1 X145.965 Y129.501 E.07255
G1 X145.547 Y129.617
G1 X143.777 Y127.846 E.07694
G1 X143.258 Y127.861
G1 X145.222 Y129.825 E.08534
G1 X144.957 Y130.093
G1 X142.739 Y127.875 E.09638
G1 X142.221 Y127.89
G1 X144.771 Y130.44 E.1108
G1 X144.658 Y130.86
G1 X141.702 Y127.905 E.12844
G1 X141.183 Y127.919
G1 X144.732 Y131.468 E.15421
; WIPE_START
M204 S10000
G1 X143.318 Y130.054 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.949 Y130.187 Z1.4 F30000
G1 X162.855 Y130.394 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X170.247 Y137.786 E.3212
G1 X170.29 Y138.362
G1 X162.864 Y130.935 E.32273
G1 X162.864 Y131.469
G1 X170.307 Y138.912 E.32344
; WIPE_START
M204 S10000
G1 X168.892 Y137.497 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.881 Y138.019 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X170.3 Y139.438 E.06167
G1 X170.293 Y139.965
G1 X168.959 Y138.63 E.058
G1 X168.853 Y139.058
G1 X170.287 Y140.492 E.06231
G1 X170.28 Y141.018
G1 X168.66 Y139.398 E.0704
G1 X168.399 Y139.67
G1 X170.274 Y141.545 E.08146
G1 X170.267 Y142.072
G1 X168.076 Y139.881 E.09521
G1 X167.66 Y139.998
G1 X170.26 Y142.598 E.11298
G1 X170.254 Y143.125
G1 X167.105 Y139.976 E.13684
; WIPE_START
M204 S10000
G1 X168.519 Y141.39 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.924 Y137.062 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X162.864 Y132.002 E.21989
G1 X162.864 Y132.535
G1 X167.317 Y136.988 E.19352
G1 X166.889 Y137.093
G1 X162.864 Y133.068 E.1749
G1 X162.856 Y133.595
G1 X166.545 Y137.283 E.16028
G1 X166.271 Y137.542
G1 X162.757 Y134.029 E.15266
M73 P65 R3
G1 X162.561 Y134.366
G1 X166.069 Y137.874 E.15243
G1 X165.948 Y138.286
G1 X162.294 Y134.632 E.15879
G1 X161.952 Y134.823
G1 X165.97 Y138.842 E.17462
; WIPE_START
M204 S10000
G1 X164.556 Y137.427 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X161.509 Y134.913 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X170.247 Y143.652 E.37973
G1 X170.241 Y144.178
G1 X160.976 Y134.913 E.40261
G1 X160.443 Y134.913
G1 X170.234 Y144.705 E.42548
G1 X170.227 Y145.232
G1 X168.312 Y143.316 E.08324
G1 X168.358 Y143.895
G1 X170.221 Y145.758 E.08096
G1 X170.214 Y146.285
G1 X168.358 Y144.428 E.08068
G1 X168.358 Y144.962
G1 X170.208 Y146.811 E.08039
G1 X170.201 Y147.338
G1 X168.358 Y145.495 E.0801
G1 X168.358 Y146.028
G1 X170.194 Y147.865 E.07982
G1 X170.188 Y148.391
G1 X168.358 Y146.561 E.07953
G1 X168.358 Y147.095
G1 X170.181 Y148.918 E.07924
G1 X170.175 Y149.445
G1 X168.358 Y147.628 E.07896
G1 X168.357 Y148.161
G1 X170.168 Y149.971 E.07867
G1 X170.161 Y150.498
G1 X168.357 Y148.694 E.07838
G1 X168.357 Y149.228
G1 X170.155 Y151.025 E.0781
G1 X170.148 Y151.551
G1 X168.357 Y149.761 E.07781
G1 X168.347 Y150.284
G1 X170.141 Y152.078 E.07797
G1 X170.135 Y152.605
G1 X168.243 Y150.713 E.08222
G1 X168.066 Y151.069
G1 X170.128 Y153.131 E.08962
G1 X170.122 Y153.658
G1 X167.833 Y151.369 E.09946
G1 X167.542 Y151.612
G1 X170.115 Y154.185 E.1118
G1 X170.108 Y154.711
G1 X167.201 Y151.804 E.12632
G1 X166.79 Y151.926
G1 X170.102 Y155.238 E.14391
G1 X170.095 Y155.765
G1 X166.284 Y151.953 E.16563
G1 X165.522 Y151.724
G1 X170.089 Y156.291 E.19845
G1 X170.082 Y156.818
G1 X164.322 Y151.058 E.25032
G1 X163.38 Y150.649
G1 X170.075 Y157.345 E.29094
G1 X170.069 Y157.871
G1 X167.678 Y155.48 E.1039
; WIPE_START
M204 S10000
G1 X169.092 Y156.894 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.393 Y156.729 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X170.062 Y158.398 E.07253
G1 X170.056 Y158.925
G1 X168.778 Y157.647 E.05551
G1 X169.024 Y158.426
G1 X170.049 Y159.451 E.04456
G1 X170.042 Y159.978
G1 X169.176 Y159.112 E.03763
G1 X169.275 Y159.743
G1 X170.036 Y160.504 E.03308
G1 X170.029 Y161.031
G1 X169.335 Y160.337 E.03017
G1 X169.359 Y160.894
G1 X170.005 Y161.54 E.02806
G1 X169.976 Y162.045
G1 X169.346 Y161.414 E.02739
G1 X169.319 Y161.921
G1 X169.91 Y162.512 E.0257
G1 X169.84 Y162.975
G1 X169.257 Y162.392 E.02534
G1 X169.184 Y162.853
G1 X169.738 Y163.406 E.02405
G1 X169.636 Y163.837
G1 X169.088 Y163.289 E.02382
G1 X168.98 Y163.714
G1 X169.509 Y164.244 E.02301
G1 X169.379 Y164.647
G1 X168.852 Y164.12 E.02293
G1 X168.715 Y164.516
G1 X169.223 Y165.024 E.0221
G1 X169.066 Y165.4
G1 X168.558 Y164.893 E.02206
G1 X168.397 Y165.264
G1 X168.888 Y165.755 E.02134
G1 X168.703 Y166.104
G1 X168.214 Y165.615 E.02123
G1 X168.031 Y165.965
G1 X168.512 Y166.446 E.0209
G1 X168.305 Y166.772
G1 X167.824 Y166.291 E.02091
G1 X167.616 Y166.617
G1 X168.094 Y167.095 E.02078
G1 X167.864 Y167.398
G1 X167.39 Y166.924 E.02059
G1 X167.158 Y167.226
G1 X167.633 Y167.7 E.02062
G1 X167.384 Y167.985
G1 X166.915 Y167.516 E.0204
G1 X166.66 Y167.794
G1 X167.131 Y168.265 E.02046
G1 X166.868 Y168.536
G1 X166.4 Y168.067 E.02035
G1 X166.122 Y168.322
G1 X166.592 Y168.792 E.02044
G1 X166.316 Y169.049
G1 X165.843 Y168.577 E.02052
G1 X165.544 Y168.81
G1 X166.017 Y169.283 E.02055
G1 X165.718 Y169.518
G1 X165.242 Y169.042 E.02067
G1 X164.925 Y169.258
G1 X165.404 Y169.737 E.02081
G1 X165.081 Y169.948
G1 X164.599 Y169.466 E.02095
G1 X164.263 Y169.663
G1 X164.752 Y170.151 E.02122
G1 X164.405 Y170.338
G1 X163.912 Y169.846 E.0214
G1 X163.556 Y170.022
G1 X164.058 Y170.524 E.02181
G1 X163.686 Y170.686
G1 X163.179 Y170.179 E.02203
G1 X162.799 Y170.332
G1 X163.314 Y170.847 E.02236
G1 X162.92 Y170.986
G1 X162.394 Y170.46 E.02288
G1 X161.986 Y170.586
G1 X162.521 Y171.12 E.02322
G1 X162.102 Y171.235
G1 X161.55 Y170.683 E.024
G1 X161.109 Y170.775
G1 X161.673 Y171.339 E.02452
G1 X161.224 Y171.424
G1 X160.638 Y170.837 E.02548
G1 X160.154 Y170.887
G1 X160.762 Y171.495 E.02641
G1 X160.275 Y171.541
G1 X159.644 Y170.909 E.02744
M73 P66 R3
G1 X159.104 Y170.903
G1 X159.776 Y171.575 E.02919
G1 X159.239 Y171.571
G1 X158.543 Y170.875 E.03023
G1 X157.929 Y170.794
G1 X158.685 Y171.55 E.03285
G1 X158.09 Y171.489
G1 X157.267 Y170.666 E.03577
G1 X156.541 Y170.473
G1 X157.451 Y171.383 E.03952
G1 X156.763 Y171.228
G1 X155.713 Y170.179 E.0456
G1 X154.703 Y169.701
G1 X156.001 Y171 E.05641
G1 X155.113 Y170.644
G1 X153.007 Y168.539 E.0915
; WIPE_START
M204 S10000
G1 X154.421 Y169.953 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X158.413 Y163.448 Z1.4 F30000
G1 X164.966 Y152.768 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X162.576 Y150.378 E.10386
G1 X161.855 Y150.191
G1 X163.718 Y152.053 E.08094
G1 X162.799 Y151.668
G1 X161.189 Y150.058 E.06998
G1 X160.581 Y149.983
G1 X162.02 Y151.423 E.06255
G1 X161.334 Y151.27
G1 X160.005 Y149.941 E.05776
G1 X159.449 Y149.918
G1 X160.703 Y151.172 E.05448
G1 X160.109 Y151.111
G1 X158.937 Y149.939 E.05096
G1 X158.433 Y149.968
G1 X159.552 Y151.087 E.04861
G1 X159.032 Y151.1
G1 X157.958 Y150.026 E.04667
G1 X157.495 Y150.096
G1 X158.532 Y151.134 E.04507
G1 X158.057 Y151.192
G1 X157.053 Y150.188 E.04365
G1 X156.621 Y150.289
G1 X157.594 Y151.262 E.04226
G1 X157.157 Y151.359
G1 X156.208 Y150.41 E.04123
G1 X155.803 Y150.538
G1 X156.732 Y151.467 E.04036
G1 X156.327 Y151.595
G1 X155.418 Y150.686 E.0395
G1 X155.034 Y150.835
G1 X155.93 Y151.732 E.03894
G1 X155.553 Y151.888
G1 X154.674 Y151.008 E.03823
G1 X154.313 Y151.181
G1 X155.182 Y152.05 E.03775
G1 X154.831 Y152.232
G1 X153.97 Y151.371 E.03742
G1 X153.63 Y151.564
G1 X154.481 Y152.415 E.03697
G1 X154.155 Y152.623
G1 X153.29 Y151.758 E.03759
G1 X152.905 Y151.906
G1 X153.829 Y152.83 E.04017
G1 X153.522 Y153.056
G1 X152.427 Y151.961 E.0476
G1 X151.772 Y151.84
G1 X153.221 Y153.288 E.06294
; WIPE_START
M204 S10000
G1 X151.806 Y151.874 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X158.168 Y147.657 Z1.4 F30000
G1 X166.879 Y141.883 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X159.91 Y134.914 E.30287
G1 X159.376 Y134.914
G1 X166.303 Y141.84 E.30099
G1 X165.856 Y141.927
G1 X158.843 Y134.914 E.30474
G1 X158.31 Y134.914
G1 X165.468 Y142.072 E.31102
G1 X165.087 Y142.224
G1 X157.777 Y134.915 E.31762
G1 X157.244 Y134.915
G1 X164.706 Y142.376 E.32423
G1 X164.325 Y142.528
G1 X156.711 Y134.915 E.33083
G1 X156.178 Y134.915
G1 X163.943 Y142.68 E.33744
G1 X163.562 Y142.833
G1 X155.645 Y134.915 E.34404
G1 X155.112 Y134.916
G1 X163.181 Y142.985 E.35065
G1 X162.8 Y143.137
G1 X154.579 Y134.916 E.35726
G1 X154.046 Y134.916
G1 X162.419 Y143.289 E.36386
G1 X162.038 Y143.442
G1 X153.513 Y134.916 E.37047
G1 X152.98 Y134.916
G1 X161.657 Y143.594 E.37707
G1 X161.276 Y143.746
G1 X152.447 Y134.917 E.38368
G1 X151.914 Y134.917
G1 X160.895 Y143.898 E.39028
G1 X160.514 Y144.05
G1 X151.381 Y134.917 E.39689
G1 X150.848 Y134.917
G1 X160.133 Y144.203 E.40349
G1 X159.752 Y144.355
G1 X150.303 Y134.906 E.4106
; WIPE_START
M204 S10000
G1 X151.717 Y136.32 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X151.927 Y137.063 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X147.076 Y132.212 E.21079
G1 X146.735 Y132.404
G1 X151.319 Y136.988 E.1992
G1 X150.89 Y137.093
M73 P67 R3
G1 X146.309 Y132.511 E.19908
G1 X145.705 Y132.441
G1 X150.546 Y137.282 E.21036
G1 X150.271 Y137.541
G1 X140.665 Y127.934 E.41746
G1 X140.146 Y127.949
G1 X142.456 Y130.258 E.10037
G1 X141.753 Y130.089
G1 X139.628 Y127.963 E.09237
G1 X139.109 Y127.978
G1 X141.22 Y130.089 E.09172
G1 X140.686 Y130.088
G1 X138.59 Y127.992 E.09106
G1 X138.072 Y128.007
G1 X140.152 Y130.088 E.09041
G1 X139.618 Y130.087
G1 X137.553 Y128.022 E.08975
G1 X137.034 Y128.036
G1 X139.085 Y130.087 E.0891
G1 X138.551 Y130.086
G1 X136.516 Y128.051 E.08844
G1 X135.997 Y128.066
G1 X138.017 Y130.086 E.08778
G1 X137.484 Y130.085
G1 X135.479 Y128.08 E.08713
G1 X134.96 Y128.095
G1 X136.95 Y130.085 E.08647
G1 X136.416 Y130.084
G1 X134.441 Y128.109 E.08582
G1 X133.923 Y128.124
G1 X135.882 Y130.084 E.08516
G1 X135.349 Y130.083
G1 X133.404 Y128.139 E.0845
G1 X132.885 Y128.153
G1 X134.815 Y130.083 E.08385
G1 X134.308 Y130.109
G1 X132.367 Y128.168 E.08434
G1 X131.848 Y128.183
G1 X133.896 Y130.231 E.08901
G1 X133.546 Y130.414
G1 X131.329 Y128.197 E.09632
G1 X130.811 Y128.212
G1 X133.258 Y130.659 E.10636
G1 X133.021 Y130.956
G1 X130.292 Y128.226 E.1186
G1 X129.774 Y128.241
G1 X132.841 Y131.309 E.13332
G1 X132.728 Y131.729
G1 X129.255 Y128.256 E.15093
G1 X128.736 Y128.27
G1 X132.723 Y132.257 E.17326
G1 X133.09 Y133.157
G1 X128.218 Y128.285 E.2117
G1 X127.699 Y128.3
G1 X133.692 Y134.293 E.26043
G1 X134.074 Y135.208
G1 X127.18 Y128.314 E.29957
G1 X126.662 Y128.329
G1 X128.948 Y130.615 E.09933
; WIPE_START
M204 S10000
G1 X127.533 Y129.201 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X127.776 Y129.977 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X126.143 Y128.343 E.07097
G1 X125.625 Y128.358
G1 X126.894 Y129.628 E.05517
G1 X126.13 Y129.397
G1 X125.106 Y128.373 E.0445
G1 X124.587 Y128.387
G1 X125.445 Y129.245 E.03726
G1 X124.825 Y129.158
G1 X124.069 Y128.402 E.03287
G1 X123.55 Y128.417
G1 X124.241 Y129.107 E.03001
G1 X123.683 Y129.083
G1 X123.045 Y128.445 E.02771
G1 X122.548 Y128.481
G1 X123.171 Y129.104 E.02708
G1 X122.677 Y129.143
G1 X122.081 Y128.547 E.02589
G1 X121.621 Y128.621
G1 X122.202 Y129.202 E.02524
G1 X121.745 Y129.278
G1 X121.189 Y128.722 E.02414
G1 X120.763 Y128.829
G1 X121.308 Y129.375 E.02372
G1 X120.888 Y129.488
G1 X120.359 Y128.958 E.023
G1 X119.962 Y129.095
G1 X120.483 Y129.616 E.02263
G1 X120.091 Y129.757
G1 X119.582 Y129.247 E.02215
G1 X119.212 Y129.411
G1 X119.714 Y129.913 E.02182
G1 X119.347 Y130.08
G1 X118.851 Y129.584 E.02155
G1 X118.507 Y129.773
G1 X118.996 Y130.262 E.02125
G1 X118.65 Y130.449
G1 X118.164 Y129.963 E.02114
G1 X117.844 Y130.177
G1 X118.325 Y130.657 E.02086
G1 X117.999 Y130.864
G1 X117.525 Y130.391 E.02059
G1 X117.221 Y130.619
G1 X117.696 Y131.094 E.02065
G1 X117.394 Y131.326
G1 X116.925 Y130.857 E.02039
G1 X116.634 Y131.099
G1 X117.112 Y131.577 E.02075
G1 X116.831 Y131.83
G1 X116.361 Y131.36 E.02041
G1 X116.089 Y131.621
G1 X116.56 Y132.092 E.02048
G1 X116.305 Y132.37
G1 X115.834 Y131.9 E.02045
G1 X115.585 Y132.183
G1 X116.052 Y132.65 E.0203
G1 X115.821 Y132.952
G1 X115.344 Y132.476 E.02071
G1 X115.118 Y132.783
G1 X115.589 Y133.254 E.02048
G1 X115.377 Y133.575
G1 X114.896 Y133.094 E.0209
G1 X114.692 Y133.423
G1 X115.169 Y133.901 E.02076
G1 X114.976 Y134.241
G1 X114.487 Y133.752 E.02124
G1 X114.3 Y134.098
G1 X114.794 Y134.591 E.02146
G1 X114.621 Y134.952
G1 X114.122 Y134.453 E.02167
G1 X113.954 Y134.818
G1 X114.465 Y135.329 E.02222
G1 X114.316 Y135.714
G1 X113.803 Y135.2 E.02231
G1 X113.655 Y135.586
G1 X114.188 Y136.119 E.02319
G1 X114.067 Y136.532
G1 X113.532 Y135.996 E.02325
G1 X113.41 Y136.407
G1 X113.971 Y136.968 E.02436
G1 X113.884 Y137.415
G1 X113.318 Y136.849 E.0246
G1 X113.227 Y137.291
G1 X113.822 Y137.886 E.02586
G1 X113.779 Y138.376
G1 X113.169 Y137.766 E.02649
G1 X113.115 Y138.245
G1 X113.756 Y138.887 E.02788
G1 X113.77 Y139.434
G1 X113.099 Y138.763 E.02917
G1 X113.102 Y139.299
G1 X113.807 Y140.004 E.03064
G1 X113.888 Y140.618
G1 X113.13 Y139.86 E.03296
G1 X113.198 Y140.462
G1 X114.028 Y141.292 E.03607
G1 X114.236 Y142.033
G1 X113.303 Y141.099 E.04056
G1 X113.465 Y141.795
G1 X114.552 Y142.882 E.04727
M73 P68 R3
G1 X115.077 Y143.94
G1 X113.716 Y142.579 E.05913
; WIPE_START
M204 S10000
G1 X115.077 Y143.94 E-.73128
G1 X115.043 Y143.872 E-.02872
; WIPE_END
G1 E-.04 F1800
G1 X121.597 Y139.961 Z1.4 F30000
G1 X132.054 Y133.722 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X134.327 Y135.994 E.09875
G1 X134.498 Y136.698
G1 X132.692 Y134.893 E.07845
G1 X133.041 Y135.775
G1 X134.624 Y137.357 E.06876
G1 X134.698 Y137.965
G1 X133.272 Y136.539 E.06196
G1 X133.424 Y137.224
G1 X134.732 Y138.532 E.05684
G1 X134.748 Y139.081
G1 X133.511 Y137.844 E.05377
G1 X133.562 Y138.429
G1 X134.727 Y139.594 E.05064
G1 X134.691 Y140.091
G1 X133.586 Y138.986 E.04802
G1 X133.565 Y139.498
G1 X134.633 Y140.566 E.04641
G1 X134.558 Y141.024
G1 X133.532 Y139.998 E.04459
G1 X133.469 Y140.469
G1 X134.467 Y141.466 E.04333
G1 X134.36 Y141.893
G1 X133.391 Y140.924 E.04209
G1 X133.295 Y141.361
G1 X134.239 Y142.306 E.04105
G1 X134.107 Y142.706
G1 X133.181 Y141.781 E.04022
G1 X133.054 Y142.186
G1 X133.959 Y143.092 E.03936
G1 X133.805 Y143.471
G1 X132.912 Y142.578 E.03883
G1 X132.756 Y142.955
G1 X133.633 Y143.832 E.03811
G1 X133.46 Y144.192
G1 X132.59 Y143.322 E.03781
G1 X132.407 Y143.673
G1 X133.263 Y144.529 E.03721
G1 X133.067 Y144.866
G1 X132.22 Y144.019 E.03681
G1 X132.012 Y144.345
G1 X132.878 Y145.21 E.0376
G1 X132.748 Y145.613
G1 X131.805 Y144.67 E.04098
G1 X131.575 Y144.973
G1 X132.715 Y146.114 E.04954
G1 X132.894 Y146.826
G1 X131.343 Y145.275 E.06741
; WIPE_START
M204 S10000
G1 X132.757 Y146.689 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X137.089 Y140.405 Z1.4 F30000
G1 X143.419 Y131.222 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X150.07 Y137.872 E.289
G1 X149.948 Y138.283
G1 X143.583 Y131.919 E.27657
G1 X143.586 Y132.455
G1 X149.97 Y138.839 E.2774
; WIPE_START
M204 S10000
G1 X148.556 Y137.425 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X152.879 Y138.016 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X159.371 Y144.507 E.28209
G1 X158.99 Y144.659
G1 X152.959 Y138.628 E.26209
G1 X152.849 Y139.051
G1 X158.609 Y144.812 E.2503
G1 X158.228 Y144.964
G1 X152.663 Y139.399 E.24181
G1 X152.4 Y139.669
G1 X157.847 Y145.116 E.23669
G1 X157.466 Y145.268
G1 X152.078 Y139.88 E.23415
G1 X151.662 Y139.998
G1 X157.085 Y145.42 E.23564
G1 X156.704 Y145.573
G1 X151.107 Y139.976 E.24319
; WIPE_START
M204 S10000
G1 X152.522 Y141.391 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X156.323 Y145.725 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.586 Y132.988 E.55347
G1 X143.586 Y133.521
G1 X155.942 Y145.877 E.53692
G1 X155.561 Y146.029
G1 X143.586 Y134.054 E.52038
G1 X143.585 Y134.587
G1 X155.18 Y146.182 E.50383
G1 X154.799 Y146.334
G1 X143.585 Y135.12 E.48728
G1 X143.585 Y135.653
G1 X154.418 Y146.486 E.47073
G1 X154.037 Y146.638
G1 X143.585 Y136.186 E.45419
G1 X143.584 Y136.719
G1 X153.655 Y146.79 E.43764
G1 X153.274 Y146.943
G1 X143.584 Y137.252 E.42109
G1 X143.584 Y137.785
G1 X152.893 Y147.095 E.40454
G1 X152.512 Y147.247
G1 X143.584 Y138.318 E.388
G1 X143.583 Y138.851
G1 X152.131 Y147.399 E.37145
M73 P69 R3
G1 X151.75 Y147.552
G1 X143.583 Y139.384 E.3549
G1 X143.583 Y139.917
G1 X151.4 Y147.735 E.3397
G1 X151.103 Y147.971
G1 X143.583 Y140.45 E.32681
G1 X143.582 Y140.983
G1 X150.86 Y148.261 E.31623
G1 X150.677 Y148.611
G1 X143.582 Y141.516 E.3083
G1 X143.582 Y142.049
G1 X150.555 Y149.022 E.303
G1 X150.53 Y149.531
G1 X147.642 Y146.643 E.12551
G1 X147.667 Y147.202
G1 X150.534 Y150.068 E.12456
G1 X150.66 Y150.727
G1 X147.55 Y147.617 E.13514
G1 X147.35 Y147.951
G1 X152.935 Y153.535 E.24268
G1 X152.654 Y153.788
G1 X147.077 Y148.211 E.24235
G1 X146.736 Y148.403
G1 X152.379 Y154.046 E.24521
G1 X152.124 Y154.324
G1 X146.311 Y148.511 E.25262
G1 X145.709 Y148.442
G1 X151.869 Y154.603 E.26771
G1 X151.636 Y154.903
G1 X148.842 Y152.109 E.1214
; WIPE_START
M204 S10000
G1 X150.256 Y153.523 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.513 Y153.313 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X151.404 Y155.204 E.08219
G1 X151.188 Y155.522
G1 X149.761 Y154.094 E.06202
G1 X149.868 Y154.734
G1 X150.981 Y155.847 E.04836
G1 X150.783 Y156.183
G1 X149.901 Y155.301 E.03833
G1 X149.88 Y155.813
G1 X150.601 Y156.534 E.03131
G1 X150.424 Y156.89
G1 X149.817 Y156.283 E.02638
G1 X149.719 Y156.719
G1 X150.268 Y157.267 E.02384
G1 X150.114 Y157.647
G1 X149.592 Y157.125 E.02269
G1 X149.459 Y157.526
G1 X149.986 Y158.053 E.0229
G1 X149.86 Y158.46
G1 X149.327 Y157.926 E.02319
G1 X149.211 Y158.343
G1 X149.764 Y158.896 E.02403
G1 X149.671 Y159.337
G1 X149.108 Y158.774 E.02449
G1 X149.022 Y159.221
G1 X149.609 Y159.808 E.02551
G1 X149.559 Y160.292
G1 X148.952 Y159.685 E.02638
G1 X148.905 Y160.171
G1 X149.537 Y160.803 E.02746
G1 X149.543 Y161.342
G1 X148.873 Y160.672 E.02914
G1 X148.876 Y161.208
G1 X149.571 Y161.903 E.03023
G1 X149.652 Y162.518
G1 X148.895 Y161.76 E.03291
G1 X148.958 Y162.357
G1 X149.78 Y163.179 E.03573
G1 X149.973 Y163.905
G1 X149.064 Y162.995 E.03951
G1 X149.217 Y163.683
G1 X150.268 Y164.733 E.04564
G1 X150.745 Y165.743
G1 X149.445 Y164.444 E.05648
G1 X149.796 Y165.328
G1 X151.907 Y167.439 E.09172
; WIPE_START
M204 S10000
G1 X150.493 Y166.025 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.387 Y166.452 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X153.996 Y170.061 E.15681
; WIPE_START
M204 S10000
G1 X152.581 Y168.646 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.648 Y161.263 Z1.4 F30000
G1 X146.53 Y145.531 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.582 Y142.583 E.12812
G1 X143.581 Y143.116
G1 X145.967 Y145.501 E.10365
G1 X145.549 Y145.616
G1 X143.581 Y143.649 E.0855
G1 X143.581 Y144.182
G1 X145.223 Y145.824 E.07136
G1 X144.958 Y146.092
G1 X143.581 Y144.715 E.05986
G1 X143.581 Y145.248
G1 X144.771 Y146.438 E.05174
G1 X144.658 Y146.858
G1 X143.58 Y145.781 E.04684
G1 X143.563 Y146.296
G1 X144.731 Y147.464 E.05076
; WIPE_START
M204 S10000
G1 X143.563 Y146.296 E-.62776
G1 X143.575 Y145.948 E-.13224
; WIPE_END
G1 E-.04 F1800
G1 X147.684 Y150.951 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.446 Y146.712 E.1842
G1 X143.263 Y147.063
G1 X146.244 Y150.044 E.12951
; WIPE_START
M204 S10000
G1 X144.83 Y148.63 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X144.896 Y149.229 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.024 Y147.357 E.08135
G1 X142.726 Y147.593
G1 X143.97 Y148.837 E.05405
G1 X143.266 Y148.666
G1 X142.376 Y147.776 E.03866
G1 X141.957 Y147.89
G1 X142.662 Y148.595 E.03064
G1 X142.116 Y148.583
G1 X141.451 Y147.917 E.02892
G1 X140.917 Y147.917
G1 X141.583 Y148.583 E.02894
G1 X141.05 Y148.583
G1 X140.383 Y147.916 E.02896
G1 X139.85 Y147.916
G1 X140.517 Y148.583 E.02898
G1 X139.983 Y148.583
G1 X139.316 Y147.915 E.029
G1 X138.782 Y147.915
G1 X139.45 Y148.583 E.02901
G1 X138.917 Y148.583
M73 P70 R3
G1 X138.249 Y147.915 E.02903
G1 X137.715 Y147.914
G1 X138.384 Y148.583 E.02905
G1 X137.85 Y148.583
G1 X137.181 Y147.914 E.02907
G1 X136.648 Y147.913
G1 X137.317 Y148.583 E.02909
G1 X136.784 Y148.583
G1 X136.114 Y147.913 E.02911
G1 X135.58 Y147.912
G1 X136.25 Y148.583 E.02913
G1 X135.717 Y148.583
G1 X135.046 Y147.912 E.02915
G1 X134.513 Y147.911
G1 X135.184 Y148.583 E.02917
G1 X134.651 Y148.583
G1 X133.788 Y147.72 E.03751
G1 X134.117 Y148.583
G1 X131.096 Y145.561 E.1313
G1 X130.841 Y145.84
G1 X133.584 Y148.583 E.11921
G1 X133.051 Y148.583
G1 X130.577 Y146.109 E.10749
G1 X130.299 Y146.364
G1 X132.518 Y148.583 E.09641
G1 X131.984 Y148.583
G1 X130.019 Y146.617 E.08542
G1 X129.717 Y146.849
G1 X131.451 Y148.583 E.07536
G1 X130.918 Y148.583
G1 X129.415 Y147.08 E.0653
G1 X129.094 Y147.292
G1 X130.385 Y148.583 E.05608
G1 X129.851 Y148.583
G1 X128.768 Y147.5 E.04706
G1 X128.428 Y147.693
G1 X129.318 Y148.583 E.03866
G1 X128.785 Y148.583
G1 X128.078 Y147.876 E.03073
G1 X127.717 Y148.048
G1 X128.252 Y148.583 E.02323
G1 X127.849 Y148.713
G1 X127.34 Y148.204 E.02212
G1 X126.955 Y148.353
G1 X127.47 Y148.868 E.02236
G1 X127.081 Y149.011
G1 X126.55 Y148.481 E.02305
G1 X126.138 Y148.602
G1 X126.673 Y149.137 E.02328
G1 X126.259 Y149.256
G1 X125.701 Y148.698 E.02425
G1 X125.255 Y148.785
G1 X125.821 Y149.352 E.02461
G1 X125.376 Y149.44
G1 X124.783 Y148.847 E.02577
G1 X124.293 Y148.891
G1 X124.904 Y149.501 E.02651
G1 X124.42 Y149.551
G1 X123.783 Y148.913 E.02771
G1 X123.235 Y148.899
G1 X123.908 Y149.572 E.02923
G1 X123.373 Y149.57
G1 X122.665 Y148.862 E.03078
G1 X122.051 Y148.781
G1 X122.814 Y149.544 E.03318
G1 X122.208 Y149.471
G1 X121.378 Y148.641 E.03608
G1 X120.636 Y148.433
G1 X121.566 Y149.363 E.04041
G1 X120.874 Y149.204
G1 X119.787 Y148.117 E.04725
G1 X118.743 Y147.606
G1 X120.096 Y148.959 E.05879
G1 X119.19 Y148.586
G1 X114.087 Y143.483 E.22175
; WIPE_START
M204 S10000
G1 X115.501 Y144.898 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X114.754 Y144.684 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X117.985 Y147.914 E.14037
; WIPE_START
M204 S10000
G1 X116.57 Y146.5 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X123.914 Y144.42 Z1.4 F30000
G1 X167.915 Y131.957 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.1075
G1 F15000
G1 X167.677 Y131.691 E.00188
; LINE_WIDTH: 0.146177
G1 X167.439 Y131.425 E.003
; LINE_WIDTH: 0.170591
G2 X166.034 Y130.042 I-16.882 J15.752 E.02052
; LINE_WIDTH: 0.110869
G1 X165.779 Y129.821 E.00187
; WIPE_START
G1 X166.034 Y130.042 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X164.757 Y129.217 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.206018
G1 F15000
G1 X164.579 Y129.076 E.00302
; LINE_WIDTH: 0.164578
G1 X164.401 Y128.935 E.00225
; LINE_WIDTH: 0.129936
G1 X164.32 Y128.877 E.00071
; LINE_WIDTH: 0.102093
G1 X164.239 Y128.818 E.00048
; WIPE_START
G1 X164.32 Y128.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X162.923 Y130.326 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.167319
G1 F15000
G2 X162.798 Y130.081 I-2.361 J1.055 E.00279
; WIPE_START
G1 X162.923 Y130.326 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X155.293 Y130.163 Z1.4 F30000
G1 X149.11 Y130.031 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.126713
G1 F15000
G1 X149.053 Y130.129 E.00077
G1 X149.08 Y130.217 E.00063
; WIPE_START
G1 X149.053 Y130.129 E-.3399
G1 X149.11 Y130.031 E-.4201
; WIPE_END
G1 E-.04 F1800
G1 X141.488 Y129.641 Z1.4 F30000
G1 X121.599 Y128.621 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.09581
G1 F15000
G1 X121.437 Y128.703 E.00078
; WIPE_START
G1 X121.599 Y128.621 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X118.167 Y135.439 Z1.4 F30000
G1 X114.149 Y143.421 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.190635
G1 F15000
G1 X114.069 Y143.302 E.00173
; LINE_WIDTH: 0.149651
G1 X113.988 Y143.183 E.00125
; LINE_WIDTH: 0.108667
G1 X113.908 Y143.064 E.00077
; WIPE_START
G1 X113.988 Y143.183 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X114.815 Y144.623 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.21442
G1 F15000
G1 X114.7 Y144.482 E.00254
; LINE_WIDTH: 0.185939
G1 X114.586 Y144.34 E.00212
; LINE_WIDTH: 0.150824
G1 X114.495 Y144.218 E.00134
; LINE_WIDTH: 0.109058
G1 X114.405 Y144.095 E.00082
; WIPE_START
G1 X114.495 Y144.218 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.47 Y144.571 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.100707
G1 F15000
G1 X115.394 Y144.476 E.00058
; LINE_WIDTH: 0.125771
G1 X115.318 Y144.38 E.00082
; LINE_WIDTH: 0.16048
G1 X115.167 Y144.19 E.00232
; LINE_WIDTH: 0.204849
G1 X115.016 Y144.001 E.0032
; WIPE_START
G1 X115.167 Y144.19 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.92 Y147.148 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.111626
G1 F15000
G3 X115.545 Y145.772 I18.002 J-19.361 E.01089
; WIPE_START
G1 X116.244 Y146.504 E-.39552
G1 X116.92 Y147.148 E-.36448
; WIPE_END
G1 E-.04 F1800
G1 X118.681 Y147.668 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.202172
G1 F15000
G1 X118.488 Y147.513 E.00321
; LINE_WIDTH: 0.156571
G1 X118.295 Y147.358 E.00229
; LINE_WIDTH: 0.110971
G1 X118.102 Y147.203 E.00137
; WIPE_START
G1 X118.295 Y147.358 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X118.58 Y148.27 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.101734
G1 F15000
G1 X118.499 Y148.211 E.00048
; LINE_WIDTH: 0.12888
G1 X118.419 Y148.152 E.0007
; LINE_WIDTH: 0.163738
G1 X118.232 Y148.003 E.00235
; LINE_WIDTH: 0.206296
G1 X118.045 Y147.854 E.00318
; WIPE_START
G1 X118.232 Y148.003 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X121.879 Y149.431 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0994367
G1 F15000
G1 X121.624 Y149.305 E.00131
; WIPE_START
G1 X121.879 Y149.431 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X129.493 Y148.893 Z1.4 F30000
G1 X134.351 Y148.549 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108274
G1 F15000
G1 X134.168 Y148.583 E.00099
G1 X134.526 Y147.898 F30000
; LINE_WIDTH: 0.104395
G1 F15000
G1 X134.311 Y147.976 E.00115
; WIPE_START
G1 X134.526 Y147.898 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.126 Y148.602 Z1.4 F30000
G1 X144.193 Y148.793 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.10974
G1 F15000
G1 X143.956 Y148.85 E.00133
; WIPE_START
G1 X144.193 Y148.793 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.474 Y149.569 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108046
G1 F15000
G1 X145.332 Y149.457 E.00096
; LINE_WIDTH: 0.148082
G1 X145.187 Y149.343 E.00158
; LINE_WIDTH: 0.181809
G1 X145.072 Y149.256 E.00163
; LINE_WIDTH: 0.208801
G1 X144.957 Y149.168 E.00195
; WIPE_START
G1 X145.072 Y149.256 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.859 Y150.421 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.111183
G1 F15000
G1 X146.674 Y150.275 E.00131
; LINE_WIDTH: 0.157219
G1 X146.489 Y150.129 E.00219
; LINE_WIDTH: 0.203255
G1 X146.305 Y149.983 E.00308
; WIPE_START
G1 X146.489 Y150.129 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X148.902 Y152.049 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.201828
G1 F15000
G1 X148.453 Y151.555 E.00864
M73 P71 R3
G1 X148.112 Y151.22 E.0062
; LINE_WIDTH: 0.216019
G1 X147.746 Y150.89 E.00695
; WIPE_START
G1 X148.112 Y151.22 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.578 Y153.248 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.178945
G1 F15000
G1 X149.489 Y153.118 E.00175
; LINE_WIDTH: 0.155429
G1 X149.402 Y152.997 E.00137
; LINE_WIDTH: 0.110593
G1 X149.315 Y152.876 E.00082
; WIPE_START
G1 X149.402 Y152.997 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.811 Y153.878 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.133613
G1 F15000
G1 X149.748 Y154.107 E.00175
; WIPE_START
G1 X149.811 Y153.878 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.716 Y161.51 Z1.4 F30000
G1 X149.699 Y162.811 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.128967
G1 F15000
G1 X149.583 Y162.587 E.00177
; WIPE_START
G1 X149.699 Y162.811 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.508 Y164.381 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.203528
G1 F15000
G1 X149.32 Y164.091 E.00452
; WIPE_START
G1 X149.508 Y164.381 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X151.089 Y166.326 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.11066
G1 F15000
G1 X150.953 Y166.156 E.0012
; LINE_WIDTH: 0.15625
G1 X150.813 Y165.981 E.00207
; LINE_WIDTH: 0.199368
G1 X150.683 Y165.805 E.00279
G1 X150.448 Y166.391 F30000
; LINE_WIDTH: 0.205358
G1 F15000
G1 X150.338 Y166.248 E.00238
; LINE_WIDTH: 0.167467
G1 X150.227 Y166.106 E.00183
; LINE_WIDTH: 0.129576
G1 X150.117 Y165.964 E.00127
; LINE_WIDTH: 0.0993881
G1 X150.066 Y165.891 E.00041
; WIPE_START
G1 X150.117 Y165.964 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X152.947 Y168.599 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.230953
G1 F15000
G3 X151.847 Y167.499 I12.119 J-13.218 E.02384
; WIPE_START
G1 X152.383 Y168.058 E-.37818
G1 X152.947 Y168.599 E-.38182
; WIPE_END
G1 E-.04 F1800
G1 X153.097 Y169.458 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0971577
G1 F15000
G1 X152.999 Y169.376 E.00056
; LINE_WIDTH: 0.125668
G1 X152.668 Y169.072 E.00303
; LINE_WIDTH: 0.178137
G3 X151.702 Y168.135 I10.512 J-11.799 E.01483
; LINE_WIDTH: 0.166844
G1 X151.398 Y167.804 E.00454
; LINE_WIDTH: 0.129295
G1 X151.093 Y167.473 E.00316
; LINE_WIDTH: 0.0993593
G1 X150.993 Y167.354 E.00071
; WIPE_START
G1 X151.093 Y167.473 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.641 Y169.763 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.198832
G1 F15000
G1 X154.46 Y169.63 E.00285
; LINE_WIDTH: 0.155632
G1 X154.291 Y169.493 E.002
; LINE_WIDTH: 0.110658
G1 X154.121 Y169.357 E.0012
; WIPE_START
G1 X154.291 Y169.493 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.545 Y170.37 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.105134
G1 F15000
G1 X154.443 Y170.298 E.00063
; LINE_WIDTH: 0.139096
G1 X154.314 Y170.198 E.00128
; LINE_WIDTH: 0.173039
G1 X154.185 Y170.099 E.00173
; LINE_WIDTH: 0.206982
G1 X154.056 Y170 E.00218
; WIPE_START
G1 X154.185 Y170.099 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X157.859 Y170.863 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.128953
G1 F15000
G1 X157.635 Y170.747 E.00177
; WIPE_START
G1 X157.859 Y170.863 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X163.483 Y165.702 Z1.4 F30000
M73 P71 R2
G1 X169.406 Y160.266 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.118671
G1 F15000
G1 X169.316 Y160.071 E.00133
; WIPE_START
G1 X169.406 Y160.266 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.805 Y152.644 Z1.4 F30000
G1 X170.134 Y146.365 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0910721
G1 F15000
G1 X170.23 Y146.556 E.00084
; WIPE_START
G1 X170.134 Y146.365 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.068 Y138.807 Z1.4 F30000
G1 X168.948 Y137.952 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.18129
G1 F15000
G1 X168.864 Y137.832 E.00165
; LINE_WIDTH: 0.161676
G1 X168.783 Y137.726 E.0013
; LINE_WIDTH: 0.125803
G1 X168.696 Y137.614 E.00095
; LINE_WIDTH: 0.106348
G2 X168.216 Y137.157 I-3.01 J2.68 E.00343
; LINE_WIDTH: 0.157362
G1 X168.102 Y137.077 E.0013
; LINE_WIDTH: 0.191169
G1 X167.988 Y136.998 E.00168
; WIPE_START
G1 X168.102 Y137.077 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.637 Y139.999 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108888
G1 F15000
G3 X167.474 Y140.078 I-.973 J-1.804 E.00097
G1 X167.027 Y140.053 F30000
; LINE_WIDTH: 0.104702
G1 F15000
G3 X166.709 Y139.818 I2.004 J-3.045 E.00199
G1 X167.116 Y139.964 F30000
; LINE_WIDTH: 0.112906
G1 F15000
G1 X166.888 Y140.025 E.00135
; WIPE_START
G1 X167.116 Y139.964 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.923 Y139.06 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.118248
G1 F15000
G1 X165.981 Y138.831 E.00145
; WIPE_START
G1 X165.923 Y139.06 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.909 Y136.114 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.116434
G1 F15000
G1 X169.909 Y135.911 E.00122
; WIPE_START
G1 X169.909 Y136.114 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.405 Y134.518 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108924
G1 F15000
G1 X169.32 Y134.394 E.0008
; LINE_WIDTH: 0.15042
G1 X169.236 Y134.271 E.00131
; LINE_WIDTH: 0.191917
G1 X169.151 Y134.148 E.00182
G1 X168.906 Y133.484 F30000
; LINE_WIDTH: 0.11118
G1 F15000
G1 X168.785 Y133.323 E.00112
; LINE_WIDTH: 0.15719
G1 X168.664 Y133.161 E.00188
; LINE_WIDTH: 0.2032
G1 X168.543 Y133 E.00263
; WIPE_START
G1 X168.664 Y133.161 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.712 Y140.794 Z1.4 F30000
G1 X168.818 Y157.421 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.10509
G1 F15000
G1 X168.765 Y157.66 E.00125
; WIPE_START
G1 X168.818 Y157.421 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.454 Y156.667 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.197243
G1 F15000
G1 X168.348 Y156.522 E.00227
; LINE_WIDTH: 0.15361
G1 X168.241 Y156.376 E.00163
; LINE_WIDTH: 0.109978
G1 X168.134 Y156.23 E.00099
G1 X167.738 Y155.419 F30000
; LINE_WIDTH: 0.217858
G1 F15000
G1 X167.62 Y155.272 E.00269
; LINE_WIDTH: 0.188478
G1 X167.43 Y155.055 E.00342
; LINE_WIDTH: 0.15075
G1 X167.24 Y154.839 E.00253
; LINE_WIDTH: 0.105279
G1 X166.941 Y154.508 E.00227
; WIPE_START
G1 X167.24 Y154.839 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.938 Y153.506 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0910988
G1 F15000
G1 X165.825 Y153.397 E.00062
; LINE_WIDTH: 0.113009
G1 X165.608 Y153.207 E.00165
; LINE_WIDTH: 0.15074
G1 X165.391 Y153.016 E.00253
; LINE_WIDTH: 0.188948
G1 X165.168 Y152.822 E.00352
; LINE_WIDTH: 0.218255
G1 X165.027 Y152.708 E.0026
G1 X164.216 Y152.312 F30000
; LINE_WIDTH: 0.109984
G1 F15000
G1 X164.07 Y152.205 E.00099
; LINE_WIDTH: 0.153615
G1 X163.925 Y152.099 E.00163
; LINE_WIDTH: 0.197245
G1 X163.779 Y151.992 E.00227
; WIPE_START
G1 X163.925 Y152.099 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.461 Y151.785 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.201289
G1 F15000
G1 X165.291 Y151.655 E.00276
; LINE_WIDTH: 0.156044
G1 X165.122 Y151.524 E.00197
; LINE_WIDTH: 0.110799
G1 X164.952 Y151.393 E.00118
; WIPE_START
G1 X165.122 Y151.524 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.919 Y144.423 Z1.4 F30000
G1 X168.382 Y143.246 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.143833
G1 F15000
G1 X168.281 Y143.089 E.00153
; LINE_WIDTH: 0.128874
G1 X168.232 Y143.018 E.00061
; LINE_WIDTH: 0.101741
G1 X168.182 Y142.946 E.00042
G1 X168.363 Y143.101 F30000
; LINE_WIDTH: 0.109512
G1 F15000
G1 X168.299 Y143.329 E.00129
; WIPE_START
G1 X168.363 Y143.101 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.249 Y141.998 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.185292
G1 F15000
G2 X166.944 Y141.818 I-2.356 J3.659 E.00411
; WIPE_START
G1 X167.249 Y141.998 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X160.166 Y144.841 Z1.4 F30000
G1 X150.656 Y148.659 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0946611
G1 F15000
G2 X150.578 Y148.779 I1.323 J.941 E.0006
; WIPE_START
G1 X150.656 Y148.659 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.967 Y151.272 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.102842
G1 F15000
G1 X150.859 Y151.141 E.00083
; LINE_WIDTH: 0.132802
G1 X150.747 Y151.006 E.00129
; LINE_WIDTH: 0.162115
G1 X150.696 Y150.936 E.00084
; LINE_WIDTH: 0.197993
G1 X150.642 Y150.861 E.00118
G1 X150.673 Y150.715 E.00188
; WIPE_START
G1 X150.642 Y150.861 E-.46759
G1 X150.696 Y150.936 E-.29241
; WIPE_END
G1 E-.04 F1800
G1 X151.709 Y151.903 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.1948
G1 F15000
G1 X151.567 Y151.805 E.00214
; LINE_WIDTH: 0.158967
G1 X151.44 Y151.705 E.00152
; LINE_WIDTH: 0.119601
G1 X151.309 Y151.603 E.00104
; LINE_WIDTH: 0.0940951
G1 X151.169 Y151.472 E.0008
; WIPE_START
G1 X151.309 Y151.603 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.259 Y151.207 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0984224
G1 F15000
G1 X154.154 Y151.288 E.0006
; WIPE_START
G1 X154.259 Y151.207 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X153.507 Y143.612 Z1.4 F30000
G1 X152.946 Y137.949 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.182952
G1 F15000
G1 X152.865 Y137.832 E.00162
; LINE_WIDTH: 0.163314
G1 X152.783 Y137.726 E.00131
; LINE_WIDTH: 0.127413
G1 X152.697 Y137.614 E.00097
; LINE_WIDTH: 0.107971
G2 X152.217 Y137.157 I-3.011 J2.681 E.00352
; LINE_WIDTH: 0.158741
G1 X152.104 Y137.078 E.0013
; LINE_WIDTH: 0.191958
G1 X151.991 Y136.999 E.00167
; WIPE_START
G1 X152.104 Y137.078 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X151.639 Y139.999 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.109767
G1 F15000
G3 X151.476 Y140.078 I-.968 J-1.791 E.00099
G1 X151.03 Y140.054 F30000
; LINE_WIDTH: 0.103424
G1 F15000
G3 X150.715 Y139.822 I1.96 J-2.987 E.00193
G1 X151.119 Y139.965 F30000
; LINE_WIDTH: 0.11599
G1 F15000
G1 X150.89 Y140.026 E.00141
; WIPE_START
G1 X151.119 Y139.965 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.921 Y139.056 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.116001
G1 F15000
G1 X149.981 Y138.827 E.00141
G1 X150.117 Y139.224 F30000
; LINE_WIDTH: 0.105219
G1 F15000
G3 X149.895 Y138.914 I3.427 J-2.689 E.00194
; WIPE_START
G1 X150.117 Y139.224 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.155 Y145.422 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.11124
G1 F15000
G2 X145.99 Y145.5 I.621 J1.526 E.00101
G1 X146.921 Y145.682 F30000
; LINE_WIDTH: 0.10873
G1 F15000
G1 X146.815 Y145.608 E.0007
; LINE_WIDTH: 0.151734
G1 X146.699 Y145.527 E.00125
; LINE_WIDTH: 0.186117
G1 X146.594 Y145.467 E.00141
; WIPE_START
G1 X146.699 Y145.527 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.715 Y146.569 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.113596
G1 F15000
G2 X147.478 Y146.24 I-3.822 J2.508 E.00234
G1 X147.691 Y146.425 F30000
; LINE_WIDTH: 0.0954006
G1 F15000
G1 X147.629 Y146.656 E.00102
; WIPE_START
G1 X147.691 Y146.425 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.639 Y148.511 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.169635
G1 F15000
G1 X145.498 Y148.41 E.0018
; LINE_WIDTH: 0.147557
G1 X145.347 Y148.289 E.00165
; LINE_WIDTH: 0.107965
G1 X145.197 Y148.168 E.00102
G1 X145 Y147.971 F30000
; LINE_WIDTH: 0.122793
G1 F15000
G3 X144.658 Y147.537 I3.849 J-3.389 E.0036
; WIPE_START
G1 X145 Y147.971 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X144.314 Y140.37 Z1.4 F30000
G1 X143.483 Y131.159 Z1.4
G1 Z1
M73 P72 R2
G1 E.8 F1800
; LINE_WIDTH: 0.201439
G1 F15000
G1 X143.378 Y131.023 E.00221
; LINE_WIDTH: 0.167593
G1 X143.27 Y130.881 E.00181
; LINE_WIDTH: 0.133035
G1 X143.038 Y130.628 E.00252
G1 X142.791 Y130.402 E.00245
; LINE_WIDTH: 0.169712
G1 X142.646 Y130.287 E.00192
; LINE_WIDTH: 0.202591
G1 X142.518 Y130.197 E.00204
; WIPE_START
G1 X142.646 Y130.287 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.006 Y131.979 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.12374
G1 F15000
G3 X144.66 Y131.541 I3.858 J-3.402 E.00368
; WIPE_START
G1 X145.006 Y131.979 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.636 Y132.51 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.171297
G1 F15000
G1 X145.498 Y132.411 E.00178
; LINE_WIDTH: 0.148769
G1 X145.344 Y132.288 E.0017
; LINE_WIDTH: 0.10837
G1 X145.19 Y132.164 E.00105
; WIPE_START
G1 X145.344 Y132.288 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.718 Y130.57 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.110594
G1 F15000
G2 X147.469 Y130.234 I-3.165 J2.089 E.00231
G1 X147.691 Y130.428 F30000
; LINE_WIDTH: 0.0984798
G1 F15000
G1 X147.63 Y130.658 E.00108
; WIPE_START
G1 X147.691 Y130.428 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.917 Y129.68 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108316
G1 F15000
G1 X146.813 Y129.607 E.00068
; LINE_WIDTH: 0.150467
G1 X146.699 Y129.528 E.00122
; LINE_WIDTH: 0.185249
G1 X146.591 Y129.466 E.00144
G1 X146.153 Y129.422 F30000
; LINE_WIDTH: 0.11213
G1 F15000
G2 X145.988 Y129.5 I.618 J1.518 E.00103
; WIPE_START
G1 X146.153 Y129.422 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X138.533 Y129.87 Z1.4 F30000
G1 X134.064 Y130.132 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0936028
G1 F15000
G2 X133.944 Y130.209 I.832 J1.416 E.00059
; WIPE_START
G1 X134.064 Y130.132 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.115 Y133.661 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.207407
G1 F15000
G1 X131.968 Y133.478 E.00315
; LINE_WIDTH: 0.166008
G1 X131.818 Y133.291 E.0024
; LINE_WIDTH: 0.130882
G1 X131.667 Y133.119 E.00164
; LINE_WIDTH: 0.102402
G1 X131.516 Y132.947 E.00111
; WIPE_START
G1 X131.667 Y133.119 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X133.402 Y133.708 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.110594
G1 F15000
G1 X133.278 Y133.545 E.00113
; LINE_WIDTH: 0.155488
G1 X133.153 Y133.381 E.00189
; LINE_WIDTH: 0.200381
G1 X133.028 Y133.218 E.00264
; WIPE_START
G1 X133.153 Y133.381 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.681 Y134.904 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.181199
G1 F15000
G1 X132.706 Y134.76 E.00165
; LINE_WIDTH: 0.191386
G1 X132.621 Y134.644 E.00173
; LINE_WIDTH: 0.150096
G1 X132.537 Y134.529 E.00125
; LINE_WIDTH: 0.108806
G1 X132.452 Y134.413 E.00077
; WIPE_START
G1 X132.537 Y134.529 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X133.198 Y142.132 Z1.4 F30000
G1 X133.687 Y147.758 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.187048
G1 F15000
G1 X133.509 Y147.616 E.00268
; LINE_WIDTH: 0.150665
G1 X133.146 Y147.272 E.00439
; LINE_WIDTH: 0.169583
G1 X132.939 Y147.031 E.00328
; LINE_WIDTH: 0.207052
G1 X132.832 Y146.888 E.00238
; WIPE_START
G1 X132.939 Y147.031 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X131.424 Y139.55 Z1.4 F30000
G1 X129.722 Y131.153 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.102406
G1 F15000
G1 X129.55 Y131.002 E.00111
; LINE_WIDTH: 0.131163
G1 X129.375 Y130.848 E.00168
; LINE_WIDTH: 0.166404
G1 X129.191 Y130.701 E.00236
; LINE_WIDTH: 0.207409
G1 X129.008 Y130.554 E.00315
G1 X128.256 Y130.217 F30000
; LINE_WIDTH: 0.108812
G1 F15000
G1 X128.141 Y130.132 E.00077
; LINE_WIDTH: 0.150099
G1 X128.025 Y130.048 E.00125
; LINE_WIDTH: 0.186279
G1 X127.91 Y129.963 E.00167
G1 X127.765 Y129.988 E.00171
G1 X127.278 Y129.771 F30000
; LINE_WIDTH: 0.109264
G1 F15000
G1 X127.179 Y129.705 E.00065
; LINE_WIDTH: 0.163579
G2 X126.96 Y129.562 I-3.583 J5.255 E.00257
; OBJECT_ID: 861
; WIPE_START
G1 X127.179 Y129.705 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 795
M625
; start printing object, unique label id: 861
M624 CAAAAAAAAAA=
G1 X131.486 Y123.404 Z1.4 F30000
G1 X147.484 Y100.003 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G3 X146.065 Y98.698 I-1.309 J-.001 E.18623
G1 X146.169 Y98.693 E.00319
G3 X147.483 Y99.943 I.005 J1.309 E.06155
; WIPE_START
M204 S10000
G1 X147.457 Y100.241 E-.11354
G1 X147.357 Y100.557 E-.12604
G1 X147.242 Y100.755 E-.08675
G1 X147.088 Y100.937 E-.09074
G1 X146.824 Y101.138 E-.12601
G1 X146.617 Y101.234 E-.0868
G1 X146.397 Y101.294 E-.08682
G1 X146.283 Y101.304 E-.0433
; WIPE_END
G1 E-.04 F1800
G1 X150.492 Y94.936 Z1.4 F30000
G1 X152.761 Y91.503 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X151.342 Y90.198 I-1.309 J-.001 E.18623
G1 X151.446 Y90.193 E.00319
G3 X152.76 Y91.443 I.005 J1.309 E.06155
; WIPE_START
M204 S10000
G1 X152.736 Y91.732 E-.10985
G1 X152.634 Y92.057 E-.12969
G1 X152.519 Y92.255 E-.08679
G1 X152.373 Y92.43 E-.08677
G1 X152.198 Y92.577 E-.08679
G1 X152 Y92.691 E-.0868
G1 X151.674 Y92.794 E-.13
G1 X151.56 Y92.804 E-.04332
; WIPE_END
G1 E-.04 F1800
G1 X158.271 Y89.168 Z1.4 F30000
G1 X162.613 Y86.816 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X161.451 Y87.713 I-1.177 J-.323 E.0484
G1 X150.441 Y87.713 E.33829
G3 X149.236 Y86.508 I.016 J-1.221 E.05798
G1 X149.236 Y83.499 E.09247
G3 X150.441 Y82.293 I1.221 J.016 E.05798
G1 X161.451 Y82.293 E.33829
G3 X162.656 Y83.499 I-.016 J1.221 E.05798
G1 X162.656 Y86.508 E.09247
G3 X162.627 Y86.758 I-1.221 J-.016 E.00774
; WIPE_START
M204 S10000
G1 X162.543 Y87.015 E-.10276
G1 X162.437 Y87.197 E-.08014
G1 X162.302 Y87.359 E-.08015
G1 X162.14 Y87.495 E-.08017
G1 X161.958 Y87.6 E-.08015
G1 X161.759 Y87.672 E-.08016
G1 X161.451 Y87.713 E-.11831
G1 X161.087 Y87.713 E-.13818
; WIPE_END
G1 E-.04 F1800
G1 X153.582 Y86.323 Z1.4 F30000
G1 X145.1 Y84.751 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X146.065 Y82.698 I1.075 J-.748 E.08432
G1 X146.169 Y82.693 E.00319
G3 X145.135 Y84.799 I.005 J1.309 E.16345
; WIPE_START
M204 S10000
G1 X144.938 Y84.451 E-.15204
G1 X144.879 Y84.231 E-.0868
G1 X144.859 Y84.003 E-.08671
G1 X144.879 Y83.776 E-.08681
G1 X144.942 Y83.546 E-.09074
G1 X145.034 Y83.348 E-.08285
G1 X145.166 Y83.16 E-.08709
G1 X145.335 Y83.006 E-.08696
; WIPE_END
G1 E-.04 F1800
G1 X144.323 Y90.571 Z1.4 F30000
G1 X143.065 Y99.982 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X141.674 Y100.713 I-1.41 J-.993 E.05014
G1 X134.619 Y100.713 E.21677
G3 X133.109 Y98.209 I.016 J-1.717 E.10753
G1 X133.644 Y97.29 E.03266
G2 X134.368 Y88.399 I-10.092 J-5.297 E.28163
G2 X133.109 Y85.798 I-12.327 J4.361 E.08899
G3 X134.619 Y83.293 I1.525 J-.788 E.10753
G1 X141.674 Y83.293 E.21678
G3 X143.379 Y84.999 I-.019 J1.725 E.08206
G1 X143.379 Y99.008 E.43047
G3 X143.098 Y99.932 I-1.725 J-.019 E.03007
; WIPE_START
M204 S10000
G1 X142.878 Y100.213 E-.13551
G1 X142.638 Y100.412 E-.11852
G1 X142.392 Y100.553 E-.10798
G1 X142.098 Y100.658 E-.11854
G1 X141.818 Y100.707 E-.10802
G1 X141.674 Y100.713 E-.05491
G1 X141.367 Y100.713 E-.11652
; WIPE_END
G1 E-.04 F1800
G1 X135.162 Y96.269 Z1.4 F30000
G1 X118.1 Y84.05 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X122.823 Y82.33 I5.569 J7.949 E.15622
G1 X122.915 Y82.326 E.00283
G1 X123.669 Y82.293 E.0232
G3 X118.051 Y84.084 I0 J9.706 E1.6897
; WIPE_START
M204 S10000
G1 X118.814 Y83.594 E-.34472
G1 X119.565 Y83.203 E-.32184
G1 X119.792 Y83.109 E-.09344
; WIPE_END
G1 E-.04 F1800
G1 X125.016 Y88.674 Z1.4 F30000
G1 X157.761 Y123.56 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X158.6 Y104.33 I1.685 J-9.56 E.85897
G1 X158.692 Y104.326 E.00283
G1 X159.446 Y104.293 E.0232
G3 X157.82 Y123.57 I0 J9.707 E.98726
; WIPE_START
M204 S10000
G1 X156.933 Y123.383 E-.3446
G1 X156.125 Y123.128 E-.32188
G1 X155.898 Y123.034 E-.09353
; WIPE_END
G1 E-.04 F1800
G1 X158.707 Y115.937 Z1.4 F30000
G1 X166.948 Y95.119 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X168.156 Y96.744 I-.513 J1.643 E.06655
G1 X168.156 Y103.053 E.19386
G3 X165.652 Y104.563 I-1.717 J-.016 E.10753
G1 X164.733 Y104.028 E.03266
G2 X155.842 Y103.304 I-5.287 J9.976 E.28178
G2 X153.241 Y104.563 I4.36 J12.326 E.08899
G3 X150.761 Y103.34 I-.787 J-1.53 E.09867
G3 X150.736 Y102.337 I5.794 J-.645 E.03087
G3 X151.808 Y100.755 I1.744 J.027 E.06213
G1 X165.816 Y95.159 E.46351
G3 X166.245 Y95.051 I.667 J1.741 E.01364
G3 X166.89 Y95.102 I.189 J1.711 E.01999
; WIPE_START
M204 S10000
G1 X167.219 Y95.223 E-.13304
G1 X167.464 Y95.375 E-.10977
G1 X167.577 Y95.466 E-.05514
G1 X167.682 Y95.566 E-.05508
G1 X167.864 Y95.792 E-.11008
G1 X168.005 Y96.045 E-.11017
G1 X168.101 Y96.318 E-.1101
G1 X168.132 Y96.46 E-.05507
G1 X168.137 Y96.516 E-.02155
; WIPE_END
G1 E-.04 F1800
G1 X168.741 Y91.275 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X167.342 Y90.198 I-1.29 J.228 E.19328
M73 P73 R2
G1 X167.446 Y90.193 E.00319
G3 X168.729 Y91.216 I.005 J1.309 E.05451
; WIPE_START
M204 S10000
G1 X168.756 Y91.503 E-.1095
G1 X168.712 Y91.842 E-.13
G1 X168.633 Y92.058 E-.08709
G1 X168.519 Y92.255 E-.08647
G1 X168.373 Y92.43 E-.08677
G1 X168.198 Y92.577 E-.08679
G1 X168 Y92.691 E-.0868
G1 X167.783 Y92.759 E-.0866
; WIPE_END
G1 E-.04 F1800
G1 X160.341 Y94.458 Z1.4 F30000
G1 X128.211 Y101.793 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X123.367 Y81.218 I-4.533 J-9.791 E1.17571
G1 X158.827 Y80.217 E1.09002
G3 X170.518 Y91.622 I-.09 J11.786 E.55438
G1 X170.235 Y114.134 E.6918
G3 X149.069 Y111.047 I-10.788 J-.139 E1.12892
G1 X149.5 Y109.748 E.04205
G2 X147.22 Y103.891 I-5.035 J-1.413 E.20718
G1 X145.061 Y102.563 E.07788
G2 X142.339 Y101.793 I-2.754 J4.542 E.08796
G1 X128.271 Y101.793 E.4323
; WIPE_START
M204 S10000
G1 X127.301 Y102.164 E-.39452
G1 X126.41 Y102.439 E-.35411
G1 X126.381 Y102.445 E-.01137
; WIPE_END
G1 E-.04 F1800
G1 X133.131 Y98.883 Z1.4 F30000
G1 X164.818 Y82.16 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Top surface
G1 F9547.055
M204 S2000
G1 X168.602 Y85.944 E.16445
; WIPE_START
M204 S10000
G1 X167.188 Y84.53 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.213 Y87.089 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X163.642 Y81.517 E.24211
G1 X162.727 Y81.136
G1 X169.595 Y88.004 E.29846
G1 X169.861 Y88.803
G1 X161.941 Y80.883 E.34419
G1 X161.228 Y80.704
G1 X170.04 Y89.516 E.38292
G1 X170.159 Y90.168
G1 X160.563 Y80.572 E.41699
G1 X159.951 Y80.493
G1 X161.552 Y82.094 E.06959
G1 X161.011 Y82.086
G1 X159.373 Y80.448 E.07116
G1 X158.817 Y80.425
G1 X160.478 Y82.086 E.07216
G1 X159.944 Y82.086
G1 X158.298 Y80.44 E.07153
G1 X157.78 Y80.455
G1 X159.411 Y82.086 E.07089
G1 X158.878 Y82.086
G1 X157.261 Y80.469 E.07026
G1 X156.742 Y80.484
G1 X158.345 Y82.086 E.06962
G1 X157.811 Y82.086
G1 X156.224 Y80.498 E.06899
G1 X155.705 Y80.513
G1 X157.278 Y82.086 E.06835
G1 X156.745 Y82.086
G1 X155.187 Y80.528 E.06772
G1 X154.668 Y80.542
G1 X156.212 Y82.086 E.06708
G1 X155.678 Y82.086
G1 X154.149 Y80.557 E.06644
G1 X153.631 Y80.572
G1 X155.145 Y82.086 E.06581
G1 X154.612 Y82.086
G1 X153.112 Y80.586 E.06517
G1 X152.593 Y80.601
G1 X154.079 Y82.086 E.06454
G1 X153.545 Y82.086
G1 X152.075 Y80.615 E.0639
G1 X151.556 Y80.63
G1 X153.012 Y82.086 E.06327
G1 X152.479 Y82.086
G1 X151.037 Y80.645 E.06263
G1 X150.519 Y80.659
G1 X151.945 Y82.086 E.062
G1 X151.412 Y82.086
G1 X150 Y80.674 E.06136
G1 X149.482 Y80.689
G1 X150.879 Y82.086 E.06072
G1 X150.353 Y82.093
G1 X148.963 Y80.703 E.06039
G1 X148.444 Y80.718
G1 X149.92 Y82.193 E.06411
G1 X149.579 Y82.386
G1 X147.926 Y80.732 E.07186
G1 X147.407 Y80.747
G1 X149.314 Y82.654 E.08287
G1 X149.126 Y82.999
G1 X146.888 Y80.762 E.09723
G1 X146.37 Y80.776
G1 X149.033 Y83.44 E.11573
G1 X149.032 Y83.972
G1 X145.851 Y80.791 E.13824
G1 X145.333 Y80.806
G1 X149.032 Y84.505 E.16074
G1 X149.031 Y85.037
G1 X147.642 Y83.649 E.06033
G1 X147.667 Y84.207
G1 X149.03 Y85.57 E.05923
G1 X149.029 Y86.102
G1 X147.549 Y84.622 E.06431
G1 X147.349 Y84.955
G1 X149.04 Y86.646 E.07349
; WIPE_START
M204 S10000
G1 X147.626 Y85.232 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.527 Y82.533 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X144.814 Y80.82 E.07444
G1 X144.295 Y80.835
G1 X145.965 Y82.504 E.07255
G1 X145.547 Y82.62
G1 X143.777 Y80.849 E.07694
G1 X143.258 Y80.864
G1 X145.222 Y82.828 E.08534
G1 X144.957 Y83.097
G1 X142.739 Y80.879 E.09638
G1 X142.221 Y80.893
G1 X144.771 Y83.443 E.1108
M73 P74 R2
G1 X144.658 Y83.864
G1 X141.702 Y80.908 E.12844
G1 X141.183 Y80.923
G1 X144.732 Y84.471 E.15421
; WIPE_START
M204 S10000
G1 X143.318 Y83.057 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.949 Y83.19 Z1.4 F30000
G1 X162.855 Y83.397 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X170.247 Y90.789 E.3212
G1 X170.29 Y91.365
G1 X162.864 Y83.939 E.32273
G1 X162.864 Y84.472
G1 X170.307 Y91.915 E.32344
; WIPE_START
M204 S10000
G1 X168.892 Y90.501 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.881 Y91.022 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X170.3 Y92.442 E.06167
G1 X170.293 Y92.968
G1 X168.959 Y91.634 E.058
G1 X168.853 Y92.061
G1 X170.287 Y93.495 E.06231
G1 X170.28 Y94.022
G1 X168.66 Y92.401 E.0704
G1 X168.399 Y92.673
G1 X170.274 Y94.548 E.08146
G1 X170.267 Y95.075
G1 X168.076 Y92.884 E.09521
G1 X167.66 Y93.001
G1 X170.26 Y95.601 E.11298
G1 X170.254 Y96.128
G1 X167.105 Y92.979 E.13684
; WIPE_START
M204 S10000
G1 X168.519 Y94.393 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.924 Y90.065 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X162.864 Y85.005 E.21989
G1 X162.864 Y85.538
G1 X167.317 Y89.992 E.19352
G1 X166.889 Y90.097
G1 X162.864 Y86.072 E.1749
G1 X162.856 Y86.598
G1 X166.545 Y90.286 E.16028
G1 X166.271 Y90.545
G1 X162.757 Y87.032 E.15266
G1 X162.561 Y87.369
G1 X166.069 Y90.877 E.15243
G1 X165.948 Y91.289
G1 X162.294 Y87.635 E.15879
G1 X161.952 Y87.826
G1 X165.97 Y91.845 E.17462
; WIPE_START
M204 S10000
G1 X164.556 Y90.431 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X161.509 Y87.916 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X170.247 Y96.655 E.37973
G1 X170.241 Y97.181
G1 X160.976 Y87.916 E.40261
G1 X160.443 Y87.917
G1 X170.234 Y97.708 E.42548
G1 X170.227 Y98.235
G1 X168.312 Y96.319 E.08324
G1 X168.358 Y96.898
G1 X170.221 Y98.761 E.08096
G1 X170.214 Y99.288
G1 X168.358 Y97.431 E.08068
G1 X168.358 Y97.965
G1 X170.208 Y99.815 E.08039
G1 X170.201 Y100.341
G1 X168.358 Y98.498 E.0801
G1 X168.358 Y99.031
G1 X170.194 Y100.868 E.07982
G1 X170.188 Y101.395
G1 X168.358 Y99.564 E.07953
G1 X168.358 Y100.098
G1 X170.181 Y101.921 E.07924
G1 X170.175 Y102.448
G1 X168.358 Y100.631 E.07896
G1 X168.357 Y101.164
G1 X170.168 Y102.975 E.07867
G1 X170.161 Y103.501
G1 X168.357 Y101.697 E.07838
G1 X168.357 Y102.231
G1 X170.155 Y104.028 E.0781
G1 X170.148 Y104.555
G1 X168.357 Y102.764 E.07781
G1 X168.347 Y103.287
G1 X170.141 Y105.081 E.07797
G1 X170.135 Y105.608
G1 X168.243 Y103.716 E.08222
G1 X168.066 Y104.072
G1 X170.128 Y106.135 E.08962
G1 X170.122 Y106.661
G1 X167.833 Y104.372 E.09946
G1 X167.542 Y104.615
G1 X170.115 Y107.188 E.1118
G1 X170.108 Y107.715
G1 X167.201 Y104.807 E.12632
G1 X166.79 Y104.929
G1 X170.102 Y108.241 E.14391
G1 X170.095 Y108.768
G1 X166.284 Y104.956 E.16563
G1 X165.522 Y104.728
G1 X170.089 Y109.294 E.19845
G1 X170.082 Y109.821
G1 X164.322 Y104.061 E.25032
G1 X163.38 Y103.653
G1 X170.075 Y110.348 E.29094
G1 X170.069 Y110.874
G1 X167.678 Y108.483 E.1039
; WIPE_START
M204 S10000
G1 X169.092 Y109.898 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.393 Y109.732 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
M73 P75 R2
G1 X170.062 Y111.401 E.07253
G1 X170.056 Y111.928
G1 X168.778 Y110.65 E.05551
G1 X169.024 Y111.429
G1 X170.049 Y112.454 E.04456
G1 X170.042 Y112.981
G1 X169.176 Y112.115 E.03763
G1 X169.275 Y112.746
G1 X170.036 Y113.508 E.03308
G1 X170.029 Y114.034
G1 X169.335 Y113.34 E.03017
G1 X169.359 Y113.898
G1 X170.005 Y114.543 E.02806
G1 X169.976 Y115.048
G1 X169.346 Y114.417 E.02739
G1 X169.319 Y114.924
G1 X169.91 Y115.515 E.0257
G1 X169.84 Y115.978
G1 X169.257 Y115.395 E.02534
G1 X169.184 Y115.856
G1 X169.738 Y116.409 E.02405
G1 X169.636 Y116.84
G1 X169.088 Y116.292 E.02382
G1 X168.98 Y116.717
G1 X169.509 Y117.247 E.02301
G1 X169.379 Y117.651
G1 X168.852 Y117.123 E.02293
G1 X168.715 Y117.519
G1 X169.223 Y118.028 E.0221
G1 X169.066 Y118.404
G1 X168.558 Y117.896 E.02206
G1 X168.397 Y118.268
G1 X168.888 Y118.759 E.02134
G1 X168.703 Y119.107
G1 X168.214 Y118.618 E.02123
G1 X168.031 Y118.969
G1 X168.512 Y119.45 E.0209
G1 X168.305 Y119.776
G1 X167.824 Y119.294 E.02091
G1 X167.616 Y119.62
G1 X168.094 Y120.098 E.02078
G1 X167.864 Y120.401
G1 X167.39 Y119.927 E.02059
G1 X167.158 Y120.229
G1 X167.633 Y120.703 E.02062
G1 X167.384 Y120.988
G1 X166.915 Y120.519 E.0204
G1 X166.66 Y120.797
G1 X167.131 Y121.268 E.02046
G1 X166.868 Y121.539
G1 X166.4 Y121.07 E.02035
G1 X166.122 Y121.325
G1 X166.592 Y121.796 E.02044
G1 X166.316 Y122.053
G1 X165.843 Y121.58 E.02052
G1 X165.544 Y121.814
G1 X166.017 Y122.287 E.02055
G1 X165.718 Y122.521
G1 X165.242 Y122.045 E.02067
G1 X164.925 Y122.261
G1 X165.404 Y122.74 E.02081
G1 X165.081 Y122.951
G1 X164.599 Y122.469 E.02095
G1 X164.263 Y122.666
G1 X164.752 Y123.155 E.02122
G1 X164.405 Y123.341
G1 X163.912 Y122.849 E.0214
G1 X163.556 Y123.026
G1 X164.058 Y123.528 E.02181
G1 X163.686 Y123.689
G1 X163.179 Y123.182 E.02203
G1 X162.799 Y123.335
G1 X163.314 Y123.85 E.02236
G1 X162.92 Y123.99
G1 X162.394 Y123.463 E.02288
G1 X161.986 Y123.589
G1 X162.521 Y124.123 E.02322
G1 X162.102 Y124.238
G1 X161.55 Y123.686 E.024
G1 X161.109 Y123.778
G1 X161.673 Y124.342 E.02452
G1 X161.224 Y124.427
G1 X160.638 Y123.84 E.02548
G1 X160.154 Y123.89
G1 X160.762 Y124.498 E.02641
G1 X160.275 Y124.544
G1 X159.644 Y123.912 E.02744
G1 X159.104 Y123.906
G1 X159.776 Y124.578 E.02919
G1 X159.239 Y124.574
G1 X158.543 Y123.878 E.03023
G1 X157.929 Y123.797
G1 X158.685 Y124.553 E.03285
G1 X158.09 Y124.492
G1 X157.267 Y123.669 E.03577
G1 X156.541 Y123.477
G1 X157.451 Y124.386 E.03952
G1 X156.763 Y124.231
G1 X155.713 Y123.182 E.0456
G1 X154.703 Y122.705
G1 X156.001 Y124.003 E.05641
G1 X155.113 Y123.648
G1 X153.007 Y121.542 E.0915
; WIPE_START
M204 S10000
G1 X154.421 Y122.956 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X158.413 Y116.451 Z1.4 F30000
G1 X164.966 Y105.772 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X162.576 Y103.382 E.10386
G1 X161.855 Y103.194
G1 X163.718 Y105.056 E.08094
G1 X162.799 Y104.671
G1 X161.189 Y103.061 E.06998
G1 X160.581 Y102.986
G1 X162.02 Y104.426 E.06255
G1 X161.334 Y104.273
G1 X160.005 Y102.944 E.05776
G1 X159.449 Y102.921
G1 X160.703 Y104.175 E.05448
G1 X160.109 Y104.114
G1 X158.937 Y102.942 E.05096
G1 X158.433 Y102.972
G1 X159.552 Y104.09 E.04861
G1 X159.032 Y104.104
G1 X157.958 Y103.03 E.04667
G1 X157.495 Y103.1
G1 X158.532 Y104.137 E.04507
G1 X158.057 Y104.195
G1 X157.053 Y103.191 E.04365
G1 X156.621 Y103.293
G1 X157.594 Y104.265 E.04226
G1 X157.157 Y104.362
G1 X156.208 Y103.413 E.04123
G1 X155.803 Y103.541
G1 X156.732 Y104.47 E.04036
G1 X156.327 Y104.598
G1 X155.418 Y103.689 E.0395
G1 X155.034 Y103.839
G1 X155.93 Y104.735 E.03894
G1 X155.553 Y104.891
G1 X154.674 Y104.011 E.03823
G1 X154.313 Y104.184
G1 X155.182 Y105.053 E.03775
G1 X154.831 Y105.235
G1 X153.97 Y104.374 E.03742
G1 X153.63 Y104.567
G1 X154.481 Y105.418 E.03697
G1 X154.155 Y105.626
G1 X153.29 Y104.761 E.03759
G1 X152.905 Y104.909
G1 X153.829 Y105.833 E.04017
G1 X153.522 Y106.06
G1 X152.427 Y104.964 E.0476
G1 X151.772 Y104.843
G1 X153.221 Y106.291 E.06294
; WIPE_START
M204 S10000
G1 X151.806 Y104.877 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X158.168 Y100.66 Z1.4 F30000
G1 X166.879 Y94.887 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X159.91 Y87.917 E.30287
G1 X159.376 Y87.917
G1 X166.303 Y94.844 E.30099
G1 X165.856 Y94.93
G1 X158.843 Y87.917 E.30474
G1 X158.31 Y87.918
G1 X165.468 Y95.075 E.31102
G1 X165.087 Y95.227
G1 X157.777 Y87.918 E.31762
G1 X157.244 Y87.918
G1 X164.706 Y95.379 E.32423
G1 X164.325 Y95.531
G1 X156.711 Y87.918 E.33083
G1 X156.178 Y87.918
G1 X163.943 Y95.684 E.33744
M73 P76 R2
G1 X163.562 Y95.836
G1 X155.645 Y87.919 E.34404
G1 X155.112 Y87.919
G1 X163.181 Y95.988 E.35065
G1 X162.8 Y96.14
G1 X154.579 Y87.919 E.35726
G1 X154.046 Y87.919
G1 X162.419 Y96.293 E.36386
G1 X162.038 Y96.445
G1 X153.513 Y87.919 E.37047
G1 X152.98 Y87.92
G1 X161.657 Y96.597 E.37707
G1 X161.276 Y96.749
G1 X152.447 Y87.92 E.38368
G1 X151.914 Y87.92
G1 X160.895 Y96.901 E.39028
G1 X160.514 Y97.054
G1 X151.381 Y87.92 E.39689
G1 X150.848 Y87.921
G1 X160.133 Y97.206 E.40349
G1 X159.752 Y97.358
G1 X150.303 Y87.909 E.4106
; WIPE_START
M204 S10000
G1 X151.717 Y89.323 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X151.927 Y90.066 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X147.076 Y85.215 E.21079
G1 X146.735 Y85.407
G1 X151.319 Y89.991 E.1992
G1 X150.89 Y90.096
G1 X146.309 Y85.515 E.19908
G1 X145.705 Y85.444
G1 X150.546 Y90.285 E.21036
G1 X150.271 Y90.544
G1 X140.665 Y80.937 E.41746
G1 X140.146 Y80.952
G1 X142.456 Y83.262 E.10037
G1 X141.753 Y83.092
G1 X139.628 Y80.966 E.09237
G1 X139.109 Y80.981
G1 X141.22 Y83.092 E.09172
G1 X140.686 Y83.091
G1 X138.59 Y80.996 E.09106
G1 X138.072 Y81.01
G1 X140.152 Y83.091 E.09041
G1 X139.618 Y83.09
G1 X137.553 Y81.025 E.08975
G1 X137.034 Y81.04
G1 X139.085 Y83.09 E.0891
G1 X138.551 Y83.089
G1 X136.516 Y81.054 E.08844
G1 X135.997 Y81.069
G1 X138.017 Y83.089 E.08778
G1 X137.484 Y83.088
G1 X135.479 Y81.083 E.08713
G1 X134.96 Y81.098
G1 X136.95 Y83.088 E.08647
G1 X136.416 Y83.088
G1 X134.441 Y81.113 E.08582
G1 X133.923 Y81.127
G1 X135.882 Y83.087 E.08516
G1 X135.349 Y83.087
G1 X133.404 Y81.142 E.0845
G1 X132.885 Y81.157
G1 X134.815 Y83.086 E.08385
G1 X134.308 Y83.112
G1 X132.367 Y81.171 E.08434
G1 X131.848 Y81.186
G1 X133.896 Y83.234 E.08901
G1 X133.546 Y83.417
G1 X131.329 Y81.2 E.09632
G1 X130.811 Y81.215
G1 X133.258 Y83.663 E.10636
G1 X133.021 Y83.959
G1 X130.292 Y81.23 E.1186
G1 X129.774 Y81.244
G1 X132.841 Y84.312 E.13332
G1 X132.728 Y84.732
G1 X129.255 Y81.259 E.15093
G1 X128.736 Y81.274
G1 X132.723 Y85.261 E.17326
G1 X133.09 Y86.16
G1 X128.218 Y81.288 E.2117
G1 X127.699 Y81.303
G1 X133.692 Y87.296 E.26043
G1 X134.074 Y88.211
G1 X127.18 Y81.317 E.29957
G1 X126.662 Y81.332
G1 X128.948 Y83.618 E.09933
; WIPE_START
M204 S10000
G1 X127.533 Y82.204 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X127.776 Y82.98 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X126.143 Y81.347 E.07097
G1 X125.625 Y81.361
G1 X126.894 Y82.631 E.05517
G1 X126.13 Y82.4
G1 X125.106 Y81.376 E.0445
G1 X124.587 Y81.391
G1 X125.445 Y82.248 E.03726
G1 X124.825 Y82.162
G1 X124.069 Y81.405 E.03287
G1 X123.55 Y81.42
M73 P77 R2
G1 X124.241 Y82.11 E.03001
G1 X123.683 Y82.086
G1 X123.045 Y81.449 E.02771
G1 X122.548 Y81.484
G1 X123.171 Y82.107 E.02708
G1 X122.677 Y82.146
G1 X122.081 Y81.551 E.02589
G1 X121.621 Y81.624
G1 X122.202 Y82.205 E.02524
G1 X121.745 Y82.281
G1 X121.189 Y81.726 E.02414
G1 X120.763 Y81.832
G1 X121.308 Y82.378 E.02372
G1 X120.888 Y82.491
G1 X120.359 Y81.962 E.023
G1 X119.962 Y82.098
G1 X120.483 Y82.619 E.02263
G1 X120.091 Y82.761
G1 X119.582 Y82.251 E.02215
G1 X119.212 Y82.414
G1 X119.714 Y82.917 E.02182
G1 X119.347 Y83.083
G1 X118.851 Y82.587 E.02155
G1 X118.507 Y82.776
G1 X118.996 Y83.265 E.02125
G1 X118.65 Y83.452
G1 X118.164 Y82.966 E.02114
G1 X117.844 Y83.18
G1 X118.325 Y83.66 E.02086
G1 X117.999 Y83.867
G1 X117.525 Y83.394 E.02059
G1 X117.221 Y83.622
G1 X117.696 Y84.098 E.02065
G1 X117.394 Y84.329
G1 X116.925 Y83.86 E.02039
G1 X116.634 Y84.102
G1 X117.112 Y84.58 E.02075
G1 X116.831 Y84.833
G1 X116.361 Y84.363 E.02041
G1 X116.089 Y84.624
G1 X116.56 Y85.095 E.02048
G1 X116.305 Y85.373
G1 X115.834 Y84.903 E.02045
G1 X115.585 Y85.186
G1 X116.052 Y85.654 E.0203
G1 X115.821 Y85.955
G1 X115.344 Y85.479 E.02071
G1 X115.118 Y85.786
G1 X115.589 Y86.257 E.02048
G1 X115.377 Y86.578
G1 X114.896 Y86.097 E.0209
G1 X114.692 Y86.426
G1 X115.169 Y86.904 E.02076
G1 X114.976 Y87.244
G1 X114.487 Y86.755 E.02124
G1 X114.3 Y87.101
G1 X114.794 Y87.595 E.02146
G1 X114.621 Y87.955
G1 X114.122 Y87.457 E.02167
G1 X113.954 Y87.821
G1 X114.465 Y88.332 E.02222
G1 X114.316 Y88.717
G1 X113.803 Y88.204 E.02231
G1 X113.655 Y88.589
G1 X114.188 Y89.122 E.02319
G1 X114.067 Y89.535
G1 X113.532 Y89 E.02325
G1 X113.41 Y89.411
G1 X113.971 Y89.971 E.02436
G1 X113.884 Y90.418
G1 X113.318 Y89.852 E.0246
G1 X113.227 Y90.294
G1 X113.822 Y90.889 E.02586
G1 X113.779 Y91.379
G1 X113.169 Y90.769 E.02649
G1 X113.115 Y91.248
G1 X113.756 Y91.89 E.02788
G1 X113.77 Y92.437
G1 X113.099 Y91.766 E.02917
G1 X113.102 Y92.303
G1 X113.807 Y93.008 E.03064
G1 X113.888 Y93.622
G1 X113.13 Y92.863 E.03296
G1 X113.198 Y93.465
G1 X114.028 Y94.295 E.03607
G1 X114.236 Y95.036
G1 X113.303 Y94.102 E.04056
G1 X113.465 Y94.798
G1 X114.552 Y95.886 E.04727
G1 X115.077 Y96.943
G1 X113.716 Y95.582 E.05913
; WIPE_START
M204 S10000
G1 X115.077 Y96.943 E-.73128
G1 X115.043 Y96.875 E-.02872
; WIPE_END
G1 E-.04 F1800
G1 X121.597 Y92.964 Z1.4 F30000
G1 X132.054 Y86.725 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X134.327 Y88.997 E.09875
G1 X134.498 Y89.701
G1 X132.692 Y87.896 E.07845
G1 X133.041 Y88.778
G1 X134.624 Y90.361 E.06876
G1 X134.698 Y90.968
G1 X133.272 Y89.542 E.06196
G1 X133.424 Y90.228
G1 X134.732 Y91.536 E.05684
G1 X134.748 Y92.085
G1 X133.511 Y90.847 E.05377
G1 X133.562 Y91.432
G1 X134.727 Y92.597 E.05064
G1 X134.691 Y93.094
G1 X133.586 Y91.989 E.04802
G1 X133.565 Y92.501
G1 X134.633 Y93.569 E.04641
G1 X134.558 Y94.027
G1 X133.532 Y93.001 E.04459
G1 X133.469 Y93.472
G1 X134.467 Y94.47 E.04333
G1 X134.36 Y94.896
G1 X133.391 Y93.928 E.04209
G1 X133.295 Y94.364
G1 X134.239 Y95.309 E.04105
G1 X134.107 Y95.71
G1 X133.181 Y94.784 E.04022
G1 X133.054 Y95.19
G1 X133.959 Y96.095 E.03936
G1 X133.805 Y96.474
G1 X132.912 Y95.581 E.03883
G1 X132.756 Y95.958
G1 X133.633 Y96.835 E.03811
G1 X133.46 Y97.195
G1 X132.59 Y96.325 E.03781
G1 X132.407 Y96.676
G1 X133.263 Y97.532 E.03721
G1 X133.067 Y97.869
G1 X132.22 Y97.022 E.03681
G1 X132.012 Y97.348
G1 X132.878 Y98.213 E.0376
G1 X132.748 Y98.617
G1 X131.805 Y97.674 E.04098
G1 X131.575 Y97.977
G1 X132.715 Y99.117 E.04954
G1 X132.894 Y99.83
G1 X131.343 Y98.278 E.06741
; WIPE_START
M204 S10000
G1 X132.757 Y99.693 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X137.089 Y93.408 Z1.4 F30000
G1 X143.419 Y84.225 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X150.07 Y90.876 E.289
G1 X149.948 Y91.287
G1 X143.583 Y84.922 E.27657
G1 X143.586 Y85.458
G1 X149.97 Y91.842 E.2774
; WIPE_START
M204 S10000
G1 X148.556 Y90.428 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X152.879 Y91.019 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X159.371 Y97.51 E.28209
G1 X158.99 Y97.663
G1 X152.959 Y91.631 E.26209
G1 X152.849 Y92.055
G1 X158.609 Y97.815 E.2503
G1 X158.228 Y97.967
G1 X152.663 Y92.402 E.24181
G1 X152.4 Y92.672
G1 X157.847 Y98.119 E.23669
G1 X157.466 Y98.271
G1 X152.078 Y92.883 E.23415
G1 X151.662 Y93.001
G1 X157.085 Y98.424 E.23564
M73 P78 R2
G1 X156.704 Y98.576
G1 X151.107 Y92.98 E.24319
; WIPE_START
M204 S10000
G1 X152.522 Y94.394 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X156.323 Y98.728 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.586 Y85.991 E.55347
G1 X143.586 Y86.524
G1 X155.942 Y98.88 E.53692
G1 X155.561 Y99.033
G1 X143.586 Y87.057 E.52038
G1 X143.585 Y87.59
G1 X155.18 Y99.185 E.50383
G1 X154.799 Y99.337
G1 X143.585 Y88.123 E.48728
G1 X143.585 Y88.656
G1 X154.418 Y99.489 E.47073
G1 X154.037 Y99.641
G1 X143.585 Y89.189 E.45419
G1 X143.584 Y89.722
G1 X153.655 Y99.794 E.43764
G1 X153.274 Y99.946
G1 X143.584 Y90.256 E.42109
G1 X143.584 Y90.789
G1 X152.893 Y100.098 E.40454
G1 X152.512 Y100.25
G1 X143.584 Y91.322 E.388
G1 X143.583 Y91.855
G1 X152.131 Y100.403 E.37145
G1 X151.75 Y100.555
G1 X143.583 Y92.388 E.3549
G1 X143.583 Y92.921
G1 X151.4 Y100.738 E.3397
G1 X151.103 Y100.974
G1 X143.583 Y93.454 E.32681
G1 X143.582 Y93.987
G1 X150.86 Y101.264 E.31623
G1 X150.677 Y101.615
G1 X143.582 Y94.52 E.3083
G1 X143.582 Y95.053
G1 X150.555 Y102.026 E.303
G1 X150.53 Y102.534
G1 X147.642 Y99.646 E.12551
G1 X147.667 Y100.205
G1 X150.534 Y103.071 E.12456
G1 X150.66 Y103.731
G1 X147.55 Y100.621 E.13514
G1 X147.35 Y100.954
G1 X152.935 Y106.539 E.24268
G1 X152.654 Y106.791
G1 X147.077 Y101.214 E.24235
G1 X146.736 Y101.407
G1 X152.379 Y107.049 E.24521
G1 X152.124 Y107.328
G1 X146.311 Y101.514 E.25262
G1 X145.709 Y101.445
G1 X151.869 Y107.606 E.26771
G1 X151.636 Y107.906
G1 X148.842 Y105.112 E.1214
; WIPE_START
M204 S10000
G1 X150.256 Y106.526 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.513 Y106.316 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X151.404 Y108.208 E.08219
G1 X151.188 Y108.525
G1 X149.761 Y107.098 E.06202
G1 X149.868 Y107.738
G1 X150.981 Y108.85 E.04836
G1 X150.783 Y109.186
G1 X149.901 Y108.304 E.03833
G1 X149.88 Y108.816
G1 X150.601 Y109.537 E.03131
G1 X150.424 Y109.893
G1 X149.817 Y109.286 E.02638
G1 X149.719 Y109.722
G1 X150.268 Y110.27 E.02384
G1 X150.114 Y110.65
G1 X149.592 Y110.128 E.02269
G1 X149.459 Y110.529
G1 X149.986 Y111.056 E.0229
G1 X149.86 Y111.463
G1 X149.327 Y110.929 E.02319
G1 X149.211 Y111.347
G1 X149.764 Y111.9 E.02403
G1 X149.671 Y112.34
G1 X149.108 Y111.777 E.02449
G1 X149.022 Y112.225
G1 X149.609 Y112.812 E.02551
G1 X149.559 Y113.295
G1 X148.952 Y112.688 E.02638
G1 X148.905 Y113.174
G1 X149.537 Y113.806 E.02746
G1 X149.543 Y114.345
G1 X148.873 Y113.675 E.02914
G1 X148.876 Y114.211
G1 X149.571 Y114.907 E.03023
G1 X149.652 Y115.521
G1 X148.895 Y114.764 E.03291
G1 X148.958 Y115.36
G1 X149.78 Y116.182 E.03573
G1 X149.973 Y116.908
G1 X149.064 Y115.999 E.03951
G1 X149.217 Y116.686
G1 X150.268 Y117.736 E.04564
G1 X150.745 Y118.747
G1 X149.445 Y117.447 E.05648
M73 P79 R2
G1 X149.796 Y118.331
G1 X151.907 Y120.442 E.09172
; WIPE_START
M204 S10000
G1 X150.493 Y119.028 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.387 Y119.455 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X153.996 Y123.064 E.15681
; WIPE_START
M204 S10000
G1 X152.581 Y121.65 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.648 Y114.266 Z1.4 F30000
G1 X146.53 Y98.534 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.582 Y95.586 E.12812
G1 X143.581 Y96.119
G1 X145.967 Y98.504 E.10365
G1 X145.549 Y98.619
G1 X143.581 Y96.652 E.0855
G1 X143.581 Y97.185
G1 X145.223 Y98.827 E.07136
G1 X144.958 Y99.095
G1 X143.581 Y97.718 E.05986
G1 X143.581 Y98.251
G1 X144.771 Y99.441 E.05174
G1 X144.658 Y99.862
G1 X143.58 Y98.784 E.04684
G1 X143.563 Y99.299
G1 X144.731 Y100.468 E.05076
; WIPE_START
M204 S10000
G1 X143.563 Y99.299 E-.62776
G1 X143.575 Y98.952 E-.13224
; WIPE_END
G1 E-.04 F1800
G1 X147.684 Y103.955 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.446 Y99.716 E.1842
G1 X143.263 Y100.067
G1 X146.244 Y103.047 E.12951
; WIPE_START
M204 S10000
G1 X144.83 Y101.633 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X144.896 Y102.233 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X143.024 Y100.361 E.08135
G1 X142.726 Y100.596
G1 X143.97 Y101.84 E.05405
G1 X143.266 Y101.669
G1 X142.376 Y100.779 E.03866
G1 X141.957 Y100.893
G1 X142.662 Y101.598 E.03064
G1 X142.116 Y101.586
G1 X141.451 Y100.92 E.02892
G1 X140.917 Y100.92
G1 X141.583 Y101.586 E.02894
G1 X141.05 Y101.586
G1 X140.383 Y100.92 E.02896
G1 X139.85 Y100.919
G1 X140.517 Y101.586 E.02898
G1 X139.983 Y101.586
G1 X139.316 Y100.919 E.029
G1 X138.782 Y100.918
G1 X139.45 Y101.586 E.02901
G1 X138.917 Y101.586
G1 X138.249 Y100.918 E.02903
G1 X137.715 Y100.917
G1 X138.384 Y101.586 E.02905
G1 X137.85 Y101.586
G1 X137.181 Y100.917 E.02907
G1 X136.648 Y100.916
G1 X137.317 Y101.586 E.02909
G1 X136.784 Y101.586
G1 X136.114 Y100.916 E.02911
G1 X135.58 Y100.916
G1 X136.25 Y101.586 E.02913
G1 X135.717 Y101.586
G1 X135.046 Y100.915 E.02915
G1 X134.513 Y100.915
G1 X135.184 Y101.586 E.02917
G1 X134.651 Y101.586
G1 X133.788 Y100.723 E.03751
G1 X134.117 Y101.586
G1 X131.096 Y98.564 E.1313
G1 X130.841 Y98.843
G1 X133.584 Y101.586 E.11921
G1 X133.051 Y101.586
G1 X130.577 Y99.112 E.10749
G1 X130.299 Y99.367
G1 X132.518 Y101.586 E.09641
G1 X131.984 Y101.586
G1 X130.019 Y99.62 E.08542
G1 X129.717 Y99.852
G1 X131.451 Y101.586 E.07536
G1 X130.918 Y101.586
G1 X129.415 Y100.083 E.0653
G1 X129.094 Y100.295
G1 X130.385 Y101.586 E.05608
G1 X129.851 Y101.586
G1 X128.768 Y100.503 E.04706
G1 X128.428 Y100.696
G1 X129.318 Y101.586 E.03866
G1 X128.785 Y101.586
G1 X128.078 Y100.879 E.03073
G1 X127.717 Y101.051
G1 X128.252 Y101.586 E.02323
G1 X127.849 Y101.717
G1 X127.34 Y101.207 E.02212
G1 X126.955 Y101.356
G1 X127.47 Y101.871 E.02236
G1 X127.081 Y102.015
G1 X126.55 Y101.484 E.02305
G1 X126.138 Y101.605
G1 X126.673 Y102.141 E.02328
G1 X126.259 Y102.26
G1 X125.701 Y101.702 E.02425
G1 X125.255 Y101.788
G1 X125.821 Y102.355 E.02461
G1 X125.376 Y102.443
G1 X124.783 Y101.85 E.02577
G1 X124.293 Y101.894
G1 X124.904 Y102.504 E.02651
G1 X124.42 Y102.554
G1 X123.783 Y101.916 E.02771
G1 X123.235 Y101.902
G1 X123.908 Y102.575 E.02923
G1 X123.373 Y102.573
G1 X122.665 Y101.865 E.03078
G1 X122.051 Y101.784
G1 X122.814 Y102.548 E.03318
G1 X122.208 Y102.474
G1 X121.378 Y101.644 E.03608
G1 X120.636 Y101.436
G1 X121.566 Y102.366 E.04041
G1 X120.874 Y102.207
G1 X119.787 Y101.12 E.04725
G1 X118.743 Y100.609
G1 X120.096 Y101.962 E.05879
G1 X119.19 Y101.589
G1 X114.087 Y96.487 E.22175
; WIPE_START
M204 S10000
G1 X115.501 Y97.901 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X114.754 Y97.687 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X117.985 Y100.917 E.14037
; WIPE_START
M204 S10000
G1 X116.57 Y99.503 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X123.914 Y97.423 Z1.4 F30000
G1 X167.915 Y84.96 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.1075
G1 F15000
G1 X167.677 Y84.694 E.00188
; LINE_WIDTH: 0.146177
G1 X167.439 Y84.428 E.003
; LINE_WIDTH: 0.170591
G2 X166.034 Y83.045 I-16.882 J15.752 E.02052
; LINE_WIDTH: 0.110869
G1 X165.779 Y82.824 E.00187
; WIPE_START
G1 X166.034 Y83.045 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X164.757 Y82.221 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.206018
G1 F15000
G1 X164.579 Y82.08 E.00302
; LINE_WIDTH: 0.164578
G1 X164.401 Y81.939 E.00225
; LINE_WIDTH: 0.129936
G1 X164.32 Y81.88 E.00071
; LINE_WIDTH: 0.102093
G1 X164.239 Y81.821 E.00048
; WIPE_START
G1 X164.32 Y81.88 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X162.923 Y83.329 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.167319
G1 F15000
G2 X162.798 Y83.084 I-2.361 J1.055 E.00279
; WIPE_START
G1 X162.923 Y83.329 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X155.293 Y83.167 Z1.4 F30000
G1 X149.11 Y83.035 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.126713
G1 F15000
M73 P80 R2
G1 X149.053 Y83.132 E.00077
G1 X149.08 Y83.22 E.00063
; WIPE_START
G1 X149.053 Y83.132 E-.3399
G1 X149.11 Y83.035 E-.4201
; WIPE_END
G1 E-.04 F1800
G1 X141.488 Y82.644 Z1.4 F30000
G1 X121.599 Y81.624 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.09581
G1 F15000
G1 X121.437 Y81.707 E.00078
; WIPE_START
G1 X121.599 Y81.624 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X118.167 Y88.442 Z1.4 F30000
G1 X114.149 Y96.424 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.190635
G1 F15000
G1 X114.069 Y96.305 E.00173
; LINE_WIDTH: 0.149651
G1 X113.988 Y96.186 E.00125
; LINE_WIDTH: 0.108667
G1 X113.908 Y96.067 E.00077
; WIPE_START
G1 X113.988 Y96.186 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X114.815 Y97.627 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.21442
G1 F15000
G1 X114.7 Y97.485 E.00254
; LINE_WIDTH: 0.185939
G1 X114.586 Y97.343 E.00212
; LINE_WIDTH: 0.150824
G1 X114.495 Y97.221 E.00134
; LINE_WIDTH: 0.109058
G1 X114.405 Y97.098 E.00082
; WIPE_START
G1 X114.495 Y97.221 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.47 Y97.574 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.100707
G1 F15000
G1 X115.394 Y97.479 E.00058
; LINE_WIDTH: 0.125771
G1 X115.318 Y97.383 E.00082
; LINE_WIDTH: 0.16048
G1 X115.167 Y97.194 E.00232
; LINE_WIDTH: 0.204849
G1 X115.016 Y97.004 E.0032
; WIPE_START
G1 X115.167 Y97.194 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.92 Y100.151 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.111626
G1 F15000
G3 X115.545 Y98.775 I18.002 J-19.361 E.01089
; WIPE_START
G1 X116.244 Y99.507 E-.39552
G1 X116.92 Y100.151 E-.36448
; WIPE_END
G1 E-.04 F1800
G1 X118.681 Y100.671 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.202172
G1 F15000
G1 X118.488 Y100.516 E.00321
; LINE_WIDTH: 0.156571
G1 X118.295 Y100.361 E.00229
; LINE_WIDTH: 0.110971
G1 X118.102 Y100.207 E.00137
; WIPE_START
G1 X118.295 Y100.361 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X118.58 Y101.273 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.101734
G1 F15000
G1 X118.499 Y101.214 E.00048
; LINE_WIDTH: 0.12888
G1 X118.419 Y101.156 E.0007
; LINE_WIDTH: 0.163738
G1 X118.232 Y101.006 E.00235
; LINE_WIDTH: 0.206296
G1 X118.045 Y100.857 E.00318
; WIPE_START
G1 X118.232 Y101.006 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X121.879 Y102.434 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0994367
G1 F15000
G1 X121.624 Y102.308 E.00131
; WIPE_START
G1 X121.879 Y102.434 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X129.493 Y101.896 Z1.4 F30000
G1 X134.351 Y101.553 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108274
G1 F15000
G1 X134.168 Y101.586 E.00099
G1 X134.526 Y100.901 F30000
; LINE_WIDTH: 0.104395
G1 F15000
G1 X134.311 Y100.98 E.00115
; WIPE_START
G1 X134.526 Y100.901 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X142.126 Y101.605 Z1.4 F30000
G1 X144.193 Y101.796 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.10974
G1 F15000
G1 X143.956 Y101.853 E.00133
; WIPE_START
G1 X144.193 Y101.796 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.474 Y102.572 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108046
G1 F15000
G1 X145.332 Y102.46 E.00096
; LINE_WIDTH: 0.148082
G1 X145.187 Y102.346 E.00158
; LINE_WIDTH: 0.181809
G1 X145.072 Y102.259 E.00163
; LINE_WIDTH: 0.208801
G1 X144.957 Y102.172 E.00195
; WIPE_START
G1 X145.072 Y102.259 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.859 Y103.424 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.111183
G1 F15000
G1 X146.674 Y103.278 E.00131
; LINE_WIDTH: 0.157219
G1 X146.489 Y103.132 E.00219
; LINE_WIDTH: 0.203255
G1 X146.305 Y102.986 E.00308
; WIPE_START
G1 X146.489 Y103.132 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X148.902 Y105.052 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.201828
G1 F15000
G1 X148.453 Y104.559 E.00864
G1 X148.112 Y104.223 E.0062
; LINE_WIDTH: 0.216019
G1 X147.746 Y103.893 E.00695
; WIPE_START
G1 X148.112 Y104.223 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.578 Y106.251 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.178945
G1 F15000
G1 X149.489 Y106.121 E.00175
; LINE_WIDTH: 0.155429
G1 X149.402 Y106 E.00137
; LINE_WIDTH: 0.110593
G1 X149.315 Y105.879 E.00082
; WIPE_START
G1 X149.402 Y106 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.811 Y106.881 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.133613
G1 F15000
G1 X149.748 Y107.11 E.00175
; WIPE_START
G1 X149.811 Y106.881 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.716 Y114.513 Z1.4 F30000
G1 X149.699 Y115.814 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.128967
G1 F15000
G1 X149.583 Y115.59 E.00177
; WIPE_START
G1 X149.699 Y115.814 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.508 Y117.384 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.203528
G1 F15000
G1 X149.32 Y117.094 E.00452
; WIPE_START
G1 X149.508 Y117.384 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X151.089 Y119.329 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.11066
G1 F15000
G1 X150.953 Y119.159 E.0012
; LINE_WIDTH: 0.15625
G1 X150.813 Y118.984 E.00207
; LINE_WIDTH: 0.199368
G1 X150.683 Y118.808 E.00279
G1 X150.448 Y119.394 F30000
; LINE_WIDTH: 0.205358
G1 F15000
G1 X150.338 Y119.252 E.00238
; LINE_WIDTH: 0.167467
G1 X150.227 Y119.109 E.00183
; LINE_WIDTH: 0.129576
G1 X150.117 Y118.967 E.00127
; LINE_WIDTH: 0.0993881
G1 X150.066 Y118.894 E.00041
; WIPE_START
G1 X150.117 Y118.967 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X152.947 Y121.602 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.230953
G1 F15000
G3 X151.847 Y120.502 I12.119 J-13.218 E.02384
; WIPE_START
G1 X152.383 Y121.061 E-.37818
G1 X152.947 Y121.602 E-.38182
; WIPE_END
G1 E-.04 F1800
G1 X153.097 Y122.461 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0971577
G1 F15000
G1 X152.999 Y122.379 E.00056
; LINE_WIDTH: 0.125668
G1 X152.668 Y122.075 E.00303
; LINE_WIDTH: 0.178137
G3 X151.702 Y121.138 I10.512 J-11.799 E.01483
; LINE_WIDTH: 0.166844
G1 X151.398 Y120.807 E.00454
; LINE_WIDTH: 0.129295
G1 X151.093 Y120.476 E.00316
; LINE_WIDTH: 0.0993593
G1 X150.993 Y120.357 E.00071
; WIPE_START
G1 X151.093 Y120.476 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.641 Y122.766 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.198832
G1 F15000
G1 X154.46 Y122.633 E.00285
; LINE_WIDTH: 0.155632
G1 X154.291 Y122.497 E.002
; LINE_WIDTH: 0.110658
G1 X154.121 Y122.36 E.0012
; WIPE_START
G1 X154.291 Y122.497 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.545 Y123.373 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.105134
G1 F15000
G1 X154.443 Y123.301 E.00063
; LINE_WIDTH: 0.139096
G1 X154.314 Y123.202 E.00128
; LINE_WIDTH: 0.173039
G1 X154.185 Y123.102 E.00173
; LINE_WIDTH: 0.206982
G1 X154.056 Y123.003 E.00218
; WIPE_START
G1 X154.185 Y123.102 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X157.859 Y123.867 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.128953
G1 F15000
G1 X157.635 Y123.75 E.00177
; WIPE_START
G1 X157.859 Y123.867 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X163.483 Y118.706 Z1.4 F30000
G1 X169.406 Y113.269 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.118671
G1 F15000
G1 X169.316 Y113.074 E.00133
; WIPE_START
G1 X169.406 Y113.269 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.805 Y105.647 Z1.4 F30000
G1 X170.134 Y99.368 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0910721
G1 F15000
G1 X170.23 Y99.56 E.00084
; WIPE_START
G1 X170.134 Y99.368 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.068 Y91.81 Z1.4 F30000
G1 X168.948 Y90.955 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.18129
G1 F15000
G1 X168.864 Y90.836 E.00165
; LINE_WIDTH: 0.161676
G1 X168.783 Y90.729 E.0013
; LINE_WIDTH: 0.125803
G1 X168.696 Y90.618 E.00095
; LINE_WIDTH: 0.106348
G2 X168.216 Y90.161 I-3.01 J2.68 E.00343
; LINE_WIDTH: 0.157362
G1 X168.102 Y90.081 E.0013
; LINE_WIDTH: 0.191169
G1 X167.988 Y90.001 E.00168
; WIPE_START
G1 X168.102 Y90.081 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.637 Y93.003 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108888
G1 F15000
G3 X167.474 Y93.081 I-.973 J-1.804 E.00097
G1 X167.027 Y93.056 F30000
; LINE_WIDTH: 0.104702
G1 F15000
G3 X166.709 Y92.821 I2.004 J-3.045 E.00199
G1 X167.116 Y92.967 F30000
; LINE_WIDTH: 0.112906
G1 F15000
G1 X166.888 Y93.028 E.00135
; WIPE_START
G1 X167.116 Y92.967 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.923 Y92.063 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.118248
G1 F15000
G1 X165.981 Y91.835 E.00145
; WIPE_START
G1 X165.923 Y92.063 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.909 Y89.117 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.116434
G1 F15000
G1 X169.909 Y88.914 E.00122
; WIPE_START
G1 X169.909 Y89.117 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X169.405 Y87.521 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108924
G1 F15000
M73 P80 R1
G1 X169.32 Y87.397 E.0008
; LINE_WIDTH: 0.15042
G1 X169.236 Y87.274 E.00131
; LINE_WIDTH: 0.191917
G1 X169.151 Y87.151 E.00182
G1 X168.906 Y86.487 F30000
; LINE_WIDTH: 0.11118
G1 F15000
G1 X168.785 Y86.326 E.00112
; LINE_WIDTH: 0.15719
G1 X168.664 Y86.165 E.00188
; LINE_WIDTH: 0.2032
G1 X168.543 Y86.003 E.00263
; WIPE_START
G1 X168.664 Y86.165 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.712 Y93.797 Z1.4 F30000
G1 X168.818 Y110.424 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.10509
G1 F15000
G1 X168.765 Y110.664 E.00125
; WIPE_START
G1 X168.818 Y110.424 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X168.454 Y109.671 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.197243
G1 F15000
G1 X168.348 Y109.525 E.00227
; LINE_WIDTH: 0.15361
G1 X168.241 Y109.379 E.00163
; LINE_WIDTH: 0.109978
G1 X168.134 Y109.234 E.00099
G1 X167.738 Y108.423 F30000
; LINE_WIDTH: 0.217858
G1 F15000
G1 X167.62 Y108.275 E.00269
; LINE_WIDTH: 0.188478
G1 X167.43 Y108.059 E.00342
; LINE_WIDTH: 0.15075
G1 X167.24 Y107.842 E.00253
; LINE_WIDTH: 0.105279
G1 X166.941 Y107.511 E.00227
; WIPE_START
G1 X167.24 Y107.842 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.938 Y106.509 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0910988
G1 F15000
G1 X165.825 Y106.4 E.00062
; LINE_WIDTH: 0.113009
G1 X165.608 Y106.21 E.00165
; LINE_WIDTH: 0.15074
G1 X165.391 Y106.02 E.00253
; LINE_WIDTH: 0.188948
G1 X165.168 Y105.825 E.00352
; LINE_WIDTH: 0.218255
G1 X165.027 Y105.711 E.0026
G1 X164.216 Y105.315 F30000
; LINE_WIDTH: 0.109984
G1 F15000
G1 X164.07 Y105.209 E.00099
; LINE_WIDTH: 0.153615
G1 X163.925 Y105.102 E.00163
; LINE_WIDTH: 0.197245
G1 X163.779 Y104.995 E.00227
; WIPE_START
G1 X163.925 Y105.102 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X165.461 Y104.789 Z1.4 F30000
M73 P81 R1
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.201289
G1 F15000
G1 X165.291 Y104.658 E.00276
; LINE_WIDTH: 0.156044
G1 X165.122 Y104.527 E.00197
; LINE_WIDTH: 0.110799
G1 X164.952 Y104.397 E.00118
; WIPE_START
G1 X165.122 Y104.527 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.919 Y97.426 Z1.4 F30000
G1 X168.382 Y96.249 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.143833
G1 F15000
G1 X168.281 Y96.092 E.00153
; LINE_WIDTH: 0.128874
G1 X168.232 Y96.021 E.00061
; LINE_WIDTH: 0.101741
G1 X168.182 Y95.949 E.00042
G1 X168.363 Y96.104 F30000
; LINE_WIDTH: 0.109512
G1 F15000
G1 X168.299 Y96.332 E.00129
; WIPE_START
G1 X168.363 Y96.104 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X167.249 Y95.001 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.185292
G1 F15000
G2 X166.944 Y94.821 I-2.356 J3.659 E.00411
; WIPE_START
G1 X167.249 Y95.001 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X160.166 Y97.844 Z1.4 F30000
G1 X150.656 Y101.662 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0946611
G1 F15000
G2 X150.578 Y101.782 I1.323 J.941 E.0006
; WIPE_START
G1 X150.656 Y101.662 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X150.967 Y104.275 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.102842
G1 F15000
G1 X150.859 Y104.145 E.00083
; LINE_WIDTH: 0.132802
G1 X150.747 Y104.009 E.00129
; LINE_WIDTH: 0.162115
G1 X150.696 Y103.939 E.00084
; LINE_WIDTH: 0.197993
G1 X150.642 Y103.864 E.00118
G1 X150.673 Y103.718 E.00188
; WIPE_START
G1 X150.642 Y103.864 E-.46759
G1 X150.696 Y103.939 E-.29241
; WIPE_END
G1 E-.04 F1800
G1 X151.709 Y104.906 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.1948
G1 F15000
G1 X151.567 Y104.808 E.00214
; LINE_WIDTH: 0.158967
G1 X151.44 Y104.708 E.00152
; LINE_WIDTH: 0.119601
G1 X151.309 Y104.606 E.00104
; LINE_WIDTH: 0.0940951
G1 X151.169 Y104.475 E.0008
; WIPE_START
G1 X151.309 Y104.606 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X154.259 Y104.211 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0984224
G1 F15000
G1 X154.154 Y104.291 E.0006
; WIPE_START
G1 X154.259 Y104.211 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X153.507 Y96.615 Z1.4 F30000
G1 X152.946 Y90.952 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.182952
G1 F15000
G1 X152.865 Y90.835 E.00162
; LINE_WIDTH: 0.163314
G1 X152.783 Y90.729 E.00131
; LINE_WIDTH: 0.127413
G1 X152.697 Y90.617 E.00097
; LINE_WIDTH: 0.107971
G2 X152.217 Y90.16 I-3.011 J2.681 E.00352
; LINE_WIDTH: 0.158741
G1 X152.104 Y90.081 E.0013
; LINE_WIDTH: 0.191958
G1 X151.991 Y90.002 E.00167
; WIPE_START
G1 X152.104 Y90.081 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X151.639 Y93.002 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.109767
G1 F15000
G3 X151.476 Y93.081 I-.968 J-1.791 E.00099
G1 X151.03 Y93.057 F30000
; LINE_WIDTH: 0.103424
G1 F15000
G3 X150.715 Y92.825 I1.96 J-2.987 E.00193
G1 X151.119 Y92.968 F30000
; LINE_WIDTH: 0.11599
G1 F15000
G1 X150.89 Y93.029 E.00141
; WIPE_START
G1 X151.119 Y92.968 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X149.921 Y92.059 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.116001
G1 F15000
G1 X149.981 Y91.831 E.00141
G1 X150.117 Y92.227 F30000
; LINE_WIDTH: 0.105219
G1 F15000
G3 X149.895 Y91.917 I3.427 J-2.689 E.00194
; WIPE_START
G1 X150.117 Y92.227 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.155 Y98.425 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.11124
G1 F15000
G2 X145.99 Y98.503 I.621 J1.526 E.00101
G1 X146.921 Y98.685 F30000
; LINE_WIDTH: 0.10873
G1 F15000
G1 X146.815 Y98.611 E.0007
; LINE_WIDTH: 0.151734
G1 X146.699 Y98.53 E.00125
; LINE_WIDTH: 0.186117
G1 X146.594 Y98.47 E.00141
; WIPE_START
G1 X146.699 Y98.53 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.715 Y99.573 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.113596
G1 F15000
G2 X147.478 Y99.243 I-3.822 J2.508 E.00234
G1 X147.691 Y99.428 F30000
; LINE_WIDTH: 0.0954006
G1 F15000
G1 X147.629 Y99.659 E.00102
; WIPE_START
G1 X147.691 Y99.428 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.639 Y101.515 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.169635
G1 F15000
G1 X145.498 Y101.413 E.0018
; LINE_WIDTH: 0.147557
G1 X145.347 Y101.292 E.00165
; LINE_WIDTH: 0.107965
G1 X145.197 Y101.172 E.00102
G1 X145 Y100.975 F30000
; LINE_WIDTH: 0.122793
G1 F15000
G3 X144.658 Y100.54 I3.849 J-3.389 E.0036
; WIPE_START
G1 X145 Y100.975 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X144.314 Y93.373 Z1.4 F30000
G1 X143.483 Y84.162 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.201439
G1 F15000
G1 X143.378 Y84.026 E.00221
; LINE_WIDTH: 0.167593
G1 X143.27 Y83.885 E.00181
; LINE_WIDTH: 0.133035
G1 X143.038 Y83.631 E.00252
G1 X142.791 Y83.406 E.00245
; LINE_WIDTH: 0.169712
G1 X142.646 Y83.29 E.00192
; LINE_WIDTH: 0.202591
G1 X142.518 Y83.2 E.00204
; WIPE_START
G1 X142.646 Y83.29 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.006 Y84.982 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.12374
G1 F15000
G3 X144.66 Y84.544 I3.858 J-3.402 E.00368
; WIPE_START
G1 X145.006 Y84.982 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X145.636 Y85.513 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.171297
G1 F15000
G1 X145.498 Y85.414 E.00178
; LINE_WIDTH: 0.148769
G1 X145.344 Y85.291 E.0017
; LINE_WIDTH: 0.10837
G1 X145.19 Y85.168 E.00105
; WIPE_START
G1 X145.344 Y85.291 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X147.718 Y83.573 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.110594
G1 F15000
G2 X147.469 Y83.237 I-3.165 J2.089 E.00231
G1 X147.691 Y83.431 F30000
; LINE_WIDTH: 0.0984798
G1 F15000
G1 X147.63 Y83.661 E.00108
; WIPE_START
G1 X147.691 Y83.431 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X146.917 Y82.683 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108316
G1 F15000
G1 X146.813 Y82.61 E.00068
; LINE_WIDTH: 0.150467
G1 X146.699 Y82.531 E.00122
; LINE_WIDTH: 0.185249
G1 X146.591 Y82.469 E.00144
G1 X146.153 Y82.426 F30000
; LINE_WIDTH: 0.11213
G1 F15000
G2 X145.988 Y82.504 I.618 J1.518 E.00103
; WIPE_START
G1 X146.153 Y82.426 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X138.533 Y82.873 Z1.4 F30000
G1 X134.064 Y83.135 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0936028
G1 F15000
G2 X133.944 Y83.213 I.832 J1.416 E.00059
; WIPE_START
G1 X134.064 Y83.135 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.115 Y86.664 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.207407
G1 F15000
G1 X131.968 Y86.481 E.00315
; LINE_WIDTH: 0.166008
G1 X131.818 Y86.294 E.0024
; LINE_WIDTH: 0.130882
G1 X131.667 Y86.122 E.00164
; LINE_WIDTH: 0.102402
G1 X131.516 Y85.95 E.00111
; WIPE_START
G1 X131.667 Y86.122 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X133.402 Y86.712 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.110594
G1 F15000
G1 X133.278 Y86.548 E.00113
; LINE_WIDTH: 0.155488
G1 X133.153 Y86.385 E.00189
; LINE_WIDTH: 0.200381
G1 X133.028 Y86.221 E.00264
; WIPE_START
G1 X133.153 Y86.385 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X132.681 Y87.907 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.181199
G1 F15000
G1 X132.706 Y87.763 E.00165
; LINE_WIDTH: 0.191386
G1 X132.621 Y87.647 E.00173
; LINE_WIDTH: 0.150096
G1 X132.537 Y87.532 E.00125
; LINE_WIDTH: 0.108806
G1 X132.452 Y87.416 E.00077
; WIPE_START
G1 X132.537 Y87.532 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X133.198 Y95.136 Z1.4 F30000
G1 X133.687 Y100.761 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.187048
G1 F15000
G1 X133.509 Y100.619 E.00268
; LINE_WIDTH: 0.150665
G1 X133.146 Y100.275 E.00439
; LINE_WIDTH: 0.169583
G1 X132.939 Y100.034 E.00328
; LINE_WIDTH: 0.207052
G1 X132.832 Y99.892 E.00238
; WIPE_START
G1 X132.939 Y100.034 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X131.424 Y92.553 Z1.4 F30000
G1 X129.722 Y84.156 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.102406
G1 F15000
G1 X129.55 Y84.005 E.00111
; LINE_WIDTH: 0.131163
G1 X129.375 Y83.851 E.00168
; LINE_WIDTH: 0.166404
G1 X129.191 Y83.704 E.00236
; LINE_WIDTH: 0.207409
G1 X129.008 Y83.557 E.00315
G1 X128.256 Y83.22 F30000
; LINE_WIDTH: 0.108812
G1 F15000
G1 X128.141 Y83.136 E.00077
; LINE_WIDTH: 0.150099
G1 X128.025 Y83.051 E.00125
; LINE_WIDTH: 0.186279
G1 X127.91 Y82.966 E.00167
G1 X127.765 Y82.991 E.00171
G1 X127.278 Y82.774 F30000
; LINE_WIDTH: 0.109264
G1 F15000
G1 X127.179 Y82.708 E.00065
; LINE_WIDTH: 0.163579
G2 X126.96 Y82.565 I-3.583 J5.255 E.00257
; OBJECT_ID: 817
; WIPE_START
G1 X127.179 Y82.708 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 861
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X123.947 Y89.622 Z1.4 F30000
G1 X103.02 Y134.4 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X102.965 Y134.398 E.00168
G3 X102.723 Y115.004 I.363 J-9.703 E.90751
G3 X103.691 Y114.992 I.617 J10.646 E.02975
G3 X103.449 Y134.404 I-.363 J9.703 E.92241
G1 X103.08 Y134.4 E.01135
; WIPE_START
M204 S10000
G1 X102.965 Y134.398 E-.04363
G1 X102.482 Y134.369 E-.18388
G1 X102.001 Y134.314 E-.18397
G1 X101.523 Y134.236 E-.18405
G1 X101.1 Y134.145 E-.16446
; WIPE_END
G1 E-.04 F1800
G1 X103.737 Y126.983 Z1.4 F30000
G1 X112.94 Y101.985 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X113.435 Y101.827 I.639 J1.143 E.01606
G1 X113.556 Y101.819 E.00375
G3 X112.888 Y102.016 I.022 J1.309 E.23114
; WIPE_START
M204 S10000
G1 X113.18 Y101.882 E-.12184
G1 X113.435 Y101.827 E-.09909
G1 X113.556 Y101.819 E-.04637
G1 X113.761 Y101.831 E-.07771
G1 X114.014 Y101.892 E-.0991
G1 X114.251 Y102.002 E-.09913
G1 X114.461 Y102.157 E-.09922
G1 X114.636 Y102.351 E-.09922
G1 X114.66 Y102.392 E-.01833
; WIPE_END
G1 E-.04 F1800
G1 X119.951 Y107.894 Z1.4 F30000
G1 X126.201 Y114.394 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X124.748 Y113.141 I-1.308 J.048 E.18665
G1 X124.87 Y113.133 E.00375
G3 X126.197 Y114.334 I.022 J1.309 E.06056
; WIPE_START
M204 S10000
G1 X126.188 Y114.654 E-.12165
G1 X126.121 Y114.906 E-.0992
G1 X126.005 Y115.14 E-.09914
G1 X125.845 Y115.346 E-.09914
G1 X125.647 Y115.516 E-.09913
G1 X125.419 Y115.643 E-.09908
G1 X125.297 Y115.69 E-.04976
G1 X125.058 Y115.741 E-.0929
; WIPE_END
G1 E-.04 F1800
G1 X119.768 Y121.243 Z1.4 F30000
G1 X102.124 Y139.592 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X100.707 Y138.596 I-1.273 J.306 E.19466
G1 X100.829 Y138.589 E.00375
G3 X102.108 Y139.534 I.022 J1.309 E.05254
; WIPE_START
M204 S10000
M73 P82 R1
G1 X102.163 Y139.849 E-.12171
G1 X102.147 Y140.11 E-.09912
G1 X102.079 Y140.362 E-.0992
G1 X101.963 Y140.595 E-.09913
G1 X101.888 Y140.702 E-.04965
G1 X101.708 Y140.891 E-.0991
G1 X101.494 Y141.041 E-.09922
G1 X101.27 Y141.139 E-.09287
; WIPE_END
G1 E-.04 F1800
G1 X96.43 Y135.237 Z1.4 F30000
G1 X89.178 Y126.394 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X87.979 Y125.868 I-1.055 J.776 E.21068
G1 X88.101 Y125.861 E.00375
G3 X89.141 Y126.347 I.022 J1.309 E.03652
; WIPE_START
M204 S10000
G1 X89.313 Y126.617 E-.12172
G1 X89.399 Y126.863 E-.09922
G1 X89.435 Y127.121 E-.09908
G1 X89.419 Y127.382 E-.09914
G1 X89.351 Y127.634 E-.09923
G1 X89.235 Y127.868 E-.09912
G1 X89.075 Y128.074 E-.09915
G1 X88.988 Y128.148 E-.04334
; WIPE_END
G1 E-.04 F1800
G1 X85.872 Y128.793 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S5000
G3 X86.16 Y125.897 I1.942 J-1.269 E.09666
G1 X110.894 Y101.163 E1.07482
G3 X112.549 Y100.489 I1.674 J1.742 E.05624
G3 X114.147 Y101.163 I-.025 J2.29 E.05467
G1 X126.861 Y113.877 E.55246
G3 X126.861 Y117.13 I-1.654 J1.627 E.11078
G1 X102.127 Y141.864 E1.07482
G3 X98.873 Y141.864 I-1.627 J-1.654 E.11077
G1 X86.16 Y129.151 E.55246
G3 X85.906 Y128.843 I1.654 J-1.627 E.01228
; WIPE_START
M204 S10000
G1 X85.657 Y128.4 E-.19302
G1 X85.527 Y127.971 E-.17053
G1 X85.483 Y127.524 E-.1705
G1 X85.527 Y127.077 E-.17051
G1 X85.569 Y126.938 E-.05543
; WIPE_END
G1 E-.04 F1800
G1 X91.274 Y121.867 Z1.4 F30000
G1 X114.103 Y101.572 Z1.4
G1 Z1
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.21625
G1 F15000
G3 X114.383 Y101.773 I-3.946 J5.802 E.00487
; LINE_WIDTH: 0.148141
G1 X114.624 Y101.98 E.00273
G1 X114.937 Y102.327 E.00401
; LINE_WIDTH: 0.216185
G3 X115.138 Y102.608 I-5.316 J4.018 E.00487
; WIPE_START
G1 X114.937 Y102.327 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X120.314 Y107.745 Z1.4 F30000
G1 X125.416 Y112.886 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.216142
G1 F15000
G3 X125.697 Y113.087 I-3.834 J5.647 E.00487
; LINE_WIDTH: 0.148121
G1 X125.938 Y113.294 E.00272
G1 X126.251 Y113.641 E.00401
; LINE_WIDTH: 0.216219
G3 X126.452 Y113.921 I-5.453 J4.118 E.00487
; WIPE_START
G1 X126.251 Y113.641 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X127.318 Y115.392 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S2000
G1 X126.411 Y114.485 E.03944
G1 X126.329 Y114.936
G1 X127.291 Y115.898 E.04178
G1 X127.167 Y116.307
G1 X126.151 Y115.292 E.04413
G1 X125.903 Y115.576
G1 X126.981 Y116.655 E.04685
G1 X126.741 Y116.948
G1 X125.586 Y115.792 E.05023
G1 X125.19 Y115.93
G1 X126.479 Y117.219 E.05598
G1 X126.212 Y117.485
G1 X124.668 Y115.942 E.06708
; WIPE_START
M204 S10000
G1 X126.083 Y117.356 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X124.852 Y112.926 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X115.097 Y103.171 E.42391
G1 X115.015 Y103.622
G1 X124.401 Y113.008 E.40787
G1 X124.046 Y113.186
G1 X114.838 Y103.978 E.40013
G1 X114.589 Y104.263
G1 X123.762 Y113.435 E.3986
G1 X123.545 Y113.751
G1 X114.272 Y104.479 E.40295
G1 X113.877 Y104.617
G1 X123.408 Y114.148 E.41418
G1 X123.395 Y114.668
G1 X113.355 Y104.628 E.4363
; WIPE_START
M204 S10000
G1 X114.769 Y106.042 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X113.539 Y101.612 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X112.632 Y100.706 E.0394
G1 X112.126 Y100.733
G1 X113.088 Y101.695 E.04177
G1 X112.732 Y101.872
G1 X111.717 Y100.857 E.04411
G1 X111.369 Y101.043
G1 X112.448 Y102.122 E.04688
G1 X112.231 Y102.438
G1 X111.076 Y101.283 E.0502
G1 X110.805 Y101.545
G1 X112.094 Y102.834 E.056
G1 X112.081 Y103.355
G1 X110.539 Y101.812 E.06703
G1 X110.272 Y102.079
G1 X125.945 Y117.752 E.68108
G1 X125.679 Y118.018
G1 X110.006 Y102.345 E.68108
G1 X109.739 Y102.612
G1 X125.412 Y118.285 E.68108
G1 X125.145 Y118.552
G1 X109.472 Y102.879 E.68108
G1 X109.206 Y103.145
G1 X124.879 Y118.818 E.68108
G1 X124.612 Y119.085
G1 X108.939 Y103.412 E.68108
G1 X108.672 Y103.678
G1 X124.346 Y119.352 E.68108
G1 X124.079 Y119.618
G1 X108.406 Y103.945 E.68108
G1 X108.139 Y104.212
G1 X123.812 Y119.885 E.68108
M73 P83 R1
G1 X123.546 Y120.152
G1 X107.872 Y104.478 E.68108
G1 X107.606 Y104.745
G1 X123.279 Y120.418 E.68108
G1 X123.012 Y120.685
G1 X107.339 Y105.012 E.68108
G1 X107.073 Y105.278
G1 X122.746 Y120.951 E.68108
G1 X122.479 Y121.218
G1 X106.806 Y105.545 E.68108
G1 X106.539 Y105.811
G1 X122.213 Y121.485 E.68108
G1 X121.946 Y121.751
G1 X106.273 Y106.078 E.68108
G1 X106.006 Y106.345
G1 X121.679 Y122.018 E.68108
G1 X121.413 Y122.285
G1 X105.739 Y106.611 E.68108
G1 X105.473 Y106.878
G1 X121.146 Y122.551 E.68108
G1 X120.879 Y122.818
G1 X105.206 Y107.145 E.68108
G1 X104.94 Y107.411
G1 X120.613 Y123.084 E.68108
G1 X120.346 Y123.351
G1 X104.673 Y107.678 E.68108
G1 X104.406 Y107.945
G1 X120.079 Y123.618 E.68108
G1 X119.813 Y123.884
G1 X104.14 Y108.211 E.68108
G1 X103.873 Y108.478
G1 X119.546 Y124.151 E.68108
G1 X119.28 Y124.418
G1 X103.606 Y108.744 E.68108
G1 X103.34 Y109.011
G1 X119.013 Y124.684 E.68108
G1 X118.746 Y124.951
G1 X103.073 Y109.278 E.68108
G1 X102.807 Y109.544
G1 X118.48 Y125.217 E.68108
G1 X118.213 Y125.484
G1 X102.54 Y109.811 E.68108
G1 X102.273 Y110.078
G1 X108.328 Y116.132 E.26311
G1 X107.254 Y115.591
G1 X102.007 Y110.344 E.22801
G1 X101.74 Y110.611
G1 X106.397 Y115.268 E.20238
G1 X105.65 Y115.054
G1 X101.473 Y110.877 E.18148
G1 X101.207 Y111.144
G1 X104.983 Y114.92 E.16408
G1 X104.365 Y114.835
G1 X100.94 Y111.411 E.14881
G1 X100.674 Y111.677
G1 X103.787 Y114.79 E.13528
G1 X103.244 Y114.781
G1 X100.407 Y111.944 E.1233
G1 X100.14 Y112.211
G1 X102.726 Y114.797 E.11238
M73 P84 R1
G1 X102.235 Y114.839
G1 X99.874 Y112.477 E.10263
G1 X99.607 Y112.744
G1 X101.766 Y114.903 E.09382
G1 X101.316 Y114.986
G1 X99.34 Y113.01 E.08585
G1 X99.074 Y113.277
G1 X100.883 Y115.087 E.07863
G1 X100.466 Y115.203
G1 X98.807 Y113.544 E.07211
G1 X98.54 Y113.81
G1 X100.064 Y115.334 E.06621
G1 X99.675 Y115.478
G1 X98.274 Y114.077 E.06089
G1 X98.007 Y114.344
G1 X99.299 Y115.635 E.05613
G1 X98.935 Y115.805
G1 X97.741 Y114.61 E.05191
G1 X97.474 Y114.877
G1 X98.585 Y115.988 E.0483
G1 X98.246 Y116.183
G1 X97.207 Y115.143 E.04516
G1 X96.941 Y115.41
G1 X97.918 Y116.387 E.04246
G1 X97.599 Y116.602
G1 X96.674 Y115.677 E.0402
G1 X96.407 Y115.943
G1 X97.292 Y116.828 E.03845
G1 X96.997 Y117.066
G1 X96.141 Y116.21 E.0372
G1 X95.874 Y116.477
G1 X96.711 Y117.313 E.03634
G1 X96.434 Y117.569
G1 X95.608 Y116.743 E.0359
G1 X95.341 Y117.01
G1 X96.167 Y117.836 E.0359
G1 X95.912 Y118.115
G1 X95.074 Y117.277 E.03642
G1 X94.808 Y117.543
G1 X95.667 Y118.403 E.03735
G1 X95.431 Y118.7
G1 X94.541 Y117.81 E.03868
G1 X94.274 Y118.076
G1 X95.205 Y119.007 E.04043
G1 X94.992 Y119.327
G1 X94.008 Y118.343 E.04277
G1 X93.741 Y118.61
G1 X94.789 Y119.658 E.04555
G1 X94.597 Y119.999
G1 X93.475 Y118.876 E.04877
G1 X93.208 Y119.143
G1 X94.415 Y120.35 E.05247
G1 X94.246 Y120.714
G1 X92.941 Y119.41 E.05668
G1 X92.675 Y119.676
G1 X94.091 Y121.092 E.06154
G1 X93.949 Y121.483
G1 X92.408 Y119.943 E.06694
G1 X92.141 Y120.209
G1 X93.82 Y121.888 E.07294
G1 X93.706 Y122.307
G1 X91.875 Y120.476 E.07957
G1 X91.608 Y120.743
G1 X93.608 Y122.742 E.08689
G1 X93.527 Y123.195
G1 X91.341 Y121.009 E.09498
G1 X91.075 Y121.276
G1 X93.466 Y123.667 E.10391
G1 X93.427 Y124.161
G1 X90.808 Y121.543 E.1138
G1 X90.542 Y121.809
G1 X93.413 Y124.681 E.12478
G1 X93.428 Y125.229
G1 X90.275 Y122.076 E.13701
G1 X90.008 Y122.342
G1 X93.477 Y125.811 E.15073
G1 X93.567 Y126.434
G1 X89.742 Y122.609 E.16621
G1 X89.475 Y122.876
G1 X93.712 Y127.112 E.18411
G1 X93.934 Y127.868
G1 X89.208 Y123.142 E.20536
G1 X88.942 Y123.409
G1 X94.278 Y128.746 E.2319
; WIPE_START
M204 S10000
G1 X92.864 Y127.331 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X94.872 Y129.873 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X88.675 Y123.676 E.26929
; WIPE_START
M204 S10000
G1 X90.089 Y125.09 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X97.499 Y123.257 Z1.4 F30000
G1 X111.892 Y119.696 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X117.946 Y125.751 E.26311
G1 X117.68 Y126.017
G1 X112.433 Y120.77 E.22801
G1 X112.756 Y121.627
G1 X117.413 Y126.284 E.20238
G1 X117.147 Y126.551
G1 X112.97 Y122.374 E.18148
G1 X113.104 Y123.041
G1 X116.88 Y126.817 E.16408
G1 X116.613 Y127.084
G1 X113.189 Y123.659 E.14881
G1 X113.234 Y124.237
G1 X116.347 Y127.35 E.13528
G1 X116.08 Y127.617
G1 X113.245 Y124.782 E.12321
G1 X113.227 Y125.298
G1 X115.813 Y127.884 E.11238
G1 X115.547 Y128.15
G1 X113.185 Y125.789 E.10263
G1 X113.121 Y126.258
G1 X115.28 Y128.417 E.09382
G1 X115.014 Y128.684
G1 X113.038 Y126.708 E.08585
G1 X112.937 Y127.141
G1 X114.747 Y128.95 E.07863
G1 X114.48 Y129.217
G1 X112.821 Y127.558 E.0721
G1 X112.69 Y127.96
G1 X114.214 Y129.484 E.06621
G1 X113.947 Y129.75
G1 X112.546 Y128.349 E.06089
G1 X112.389 Y128.725
G1 X113.68 Y130.017 E.05613
G1 X113.414 Y130.283
G1 X112.219 Y129.089 E.05191
G1 X112.036 Y129.439
G1 X113.147 Y130.55 E.0483
G1 X112.881 Y130.817
G1 X111.841 Y129.778 E.04516
G1 X111.637 Y130.106
G1 X112.614 Y131.083 E.04246
G1 X112.347 Y131.35
G1 X111.422 Y130.425 E.0402
M73 P85 R1
G1 X111.196 Y130.732
G1 X112.081 Y131.617 E.03845
G1 X111.814 Y131.883
G1 X110.958 Y131.027 E.0372
G1 X110.711 Y131.313
G1 X111.547 Y132.15 E.03634
G1 X111.281 Y132.416
G1 X110.455 Y131.59 E.0359
G1 X110.188 Y131.857
G1 X111.014 Y132.683 E.0359
G1 X110.747 Y132.95
G1 X109.909 Y132.112 E.03642
G1 X109.621 Y132.357
G1 X110.481 Y133.216 E.03735
G1 X110.214 Y133.483
G1 X109.324 Y132.593 E.03868
G1 X109.017 Y132.819
G1 X109.948 Y133.75 E.04043
G1 X109.681 Y134.016
G1 X108.697 Y133.032 E.04277
G1 X108.366 Y133.235
G1 X109.414 Y134.283 E.04555
G1 X109.148 Y134.549
G1 X108.025 Y133.427 E.04877
G1 X107.674 Y133.609
G1 X108.881 Y134.816 E.05247
G1 X108.614 Y135.083
G1 X107.31 Y133.778 E.05668
G1 X106.932 Y133.933
G1 X108.348 Y135.349 E.06154
G1 X108.081 Y135.616
G1 X106.541 Y134.075 E.06694
G1 X106.136 Y134.204
G1 X107.815 Y135.883 E.07294
G1 X107.548 Y136.149
G1 X105.717 Y134.318 E.07957
G1 X105.282 Y134.416
G1 X107.281 Y136.416 E.08689
G1 X107.015 Y136.682
G1 X104.829 Y134.497 E.09498
G1 X104.357 Y134.558
G1 X106.748 Y136.949 E.10391
G1 X106.481 Y137.216
G1 X103.863 Y134.597 E.1138
G1 X103.343 Y134.611
G1 X106.215 Y137.482 E.12478
G1 X105.948 Y137.749
G1 X102.795 Y134.596 E.13701
G1 X102.213 Y134.547
G1 X105.682 Y138.016 E.15073
G1 X105.415 Y138.282
G1 X101.59 Y134.457 E.16621
G1 X100.911 Y134.312
G1 X105.148 Y138.549 E.18411
G1 X104.882 Y138.816
G1 X100.156 Y134.09 E.20536
G1 X99.278 Y133.746
G1 X104.615 Y139.082 E.2319
G1 X104.348 Y139.349
G1 X98.151 Y133.152 E.26929
; WIPE_START
M204 S10000
G1 X99.566 Y134.566 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X104.082 Y139.615 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X88.409 Y123.942 E.68108
G1 X88.142 Y124.209
G1 X103.815 Y139.882 E.68108
G1 X103.548 Y140.149
G1 X87.875 Y124.475 E.68108
G1 X87.609 Y124.742
G1 X88.595 Y125.728 E.04285
G1 X87.993 Y125.66
G1 X87.342 Y125.009 E.02829
G1 X87.075 Y125.275
G1 X87.563 Y125.763 E.02117
G1 X87.221 Y125.954
G1 X86.809 Y125.542 E.01789
G1 X86.542 Y125.809
G1 X86.948 Y126.215 E.01764
G1 X86.745 Y126.544
G1 X86.279 Y126.079 E.02022
G1 X86.04 Y126.373
G1 X86.624 Y126.957 E.02539
G1 X86.648 Y127.514
G1 X85.854 Y126.72 E.03449
; WIPE_START
M204 S10000
G1 X86.648 Y127.514 E-.42658
G1 X86.624 Y126.957 E-.21181
G1 X86.398 Y126.731 E-.12161
; WIPE_END
G1 E-.04 F1800
G1 X89.568 Y126.701 Z1.4 F30000
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X101.323 Y138.456 E.51081
G1 X100.721 Y138.388
G1 X89.636 Y127.303 E.48168
G1 X89.534 Y127.734
G1 X100.291 Y138.49 E.46743
G1 X99.949 Y138.682
G1 X89.342 Y128.076 E.46088
G1 X89.081 Y128.348
G1 X99.676 Y138.943 E.46039
G1 X99.473 Y139.272
G1 X88.752 Y128.552 E.46585
G1 X88.339 Y128.672
G1 X99.352 Y139.685 E.47858
G1 X99.376 Y140.242
G1 X87.78 Y128.647 E.50387
; WIPE_START
M204 S10000
G1 X89.195 Y130.061 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X95.403 Y134.5 Z1.4 F30000
G1 X102.296 Y139.429 Z1.4
G1 Z1
G1 E.8 F1800
G1 F9547.055
M204 S2000
G1 X103.282 Y140.415 E.04285
G1 X103.015 Y140.682
G1 X102.364 Y140.031 E.02829
G1 X102.262 Y140.462
G1 X102.749 Y140.949 E.02116
G1 X102.482 Y141.215
G1 X102.07 Y140.804 E.01788
G1 X101.809 Y141.076
G1 X102.215 Y141.482 E.01765
G1 X101.945 Y141.745
G1 X101.48 Y141.28 E.0202
G1 X101.067 Y141.4
G1 X101.651 Y141.984 E.02541
M73 P86 R1
G1 X101.304 Y142.17
G1 X100.508 Y141.375 E.03457
G1 X100.894 Y142.294
G1 X85.73 Y127.13 E.65895
G1 X85.702 Y127.635
G1 X100.389 Y142.322 E.6382
; WIPE_START
M204 S10000
G1 X98.975 Y140.907 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X102.439 Y139.956 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.116853
G1 F15000
G1 X102.348 Y139.748 E.00137
G1 X102.362 Y139.363 F30000
; LINE_WIDTH: 0.166338
G1 F15000
G2 X102.179 Y139.108 I-7.12 J4.93 E.00315
; LINE_WIDTH: 0.105311
G1 X101.982 Y138.879 E.00154
G1 X101.872 Y138.77 F30000
; LINE_WIDTH: 0.105687
G1 F15000
G1 X101.64 Y138.57 E.00157
; LINE_WIDTH: 0.166858
G2 X101.389 Y138.39 I-3.74 J4.941 E.00312
; WIPE_START
G1 X101.64 Y138.57 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.453 Y139.318 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0963501
G1 F15000
G2 X99.373 Y139.439 I2.401 J1.665 E.00063
; WIPE_START
G1 X99.453 Y139.318 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.516 Y140.638 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.179189
G1 F15000
G3 X99.311 Y140.306 I6.613 J-4.309 E.00433
G1 X99.526 Y140.631 F30000
; LINE_WIDTH: 0.109455
G1 F15000
G3 X99.302 Y140.316 I6.144 J-4.599 E.0021
; WIPE_START
G1 X99.526 Y140.631 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X100.401 Y141.42 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.141894
G1 F15000
G1 X100.268 Y141.331 E.00129
; LINE_WIDTH: 0.127717
G1 X100.196 Y141.281 E.0006
; LINE_WIDTH: 0.101357
G1 X100.125 Y141.231 E.00042
G1 X100.488 Y141.366 F30000
; LINE_WIDTH: 0.112956
G1 F15000
G3 X100.249 Y141.381 I-.426 J-4.862 E.00137
G1 X100.99 Y141.476 F30000
; LINE_WIDTH: 0.104938
G1 F15000
G1 X100.799 Y141.398 E.00105
; WIPE_START
G1 X100.99 Y141.476 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.997 Y142.283 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.27869
G1 F15000
G1 X99.806 Y142.142 E.00455
; LINE_WIDTH: 0.316718
G1 F13148.378
G1 X99.616 Y142 E.00528
; LINE_WIDTH: 0.354747
G1 F11544.872
G1 X99.426 Y141.859 E.00602
; LINE_WIDTH: 0.412778
G1 F9733.467
G1 X99.125 Y141.587 E.01224
G1 X86.437 Y128.899 E.54077
G1 X86.165 Y128.598 E.01225
; LINE_WIDTH: 0.354755
G1 F11544.582
G1 X86.023 Y128.408 E.00602
; LINE_WIDTH: 0.316729
G1 F13147.851
G1 X85.882 Y128.218 E.00528
; LINE_WIDTH: 0.278704
G1 F15000
G1 X85.741 Y128.027 E.00455
; WIPE_START
G1 X85.882 Y128.218 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X86.725 Y126.59 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.0964066
G1 F15000
G2 X86.645 Y126.712 I2.273 J1.579 E.00064
; WIPE_START
G1 X86.725 Y126.59 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X86.788 Y127.91 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.179236
G1 F15000
G3 X86.583 Y127.578 I6.395 J-4.18 E.00433
G1 X86.798 Y127.903 F30000
; LINE_WIDTH: 0.109441
G1 F15000
G3 X86.574 Y127.588 I6.132 J-4.591 E.0021
; WIPE_START
G1 X86.798 Y127.903 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X87.711 Y128.716 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.141929
G1 F15000
G1 X87.54 Y128.603 E.00165
; LINE_WIDTH: 0.127731
G1 X87.468 Y128.553 E.0006
; LINE_WIDTH: 0.101358
G1 X87.397 Y128.503 E.00042
G1 X88.262 Y128.748 F30000
; LINE_WIDTH: 0.105175
G1 F15000
G1 X88.071 Y128.67 E.00105
; WIPE_START
G1 X88.262 Y128.748 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X89.711 Y127.228 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.116904
G1 F15000
G1 X89.62 Y127.02 E.00137
G1 X89.634 Y126.635 F30000
; LINE_WIDTH: 0.166329
G1 F15000
G2 X89.451 Y126.38 I-6.776 J4.676 E.00315
; LINE_WIDTH: 0.105316
G1 X89.254 Y126.152 E.00153
G1 X89.144 Y126.042 F30000
; LINE_WIDTH: 0.105698
G1 F15000
G1 X88.912 Y125.842 E.00157
; LINE_WIDTH: 0.166903
G2 X88.661 Y125.662 I-3.893 J5.15 E.00312
; WIPE_START
G1 X88.912 Y125.842 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X94.498 Y129.205 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.106268
G1 F15000
G1 X94.428 Y129.108 E.00062
; LINE_WIDTH: 0.14248
G1 X94.358 Y129.01 E.00097
; LINE_WIDTH: 0.179283
G1 X94.286 Y128.91 E.00137
; LINE_WIDTH: 0.20514
G1 X94.216 Y128.808 E.00163
; WIPE_START
G1 X94.286 Y128.91 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X95.345 Y130.583 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.108655
G1 F15000
G1 X95.187 Y130.394 E.00132
; LINE_WIDTH: 0.149882
G1 X95.027 Y130.203 E.00217
; LINE_WIDTH: 0.184871
G1 X94.919 Y130.068 E.002
; LINE_WIDTH: 0.213138
G1 X94.812 Y129.933 E.00239
; WIPE_START
G1 X94.919 Y130.068 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X98.091 Y133.212 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.213141
G1 F15000
G1 X97.956 Y133.105 E.00239
; LINE_WIDTH: 0.184605
G1 X97.818 Y132.995 E.00203
; LINE_WIDTH: 0.149615
G1 X97.63 Y132.837 E.00214
; LINE_WIDTH: 0.108643
G1 X97.441 Y132.679 E.00132
; WIPE_START
G1 X97.63 Y132.837 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X99.216 Y133.808 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.204879
G1 F15000
G1 X99.111 Y133.736 E.00169
; LINE_WIDTH: 0.178646
G1 X99.014 Y133.666 E.00132
; LINE_WIDTH: 0.142457
G1 X98.916 Y133.596 E.00097
; LINE_WIDTH: 0.106268
G1 X98.819 Y133.526 E.00062
; WIPE_START
G1 X98.916 Y133.596 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X102.144 Y134.616 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.100352
G1 F15000
G3 X101.932 Y134.51 I3.987 J-8.25 E.00111
; WIPE_START
G1 X102.144 Y134.616 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X106.89 Y133.949 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.099949
G1 F15000
G1 X106.764 Y134.032 E.0007
; WIPE_START
G1 X106.89 Y133.949 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X109.865 Y126.921 Z1.4 F30000
G1 X112.495 Y120.708 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.195718
G1 F15000
G1 X112.421 Y120.6 E.00163
; LINE_WIDTH: 0.162604
G1 X112.346 Y120.489 E.00131
; LINE_WIDTH: 0.131268
G1 X112.287 Y120.408 E.00072
; LINE_WIDTH: 0.10253
G1 X112.228 Y120.326 E.00049
G1 X111.879 Y119.708 F30000
; LINE_WIDTH: 0.166872
G1 F15000
G1 X111.892 Y119.606 E.00104
; LINE_WIDTH: 0.182913
G1 X111.895 Y119.584 E.00025
; LINE_WIDTH: 0.210206
G1 X111.897 Y119.563 E.0003
; LINE_WIDTH: 0.206591
G1 X111.801 Y119.442 E.00206
; LINE_WIDTH: 0.172076
G1 X111.705 Y119.322 E.00162
; LINE_WIDTH: 0.137345
G1 X111.607 Y119.2 E.0012
; LINE_WIDTH: 0.104048
G1 X111.476 Y119.043 E.00102
; WIPE_START
G1 X111.607 Y119.2 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X108.981 Y116.548 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.104185
G1 F15000
G1 X108.823 Y116.415 E.00103
; LINE_WIDTH: 0.137554
G1 X108.702 Y116.319 E.00119
; LINE_WIDTH: 0.172068
G1 X108.582 Y116.223 E.00162
; LINE_WIDTH: 0.204391
G1 X108.461 Y116.127 E.00203
G1 X108.418 Y116.132 E.00057
; LINE_WIDTH: 0.167028
G1 X108.316 Y116.145 E.00104
; WIPE_START
G1 X108.418 Y116.132 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X106.769 Y115.396 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.154693
G1 F15000
G1 X106.462 Y115.203 E.0033
; WIPE_START
G1 X106.769 Y115.396 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X105.285 Y114.977 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.143482
G1 F15000
G1 X105.05 Y114.852 E.00217
; WIPE_START
G1 X105.285 Y114.977 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X109.377 Y108.534 Z1.4 F30000
G1 X113.876 Y101.451 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.441461
G1 F9032.951
G1 X113.837 Y101.402 E.00204
; LINE_WIDTH: 0.414385
G1 F9691.371
G1 X113.799 Y101.352 E.0019
; LINE_WIDTH: 0.387357
G1 F10451.856
G1 X113.595 Y101.168 E.00772
; LINE_WIDTH: 0.354852
G1 F11540.999
G1 X113.405 Y101.027 E.00602
; LINE_WIDTH: 0.316814
G1 F13143.805
G1 X113.214 Y100.886 E.00529
; LINE_WIDTH: 0.278776
G1 F15000
G1 X113.024 Y100.744 E.00455
; WIPE_START
G1 X113.214 Y100.886 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X112.208 Y102.487 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.101754
G1 F15000
G1 X112.151 Y102.571 E.00049
G1 X112.165 Y102.638 E.00033
; WIPE_START
G1 X112.151 Y102.571 E-.30442
G1 X112.208 Y102.487 E-.45558
; WIPE_END
G1 E-.04 F1800
G1 X112.165 Y103.69 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.184112
G1 F15000
G3 X112.016 Y103.42 I5.526 J-3.223 E.00355
G1 X112.171 Y103.686 F30000
; LINE_WIDTH: 0.104373
G1 F15000
G3 X112.008 Y103.427 I7.708 J-5.041 E.00153
; WIPE_START
G1 X112.171 Y103.686 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X113.285 Y104.698 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.141312
G1 F15000
G1 X113.022 Y104.541 E.00245
G1 X113.368 Y104.614 F30000
; LINE_WIDTH: 0.113524
G1 F15000
G1 X113.143 Y104.683 E.00135
; WIPE_START
G1 X113.368 Y104.614 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X118.725 Y110.051 Z1.4 F30000
G1 X124.599 Y116.011 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.141265
G1 F15000
G1 X124.335 Y115.855 E.00245
G1 X124.682 Y115.928 F30000
; LINE_WIDTH: 0.11372
G1 F15000
G1 X124.457 Y115.997 E.00136
; WIPE_START
G1 X124.682 Y115.928 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X123.479 Y115.005 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.184151
G1 F15000
G3 X123.329 Y114.734 I5.916 J-3.438 E.00356
G1 X123.486 Y115 F30000
; LINE_WIDTH: 0.102548
G1 F15000
G3 X123.322 Y114.741 I4.682 J-3.146 E.00149
G1 X123.522 Y113.8 F30000
; LINE_WIDTH: 0.101701
G1 F15000
G1 X123.464 Y113.885 E.00049
G1 X123.478 Y113.951 E.00033
; WIPE_START
G1 X123.464 Y113.885 E-.30398
G1 X123.522 Y113.8 E-.45602
; WIPE_END
G1 E-.04 F1800
G1 X124.892 Y112.944 Z1.4 F30000
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.249025
G1 F15000
G1 X125.002 Y112.886 E.00209
; LINE_WIDTH: 0.285618
G1 F14833.273
G1 X125.112 Y112.828 E.00246
; LINE_WIDTH: 0.316466
G1 F13160.531
G1 X125.127 Y112.817 E.00041
; LINE_WIDTH: 0.350127
G1 F11718.501
G1 X125.148 Y112.8 E.00069
; LINE_WIDTH: 0.392337
G1 F10302.888
G1 X125.169 Y112.782 E.00078
; LINE_WIDTH: 0.414163
G1 F9697.168
G1 X125.19 Y112.765 E.00083
G1 X125.117 Y112.662 E.00382
G1 X115.362 Y102.906 E.41735
G1 X115.259 Y102.833 E.00381
; LINE_WIDTH: 0.434016
G1 F9204.905
G1 X115.242 Y102.855 E.00088
; LINE_WIDTH: 0.391476
G1 F10328.345
G1 X115.224 Y102.876 E.00078
; LINE_WIDTH: 0.348935
G1 F11764.135
G1 X115.206 Y102.897 E.00069
; LINE_WIDTH: 0.315175
G1 F13222.927
G1 X115.196 Y102.912 E.00041
; LINE_WIDTH: 0.284472
G1 F14903.644
G1 X115.137 Y103.022 E.00246
; LINE_WIDTH: 0.248033
G1 F15000
G1 X115.079 Y103.133 E.00209
; WIPE_START
G1 X115.137 Y103.022 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X120.571 Y108.382 Z1.4 F30000
G1 X127.28 Y115 Z1.4
G1 Z1
G1 E.8 F1800
; LINE_WIDTH: 0.278784
G1 F15000
G1 X127.138 Y114.81 E.00455
; LINE_WIDTH: 0.316818
G1 F13143.616
G1 X126.997 Y114.619 E.00529
; LINE_WIDTH: 0.354851
G1 F11541.009
G1 X126.856 Y114.429 E.00602
; LINE_WIDTH: 0.38741
G1 F10450.257
G1 X126.671 Y114.225 E.00775
; LINE_WIDTH: 0.414396
G1 F9691.09
G1 X126.622 Y114.186 E.00189
; LINE_WIDTH: 0.450542
G1 F8831.712
G1 X126.573 Y114.147 E.00208
G1 X126.467 Y113.922 E.00826
; CHANGE_LAYER
; Z_HEIGHT: 1.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F8831.712
G1 X126.573 Y114.147 E-.60745
G1 X126.622 Y114.186 E-.15255
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 6/15
; update layer progress
M73 L6
M991 S0 P5 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z1.4 I-1.217 J-.012 P1  F30000
G1 X126.06 Y170.649 Z1.4
G1 Z1.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X125.838 Y170.627 E.00686
G3 X126.01 Y167.932 I.245 J-1.337 E.12138
G3 X126.192 Y167.935 I.078 J1.039 E.00562
G3 X126.12 Y170.649 I-.109 J1.355 E.12673
; WIPE_START
M204 S10000
G1 X125.838 Y170.627 E-.10754
G1 X125.499 Y170.522 E-.13484
M73 P87 R1
G1 X125.294 Y170.404 E-.09009
G1 X125.112 Y170.251 E-.0901
G1 X124.96 Y170.07 E-.09013
G1 X124.841 Y169.864 E-.09008
G1 X124.734 Y169.526 E-.13491
G1 X124.729 Y169.467 E-.02232
; WIPE_END
G1 E-.04 F1800
G1 X128.311 Y166.148 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X128.305 Y166.104 E.00138
G3 X129.545 Y164.397 I1.314 J-.349 E.07422
G3 X129.728 Y164.399 I.078 J1.039 E.00562
G3 X128.385 Y166.325 I-.109 J1.355 E.17545
G1 X128.334 Y166.204 E.00405
; WIPE_START
M204 S10000
G1 X128.305 Y166.104 E-.03952
G1 X128.249 Y165.754 E-.13452
G1 X128.27 Y165.518 E-.09008
G1 X128.377 Y165.179 E-.13495
G1 X128.495 Y164.974 E-.09009
G1 X128.648 Y164.792 E-.0901
G1 X128.829 Y164.64 E-.09011
G1 X129.035 Y164.521 E-.09008
G1 X129.036 Y164.521 E-.00054
; WIPE_END
G1 E-.04 F1800
G1 X123.969 Y158.813 Z1.6 F30000
G1 X118.356 Y152.491 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X118.642 Y152.388 E.01009
G3 X119.055 Y152.338 I.399 J1.581 E.01383
G3 X120 Y152.754 I-.055 J1.408 E.03508
G1 X131.296 Y164.049 E.52989
G3 X131.552 Y165.711 I-1.021 J1.009 E.0596
G1 X131.367 Y165.687 E.00622
G2 X129.457 Y167.5 I-1.75 J.069 E.26626
G1 X129.824 Y167.516 E.01221
G1 X127.836 Y169.505 E.09328
G2 X127.079 Y167.854 I-1.897 J-.129 E.0628
G2 X126.007 Y171.047 I-1.003 J1.44 E.21596
G1 X126.031 Y171.233 E.00622
G3 X124.369 Y170.976 I-.653 J-1.278 E.0596
G1 X113.074 Y159.681 E.52989
G3 X112.817 Y158.019 I1 J-1.005 E.05971
G1 X113.003 Y158.043 E.00622
G2 X114.913 Y156.23 I1.75 J-.069 E.26626
G1 X114.545 Y156.214 E.0122
G1 X116.534 Y154.226 E.09328
G2 X117.29 Y155.876 I1.897 J.129 E.0628
G2 X119.775 Y155.377 I1.004 J-1.438 E.09395
G2 X118.363 Y152.683 I-1.488 J-.937 E.12189
G1 X118.344 Y152.539 E.00484
; WIPE_START
G1 X118.642 Y152.388 E-.12697
G1 X118.881 Y152.341 E-.0925
G1 X119.055 Y152.338 E-.06607
G1 X119.364 Y152.384 E-.11887
G1 X119.593 Y152.467 E-.09252
G1 X119.804 Y152.589 E-.09264
G1 X120 Y152.754 E-.09741
G1 X120.136 Y152.89 E-.07302
; WIPE_END
G1 E-.04 F1800
G1 X116.979 Y154.774 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X116.946 Y154.44 E.0103
G3 X118.231 Y153.083 I1.359 J0 E.06333
G3 X118.414 Y153.085 I.078 J1.04 E.00563
G3 X117.003 Y154.828 I-.109 J1.355 E.18133
; WIPE_START
M204 S10000
G1 X116.946 Y154.44 E-.14884
G1 X116.956 Y154.204 E-.0898
G1 X117.017 Y153.975 E-.09012
G1 X117.181 Y153.66 E-.13494
G1 X117.334 Y153.479 E-.0901
G1 X117.515 Y153.326 E-.0901
G1 X117.721 Y153.208 E-.0901
G1 X117.785 Y153.184 E-.02601
; WIPE_END
G1 E-.04 F1800
G1 X113.42 Y158.207 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X113.41 Y157.976 E.00711
G3 X114.696 Y156.619 I1.36 J0 E.06335
G3 X114.879 Y156.621 I.078 J1.039 E.00562
G3 X113.44 Y158.259 I-.109 J1.355 E.18479
; WIPE_START
M204 S10000
G1 X113.41 Y157.976 E-.10813
G1 X113.446 Y157.624 E-.13451
G1 X113.527 Y157.401 E-.09009
G1 X113.646 Y157.196 E-.09013
G1 X113.798 Y157.014 E-.09006
G1 X113.98 Y156.862 E-.0901
G1 X114.185 Y156.743 E-.09009
G1 X114.351 Y156.683 E-.06689
; WIPE_END
G1 E-.04 F1800
G1 X118.218 Y152.128 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
G1 F9547.055
M204 S5000
G1 X118.249 Y152.117 E.00102
G3 X119.072 Y151.947 I.779 J1.686 E.02605
G3 X120.272 Y152.471 I-.072 J1.8 E.04117
G1 X131.579 Y163.778 E.49136
G3 X131.579 Y166.316 I-1.269 J1.269 E.08661
; object ids of layer 6 start: 817,839
M624 BgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer6 end: 817,839
M625
G1 X126.636 Y171.259 E.21482
G3 X124.098 Y171.259 I-1.269 J-1.287 E.08644
G1 X112.79 Y159.952 E.49136
G3 X112.791 Y157.414 I1.287 J-1.269 E.08645
G1 X117.734 Y152.471 E.21481
G3 X117.979 Y152.271 I1.294 J1.333 E.00973
G1 X118.166 Y152.159 E.00672
M204 S10000
G1 X118.153 Y152.589 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.174555
G1 F15000
G2 X117.493 Y153.054 I10.49 J15.575 E.00866
; LINE_WIDTH: 0.112348
G1 X117.321 Y153.196 E.00126
G1 X117.355 Y153.127 F30000
; LINE_WIDTH: 0.23538
G1 F15000
G1 X118.156 Y152.616 E.0149
G1 X118.159 Y152.636 F30000
; LINE_WIDTH: 0.30675
G1 F13645.146
G1 X117.417 Y153.065 E.01843
G1 X117.452 Y153.03 F30000
; LINE_WIDTH: 0.387784
G1 F10438.917
G3 X117.995 Y152.735 I5.126 J8.799 E.01736
G1 X118.192 Y152.884 E.00692
G1 X118.923 Y152.566 F30000
; LINE_WIDTH: 0.104934
G1 F15000
G1 X119.003 Y152.577 E.00041
; LINE_WIDTH: 0.143611
G3 X119.146 Y152.611 I-.575 J2.755 E.00121
G1 X119.151 Y152.612 E.00004
; LINE_WIDTH: 0.193558
G3 X119.313 Y152.67 I-.716 J2.261 E.00212
G1 X119.32 Y152.673 E.00009
; LINE_WIDTH: 0.242055
G3 X119.464 Y152.745 I-.742 J1.669 E.0026
G1 X119.544 Y152.795 E.00155
; LINE_WIDTH: 0.284594
G1 F14896.15
G3 X119.759 Y152.97 I-.723 J1.111 E.00546
G1 X120.005 Y153.237 E.00715
; LINE_WIDTH: 0.33131
G1 F12483.115
G1 X120.12 Y153.379 E.00431
; LINE_WIDTH: 0.36593
G1 F11145.178
G1 X120.179 Y153.46 E.00263
; LINE_WIDTH: 0.394232
G1 F10247.309
G1 X120.23 Y153.53 E.00247
; LINE_WIDTH: 0.424369
G1 F9437.709
G1 X120.385 Y153.76 E.00864
; WIPE_START
G1 X120.23 Y153.53 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X117.052 Y153.466 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; LINE_WIDTH: 0.112748
G1 F15000
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.15747
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.1905
G1 X116.716 Y153.915 E.00229
G1 X116.749 Y154.125 F30000
; LINE_WIDTH: 0.105814
G1 F15000
G1 X116.757 Y154.03 E.00049
; LINE_WIDTH: 0.139063
G1 X116.776 Y153.89 E.00111
; LINE_WIDTH: 0.164617
G1 X116.809 Y153.673 E.00218
; WIPE_START
G1 X116.776 Y153.89 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X117.916 Y156.316 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40268
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X127.494 Y165.894 E.7028
G3 X127.541 Y165.3 I2.466 J-.103 E.03095
G1 X118.749 Y156.509 E.64511
G2 X119.226 Y156.346 I-.406 J-1.966 E.02623
G1 X127.707 Y164.827 E.62234
G3 X127.952 Y164.432 I2.008 J.972 E.02417
G1 X119.615 Y156.095 E.61178
G2 X119.941 Y155.78 I-1.193 J-1.557 E.02354
G1 X128.27 Y164.109 E.61122
G1 X128.385 Y164.028 E.00732
G3 X128.659 Y163.858 I.784 J.955 E.01677
G1 X120.188 Y155.387 E.62158
G2 X120.361 Y154.92 I-1.702 J-.896 E.02592
G1 X129.129 Y163.688 E.64341
G3 X129.721 Y163.64 I.61 J3.84 E.03085
G1 X120.41 Y154.328 E.68332
G1 X120.398 Y154.196 E.00687
G1 X120.71 Y153.988 E.01944
G1 X130.208 Y163.486 E.69698
G1 X130.289 Y163.665 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.425228
; LAYER_HEIGHT: 0.2
G1 F9416.504
G1 X130.507 Y163.81 E.00815
; LINE_WIDTH: 0.396767
G1 F10173.908
G1 X130.59 Y163.87 E.00296
; LINE_WIDTH: 0.367984
G1 F11074.744
G1 X130.66 Y163.922 E.00229
; LINE_WIDTH: 0.334097
G1 F12363.616
G1 X130.804 Y164.037 E.0044
; LINE_WIDTH: 0.285101
G1 F14864.93
G3 X131.193 Y164.419 I-1.981 J2.405 E.01076
G1 X131.254 Y164.505 E.0021
; LINE_WIDTH: 0.242079
G1 F15000
G3 X131.376 Y164.729 I-1.08 J.734 E.00415
; LINE_WIDTH: 0.193576
G3 X131.437 Y164.899 I-2.859 J1.127 E.00221
; LINE_WIDTH: 0.143622
G3 X131.473 Y165.047 I-1.846 J.517 E.00125
; LINE_WIDTH: 0.104925
G1 X131.484 Y165.127 E.00041
G1 X131.166 Y165.858 F30000
; LINE_WIDTH: 0.387792
G1 F10438.672
G1 X131.315 Y166.055 E.00692
G3 X131.017 Y166.6 I-8.443 J-4.248 E.01747
G1 X130.985 Y166.633 F30000
; LINE_WIDTH: 0.306774
G1 F13643.905
G1 X131.413 Y165.891 E.01842
G1 X131.433 Y165.893 F30000
; LINE_WIDTH: 0.235387
G1 F15000
G1 X131.16 Y166.323 E.00799
; LINE_WIDTH: 0.220029
G1 X131.122 Y166.38 E.001
; LINE_WIDTH: 0.19188
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155945
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112366
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.11276
G1 F15000
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157465
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.190483
G1 X130.135 Y167.334 E.00229
G1 X129.925 Y167.301 F30000
; LINE_WIDTH: 0.106101
G1 F15000
G1 X130.023 Y167.292 E.00051
; LINE_WIDTH: 0.154949
G2 X130.377 Y167.241 I-1.04 J-8.435 E.00326
; WIPE_START
G1 X130.023 Y167.292 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X129.032 Y168.072 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Bridge
; LINE_WIDTH: 0.40268
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X116.121 Y155.161 E.94742
G1 X115.801 Y155.481 E.02349
G1 X128.569 Y168.249 E.93692
G1 X128.249 Y168.569 E.02349
G1 X115.338 Y155.658 E.94742
; WIPE_START
M73 P88 R1
G1 X116.752 Y157.072 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X113.992 Y156.489 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.164644
; LAYER_HEIGHT: 0.2
G1 F15000
G1 X114.21 Y156.456 E.00218
; LINE_WIDTH: 0.139644
G1 X114.346 Y156.438 E.00109
; LINE_WIDTH: 0.10613
G1 X114.444 Y156.429 E.00051
G1 X114.234 Y156.397 F30000
; LINE_WIDTH: 0.190127
G1 F15000
G1 X114.071 Y156.506 E.00235
; LINE_WIDTH: 0.15595
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112368
G1 X113.786 Y156.732 E.00126
G1 X113.203 Y157.872 F30000
; LINE_WIDTH: 0.387776
G1 F10439.142
G1 X113.055 Y157.675 E.00692
G3 X113.36 Y157.122 I7.402 J3.723 E.01778
G1 X113.385 Y157.097 F30000
; LINE_WIDTH: 0.30677
G1 F13644.151
G1 X112.956 Y157.839 E.01843
G1 X112.936 Y157.837 F30000
; LINE_WIDTH: 0.235428
G1 F15000
G1 X113.446 Y157.036 E.01489
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.112788
G1 F15000
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.174715
G2 X112.908 Y157.833 I14.546 J10.753 E.00863
G1 X112.885 Y158.603 F30000
; LINE_WIDTH: 0.104944
G1 F15000
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.143644
G2 X112.931 Y158.826 I1.657 J-.316 E.00121
G1 X112.932 Y158.831 E.00004
; LINE_WIDTH: 0.193578
G2 X112.99 Y158.994 I2.257 J-.715 E.00212
G1 X112.993 Y159.001 E.00009
; LINE_WIDTH: 0.242083
G2 X113.065 Y159.144 I1.67 J-.743 E.0026
G1 X113.115 Y159.225 E.00154
; LINE_WIDTH: 0.284608
G1 F14895.263
G2 X113.289 Y159.439 I1.11 J-.722 E.00545
G1 X113.556 Y159.685 E.00714
; LINE_WIDTH: 0.331314
G1 F12482.957
G1 X113.699 Y159.8 E.00432
; LINE_WIDTH: 0.365926
G1 F11145.302
G1 X113.78 Y159.86 E.00263
; LINE_WIDTH: 0.394215
G1 F10247.818
G1 X113.849 Y159.911 E.00247
; LINE_WIDTH: 0.410157
G1 F9802.948
G1 X114.077 Y160.071 E.00834
G1 X114.161 Y160.243 F30000
; FEATURE: Bridge
; LINE_WIDTH: 0.40268
; LAYER_HEIGHT: 0.4
G1 F3000
G1 X123.661 Y169.744 E.69716
G1 X123.962 Y169.533 E.01903
G1 X123.956 Y169.398 E.00703
G1 X114.648 Y160.09 E.68302
G2 X115.238 Y160.04 I.144 J-1.811 E.03088
G1 X124.008 Y168.81 E.64354
G1 X124.023 Y168.741 E.00368
G3 X124.179 Y168.34 I5.538 J1.922 E.02228
G1 X115.709 Y159.871 E.6215
G2 X116.096 Y159.617 I-.527 J-1.223 E.02411
G1 X124.429 Y167.95 E.61148
G3 X124.752 Y167.633 I2.697 J2.421 E.02351
G1 X116.417 Y159.298 E.6116
G2 X116.662 Y158.903 I-.997 J-.892 E.02425
G1 X125.147 Y167.388 E.6226
G3 X125.62 Y167.221 I.71 J1.26 E.02618
G1 X116.829 Y158.43 E.64511
G2 X116.871 Y157.832 I-2.391 J-.47 E.03117
G1 X126.447 Y167.408 E.70267
; WIPE_START
G1 X125.033 Y165.993 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X127.561 Y170.057 Z1.6 F30000
G1 Z1.2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.164636
; LAYER_HEIGHT: 0.2
G1 F15000
G1 X127.594 Y169.84 E.00218
; LINE_WIDTH: 0.139062
G1 X127.612 Y169.7 E.00111
; LINE_WIDTH: 0.105812
G1 X127.621 Y169.606 E.00049
G1 X127.653 Y169.815 F30000
; LINE_WIDTH: 0.190135
G1 F15000
G1 X127.544 Y169.978 E.00235
; LINE_WIDTH: 0.155927
G1 X127.46 Y170.093 E.0013
; LINE_WIDTH: 0.112342
G1 X127.318 Y170.264 E.00126
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.112756
G1 F15000
G1 X126.873 Y170.679 E.00129
; LINE_WIDTH: 0.157474
G1 X126.758 Y170.763 E.00134
; LINE_WIDTH: 0.193037
G1 X126.7 Y170.802 E.00085
; LINE_WIDTH: 0.233564
G3 X126.213 Y171.114 I-7.566 J-11.262 E.00899
G1 X126.211 Y171.093 F30000
; LINE_WIDTH: 0.306759
G1 F13644.696
G1 X126.951 Y170.667 E.01838
G1 X126.918 Y170.7 F30000
; LINE_WIDTH: 0.387793
G1 F10438.632
G3 X126.374 Y170.995 I-5 J-8.562 E.01737
G1 X126.178 Y170.847 E.00692
G1 X125.446 Y171.165 F30000
; LINE_WIDTH: 0.10494
G1 F15000
G1 X125.367 Y171.153 E.00041
; LINE_WIDTH: 0.143617
G3 X125.219 Y171.118 I.368 J-1.874 E.00125
; LINE_WIDTH: 0.193557
G3 X125.049 Y171.057 I.949 J-2.898 E.00221
; LINE_WIDTH: 0.242063
G3 X124.825 Y170.935 I.512 J-1.206 E.00415
; LINE_WIDTH: 0.285113
G1 F14864.183
G1 X124.739 Y170.873 E.0021
G3 X124.357 Y170.485 I2.023 J-2.369 E.01076
; LINE_WIDTH: 0.33408
G1 F12364.335
G1 X124.241 Y170.34 E.00439
; LINE_WIDTH: 0.36794
G1 F11076.239
G1 X124.19 Y170.27 E.00229
; LINE_WIDTH: 0.406408
G1 F9904.045
G3 X123.979 Y169.972 I6.749 J-5.002 E.01082
; OBJECT_ID: 817
; WIPE_START
G1 X124.19 Y170.27 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X120.27 Y163.722 Z1.6 F30000
G1 X103.411 Y135.562 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G1 X103.415 Y135.539 E.00076
G3 X103.722 Y135.367 I.267 J.117 E.01254
G1 X103.805 Y135.391 E.00288
G1 X103.898 Y135.46 E.00383
G1 X103.946 Y135.532 E.00288
G1 X103.973 Y135.645 E.00383
G1 X103.964 Y135.731 E.00288
G1 X103.912 Y135.835 E.00383
G1 X103.849 Y135.895 E.00289
G1 X103.743 Y135.941 E.00383
G3 X103.391 Y135.674 I-.061 J-.285 E.01663
G1 X103.4 Y135.621 E.0018
M204 S250
G1 X103.029 Y135.495 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X103.056 Y135.383 E.00354
G3 X103.708 Y134.972 I.626 J.271 E.02515
G1 X103.776 Y134.978 E.00209
G3 X103.001 Y135.628 I-.094 J.676 E.09665
G1 X103.016 Y135.553 E.00234
; WIPE_START
M204 S10000
G1 X103.056 Y135.383 E-.06662
G1 X103.122 Y135.263 E-.05175
G1 X103.21 Y135.16 E-.05175
G1 X103.318 Y135.076 E-.05177
G1 X103.44 Y135.016 E-.0518
G1 X103.572 Y134.98 E-.05182
G1 X103.708 Y134.972 E-.05179
G1 X103.776 Y134.978 E-.02588
G1 X103.908 Y135.01 E-.05172
G1 X104.031 Y135.067 E-.05183
G1 X104.141 Y135.148 E-.05177
G1 X104.233 Y135.249 E-.05182
G1 X104.302 Y135.367 E-.05173
G1 X104.347 Y135.495 E-.05181
G1 X104.358 Y135.616 E-.04614
; WIPE_END
G1 E-.04 F1800
G1 X98.759 Y130.429 Z1.6 F30000
G1 X92.095 Y124.254 Z1.6
G1 Z1.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F8843.478
G3 X92.408 Y124.053 I.277 J.088 E.01339
G1 X92.517 Y124.091 E.00383
G1 X92.585 Y124.146 E.00289
G1 X92.633 Y124.219 E.00288
G1 X92.66 Y124.331 E.00383
G1 X92.65 Y124.418 E.00289
G1 X92.599 Y124.521 E.00383
G1 X92.511 Y124.596 E.00384
G1 X92.43 Y124.627 E.00288
G3 X92.083 Y124.313 I-.057 J-.285 E.01803
M204 S250
G1 X91.73 Y124.117 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F9547.055
M204 S5000
G1 X91.742 Y124.069 E.00151
G3 X92.394 Y123.658 I.626 J.271 E.02516
G1 X92.462 Y123.664 E.00209
G3 X91.686 Y124.312 I-.094 J.676 E.09683
G1 X91.717 Y124.175 E.0043
; CHANGE_LAYER
; Z_HEIGHT: 1.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.742 Y124.069 E-.04149
G1 X91.808 Y123.95 E-.05175
G1 X91.897 Y123.846 E-.0518
G1 X92.004 Y123.763 E-.05179
G1 X92.126 Y123.702 E-.05178
G1 X92.258 Y123.667 E-.05179
G1 X92.394 Y123.658 E-.0518
G1 X92.462 Y123.664 E-.02588
G1 X92.594 Y123.696 E-.0517
G1 X92.718 Y123.754 E-.05179
G1 X92.827 Y123.835 E-.0518
G1 X92.919 Y123.936 E-.05185
G1 X92.988 Y124.053 E-.05173
G1 X93.033 Y124.181 E-.0518
G1 X93.05 Y124.368 E-.07124
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 7/15
; update layer progress
M73 L7
M991 S0 P6 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z1.6 I-.991 J.707 P1  F30000
G1 X126.069 Y170.649 Z1.6
G1 Z1.4
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X125.839 Y170.623 E.00713
G3 X125.993 Y167.933 I.243 J-1.335 E.12081
G3 X126.192 Y167.935 I.09 J1.138 E.00614
G3 X126.127 Y170.644 I-.111 J1.353 E.1262
; WIPE_START
G1 F9547.055
M204 S10000
G1 X125.839 Y170.623 E-.10987
G1 X125.499 Y170.522 E-.13465
G1 X125.294 Y170.404 E-.09015
G1 X125.11 Y170.25 E-.09096
G1 X124.896 Y169.97 E-.13401
G1 X124.796 Y169.755 E-.09014
G1 X124.734 Y169.526 E-.09009
G1 X124.73 Y169.473 E-.02014
; WIPE_END
G1 E-.04 F1800
G1 X128.321 Y166.181 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X128.278 Y165.989 E.00606
G3 X129.528 Y164.397 I1.339 J-.235 E.07014
G3 X129.728 Y164.399 I.091 J1.14 E.00614
G3 X128.346 Y166.236 I-.111 J1.355 E.17832
; WIPE_START
G1 F9547.055
M204 S10000
G1 X128.278 Y165.989 E-.09735
G1 X128.249 Y165.754 E-.08985
G1 X128.27 Y165.518 E-.09008
G1 X128.377 Y165.179 E-.13495
G1 X128.495 Y164.974 E-.09009
G1 X128.649 Y164.791 E-.091
G1 X128.829 Y164.64 E-.08922
G1 X129.006 Y164.538 E-.07746
; WIPE_END
G1 E-.04 F1800
G1 X123.958 Y158.813 Z1.8 F30000
G1 X118.377 Y152.483 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4605
G1 X118.642 Y152.388 E.00935
G3 X119.037 Y152.337 I.405 J1.599 E.01325
G3 X120 Y152.754 I-.038 J1.41 E.03566
G1 X131.296 Y164.049 E.52989
G3 X131.552 Y165.711 I-1 J1.005 E.05971
G1 X131.367 Y165.687 E.00622
G2 X129.415 Y167.495 I-1.749 J.069 E.2646
G1 X129.819 Y167.521 E.01343
G1 X127.836 Y169.505 E.09303
G2 X127.079 Y167.854 I-1.897 J-.129 E.0628
G2 X126.007 Y171.047 I-.999 J1.441 E.21557
G1 X126.031 Y171.233 E.00622
G3 X124.369 Y170.976 I-.653 J-1.278 E.0596
G1 X113.074 Y159.681 E.52989
G3 X112.817 Y158.019 I1 J-1.005 E.05971
G1 X113.003 Y158.043 E.00622
G2 X114.913 Y156.23 I1.75 J-.069 E.26626
G1 X114.545 Y156.214 E.01221
G1 X116.534 Y154.226 E.09328
G2 X117.29 Y155.876 I1.897 J.129 E.06279
G2 X118.363 Y152.683 I.999 J-1.441 E.21557
G1 X118.341 Y152.516 E.00558
; WIPE_START
G1 F8843.478
M73 P89 R1
G1 X118.642 Y152.388 E-.12445
G1 X118.881 Y152.341 E-.09244
G1 X119.037 Y152.337 E-.05946
G1 X119.364 Y152.384 E-.1255
G1 X119.593 Y152.467 E-.09254
G1 X119.804 Y152.589 E-.09261
G1 X120 Y152.754 E-.09748
G1 X120.141 Y152.895 E-.07551
; WIPE_END
G1 E-.04 F1800
G1 X116.976 Y154.746 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4605
M204 S5000
G1 X116.946 Y154.44 E.00944
G3 X118.215 Y153.084 I1.357 J-.002 E.06285
G3 X118.414 Y153.085 I.09 J1.138 E.00614
G3 X116.996 Y154.803 I-.111 J1.353 E.18178
; WIPE_START
G1 F9547.055
M204 S10000
G1 X116.946 Y154.44 E-.13897
G1 X116.956 Y154.204 E-.08981
G1 X117.063 Y153.866 E-.13494
G1 X117.181 Y153.66 E-.09013
G1 X117.335 Y153.477 E-.09097
G1 X117.516 Y153.326 E-.08922
G1 X117.721 Y153.208 E-.09009
G1 X117.81 Y153.175 E-.03586
; WIPE_END
G1 E-.04 F1800
G1 X113.424 Y158.223 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X113.431 Y158.21 E.00046
G3 X114.679 Y156.619 I1.337 J-.237 E.07009
G3 X114.879 Y156.621 I.09 J1.137 E.00614
G3 X113.492 Y158.437 I-.111 J1.353 E.17858
G1 X113.442 Y158.281 E.00506
; WIPE_START
G1 F9547.055
M204 S10000
G1 X113.431 Y158.21 E-.02701
G1 X113.4 Y157.976 E-.08981
G1 X113.446 Y157.624 E-.13495
G1 X113.528 Y157.399 E-.09094
G1 X113.646 Y157.196 E-.08926
G1 X113.798 Y157.014 E-.09009
G1 X113.98 Y156.862 E-.09009
G1 X114.185 Y156.743 E-.09012
G1 X114.328 Y156.691 E-.05773
; WIPE_END
G1 E-.04 F1800
G1 X118.238 Y152.116 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X118.249 Y152.117 E.00033
G3 X119.055 Y151.946 I.78 J1.689 E.02551
G3 X120.272 Y152.471 I-.055 J1.802 E.04171
G1 X131.579 Y163.778 E.49136
G3 X131.579 Y166.316 I-1.287 J1.269 E.08644
; object ids of layer 7 start: 817,839
M624 BgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer7 end: 817,839
M625
G1 X126.636 Y171.259 E.21482
G3 X124.098 Y171.259 I-1.269 J-1.287 E.08644
G1 X112.79 Y159.952 E.49137
G3 X112.79 Y157.414 I1.287 J-1.269 E.08644
G1 X117.734 Y152.471 E.21482
G3 X117.979 Y152.271 I1.295 J1.335 E.00972
G1 X118.187 Y152.147 E.00745
M204 S10000
G1 X118.156 Y152.617 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.235346
G1 F4605
G1 X117.727 Y152.89 E.00798
; LINE_WIDTH: 0.220007
G1 X117.669 Y152.928 E.001
; LINE_WIDTH: 0.191877
G1 X117.607 Y152.97 E.00091
; LINE_WIDTH: 0.155926
G1 X117.493 Y153.054 E.0013
; LINE_WIDTH: 0.112356
G1 X117.321 Y153.196 E.00126
G1 X117.052 Y153.466 F30000
; LINE_WIDTH: 0.112754
G1 F4605
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.157464
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.190493
G1 X116.716 Y153.915 E.00229
G1 X116.749 Y154.125 F30000
; LINE_WIDTH: 0.106129
G1 F4605
G1 X116.758 Y154.027 E.00051
; LINE_WIDTH: 0.154992
G3 X116.809 Y153.673 I7.737 J.948 E.00327
G1 X118.191 Y152.882 F30000
; LINE_WIDTH: 0.387015
G1 F4605
G1 X117.995 Y152.735 E.00687
G1 X117.474 Y153.008 E.01649
G1 X117.418 Y153.064 F30000
; LINE_WIDTH: 0.306767
G1 F4605
G1 X118.159 Y152.636 E.0184
G1 X118.923 Y152.565 F30000
; LINE_WIDTH: 0.100322
G1 F4605
G1 X118.974 Y152.573 E.00024
; LINE_WIDTH: 0.129697
G3 X119.102 Y152.599 I-.327 J1.902 E.00092
; LINE_WIDTH: 0.167335
G1 X119.198 Y152.627 E.00101
; LINE_WIDTH: 0.208155
G3 X119.313 Y152.67 I-.434 J1.336 E.00166
G1 X119.379 Y152.701 E.00097
; LINE_WIDTH: 0.254831
G3 X119.622 Y152.85 I-.596 J1.246 E.00493
; LINE_WIDTH: 0.288533
G3 X119.759 Y152.97 I-1.823 J2.226 E.00365
G1 X120.02 Y153.255 E.00774
; LINE_WIDTH: 0.340659
G1 X120.148 Y153.418 E.00502
; LINE_WIDTH: 0.386326
G1 X120.23 Y153.53 E.00388
; LINE_WIDTH: 0.424394
G1 X120.385 Y153.76 E.00863
; WIPE_START
G1 F9437.092
G1 X120.23 Y153.53 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X113.993 Y156.489 Z1.8 F30000
G1 Z1.4
G1 E.8 F1800
; LINE_WIDTH: 0.164623
G1 F4605
G1 X114.21 Y156.456 E.00217
; LINE_WIDTH: 0.139634
G1 X114.346 Y156.438 E.00109
; LINE_WIDTH: 0.106119
G1 X114.444 Y156.429 E.00051
G1 X114.234 Y156.397 F30000
; LINE_WIDTH: 0.19014
G1 F4605
G1 X114.071 Y156.506 E.00235
; LINE_WIDTH: 0.155944
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112355
G1 X113.786 Y156.732 E.00126
G1 X113.203 Y157.872 F30000
; LINE_WIDTH: 0.38779
G1 F4605
G1 X113.055 Y157.675 E.00692
G3 X113.352 Y157.13 I8.643 J4.357 E.01747
G1 X113.384 Y157.098 F30000
; LINE_WIDTH: 0.30678
G1 F4605
G1 X112.956 Y157.839 E.01839
G1 X112.936 Y157.837 F30000
; LINE_WIDTH: 0.235423
G1 F4605
G1 X113.445 Y157.036 E.01488
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.108728
G1 F4605
G1 X113.397 Y157.144 E.001
; LINE_WIDTH: 0.150879
G1 X113.293 Y157.282 E.00152
; LINE_WIDTH: 0.176467
G1 X112.904 Y157.832 E.00733
G1 X112.885 Y158.603 F30000
; LINE_WIDTH: 0.104949
G1 F4605
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.143624
G2 X112.931 Y158.826 I1.649 J-.314 E.00121
G1 X112.932 Y158.831 E.00004
; LINE_WIDTH: 0.193578
G2 X112.99 Y158.994 I2.259 J-.715 E.00212
G1 X112.993 Y159.001 E.00009
; LINE_WIDTH: 0.242076
G2 X113.065 Y159.144 I1.671 J-.744 E.0026
G1 X113.115 Y159.225 E.00154
; LINE_WIDTH: 0.284971
G2 X113.281 Y159.431 I1.359 J-.923 E.00523
G1 X113.556 Y159.685 E.00738
; LINE_WIDTH: 0.331307
G1 X113.699 Y159.8 E.00431
; LINE_WIDTH: 0.365937
G1 X113.78 Y159.86 E.00263
; LINE_WIDTH: 0.394274
G1 X113.849 Y159.911 E.00247
; LINE_WIDTH: 0.424395
G1 X114.08 Y160.065 E.00863
G1 X114.139 Y160.272 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42317
G1 F4605
G1 X123.655 Y169.789 E.41702
G1 X123.978 Y169.573 E.01201
G1 X114.476 Y160.072 E.41635
G1 X114.496 Y160.043 E.00107
G2 X114.942 Y160.055 I.268 J-1.687 E.01388
G1 X114.989 Y160.047 E.00148
G1 X124.002 Y169.06 E.39494
G3 X124.104 Y168.624 I1.772 J.183 E.01391
G1 X115.426 Y159.946 E.38025
G2 X115.796 Y159.779 I-.29 J-1.134 E.01265
G1 X124.271 Y168.253 E.37137
G3 X124.489 Y167.933 I1.875 J1.039 E.01201
G1 X116.112 Y159.556 E.36708
G2 X116.38 Y159.287 I-1.078 J-1.345 E.01181
G1 X124.763 Y167.67 E.36732
G3 X125.087 Y167.456 I.767 J.811 E.01209
G1 X116.594 Y158.963 E.37215
G2 X116.75 Y158.582 I-1.003 J-.634 E.01284
G1 X125.468 Y167.299 E.38201
G3 X125.922 Y167.215 I.462 J1.229 E.01437
G1 X116.839 Y158.133 E.39799
G2 X116.816 Y157.614 I-1.982 J-.169 E.01616
G1 X116.8 Y157.556 E.00185
G1 X126.492 Y167.247 E.42469
G3 X128.094 Y168.775 I-.42 J2.045 E.0723
G1 X128.326 Y168.544 E.01013
G1 X115.506 Y155.724 E.56175
G1 X115.775 Y155.455 E.01178
G1 X128.594 Y168.275 E.56175
G1 X128.863 Y168.006 E.01178
G1 X116.044 Y155.186 E.56175
G1 X116.275 Y154.955 E.01013
G2 X117.878 Y156.483 I2.047 J-.544 E.07218
G1 X127.573 Y166.177 E.42483
G3 X127.53 Y165.597 I1.626 J-.411 E.01812
G1 X118.447 Y156.514 E.39801
G2 X118.901 Y156.431 I-.01 J-1.33 E.01438
G1 X127.619 Y165.148 E.38201
G3 X127.775 Y164.767 I1.16 J.253 E.01284
G1 X119.283 Y156.274 E.37215
G2 X119.603 Y156.057 I-.715 J-1.402 E.01203
G1 X127.989 Y164.443 E.36746
G1 X128.257 Y164.173 E.01178
G1 X119.88 Y155.796 E.36707
G2 X120.103 Y155.484 I-1.076 J-1.004 E.01192
G1 X128.568 Y163.946 E.37088
G3 X128.943 Y163.784 I.805 J1.343 E.01271
G1 X120.269 Y155.109 E.38011
G2 X120.368 Y154.67 I-1.619 J-.594 E.01398
G1 X129.383 Y163.686 E.39507
G3 X129.872 Y163.69 I.233 J1.41 E.01521
M73 P90 R1
G1 X129.893 Y163.658 E.00119
G1 X120.392 Y154.157 E.41635
G1 X120.714 Y153.941 E.01201
G1 X130.231 Y163.458 E.41702
G1 X130.289 Y163.665 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.425239
G1 F4605
G1 X130.507 Y163.81 E.00815
; LINE_WIDTH: 0.396751
G1 X130.59 Y163.871 E.00296
; LINE_WIDTH: 0.367948
G1 X130.66 Y163.922 E.00229
; LINE_WIDTH: 0.334078
G1 X130.804 Y164.037 E.00439
; LINE_WIDTH: 0.285105
G3 X131.193 Y164.419 I-1.981 J2.405 E.01077
G1 X131.254 Y164.506 E.0021
; LINE_WIDTH: 0.242074
G3 X131.376 Y164.73 I-1.078 J.732 E.00414
; LINE_WIDTH: 0.193575
G3 X131.437 Y164.899 I-2.851 J1.123 E.00221
; LINE_WIDTH: 0.143618
G3 X131.473 Y165.047 I-1.852 J.519 E.00125
; LINE_WIDTH: 0.104947
G1 X131.484 Y165.127 E.00041
G1 X131.164 Y165.858 F30000
; LINE_WIDTH: 0.387136
G1 F4605
G1 X131.315 Y166.055 E.00695
G3 X131.02 Y166.598 I-6.372 J-3.109 E.01734
G1 X130.976 Y166.641 F30000
; LINE_WIDTH: 0.286364
G1 F4605
G1 X131.415 Y165.891 E.01724
G1 X131.433 Y165.894 F30000
; LINE_WIDTH: 0.235357
G1 F4605
G1 X131.16 Y166.323 E.00798
; LINE_WIDTH: 0.220004
G1 X131.122 Y166.38 E.001
; LINE_WIDTH: 0.191891
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155959
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112364
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112744
G1 F4605
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157445
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.194078
G1 X130.118 Y167.345 E.00259
G1 X129.897 Y167.307 F30000
; LINE_WIDTH: 0.11079
G1 F4605
G1 X130.021 Y167.297 E.00069
; LINE_WIDTH: 0.137947
G1 X130.093 Y167.289 E.00056
; LINE_WIDTH: 0.164136
G1 X130.162 Y167.281 E.00068
; LINE_WIDTH: 0.178162
G1 X130.367 Y167.251 E.00228
G1 X127.56 Y170.057 F30000
; LINE_WIDTH: 0.154997
G1 F4605
G2 X127.612 Y169.704 I-7.767 J-1.312 E.00327
; LINE_WIDTH: 0.106139
G1 X127.621 Y169.606 E.00051
G1 X127.653 Y169.815 F30000
; LINE_WIDTH: 0.190129
G1 F4605
G1 X127.544 Y169.978 E.00235
; LINE_WIDTH: 0.15592
G1 X127.46 Y170.093 E.0013
; LINE_WIDTH: 0.112345
G1 X127.318 Y170.264 E.00126
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.101099
G1 F4605
G1 X126.979 Y170.594 E.00044
; LINE_WIDTH: 0.12668
G1 X126.841 Y170.702 E.0012
; LINE_WIDTH: 0.163584
G1 X126.758 Y170.763 E.00102
; LINE_WIDTH: 0.193038
G1 X126.7 Y170.802 E.00085
; LINE_WIDTH: 0.233524
G3 X126.213 Y171.114 I-7.323 J-10.897 E.00898
G1 X126.211 Y171.094 F30000
; LINE_WIDTH: 0.306778
G1 F4605
G1 X126.953 Y170.665 E.01843
G1 X126.924 Y170.693 F30000
; LINE_WIDTH: 0.387819
G1 F4605
G3 X126.374 Y170.995 I-4.341 J-7.26 E.01764
G1 X126.178 Y170.846 E.00692
G1 X125.446 Y171.165 F30000
; LINE_WIDTH: 0.104943
G1 F4605
G1 X125.367 Y171.153 E.00041
; LINE_WIDTH: 0.143623
G3 X125.218 Y171.118 I.37 J-1.882 E.00125
; LINE_WIDTH: 0.193557
G3 X125.049 Y171.057 I.948 J-2.896 E.00221
; LINE_WIDTH: 0.242067
G3 X124.825 Y170.935 I.512 J-1.206 E.00414
; LINE_WIDTH: 0.285468
G1 X124.739 Y170.873 E.0021
G3 X124.357 Y170.485 I2.216 J-2.559 E.01078
; LINE_WIDTH: 0.334058
G1 X124.241 Y170.34 E.00439
; LINE_WIDTH: 0.367913
G1 X124.19 Y170.27 E.00229
; LINE_WIDTH: 0.396743
G1 X124.13 Y170.187 E.00296
; LINE_WIDTH: 0.425238
G1 X123.984 Y169.97 E.00815
; OBJECT_ID: 817
; WIPE_START
G1 F9416.265
G1 X124.13 Y170.187 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X120.204 Y163.642 Z1.8 F30000
G1 X103.402 Y135.624 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4605
G1 X103.436 Y135.518 E.00371
G1 X103.509 Y135.433 E.0037
G1 X103.609 Y135.384 E.00371
G1 X103.706 Y135.375 E.00323
G1 X103.801 Y135.4 E.00325
G1 X103.891 Y135.467 E.0037
G1 X103.948 Y135.563 E.0037
G1 X103.963 Y135.673 E.00371
G1 X103.934 Y135.781 E.00371
G1 X103.866 Y135.869 E.0037
G1 X103.768 Y135.924 E.0037
G1 X103.657 Y135.936 E.00371
G1 X103.55 Y135.905 E.0037
G1 X103.464 Y135.834 E.0037
G1 X103.412 Y135.735 E.00371
G1 X103.407 Y135.684 E.00171
M204 S250
G1 X103.021 Y135.526 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4605
M204 S5000
G1 X103.019 Y135.513 E.00042
G3 X103.64 Y134.983 I.658 J.141 E.02696
G3 X103.74 Y134.985 I.04 J.502 E.00309
G3 X103.004 Y135.647 I-.064 J.669 E.09563
G1 X103.013 Y135.586 E.00191
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.019 Y135.513 E-.02771
G1 X103.064 Y135.386 E-.05114
G1 X103.13 Y135.269 E-.05104
G1 X103.217 Y135.167 E-.05101
G1 X103.323 Y135.085 E-.05104
G1 X103.443 Y135.025 E-.05101
G1 X103.64 Y134.983 E-.07638
G1 X103.74 Y134.985 E-.0382
G1 X103.967 Y135.045 E-.08905
G1 X104.082 Y135.113 E-.051
G1 X104.182 Y135.203 E-.05101
G1 X104.262 Y135.311 E-.05103
G1 X104.318 Y135.433 E-.05103
G1 X104.35 Y135.563 E-.05102
G1 X104.352 Y135.612 E-.01833
; WIPE_END
G1 E-.04 F1800
G1 X98.754 Y130.423 Z1.8 F30000
G1 X92.105 Y124.259 Z1.8
G1 Z1.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4605
G1 X92.123 Y124.204 E.00192
G1 X92.195 Y124.119 E.00371
G1 X92.295 Y124.07 E.0037
G1 X92.393 Y124.062 E.00323
G1 X92.488 Y124.087 E.00326
G1 X92.577 Y124.153 E.0037
G1 X92.634 Y124.249 E.0037
G1 X92.649 Y124.36 E.00371
G1 X92.621 Y124.467 E.0037
G1 X92.552 Y124.556 E.0037
G1 X92.455 Y124.61 E.00371
G1 X92.344 Y124.623 E.00371
G1 X92.237 Y124.591 E.0037
G1 X92.15 Y124.52 E.0037
G1 X92.098 Y124.422 E.00371
G1 X92.089 Y124.317 E.0035
M204 S250
G1 X91.726 Y124.137 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4605
M204 S5000
G1 X91.723 Y124.134 E.00014
G3 X92.326 Y123.669 I.64 J.207 E.02489
G3 X92.427 Y123.671 I.04 J.502 E.00309
G3 X91.694 Y124.266 I-.064 J.669 E.0977
G1 X91.712 Y124.195 E.00223
; CHANGE_LAYER
; Z_HEIGHT: 1.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.723 Y124.134 E-.02372
G1 X91.78 Y124.012 E-.0512
G1 X91.857 Y123.902 E-.05104
G1 X91.954 Y123.81 E-.05103
G1 X92.068 Y123.738 E-.05106
G1 X92.194 Y123.691 E-.05099
G1 X92.326 Y123.669 E-.051
G1 X92.427 Y123.671 E-.03821
G1 X92.653 Y123.731 E-.08906
G1 X92.769 Y123.799 E-.05098
G1 X92.868 Y123.89 E-.05105
G1 X92.948 Y123.998 E-.05101
G1 X93.005 Y124.119 E-.051
G1 X93.036 Y124.25 E-.05103
G1 X93.041 Y124.375 E-.04762
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 8/15
; update layer progress
M73 L8
M991 S0 P7 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z1.8 I-.99 J.707 P1  F30000
G1 X126.079 Y170.649 Z1.8
G1 Z1.6
G1 E.8 F1800
G1 F4738
M204 S5000
G1 X126.074 Y170.645 E.00021
G3 X125.982 Y167.933 I.006 J-1.357 E.12785
G3 X126.192 Y167.935 I.098 J1.196 E.00647
G3 X126.309 Y170.625 I-.113 J1.353 E.12047
G1 X126.139 Y170.643 E.00527
; WIPE_START
G1 F9547.055
M204 S10000
G1 X126.074 Y170.645 E-.02462
G1 X125.838 Y170.629 E-.08994
G1 X125.499 Y170.522 E-.13495
G1 X125.294 Y170.404 E-.09013
G1 X125.112 Y170.251 E-.09006
G1 X124.945 Y170.047 E-.10025
G1 X124.841 Y169.865 E-.07987
G1 X124.76 Y169.642 E-.09008
G1 X124.739 Y169.485 E-.0601
; WIPE_END
G1 E-.04 F1800
G1 X128.327 Y166.205 Z2 F30000
G1 Z1.6
G1 E.8 F1800
G1 F4738
M204 S5000
G1 X128.279 Y165.989 E.0068
G3 X129.518 Y164.398 I1.337 J-.237 E.06983
G3 X129.728 Y164.399 I.099 J1.2 E.00647
G3 X128.355 Y166.256 I-.112 J1.353 E.1772
; WIPE_START
G1 F9547.055
M204 S10000
G1 X128.279 Y165.989 E-.10577
G1 X128.249 Y165.754 E-.08983
G1 X128.27 Y165.518 E-.09008
G1 X128.331 Y165.289 E-.0901
G1 X128.431 Y165.074 E-.0901
G1 X128.648 Y164.792 E-.13494
G1 X128.852 Y164.625 E-.10026
G1 X128.987 Y164.549 E-.05892
; WIPE_END
G1 E-.04 F1800
G1 X123.954 Y158.811 Z2 F30000
G1 X118.397 Y152.476 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4738
G1 X118.642 Y152.388 E.00864
G3 X119.02 Y152.337 I.414 J1.627 E.01268
G3 X120 Y152.754 I-.023 J1.413 E.03625
G1 X131.296 Y164.049 E.52988
G3 X131.552 Y165.711 I-1 J1.005 E.05971
G1 X131.367 Y165.687 E.00622
G2 X129.457 Y167.5 I-1.75 J.069 E.26625
G1 X129.824 Y167.516 E.01221
G1 X127.836 Y169.505 E.09328
G2 X127.079 Y167.854 I-1.897 J-.129 E.06279
G2 X126.007 Y171.047 I-.999 J1.441 E.21557
M73 P90 R0
G1 X126.031 Y171.233 E.00622
G3 X124.369 Y170.976 I-.657 J-1.257 E.05972
G1 X113.074 Y159.681 E.52989
G3 X112.817 Y158.019 I1 J-1.005 E.05971
G1 X113.003 Y158.043 E.00622
G2 X114.913 Y156.23 I1.75 J-.069 E.26626
G1 X114.545 Y156.214 E.0122
G1 X116.534 Y154.226 E.09328
G2 X117.29 Y155.876 I1.897 J.129 E.0628
G2 X118.363 Y152.683 I.999 J-1.441 E.21557
G1 X118.338 Y152.497 E.00622
G1 X118.341 Y152.497 E.00007
; WIPE_START
G1 F8843.478
G1 X118.642 Y152.388 E-.12178
G1 X118.881 Y152.341 E-.09254
G1 X119.02 Y152.337 E-.05281
G1 X119.365 Y152.384 E-.13216
G1 X119.593 Y152.467 E-.0925
G1 X119.804 Y152.589 E-.09259
G1 X120 Y152.754 E-.0975
G1 X120.146 Y152.899 E-.07813
; WIPE_END
G1 E-.04 F1800
G1 X116.973 Y154.722 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4738
M204 S5000
G1 X116.944 Y154.44 E.00869
G3 X118.204 Y153.084 I1.357 J-.002 E.06259
G3 X118.414 Y153.085 I.098 J1.196 E.00647
G3 X116.991 Y154.79 I-.113 J1.353 E.18213
G1 X116.988 Y154.78 E.00033
; WIPE_START
G1 F9547.055
M204 S10000
G1 X116.944 Y154.44 E-.13007
G1 X116.982 Y154.088 E-.13455
G1 X117.063 Y153.866 E-.0901
G1 X117.181 Y153.66 E-.0901
G1 X117.335 Y153.477 E-.09077
G1 X117.516 Y153.326 E-.08943
G1 X117.721 Y153.208 E-.09006
G1 X117.832 Y153.167 E-.04492
; WIPE_END
G1 E-.04 F1800
G1 X113.436 Y158.246 Z2 F30000
G1 Z1.6
G1 E.8 F1800
G1 F4738
M204 S5000
G1 X113.409 Y157.976 E.00835
G3 X114.668 Y156.62 I1.357 J-.002 E.06259
G3 X114.879 Y156.621 I.098 J1.196 E.00647
G3 X113.455 Y158.326 I-.113 J1.353 E.18213
G1 X113.45 Y158.305 E.00067
; WIPE_START
G1 F9547.055
M204 S10000
G1 X113.409 Y157.976 E-.12588
G1 X113.421 Y157.74 E-.08984
G1 X113.482 Y157.511 E-.09007
G1 X113.582 Y157.296 E-.09014
G1 X113.719 Y157.1 E-.09077
G1 X113.98 Y156.862 E-.13425
G1 X114.185 Y156.743 E-.09011
G1 X114.306 Y156.699 E-.04893
; WIPE_END
G1 E-.04 F1800
G1 X118.258 Y152.106 Z2 F30000
G1 Z1.6
G1 E.8 F1800
G1 F4738
M204 S5000
G1 X118.393 Y152.058 E.00441
G3 X119.037 Y151.945 I.639 J1.752 E.0202
G3 X120.272 Y152.471 I-.039 J1.804 E.04225
G1 X131.579 Y163.778 E.49135
G3 X131.579 Y166.316 I-1.269 J1.269 E.08662
; object ids of layer 8 start: 817,839
M624 BgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer8 end: 817,839
M625
G1 X126.636 Y171.259 E.21481
G3 X124.098 Y171.259 I-1.269 J-1.287 E.08645
G1 X112.79 Y159.952 E.49136
G3 X112.79 Y157.414 I1.287 J-1.269 E.08644
G1 X117.734 Y152.471 E.21481
G3 X118.208 Y152.137 I1.298 J1.339 E.01789
M204 S10000
G1 X118.153 Y152.588 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.174529
G1 F4738
G2 X117.493 Y153.054 I10.657 J15.802 E.00866
; LINE_WIDTH: 0.112346
G1 X117.321 Y153.197 E.00126
G1 X117.356 Y153.126 F30000
; LINE_WIDTH: 0.235436
G1 F4738
G1 X118.156 Y152.617 E.01488
G1 X118.159 Y152.637 F30000
; LINE_WIDTH: 0.306719
G1 F4738
G1 X117.418 Y153.064 E.01838
G1 X117.478 Y153.004 F30000
; LINE_WIDTH: 0.387275
G1 F4738
G1 X117.995 Y152.735 E.01634
G1 X118.191 Y152.882 E.00688
G1 X118.923 Y152.565 F30000
; LINE_WIDTH: 0.10589
G1 F4738
G1 X119.011 Y152.579 E.00046
; LINE_WIDTH: 0.145052
G3 X119.146 Y152.611 I-.298 J1.56 E.00115
G1 X119.151 Y152.612 E.00005
; LINE_WIDTH: 0.193582
G3 X119.313 Y152.67 I-.714 J2.255 E.00212
G1 X119.32 Y152.673 E.00009
; LINE_WIDTH: 0.242061
G3 X119.464 Y152.745 I-.745 J1.674 E.0026
G1 X119.544 Y152.795 E.00154
; LINE_WIDTH: 0.284596
G3 X119.759 Y152.97 I-.723 J1.111 E.00546
G1 X120.005 Y153.236 E.00714
; LINE_WIDTH: 0.331308
G1 X120.12 Y153.379 E.00431
; LINE_WIDTH: 0.365945
G1 X120.179 Y153.46 E.00263
; LINE_WIDTH: 0.394262
G1 X120.23 Y153.53 E.00247
; LINE_WIDTH: 0.424372
G1 X120.385 Y153.76 E.00864
G1 X120.992 Y153.977 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F4738
G1 X120.179 Y154.791 E.03542
; WIPE_START
G1 F9531.878
G1 X120.992 Y153.977 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X117.052 Y153.466 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.112756
G1 F4738
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.157457
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.190491
G1 X116.716 Y153.915 E.00229
G1 X116.749 Y154.125 F30000
; LINE_WIDTH: 0.106117
G1 F4738
G1 X116.758 Y154.027 E.00051
; LINE_WIDTH: 0.154965
G3 X116.809 Y153.673 I7.752 J.95 E.00327
; WIPE_START
G1 F15000
G1 X116.758 Y154.027 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.636 Y158.334 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F4738
G1 X118.456 Y156.514 E.07922
G3 X117.939 Y156.496 I-.156 J-3.082 E.01593
G1 X116.816 Y157.614 E.04879
G2 X116.693 Y157.209 I-1.26 J.16 E.01311
G1 X117.528 Y156.374 E.03634
G3 X117.174 Y156.194 I.333 J-1.094 E.01229
G1 X116.515 Y156.852 E.02866
G2 X116.28 Y156.553 I-1.252 J.742 E.01174
G1 X116.873 Y155.961 E.02578
G3 X116.623 Y155.676 I1.027 J-1.155 E.01168
G1 X115.998 Y156.301 E.02718
G1 X115.667 Y156.098 E.01196
G1 X116.418 Y155.347 E.0327
G3 X116.275 Y154.956 I4.433 J-1.838 E.01283
G1 X115.133 Y156.098 E.0497
; WIPE_START
G1 F9531.878
G1 X116.275 Y154.956 E-.61369
G1 X116.407 Y155.317 E-.14632
; WIPE_END
G1 E-.04 F1800
G1 X113.992 Y156.49 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.154991
G1 F4738
G3 X114.346 Y156.438 I1.308 J7.73 E.00327
; LINE_WIDTH: 0.106116
G1 X114.444 Y156.429 E.00051
G1 X114.234 Y156.397 F30000
; LINE_WIDTH: 0.190127
G1 F4738
G1 X114.071 Y156.506 E.00235
; LINE_WIDTH: 0.155928
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.11235
G1 X113.786 Y156.732 E.00126
G1 X113.203 Y157.872 F30000
; LINE_WIDTH: 0.387807
G1 F4738
G1 X113.055 Y157.675 E.00692
G3 X113.351 Y157.131 I8.659 J4.358 E.01742
G1 X113.384 Y157.098 F30000
; LINE_WIDTH: 0.306744
G1 F4738
G1 X112.956 Y157.839 E.01839
G1 X112.936 Y157.837 F30000
; LINE_WIDTH: 0.235492
G1 F4738
G1 X113.446 Y157.036 E.01491
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.112759
G1 F4738
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.174711
G2 X112.908 Y157.833 I14.549 J10.755 E.00863
G1 X112.885 Y158.603 F30000
; LINE_WIDTH: 0.104951
G1 F4738
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.143643
G2 X112.931 Y158.826 I1.662 J-.316 E.00121
G1 X112.932 Y158.831 E.00004
; LINE_WIDTH: 0.193557
G2 X112.99 Y158.994 I2.258 J-.715 E.00211
G1 X112.993 Y159 E.00009
; LINE_WIDTH: 0.242712
G2 X113.055 Y159.125 I1.461 J-.646 E.00227
G1 X113.116 Y159.224 E.00189
; LINE_WIDTH: 0.284605
G2 X113.289 Y159.439 I1.027 J-.652 E.00546
G1 X113.556 Y159.685 E.00714
; LINE_WIDTH: 0.331291
M73 P91 R0
G1 X113.699 Y159.8 E.00431
; LINE_WIDTH: 0.374097
G1 X113.823 Y159.891 E.00416
; LINE_WIDTH: 0.419257
G1 X114.08 Y160.066 E.00952
G1 X115.118 Y159.852 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F4738
G1 X114.417 Y160.553 E.0305
G1 X114.684 Y160.82 E.01162
G1 X121.139 Y154.364 E.28097
G1 X121.407 Y154.631 E.01162
G1 X114.951 Y161.087 E.28097
G1 X115.218 Y161.354 E.01162
G1 X121.674 Y154.899 E.28097
G1 X121.941 Y155.166 E.01162
G1 X115.485 Y161.621 E.28097
G1 X115.752 Y161.888 E.01162
G1 X122.208 Y155.433 E.28097
G1 X122.475 Y155.7 E.01162
G1 X116.019 Y162.155 E.28097
G1 X116.286 Y162.422 E.01162
G1 X122.742 Y155.967 E.28097
G1 X123.009 Y156.234 E.01162
G1 X116.553 Y162.689 E.28097
G1 X116.821 Y162.956 E.01162
G1 X123.276 Y156.501 E.28097
G1 X123.543 Y156.768 E.01162
G1 X117.088 Y163.223 E.28097
G1 X117.355 Y163.49 E.01162
G1 X123.81 Y157.035 E.28097
G1 X124.077 Y157.302 E.01162
G1 X117.622 Y163.757 E.28097
G1 X117.889 Y164.025 E.01162
G1 X124.344 Y157.569 E.28097
G1 X124.611 Y157.836 E.01162
G1 X118.156 Y164.292 E.28097
G1 X118.423 Y164.559 E.01162
G1 X124.878 Y158.103 E.28097
G1 X125.145 Y158.37 E.01162
G1 X118.69 Y164.826 E.28097
G1 X118.957 Y165.093 E.01162
G1 X125.412 Y158.637 E.28097
G1 X125.679 Y158.904 E.01162
G1 X119.224 Y165.36 E.28097
G1 X119.491 Y165.627 E.01162
G1 X125.947 Y159.171 E.28097
G1 X126.214 Y159.439 E.01162
G1 X119.758 Y165.894 E.28097
G1 X120.025 Y166.161 E.01162
G1 X126.481 Y159.706 E.28097
G1 X126.748 Y159.973 E.01162
G1 X120.292 Y166.428 E.28097
G1 X120.559 Y166.695 E.01162
G1 X127.015 Y160.24 E.28097
G1 X127.282 Y160.507 E.01162
G1 X120.826 Y166.962 E.28097
G1 X121.094 Y167.229 E.01162
G1 X127.549 Y160.774 E.28097
G1 X127.816 Y161.041 E.01162
G1 X121.361 Y167.496 E.28097
G1 X121.628 Y167.763 E.01162
G1 X128.083 Y161.308 E.28097
G1 X128.35 Y161.575 E.01162
G1 X121.895 Y168.03 E.28097
G1 X122.162 Y168.297 E.01162
G1 X128.617 Y161.842 E.28097
G1 X128.884 Y162.109 E.01162
G1 X122.429 Y168.565 E.28097
G1 X122.696 Y168.832 E.01162
G1 X129.151 Y162.376 E.28097
G1 X129.418 Y162.643 E.01162
G1 X122.963 Y169.099 E.28097
G1 X123.23 Y169.366 E.01162
G1 X129.685 Y162.91 E.28097
G1 X129.952 Y163.177 E.01162
G1 X129.259 Y163.871 E.03018
G1 X130.289 Y163.665 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.425237
G1 F4738
G1 X130.507 Y163.81 E.00815
; LINE_WIDTH: 0.396748
G1 X130.59 Y163.871 E.00296
; LINE_WIDTH: 0.367972
G1 X130.66 Y163.922 E.00229
; LINE_WIDTH: 0.334084
G1 X130.804 Y164.037 E.0044
; LINE_WIDTH: 0.285101
G3 X131.193 Y164.419 I-1.98 J2.405 E.01076
G1 X131.254 Y164.505 E.00209
; LINE_WIDTH: 0.242055
G3 X131.376 Y164.73 I-1.081 J.734 E.00415
; LINE_WIDTH: 0.193541
G3 X131.437 Y164.899 I-2.844 J1.121 E.00221
; LINE_WIDTH: 0.143639
G3 X131.473 Y165.047 I-1.851 J.519 E.00125
; LINE_WIDTH: 0.104948
G1 X131.484 Y165.127 E.00041
G1 X131.166 Y165.858 F30000
; LINE_WIDTH: 0.387808
G1 F4738
G1 X131.315 Y166.055 E.00692
G3 X131.022 Y166.596 I-9.201 J-4.631 E.0173
G1 X130.986 Y166.632 F30000
; LINE_WIDTH: 0.306792
G1 F4738
G1 X131.413 Y165.891 E.01839
G1 X131.433 Y165.894 F30000
; LINE_WIDTH: 0.23541
G1 F4738
G1 X131.16 Y166.323 E.00799
; LINE_WIDTH: 0.220043
G1 X131.122 Y166.38 E.001
; LINE_WIDTH: 0.191868
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155923
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112351
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112755
G1 F4738
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157458
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.190496
G1 X130.135 Y167.334 E.00229
G1 X129.925 Y167.301 F30000
; LINE_WIDTH: 0.106123
G1 F4738
G1 X130.023 Y167.292 E.00051
; LINE_WIDTH: 0.154987
G2 X130.377 Y167.241 I-.966 J-7.873 E.00327
; WIPE_START
G1 F15000
G1 X130.023 Y167.292 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X125.723 Y167.407 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F4738
G1 X127.53 Y165.6 E.07866
G2 X127.56 Y166.104 I1.447 J.168 E.01563
G1 X126.43 Y167.234 E.04917
G3 X126.842 Y167.356 I-.26 J1.624 E.01325
G1 X127.676 Y166.522 E.03632
G2 X127.856 Y166.876 I1.421 J-.501 E.01226
G1 X127.195 Y167.537 E.02877
G3 X127.495 Y167.772 I-.473 J.911 E.01178
G1 X128.09 Y167.176 E.02592
G2 X128.37 Y167.43 I1.089 J-.916 E.01167
G1 X127.747 Y168.053 E.0271
G3 X127.952 Y168.383 I-1.199 J.97 E.01197
G1 X128.703 Y167.632 E.0327
G2 X129.099 Y167.77 I.819 J-1.711 E.01293
G1 X127.948 Y168.921 E.05009
; WIPE_START
G1 F9531.878
G1 X129.099 Y167.77 E-.61852
G1 X128.903 Y167.717 E-.07711
G1 X128.747 Y167.651 E-.06437
; WIPE_END
G1 E-.04 F1800
G1 X127.559 Y170.058 Z2 F30000
G1 Z1.6
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.166103
G1 F4738
G1 X127.593 Y169.844 E.00218
; LINE_WIDTH: 0.140245
G1 X127.612 Y169.704 E.00112
; LINE_WIDTH: 0.106129
G1 X127.621 Y169.606 E.00051
G1 X127.653 Y169.816 F30000
; LINE_WIDTH: 0.185958
G1 F4738
G1 X127.527 Y170.002 E.00261
; LINE_WIDTH: 0.151523
G1 X127.46 Y170.093 E.001
; LINE_WIDTH: 0.112355
G1 X127.318 Y170.264 E.00126
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.112763
G1 F4738
G1 X126.873 Y170.679 E.00129
; LINE_WIDTH: 0.15747
G1 X126.758 Y170.763 E.00134
; LINE_WIDTH: 0.193029
G1 X126.7 Y170.802 E.00085
; LINE_WIDTH: 0.233552
G3 X126.213 Y171.114 I-7.297 J-10.856 E.00898
G1 X126.211 Y171.094 F30000
; LINE_WIDTH: 0.306797
G1 F4738
G1 X126.952 Y170.665 E.01842
G1 X126.919 Y170.699 F30000
; LINE_WIDTH: 0.387783
G1 F4738
G3 X126.374 Y170.995 I-4.803 J-8.185 E.01741
G1 X126.178 Y170.847 E.00692
G1 X125.446 Y171.165 F30000
; LINE_WIDTH: 0.104947
G1 F4738
G1 X125.367 Y171.153 E.00041
; LINE_WIDTH: 0.1436
G3 X125.219 Y171.118 I.368 J-1.877 E.00125
; LINE_WIDTH: 0.193559
G3 X125.049 Y171.057 I.947 J-2.893 E.00221
; LINE_WIDTH: 0.242074
G3 X124.825 Y170.935 I.511 J-1.204 E.00414
; LINE_WIDTH: 0.278941
G1 X124.739 Y170.873 E.00204
G3 X124.471 Y170.615 I1.424 J-1.748 E.00716
; LINE_WIDTH: 0.305338
G1 X124.337 Y170.459 E.00441
; LINE_WIDTH: 0.337596
G1 X124.241 Y170.34 E.00367
; LINE_WIDTH: 0.367934
G1 X124.19 Y170.27 E.00229
; LINE_WIDTH: 0.396755
G1 X124.13 Y170.187 E.00296
; LINE_WIDTH: 0.425251
G1 X123.984 Y169.97 E.00815
G1 X123.377 Y169.753 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.4206
G1 F4738
G1 X124.19 Y168.939 E.0354
; OBJECT_ID: 817
; WIPE_START
G1 F9531.878
G1 X123.377 Y169.753 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X119.515 Y163.169 Z2 F30000
G1 X103.421 Y135.733 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4738
G1 X103.412 Y135.625 E.00357
G1 X103.445 Y135.523 E.00358
G1 X103.515 Y135.441 E.00357
G1 X103.612 Y135.393 E.00358
G1 X103.705 Y135.385 E.00311
G1 X103.797 Y135.409 E.00314
G1 X103.884 Y135.473 E.00357
G1 X103.939 Y135.566 E.00358
G1 X103.953 Y135.673 E.00357
G1 X103.925 Y135.777 E.00357
G1 X103.859 Y135.862 E.00358
G1 X103.765 Y135.914 E.00357
G1 X103.658 Y135.926 E.00358
G1 X103.555 Y135.896 E.00357
G1 X103.472 Y135.828 E.00357
G1 X103.449 Y135.786 E.00158
M204 S250
G1 X103.036 Y135.8 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4738
M204 S5000
G1 X103.017 Y135.714 E.0027
G3 X103.64 Y134.993 I.66 J-.06 E.03271
G3 X103.74 Y134.995 I.039 J.494 E.00305
G3 X103.046 Y135.859 I-.063 J.66 E.08762
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.017 Y135.714 E-.05606
G1 X103.022 Y135.581 E-.05045
G1 X103.05 Y135.452 E-.05027
G1 X103.103 Y135.331 E-.05032
G1 X103.178 Y135.222 E-.05025
G1 X103.274 Y135.131 E-.05023
G1 X103.386 Y135.061 E-.05027
G1 X103.51 Y135.014 E-.05034
G1 X103.64 Y134.993 E-.05021
G1 X103.74 Y134.995 E-.03765
G1 X103.963 Y135.054 E-.0877
G1 X104.077 Y135.121 E-.05032
G1 X104.175 Y135.21 E-.05027
G1 X104.253 Y135.316 E-.05028
G1 X104.281 Y135.377 E-.0254
; WIPE_END
G1 E-.04 F1800
G1 X98.634 Y130.243 Z2 F30000
G1 X92.101 Y124.303 Z2
G1 Z1.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4738
G1 X92.131 Y124.209 E.00329
G1 X92.201 Y124.127 E.00357
G1 X92.298 Y124.079 E.00358
G1 X92.392 Y124.072 E.00312
G1 X92.483 Y124.096 E.00314
G1 X92.57 Y124.16 E.00357
G1 X92.625 Y124.252 E.00357
G1 X92.64 Y124.359 E.00358
G1 X92.612 Y124.463 E.00357
G1 X92.546 Y124.548 E.00357
G1 X92.452 Y124.601 E.00358
G1 X92.344 Y124.613 E.00358
G1 X92.241 Y124.582 E.00356
G1 X92.158 Y124.514 E.00358
G1 X92.108 Y124.419 E.00358
G1 X92.103 Y124.363 E.00187
M204 S250
G1 X91.725 Y124.182 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4738
M204 S5000
G1 X91.756 Y124.075 E.00344
G3 X92.327 Y123.679 I.607 J.266 E.02247
G3 X92.426 Y123.681 I.039 J.494 E.00305
G3 X91.708 Y124.239 I-.063 J.66 E.09713
; CHANGE_LAYER
; Z_HEIGHT: 1.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.756 Y124.075 E-.06501
G1 X91.824 Y123.961 E-.0504
G1 X91.91 Y123.861 E-.0503
G1 X92.073 Y123.747 E-.07527
G1 X92.196 Y123.7 E-.05029
G1 X92.327 Y123.679 E-.05021
G1 X92.426 Y123.681 E-.03765
G1 X92.649 Y123.74 E-.08773
G1 X92.763 Y123.807 E-.05027
G1 X92.861 Y123.896 E-.05027
G1 X92.939 Y124.003 E-.0503
G1 X92.995 Y124.123 E-.05022
G1 X93.026 Y124.251 E-.05029
G1 X93.031 Y124.361 E-.04179
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 9/15
; update layer progress
M73 L9
M991 S0 P8 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z2 I-.99 J.707 P1  F30000
G1 X126.088 Y170.649 Z2
G1 Z1.8
M73 P92 R0
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X126.074 Y170.648 E.00043
G3 X125.972 Y167.934 I.008 J-1.359 E.12757
G1 X126.074 Y167.929 E.00315
G3 X126.31 Y170.629 I.008 J1.359 E.12444
G1 X126.147 Y170.643 E.00501
; WIPE_START
G1 F9547.055
M204 S10000
G1 X126.074 Y170.648 E-.02803
G1 X125.837 Y170.629 E-.09048
G1 X125.499 Y170.522 E-.13451
G1 X125.294 Y170.404 E-.09008
G1 X125.112 Y170.251 E-.09012
G1 X124.96 Y170.07 E-.09011
G1 X124.841 Y169.865 E-.09006
G1 X124.734 Y169.526 E-.13495
G1 X124.732 Y169.495 E-.01166
; WIPE_END
G1 E-.04 F1800
G1 X128.342 Y166.233 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X128.304 Y166.104 E.00414
G3 X129.507 Y164.398 I1.313 J-.351 E.07311
G1 X129.609 Y164.394 E.00315
G3 X128.384 Y166.325 I.008 J1.359 E.17895
G1 X128.367 Y166.288 E.00127
; WIPE_START
G1 F9547.055
M204 S10000
G1 X128.304 Y166.104 E-.07387
G1 X128.249 Y165.754 E-.13452
G1 X128.27 Y165.517 E-.09052
G1 X128.377 Y165.179 E-.13452
G1 X128.495 Y164.974 E-.0901
G1 X128.648 Y164.791 E-.09055
G1 X128.829 Y164.64 E-.08965
G1 X128.957 Y164.566 E-.05626
; WIPE_END
G1 E-.04 F1800
G1 X123.948 Y158.808 Z2.2 F30000
G1 X118.426 Y152.461 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4605
G1 X118.525 Y152.422 E.00354
G3 X119.125 Y152.341 I.51 J1.528 E.02017
G3 X120 Y152.754 I-.162 J1.48 E.03272
G1 X131.296 Y164.049 E.52989
G3 X131.552 Y165.711 I-1.021 J1.008 E.0596
G1 X131.367 Y165.687 E.00622
G2 X129.457 Y167.5 I-1.75 J.069 E.26615
G1 X129.824 Y167.516 E.01221
G1 X127.836 Y169.505 E.09328
G2 X127.079 Y167.854 I-1.897 J-.129 E.06279
G2 X126.007 Y171.047 I-.999 J1.441 E.21557
G1 X126.031 Y171.233 E.00622
G3 X124.369 Y170.976 I-.653 J-1.278 E.0596
G1 X113.074 Y159.681 E.52988
G3 X112.817 Y158.019 I1.019 J-1.008 E.05962
G1 X113.003 Y158.043 E.00622
G2 X114.913 Y156.23 I1.75 J-.069 E.26625
G1 X114.545 Y156.214 E.01221
G1 X116.534 Y154.226 E.09328
G2 X117.29 Y155.876 I1.897 J.129 E.0628
G2 X118.363 Y152.683 I.998 J-1.441 E.21548
G1 X118.338 Y152.497 E.00622
G1 X118.371 Y152.484 E.00116
; WIPE_START
G1 F8843.478
G1 X118.525 Y152.422 E-.06336
G1 X118.76 Y152.357 E-.09253
G1 X119.125 Y152.341 E-.13855
G1 X119.364 Y152.384 E-.09258
G1 X119.593 Y152.467 E-.09256
G1 X119.804 Y152.588 E-.09243
G1 X120 Y152.754 E-.09765
G1 X120.169 Y152.922 E-.09035
; WIPE_END
G1 E-.04 F1800
G1 X116.961 Y154.691 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4605
M204 S5000
G1 X116.965 Y154.675 E.0005
G3 X118.193 Y153.085 I1.339 J-.235 E.06948
G1 X118.296 Y153.08 E.00315
G3 X117.071 Y155.012 I.008 J1.359 E.17895
G1 X116.98 Y154.747 E.00858
; WIPE_START
G1 F9547.055
M204 S10000
G1 X116.965 Y154.675 E-.02809
G1 X116.935 Y154.44 E-.08984
G1 X116.956 Y154.204 E-.09008
G1 X117.063 Y153.866 E-.13494
G1 X117.181 Y153.66 E-.09012
G1 X117.334 Y153.479 E-.09009
G1 X117.516 Y153.326 E-.0901
G1 X117.721 Y153.208 E-.09009
G1 X117.861 Y153.157 E-.05665
; WIPE_END
G1 E-.04 F1800
G1 X113.434 Y158.255 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X113.43 Y158.211 E.00137
G3 X114.658 Y156.62 I1.339 J-.235 E.06948
G1 X114.76 Y156.616 E.00315
G3 X113.535 Y158.547 I.008 J1.359 E.17895
G1 X113.454 Y158.312 E.00766
; WIPE_START
G1 F9547.055
M204 S10000
G1 X113.43 Y158.211 E-.03952
G1 X113.4 Y157.976 E-.08984
G1 X113.421 Y157.74 E-.09007
G1 X113.482 Y157.51 E-.09059
G1 X113.646 Y157.196 E-.13447
G1 X113.798 Y157.014 E-.09011
G1 X113.98 Y156.862 E-.09012
G1 X114.185 Y156.743 E-.09004
G1 X114.297 Y156.703 E-.04524
; WIPE_END
G1 E-.04 F1800
G1 X118.276 Y152.099 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
G1 F4605
M204 S5000
G1 X118.393 Y152.058 E.0038
G3 X119.159 Y151.95 I.636 J1.747 E.02393
G3 X120.272 Y152.471 I-.207 J1.893 E.03844
G1 X131.579 Y163.778 E.49136
G3 X131.579 Y166.316 I-1.287 J1.269 E.08644
; object ids of layer 9 start: 817,839
M624 BgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer9 end: 817,839
M625
G1 X126.636 Y171.259 E.21482
G3 X124.098 Y171.259 I-1.269 J-1.287 E.08645
G1 X112.79 Y159.952 E.49136
G3 X112.79 Y157.414 I1.287 J-1.269 E.08645
G1 X117.734 Y152.471 E.21481
G3 X118.224 Y152.129 I1.295 J1.334 E.01846
M204 S10000
G1 X118.152 Y152.587 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.17453
G1 F4605
G2 X117.493 Y153.054 I11.349 J16.742 E.00867
; LINE_WIDTH: 0.112356
G1 X117.321 Y153.197 E.00126
G1 X117.356 Y153.126 F30000
; LINE_WIDTH: 0.235423
G1 F4605
G1 X118.156 Y152.616 E.01489
G1 X118.159 Y152.637 F30000
; LINE_WIDTH: 0.30672
G1 F4605
G1 X117.418 Y153.064 E.01839
G1 X117.49 Y152.992 F30000
; LINE_WIDTH: 0.387666
G1 F4605
G1 X117.995 Y152.735 E.01593
G1 X118.191 Y152.882 E.00689
G1 X118.926 Y152.566 F30000
; LINE_WIDTH: 0.107819
G1 F4605
G1 X119.024 Y152.582 E.00053
; LINE_WIDTH: 0.147292
G3 X119.146 Y152.611 I-.272 J1.41 E.00106
G1 X119.151 Y152.612 E.00005
; LINE_WIDTH: 0.193559
G3 X119.313 Y152.67 I-.714 J2.256 E.00212
G1 X119.32 Y152.673 E.00009
; LINE_WIDTH: 0.242077
G3 X119.464 Y152.745 I-.751 J1.685 E.0026
G1 X119.544 Y152.796 E.00154
; LINE_WIDTH: 0.284603
G3 X119.759 Y152.97 I-.723 J1.112 E.00546
G1 X120.005 Y153.237 E.00715
; LINE_WIDTH: 0.331315
G1 X120.12 Y153.379 E.00431
; LINE_WIDTH: 0.365928
G1 X120.179 Y153.46 E.00263
; LINE_WIDTH: 0.394239
G1 X120.23 Y153.53 E.00247
; LINE_WIDTH: 0.424374
G1 X120.385 Y153.76 E.00864
; WIPE_START
G1 F9437.586
G1 X120.23 Y153.53 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X117.052 Y153.466 Z2.2 F30000
G1 Z1.8
G1 E.8 F1800
; LINE_WIDTH: 0.11276
G1 F4605
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.15748
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.190509
G1 X116.716 Y153.915 E.00229
G1 X116.749 Y154.125 F30000
; LINE_WIDTH: 0.106118
G1 F4605
G1 X116.758 Y154.027 E.00051
; LINE_WIDTH: 0.154979
G3 X116.809 Y153.673 I7.778 J.954 E.00327
G1 X113.992 Y156.49 F30000
; LINE_WIDTH: 0.154988
G1 F4605
G3 X114.346 Y156.438 I1.307 J7.724 E.00327
; LINE_WIDTH: 0.106116
G1 X114.444 Y156.429 E.00051
G1 X114.234 Y156.397 F30000
; LINE_WIDTH: 0.190124
G1 F4605
G1 X114.071 Y156.506 E.00235
; LINE_WIDTH: 0.155935
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112353
G1 X113.786 Y156.732 E.00126
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.112762
G1 F4605
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.154626
G1 X113.297 Y157.277 E.00114
; LINE_WIDTH: 0.188351
G1 X113.254 Y157.341 E.00091
; LINE_WIDTH: 0.231906
G2 X112.935 Y157.836 I9.662 J6.583 E.00909
G1 X112.956 Y157.839 F30000
; LINE_WIDTH: 0.306789
G1 F4605
G1 X113.384 Y157.098 E.0184
G1 X113.354 Y157.128 F30000
; LINE_WIDTH: 0.387786
G1 F4605
G2 X113.055 Y157.675 I7.832 J4.639 E.01755
G1 X113.203 Y157.872 E.00692
G1 X112.885 Y158.603 F30000
; LINE_WIDTH: 0.104949
G1 F4605
G1 X112.897 Y158.683 E.00041
; LINE_WIDTH: 0.142821
G2 X112.931 Y158.826 I1.665 J-.317 E.0012
; LINE_WIDTH: 0.192423
G2 X112.991 Y158.993 I3.11 J-1.023 E.00217
G1 X112.994 Y159 E.00009
; LINE_WIDTH: 0.241847
G2 X113.065 Y159.144 I1.492 J-.647 E.0026
G1 X113.115 Y159.225 E.00154
; LINE_WIDTH: 0.284594
G2 X113.289 Y159.439 I1.111 J-.723 E.00545
G1 X113.556 Y159.685 E.00715
; LINE_WIDTH: 0.331312
G1 X113.699 Y159.8 E.00431
; LINE_WIDTH: 0.365922
G1 X113.78 Y159.86 E.00263
; LINE_WIDTH: 0.394207
G1 X113.849 Y159.911 E.00247
; LINE_WIDTH: 0.424352
G1 X114.08 Y160.065 E.00864
G1 X114.139 Y160.272 F30000
; FEATURE: Internal solid infill
; LINE_WIDTH: 0.42317
G1 F4605
G1 X123.657 Y169.791 E.41711
G1 X123.974 Y169.569 E.01196
G1 X114.476 Y160.072 E.41617
G1 X114.496 Y160.043 E.00107
G2 X114.942 Y160.055 I.268 J-1.688 E.01388
G1 X114.989 Y160.047 E.00148
G1 X124.006 Y169.064 E.39514
G3 X124.104 Y168.624 I1.524 J.105 E.01403
G1 X115.426 Y159.946 E.38025
G2 X115.801 Y159.784 I-.429 J-1.505 E.01271
G1 X124.271 Y168.254 E.37115
G3 X124.489 Y167.933 I1.79 J.984 E.01201
G1 X116.116 Y159.56 E.36691
G1 X116.38 Y159.287 E.01178
G1 X124.763 Y167.669 E.36732
G3 X125.087 Y167.456 I.768 J.813 E.01209
G1 X116.594 Y158.963 E.37215
G2 X116.75 Y158.582 I-1.003 J-.634 E.01284
G1 X125.468 Y167.299 E.38201
G3 X125.922 Y167.216 I.463 J1.237 E.01438
G1 X116.839 Y158.133 E.398
G2 X116.816 Y157.613 I-1.984 J-.169 E.01617
G1 X116.8 Y157.556 E.00184
G1 X126.492 Y167.247 E.42468
G3 X128.09 Y168.749 I-.418 J2.046 E.07155
G1 X128.094 Y168.775 E.0008
G1 X128.326 Y168.544 E.01013
G1 X115.506 Y155.724 E.56175
G1 X115.775 Y155.455 E.01178
G1 X128.594 Y168.275 E.56175
G1 X128.863 Y168.006 E.01178
G1 X116.044 Y155.186 E.56175
M73 P93 R0
G1 X116.275 Y154.955 E.01013
G2 X117.876 Y156.48 I2.018 J-.516 E.07221
G1 X127.573 Y166.177 E.42493
G3 X127.53 Y165.597 I1.625 J-.411 E.01812
G1 X118.447 Y156.514 E.39801
G2 X118.903 Y156.432 I-.065 J-1.66 E.01439
G1 X127.617 Y165.146 E.38186
G3 X127.774 Y164.766 I1.557 J.419 E.0128
G1 X119.281 Y156.272 E.37218
G2 X119.603 Y156.057 I-.449 J-1.023 E.01208
G1 X127.989 Y164.443 E.36746
G1 X128.255 Y164.171 E.01178
G1 X119.88 Y155.796 E.36699
G2 X120.103 Y155.484 I-1.075 J-1.003 E.01191
G1 X128.568 Y163.946 E.37088
G3 X128.943 Y163.784 I.805 J1.343 E.01271
G1 X120.27 Y155.11 E.38008
G2 X120.367 Y154.669 I-1.627 J-.588 E.01403
G1 X129.382 Y163.685 E.39507
G3 X129.874 Y163.687 I.237 J2.649 E.01525
G1 X129.893 Y163.658 E.00107
G1 X120.392 Y154.157 E.41635
G1 X120.714 Y153.941 E.01201
G1 X130.231 Y163.458 E.41702
G1 X130.289 Y163.665 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.425256
G1 F4605
G1 X130.507 Y163.81 E.00815
; LINE_WIDTH: 0.396788
G1 X130.59 Y163.87 E.00296
; LINE_WIDTH: 0.367979
G1 X130.66 Y163.922 E.00229
; LINE_WIDTH: 0.334093
G1 X130.804 Y164.037 E.0044
; LINE_WIDTH: 0.284936
G3 X131.192 Y164.419 I-1.918 J2.335 E.01075
G1 X131.254 Y164.505 E.00209
; LINE_WIDTH: 0.24205
G3 X131.376 Y164.73 I-1.081 J.734 E.00415
; LINE_WIDTH: 0.193563
G3 X131.437 Y164.899 I-2.845 J1.122 E.0022
; LINE_WIDTH: 0.143648
G3 X131.473 Y165.047 I-1.85 J.519 E.00125
; LINE_WIDTH: 0.104959
G1 X131.484 Y165.127 E.00041
G1 X131.165 Y165.858 F30000
; LINE_WIDTH: 0.387474
G1 F4605
G1 X131.315 Y166.055 E.00694
G3 X131.02 Y166.597 I-7.206 J-3.56 E.01734
G1 X130.98 Y166.637 F30000
; LINE_WIDTH: 0.297798
G1 F4605
G1 X131.414 Y165.891 E.01793
G1 X131.433 Y165.893 F30000
; LINE_WIDTH: 0.235392
G1 F4605
G1 X131.16 Y166.323 E.00798
; LINE_WIDTH: 0.220033
G1 X131.122 Y166.38 E.001
; LINE_WIDTH: 0.191894
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.15593
G1 X130.996 Y166.557 E.0013
; LINE_WIDTH: 0.112345
G1 X130.853 Y166.729 E.00126
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112744
G1 F4605
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.157427
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.190472
G1 X130.135 Y167.334 E.00229
G1 X129.925 Y167.301 F30000
; LINE_WIDTH: 0.105806
G1 F4605
G1 X130.02 Y167.293 E.00049
; LINE_WIDTH: 0.13906
G1 X130.16 Y167.274 E.00111
; LINE_WIDTH: 0.164624
G1 X130.377 Y167.241 E.00218
G1 X127.561 Y170.057 F30000
; LINE_WIDTH: 0.154967
G1 F4605
G2 X127.612 Y169.703 I-8.37 J-1.392 E.00326
; LINE_WIDTH: 0.106129
G1 X127.621 Y169.606 E.00051
G1 X127.653 Y169.815 F30000
; LINE_WIDTH: 0.19012
G1 F4605
G1 X127.544 Y169.978 E.00235
; LINE_WIDTH: 0.155913
G1 X127.46 Y170.093 E.0013
; LINE_WIDTH: 0.112342
G1 X127.318 Y170.264 E.00126
G1 X126.178 Y170.846 F30000
; LINE_WIDTH: 0.387846
G1 F4605
G1 X126.374 Y170.995 E.00692
G2 X126.92 Y170.698 I-4.07 J-8.117 E.01747
G1 X126.952 Y170.665 F30000
; LINE_WIDTH: 0.306752
G1 F4605
G1 X126.211 Y171.094 E.01841
G1 X126.213 Y171.114 F30000
; LINE_WIDTH: 0.235393
G1 F4605
G1 X127.014 Y170.604 E.01489
G1 X127.048 Y170.534 F30000
; LINE_WIDTH: 0.112745
G1 F4605
G1 X126.874 Y170.679 E.00129
; LINE_WIDTH: 0.174734
G3 X126.217 Y171.142 I-10.766 J-14.564 E.00863
G1 X125.446 Y171.165 F30000
; LINE_WIDTH: 0.104946
G1 F4605
G1 X125.367 Y171.153 E.00041
; LINE_WIDTH: 0.143622
G3 X125.219 Y171.118 I.369 J-1.879 E.00125
; LINE_WIDTH: 0.193572
G3 X125.049 Y171.057 I.954 J-2.912 E.00221
; LINE_WIDTH: 0.242076
G3 X124.825 Y170.935 I.511 J-1.204 E.00415
; LINE_WIDTH: 0.285106
G1 X124.739 Y170.873 E.0021
G3 X124.357 Y170.485 I2.023 J-2.369 E.01076
; LINE_WIDTH: 0.334067
G1 X124.241 Y170.34 E.00439
; LINE_WIDTH: 0.36794
G1 X124.19 Y170.27 E.00229
; LINE_WIDTH: 0.406403
G3 X123.979 Y169.972 I6.695 J-4.963 E.01082
; OBJECT_ID: 817
; WIPE_START
G1 F9904.178
G1 X124.19 Y170.27 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X120.258 Y163.728 Z2.2 F30000
G1 X103.431 Y135.73 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4605
G1 X103.422 Y135.626 E.00344
G1 X103.454 Y135.528 E.00344
G1 X103.521 Y135.449 E.00345
G1 X103.614 Y135.403 E.00344
G1 X103.705 Y135.395 E.003
G1 X103.793 Y135.418 E.00303
G1 X103.876 Y135.48 E.00345
G1 X103.929 Y135.569 E.00344
G1 X103.943 Y135.672 E.00344
G1 X103.916 Y135.772 E.00344
G1 X103.853 Y135.854 E.00344
G1 X103.762 Y135.905 E.00345
G1 X103.659 Y135.917 E.00345
G1 X103.56 Y135.887 E.00344
G1 X103.479 Y135.821 E.00345
G1 X103.459 Y135.783 E.00145
M204 S250
G1 X103.064 Y135.865 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4605
M204 S5000
G1 X103.051 Y135.842 E.0008
G3 X103.641 Y135.003 I.625 J-.187 E.03625
G3 X103.739 Y135.005 I.039 J.487 E.003
G3 X103.101 Y135.963 I-.062 J.65 E.08273
G1 X103.085 Y135.921 E.00139
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.051 Y135.842 E-.03266
G1 X103.03 Y135.713 E-.04958
G1 X103.032 Y135.582 E-.04956
G1 X103.059 Y135.455 E-.04952
G1 X103.111 Y135.336 E-.04956
G1 X103.186 Y135.229 E-.04947
G1 X103.28 Y135.139 E-.04956
G1 X103.391 Y135.07 E-.04949
G1 X103.513 Y135.024 E-.04958
G1 X103.641 Y135.003 E-.04948
G1 X103.739 Y135.005 E-.03705
G1 X103.959 Y135.063 E-.08642
G1 X104.071 Y135.129 E-.0495
G1 X104.167 Y135.217 E-.04957
G1 X104.245 Y135.322 E-.04953
G1 X104.255 Y135.344 E-.00949
; WIPE_END
G1 E-.04 F1800
G1 X98.62 Y130.196 Z2.2 F30000
G1 X92.125 Y124.261 Z2.2
G1 Z1.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F4605
G1 X92.14 Y124.214 E.00165
G1 X92.208 Y124.135 E.00344
G1 X92.301 Y124.089 E.00345
G1 X92.391 Y124.081 E.003
G1 X92.479 Y124.105 E.00303
G1 X92.562 Y124.166 E.00344
G1 X92.615 Y124.256 E.00344
G1 X92.63 Y124.358 E.00344
G1 X92.603 Y124.459 E.00344
G1 X92.539 Y124.541 E.00344
G1 X92.449 Y124.591 E.00344
G1 X92.345 Y124.603 E.00345
G1 X92.246 Y124.574 E.00344
G1 X92.166 Y124.508 E.00344
G1 X92.117 Y124.416 E.00344
G1 X92.109 Y124.319 E.00324
M204 S250
G1 X91.746 Y124.139 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F4605
M204 S5000
G1 X91.794 Y124.02 E.00395
G3 X92.327 Y123.689 I.569 J.321 E.02012
G3 X92.425 Y123.691 I.039 J.487 E.003
G3 X91.727 Y124.194 I-.062 J.65 E.09715
; CHANGE_LAYER
; Z_HEIGHT: 2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.794 Y124.02 E-.07072
G1 X91.872 Y123.915 E-.04964
G1 X91.967 Y123.825 E-.04953
G1 X92.077 Y123.756 E-.04952
G1 X92.199 Y123.71 E-.04958
G1 X92.327 Y123.689 E-.04944
G1 X92.425 Y123.691 E-.03708
G1 X92.645 Y123.749 E-.08645
G1 X92.757 Y123.815 E-.0495
G1 X92.854 Y123.903 E-.04952
G1 X92.931 Y124.008 E-.04952
G1 X92.986 Y124.126 E-.04954
G1 X93.017 Y124.253 E-.04955
G1 X93.021 Y124.383 E-.0495
G1 X93.013 Y124.437 E-.0209
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 10/15
; update layer progress
M73 L10
M991 S0 P9 ;notify layer change
; OBJECT_ID: 839
; start printing object, unique label id: 839
M624 BAAAAAAAAAA=
G17
G3 Z2.2 I-.99 J.708 P1  F30000
G1 X126.096 Y170.648 Z2.2
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S5000
G1 X126.073 Y170.648 E.00069
G3 X125.961 Y167.934 I.003 J-1.359 E.12757
G1 X126.074 Y167.929 E.00348
G3 X126.31 Y170.628 I.003 J1.359 E.12412
G1 X126.156 Y170.642 E.00475
; WIPE_START
G1 F9547.055
M204 S10000
G1 X126.073 Y170.648 E-.03135
G1 X125.722 Y170.603 E-.13473
G1 X125.499 Y170.522 E-.09006
G1 X125.294 Y170.404 E-.09013
G1 X125.112 Y170.251 E-.09024
G1 X124.896 Y169.97 E-.13478
G1 X124.796 Y169.755 E-.0901
G1 X124.734 Y169.526 E-.09001
G1 X124.732 Y169.503 E-.0086
; WIPE_END
G1 E-.04 F1800
G1 X128.346 Y166.247 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S5000
G1 X128.335 Y166.218 E.00096
G3 X129.496 Y164.399 I1.278 J-.465 E.07662
G1 X129.609 Y164.394 E.00348
G3 X128.495 Y166.528 I.003 J1.359 E.17163
G1 X128.374 Y166.3 E.00792
; WIPE_START
G1 F9547.055
M204 S10000
G1 X128.335 Y166.218 E-.03455
G1 X128.27 Y165.99 E-.09001
G1 X128.249 Y165.754 E-.09025
G1 X128.296 Y165.402 E-.1348
G1 X128.377 Y165.179 E-.09006
G1 X128.495 Y164.974 E-.09009
G1 X128.648 Y164.792 E-.09027
G1 X128.829 Y164.64 E-.08998
G1 X128.943 Y164.574 E-.04999
; WIPE_END
G1 E-.04 F1800
G1 X123.06 Y159.712 Z2.4 F30000
G1 X116.955 Y154.668 Z2.4
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S5000
G1 X116.939 Y154.44 E.00702
G3 X118.182 Y153.085 I1.359 J0 E.06205
G1 X118.296 Y153.08 E.00348
G3 X116.97 Y154.726 I.003 J1.359 E.18808
; WIPE_START
G1 F9547.055
M204 S10000
G1 X116.939 Y154.44 E-.10927
G1 X116.982 Y154.088 E-.13461
G1 X117.063 Y153.866 E-.09007
G1 X117.181 Y153.66 E-.09005
G1 X117.334 Y153.478 E-.09031
G1 X117.516 Y153.326 E-.09
G1 X117.721 Y153.208 E-.09001
G1 X117.883 Y153.149 E-.06567
; WIPE_END
G1 E-.04 F1800
G1 X113.436 Y158.27 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S5000
G1 X113.424 Y158.211 E.00182
G3 X114.647 Y156.621 I1.339 J-.236 E.06934
G1 X114.76 Y156.616 E.00348
G3 X113.486 Y158.44 I.003 J1.359 E.18238
G1 X113.453 Y158.327 E.0036
; WIPE_START
G1 F9547.055
M204 S10000
G1 X113.424 Y158.211 E-.04527
G1 X113.4 Y157.976 E-.08999
G1 X113.421 Y157.739 E-.09024
G1 X113.527 Y157.401 E-.13476
G1 X113.646 Y157.196 E-.09016
G1 X113.799 Y157.014 E-.09023
G1 X113.98 Y156.862 E-.08992
G1 X114.185 Y156.743 E-.09014
G1 X114.283 Y156.708 E-.0393
; WIPE_END
G1 E-.04 F1800
G1 X118.292 Y152.092 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S5000
G1 X118.393 Y152.058 E.00328
G3 X119.159 Y151.95 I.636 J1.747 E.02393
G3 X120.272 Y152.471 I-.207 J1.893 E.03844
G1 X131.579 Y163.778 E.49136
G3 X131.579 Y166.316 I-1.287 J1.269 E.08646
; object ids of layer 10 start: 817,839
M624 BgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer10 end: 817,839
M625
G1 X126.636 Y171.259 E.21481
G3 X124.098 Y171.259 I-1.269 J-1.287 E.08645
G1 X112.79 Y159.952 E.49136
G3 X112.79 Y157.414 I1.287 J-1.269 E.08645
G1 X117.734 Y152.471 E.21482
G3 X118.24 Y152.122 I1.295 J1.334 E.01897
M204 S10000
G1 X118.153 Y152.588 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.17451
G1 F5950
G2 X117.493 Y153.054 I10.653 J15.795 E.00866
; LINE_WIDTH: 0.112348
G1 X117.321 Y153.197 E.00126
G1 X117.355 Y153.127 F30000
; LINE_WIDTH: 0.23547
G1 F5950
G1 X118.156 Y152.616 E.0149
G1 X118.159 Y152.637 F30000
; LINE_WIDTH: 0.306776
G1 F5950
G1 X117.418 Y153.064 E.01839
G1 X117.448 Y153.034 F30000
; LINE_WIDTH: 0.38832
G1 F5950
G3 X117.995 Y152.735 I5.124 J8.733 E.01754
G1 X118.191 Y152.882 E.0069
; WIPE_START
G1 F10422.71
G1 X117.995 Y152.735 E-.21462
G1 X117.448 Y153.034 E-.54538
; WIPE_END
G1 E-.04 F1800
G1 X117.052 Y153.466 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.11276
G1 F5950
G1 X116.907 Y153.641 E.00129
; LINE_WIDTH: 0.157472
G1 X116.822 Y153.757 E.00134
; LINE_WIDTH: 0.19053
G1 X116.716 Y153.915 E.00229
G1 X116.758 Y154.027 F30000
; LINE_WIDTH: 0.106142
G1 F5950
G1 X116.749 Y154.125 E.00051
G1 X116.758 Y154.027 F30000
; LINE_WIDTH: 0.155015
G1 F5950
G3 X116.809 Y153.673 I7.71 J.944 E.00327
; WIPE_START
G1 F15000
G1 X116.758 Y154.027 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X114.444 Y156.429 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.106121
G1 F5950
G1 X114.346 Y156.438 E.00051
; LINE_WIDTH: 0.15495
G2 X113.993 Y156.489 I1.03 J8.35 E.00326
G1 X114.071 Y156.506 F30000
; LINE_WIDTH: 0.190141
G1 F5950
G1 X114.234 Y156.397 E.00235
G1 X114.071 Y156.506 F30000
; LINE_WIDTH: 0.155959
G1 F5950
G1 X113.957 Y156.589 E.0013
; LINE_WIDTH: 0.112362
G1 X113.786 Y156.732 E.00126
G1 X113.516 Y157.001 F30000
; LINE_WIDTH: 0.112758
G1 F5950
G1 X113.371 Y157.176 E.00129
; LINE_WIDTH: 0.17474
G2 X112.908 Y157.833 I14.62 J10.804 E.00863
G1 X112.936 Y157.837 F30000
; LINE_WIDTH: 0.235421
G1 F5950
G1 X113.446 Y157.036 E.0149
G1 X113.386 Y157.096 F30000
; LINE_WIDTH: 0.303731
G1 F5950
G1 X112.956 Y157.839 E.01825
G1 X113.204 Y157.872 F30000
; LINE_WIDTH: 0.387652
G1 F5950
G1 X113.055 Y157.675 E.00693
G3 X113.352 Y157.13 I7.938 J3.973 E.01746
; WIPE_START
G1 F10442.908
G1 X113.055 Y157.675 E-.5441
M73 P94 R0
G1 X113.204 Y157.872 E-.2159
; WIPE_END
G1 E-.04 F1800
G1 X118.601 Y163.269 Z2.4 F30000
G1 X126.178 Y170.847 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.387781
G1 F5950
G1 X126.374 Y170.995 E.00692
G2 X126.918 Y170.7 I-4.523 J-8.97 E.01739
G1 X126.952 Y170.666 F30000
; LINE_WIDTH: 0.30678
G1 F5950
G1 X126.21 Y171.094 E.01841
G1 X126.213 Y171.114 F30000
; LINE_WIDTH: 0.233575
G1 F5950
G2 X126.7 Y170.802 I-6.843 J-11.217 E.00899
; LINE_WIDTH: 0.19303
G1 X126.758 Y170.763 E.00085
; LINE_WIDTH: 0.157478
G1 X126.873 Y170.679 E.00134
; LINE_WIDTH: 0.112774
G1 X127.048 Y170.534 E.00129
G1 X127.318 Y170.264 F30000
; LINE_WIDTH: 0.112356
G1 F5950
G1 X127.46 Y170.093 E.00126
; LINE_WIDTH: 0.155935
G1 X127.544 Y169.978 E.0013
; LINE_WIDTH: 0.190135
G1 X127.653 Y169.815 E.00235
G1 X127.594 Y169.84 F30000
; LINE_WIDTH: 0.164654
G1 F5950
G1 X127.561 Y170.057 E.00218
G1 X127.594 Y169.84 F30000
; LINE_WIDTH: 0.139078
G1 F5950
G1 X127.612 Y169.7 E.00111
; LINE_WIDTH: 0.105813
G1 X127.62 Y169.606 E.00049
; WIPE_START
G1 F15000
G1 X127.612 Y169.7 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X125.943 Y171.172 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; FEATURE: Top surface
; LINE_WIDTH: 0.42
G1 F5950
M204 S2000
G1 X125.547 Y171.567 E.01719
G1 X125.041 Y171.541
G1 X125.766 Y170.815 E.03151
G1 X125.365 Y170.683
G1 X124.645 Y171.403 E.03129
G1 X124.328 Y171.187
G1 X125.045 Y170.47 E.03113
G1 X124.798 Y170.184
G1 X124.061 Y170.92 E.03201
G1 X123.795 Y170.654
G1 X124.611 Y169.838 E.03545
G1 X124.511 Y169.404
G1 X123.528 Y170.387 E.04274
G1 X123.261 Y170.12
G1 X124.6 Y168.782 E.05818
; WIPE_START
G1 F9547.055
M204 S10000
G1 X123.261 Y170.12 E-.71946
G1 X123.337 Y170.196 E-.04054
; WIPE_END
G1 E-.04 F1800
G1 X127.709 Y169.405 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S2000
G1 X129.725 Y167.39 E.08759
G1 X129.296 Y167.285
G1 X127.599 Y168.982 E.07374
G1 X127.467 Y168.581
G1 X128.902 Y167.146 E.06238
G1 X128.58 Y166.935
G1 X127.254 Y168.261 E.05762
G1 X126.971 Y168.011
G1 X128.334 Y166.648 E.05922
G1 X128.146 Y166.302
G1 X126.625 Y167.823 E.06609
G1 X126.178 Y167.737
G1 X128.047 Y165.868 E.0812
G1 X128.126 Y165.256
G1 X125.572 Y167.81 E.11098
; WIPE_START
G1 F9547.055
M204 S10000
G1 X126.986 Y166.395 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X131.882 Y165.233 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S2000
G1 X131.491 Y165.623 E.01697
G1 X131.141 Y165.441
G1 X131.859 Y164.722 E.03123
G1 X131.72 Y164.328
G1 X131.004 Y165.044 E.03112
G1 X130.783 Y164.732
G1 X131.504 Y164.011 E.03132
G1 X131.245 Y163.737
G1 X130.506 Y164.475 E.03207
G1 X130.161 Y164.287
G1 X130.978 Y163.47 E.0355
G1 X130.711 Y163.204
G1 X129.714 Y164.201 E.04334
G1 X129.108 Y164.274
G1 X130.445 Y162.937 E.0581
G1 X130.178 Y162.67
G1 X122.994 Y169.854 E.31216
G1 X122.728 Y169.587
G1 X129.911 Y162.404 E.31216
G1 X129.645 Y162.137
G1 X122.461 Y169.321 E.31217
G1 X122.194 Y169.054
G1 X129.378 Y161.871 E.31217
G1 X129.112 Y161.604
G1 X121.928 Y168.788 E.31218
G1 X121.661 Y168.521
G1 X128.845 Y161.337 E.31218
G1 X128.578 Y161.071
G1 X121.394 Y168.255 E.31219
G1 X121.127 Y167.988
G1 X128.312 Y160.804 E.31219
G1 X128.045 Y160.537
G1 X120.861 Y167.722 E.3122
G1 X120.594 Y167.455
G1 X127.778 Y160.271 E.31221
G1 X127.512 Y160.004
G1 X120.327 Y167.189 E.31221
G1 X120.06 Y166.922
G1 X127.245 Y159.738 E.31222
G1 X126.978 Y159.471
G1 X119.794 Y166.656 E.31222
G1 X119.527 Y166.389
G1 X126.712 Y159.204 E.31222
G1 X126.445 Y158.938
G1 X119.26 Y166.123 E.31223
G1 X118.993 Y165.856
G1 X126.179 Y158.671 E.31224
G1 X125.912 Y158.404
G1 X118.727 Y165.59 E.31224
G1 X118.46 Y165.323
G1 X125.645 Y158.138 E.31225
G1 X125.379 Y157.871
G1 X118.193 Y165.057 E.31225
G1 X117.926 Y164.79
G1 X125.112 Y157.604 E.31226
G1 X124.845 Y157.338
G1 X117.66 Y164.524 E.31226
G1 X117.393 Y164.257
G1 X124.579 Y157.071 E.31227
G1 X124.312 Y156.805
G1 X117.126 Y163.991 E.31227
G1 X116.859 Y163.724
G1 X124.046 Y156.538 E.31228
M73 P95 R0
G1 X123.779 Y156.271
G1 X116.593 Y163.458 E.31228
G1 X116.326 Y163.191
G1 X123.512 Y156.005 E.31229
G1 X123.246 Y155.738
G1 X116.059 Y162.925 E.31229
G1 X115.792 Y162.658
G1 X122.979 Y155.471 E.3123
G1 X122.712 Y155.205
G1 X115.526 Y162.392 E.3123
G1 X115.259 Y162.125
G1 X122.446 Y154.938 E.31231
G1 X122.179 Y154.672
G1 X114.992 Y161.859 E.31231
G1 X114.725 Y161.592
G1 X121.913 Y154.405 E.31232
G1 X121.646 Y154.138
G1 X114.459 Y161.326 E.31232
G1 X114.192 Y161.059
G1 X121.379 Y153.872 E.31233
G1 X121.113 Y153.605
G1 X119.779 Y154.939 E.05796
G1 X119.858 Y154.326
G1 X120.846 Y153.338 E.04293
G1 X120.579 Y153.072
G1 X119.759 Y153.892 E.03566
G1 X119.571 Y153.547
G1 X120.313 Y152.805 E.03223
G1 X120.039 Y152.546
G1 X119.325 Y153.26 E.03103
G1 X119.004 Y153.047
G1 X119.722 Y152.329 E.03119
G1 X119.328 Y152.191
G1 X118.611 Y152.907 E.03114
G1 X118.428 Y152.557
G1 X118.822 Y152.163 E.01715
; WIPE_START
G1 F9547.055
M204 S10000
G1 X118.428 Y152.557 E-.21205
G1 X118.611 Y152.907 E-.15013
G1 X119.328 Y152.191 E-.38515
G1 X119.359 Y152.202 E-.01267
; WIPE_END
G1 E-.04 F1800
G1 X118.797 Y155.921 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S2000
G1 X116.24 Y158.478 E.11113
G1 X116.323 Y157.862
G1 X118.182 Y156.003 E.08079
G1 X117.752 Y155.9
G1 X116.226 Y157.425 E.06628
G1 X116.039 Y157.079
G1 X117.398 Y155.72 E.05906
G1 X117.115 Y155.47
G1 X115.789 Y156.795 E.05762
G1 X115.469 Y156.583
G1 X116.902 Y155.149 E.06229
G1 X116.764 Y154.754
G1 X115.075 Y156.443 E.0734
G1 X114.645 Y156.34
G1 X116.66 Y154.325 E.08758
; WIPE_START
G1 F9547.055
M204 S10000
G1 X115.246 Y155.739 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X115.262 Y159.456 Z2.4 F30000
G1 Z2
G1 E.8 F1800
G1 F5950
M204 S2000
G1 X113.925 Y160.793 E.05807
G1 X113.658 Y160.526
G1 X114.646 Y159.538 E.04292
G1 X114.209 Y159.443
G1 X113.392 Y160.26 E.0355
G1 X113.125 Y159.993
G1 X113.863 Y159.255 E.03207
G1 X113.58 Y159.005
G1 X112.866 Y159.719 E.03105
G1 X112.65 Y159.402
G1 X113.367 Y158.685 E.03116
G1 X113.229 Y158.289
G1 X112.51 Y159.008 E.03123
G1 X112.485 Y158.499
G1 X112.878 Y158.107 E.01707
; WIPE_START
G1 F9547.055
M204 S10000
G1 X112.485 Y158.499 E-.21104
G1 X112.51 Y159.008 E-.19349
G1 X113.172 Y158.347 E-.35547
; WIPE_END
G1 E-.04 F1800
G1 X120.28 Y161.125 Z2.4 F30000
G1 X131.792 Y165.625 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Gap infill
; LINE_WIDTH: 0.135498
G1 F5950
G1 X131.653 Y165.812 E.00176
; WIPE_START
G1 F15000
G1 X131.792 Y165.625 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X131.697 Y164.279 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.0969243
G1 F5950
G2 X131.612 Y164.17 I-.87 J.591 E.00061
; WIPE_START
G1 F15000
G1 X131.697 Y164.279 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X129.039 Y164.206 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.178993
G1 F5950
G1 X128.915 Y164.295 E.0017
; LINE_WIDTH: 0.15502
G1 X128.762 Y164.418 E.0018
; LINE_WIDTH: 0.104143
G1 X128.604 Y164.544 E.00101
G1 X128.406 Y164.741 E.00139
G1 X128.224 Y164.959 E.00142
; LINE_WIDTH: 0.156202
G1 X128.143 Y165.075 E.00131
; LINE_WIDTH: 0.19082
G1 X128.062 Y165.191 E.00171
; WIPE_START
G1 F15000
G1 X128.143 Y165.075 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X128.133 Y166.265 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.125861
G1 F5950
G1 X128.073 Y166.169 E.00077
G1 X128.095 Y166.087 E.00058
; WIPE_START
G1 F15000
G1 X128.073 Y166.169 E-.32576
G1 X128.133 Y166.265 E-.43424
; WIPE_END
G1 E-.04 F1800
G1 X129.845 Y167.657 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.213654
G1 F5950
G1 X127.978 Y169.525 E.03674
G1 X127.926 Y169.658 E.00198
; WIPE_START
G1 F15000
G1 X127.978 Y169.525 E-.05419
G1 X129.291 Y168.211 E-.70581
; WIPE_END
G1 E-.04 F1800
G1 X125.504 Y167.741 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.179055
G1 F5950
G1 X125.379 Y167.83 E.0017
; LINE_WIDTH: 0.155057
G1 X125.226 Y167.953 E.0018
; LINE_WIDTH: 0.103949
G1 X125.069 Y168.08 E.001
G1 X124.871 Y168.277 E.00139
G1 X124.691 Y168.491 E.00139
; LINE_WIDTH: 0.138908
G1 X124.685 Y168.5 E.00008
; LINE_WIDTH: 0.15787
G1 X124.611 Y168.61 E.00124
; LINE_WIDTH: 0.192781
G1 X124.538 Y168.719 E.00161
; WIPE_START
G1 F15000
G1 X124.611 Y168.61 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X126.132 Y171.334 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.130316
G1 F5950
G1 X126.036 Y171.401 E.00084
; LINE_WIDTH: 0.102222
G1 X125.939 Y171.468 E.00057
; WIPE_START
G1 F15000
G1 X126.036 Y171.401 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X120.386 Y166.269 Z2.4 F30000
G1 X112.594 Y159.191 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.0998271
G1 F5950
G1 X112.511 Y159.031 E.00083
; WIPE_START
G1 F15000
G1 X112.594 Y159.191 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X112.716 Y157.918 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.135397
G1 F5950
G1 X112.578 Y158.105 E.00175
; WIPE_START
G1 F15000
G1 X112.716 Y157.918 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.308 Y158.546 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.176981
G1 F5950
G1 X116.216 Y158.675 E.00173
; LINE_WIDTH: 0.153347
G1 X116.093 Y158.828 E.00177
; LINE_WIDTH: 0.0978755
G1 X115.966 Y158.985 E.0009
G1 X115.766 Y159.185 E.00127
; LINE_WIDTH: 0.111285
G1 X115.61 Y159.31 E.00111
; LINE_WIDTH: 0.165195
G3 X115.33 Y159.524 I-2.098 J-2.455 E.00352
; WIPE_START
G1 F15000
G1 X115.61 Y159.31 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X116.39 Y154.208 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.214079
G1 F5950
G1 X114.528 Y156.068 E.0367
; LINE_WIDTH: 0.196904
G1 X114.528 Y156.094 E.00032
; LINE_WIDTH: 0.160001
G1 X114.529 Y156.12 E.00025
; LINE_WIDTH: 0.110752
G3 X114.517 Y156.18 I-.09 J.014 E.00035
; WIPE_START
G1 F15000
G1 X114.529 Y156.12 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X119.843 Y155.003 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.190781
G1 F5950
G1 X119.762 Y155.119 E.00171
; LINE_WIDTH: 0.155116
G1 X119.676 Y155.242 E.00137
; LINE_WIDTH: 0.103311
G1 X119.499 Y155.453 E.00136
G3 X119.204 Y155.735 I-44.353 J-46.068 E.00201
; LINE_WIDTH: 0.12472
G1 X119.094 Y155.819 E.00092
; LINE_WIDTH: 0.171199
G3 X118.864 Y155.988 I-2.028 J-2.53 E.00298
; WIPE_START
G1 F15000
G1 X119.094 Y155.819 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X119.772 Y153.929 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.125863
G1 F5950
G1 X119.832 Y154.026 E.00077
M73 P96 R0
G1 X119.81 Y154.108 E.00057
; WIPE_START
G1 F15000
G1 X119.832 Y154.026 E-.32547
G1 X119.772 Y153.929 E-.43453
; WIPE_END
G1 E-.04 F1800
G1 X118.43 Y152.262 Z2.4 F30000
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.102165
G1 F5950
G1 X118.334 Y152.329 E.00057
; LINE_WIDTH: 0.130173
G1 X118.238 Y152.396 E.00083
; WIPE_START
G1 F15000
G1 X118.334 Y152.329 E-.76
; WIPE_END
G1 E-.04 F1800
G1 X123.586 Y157.867 Z2.4 F30000
G1 X131.166 Y165.858 Z2.4
G1 Z2
G1 E.8 F1800
; LINE_WIDTH: 0.387657
G1 F5950
G1 X131.315 Y166.055 E.00692
G3 X131.019 Y166.598 I-8.365 J-4.194 E.01739
G1 X130.996 Y166.557 F30000
; LINE_WIDTH: 0.112374
G1 F5950
G1 X130.853 Y166.729 E.00126
G1 X130.985 Y166.633 F30000
; LINE_WIDTH: 0.303749
G1 F5950
G1 X131.413 Y165.891 E.01821
G1 X131.434 Y165.894 F30000
; LINE_WIDTH: 0.235396
G1 F5950
G1 X131.16 Y166.323 E.00799
; LINE_WIDTH: 0.22005
G1 X131.122 Y166.38 E.001
; LINE_WIDTH: 0.19189
G1 X131.08 Y166.443 E.00091
; LINE_WIDTH: 0.155961
G1 X130.996 Y166.557 E.0013
G1 X130.584 Y166.998 F30000
; LINE_WIDTH: 0.112746
G1 F5950
G1 X130.409 Y167.143 E.00129
; LINE_WIDTH: 0.15745
G1 X130.293 Y167.228 E.00134
; LINE_WIDTH: 0.190472
G1 X130.135 Y167.333 E.00229
G1 X130.16 Y167.274 F30000
; LINE_WIDTH: 0.138994
G1 F5950
G1 X130.02 Y167.293 E.0011
; LINE_WIDTH: 0.105781
G1 X129.925 Y167.301 E.00049
G1 X130.16 Y167.274 F30000
; LINE_WIDTH: 0.164555
G1 F5950
G1 X130.377 Y167.241 E.00218
; OBJECT_ID: 817
; WIPE_START
G1 F15000
G1 X130.16 Y167.274 E-.76
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 839
M625
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G1 X125.226 Y161.451 Z2.4 F30000
G1 X103.461 Y135.767 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5950
G1 X103.44 Y135.727 E.00149
G1 X103.432 Y135.628 E.00331
G1 X103.462 Y135.532 E.00331
G1 X103.527 Y135.457 E.00331
G1 X103.617 Y135.412 E.00332
G1 X103.703 Y135.405 E.00288
G1 X103.788 Y135.427 E.00291
G1 X103.869 Y135.487 E.00331
G1 X103.92 Y135.573 E.00331
G1 X103.933 Y135.671 E.00331
G1 X103.908 Y135.768 E.00331
G1 X103.846 Y135.847 E.00331
G1 X103.759 Y135.896 E.00331
G1 X103.66 Y135.907 E.00331
G1 X103.564 Y135.878 E.00331
G1 X103.491 Y135.818 E.00315
M204 S250
G1 X103.113 Y135.951 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5950
M204 S5000
G1 X103.083 Y135.9 E.00183
G3 X103.642 Y135.013 I.594 J-.245 E.03769
G3 X103.738 Y135.014 I.038 J.479 E.00296
G3 X103.143 Y136.013 I-.061 J.64 E.07949
G1 X103.139 Y136.005 E.00029
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.083 Y135.9 E-.04535
G1 X103.049 Y135.775 E-.04891
G1 X103.038 Y135.648 E-.04878
G1 X103.052 Y135.52 E-.04874
G1 X103.091 Y135.398 E-.04876
G1 X103.154 Y135.286 E-.04879
G1 X103.238 Y135.189 E-.0488
G1 X103.339 Y135.11 E-.04874
G1 X103.454 Y135.053 E-.04876
G1 X103.642 Y135.013 E-.07296
G1 X103.738 Y135.014 E-.03651
G1 X103.954 Y135.072 E-.0851
G1 X104.065 Y135.137 E-.04878
G1 X104.16 Y135.223 E-.04877
G1 X104.21 Y135.292 E-.03227
; WIPE_END
G1 E-.04 F1800
G1 X98.575 Y130.144 Z2.4 F30000
G1 X92.135 Y124.262 Z2.4
G1 Z2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F5950
G1 X92.149 Y124.219 E.00149
G1 X92.214 Y124.143 E.00331
G1 X92.303 Y124.099 E.00331
G1 X92.39 Y124.091 E.00289
G1 X92.475 Y124.114 E.00291
G1 X92.555 Y124.173 E.00331
G1 X92.606 Y124.259 E.00331
G1 X92.62 Y124.358 E.00331
G1 X92.594 Y124.454 E.00331
G1 X92.532 Y124.533 E.00332
G1 X92.446 Y124.582 E.0033
G1 X92.346 Y124.593 E.00332
G1 X92.25 Y124.565 E.00331
G1 X92.173 Y124.502 E.00331
G1 X92.127 Y124.413 E.00331
G1 X92.118 Y124.319 E.00314
M204 S250
G1 X91.757 Y124.14 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F5950
M204 S5000
G1 X91.803 Y124.025 E.00381
G3 X92.328 Y123.699 I.56 J.316 E.01981
G3 X92.424 Y123.701 I.038 J.48 E.00296
G3 X91.737 Y124.195 I-.061 J.64 E.09571
; CHANGE_LAYER
; Z_HEIGHT: 2.2
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.803 Y124.025 E-.0692
G1 X91.88 Y123.922 E-.0489
G1 X91.973 Y123.833 E-.04874
G1 X92.081 Y123.765 E-.04877
G1 X92.201 Y123.719 E-.04878
G1 X92.328 Y123.699 E-.04874
G1 X92.424 Y123.701 E-.03651
G1 X92.641 Y123.758 E-.0851
G1 X92.751 Y123.823 E-.04876
G1 X92.846 Y123.91 E-.04877
G1 X92.922 Y124.013 E-.04875
G1 X92.977 Y124.129 E-.04879
G1 X93.007 Y124.254 E-.04881
G1 X93.011 Y124.382 E-.04876
G1 X92.998 Y124.467 E-.03261
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 11/15
; update layer progress
M73 L11
M991 S0 P10 ;notify layer change
; OBJECT_ID: 817
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G17
G3 Z2.4 I-.893 J.827 P1  F30000
G1 X103.495 Y135.809 Z2.4
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X103.45 Y135.724 E.00318
G1 X103.442 Y135.629 E.00318
G1 X103.471 Y135.537 E.00318
G1 X103.534 Y135.465 E.00319
; object ids of layer 11 start: 817
M624 AgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer11 end: 817
M625
G1 X103.619 Y135.422 E.00318
G1 X103.703 Y135.415 E.00277
G1 X103.784 Y135.436 E.0028
G1 X103.861 Y135.493 E.00318
G1 X103.91 Y135.576 E.00318
G1 X103.923 Y135.671 E.00318
G1 X103.899 Y135.763 E.00318
G1 X103.84 Y135.839 E.00318
G1 X103.756 Y135.886 E.00319
G1 X103.661 Y135.897 E.00318
G1 X103.569 Y135.87 E.00319
G1 X103.541 Y135.847 E.00119
M204 S250
G1 X103.147 Y135.995 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X103.092 Y135.896 E.00349
G3 X103.642 Y135.022 I.585 J-.242 E.0371
G3 X103.737 Y135.024 I.038 J.472 E.00291
G3 X103.179 Y136.045 I-.06 J.63 E.07682
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.092 Y135.896 E-.06582
G1 X103.059 Y135.774 E-.0481
G1 X103.048 Y135.648 E-.04806
G1 X103.062 Y135.522 E-.04802
G1 X103.1 Y135.402 E-.048
G1 X103.162 Y135.292 E-.04802
G1 X103.245 Y135.196 E-.04795
G1 X103.4 Y135.088 E-.07192
G1 X103.518 Y135.043 E-.04801
G1 X103.642 Y135.022 E-.04799
G1 X103.737 Y135.024 E-.03595
G1 X103.95 Y135.081 E-.08379
G1 X104.059 Y135.145 E-.04802
G1 X104.152 Y135.23 E-.048
G1 X104.187 Y135.277 E-.02237
; WIPE_END
G1 E-.04 F1800
G1 X98.555 Y130.126 Z2.6 F30000
G1 X92.144 Y124.264 Z2.6
G1 Z2.2
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X92.157 Y124.224 E.00139
G1 X92.22 Y124.151 E.00318
G1 X92.306 Y124.108 E.00319
G1 X92.389 Y124.101 E.00277
G1 X92.471 Y124.123 E.0028
G1 X92.548 Y124.18 E.00318
G1 X92.597 Y124.262 E.00318
G1 X92.61 Y124.357 E.00318
G1 X92.585 Y124.45 E.00318
G1 X92.526 Y124.525 E.00318
G1 X92.443 Y124.572 E.00318
G1 X92.347 Y124.583 E.00319
G1 X92.255 Y124.556 E.00318
G1 X92.181 Y124.495 E.00318
G1 X92.136 Y124.41 E.00318
G1 X92.128 Y124.321 E.00298
M204 S250
G1 X91.767 Y124.142 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X91.812 Y124.03 E.00371
G3 X92.329 Y123.709 I.551 J.311 E.01951
G3 X92.423 Y123.711 I.038 J.472 E.00291
G3 X91.747 Y124.197 I-.06 J.63 E.09423
; CHANGE_LAYER
; Z_HEIGHT: 2.4
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.812 Y124.03 E-.06814
G1 X91.887 Y123.928 E-.0482
G1 X91.979 Y123.841 E-.048
G1 X92.086 Y123.774 E-.04804
G1 X92.204 Y123.729 E-.04801
G1 X92.329 Y123.709 E-.04796
G1 X92.423 Y123.711 E-.03596
G1 X92.636 Y123.767 E-.08378
G1 X92.745 Y123.831 E-.04803
G1 X92.839 Y123.916 E-.04803
G1 X92.914 Y124.018 E-.04796
G1 X92.967 Y124.132 E-.04805
G1 X92.997 Y124.255 E-.04802
G1 X93.002 Y124.382 E-.04805
G1 X92.983 Y124.495 E-.04377
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 12/15
; update layer progress
M73 L12
M991 S0 P11 ;notify layer change
; OBJECT_ID: 817
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G17
G3 Z2.6 I-.891 J.829 P1  F30000
G1 X103.502 Y135.803 Z2.6
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X103.459 Y135.721 E.00305
G1 X103.451 Y135.63 E.00304
G1 X103.48 Y135.542 E.00306
G1 X103.54 Y135.473 E.00305
; object ids of layer 12 start: 817
M624 AgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer12 end: 817
M625
G1 X103.622 Y135.432 E.00305
G1 X103.702 Y135.425 E.00267
G1 X103.78 Y135.445 E.00267
G1 X103.854 Y135.5 E.00305
G1 X103.901 Y135.579 E.00305
G1 X103.914 Y135.67 E.00305
G1 X103.89 Y135.759 E.00305
G1 X103.833 Y135.832 E.00305
G1 X103.753 Y135.877 E.00305
G1 X103.662 Y135.887 E.00306
G1 X103.574 Y135.861 E.00304
G1 X103.549 Y135.841 E.00106
M204 S250
G1 X103.209 Y136.061 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X103.197 Y136.052 E.00045
G3 X103.643 Y135.032 I.479 J-.398 E.04229
G3 X103.736 Y135.034 I.037 J.464 E.00287
G3 X103.286 Y136.14 I-.059 J.62 E.07128
G1 X103.251 Y136.104 E.00154
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.197 Y136.052 E-.0283
G1 X103.13 Y135.948 E-.04732
G1 X103.083 Y135.832 E-.04729
G1 X103.06 Y135.71 E-.04719
G1 X103.061 Y135.586 E-.04731
G1 X103.087 Y135.464 E-.04724
G1 X103.137 Y135.35 E-.04729
G1 X103.209 Y135.248 E-.04723
G1 X103.299 Y135.163 E-.04732
G1 X103.404 Y135.096 E-.04722
G1 X103.52 Y135.052 E-.04725
G1 X103.643 Y135.032 E-.04726
G1 X103.736 Y135.034 E-.03539
G1 X103.946 Y135.09 E-.08248
G1 X104.053 Y135.153 E-.04728
G1 X104.144 Y135.236 E-.04665
; WIPE_END
G1 E-.04 F1800
G1 X98.513 Y130.083 Z2.8 F30000
G1 X92.154 Y124.265 Z2.8
G1 Z2.4
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X92.166 Y124.229 E.00127
G1 X92.226 Y124.159 E.00305
G1 X92.308 Y124.118 E.00306
G1 X92.388 Y124.111 E.00266
G1 X92.466 Y124.132 E.00268
G1 X92.54 Y124.186 E.00305
G1 X92.587 Y124.265 E.00305
G1 X92.6 Y124.357 E.00306
G1 X92.576 Y124.445 E.00305
G1 X92.52 Y124.518 E.00304
G1 X92.439 Y124.563 E.00305
G1 X92.348 Y124.573 E.00305
G1 X92.26 Y124.547 E.00305
G1 X92.189 Y124.489 E.00305
G1 X92.146 Y124.408 E.00305
G1 X92.138 Y124.322 E.00284
M204 S250
G1 X91.777 Y124.143 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X91.82 Y124.035 E.0036
G3 X92.329 Y123.719 I.543 J.306 E.0192
G3 X92.422 Y123.721 I.037 J.467 E.00287
G3 X91.757 Y124.199 I-.059 J.62 E.09277
; CHANGE_LAYER
; Z_HEIGHT: 2.6
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.82 Y124.035 E-.06683
G1 X91.895 Y123.935 E-.04738
G1 X91.985 Y123.849 E-.04728
G1 X92.09 Y123.783 E-.04725
G1 X92.207 Y123.739 E-.04732
G1 X92.329 Y123.719 E-.04718
G1 X92.422 Y123.721 E-.03539
G1 X92.632 Y123.776 E-.08245
G1 X92.739 Y123.839 E-.04725
G1 X92.831 Y123.923 E-.04728
G1 X92.905 Y124.023 E-.04727
G1 X92.958 Y124.136 E-.04724
M73 P97 R0
G1 X92.987 Y124.257 E-.04726
G1 X92.992 Y124.381 E-.04731
G1 X92.972 Y124.504 E-.04721
G1 X92.964 Y124.523 E-.00808
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 13/15
; update layer progress
M73 L13
M991 S0 P12 ;notify layer change
; OBJECT_ID: 817
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G17
G3 Z2.8 I-.889 J.831 P1  F30000
G1 X103.515 Y135.801 Z2.8
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X103.51 Y135.796 E.00023
G1 X103.469 Y135.719 E.00292
G1 X103.461 Y135.631 E.00292
G1 X103.488 Y135.547 E.00292
G1 X103.546 Y135.48 E.00292
; object ids of layer 13 start: 817
M624 AgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer13 end: 817
M625
G1 X103.625 Y135.441 E.00293
G1 X103.701 Y135.435 E.00255
G1 X103.776 Y135.454 E.00256
G1 X103.847 Y135.507 E.00292
G1 X103.892 Y135.582 E.00292
G1 X103.904 Y135.67 E.00292
G1 X103.881 Y135.755 E.00292
G1 X103.827 Y135.824 E.00291
G1 X103.75 Y135.867 E.00293
G1 X103.663 Y135.877 E.00292
G1 X103.578 Y135.852 E.00292
G1 X103.562 Y135.839 E.0007
M204 S250
G1 X103.266 Y136.106 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X103.247 Y136.091 E.00074
G3 X103.644 Y135.042 I.43 J-.437 E.0435
G3 X103.735 Y135.044 I.036 J.458 E.00282
G3 X103.342 Y136.168 I-.058 J.61 E.06826
G1 X103.312 Y136.144 E.00118
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.247 Y136.091 E-.03199
G1 X103.17 Y135.996 E-.04657
G1 X103.113 Y135.887 E-.04647
G1 X103.078 Y135.77 E-.04651
G1 X103.067 Y135.648 E-.04656
G1 X103.081 Y135.526 E-.04648
G1 X103.119 Y135.41 E-.04653
G1 X103.179 Y135.303 E-.04648
G1 X103.258 Y135.21 E-.04652
G1 X103.408 Y135.105 E-.06959
G1 X103.523 Y135.062 E-.04655
G1 X103.644 Y135.042 E-.04648
G1 X103.735 Y135.044 E-.03482
G1 X103.942 Y135.099 E-.08113
G1 X104.047 Y135.161 E-.04648
G1 X104.107 Y135.216 E-.03084
; WIPE_END
G1 E-.04 F1800
G1 X98.49 Y130.048 Z3 F30000
G1 X92.174 Y124.237 Z3
G1 Z2.6
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X92.175 Y124.233 E.00011
G1 X92.232 Y124.167 E.00292
G1 X92.311 Y124.127 E.00292
G1 X92.387 Y124.121 E.00254
G1 X92.462 Y124.141 E.00257
G1 X92.533 Y124.193 E.00292
G1 X92.578 Y124.269 E.00292
G1 X92.59 Y124.356 E.00292
G1 X92.567 Y124.441 E.00292
G1 X92.513 Y124.51 E.00292
G1 X92.436 Y124.553 E.00292
G1 X92.349 Y124.563 E.00292
G1 X92.264 Y124.538 E.00292
G1 X92.196 Y124.483 E.00292
G1 X92.155 Y124.405 E.00292
G1 X92.148 Y124.317 E.00292
G1 X92.155 Y124.294 E.00082
M204 S250
G1 X91.799 Y124.116 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X91.802 Y124.095 E.00066
G3 X92.33 Y123.729 I.562 J.246 E.02079
G3 X92.422 Y123.73 I.036 J.458 E.00282
G3 X91.764 Y124.212 I-.058 J.61 E.09095
G1 X91.778 Y124.172 E.00129
; CHANGE_LAYER
; Z_HEIGHT: 2.8
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.802 Y124.095 E-.0308
G1 X91.865 Y123.989 E-.04668
G1 X91.945 Y123.897 E-.04647
G1 X92.095 Y123.792 E-.06963
G1 X92.209 Y123.748 E-.04656
G1 X92.33 Y123.729 E-.04644
G1 X92.422 Y123.73 E-.03483
G1 X92.628 Y123.785 E-.08115
G1 X92.733 Y123.847 E-.04651
G1 X92.824 Y123.93 E-.04653
G1 X92.897 Y124.028 E-.0465
G1 X92.948 Y124.139 E-.04647
G1 X92.977 Y124.258 E-.04653
G1 X92.982 Y124.38 E-.04655
G1 X92.962 Y124.501 E-.04646
G1 X92.932 Y124.58 E-.03189
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 14/15
; update layer progress
M73 L14
M991 S0 P13 ;notify layer change
; OBJECT_ID: 817
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G17
G3 Z3 I-.885 J.836 P1  F30000
G1 X103.551 Y135.817 Z3
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X103.518 Y135.79 E.00142
G1 X103.479 Y135.716 E.00278
G1 X103.471 Y135.632 E.0028
G1 X103.497 Y135.552 E.00278
G1 X103.552 Y135.488 E.00279
; object ids of layer 14 start: 817
M624 AgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer14 end: 817
M625
G1 X103.627 Y135.451 E.00279
G1 X103.7 Y135.445 E.00243
G1 X103.772 Y135.463 E.00245
G1 X103.839 Y135.513 E.00279
G1 X103.882 Y135.586 E.00279
G1 X103.894 Y135.669 E.00279
G1 X103.872 Y135.75 E.00278
G1 X103.82 Y135.817 E.0028
G1 X103.747 Y135.858 E.00279
G1 X103.664 Y135.867 E.00279
G1 X103.601 Y135.849 E.00217
M204 S250
G1 X103.298 Y136.112 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X103.254 Y136.084 E.00162
G3 X103.644 Y135.052 I.423 J-.43 E.0428
G3 X103.734 Y135.054 I.036 J.45 E.00278
G3 X103.454 Y136.215 I-.057 J.6 E.06345
G1 X103.348 Y136.145 E.0039
; WIPE_START
G1 F9547.055
M204 S10000
G1 X103.254 Y136.084 E-.0428
G1 X103.122 Y135.884 E-.09116
G1 X103.077 Y135.648 E-.09105
G1 X103.106 Y135.47 E-.06845
G1 X103.155 Y135.36 E-.04577
G1 X103.224 Y135.261 E-.04581
G1 X103.413 Y135.114 E-.09103
G1 X103.644 Y135.052 E-.09101
G1 X103.734 Y135.054 E-.03426
G1 X103.937 Y135.108 E-.07983
G1 X104.104 Y135.231 E-.07882
; WIPE_END
G1 E-.04 F1800
G1 X98.485 Y130.066 Z3.2 F30000
G1 X92.175 Y124.265 Z3.2
G1 Z2.8
G1 E.8 F1800
; FEATURE: Inner wall
; LINE_WIDTH: 0.45
G1 F1200
G1 X92.183 Y124.238 E.00095
G1 X92.238 Y124.175 E.00279
G1 X92.313 Y124.137 E.00279
G1 X92.386 Y124.131 E.00243
G1 X92.458 Y124.15 E.00245
G1 X92.526 Y124.2 E.00279
G1 X92.568 Y124.272 E.00278
G1 X92.58 Y124.355 E.00279
G1 X92.558 Y124.436 E.00279
G1 X92.507 Y124.503 E.00278
G1 X92.433 Y124.544 E.00279
G1 X92.35 Y124.553 E.00279
G1 X92.269 Y124.53 E.00279
G1 X92.204 Y124.476 E.00279
G1 X92.165 Y124.402 E.00279
G1 X92.158 Y124.323 E.00264
M204 S250
G1 X91.799 Y124.145 F30000
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X91.908 Y123.946 E.00697
G3 X92.331 Y123.739 I.456 J.395 E.01487
G3 X92.421 Y123.74 I.036 J.45 E.00277
G3 X91.777 Y124.199 I-.057 J.6 E.08995
; CHANGE_LAYER
; Z_HEIGHT: 3
; LAYER_HEIGHT: 0.2
; WIPE_START
G1 F9547.055
M204 S10000
G1 X91.908 Y123.946 E-.10836
G1 X92.099 Y123.801 E-.09129
G1 X92.331 Y123.739 E-.09105
G1 X92.421 Y123.74 E-.03426
G1 X92.624 Y123.794 E-.07985
G1 X92.817 Y123.936 E-.09106
G1 X92.939 Y124.142 E-.09105
G1 X92.972 Y124.38 E-.09109
G1 X92.916 Y124.588 E-.082
; WIPE_END
G1 E-.04 F1800
; stop printing object, unique label id: 817
M625
; layer num/total_layer_count: 15/15
; update layer progress
M73 L15
M991 S0 P14 ;notify layer change
; OBJECT_ID: 817
; start printing object, unique label id: 817
M624 AgAAAAAAAAA=
G17
G3 Z3.2 I-.903 J.816 P1  F30000
G1 X103.346 Y136.132 Z3.2
G1 Z3
G1 E.8 F1800
G1 F1200
M204 S5000
G1 X103.263 Y136.075 E.0031
G3 X103.704 Y135.061 I.419 J-.42 E.04367
; object ids of layer 15 start: 817
M624 AgAAAAAAAAA=
;========Date 20250206========
M622.1 S1 ; for prev firmware, default turned on
M1002 judge_flag timelapse_record_flag
M622 J1
 ; timelapse without wipe tower
M971 S11 C10 O0

M623

; object ids of this layer15 end: 817
M625
G1 X103.763 Y135.067 E.00182
G3 X103.459 Y136.204 I-.081 J.588 E.06185
G1 X103.396 Y136.165 E.00227
M204 S10000
G1 X103.517 Y135.318 F30000
; FEATURE: Top surface
G1 F1200
M204 S2000
G1 X104.026 Y135.827 E.02211
M204 S10000
G1 X103.766 Y136.043 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.36507
G1 F1200
G3 X103.306 Y135.538 I1.019 J-1.392 E.01807
G1 X104.051 Y135.559 F30000
; LINE_WIDTH: 0.119608
G1 F1200
G2 X103.797 Y135.278 I-.823 J.49 E.00239
; WIPE_START
G1 F15000
G1 X103.97 Y135.443 E-.47724
G1 X104.051 Y135.559 E-.28276
; WIPE_END
G1 E-.04 F1800
G1 X98.478 Y130.345 Z3.4 F30000
G1 X91.821 Y124.117 Z3.4
G1 Z3
G1 E.8 F1800
; FEATURE: Outer wall
; LINE_WIDTH: 0.42
G1 F1200
M204 S5000
G1 X91.824 Y124.104 E.00039
G3 X92.391 Y123.748 I.544 J.237 E.02185
G1 X92.449 Y123.753 E.00182
G3 X91.775 Y124.335 I-.081 J.588 E.08365
G1 X91.808 Y124.175 E.005
M204 S10000
G1 X92.204 Y124.004 F30000
; FEATURE: Top surface
G1 F1200
M204 S2000
G1 X92.707 Y124.508 E.02188
M204 S10000
G1 X92.453 Y124.729 F30000
; FEATURE: Gap infill
; LINE_WIDTH: 0.365074
G1 F1200
G3 X91.992 Y124.224 I1.018 J-1.391 E.01807
G1 X92.738 Y124.245 F30000
; LINE_WIDTH: 0.119577
G1 F1200
G2 X92.483 Y123.964 I-.822 J.489 E.00238
; close powerlost recovery
M1003 S0
; WIPE_START
G1 F15000
G1 X92.656 Y124.129 E-.47745
G1 X92.738 Y124.245 E-.28255
; WIPE_END
G1 E-.04 F1800
G17
G3 Z3.4 I1.217 J0 P1  F30000
; stop printing object, unique label id: 817
M625
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
G1 Z3.5 F900 ; lower z a little
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
M73 P98 R0
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

    G1 Z103 F600
    G1 Z101

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

