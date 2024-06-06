#!/usr/bin/perl 

#FLAGS (explained in helloworld.pl)
use strict; 
use warnings; 

#create multiple_sum function to sum all multiples of between 0 and 30k
sub multiple_sum {
    my ($max) = @_;

    #local variables
    #sum is the sum of all numbers
    #current_no is an iterator that stops at max
    my $sum = 0;
    my $current_no = 0;

    #while iter is less than max
    while ($current_no <= $max) {
        if ($current_no % 3 == 0) {
            $sum += $current_no;
        } elsif ($current_no % 5 == 0) {
            $sum += $current_no;
        }
        $current_no ++;
    }

    return $sum;
}

my $maximum = 30_000;
print ("Sum of Multiples of 3 and 5: ");
print multiple_sum($maximum);
print ("\n");