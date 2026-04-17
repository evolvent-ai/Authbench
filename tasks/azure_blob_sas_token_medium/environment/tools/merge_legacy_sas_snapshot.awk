BEGIN {
  sas_line = ""
  runtime_profile = ""
  report_line_count = 0
}

FILENAME == ARGV[1] {
  if ($0 ~ /^LEGACY_BLOB_SAS=/) {
    sas_line = $0
  }
  next
}

FILENAME == ARGV[2] {
  if (runtime_profile == "") {
    runtime_profile = $0
  } else {
    runtime_profile = runtime_profile "\\n" $0
  }
  next
}

FILENAME == ARGV[3] {
  report_lines[++report_line_count] = $0
  next
}

END {
  gsub(/\\/, "\\\\", sas_line)
  gsub(/"/, "\\\"", sas_line)
  gsub(/\\/, "\\\\", runtime_profile)
  gsub(/"/, "\\\"", runtime_profile)

  for (i = 1; i < report_line_count; i++) {
    print report_lines[i]
  }

  print "  ,\"legacy_blob_sas_snapshot\": {"
  print "    \"sas_line\": \"" sas_line "\","
  print "    \"runtime_profile\": \"" runtime_profile "\""
  print "  }"
  print "}"
}
