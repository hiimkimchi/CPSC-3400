;Bryan Kim
;CPSC 3400
;lp1.scm

;desc: displays the sum of multiples of 3 or 5 within a certain range
;pre : -data is passed in when called
;post: none
(define (print-sum data)
    (display "Sum of Multiples of 3 or 5: ")
    (display data)
    (display "\n")
)

;desc: calculates the sum of multiples of 3 or 5 within a range
;pre : -a range is passed in when called
;post: -the sum is returned
(define (sum-multiples range)
    (cond ((zero? (length range)) 0)
        ((zero? (modulo(car range) 3))
            (+ (sum-multiples (cdr range)) (car range))
        )
        ((zero? (modulo (car range) 5))
            (+ (sum-multiples (cdr range)) (car range))
        )
        (else (+ (sum-multiples(cdr range)) 0))
    )
)

(define num 30000)
;0 and num is not inclusive!
(define nums (iota (- num 2) 1))
(print-sum (sum-multiples nums))