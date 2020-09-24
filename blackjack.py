#! /usr/bin/env python3


import cards
import db
import locale as lc
from datetime import time, datetime

result = lc.setlocale(lc.LC_ALL,"en_US")
if result == "C":
    lc.setlocale(lc.LC_ALL,"en_US")



def display_title(start_time):
    # header
    print("BLACKJACK!")
    print("Blackjack payout is 3:2")
    print("Enter 'x' for bet to exit")
    print("Start time: ", start_time.strftime("%I:%M:%S %p"))
    print()


def get_starting_money():
    try:
        money = db.read_money()
    except FileNotFoundError:
        print("Data file missing, resetting starting amount to 1000.")
        money = 0
    if money < 5:
        #print("You were out of money")
        #print("We gave you 100 so you could play.")
        db.write_money(1000)
        return 1000
    else:
        return money

def get_bet(money):
    while True:
        try:
            bet = float(input("Bet amount:     "))
        except ValueError:
            print("Invalid amount, try again")
            continue
        # I am pretty sure the way he told us to code this that this part
        # won't work anymore but ... I am just going to leave it atm
        if bet == "x":
            return bet

        bet = float(bet)
        if bet < 5:
            print("The minimum bet is 5.")
        elif bet > 1000:
            print("The maximum bet is 1,000.")
        elif bet > money:
            print("You don't have enough money to make that bet.")
        else:
            return bet


def display_card(hand, title):
    print(title.upper())
    for card in hand:
        print(card[0], "of", card[1])
    print()


def play(deck, player_hand, money, bet):
    while True:
        can_double_down = False
        if(money >= bet *2 ) and (len(player_hand)==2):
            can_double_down = True

        if can_double_down:
            msg = "Hit or Stand or Double Down? (h/s/d): "
        else:
            msg = "Hit or Stand? (h/s): "
        choice = input(msg)
        print()

        if choice.lower() == "h":
            cards.add_card(player_hand, cards.deal_card(deck))
            if cards.get_points(player_hand) > 21:
                break
            display_card(player_hand, "YOUR CARDS: ")
        elif choice.lower() == "d" and can_double_down:
            cards.add_card(player_hand, cards.deal_card(deck))
            display_card(player_hand, "YOUR CARDS: ")
            bet *= 2
            break
        elif choice.lower() == "d":
            print("Insufficient funds to do that.")
        elif choice.lower() == "s":
            break
        else:
            print("Not a valid choice, Try again.")
    return player_hand, bet


def compare_hands(players_hand, dealers_hand):
    player_value = cards.get_points(players_hand)
    dealer_value = cards.get_points(dealers_hand)
    print("YOUR POINTS:     ", player_value)
    print("DEALER'S POINTS: ", dealer_value)
    print()
    if player_value > 21:
        print(" Oh no! You busted, you lose!")
        return "lose"
    elif player_value == 21 and len(players_hand) == 2:
        if dealer_value == 21 and len(dealers_hand) == 2:
            print("Dang, dealer got blackjack too. You push.")
            return "push"
        else:
            print("Blackjack! You win!")
            return "blackjack"
    elif dealer_value > 21:
        print("Yay! Dealer busted, you win!")
        return "win"
    elif player_value > dealer_value:
        print(" Yay. You win.")
        return "win"
    elif dealer_value > player_value:
        print("Sorry, you lose")
        return "lose"
    elif dealer_value == player_value:
        print("Push")
        return "push"
    else:
        print("Sorry, I don't know what happened")


def buy_more_chips(money):
    while True:
        try:
            amount= float(input("Amount: "))
        except ValueError:
            print("Invalid amount. Try again")
            continue
        if 0< amount  <= 10000:
            money += amount
            return money
        else:
            print("Invalid amount, must be from 0 to 10,000.")


def main():
    start_time = datetime.now()
    display_title(start_time)

    # Input money & bet from user
    money = get_starting_money()
    print("PLayer's money:", lc.currency(money, grouping=True))
    print()
    while True:
        if money<5:
            print("You are out of money.")
            buy_more = input("Would you like to buy more chips? (y/n): ").lower()
            if buy_more =="y":
                money = buy_more_chips(money)
                print("Player's money: ",lc.currency(money, grouping=True))
                print()
                db.write_money(money)
            else:
                break
        bet = get_bet(money)
        if bet =="x":
            break
        deck = cards.get_deck()
        cards.shuffle(deck)
        players_hand = cards.get_empty_hand()
        dealers_hand = cards.get_empty_hand()
        cards.add_card(players_hand, cards.deal_card(deck))
        cards.add_card(dealers_hand, cards.deal_card(deck))
        cards.add_card(players_hand, cards.deal_card(deck))
        print()
        display_card(dealers_hand, "Dealer's SHOW CARD: ")
        display_card(players_hand, "YOUR CARDs: ")
        players_hand, bet = play(deck, players_hand,money, bet)
        while True:
            if cards.get_points(dealers_hand) >= 17:
                break
            else:
                cards.add_card(dealers_hand, cards.deal_card(deck))
        if cards.get_points(players_hand) > 21:
            display_card(dealers_hand, "Dealer's CARDs: ")
        else:
            display_card(dealers_hand, "Dealer's CARDs: ")
        result = compare_hands(players_hand, dealers_hand)

        if result.lower() == "blackjack":
            print("You got blackjack!")
            money += round(int(bet) * 1.5, 2)
        elif result.lower() == "win":
            #print("You won!")
            money += float(bet)
        elif result.lower() == "push":
             #print("You pushed.")
            money = money
        elif result.lower() == "lose":
            #print(" You lost.")
            money -= float(bet)
        # Printing out the money
        print("Player's Money: ", lc.currency(money, grouping=True))
        print()
        db.write_money(money)
        again = input("Play again? (y/n): ")
        if again.lower() != "y":
            print()
            print("Come again soon!")
            break


    stop_time = datetime.now()
    display_end(start_time, stop_time)

def display_end(start_time, stop_time):
    elapse_time = stop_time - start_time
    minutes = elapse_time.seconds//60
    seconds = elapse_time.seconds%60
    hours = minutes//60
    minutes = minutes % 60
    time_object = time(hours, minutes, seconds)
    print("Stop time:        ", stop_time.strftime("%I:%M:%S %p"))
    print("Elapsed time:     ", time_object)
    print("Come back again soon!")

if __name__ == "__main__":
    main()