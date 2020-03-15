# geodesic_groups_file 2.3

#
proc group_autoload {} {
  global gFilenames
  set grpdir $gFilenames(groups_dir)
  # Group Stuff
  group_readProfiles {aorta} [file join $grpdir {aorta}]
  group_readProfiles {renal} [file join $grpdir {renal}]
  group_readProfiles {right_iliac} [file join $grpdir {right_iliac}]
}
proc seg3d_autoload {} {
  global gFilenames
  set grpdir $gFilenames(groups_dir)
  # Seg Stuff
}
