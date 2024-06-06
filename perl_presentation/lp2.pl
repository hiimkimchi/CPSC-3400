
# create fibonacci_sum function to calculate all even number fibonacci values
sub fibonacci_sum {
    # hold the argument
    my ($limit) = @_;

    # variables to track the previous fib, current fib, and the sum
    my $prev = 0;
    my $curr = 1;
    my $sum = 0;

    # while the current value is less than tne value
    while ($curr <= $limit) {
        # if the value is even add it to the sum
        if ($curr % 2 == 0) {
            $sum += $curr;
        }
        # next fibonacci number
        my $next = $prev + $curr;

        # set previous number to the current value
        $prev = $curr;
        # set curr to the next fibonacci number
        $curr = $next;

    }

    return $sum;
}


my $range = 1000000000;

print "Sum of even Fibonacci numbers less than 1,000,000,000: ";
print fibonacci_sum($range);
print "\n";
