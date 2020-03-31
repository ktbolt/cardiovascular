# geodesic_groups_file 2.1

#
# Group Stuff
#

proc group_autoload {} {
  global gFilenames
  set grpdir $gFilenames(groups_dir)
  group_readProfiles {lt_post_comm_FINAL} [file join $grpdir {lt_post_comm_FINAL}]
  group_readProfiles {rt_ext_crtd_FINAL} [file join $grpdir {rt_ext_crtd_FINAL}]
  group_readProfiles {lt_crtd_FINAL} [file join $grpdir {lt_crtd_FINAL}]
  group_readProfiles {lt_sbclvn_FINAL} [file join $grpdir {lt_sbclvn_FINAL}]
  group_readProfiles {brchcph_FINAL} [file join $grpdir {brchcph_FINAL}]
  group_readProfiles {rt_crtd_FINAL} [file join $grpdir {rt_crtd_FINAL}]
  group_readProfiles {rt_vrtbrl_FINAL} [file join $grpdir {rt_vrtbrl_FINAL}]
  group_readProfiles {rt_ant_crbrl_FINAL} [file join $grpdir {rt_ant_crbrl_FINAL}]
  group_readProfiles {arch_FINAL} [file join $grpdir {arch_FINAL}]
  group_readProfiles {lt_ant_crbrl_FINAL} [file join $grpdir {lt_ant_crbrl_FINAL}]
  group_readProfiles {rt_post_comm_FINAL} [file join $grpdir {rt_post_comm_FINAL}]
  group_readProfiles {lt_vrtbrl_FINAL} [file join $grpdir {lt_vrtbrl_FINAL}]
  group_readProfiles {lt_ext_crtd_FINAL} [file join $grpdir {lt_ext_crtd_FINAL}]
  group_readProfiles {lt_post_crbrl_FINAL} [file join $grpdir {lt_post_crbrl_FINAL}]
}
