;Bryan Kim
;CPSC 3400
;lp3.scm

;desc: pretty much same print function as last couple of little programs
;pre : none
;post: none
(define (print n)
    (display "Number of heap configurations where player wins: ")
    (display n)
    (display "\n")
)

;desc: function is responsible for running nim simulation
;pre : -none
;post: -will return a sum of all possible winning conditions
(define (nim-win h1 h2 h3)
    (nim-iter h1 h2 h3 0)
)

;desc: function responsible for nim tail recursion
;pre : -is only called within nim-win
;post: -adds 1 if opponent loses
;      -adds 0 if self loses
(define (nim-iter h1 h2 h3 wins)
    (define xor-result (logxor h1 h2 h3))
    (define next-h1 (- h1 1))
    (cond 
        ;if the first heap is less than or equal to 0, return wins
        ((<= h1 0)
            wins
        )

        ;add 0 because this counts as a loss
        ((zero? xor-result)
            (nim-iter next-h1 (* 2 next-h1) (* 3 next-h1) wins)
        )

        ;add 1 because this counts as a win
        (else
            (nim-iter next-h1 (* 2 next-h1) (* 3 next-h1) (+ 1 wins))
        )
    )
)

(define n (expt 2 30))
(print (nim-win n (* 2 n) (* 3 n)))