;Bryan Kim
;CPSC 3400 
;lp4.scm

;desc: set the cardValue of each card (all face cards = 10 and ace = 1)
;pre : card is passed in
;post: int value is returned representing the 
(define (cardValue card)
    (let ((rank (substring card 0 1)))
        (cond 
            ((string=? rank "A") 1)
            ((or (string=? rank "T") (string=? rank "J") (string=? rank "Q") (string=? rank "K")) 10)
            (else (string->number rank))
        )
    )
)

;desc: sums all values of the cards
;pre : cards and total is passed in
;post: returns sum
(define (sumCards cards total)
    (cond 
        ((null? cards) total) 
        (else (sumCards (cdr cards) (+ total (cardValue (car cards)))))
    )
)

;desc: displays the result of the game
;pre : player total and dealer total is passed in
;post: none
(define (displayResult playerTotal dealerTotal)
    (cond
        ((> playerTotal 21) 
            (display "Player busts.") (newline) "Lose")
        ((> playerTotal dealerTotal) 
            (display "Player wins!") (newline) "Win")
        ((< playerTotal dealerTotal) 
            (display "Player loses.") (newline) "Lose")
        (else (display "Player loses.") (newline) "Lose") 
    )
)

;desc: the main function that handles gameplay
;pre : deck is passed in (must be a list)
;post: none
(define (play deck) 
    (define dealerHand (car deck)) 
    (define playerHand (list (cadr deck) (caddr deck))) 
    (define remainingDeck (cdddr deck)) 

    ;helper function to initialize handVal to 0
    (define (handVal hand) 
        (sumCards hand 0)
    )

    ;helper function to determine if the current player should hit or not
    ;(for deck.scm, it yields the best result if we set the threshold to be 16)
    (define (hit hand deck) 
        (if (or (>= (handVal hand) 16) (null? deck)) hand 
            (hit (append hand (list (car deck))) (cdr deck))
        )
    )

    ;set values and display the results
    (define stayedPlayerHand (hit playerHand remainingDeck))
    (define playerTotal (handVal stayedPlayerHand))
    (define dealerTotal (handVal dealerHand))
    (display "Player's Hand: ") (display playerTotal) (newline)
    (display "Dealer's Hand: ") (display dealerTotal) (newline)
    (displayResult playerTotal dealerTotal)
)

;desc: checks if a game is won by player or dealer
;pre : result is passed in
;post: return true of Win, false if not
(define (isWin result) 
    (eq? result "Win")
)

;desc: prints the total wins out of total played
;pre : winCount and totalCount must be passed in beforehand
;post: none
(define (displayWins winCount totalCount)
    (display "Number of blackjack hands where the current player wins: ")
    (display winCount)
    (display "/")
    (display totalCount)
)

(load "deck.scm")
(define possibleHands deck) 
(define result (map play possibleHands))
(define winCount (length (filter isWin result)))
(define totalWins (length result))
(displayWins winCount totalWins)
(newline)