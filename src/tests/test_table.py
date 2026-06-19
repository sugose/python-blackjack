"""Tests for HouseRules and Table dataclasses."""

import pytest

from src.dealer import Dealer
from src.player import Player
from src.table import HouseRules, Table


def _make_player(name: str = "Alice", wallet: float = 100.0) -> Player:
    return Player(name=name, strategy=lambda hand: "stand", wallet=wallet)


def _make_table(
    players: list[Player] | None = None,
    max_seats: int = 3,
    num_decks: int = 1,
    min_bet: float = 1.0,
    max_bet: float = 100.0,
) -> Table:
    return Table(
        tableId="test-table-id",
        maxSeats=max_seats,
        minBet=min_bet,
        maxBet=max_bet,
        numDecks=num_decks,
        players=players or [_make_player()],
        dealer=Dealer(),
        houseRules=HouseRules(blackjackPayout=1.5, dealerHitsOnSoft17=False),
    )


class TestHouseRules:
    def test_construction(self) -> None:
        rules = HouseRules(blackjackPayout=1.5, dealerHitsOnSoft17=False)
        assert rules.blackjackPayout == 1.5
        assert rules.dealerHitsOnSoft17 is False

    def test_six_to_five_payout(self) -> None:
        rules = HouseRules(blackjackPayout=1.2, dealerHitsOnSoft17=True)
        assert rules.blackjackPayout == 1.2
        assert rules.dealerHitsOnSoft17 is True


class TestTable:
    def test_construction(self) -> None:
        players = [_make_player("Alice"), _make_player("Bob")]
        table = _make_table(players=players, max_seats=7, num_decks=6)
        assert table.tableId == "test-table-id"
        assert table.maxSeats == 7
        assert table.numDecks == 6
        assert len(table.players) == 2
        assert table.houseRules.blackjackPayout == 1.5

    def test_max_seats_less_than_1_raises(self) -> None:
        with pytest.raises(ValueError, match="maxSeats"):
            _make_table(max_seats=0)

    def test_max_seats_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="maxSeats"):
            _make_table(max_seats=-1)

    def test_players_exceed_max_seats_raises(self) -> None:
        players = [_make_player(f"P{i}") for i in range(4)]
        with pytest.raises(ValueError, match="players"):
            _make_table(players=players, max_seats=3)

    @pytest.mark.parametrize("num_decks", [3, 5, 7, 9, 0, -1])
    def test_invalid_num_decks_raises(self, num_decks: int) -> None:
        with pytest.raises(ValueError, match="numDecks"):
            _make_table(num_decks=num_decks)

    @pytest.mark.parametrize("num_decks", [1, 2, 4, 6, 8])
    def test_valid_num_decks(self, num_decks: int) -> None:
        table = _make_table(num_decks=num_decks)
        assert table.numDecks == num_decks

    def test_min_bet_exceeds_max_bet_raises(self) -> None:
        with pytest.raises(ValueError, match="minBet"):
            _make_table(min_bet=50.0, max_bet=10.0)

    def test_min_bet_equals_max_bet_is_valid(self) -> None:
        table = _make_table(min_bet=10.0, max_bet=10.0)
        assert table.minBet == table.maxBet

    def test_player_vip_field_default_false(self) -> None:
        player = _make_player()
        assert player.vip is False

    def test_player_vip_can_be_set_true(self) -> None:
        player = Player(name="VIP", strategy=lambda h: "stand", wallet=500.0, vip=True)
        assert player.vip is True
