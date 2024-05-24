;Bryan Kim
;CPSC 3400
;lp2.scm

;desc: displays the sum of even fibonacci numbers within a certain range
;pre : -data is passed in when called
;post: none
(define (print-sum data)
    (display "Sum of Even Fibonacci Numbers: ")
    (display data)
    (display "\n")
)

;desc: sum even fibonacci numbers until given range. 
;pre : -a range is passed in when called
;post: -the sum is returned 
(define (sum-fib range)
    ;subfunction will generate fib numbers to range and sum them up. 
    (define (fib-even a b sum)
        (if (> b range)
            sum
            (fib-even b (+ a b) 
                (if (even? b) (+ sum b) 
                    sum
                )
            )
        )
    )
    ;call to subfunction gives a returnable value
    (fib-even 0 1 0)
)

(define max 1000000000)
(print-sum (sum-fib max))