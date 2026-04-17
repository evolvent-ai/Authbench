#!/usr/bin/perl
use strict;
use warnings;

my $archive_path = shift @ARGV;
if (!defined $archive_path || $archive_path eq '') {
    die "Usage: 7z2john.pl <archive>\n";
}

print "7z:$archive_path\n";
