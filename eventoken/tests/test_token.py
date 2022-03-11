import pytest
from brownie import accounts, Eventoken
import brownie

TOTAL_SUPPLY = 5000
NAME = "ChattyPoint"
SYMBOL = "CP"
DECIMALS = 0


@pytest.fixture(autouse=True)
def eventoken():
    token = accounts[0].deploy(Eventoken, NAME, SYMBOL, TOTAL_SUPPLY)
    _user1, _user2 = "OVECJOE", "B_Keys"
    token.createToken(_user1, {'from': accounts[1], 'value': '2'})
    token.createToken(_user2, {'from': accounts[2], 'value': '2'})
    return token

def test_init_works(eventoken):
    assert eventoken.usernames("Minter") == eventoken.contract_owner()
    assert eventoken.totalSupply() == TOTAL_SUPPLY
    assert eventoken.name() == NAME
    assert eventoken.symbol() == SYMBOL
    assert eventoken.decimals() == DECIMALS


def test_create_token(eventoken):
    _username = 'OVECJOE'
    with brownie.reverts('Username already exists!'):
        eventoken.createToken(_username, {'from': accounts[2], 'value': '2'})
    assert eventoken.usernames(_username) == accounts[1].address
    assert eventoken.tokens(accounts[1])['owner'] == accounts[1].address
    assert eventoken.tokens(accounts[1])['point_balance'] == 0
    assert len(_username) >= 6


def test_transfer_revert(eventoken):
    with brownie.reverts("Insufficient Balance!"):
        eventoken.transfer(accounts[1], 100, {'from': accounts[2]})
    with brownie.reverts("Cannot send points to the same address!"):
        eventoken.transfer(accounts[0], 100, {'from': accounts[0]})


@pytest.fixture(autouse=True)
def test_mine_points(eventoken):
    with brownie.reverts("You can only mine for yourself!"):
        eventoken.mine_points(accounts[1], {'from': accounts[2]})
    with brownie.reverts("Contract owner is not permitted to mine!"):
        eventoken.mine_points(accounts[0], {'from': accounts[0]})
    eventoken.mine_points(accounts[1], {'from': accounts[1]})
    eventoken.mine_points(accounts[2], {'from': accounts[2]})
    assert eventoken.balanceOf(accounts[1]) > 0
    assert eventoken.balanceOf(accounts[2]) > 0
